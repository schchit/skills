"""
GovernanceEngine - 治理引擎总线
整合所有 Harness 组件，提供统一的 Bot 治理接口
"""
import time
import threading
from typing import Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from .circuit_breaker import CircuitBreaker, CircuitOpenError, get_breaker
from .retry_budget import RetryBudget, RetryExhaustedError, get_retry_budget, execute_with_retry
from .policy_gate import PolicyGate, PolicyContext, PolicyDecision, PolicyDeniedError, PolicyEscalatedError
from .token_budget import TokenBudget
from .execution_trace import ExecutionTrace
from .output_gate import OutputGate, OutputDecision


class SessionState(Enum):
    ACTIVE = "active"
    TIMEOUT = "timeout"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class GovernanceConfig:
    """治理配置（可 YAML 驱动）"""
    # 熔断器
    cb_failure_threshold: int = 5
    cb_recovery_timeout: float = 60.0

    # 重试
    max_retries_default: int = 3

    # Token 预算
    max_tokens_per_session: int = 8192
    max_cost_cny_per_session: float = 1.0
    max_messages_per_session: int = 50

    # 超时
    default_timeout: float = 30.0

    # 外部操作
    require_output_gate: bool = True
    require_human_approval_cost: float = 10.0  # 超过此成本需人工审批


class GovernanceEngine:
    """
    CommunityOS 治理引擎

    整合 PolicyGate + CircuitBreaker + RetryBudget + TokenBudget + OutputGate + ExecutionTrace
    所有 Bot 操作通过此引擎执行，确保系统稳定性
    """

    def __init__(self, config: Optional[GovernanceConfig] = None):
        self.config = config or GovernanceConfig()

        # 核心组件
        self.policy_gate = PolicyGate()
        self.token_budget = TokenBudget(
            max_tokens=self.config.max_tokens_per_session,
            max_cost=self.config.max_cost_cny_per_session,
            max_messages=self.config.max_messages_per_session,
        )
        self.output_gate = OutputGate()
        self.trace = ExecutionTrace()

        # 熔断器（按 Bot 分组）
        self._breakers: dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()

        # 会话统计
        self._stats = {
            "total_calls": 0,
            "denied_calls": 0,
            "circuit_open": 0,
            "retry_exhausted": 0,
            "policy_denied": 0,
        }
        self._stats_lock = threading.Lock()

    def get_breaker(self, bot_id: str) -> CircuitBreaker:
        """获取 Bot 的熔断器"""
        with self._lock:
            if bot_id not in self._breakers:
                self._breakers[bot_id] = CircuitBreaker(
                    name=bot_id,
                    failure_threshold=self.config.cb_failure_threshold,
                    recovery_timeout=self.config.cb_recovery_timeout,
                )
            return self._breakers[bot_id]

    # ── 托管执行入口 ────────────────────────────────────

    def execute(
        self,
        bot_id: str,
        bot_role: str,
        tool: str,
        func,
        args: tuple = (),
        kwargs: dict = None,
        ctx: Optional[PolicyContext] = None,
        timeout: Optional[float] = None,
        user_id: Optional[str] = None,
        chat_id: Optional[str] = None,
        chat_type: str = "group",
        is_admin: bool = False,
    ) -> Any:
        """
        托管执行：所有 Bot 操作通过此方法

        流程:
        1. PolicyGate 检查权限
        2. CircuitBreaker 检查熔断状态
        3. RetryBudget 执行（带重试）
        4. TokenBudget 扣减
        5. OutputGate 验证（仅外部行动）
        6. ExecutionTrace 记录
        """
        kwargs = kwargs or {}
        call_id = f"{bot_id}_{tool}_{int(time.time()*1000)}"
        start_time = time.time()

        # 构建策略上下文
        if ctx is None:
            ctx = PolicyContext(
                bot_id=bot_id,
                bot_role=bot_role,
                user_id=user_id,
                chat_id=chat_id,
                chat_type=chat_type,
                is_admin=is_admin,
            )

        # ── 1. PolicyGate ──
        policy_result = self.policy_gate.evaluate(tool, ctx, {"args": args, "kwargs": kwargs})
        if policy_result.decision == PolicyDecision.DENY:
            self._record_stat("denied_calls")
            self._record_stat("policy_denied")
            self.trace.log(call_id, {
                "event": "policy_denied",
                "tool": tool,
                "reason": policy_result.reason,
                "bot_id": bot_id,
            })
            raise PolicyDeniedError(f"[{tool}] {policy_result.reason}", tool=tool, reason=policy_result.reason)

        if policy_result.decision == PolicyDecision.ESCALATE:
            self.trace.log(call_id, {
                "event": "policy_escalated",
                "tool": tool,
                "reason": policy_result.reason,
                "bot_id": bot_id,
            })
            raise PolicyEscalatedError(f"[{tool}] {policy_result.reason}", tool=tool, reason=policy_result.reason)

        # ── 2. CircuitBreaker ──
        breaker = self.get_breaker(bot_id)
        if not breaker.can_execute():
            self._record_stat("circuit_open")
            self.trace.log(call_id, {
                "event": "circuit_open",
                "tool": tool,
                "bot_id": bot_id,
                "breaker_state": breaker.state.value,
            })
            raise CircuitOpenError(f"Bot '{bot_id}' circuit is OPEN")

        # ── 3. TokenBudget ──
        session_key = f"{bot_id}:{chat_id or 'global'}"
        if not self.token_budget.can_execute(session_key):
            self.trace.log(call_id, {
                "event": "token_budget_exceeded",
                "tool": tool,
                "session": session_key,
            })
            raise TokenBudgetExceededError(f"Session budget exceeded for '{session_key}'")

        # ── 4. 执行（带重试）──
        result = None
        error = None
        attempt = 0
        max_attempts = self.config.max_retries_default + 1

        for attempt in range(1, max_attempts + 1):
            try:
                # 尝试通过熔断器执行
                breaker_call = breaker.call
                result = self._try_call(breaker_call, func, args, kwargs)
                break
            except CircuitOpenError:
                raise
            except Exception as e:
                budget = get_retry_budget(tool)
                if not budget.can_retry(tool) or attempt >= max_attempts:
                    error = e
                    self._record_stat("retry_exhausted")
                    breaker.record_failure()
                    break
                # 重试延迟
                delay = budget.get_delay(tool)
                time.sleep(delay)

        if error and result is None:
            self.trace.log(call_id, {
                "event": "call_failed",
                "tool": tool,
                "bot_id": bot_id,
                "attempts": attempt,
                "error": str(error),
                "duration_ms": int((time.time() - start_time) * 1000),
            })
            raise error

        # ── 5. OutputGate（仅外部行动）──
        external_tools = {"send_message", "reply_message", "broadcast", "send_email"}
        if tool in external_tools and self.config.require_output_gate:
            gate_result = self.output_gate.validate(result, ctx)
            if gate_result.decision == OutputDecision.BLOCK:
                self.trace.log(call_id, {
                    "event": "output_blocked",
                    "tool": tool,
                    "reason": gate_result.reason,
                })
                raise OutputBlockedError(f"Output blocked: {gate_result.reason}")

        # ── 6. Token 扣减 ──
        tokens_used = self._estimate_tokens(result)
        cost = self._estimate_cost(tokens_used)
        self.token_budget.consume(session_key, tokens_used, cost)

        # ── 7. ExecutionTrace ──
        self.trace.log(call_id, {
            "event": "call_success",
            "tool": tool,
            "bot_id": bot_id,
            "attempts": attempt,
            "tokens_used": tokens_used,
            "cost_cny": cost,
            "duration_ms": int((time.time() - start_time) * 1000),
            "policy_decision": policy_result.decision.value,
        })
        self._record_stat("total_calls")

        return result

    def _try_call(self, breaker_call, func, args, kwargs):
        """通过熔断器尝试调用"""
        return breaker_call(func, *args, **kwargs)

    def _estimate_tokens(self, result: Any) -> int:
        """粗略估算 tokens"""
        if isinstance(result, str):
            return len(result) // 4  # 粗略
        elif isinstance(result, dict):
            import json
            return len(json.dumps(result)) // 4
        return 0

    def _estimate_cost(self, tokens: int) -> float:
        """粗略估算成本（CNY）"""
        return tokens / 1_000_000 * 0.1  # 假设 $0.1/1M tokens

    def _record_stat(self, key: str):
        with self._stats_lock:
            self._stats[key] = self._stats.get(key, 0) + 1

    def get_status(self) -> dict:
        """获取治理引擎整体状态"""
        with self._lock:
            breakers = {
                bid: b.get_status()
                for bid, b in self._breakers.items()
            }
        return {
            "stats": dict(self._stats),
            "breakers": breakers,
            "token_budget": self.token_budget.get_all_status(),
            "config": {
                "cb_threshold": self.config.cb_failure_threshold,
                "cb_timeout": self.config.cb_recovery_timeout,
                "max_tokens": self.config.max_tokens_per_session,
            }
        }

    def reset_bot(self, bot_id: str):
        """重置 Bot 的所有治理状态"""
        with self._lock:
            if bot_id in self._breakers:
                self._breakers[bot_id].reset()


class TokenBudgetExceededError(Exception):
    pass


class OutputBlockedError(Exception):
    pass
