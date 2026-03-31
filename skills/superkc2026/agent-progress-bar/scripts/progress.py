#!/usr/bin/env python3
"""
ASCII进度条生成器
用法: python3 progress.py <当前步骤> <总步骤数> <步骤名称>
示例: python3 progress.py 3 10 "数据清洗"
输出: [██████░░░░░░░░░░░] 30%  正在执行：数据清洗...
"""

import sys


def draw_progress(current: int, total: int, step_name: str = "") -> str:
    """绘制ASCII进度条"""
    if total <= 0:
        total = 1

    percentage = min(int(current / total * 100), 100)
    filled = int(current / total * 20)
    bar = "█" * filled + "░" * (20 - filled)

    step_label = f"  正在执行：{step_name}" if step_name else ""
    return f"[{bar}] {percentage:3d}%{step_label}"


def main():
    if len(sys.argv) < 3:
        print("用法: python3 progress.py <当前步骤> <总步骤数> [步骤名称]")
        sys.exit(1)

    current = int(sys.argv[1])
    total = int(sys.argv[2])
    step_name = sys.argv[3] if len(sys.argv) > 3 else ""

    print(draw_progress(current, total, step_name))


if __name__ == "__main__":
    main()
