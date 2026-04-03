"""
ExecutionTrace - 执行追踪
全链路审计日志，每个操作都有完整记录
"""
import time
import threading
import json
from typing import Optional, Any
from dataclasses import dataclass, field, asdict
from collections import deque


@dataclass
class TraceEntry:
    call_id: str
    timestamp: float
    event: str
    data: dict


class ExecutionTrace:
    """
    执行追踪器

    记录每个 Bot 操作的完整执行链路，供审计和调试

    追踪内容:
    - trigger_input: 触发输入
    - llm_calls: LLM 调用记录
    - tool_calls: 工具调用记录（含 PolicyGate 决策）
    - human_approvals: 人工审批记录
    - final_output: 最终输出
    - token_used / cost / duration
    """

    MAX_ENTRIES = 1000  # 内存中最多保留条数

    def __init__(self, persist_path: Optional[str] = None):
        self._entries: deque = deque(maxlen=self.MAX_ENTRIES)
        self._lock = threading.Lock()
        self._persist_path = persist_path

    def log(self, call_id: str, data: dict):
        """记录一条追踪"""
        entry = TraceEntry(
            call_id=call_id,
            timestamp=time.time(),
            event=data.get("event", "unknown"),
            data=data,
        )
        with self._lock:
            self._entries.append(entry)

        # 可选持久化
        if self._persist_path:
            self._persist(entry)

    def _persist(self, entry: TraceEntry):
        try:
            with open(self._persist_path, "a") as f:
                f.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
        except Exception:
            pass

    def get_recent(self, n: int = 50) -> list[dict]:
        """获取最近 N 条记录"""
        with self._lock:
            entries = list(self._entries)[-n:]
        return [asdict(e) for e in entries]

    def get_by_call_id(self, call_id: str) -> list[dict]:
        """获取特定 call_id 的所有记录"""
        with self._lock:
            return [asdict(e) for e in self._entries if e.call_id == call_id]

    def get_stats(self) -> dict:
        """统计"""
        with self._lock:
            total = len(self._entries)
            events = {}
            for e in self._entries:
                events[e.event] = events.get(e.event, 0) + 1
            return {
                "total_entries": total,
                "events": events,
                "oldest": time.strftime("%H:%M:%S", time.localtime(self._entries[0].timestamp)) if self._entries else None,
                "newest": time.strftime("%H:%M:%S", time.localtime(self._entries[-1].timestamp)) if self._entries else None,
            }

    def clear(self):
        with self._lock:
            self._entries.clear()
