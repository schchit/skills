#!/usr/bin/env python3
"""Create a new bot for CommunityOS from templates."""

import argparse
import os
import sys
import yaml
from pathlib import Path


# Bot SOUL templates
SOUL_TEMPLATES = {
    "helper": """# {{bot_name}} Bot Soul

你是{{bot_name}}，社区运营助手。

**核心职责：**
- 欢迎新人入群
- 定时播报（新闻、天气、资讯）
- 活动公告
- 内容推荐

**性格特点：**
- 热情周到，像体贴的社区管家
- 回答问题专业但不枯燥
- 适当使用 emoji 让对话更有趣
- 如果不确定会诚实说不知道
- 回复简洁，100字以内

**协作方式：**
- 需要技术细节时 @ 其他技术Bot
- 需要活跃气氛时 @ 社区Bot

**回复要求：** 简洁，100字以内
""",
    "moderator": """# {{bot_name}} Bot Soul

你是{{bot_name}}，技术专家。

**核心职责：**
- RAG 问答（必须使用知识库回答问题）
- 技术问题解答
- 代码示例提供
- 上下文补充（主动补充其他Bot的回答）
- 被 @ 时解答专业问题

**性格特点：**
- 技术精湛，回答准确
- 说话简洁直接，不废话
- 喜欢用代码示例说明问题
- 乐于助人

**协作方式：**
- 看到其他Bot的播报可主动补充技术细节
- 复杂问题可转给其他专家

**回复要求：** 简洁，100字以内
""",
    "broadcaster": """# {{bot_name}} Bot Soul

你是{{bot_name}}，社区氛围担当。

**核心职责：**
- 主动分享有趣资讯、点评
- 活跃群内气氛
- 发起话题讨论
- 互相 @ 协作

**性格特点：**
- 活泼开朗，善于活跃气氛
- 喜欢分享有趣资讯
- 偶尔幽默调侃
- 社区至上

**协作方式：**
- 看到技术Bot回答可补充产品/运营视角
- 看到运营Bot播报可发起相关讨论
- 主动 @ 其他Bot协作

**回复要求：** 简洁有趣，100字以内
""",
    "custom": """# {{bot_name}} Bot Soul

你是{{bot_name}}。

**核心职责：**
{{custom_roles}}

**性格特点：**
{{custom_personality}}

**协作方式：**
{{custom_collaboration}}

**回复要求：** 简洁，100字以内
"""
}


def load_bots_config(project_path: Path) -> dict:
    """Load or create bots.yaml config."""
    config_path = project_path / "config" / "bots.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    return {"bots": {}}


def save_bots_config(project_path: Path, config: dict):
    """Save bots.yaml config."""
    config_path = project_path / "config" / "bots.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def create_bot_soul(project_path: Path, bot_id: str, bot_name: str, role: str = "helper"):
    """Generate SOUL.md from template."""
    souls_dir = project_path / "souls"
    souls_dir.mkdir(parents=True, exist_ok=True)
    
    soul_path = souls_dir / f"{bot_id}.md"
    
    if role == "custom":
        template = SOUL_TEMPLATES["custom"].replace("{{bot_name}}", bot_name)
        template = template.replace("{{custom_roles}}", "- (define your roles)")
        template = template.replace("{{custom_personality}}", "- (define your personality)")
        template = template.replace("{{custom_collaboration}}", "- (define collaboration)")
    else:
        template = SOUL_TEMPLATES.get(role, SOUL_TEMPLATES["helper"]).replace("{{bot_name}}", bot_name)
    
    with open(soul_path, "w") as f:
        f.write(template)
    
    return soul_path


def register_bot(project_path: Path, bot_id: str, bot_token: str, role: str = "helper"):
    """Register bot in bots.yaml."""
    config = load_bots_config(project_path)
    
    if "bots" not in config:
        config["bots"] = {}
    
    config["bots"][bot_id] = {
        "token": bot_token,
        "role": role,
        "enabled": True
    }
    
    save_bots_config(project_path, config)


def main():
    parser = argparse.ArgumentParser(description="Create a new CommunityOS bot")
    parser.add_argument("project_path", help="Path to CommunityOS project")
    parser.add_argument("bot_id", help="Bot ID (e.g., assistant)")
    parser.add_argument("bot_name", help="Bot display name (e.g., 小助手)")
    parser.add_argument("--role", "-r", choices=["helper", "moderator", "broadcaster", "custom"],
                        default="helper", help="Bot role template")
    parser.add_argument("--token", "-t", help="Telegram bot token")
    
    args = parser.parse_args()
    
    project_path = Path(args.project_path).resolve()
    
    # Validate project
    if not (project_path / "souls").exists():
        print(f"Error: {project_path} is not a valid CommunityOS project")
        sys.exit(1)
    
    # Create soul
    soul_path = create_bot_soul(project_path, args.bot_id, args.bot_name, args.role)
    print(f"✓ Created soul: {soul_path}")
    
    # Register bot
    if args.token:
        register_bot(project_path, args.bot_id, args.token, args.role)
        print(f"✓ Registered bot in config/bots.yaml")
    else:
        print(f"⚠ No token provided. Add manually to config/bots.yaml:")
        print(f"  {args.bot_id}:")
        print(f"    token: YOUR_BOT_TOKEN")
        print(f"    role: {args.role}")
    
    print(f"\n✅ Bot '{args.bot_name}' created!")
    print(f"   Restart harness: python start_harness.py")


if __name__ == "__main__":
    main()
