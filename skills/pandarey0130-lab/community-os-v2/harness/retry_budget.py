"""
RetryBudget - 重试预算
每个工具的调用次数严格限制，防止无限重试
"""
import time
import threading
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RetryBudget:
    """
    重试预算管理器

    每个工具最多重试 N 次，超过则放弃并记录错误
    """
    max_retries: int = 3
    base_delay: float = 1.0      # 基础重试延迟（秒）
    max_delay: float = 30.0      # 最大延迟上限
    exponential_backoff: bool = True

    _attempts: dict[str, int] = field(default_factory=dict, init=False)
    _last_attempt: dict[str, float] = field(default_factory=dict, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def can_retry(self, operation: str) -> bool:
        """检查操作是否还能重试"""
        with self._lock:
            return self._attempts.get(operation, 0) < self.max_retries

    def record_attempt(self, operation: str) -> int:
        """记录一次尝试，返回当前尝试次数"""
        with self._lock:
            count = self._attempts.get(operation, 0) + 1
            self._attempts[operation] = count
            self._last_attempt[operation] = time.time()
            return count

    def get_delay(self, operation: str) -> float:
        """计算下次重试的延迟时间"""
        with self._lock:
            attempt = self._attempts.get(operation, 0)
        if not self.exponential_backoff:
            return self.base_delay
        # 指数退避: 1s, 2s, 4s, 8s...
        delay = min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)
        return delay

    def reset(self, operation: str) -> None:
        """重置操作的计数器（成功后调用）"""
        with self._lock:
            self._attempts.pop(operation, None)
            self._last_attempt.pop(operation, None)

    def get_status(self, operation: str) -> dict:
        with self._lock:
            attempts = self._attempts.get(operation, 0)
            last = self._last_attempt.get(operation)
        return {
            "operation": operation,
            "attempts": attempts,
            "max_retries": self.max_retries,
            "remaining": max(0, self.max_retries - attempts),
            "can_retry": attempts < self.max_retries,
            "last_attempt": time.strftime("%H:%M:%S", time.localtime(last)) if last else None,
        }

    def get_all_status(self) -> dict:
        with self._lock:
            return {op: self.get_status(op) for op in self._attempts}


# ── 默认全局重试预算配置 ─────────────────────────────────
DEFAULT_RETRY_BUDGETS = {
    "telegram_send_message": {"max_retries": 3},
    "telegram_reply": {"max_retries": 2},
    "llm_call": {"max_retries": 2},
    "knowledge_retrieve": {"max_retries": 1},
    "http_request": {"max_retries": 2},
    "index_knowledge": {"max_retries": 1},
}

_global_budgets: dict[str, RetryBudget] = {}
_budgets_lock = threading.Lock()


def get_retry_budget(operation: str) -> RetryBudget:
    """获取或创建操作的重试预算"""
    with _budgets_lock:
        if operation not in _global_budgets:
            cfg = DEFAULT_RETRY_BUDGETS.get(operation, {"max_retries": 2})
            _global_budgets[operation] = RetryBudget(**cfg)
        return _global_budgets[operation]


def execute_with_retry(operation: str, func, *args, **kwargs):
    """
    带重试预算的函数执行
    超过预算后抛出 RetryExhaustedError
    """
    budget = get_retry_budget(operation)
    while True:
        if not budget.can_retry(operation):
            raise RetryExhaustedError(
                f"Retry budget exhausted for '{operation}' "
                f"(max: {budget.max_retries})"
            )
        attempt = budget.record_attempt(operation)
        try:
            result = func(*args, **kwargs)
            budget.reset(operation)
            return result
        except Exception as e:
            if budget.can_retry(operation):
                delay = budget.get_delay(operation)
                time.sleep(delay)
            else:
                raise RetryExhaustedError(
                    f"All retries exhausted for '{operation}' after {attempt} attempts: {e}"
                ) from e


class RetryExhaustedError(Exception):
    """重试预算耗尽时抛出"""
    pass
