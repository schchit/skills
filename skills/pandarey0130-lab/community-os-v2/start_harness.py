#!/usr/bin/env python3
"""
CommunityOS Multi-Bot Starter - Harness Engineering Mode
=========================================================
使用 Harness Engineering 模式启动所有 Bot

用法:
    python start_harness.py              # 启动所有 Bot
    python start_harness.py panda        # 只启动 panda
"""
import os
import sys
import time
import signal
import subprocess
import logging
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class HarnessBotManager:
    """
    Harness Engineering 模式的多 Bot 管理器
    
    特性：
    - 统一初始化 HarnessOS
    - 独立进程运行每个 Bot
    - 治理引擎集中管理
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.processes: Dict[str, subprocess.Popen] = {}
        self.bots = ["panda", "cypher", "buzz", "Quantkeybot"]
        self.tokens = self._load_tokens()
    
    def _load_tokens(self) -> Dict[str, str]:
        """加载 Bot Token"""
        return {
            "panda": os.environ.get("PANDORA_TOKEN", ""),
            "cypher": os.environ.get("CYPHER_TOKEN", ""),
            "buzz": os.environ.get("BUZZ_TOKEN", ""),
            "Quantkeybot": os.environ.get("QUANTKEY_TOKEN", ""),
        }
    
    def _check_tokens(self) -> bool:
        """检查 Token 配置"""
        missing = [b for b, t in self.tokens.items() if not t]
        if missing:
            logger.warning(f"⚠️ 以下 Bot 未配置 Token: {', '.join(missing)}")
            logger.warning("请设置环境变量: PANDORA_TOKEN, CYPHER_TOKEN, BUZZ_TOKEN, QUANTKEY_TOKEN")
            return False
        return True
    
    def start_bot(self, bot_id: str) -> subprocess.Popen:
        """启动单个 Bot"""
        script = self.base_dir / "run_harness_bot.py"
        
        env = os.environ.copy()
        env["SINGLE_BOT_ID"] = bot_id
        
        proc = subprocess.Popen(
            [sys.executable, str(script), bot_id],
            cwd=str(self.base_dir),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        logger.info(f"🚀 启动 {bot_id} (PID: {proc.pid})")
        return proc
    
    def start_all(self, specific_bot: str = None):
        """启动所有 Bot"""
        if not self._check_tokens():
            logger.error("❌ Token 配置不完整，无法启动")
            return False
        
        bots_to_start = [specific_bot] if specific_bot else self.bots
        
        logger.info("=" * 60)
        logger.info("🚀 CommunityOS (Harness Engineering Mode)")
        logger.info("=" * 60)
        
        for bot_id in bots_to_start:
            if bot_id not in self.tokens:
                logger.error(f"❌ 未知 Bot: {bot_id}")
                continue
            
            if not self.tokens[bot_id]:
                logger.warning(f"⏭️ 跳过 {bot_id} (未配置 Token)")
                continue
            
            try:
                proc = self.start_bot(bot_id)
                self.processes[bot_id] = proc
                time.sleep(1)  # 错开启动
            except Exception as e:
                logger.error(f"❌ 启动 {bot_id} 失败: {e}")
        
        if self.processes:
            logger.info("=" * 60)
            logger.info(f"✅ 已启动 {len(self.processes)} 个 Bot")
            logger.info(f"   Bots: {', '.join(self.processes.keys())}")
            logger.info("=" * 60)
            return True
        else:
            logger.error("❌ 没有 Bot 成功启动")
            return False
    
    def stream_output(self):
        """实时输出所有 Bot 日志"""
        import select
        
        streams = {p.stdout: name for name, p in self.processes.items() if p.stdout}
        
        try:
            while self.processes:
                readable, _, _ = select.select(list(streams.keys()), [], [], 1)
                
                for stream in readable:
                    name = streams[stream]
                    line = stream.readline()
                    
                    if line:
                        print(f"[{name}] {line.rstrip()}")
                    else:
                        proc = self.processes[name]
                        proc.wait()
                        
                        if proc.returncode != 0:
                            logger.warning(f"⚠️ Bot {name} 已退出，code={proc.returncode}")
                        
                        del self.processes[name]
                        del streams[stream]
                        
                        if not streams:
                            logger.info("所有 Bot 已停止")
                            return
        except KeyboardInterrupt:
            self.stop_all()
    
    def stop_all(self):
        """停止所有 Bot"""
        logger.info("🛑 正在停止所有 Bot...")
        
        for name, proc in self.processes.items():
            logger.info(f"   停止 {name}...")
            proc.terminate()
            
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        
        self.processes.clear()
        logger.info("✅ 所有 Bot 已停止")


def main():
    specific_bot = sys.argv[1] if len(sys.argv) > 1 else None
    
    # 检查 Python 版本
    if sys.version_info < (3, 10):
        logger.error("❌ 需要 Python 3.10+")
        sys.exit(1)
    
    manager = HarnessBotManager()
    
    # 信号处理
    def signal_handler(signum, frame):
        logger.info("收到退出信号...")
        manager.stop_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动
    if manager.start_all(specific_bot):
        manager.stream_output()


if __name__ == "__main__":
    main()
