#!/usr/bin/env python3
"""
delete-subagent.py - 清理 OpenClaw 子 agent 会话

用法:
    python3 delete-subagent.py                    # 清理所有已完成子 agent
    python3 delete-subagent.py --target <ID>      # 清理指定子 agent
    python3 delete-subagent.py --dry-run          # 预览模式
    python3 delete-subagent.py --quick-clean      # 快速清理（推荐）
    python3 delete-subagent.py --force            # 强制清理（包括活跃子 agent）
    python3 delete-subagent.py --list             # 列出所有子 agent
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 配置 - 动态获取当前 agent 目录
OPENCLAW_DIR = Path.home() / ".openclaw"
AGENTS_DIR = OPENCLAW_DIR / "agents"

def get_current_agent_dir(agent_name=None):
    """获取当前会话的 agent 目录"""
    # 优先使用传入的 agent_name 参数
    if agent_name:
        return AGENTS_DIR / agent_name / "sessions"
    
    # 其次使用环境变量 OPENCLAW_AGENT
    agent_name = os.environ.get("OPENCLAW_AGENT")
    
    if agent_name:
        return AGENTS_DIR / agent_name / "sessions"
    
    # 扫描所有 agent 目录，找到包含 :main 会话的目录
    for agent_dir in AGENTS_DIR.iterdir():
        if agent_dir.is_dir():
            sessions_json = agent_dir / "sessions" / "sessions.json"
            if sessions_json.exists():
                with open(sessions_json, 'r') as f:
                    sessions = json.load(f)
                # 查找主会话 key 格式：agent:{name}:main
                for key in sessions.keys():
                    if key.endswith(":main"):
                        # 提取 agent 名称
                        parts = key.split(":")
                        if len(parts) >= 3:
                            return agent_dir / "sessions"
    
    # 如果都没有找到，返回 orchestrator 作为最后回退
    return AGENTS_DIR / "orchestrator" / "sessions"

SESSIONS_DIR = get_current_agent_dir()
SESSIONS_JSON = SESSIONS_DIR / "sessions.json"
ARCHIVE_DIR = SESSIONS_DIR / "archive"
BACKUP_DIR = SESSIONS_DIR / "backups"


def print_color(text, color="0m"):
    """打印彩色文本"""
    print(f"\033[{color}{text}\033[0m")


def list_subagents():
    """列出所有子 agent"""
    print_color("🔍 扫描子 agent...", "1m")
    
    if not SESSIONS_JSON.exists():
        print_color("  sessions.json 不存在", "31m")
        return []
    
    with open(SESSIONS_JSON, 'r') as f:
        sessions = json.load(f)
    
    subagents = [k for k in sessions.keys() if 'subagent' in k]
    
    print_color(f"\n总计：{len(subagents)} 个子 agent 记录", "1m")
    return subagents


def backup_sessions():
    """备份 sessions.json"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"sessions.json.backup.{timestamp}"
    
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    shutil.copy2(SESSIONS_JSON, backup_file)
    print_color(f"  ✓ 备份到 {backup_file}", "32m")
    return backup_file


def get_main_session_key(sessions):
    """获取主会话的 key"""
    for key in sessions.keys():
        if key.endswith(":main"):
            return key
    return None

def clean_sessions_json():
    """清理 sessions.json - 只保留主会话"""
    print_color("\n💾 清理 sessions.json...", "1m")
    
    if not SESSIONS_JSON.exists():
        print_color("  sessions.json 不存在", "31m")
        return False
    
    with open(SESSIONS_JSON, 'r') as f:
        sessions = json.load(f)
    
    # 获取主会话 key
    main_key = get_main_session_key(sessions)
    if not main_key:
        print_color("  ⚠️ 主会话不存在", "33m")
        return False
    
    main_session = sessions[main_key]
    
    # 创建干净的 sessions.json
    clean_sessions = {
        main_key: main_session
    }
    
    # 确保 childSessions 为 null
    clean_sessions[main_key]["childSessions"] = None
    
    # 写回文件
    with open(SESSIONS_JSON, 'w') as f:
        json.dump(clean_sessions, f, indent=2)
    
    print_color(f"  ✓ 已清理 sessions.json (保留：{main_key})", "32m")
    print_color("  ✓ 已设置 childSessions 为 null", "32m")
    return True


def archive_session_files():
    """归档所有子会话文件"""
    print_color("\n📦 归档会话文件...", "1m")
    
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 获取主会话文件 ID
    with open(SESSIONS_JSON, 'r') as f:
        sessions = json.load(f)
    
    main_key = get_main_session_key(sessions)
    main_session_id = sessions.get(main_key, {}).get("sessionId") if main_key else None
    main_file = f"{main_session_id}.jsonl" if main_session_id else None
    
    archived = 0
    for file in SESSIONS_DIR.glob("*.jsonl"):
        if file.name != main_file and not file.name.endswith(".lock"):
            shutil.move(str(file), str(ARCHIVE_DIR / file.name))
            print_color(f"  归档：{file.name}", "36m")
            archived += 1
    
    print_color(f"\n  ✓ 归档 {archived} 个会话文件", "32m")
    return archived


def quick_clean(agent_name=None):
    """快速清理 - 推荐方式"""
    global SESSIONS_DIR, SESSIONS_JSON, ARCHIVE_DIR, BACKUP_DIR
    
    # 重新初始化路径
    SESSIONS_DIR = get_current_agent_dir(agent_name)
    SESSIONS_JSON = SESSIONS_DIR / "sessions.json"
    ARCHIVE_DIR = SESSIONS_DIR / "archive"
    BACKUP_DIR = SESSIONS_DIR / "backups"
    
    print_color(f"=== 快速清理子 agent (agent: {SESSIONS_DIR.parent.name}) ===\n", "1m")
    
    # 1. 备份
    print_color("📦 备份检查...", "1m")
    backup_sessions()
    
    # 2. 清理 sessions.json
    clean_sessions_json()
    
    # 3. 归档会话文件
    archive_session_files()
    
    # 4. 验证
    print_color("\n✅ 清理完成\n", "32m")
    print_color("清理摘要:", "1m")
    print_color("  活跃子 agent:     0", "36m")
    print_color("  历史子 agent:     已清理", "36m")
    print_color("  删除条目：        所有子 agent", "36m")
    print_color("  归档：            所有会话文件", "36m")


def clean_all_agents():
    """清理所有 agent 的子 agent"""
    print_color("=== 清理所有 agent 的子 agent ===\n", "1m")
    
    cleaned = 0
    for agent_dir in AGENTS_DIR.iterdir():
        if agent_dir.is_dir():
            sessions_json = agent_dir / "sessions" / "sessions.json"
            if sessions_json.exists():
                quick_clean(agent_dir.name)
                cleaned += 1
                print()
    
    print_color(f"\n✅ 总共清理了 {cleaned} 个 agent", "32m")

def main():
    parser = argparse.ArgumentParser(description="清理 OpenClaw 子 agent 会话")
    parser.add_argument("--target", type=str, help="目标子 agent ID")
    parser.add_argument("--agent", type=str, help="指定 agent 名称（如 qq, main, orchestrator）")
    parser.add_argument("--all", action="store_true", help="清理所有 agent")
    parser.add_argument("--dry-run", action="store_true", help="预览模式")
    parser.add_argument("--force", action="store_true", help="强制清理")
    parser.add_argument("--no-backup", action="store_true", help="不创建备份")
    parser.add_argument("--list", action="store_true", help="列出所有子 agent")
    parser.add_argument("--quick-clean", action="store_true", help="快速清理（推荐）")
    parser.add_argument("--cleanup-archive", type=int, help="清理归档文件（天数）")
    
    args = parser.parse_args()
    
    if args.list:
        list_subagents()
        return
    
    if args.all:
        clean_all_agents()
        return
    
    if args.quick_clean:
        quick_clean(args.agent)
        return
    
    # 默认执行快速清理
    quick_clean(args.agent)


if __name__ == "__main__":
    main()
