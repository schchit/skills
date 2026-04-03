"""
CircuitBreaker - 熔断器
防止 Bot 操作进入"847次重试"死循环
"""
import time
import threading
from enum import Enum
from typing import Optional, Callable, Any
from dataclasses import dataclass, field


class CircuitState(Enum):
    CLOSED = "closed"      # 正常：放行所有请求
    OPEN = "open"          # 熔断：拒绝所有请求
    HALF_OPEN = "half_open"  # 半开：尝试恢复


@dataclass
class CircuitBreaker:
    """
    熔断器实现

    状态机:
        CLOSED → (连续失败 N 次) → OPEN
        OPEN → (冷却时间后) → HALF_OPEN
        HALF_OPEN → (成功) → CLOSED
        HALF_OPEN → (失败) → OPEN
    """
    name: str
    failure_threshold: int = 5        # 触发熔断的连续失败次数
    recovery_timeout: float = 60.0   # 冷却时间（秒）
    half_open_max_calls: int = 3     # 半开状态允许的尝试次数

    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_count: int = field(default=0, init=False)
    _success_count: int = field(default=0, init=False)
    _last_failure_time: float = field(default=0.0, init=False)
    _half_open_calls: int = field(default=0, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def record_success(self) -> None:
        """记录一次成功调用"""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.half_open_max_calls:
                    self._transition_to(CircuitState.CLOSED)
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0

    def record_failure(self) -> None:
        """记录一次失败调用"""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)
            elif self._state == CircuitState.CLOSED:
                self._failure_count += 1
                if self._failure_count >= self.failure_threshold:
                    self._transition_to(CircuitState.OPEN)

    def can_execute(self) -> bool:
        """检查是否可以执行"""
        with self._lock:
            if self._state == CircuitState.CLOSED:
                return True
            elif self._state == CircuitState.OPEN:
                # 检查冷却时间
                if time.time() - self._last_failure_time >= self.recovery_timeout:
                    self._transition_to(CircuitState.HALF_OPEN)
                    return True
                return False
            elif self._state == CircuitState.HALF_OPEN:
                return self._half_open_calls < self.half_open_max_calls
            return False

    def _transition_to(self, new_state: CircuitState) -> None:
        """状态转换"""
        if self._state == new_state:
            return
        self._state = new_state
        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
            self._half_open_calls = 0
        elif new_state == CircuitState.OPEN:
            self._last_failure_time = time.time()
            self._failure_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._half_open_calls = 0
            self._success_count = 0

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        通过熔断器执行函数
        如果熔断则抛出 CircuitOpenError
        """
        if not self.can_execute():
            raise CircuitOpenError(f"CircuitBreaker '{self.name}' is OPEN")

        try:
            with self._lock:
                if self._state == CircuitState.HALF_OPEN:
                    self._half_open_calls += 1

            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise

    @property
    def state(self) -> CircuitState:
        with self._lock:
            return self._state

    def get_status(self) -> dict:
        with self._lock:
            return {
                "name": self.name,
                "state": self._state.value,
                "failure_count": self._failure_count,
                "last_failure": time.strftime("%H:%M:%S", time.localtime(self._last_failure_time))
                                if self._last_failure_time else None,
            }

    def reset(self) -> None:
        with self._lock:
            self._transition_to(CircuitState.CLOSED)


class CircuitOpenError(Exception):
    """熔断器打开时抛出"""
    pass


# ── 全局熔断器注册表 ─────────────────────────────────────
_breakers: dict[str, CircuitBreaker] = {}
_breakers_lock = threading.Lock()


def get_breaker(name: str, **kwargs) -> CircuitBreaker:
    """获取或创建命名熔断器"""
    with _breakers_lock:
        if name not in _breakers:
            _breakers[name] = CircuitBreaker(name=name, **kwargs)
        return _breakers[name]


def get_all_breakers() -> dict[str, CircuitBreaker]:
    return dict(_breakers)
