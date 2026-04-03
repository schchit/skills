#!/usr/bin/env python3
"""
CommunityOS 项目初始化脚本
复制完整框架代码到新项目目录
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

# Skill 资源目录
SKILL_DIR = Path(__file__).parent.parent / "assets" / "templates"


def copy_tree(src: Path, dst: Path, replacements: dict = None):
    """递归复制目录树，可选替换占位符。"""
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.rglob("*"):
        if item.is_file():
            rel = item.relative_to(src)
            dst_file = dst / rel

            # 创建父目录
            dst_file.parent.mkdir(parents=True, exist_ok=True)

            # 如果是文本文件且有替换规则，替换占位符
            if replacements and item.suffix in {".md", ".yaml", ".yml", ".txt", ".sh", ".env"}:
                content = item.read_text(encoding="utf-8")
                for placeholder, value in replacements.items():
                    content = content.replace(placeholder, value)
                dst_file.write_text(content, encoding="utf-8")
            else:
                # 二进制文件直接复制
                shutil.copy2(item, dst_file)


def get_bot_config() -> dict:
    """交互式获取 Bot 配置。"""
    print("\n" + "=" * 50)
    print("🤖 CommunityOS Bot 配置向导")
    print("=" * 50)

    # Bot 1 配置
    print("\n【Bot 1 - 运营助手（Helper）】")
    bot1_id = input("  Bot ID（默认: panda）: ").strip() or "panda"
    bot1_name = input("  Bot 名字（默认: 小P）: ").strip() or "小P"
    bot1_token = input("  Bot Token（从 @BotFather 获取）: ").strip()
    while not bot1_token:
        print("  ⚠ Token 不能为空")
        bot1_token = input("  Bot Token: ").strip()

    # Bot 2 配置
    print("\n【Bot 2 - 技术专家（Moderator）】")
    bot2_id = input("  Bot ID（默认: cypher）: ").strip() or "cypher"
    bot2_name = input("  Bot 名字（默认: Cypher）: ").strip() or "Cypher"
    bot2_token = input("  Bot Token（可选，回车跳过）: ").strip() or ""

    # Bot 3 配置
    print("\n【Bot 3 - 社区活跃（Broadcaster）】")
    bot3_id = input("  Bot ID（默认: buzz）: ").strip() or "buzz"
    bot3_name = input("  Bot 名字（默认: Buzz）: ").strip() or "Buzz"
    bot3_token = input("  Bot Token（可选，回车跳过）: ").strip() or ""

    # 共同配置
    print("\n【共同配置】")
    group_id = input("  Telegram 群 ID（默认: -1001234567890）: ").strip() or "-1001234567890"
    minimax_key = input("  MiniMax API Key: ").strip()
    while not minimax_key:
        print("  ⚠ API Key 不能为空")
        minimax_key = input("  MiniMax API Key: ").strip()

    # 生成替换规则
    replacements = {
        "{{bot1_id}}": bot1_id,
        "{{bot1_name}}": bot1_name,
        "{{bot1_token}}": bot1_token,
        "{{bot1_role}}": "helper",
        "{{bot2_id}}": bot2_id,
        "{{bot2_name}}": bot2_name,
        "{{bot2_token}}": bot2_token,
        "{{bot2_role}}": "moderator",
        "{{bot3_id}}": bot3_id,
        "{{bot3_name}}": bot3_name,
        "{{bot3_token}}": bot3_token,
        "{{bot3_role}}": "broadcaster",
        "{{helper_bot_name}}": bot1_name,
        "{{tech_bot_name}}": bot2_name,
        "{{moderator_bot_name}}": bot2_name,
        "{{community_bot_name}}": bot3_name,
        "{{group_id}}": group_id,
        "{{minimax_api_key}}": minimax_key,
    }

    return replacements, {
        "minimax_key": minimax_key,
        "bots": [
            {"id": bot1_id, "name": bot1_name, "token": bot1_token, "role": "helper"},
            {"id": bot2_id, "name": bot2_name, "token": bot2_token, "role": "moderator"},
            {"id": bot3_id, "name": bot3_name, "token": bot3_token, "role": "broadcaster"},
        ],
        "group_id": group_id,
    }


def init_non_interactive(project_path: Path) -> tuple:
    """非交互式初始化，使用默认值。"""
    replacements = {
        "{{bot1_id}}": "panda",
        "{{bot1_name}}": "小P",
        "{{bot1_token}}": "YOUR_BOT_TOKEN_1",
        "{{bot1_role}}": "helper",
        "{{bot2_id}}": "cypher",
        "{{bot2_name}}": "Cypher",
        "{{bot2_token}}": "YOUR_BOT_TOKEN_2",
        "{{bot2_role}}": "moderator",
        "{{bot3_id}}": "buzz",
        "{{bot3_name}}": "Buzz",
        "{{bot3_token}}": "YOUR_BOT_TOKEN_3",
        "{{bot3_role}}": "broadcaster",
        "{{helper_bot_name}}": "小P",
        "{{tech_bot_name}}": "Cypher",
        "{{moderator_bot_name}}": "Cypher",
        "{{community_bot_name}}": "Buzz",
        "{{group_id}}": "-1001234567890",
        "{{minimax_api_key}}": "YOUR_MINIMAX_API_KEY",
    }
    return replacements


def main():
    parser = argparse.ArgumentParser(description="初始化 CommunityOS 项目")
    parser.add_argument("project_path", help="项目目录路径")
    parser.add_argument("--non-interactive", "-y", action="store_true",
                        help="非交互模式，使用默认配置")
    parser.add_argument("--bots", "-b", type=int, default=3,
                        help="Bot 数量（1-3，默认3）")

    args = parser.parse_args()
    project_path = Path(args.project_path).resolve()

    # 检查目标目录
    if project_path.exists() and any(project_path.iterdir()):
        response = input(f"\n⚠ 目录 {project_path} 已存在且非空。是否继续？（y/N）: ")
        if response.lower() != "y":
            print("取消初始化。")
            sys.exit(0)

    # 检查模板目录
    if not SKILL_DIR.exists():
        print(f"❌ 错误：找不到模板目录 {SKILL_DIR}")
        print("请确保 Skill 已正确安装。")
        sys.exit(1)

    # 获取配置
    if args.non_interactive:
        print("\n🔧 非交互模式，使用默认配置...")
        replacements = init_non_interactive(project_path)
    else:
        replacements, config = get_bot_config()

    # 复制文件
    print(f"\n📁 复制框架代码到 {project_path}...")
    copy_tree(SKILL_DIR, project_path, replacements)
    print("✓ 框架代码已复制")

    # 创建必要的目录
    for subdir in ["knowledge", "chroma_db", "logs"]:
        (project_path / subdir).mkdir(exist_ok=True)

    # 如果是交互模式，生成 bots.yaml
    if not args.non_interactive:
        bots_yaml = project_path / "config" / "bots.yaml"
        if bots_yaml.exists():
            content = bots_yaml.read_text()
            # 只保留有 token 的 bot
            new_lines = []
            for line in content.split("\n"):
                if "token:" in line and "YOUR_BOT_TOKEN" in line:
                    continue
                new_lines.append(line)
            bots_yaml.write_text("\n".join(new_lines))
            print("✓ Bot 配置已生成")

    # 生成 .env 文件
    env_file = project_path / ".env"
    env_content = f"""# CommunityOS 环境变量配置
# 生成时间: 2026-04-02

# MiniMax API Key
MINIMAX_API_KEY={replacements.get('{{minimax_api_key}}', 'YOUR_MINIMAX_API_KEY')}

# Bot Token（从 @BotFather 获取）
BOT_TOKEN={replacements.get('{{bot1_token}}', 'YOUR_BOT_TOKEN')}

# 服务器配置
HOST=0.0.0.0
PORT=8080

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=harness.log
"""
    env_file.write_text(env_content)
    print(f"✓ .env 文件已生成")

    # 生成 README
    readme = project_path / "README.md"
    if readme.exists():
        readme_content = f"""# {project_path.name}

**CommunityOS - Harness Engineering Telegram 多 Bot 协作平台**

## 快速开始

```bash
# 1. 填入 Token
nano .env

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动
python3 start_harness.py
```

## Bot 角色

- **Helper** - 运营助手（{replacements.get('{{helper_bot_name}}', '小P')}）
- **Moderator** - 技术专家（{replacements.get('{{tech_bot_name}}', 'Cypher')}）
- **Broadcaster** - 社区活跃（{replacements.get('{{community_bot_name}}', 'Buzz')}）

## 文件说明

- `harness_os.py` - 核心框架
- `start_harness.py` - 启动脚本
- `souls/` - Bot 灵魂配置
- `config/` - 配置文件
- `harness/` - 治理引擎
- `bot_engine/` - Bot 引擎
- `knowledge_base/` - 知识库 RAG

---
_由 CommunityOS Skill 生成_
"""
        readme.write_text(readme_content)

    print("\n" + "=" * 50)
    print("✅ CommunityOS 项目初始化完成！")
    print("=" * 50)
    print(f"\n📁 项目目录: {project_path}")
    print("\n下一步:")
    print(f"  1. 编辑 .env 填入 Token")
    print(f"  2. pip install -r requirements.txt")
    print(f"  3. python3 start_harness.py")
    print("\n如需交互式配置，重新运行不带 --non-interactive 参数。")


if __name__ == "__main__":
    main()
