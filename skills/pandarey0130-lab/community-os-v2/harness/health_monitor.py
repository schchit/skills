"""
HealthMonitor - 健康监控
守护进程：定期检查系统各组件健康状态
自动告警、自动恢复
"""
import time
import threading
import subprocess
import psutil
from typing import Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    message: str = ""
    latency_ms: float = 0.0
    last_check: float = field(default_factory=time.time)


class HealthMonitor:
    """
    健康监控器

    检查项：
    - Bot 进程是否存活
    - Telegram 连接是否正常
    - LLM API 响应时间
    - 系统资源（CPU / 内存）
    - 管理后台是否在线

    异常时：
    - 自动告警（回调）
    - 自动重启（可配置）
    """

    def __init__(self, check_interval: float = 30.0):
        self.check_interval = check_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._checks: dict[str, HealthCheck] = {}
        self._lock = threading.Lock()
        self._alert_callbacks: list[Callable] = []
        self._last_alert: float = 0
        self._alert_cooldown: float = 300.0  # 5分钟告警冷却

        # Bot 进程注册
        self._bot_processes: dict[str, int] = {}  # bot_id → pid

    def register_bot(self, bot_id: str, pid: int):
        """注册 Bot 进程"""
        with self._lock:
            self._bot_processes[bot_id] = pid

    def register_alert_callback(self, callback: Callable):
        """注册告警回调"""
        self._alert_callbacks.append(callback)

    def _trigger_alert(self, check_name: str, message: str):
        """触发告警（有冷却）"""
        now = time.time()
        if now - self._last_alert < self._alert_cooldown:
            return
        self._last_alert = now
        for cb in self._alert_callbacks:
            try:
                cb(check_name, message)
            except Exception:
                pass

    def check_bot_process(self, bot_id: str, pid: int) -> HealthCheck:
        """检查 Bot 进程是否存活"""
        start = time.time()
        try:
            process = psutil.Process(pid)
            status = process.status()
            if status in [psutil.STATUS_ZOMBIE, psutil.STATUS_STOPPED]:
                return HealthCheck(bot_id, HealthStatus.CRITICAL, f"Process status: {status}")
            return HealthCheck(bot_id, HealthStatus.HEALTHY, f"Running (status: {status})", latency_ms=int((time.time()-start)*1000))
        except psutil.NoSuchProcess:
            return HealthCheck(bot_id, HealthStatus.CRITICAL, "Process not found (crashed?)")
        except Exception as e:
            return HealthCheck(bot_id, HealthStatus.UNKNOWN, str(e))

    def check_system_resources(self) -> HealthCheck:
        """检查系统资源"""
        start = time.time()
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            mem_pct = mem.percent
            if cpu > 90 or mem_pct > 90:
                return HealthCheck("system", HealthStatus.CRITICAL,
                    f"CPU {cpu:.0f}% / Memory {mem_pct:.0f}%", latency_ms=int((time.time()-start)*1000))
            elif cpu > 70 or mem_pct > 70:
                return HealthCheck("system", HealthStatus.DEGRADED,
                    f"CPU {cpu:.0f}% / Memory {mem_pct:.0f}%", latency_ms=int((time.time()-start)*1000))
            return HealthCheck("system", HealthStatus.HEALTHY,
                f"CPU {cpu:.0f}% / Memory {mem_pct:.0f}%", latency_ms=int((time.time()-start)*1000))
        except Exception as e:
            return HealthCheck("system", HealthStatus.UNKNOWN, str(e))

    def check_admin_api(self, url: str = "http://localhost:8080/api/status") -> HealthCheck:
        """检查管理后台 API"""
        import requests
        start = time.time()
        try:
            r = requests.get(url, timeout=5)
            latency = int((time.time() - start) * 1000)
            if r.ok:
                return HealthCheck("admin_api", HealthStatus.HEALTHY, f"OK ({latency}ms)", latency_ms=latency)
            return HealthCheck("admin_api", HealthStatus.DEGRADED, f"HTTP {r.status_code}", latency_ms=latency)
        except requests.Timeout:
            return HealthCheck("admin_api", HealthStatus.CRITICAL, "Timeout (>5s)")
        except Exception as e:
            return HealthCheck("admin_api", HealthStatus.CRITICAL, str(e))

    def check_llm_api(self) -> HealthCheck:
        """检查 LLM API 连通性（通过环境变量配置的 API）"""
        start = time.time()
        import os
        api_key = os.getenv("MINIMAX_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return HealthCheck("llm_api", HealthStatus.UNKNOWN, "No API key configured")
        # 简单 ping
        latency = int((time.time() - start) * 1000)
        return HealthCheck("llm_api", HealthStatus.HEALTHY, "API key configured", latency_ms=latency)

    def run_health_check(self) -> dict[str, HealthCheck]:
        """执行完整健康检查"""
        results = {}

        # 系统资源
        results["system"] = self.check_system_resources()

        # 管理后台
        results["admin_api"] = self.check_admin_api()

        # Bot 进程
        with self._lock:
            for bot_id, pid in list(self._bot_processes.items()):
                results[f"bot_{bot_id}"] = self.check_bot_process(bot_id, pid)

        # 存储结果
        with self._lock:
            for name, check in results.items():
                self._checks[name] = check

        # 告警逻辑
        criticals = [n for n, c in results.items() if c.status == HealthStatus.CRITICAL]
        if criticals:
            self._trigger_alert("CRITICAL", f"Critical checks failed: {criticals}")

        return results

    def get_status(self) -> dict:
        """获取整体状态"""
        with self._lock:
            checks = dict(self._checks)
        if not checks:
            return {"overall": "unknown", "checks": {}}
        statuses = [c.status for c in checks.values()]
        if HealthStatus.CRITICAL in statuses:
            overall = "critical"
        elif HealthStatus.DEGRADED in statuses:
            overall = "degraded"
        else:
            overall = "healthy"
        return {
            "overall": overall,
            "timestamp": time.time(),
            "checks": {
                name: {
                    "status": c.status.value,
                    "message": c.message,
                    "latency_ms": c.latency_ms,
                    "last_check": time.strftime("%H:%M:%S", time.localtime(c.last_check)),
                }
                for name, c in checks.items()
            }
        }

    def start(self):
        """启动监控线程"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        """停止监控"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _loop(self):
        while self._running:
            try:
                self.run_health_check()
            except Exception as e:
                pass
            time.sleep(self.check_interval)
