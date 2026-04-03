"""
Harness 配置
支持 YAML 驱动，所有治理参数可配置化
"""
import yaml
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from .core import GovernanceConfig


DEFAULT_CONFIG = """
# CommunityOS Harness 配置

# ── 熔断器 ──
circuit_breaker:
  failure_threshold: 5      # 连续失败多少次触发熔断
  recovery_timeout: 60       # 冷却时间（秒）
  half_open_max_calls: 3     # 半开状态允许尝试次数

# ── 重试预算 ──
retry_budgets:
  telegram_send_message: 3
  telegram_reply: 2
  llm_call: 2
  knowledge_retrieve: 1
  http_request: 2
  index_knowledge: 1

# ── Token 预算 ──
token_budget:
  max_tokens_per_session: 8192
  max_cost_cny_per_session: 1.0
  max_messages_per_session: 50

# ── 执行超时 ──
execution:
  default_timeout: 30        # 默认执行超时（秒）
  llm_timeout: 60            # LLM 调用超时
  telegram_timeout: 10       # Telegram API 超时

# ── 输出验证 ──
output_gate:
  enabled: true
  telegram_max_length: 4096
  spam_threshold: 3
  spam_window_seconds: 60

# ── 健康监控 ──
health_monitor:
  enabled: true
  check_interval: 30         # 检查间隔（秒）
  alert_cooldown: 300        # 告警冷却（秒）

# ── Bot 角色权限 ──
bot_roles:
  panda:
    role: helper
    is_admin: false
  cypher:
    role: moderator
    is_admin: false
  buzz:
    role: broadcaster
    is_admin: false

# ── 工具权限 ──
tool_permissions:
  - tool: kick_user
    allowed_roles: [moderator]
  - tool: ban_user
    allowed_roles: [moderator]
  - tool: broadcast
    allowed_roles: [broadcaster]
  - tool: edit_config
    allowed_roles: [admin]
"""


@dataclass
class HarnessFullConfig:
    governance: GovernanceConfig = field(default_factory=GovernanceConfig)

    circuit_breaker: dict = field(default_factory=lambda: {
        "failure_threshold": 5,
        "recovery_timeout": 60.0,
        "half_open_max_calls": 3,
    })

    retry_budgets: dict = field(default_factory=dict)

    token_budget: dict = field(default_factory=lambda: {
        "max_tokens_per_session": 8192,
        "max_cost_cny_per_session": 1.0,
        "max_messages_per_session": 50,
    })

    execution: dict = field(default_factory=lambda: {
        "default_timeout": 30.0,
        "llm_timeout": 60.0,
        "telegram_timeout": 10.0,
    })

    output_gate: dict = field(default_factory=lambda: {
        "enabled": True,
        "telegram_max_length": 4096,
        "spam_threshold": 3,
    })

    health_monitor: dict = field(default_factory=lambda: {
        "enabled": True,
        "check_interval": 30.0,
    })

    bot_roles: dict = field(default_factory=dict)

    tool_permissions: list = field(default_factory=list)


def load_harness_config(path: Optional[str] = None) -> HarnessFullConfig:
    """从 YAML 文件加载配置"""
    if path:
        p = Path(path)
        if p.exists():
            with open(p) as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}
    else:
        data = {}

    return _merge_config(data)


def _merge_config(data: dict) -> HarnessFullConfig:
    cfg = HarnessFullConfig()

    if "circuit_breaker" in data:
        cfg.circuit_breaker = data["circuit_breaker"]

    if "retry_budgets" in data:
        cfg.retry_budgets = data["retry_budgets"]

    if "token_budget" in data:
        tb = data["token_budget"]
        cfg.governance.max_tokens_per_session = tb.get("max_tokens_per_session", 8192)
        cfg.governance.max_cost_cny_per_session = tb.get("max_cost_cny_per_session", 1.0)
        cfg.governance.max_messages_per_session = tb.get("max_messages_per_session", 50)

    if "execution" in data:
        ex = data["execution"]
        cfg.execution = ex
        cfg.governance.default_timeout = ex.get("default_timeout", 30.0)

    if "output_gate" in data:
        cfg.output_gate = data["output_gate"]
        cfg.governance.require_output_gate = cfg.output_gate.get("enabled", True)

    if "health_monitor" in data:
        cfg.health_monitor = data["health_monitor"]

    if "bot_roles" in data:
        cfg.bot_roles = data["bot_roles"]

    if "tool_permissions" in data:
        cfg.tool_permissions = data["tool_permissions"]

    # Circuit breaker
    cb = cfg.circuit_breaker
    cfg.governance.cb_failure_threshold = cb.get("failure_threshold", 5)
    cfg.governance.cb_recovery_timeout = cb.get("recovery_timeout", 60.0)

    return cfg


def save_default_config(path: str):
    """保存默认配置到文件"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(DEFAULT_CONFIG)
