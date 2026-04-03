"""
Bot 配置解析器
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class BotConfig:
    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        self.bot_id = self.config["bot_id"]
        self.name = self.config.get("name", self.bot_id)
        self.avatar = self.config.get("avatar", "🤖")
        self.soul = self.config.get("soul", "")
        self.modes = self.config.get("modes", {})
        self.knowledge_config = self.config.get("knowledge", {})
        self.llm_config = self.config.get("llm", {})
        self.broadcast_config = self.config.get("broadcast", {})
        self.welcome_config = self.config.get("welcome", {})

    def is_mode_enabled(self, mode: str) -> bool:
        """检查指定模式是否启用"""
        return self.modes.get(mode, False)

    def get_knowledge_folder(self, default: str = "") -> str:
        """获取知识库文件夹"""
        if self.knowledge_config.get("enabled", False):
            return self.knowledge_config.get("folder", default)
        return ""

    def __repr__(self):
        return f"<BotConfig {self.bot_id} ({self.name})>"


class GroupConfig:
    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        self.group_id = self.config["group_id"]
        self.group_name = self.config.get("group_name", self.group_id)
        self.bots = self.config.get("bots", [])
        self.knowledge_folder = self.config.get("knowledge_folder", "")
        self.admin_ids = self.config.get("admin_ids", [])

    def get_bot_modes(self, bot_id: str) -> Dict[str, bool]:
        """获取指定 Bot 在本群启用的模式"""
        for bot in self.bots:
            if bot.get("bot_id") == bot_id:
                return bot.get("modes", {})
        return {}

    def __repr__(self):
        return f"<GroupConfig {self.group_id} ({self.group_name})>"
