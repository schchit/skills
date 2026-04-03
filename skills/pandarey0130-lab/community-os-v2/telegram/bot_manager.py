"""
CommunityOS Bot Manager
Bot 协调层 — 消息路由、Bot 生命周期管理
"""
import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Optional

import yaml
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, Update, ChatMemberUpdated
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("CommunityOS")

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.resolve()


class Config:
    """配置管理"""
    
    def __init__(self):
        self.config = self._load_config()
        self.bots_config = self._load_bots_config()
    
    def _load_config(self) -> dict:
        config_path = PROJECT_ROOT / "config" / "openclaw.json"
        with open(config_path) as f:
            return json.load(f)
    
    def _load_bots_config(self) -> dict:
        config_path = PROJECT_ROOT / "config" / "bots.yaml"
        if not config_path.exists():
            logger.warning("bots.yaml not found, using defaults")
            return {}
        with open(config_path) as f:
            return yaml.safe_load(f)


class MessageBus:
    """共享消息总线 — Bot 间上下文共享"""
    
    def __init__(self, path: str = "telegram/message_bus.json"):
        self.path = PROJECT_ROOT / path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.messages: list[dict] = self._load()
    
    def _load(self) -> list:
        if self.path.exists():
            try:
                with open(self.path) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    
    def save(self):
        # 只保留最近 100 条消息
        self.messages = self.messages[-100:]
        with open(self.path, "w") as f:
            json.dump(self.messages, f, ensure_ascii=False)
    
    def add(self, message: dict):
        self.messages.append(message)
        self.save()
    
    def get_recent(self, limit: int = 20) -> list[dict]:
        return self.messages[-limit:]
    
    def get_for_agent(self, agent_name: str, limit: int = 10) -> list[dict]:
        """获取特定 Bot 相关的最近消息"""
        relevant = []
        for msg in reversed(self.messages):
            if msg.get("agent") == agent_name or msg.get("is_public"):
                relevant.append(msg)
            if len(relevant) >= limit:
                break
        return list(reversed(relevant))


class BotRouter:
    """Bot 消息路由器"""
    
    def __init__(self, config: Config, message_bus: MessageBus):
        self.config = config
        self.bots_config = config.bots_config
        self.message_bus = message_bus
        self.bots: dict[str, Bot] = {}
        self.routers: dict[str, Router] = {}
    
    def _get_telegram_token(self, bot_name: str) -> Optional[str]:
        tokens = {
            "pandora": self.bots_config.get("telegram", {}).get("pandora_token"),
            "cypher": self.bots_config.get("telegram", {}).get("cypher_token"),
            "buzz": self.bots_config.get("telegram", {}).get("buzz_token"),
        }
        return tokens.get(bot_name)
    
    def _get_bot_username(self, bot_name: str) -> Optional[str]:
        usernames = {
            "pandora": self.bots_config.get("telegram", {}).get("pandora_username"),
            "cypher": self.bots_config.get("telegram", {}).get("cypher_username"),
            "buzz": self.bots_config.get("telegram", {}).get("buzz_username"),
        }
        return usernames.get(bot_name)
    
    async def initialize(self):
        """初始化所有 Bot"""
        for bot_name in ["pandora", "cypher", "buzz"]:
            token = self._get_telegram_token(bot_name)
            if not token or token.startswith("YOUR_"):
                logger.warning(f"[{bot_name}] Token not configured, skipping")
                continue
            
            bot = Bot(token=token)
            dispatcher = Dispatcher()
            
            # 注册路由
            router = self._create_router(bot_name)
            dispatcher.include_router(router)
            
            self.bots[bot_name] = bot
            self.routers[bot_name] = router
            
            logger.info(f"[{bot_name}] Bot initialized: @{self._get_bot_username(bot_name)}")
    
    def _create_router(self, bot_name: str) -> Router:
        """为每个 Bot 创建专属路由"""
        router = Router()
        
        # 获取 Bot 用户名
        bot_username = self._get_bot_username(bot_name)
        
        # 通用消息处理
        @router.message()
        async def handle_message(message: Message, state: FSMContext):
            await self._handle_message(bot_name, message)
        
        # 新成员加入处理（熊猫 Bot 专属）
        @router.my_chat_member()
        async def handle_chat_member_update(message: ChatMemberUpdated):
            if bot_name == "pandora":
                await self._handle_new_member(bot_name, message)
        
        # 命令处理
        @router.message(Command("start"))
        async def cmd_start(message: Message):
            await message.answer(
                f"👋 CommunityOS {bot_name.title()} Bot 已启动！\n"
                f"版本: v0.1.0\n"
                f"输入 /help 查看可用命令"
            )
        
        @router.message(Command("help"))
        async def cmd_help(message: Message):
            help_text = self._get_help_text(bot_name)
            await message.answer(help_text)
        
        return router
    
    def _get_help_text(self, bot_name: str) -> str:
        helps = {
            "pandora": (
                "🐼 **Panda 运营 Bot**\n\n"
                "/broadcast - 手动触发播报\n"
                "/status - 查看运营状态\n"
                "/recommend - 内容推荐\n\n"
                "直接发送消息，我会热情回复！"
            ),
            "cypher": (
                "🔐 **Cypher 技术 Bot**\n\n"
                "/search <query> - 搜索知识库\n"
                "/code <topic> - 获取代码示例\n"
                "/doc <topic> - 查看技术文档\n\n"
                "直接 @ 我提问技术问题！"
            ),
            "buzz": (
                "🐝 **Buzz 社区 Bot**\n\n"
                "/news - 最新资讯\n"
                "/poll - 创建投票\n"
                "/topic - 发起话题讨论\n\n"
                "直接发消息，我来活跃气氛！"
            ),
        }
        return helps.get(bot_name, "未知 Bot")
    
    async def _handle_message(self, bot_name: str, message: Message):
        """处理来自用户的消息"""
        if message.chat.type != ChatType.PRIVATE:
            # 群组消息
            if not self._should_respond(bot_name, message):
                return
        
        # 记录到消息总线
        msg_record = {
            "bot": bot_name,
            "chat_id": message.chat.id,
            "user_id": message.from_user.id,
            "text": message.text,
            "is_public": message.chat.type != ChatType.PRIVATE,
        }
        self.message_bus.add(msg_record)
        
        # 构建上下文
        context = self._build_context(bot_name, message)
        
        # 调用对应的 Bot 处理
        handler = self._get_bot_handler(bot_name)
        if handler:
            try:
                response = await handler(bot_name, message, context)
                if response:
                    await message.answer(response)
            except Exception as e:
                logger.error(f"[{bot_name}] Error handling message: {e}")
                await message.answer("抱歉，处理消息时出了点问题 😅")
    
    async def _handle_new_member(self, bot_name: str, message: ChatMemberUpdated):
        """处理新成员加入群组"""
        if message.new_chat_member.status == "member":
            new_user = message.new_chat_member.user
            logger.info(f"[{bot_name}] New member joined: {new_user.full_name}")
            
            # 加载欢迎消息模板
            welcome_template = self.bots_config.get("panda", {}).get(
                "welcome_message",
                "🐼 欢迎 {name} 加入社区！有什么问题随时问我~"
            )
            welcome_msg = welcome_template.format(name=new_user.full_name)
            
            await message.answer(welcome_msg)
    
    def _should_respond(self, bot_name: str, message: Message) -> bool:
        """判断是否应该响应消息"""
        bot_username = self._get_bot_username(bot_name)
        text = message.text or ""
        
        # 检查是否 @ 了当前 Bot
        if message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    mentioned = text[entity.offset:entity.offset + entity.length]
                    if f"@{bot_username}" == mentioned:
                        return True
        
        # 检查是否回复了 Bot 的消息
        if message.reply_to_message and message.reply_to_message.from_user:
            if message.reply_to_message.from_user.username == bot_username:
                return True
        
        # Cypher 对技术关键词敏感
        if bot_name == "cypher":
            tech_keywords = self.bots_config.get("cypher", {}).get("tech_keywords", [])
            if any(kw in text.lower() for kw in tech_keywords):
                return True
        
        # Buzz 对非私聊的公共消息更开放
        if bot_name == "buzz":
            return True
        
        # Panda 只响应特定触发
        if bot_name == "pandora":
            if any(kw in text for kw in ["欢迎", "播报", "公告", "hello", "hi"]):
                return True
        
        return False
    
    def _build_context(self, bot_name: str, message: Message) -> dict:
        """构建消息上下文"""
        recent = self.message_bus.get_recent(limit=10)
        return {
            "bot_name": bot_name,
            "message_text": message.text or "",
            "user_id": message.from_user.id,
            "chat_id": message.chat.id,
            "chat_type": message.chat.type,
            "recent_messages": recent,
        }
    
    def _get_bot_handler(self, bot_name: str):
        """获取 Bot 处理器"""
        handlers = {
            "pandora": self._handle_pandora,
            "cypher": self._handle_cypher,
            "buzz": self._handle_buzz,
        }
        return handlers.get(bot_name)
    
    async def _handle_pandora(self, bot_name: str, message: Message, context: dict) -> Optional[str]:
        """Panda 运营 Bot 处理器"""
        text = message.text or ""
        
        # 加载 Panda SOUL
        soul = self._load_soul("pandora")
        
        # 简单规则判断（后续接入 OpenClaw Agent）
        if "状态" in text or "status" in text.lower():
            return (
                "🐼 **运营状态报告**\n\n"
                f"• 群组数：5\n"
                f"• 成员数：xxx\n"
                f"• 今日播报：3\n"
                f"• 欢迎新成员：12\n\n"
                "一切运行正常！✨"
            )
        
        if "播报" in text or "broadcast" in text.lower():
            return "📢 正在准备播报内容，请稍候..."
        
        # 默认回复（使用 SOUL 风格）
        responses = [
            "🐼 收到！我来帮你处理运营相关的事情~",
            "好的，让我看看有什么可以帮到你的 👀",
            "明白！社区运营的事交给我就好 😊",
        ]
        import random
        return random.choice(responses)
    
    async def _handle_cypher(self, bot_name: str, message: Message, context: dict) -> Optional[str]:
        """Cypher 技术 Bot 处理器"""
        text = message.text or ""
        
        # 加载 Cypher SOUL
        soul = self._load_soul("cypher")
        
        # 知识库搜索
        if "/search" in text:
            query = text.replace("/search", "").strip()
            if query:
                return f"🔍 正在搜索知识库: {query}\n\n[这里将调用 RAG 引擎]"
            return "🔍 请提供搜索关键词，例如: /search Python 异步编程"
        
        # 代码示例
        if "/code" in text:
            topic = text.replace("/code", "").strip()
            if topic:
                return f"💻 关于 {topic} 的代码示例:\n\n[这里将调用 RAG 引擎生成代码]"
            return "💻 请提供主题，例如: /code FastAPI 中间件"
        
        # 默认回复
        responses = [
            "🔐 让我查一下知识库... 🔍",
            "技术问题我帮你看看 💡",
            "这个问题涉及到技术细节，我来详细解答 📚",
        ]
        import random
        return random.choice(responses)
    
    async def _handle_buzz(self, bot_name: str, message: Message, context: dict) -> Optional[str]:
        """Buzz 社区 Bot 处理器"""
        text = message.text or ""
        
        # 加载 Buzz SOUL
        soul = self._load_soul("buzz")
        
        # 资讯分享
        if "资讯" in text or "news" in text.lower():
            return (
                "🐝 **最新资讯** 🐝\n\n"
                "1. 🔥 AI Agent 新突破：OpenClaw 发布多 Agent 协作功能\n"
                "2. 📈 Web3 社区活跃度创历史新高\n"
                "3. 🚀 新技术分享：Chroma + RAG 实战\n\n"
                "想要了解更多？直接问我就好！"
            )
        
        # 发起投票
        if "/poll" in text:
            return "📊 正在创建投票... [功能开发中]"
        
        # 活跃气氛回复
        responses = [
            "🐝 嗨！社区最近有什么新鲜事？",
            "大家好呀！今天想聊点什么？🌟",
            "嘿！看到你在群里超活跃 👍",
            "社区氛围真好！大家都好棒 ✨",
        ]
        import random
        return random.choice(responses)
    
    def _load_soul(self, bot_name: str) -> str:
        """加载 Bot SOUL"""
        soul_path = PROJECT_ROOT / "telegram" / bot_name / "soul.md"
        if soul_path.exists():
            with open(soul_path) as f:
                return f.read()
        return ""
    
    async def start(self):
        """启动所有 Bot"""
        await self.initialize()
        
        if not self.bots:
            logger.error("No bots configured! Please set up tokens in config/bots.yaml")
            return
        
        # 并发启动所有 Bot
        tasks = []
        for bot_name, bot in self.bots.items():
            dispatcher = Dispatcher()
            dispatcher.include_router(self.routers[bot_name])
            tasks.append(self._start_bot(bot, dispatcher, bot_name))
        
        await asyncio.gather(*tasks)
    
    async def _start_bot(self, bot: Bot, dispatcher: Dispatcher, bot_name: str):
        """启动单个 Bot"""
        try:
            logger.info(f"[{bot_name}] Starting polling...")
            await dispatcher.start_polling(bot, handle_as_updates=True)
        except Exception as e:
            logger.error(f"[{bot_name}] Polling error: {e}")


async def main():
    """主入口"""
    logger.info("=" * 50)
    logger.info("CommunityOS Bot Manager 启动中...")
    logger.info("=" * 50)
    
    # 加载配置
    config = Config()
    message_bus = MessageBus()
    
    # 创建 Bot 路由器
    router = BotRouter(config, message_bus)
    
    # 启动
    await router.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("CommunityOS 关闭")
