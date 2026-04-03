"""
文件监听器
使用 watchdog 监控 knowledge/ 文件夹，
文件变化时自动触发增量索引到 Chroma
"""
import os
import sys
import time
import threading
from pathlib import Path
from typing import Optional, Callable

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
except ImportError:
    Observer = None
    FileSystemEventHandler = object

from .indexer import KnowledgeIndexer


class KnowledgeHandler(FileSystemEventHandler):
    """
    监听 knowledge/ 目录下的文件变化
    - 新增/修改文件 → 触发增量索引
    - 删除文件 → 从状态记录中移除（下次全量重建跳过）
    """

    def __init__(
        self,
        knowledge_dir: str,
        chroma_dir: str,
        state_file: str,
        debounce_seconds: float = 2.0,
        on_update: Optional[Callable[[str, int], None]] = None,
    ):
        self.knowledge_dir = knowledge_dir
        self.indexer = KnowledgeIndexer(knowledge_dir, chroma_dir, state_file)
        self.debounce_seconds = debounce_seconds
        self.on_update = on_update
        self._pending: dict[str, float] = {}  # path -> trigger_time
        self._lock = threading.Lock()

    def _queue(self, path: str):
        """防抖：将 path 加入待处理队列"""
        with self._lock:
            self._pending[path] = time.time() + self.debounce_seconds

    def _flush(self):
        """处理已到期的待处理事件"""
        now = time.time()
        with self._lock:
            expired = {p for p, t in self._pending.items() if t <= now}
            for p in expired:
                del self._pending[p]
        return expired

    def _process(self, path: str):
        """实际处理单个文件"""
        ext = Path(path).suffix.lower()
        if ext not in {".pdf", ".txt", ".md", ".docx"}:
            return

        # 找出该文件属于哪个子文件夹
        rel = os.path.relpath(path, self.knowledge_dir)
        subfolder = os.path.dirname(rel).split(os.sep)[0] if os.sep in rel else ""

        print(f"[Watcher] 检测到文件变化: {path}")
        result = self.indexer.index_folder(subfolder)
        total = sum(result.values())
        if self.on_update:
            self.on_update(path, total)

    def on_created(self, event: FileSystemEvent):
        if not event.is_directory:
            self._queue(event.src_path)

    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory:
            self._queue(event.src_path)

    def on_deleted(self, event: FileSystemEvent):
        if not event.is_directory:
            with self._lock:
                self._pending.pop(event.src_path, None)

    def poll(self):
        """在主线程中定期调用，触发到期的事件处理"""
        expired = self._flush()
        for path in expired:
            self._process(path)


class KnowledgeWatcher:
    """
    启动一个后台线程，监控 knowledge/ 目录
    支持 start() / stop() / poll()
    """

    def __init__(
        self,
        knowledge_dir: str,
        chroma_dir: str,
        state_file: Optional[str] = None,
        debounce_seconds: float = 2.0,
        on_update: Optional[Callable[[str, int], None]] = None,
    ):
        if Observer is None:
            raise ImportError("请安装 watchdog: pip install watchdog")

        if state_file is None:
            state_file = str(Path(chroma_dir).parent / ".index_state.json")

        self.knowledge_dir = knowledge_dir
        self.chroma_dir = chroma_dir
        self.state_file = state_file
        self.debounce_seconds = debounce_seconds
        self.on_update = on_update

        self.handler = KnowledgeHandler(
            knowledge_dir, chroma_dir, state_file,
            debounce_seconds, on_update
        )
        self.observer = Observer()
        self._poller_thread: Optional[threading.Thread] = None
        self._stop_poller = threading.Event()

    def start(self, polling_interval: float = 1.0):
        """启动文件监听（后台线程）"""
        self.observer.schedule(self.handler, self.knowledge_dir, recursive=True)
        self.observer.start()
        print(f"[Watcher] 已启动，监听目录: {self.knowledge_dir}")

        # 防抖轮询线程
        def poller():
            while not self._stop_poller.wait(polling_interval):
                self.handler.poll()

        self._poller_thread = threading.Thread(target=poller, daemon=True)
        self._poller_thread.start()

    def stop(self):
        """停止文件监听"""
        self._stop_poller.set()
        self.observer.stop()
        self.observer.join()
        print("[Watcher] 已停止")

    def poll(self):
        """主动触发一次处理（用于启动时先全量索引）"""
        self.handler.poll()


def create_watcher(
    knowledge_dir: Optional[str] = None,
    chroma_dir: Optional[str] = None,
    state_file: Optional[str] = None,
) -> KnowledgeWatcher:
    """工厂函数：创建默认配置的 watcher"""
    base = Path(__file__).parent.parent
    if knowledge_dir is None:
        knowledge_dir = str(base / "knowledge")
    if chroma_dir is None:
        chroma_dir = str(base / "knowledge_base" / "chroma_db")
    if state_file is None:
        state_file = str(base / "knowledge_base" / ".index_state.json")
    return KnowledgeWatcher(knowledge_dir, chroma_dir, state_file)


if __name__ == "__main__":
    # CLI 测试
    watcher = create_watcher()

    def on_update(path, count):
        print(f"[通知] 文件 {path} 已索引，{count} 个片段")

    watcher.handler.on_update = on_update
    watcher.start()

    print("监听中... 按 Ctrl+C 退出")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        watcher.stop()
