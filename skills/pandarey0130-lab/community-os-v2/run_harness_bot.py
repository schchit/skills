#!/usr/bin/env python3
"""
CommunityOS Bot Runner - Harness Engineering Mode
=================================================
使用 Harness Engineering 模式运行 Bot

用法:
    python run_harness_bot.py panda
    python run_harness_bot.py cypher
    python run_harness_bot.py buzz
"""
import os
import sys
import asyncio
import signal
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("telegram.bot")

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from harness_os import HarnessOS, BotAgent


class TelegramBot:
    """Telegram Bot 包装器 - 与 HarnessOS 集成"""
    
    def __init__(self, bot_id: str, token: str, os_instance: HarnessOS):
        self.bot_id = bot_id
        self.token = token
        self.os = os_instance
        self.agent = os_instance.get_bot(bot_id)
        
        if not self.agent:
            raise ValueError(f"Bot {bot_id} not found")
    
    async def start(self):
        """启动 Bot"""
        from telegram import Bot
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        
        app = (
            Application.builder()
            .token(self.token)
            .read_timeout(60)
            .write_timeout(60)
            .build()
        )
        
        # 获取 Bot 信息
        bot = Bot(self.token)
        me = await bot.getMe()
        print(f"✅ {self.bot_id} Bot 已连接 (@{me.username})")
        print(f"   Role: {self.agent.role.value}")
        print(f"   Governance: {self.agent.config.role.value}")
        
        # 命令处理器
        async def handle_start(update, ctx):
            await update.message.reply_text(
                f"👋 你好！我是 {self.bot_id}\n"
                f"角色: {self.agent.role.value}\n\n"
                f"直接发送问题或 @ 我，我会尽力回答！"
            )
        
        async def handle_help(update, ctx):
            await update.message.reply_text(
                f"📖 {self.bot_id} 帮助\n\n"
                f"直接发送问题，我会用 AI 帮你回答\n"
                f"可用工具: {', '.join(self.os.tools.list_tools(self.agent.role))}"
            )
        
        async def handle_status(update, ctx):
            status = self.agent.get_status()
            await update.message.reply_text(
                f"📊 Bot 状态\n\n"
                f"ID: {status['bot_id']}\n"
                f"角色: {status['role']}\n"
                f"历史消息: {status['history_count']}"
            )
        
        # 消息处理器
        async def handle_message(update, ctx):
            if not update.message or not update.message.text:
                return
            
            text = update.message.text.strip()
            if not text:
                return
            
            # 私聊白名单（允许私聊的用户ID）
            ADMIN_USERS = [YOUR_TELEGRAM_ID]  # Replace with your Telegram user ID
            
            # 私聊权限检查
            if update.message.chat.type == "private":
                if update.message.from_user.id not in ADMIN_USERS:
                    await update.message.reply_text("⚠️ 本Bot仅在群组中使用，不提供私聊服务。")
                    return
            
            # 调试：打印收到的群消息
            print(f"[DEBUG] 消息 from {update.message.from_user.username} [{update.message.chat.type}]: {update.message.text}")
            print(f"[DEBUG] Bot username: @{ctx.bot.username}")
            
            # 群组模式：移除@也能回复
            if update.message.chat.type != "private":
                text = text.replace(f"@{ctx.bot.username}", "").strip()
            
            # 发送处理中状态
            status_msg = await update.message.reply_text("🤔 思考中...")
            
            try:
                # 通过 HarnessOS 处理
                response = await self.agent.handle_message(
                    message=text,
                    user_id=str(update.message.from_user.id),
                    chat_type="group" if update.message.chat.type != "private" else "private",
                    is_mentioned=False,  # 群组无需@也能回复
                    chat_id=str(update.message.chat.id),  # 传入真实chat_id用于知识库查找
                )
                
                if response:
                    await update.message.reply_text(response[:2000])
            except Exception as e:
                await update.message.reply_text(f"⚠️ 出错了: {str(e)[:100]}")
            finally:
                try:
                    await status_msg.delete()
                except:
                    pass
        
        # 注册处理器
        app.add_handler(CommandHandler("start", handle_start))
        app.add_handler(CommandHandler("help", handle_help))
        app.add_handler(CommandHandler("status", handle_status))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # 启动
        print(f"🚀 {self.bot_id} 开始监听消息...")
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        
        # 保持运行
        await asyncio.Event().wait()


async def main():
    """主入口"""
    bot_id = sys.argv[1] if len(sys.argv) > 1 else "panda"
    
    # 获取 Token（优先从环境变量，其次从 .env 文件）
    _env_file = Path(__file__).parent / ".env"
    if _env_file.exists():
        with open(_env_file) as _f:
            for line in _f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

    tokens = {
        "panda": os.environ.get("PANDORA_TOKEN", "") or os.environ.get("TELEGRAM_BOT_TOKEN_PANDA", ""),
        "cypher": os.environ.get("CYPHER_TOKEN", "") or os.environ.get("TELEGRAM_BOT_TOKEN_CYPHER", ""),
        "buzz": os.environ.get("BUZZ_TOKEN", "") or os.environ.get("TELEGRAM_BOT_TOKEN_BUZZ", ""),
        "quantkey": os.environ.get("QUANTKEY_TOKEN", ""),
        "Quantkeybot": os.environ.get("QUANTKEY_TOKEN", "") or os.environ.get("TELEGRAM_BOT_TOKEN_QUANTKEYBOT", "") or os.environ.get("BUZZ_TOKEN", ""),
    }
    token = tokens.get(bot_id, "")
    
    if not token:
        print(f"❌ 未找到 {bot_id} 的 Token")
        print(f"请设置环境变量: PANDORA_TOKEN / CYPHER_TOKEN / BUZZ_TOKEN")
        sys.exit(1)
    
    # 设置 MiniMax API Key
    if not os.environ.get("MINIMAX_API_KEY"):
        os.environ["MINIMAX_API_KEY"] = "YOUR_MINIMAX_API_KEY"
    
    # 初始化 HarnessOS
    print(f"🔧 初始化 CommunityOS (Harness Mode)...")
    config_path = Path(__file__).parent / "config" / "harness.yaml"
    os_instance = HarnessOS(str(config_path) if config_path.exists() else None)
    
    # 创建 Bot
    bot = TelegramBot(bot_id, token, os_instance)
    
    # 信号处理
    loop = asyncio.get_event_loop()
    
    def signal_handler():
        print(f"\n🛑 {bot_id} 正在停止...")
        sys.exit(0)
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)
    
    # 启动
    try:
        await bot.start()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
