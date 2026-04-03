"""
TokenBudget - 会话 Token 预算
防止单个会话消耗过多资源
"""
import threading
import time
from dataclasses import dataclass, field


@dataclass
class SessionBudget:
    tokens_used: int = 0
    cost_used: float = 0.0
    messages_count: int = 0
    first_used: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)


class TokenBudget:
    """
    Token/成本预算管理器

    限制每个会话的最大消耗，超过则拒绝新操作
    """

    def __init__(
        self,
        max_tokens: int = 8192,
        max_cost: float = 1.0,
        max_messages: int = 50,
    ):
        self.max_tokens = max_tokens
        self.max_cost = max_cost
        self.max_messages = max_messages
        self._sessions: dict[str, SessionBudget] = {}
        self._lock = threading.Lock()

    def can_execute(self, session_key: str) -> bool:
        """检查会话是否还有预算"""
        with self._lock:
            budget = self._sessions.get(session_key)
            if not budget:
                return True
            return (
                budget.tokens_used < self.max_tokens
                and budget.cost_used < self.max_cost
                and budget.messages_count < self.max_messages
            )

    def consume(self, session_key: str, tokens: int, cost: float = 0.0):
        """消费 Token"""
        with self._lock:
            if session_key not in self._sessions:
                self._sessions[session_key] = SessionBudget()
            b = self._sessions[session_key]
            b.tokens_used += tokens
            b.cost_used += cost
            b.messages_count += 1
            b.last_used = time.time()

    def get_status(self, session_key: str) -> dict:
        with self._lock:
            b = self._sessions.get(session_key)
            if not b:
                return {"session": session_key, "exists": False}
            return {
                "session": session_key,
                "exists": True,
                "tokens_used": b.tokens_used,
                "tokens_max": self.max_tokens,
                "tokens_pct": round(b.tokens_used / self.max_tokens * 100, 1),
                "cost_used": round(b.cost_used, 4),
                "cost_max": self.max_cost,
                "messages": b.messages_count,
                "messages_max": self.max_messages,
            }

    def get_all_status(self) -> dict:
        with self._lock:
            return {k: self.get_status(k) for k in self._sessions}

    def reset(self, session_key: str):
        with self._lock:
            self._sessions.pop(session_key, None)

    def reset_all(self):
        with self._lock:
            self._sessions.clear()
