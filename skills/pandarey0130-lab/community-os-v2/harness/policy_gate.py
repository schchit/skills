"""
PolicyGate - 策略门
行为治理核心：每次工具调用前必须通过策略检查
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Callable, Any
import threading


class PolicyDecision(Enum):
    ALLOW = "allow"       # 放行
    DENY = "deny"        # 拒绝
    ESCALATE = "escalate"  # 升级（需人工审批）


@dataclass
class PolicyContext:
    """策略评估上下文"""
    bot_id: str
    bot_role: str               # "helper", "moderator", "broadcaster"
    user_id: Optional[str] = None
    chat_id: Optional[str] = None
    chat_type: str = "group"    # "group", "private"
    is_admin: bool = False
    custom_data: dict = field(default_factory=dict)


@dataclass
class PolicyResult:
    decision: PolicyDecision
    reason: str = ""
    metadata: dict = field(default_factory=dict)


class PolicyGate:
    """
    策略门：拦截并评估每个 Bot 操作

    评估三问：
    1. Bot 角色是否有权限调用此工具？
    2. 操作对象是否在允许范围内？
    3. 当前上下文是否允许此操作？
    """

    def __init__(self):
        self._policies: dict[str, Callable] = {}
        self._tool_roles: dict[str, list[str]] = {}  # tool → allowed roles
        self._resource_rules: dict[str, Callable] = {}  # tool → resource validator
        self._lock = threading.Lock()
        self._setup_default_policies()

    def _setup_default_policies(self):
        """设置默认策略"""

        # Bot 角色工具权限映射
        self._tool_roles = {
            "send_message": ["helper", "moderator", "broadcaster"],
            "reply_message": ["helper", "moderator"],
            "kick_user": ["moderator"],
            "ban_user": ["moderator"],
            "broadcast": ["broadcaster"],
            "edit_config": ["admin"],
            "access_knowledge": ["helper", "moderator"],
            "create_invite_link": ["moderator"],
            "pin_message": ["moderator"],
        }

        # 默认放行
        self.set_tool_policy("llm_call", lambda ctx, tool, args: PolicyResult(PolicyDecision.ALLOW))
        self.set_tool_policy("receive_message", lambda ctx, tool, args: PolicyResult(PolicyDecision.ALLOW))
        self.set_tool_policy("access_knowledge", self._check_knowledge_policy)

    def _check_knowledge_policy(self, ctx: PolicyContext, tool: str, args: dict) -> PolicyResult:
        """知识库访问策略：公开组直接放行，私有组需验证"""
        if ctx.chat_type == "private":
            return PolicyResult(PolicyDecision.ALLOW)
        # 群组知识库访问
        return PolicyResult(PolicyDecision.ALLOW, "Group knowledge access permitted")

    def set_tool_policy(self, tool: str, policy_fn: Callable):
        """注册工具的策略函数"""
        with self._lock:
            self._policies[tool] = policy_fn

    def evaluate(self, tool: str, ctx: PolicyContext, args: dict = None) -> PolicyResult:
        """
        评估工具调用是否允许

        Args:
            tool: 工具名称
            ctx: 策略上下文
            args: 工具参数

        Returns:
            PolicyResult: 包含决策和原因
        """
        args = args or {}
        with self._lock:
            # 1. 检查角色权限
            allowed_roles = self._tool_roles.get(tool, [])
            if allowed_roles and ctx.bot_role not in allowed_roles:
                return PolicyResult(
                    PolicyDecision.DENY,
                    f"Bot role '{ctx.bot_role}' not permitted to call '{tool}'. "
                    f"Allowed roles: {allowed_roles}"
                )

            # 2. 检查管理员限制
            admin_only_tools = {"edit_config"}
            if tool in admin_only_tools and not ctx.is_admin:
                return PolicyResult(
                    PolicyDecision.DENY,
                    f"Tool '{tool}' requires admin privileges"
                )

            # 3. 执行自定义策略
            policy_fn = self._policies.get(tool)
            if policy_fn:
                return policy_fn(ctx, tool, args)

            # 4. 默认放行
            return PolicyResult(PolicyDecision.ALLOW, "Default allow")

    def wrap(self, tool: str, func: Callable) -> Callable:
        """
        包装函数，自动注入策略检查

        用法:
            gated_send = policy_gate.wrap("send_message", raw_send_message)
            result = gated_send(ctx, "Hello!")
        """
        def wrapped(ctx: PolicyContext, *args, **kwargs):
            result = self.evaluate(tool, ctx, {"args": args, "kwargs": kwargs})
            if result.decision == PolicyDecision.DENY:
                raise PolicyDeniedError(
                    f"[{tool}] Policy denied: {result.reason}",
                    tool=tool,
                    reason=result.reason,
                )
            if result.decision == PolicyDecision.ESCALATE:
                raise PolicyEscalatedError(
                    f"[{tool}] Policy escalated: {result.reason}",
                    tool=tool,
                    reason=result.reason,
                )
            return func(*args, **kwargs)
        return wrapped

    def get_tool_roles(self) -> dict:
        return dict(self._tool_roles)


class PolicyDeniedError(Exception):
    def __init__(self, message, tool=None, reason=None):
        super().__init__(message)
        self.tool = tool
        self.reason = reason


class PolicyEscalatedError(Exception):
    def __init__(self, message, tool=None, reason=None):
        super().__init__(message)
        self.tool = tool
        self.reason = reason
