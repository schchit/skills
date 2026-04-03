"""
CommunityOS Bot & Group Configuration Parser

解析 config/bots/*.yaml 和 config/groups/*.yaml
提供 BotConfig, GroupConfig 类及合法性验证。
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ConfigError(Exception):
    """配置解析/验证错误基类"""
    pass


class BotConfigError(ConfigError):
    """Bot 配置错误"""
    pass


class GroupConfigError(ConfigError):
    """Group 配置错误"""
    pass


# ---------------------------------------------------------------------------
# Bot Config
# ---------------------------------------------------------------------------

@dataclass
class LLMConfig:
    """LLM 配置"""
    provider: str = "claude_code"
    model: str = "MiniMax-2.7"
    api_key_env: Optional[str] = None   # 从环境变量读取
    temperature: float = 0.7
    max_tokens: int = 2000

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "LLMConfig":
        if data is None:
            return cls()
        return cls(
            provider=data.get("provider", "claude_code"),
            model=data.get("model", "MiniMax-2.7"),
            api_key_env=data.get("api_key_env"),
            temperature=float(data.get("temperature", 0.7)),
            max_tokens=int(data.get("max_tokens", 2000)),
        )


@dataclass
class KnowledgeConfig:
    """知识库配置"""
    enabled: bool = False
    folder: str = ""
    use_rag: bool = False

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "KnowledgeConfig":
        if data is None:
            return cls()
        return cls(
            enabled=bool(data.get("enabled", False)),
            folder=str(data.get("folder", "")),
            use_rag=bool(data.get("use_rag", False)),
        )


@dataclass
class BotModes:
    """Bot 运行模式开关"""
    passive_qa: bool = False
    welcome: bool = False
    join_discussion: bool = False
    boost_atmosphere: bool = False
    scheduled_broadcast: bool = False
    api_data_push: bool = False

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "BotModes":
        if data is None:
            return cls()
        return cls(
            passive_qa=bool(data.get("passive_qa", False)),
            welcome=bool(data.get("welcome", False)),
            join_discussion=bool(data.get("join_discussion", False)),
            boost_atmosphere=bool(data.get("boost_atmosphere", False)),
            scheduled_broadcast=bool(data.get("scheduled_broadcast", False)),
            api_data_push=bool(data.get("api_data_push", False)),
        )

    # 所有已知 mode 键
    KNOWN_KEYS = frozenset([
        "passive_qa", "welcome", "join_discussion",
        "boost_atmosphere", "scheduled_broadcast", "api_data_push",
    ])

    def to_dict(self) -> dict:
        return {
            "passive_qa": self.passive_qa,
            "welcome": self.welcome,
            "join_discussion": self.join_discussion,
            "boost_atmosphere": self.boost_atmosphere,
            "scheduled_broadcast": self.scheduled_broadcast,
            "api_data_push": self.api_data_push,
        }


@dataclass
class BroadcastConfig:
    """定时播报配置"""
    schedule: str = ""          # cron 表达式，空=禁用
    content_source: str = ""    # "api" | "manual" | ""
    api_endpoint: str = ""
    template: str = ""

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "BroadcastConfig":
        if data is None:
            return cls()
        return cls(
            schedule=str(data.get("schedule", "")),
            content_source=str(data.get("content_source", "")),
            api_endpoint=str(data.get("api_endpoint", "")),
            template=str(data.get("template", "")),
        )


@dataclass
class WelcomeConfig:
    """欢迎消息配置"""
    template: str = ""

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "WelcomeConfig":
        if data is None:
            return cls()
        return cls(
            template=str(data.get("template", "")),
        )


@dataclass
class BotConfig:
    """
    单个 Bot 配置，解析自 config/bots/<name>.yaml

    Attributes
    ----------
    bot_id : str
        Bot 唯一标识（文件名即 bot_id）
    name : str
        显示名称
    avatar : str
        头像 emoji
    soul : str
        Bot 角色设定（系统提示词）
    knowledge : KnowledgeConfig
        知识库配置
    llm : LLMConfig
        LLM 调用配置
    modes : BotModes
        运行模式开关
    welcome : WelcomeConfig
        欢迎消息配置
    broadcast : BroadcastConfig
        定时播报配置
    _raw : dict
        原始 YAML dict（用于调试/扩展）
    """

    bot_id: str
    name: str = ""
    avatar: str = ""
    soul: str = ""
    knowledge: KnowledgeConfig = field(default_factory=KnowledgeConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    modes: BotModes = field(default_factory=BotModes)
    welcome: WelcomeConfig = field(default_factory=WelcomeConfig)
    broadcast: BroadcastConfig = field(default_factory=BroadcastConfig)
    _raw: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, bot_id: str, data: dict) -> "BotConfig":
        """从 dict 构造（不读写文件）"""
        # soul 字段支持多行字符串（YAML | 语法）
        soul = data.get("soul", "") or ""
        if isinstance(soul, list):
            soul = "\n".join(str(s) for s in soul)

        return cls(
            bot_id=bot_id,
            name=data.get("name", bot_id),
            avatar=data.get("avatar", ""),
            soul=str(soul).strip(),
            knowledge=KnowledgeConfig.from_dict(data.get("knowledge")),
            llm=LLMConfig.from_dict(data.get("llm")),
            modes=BotModes.from_dict(data.get("modes")),
            welcome=WelcomeConfig.from_dict(data.get("welcome_config")),
            broadcast=BroadcastConfig.from_dict(data.get("broadcast")),
            _raw=data,
        )

    @classmethod
    def from_yaml(cls, path: str | Path) -> "BotConfig":
        """从 YAML 文件加载

        bot_id 优先级：
        1. YAML 内 bot_id 字段（配置文件本身声明的 ID）
        2. 文件名（不含扩展名），作为 fallback
        这样即使 YAML 内 bot_id 与文件名不一致，也能正确解析。
        """
        path = Path(path)
        if not path.exists():
            raise BotConfigError(f"Bot 配置文件不存在: {path}")

        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            raise BotConfigError(f"Bot 配置文件为空: {path}")

        # 优先用 YAML 内声明的 bot_id；无则用文件名（兼容旧格式）
        bot_id = str(data.get("bot_id") or path.stem).strip()
        if not bot_id:
            raise BotConfigError(f"Bot 配置文件无法确定 bot_id: {path}")
        return cls.from_dict(bot_id, data)

    def validate(self) -> list[str]:
        """
        验证配置合法性，返回错误列表（空=通过）。
        """
        errors = []

        if not self.bot_id:
            errors.append("bot_id 不能为空")

        if not self.name:
            errors.append(f"Bot '{self.bot_id}': name 不能为空")

        if self.llm.provider not in SUPPORTED_LLM_PROVIDERS:
            errors.append(
                f"Bot '{self.bot_id}': 不支持的 LLM provider '{self.llm.provider}'，"
                f"支持: {', '.join(SUPPORTED_LLM_PROVIDERS)}"
            )

        if self.llm.temperature < 0 or self.llm.temperature > 2:
            errors.append(
                f"Bot '{self.bot_id}': temperature 应在 [0, 2] 范围，当前={self.llm.temperature}"
            )

        if self.llm.max_tokens < 1:
            errors.append(
                f"Bot '{self.bot_id}': max_tokens 应 > 0，当前={self.llm.max_tokens}"
            )

        # 未知 mode 键
        raw_modes = self._raw.get("modes") or {}
        unknown_keys = set(raw_modes.keys()) - BotModes.KNOWN_KEYS
        if unknown_keys:
            errors.append(
                f"Bot '{self.bot_id}': modes 中存在未知键: {sorted(unknown_keys)}"
            )

        # broadcast schedule 格式（宽松校验，仅非空时检查是否像 cron）
        if self.modes.scheduled_broadcast and self.broadcast.schedule:
            if not _looks_like_cron(self.broadcast.schedule):
                errors.append(
                    f"Bot '{self.bot_id}': broadcast.schedule 格式疑似错误: "
                    f"'{self.broadcast.schedule}'"
                )

        return errors

    def is_valid(self) -> bool:
        """配置是否合法"""
        return len(self.validate()) == 0


# ---------------------------------------------------------------------------
# Group Config
# ---------------------------------------------------------------------------

@dataclass
class BotModeOverride:
    """
    群内单个 Bot 的模式覆盖配置
    （来自 group yaml 的 bots[].modes）
    """
    bot_id: str
    modes: BotModes = field(default_factory=BotModes)

    @classmethod
    def from_dict(cls, data: dict) -> "BotModeOverride":
        return cls(
            bot_id=str(data.get("bot_id", "")),
            modes=BotModes.from_dict(data.get("modes")),
        )


@dataclass
class GroupSettings:
    """群设置"""
    language: str = "zh-CN"
    timezone: str = "Asia/Shanghai"

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "GroupSettings":
        if data is None:
            return cls()
        return cls(
            language=str(data.get("language", "zh-CN")),
            timezone=str(data.get("timezone", "Asia/Shanghai")),
        )


@dataclass
class GroupConfig:
    """
    群配置，解析自 config/groups/<name>.yaml

    Attributes
    ----------
    group_id : str
        Telegram 群 ID（chat_id）
    group_name : str
        群名称
    bots : list[BotModeOverride]
        群内 Bot 及各自的模式覆盖
    knowledge_folder : str
        群专属知识库目录（覆盖 Bot 默认）
    admin_ids : list[str]
        群管理员 user_id 列表
    settings : GroupSettings
        群语言/时区等设置
    _raw : dict
        原始 YAML dict
    """

    group_id: str
    group_name: str = ""
    bots: list[BotModeOverride] = field(default_factory=list)
    knowledge_folder: str = ""
    admin_ids: list[str] = field(default_factory=list)
    settings: GroupSettings = field(default_factory=GroupSettings)
    _raw: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "GroupConfig":
        bots = []
        for b in data.get("bots") or []:
            if not b.get("bot_id"):
                continue          # 跳过无效条目
            bots.append(BotModeOverride.from_dict(b))

        admin_ids_raw = data.get("admin_ids") or []
        admin_ids = [str(a) for a in admin_ids_raw]

        return cls(
            group_id=str(data.get("group_id", "")),
            group_name=str(data.get("group_name", "")),
            bots=bots,
            knowledge_folder=str(data.get("knowledge_folder", "")),
            admin_ids=admin_ids,
            settings=GroupSettings.from_dict(data.get("settings")),
            _raw=data,
        )

    @classmethod
    def from_yaml(cls, path: str | Path) -> "GroupConfig":
        """从 YAML 文件加载"""
        path = Path(path)
        if not path.exists():
            raise GroupConfigError(f"群配置文件不存在: {path}")

        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            raise GroupConfigError(f"群配置文件为空: {path}")

        return cls.from_dict(data)

    def get_bot_modes(self, bot_id: str) -> Optional[BotModes]:
        """
        获取指定 bot 在本群内的模式覆盖。
        若群内未单独配置，返回 None（使用 Bot 默认配置）。
        """
        for b in self.bots:
            if b.bot_id == bot_id:
                return b.modes
        return None

    def validate(self) -> list[str]:
        """验证配置合法性"""
        errors = []

        if not self.group_id:
            errors.append("group_id 不能为空")

        if not self.group_name:
            errors.append(f"群 '{self.group_id}': group_name 不能为空")

        # 检查 bot_id 是否重复
        seen = set()
        for b in self.bots:
            if not b.bot_id:
                errors.append("存在 bot_id 为空的条目")
            elif b.bot_id in seen:
                errors.append(f"Bot '{b.bot_id}' 在本群配置中出现多次")
            else:
                seen.add(b.bot_id)

            # 未知 mode 键
            raw_bots = (self._raw.get("bots") or [])
            for raw_bot in raw_bots:
                if raw_bot.get("bot_id") == b.bot_id:
                    unknown = set((raw_bot.get("modes") or {}).keys()) - BotModes.KNOWN_KEYS
                    if unknown:
                        errors.append(
                            f"群 '{self.group_id}' Bot '{b.bot_id}' modes 中存在未知键: "
                            f"{sorted(unknown)}"
                        )
                    break

        return errors

    def is_valid(self) -> bool:
        """配置是否合法"""
        return len(self.validate()) == 0


# ---------------------------------------------------------------------------
# Loader — 批量加载
# ---------------------------------------------------------------------------

def load_all_bots(config_dir: str | Path = "config/bots") -> dict[str, BotConfig]:
    """
    加载 config_dir 下所有 *.yaml 文件，返回 {bot_id: BotConfig}。

    不合法配置文件会打印警告但不抛异常（以便部分可用）。
    如需严格校验，遍历返回的 dict 逐一调用 .validate()。
    """
    config_dir = Path(config_dir)
    bots: dict[str, BotConfig] = {}

    if not config_dir.is_dir():
        return bots

    for path in sorted(config_dir.glob("*.yaml")):
        try:
            bot = BotConfig.from_yaml(path)
            bots[bot.bot_id] = bot
        except Exception as exc:
            print(f"[WARN] 加载 Bot 配置失败 {path}: {exc}")

    return bots


def load_all_groups(config_dir: str | Path = "config/groups") -> dict[str, GroupConfig]:
    """
    加载 config_dir 下所有 *.yaml 文件，返回 {group_id: GroupConfig}。

    不合法配置文件会打印警告但不抛异常。
    如需严格校验，遍历返回的 dict 逐一调用 .validate()。
    """
    config_dir = Path(config_dir)
    groups: dict[str, GroupConfig] = {}

    if not config_dir.is_dir():
        return groups

    for path in sorted(config_dir.glob("*.yaml")):
        try:
            group = GroupConfig.from_yaml(path)
            groups[group.group_id] = group
        except Exception as exc:
            print(f"[WARN] 加载群配置失败 {path}: {exc}")

    return groups


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

# 目前支持的 LLM provider 列表（可按需扩展）
SUPPORTED_LLM_PROVIDERS = frozenset([
    "claude_code",
    "openai",
    "gemini",
    "deepseek",
    "minimax",
    "local",
])


def _looks_like_cron(expr: str) -> bool:
    """宽松检查是否像 cron 表达式（5-6 个字段）"""
    if not expr or not expr.strip():
        return False
    parts = expr.strip().split()
    # 标准 cron 5段，cron 带秒 6段
    return len(parts) in (5, 6) and all(
        re.match(r"^[\d\-\*,/]+$", p) for p in parts
    )


def resolve_bot_for_group(
    bot: BotConfig,
    group: GroupConfig,
) -> BotModes:
    """
    合并 Bot 默认配置与群级覆盖，返回最终生效的 BotModes。

    规则：
    - 若群内未配置该 Bot，返回 Bot 默认 modes
    - 若群内有配置，取群配置（完全覆盖，非合并）
    """
    override = group.get_bot_modes(bot.bot_id)
    if override is None:
        return bot.modes
    return override


# ---------------------------------------------------------------------------
# CLI 快速测试
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    base = Path(__file__).parent.parent
    bots   = load_all_bots(base / "config" / "bots")
    groups = load_all_groups(base / "config" / "groups")

    print(f"=== Loaded {len(bots)} bots ===")
    for bid, b in bots.items():
        status = "✅" if b.is_valid() else "❌"
        print(f"  {status} [{bid}] {b.name} {b.avatar}")
        for err in b.validate():
            print(f"       ✗ {err}")

    print(f"\n=== Loaded {len(groups)} groups ===")
    for gid, g in groups.items():
        status = "✅" if g.is_valid() else "❌"
        print(f"  {status} [{gid}] {g.group_name}  (bots: {[b.bot_id for b in g.bots]})")
        for err in g.validate():
            print(f"       ✗ {err}")

    print(f"\n=== Demo: resolve_bot_for_group ===")
    for gid, g in groups.items():
        for bot_id in ["panda", "buzz"]:
            if bot_id not in bots:
                continue
            modes = resolve_bot_for_group(bots[bot_id], g)
            active = [k for k, v in modes.to_dict().items() if v]
            print(f"  {gid} + {bot_id}: {active}")
