"""
Bot 管理器 — 总管理器
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from .bot_instance import BotInstance
from .config_parser import BotConfig, GroupConfig


class BotManager:
    def __init__(self, config_dir: str, base_dir: Optional[str] = None):
        self.base_dir = base_dir or config_dir
        self.config_dir = config_dir

        # 加载所有 Bot 配置
        bots_dir = os.path.join(config_dir, "bots")
        self.bot_configs: Dict[str, str] = {}
        if os.path.exists(bots_dir):
            for fname in os.listdir(bots_dir):
                if fname.endswith(".yaml") or fname.endswith(".yml"):
                    fpath = os.path.join(bots_dir, fname)
                    try:
                        cfg = BotConfig(fpath)
                        self.bot_configs[cfg.bot_id] = fpath
                        print(f"加载 Bot: {cfg.bot_id} ({cfg.name})")
                    except Exception as e:
                        print(f"加载 Bot 配置失败 {fname}: {e}")

        # 加载所有群配置
        groups_dir = os.path.join(config_dir, "groups")
        self.group_configs: Dict[str, GroupConfig] = {}
        if os.path.exists(groups_dir):
            for fname in os.listdir(groups_dir):
                if fname.endswith(".yaml") or fname.endswith(".yml"):
                    fpath = os.path.join(groups_dir, fname)
                    try:
                        cfg = GroupConfig(fpath)
                        self.group_configs[cfg.group_id] = cfg
                        print(f"加载群: {cfg.group_name} ({cfg.group_id})")
                    except Exception as e:
                        print(f"加载群配置失败 {fname}: {e}")

        # Bot 实例缓存: {(bot_id, group_id): BotInstance}
        self._instances: Dict[tuple, BotInstance] = {}

    def get_bot_instance(self, bot_id: str, group_id: Optional[str] = None) -> Optional[BotInstance]:
        """获取 Bot 实例"""
        key = (bot_id, group_id)
        if key in self._instances:
            return self._instances[key]

        if bot_id not in self.bot_configs:
            return None

        bot_config_path = self.bot_configs[bot_id]
        group_config = self.group_configs.get(group_id) if group_id else None

        try:
            instance = BotInstance(bot_config_path, group_config, self.base_dir)
            self._instances[key] = instance
            return instance
        except Exception as e:
            print(f"创建 Bot 实例失败 {bot_id}: {e}")
            return None

    def get_group_bots(self, group_id: str) -> List[BotInstance]:
        """获取群里所有 Bot 实例"""
        group_cfg = self.group_configs.get(group_id)
        if not group_cfg:
            return []

        bots = []
        for bot in group_cfg.bots:
            bot_id = bot.get("bot_id")
            instance = self.get_bot_instance(bot_id, group_id)
            if instance:
                bots.append(instance)
        return bots

    def process_message(
        self,
        chat_id: str,
        message: str,
        bot_ids: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """
        处理收到的群消息
        返回: [{"bot_id": "...", "response": "..."}]
        
        当 bot_ids 被指定时，只让这些 Bot 处理（@ 协作逻辑）
        其他 Bot 也会收到 context 通知（用于感知）
        """
        context = context or {}
        results = []
        mentioned_bots = context.get("mentioned_bot_ids", [])

        bots = self.get_group_bots(chat_id) if chat_id in self.group_configs else []

        if bot_ids:
            # @ 指定了特定 Bot，只让目标 Bot 处理
            bots = [b for b in bots if b.config.bot_id in bot_ids]
            
            for bot in bots:
                try:
                    # 使用 respond_to_mention 方法处理被 @ 的情况
                    response = bot.respond_to_mention(message, context)
                    if response:
                        results.append({
                            "bot_id": bot.config.bot_id,
                            "bot_name": bot.config.name,
                            "avatar": bot.config.avatar,
                            "response": response
                        })
                except Exception as e:
                    print(f"Bot {bot.config.bot_id} 处理 @ 消息失败: {e}")
        else:
            # 没有 @，所有 Bot 按配置决定是否响应
            for bot in bots:
                try:
                    if bot.should_respond(message, is_new_member=context.get("is_new_member", False)):
                        response = bot.generate_response(message, context)
                        if response:
                            results.append({
                                "bot_id": bot.config.bot_id,
                                "bot_name": bot.config.name,
                                "avatar": bot.config.avatar,
                                "response": response
                            })
                except Exception as e:
                    print(f"Bot {bot.config.bot_id} 处理消息失败: {e}")

        return results

    def list_bots(self) -> List[str]:
        """列出所有已加载的 Bot ID"""
        return list(self.bot_configs.keys())

    def list_groups(self) -> List[str]:
        """列出所有已加载的群 ID"""
        return list(self.group_configs.keys())


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(base_dir, "config")
    manager = BotManager(config_dir, base_dir)
    print(f"已加载 Bots: {manager.list_bots()}")
    print(f"已加载 Groups: {manager.list_groups()}")
