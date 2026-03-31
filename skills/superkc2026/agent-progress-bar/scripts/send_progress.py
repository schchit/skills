#!/usr/bin/env python3
"""
进度汇报发送脚本
用法: python3 send_progress.py <当前步骤> <总步骤数> <步骤名称> <target用户ID> <channel>

示例:
python3 send_progress.py 1 5 "读取数据" 202112031231256514ec16 meishi
"""

import sys
import subprocess
import json
import datetime

def get_progress_bar(current: int, total: int) -> str:
    """生成进度条"""
    if total <= 0:
        total = 1
    percentage = min(int(current / total * 100), 100)
    filled = int(current / total * 20)
    bar = "█" * filled + "░" * (20 - filled)
    return f"[{bar}] {percentage:3d}%"

def get_status_table(current: int, total: int, step_names: list) -> str:
    """生成状态表格"""
    lines = []
    for i, name in enumerate(step_names, 1):
        if i < current:
            status = "✅ 已完成"
        elif i == current:
            remaining = total - current
            est = remaining * 2  # 预估每步2分钟
            status = f"🔄 进行中，预估还需{est}分钟"
        else:
            status = "⏳ 待开始"
        lines.append(f"{status}  — {name}")
    return "\n".join(lines)

def build_message(current: int, total: int, step_names: list, current_step_name: str) -> str:
    """构建完整进度消息"""
    bar = get_progress_bar(current, total)
    table = get_status_table(current, total, step_names)
    
    emoji = "🔍" if current < total else "🎉"
    footer = "" if current < total else "\n\n🎉 任务全部完成！"
    
    return f"""```
{bar}  {emoji} {current_step_name}...

{footer}
```"""

def send_message(channel: str, target: str, message: str):
    """通过OpenClaw MCP工具发送消息"""
    # 通过 openclaw message 命令发送
    cmd = [
        "openclaw", "message", "send",
        "--channel", channel,
        "--target", target,
        "--message", message
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        print(f"发送成功: {result.stdout}")
    except subprocess.TimeoutExpired:
        print("发送超时")
    except FileNotFoundError:
        # openclaw CLI not found, try direct API
        print("openclaw CLI 未找到，尝试其他方式...")
    except Exception as e:
        print(f"发送失败: {e}")

def main():
    if len(sys.argv) < 5:
        print("用法: python3 send_progress.py <当前步骤> <总步骤数> <步骤名称> <target用户ID> [channel]")
        print("示例: python3 send_progress.py 1 5 '读取数据' 202112031231256514ec16 meishi")
        sys.exit(1)
    
    current = int(sys.argv[1])
    total = int(sys.argv[2])
    step_name = sys.argv[3]
    target = sys.argv[4]
    channel = sys.argv[5] if len(sys.argv) > 5 else "meishi"
    
    # 默认步骤名称（如果没提供完整列表）
    default_steps = [f"步骤{i}" for i in range(1, total + 1)]
    if len(default_steps) >= current:
        default_steps[current - 1] = step_name
    
    message = build_message(current, total, default_steps, step_name)
    print(f"消息内容:\n{message}")
    send_message(channel, target, message)

if __name__ == "__main__":
    main()
