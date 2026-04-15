---
name: cn-habits-tracker
description: |
  中文习惯打卡追踪器。每日打卡、连续天数、习惯统计。
  本地存储，无账户，隐私安全。
  当用户说"打卡"、"习惯"、"连续多少天"、"今天完成了吗"时触发。
  Keywords: 打卡, 习惯, 追踪, streak, habit, 日签, 坚持.
metadata: {"openclaw": {"emoji": "🎯"}}
---

# 🎯 CN Habits Tracker — 中文习惯打卡

坚持记录，养成好习惯。

## 核心功能

| 功能 | 说明 |
|------|------|
| 打卡 | 每日完成习惯后打卡 |
| 连续天数 | 自动计算连续打卡记录 |
| 习惯管理 | 添加/删除/查看习惯列表 |
| 统计报告 | 周报/月报，完不成原因分析 |
| 提醒 | 每日定时提醒未打卡习惯 |

## 使用方式

```bash
# 打卡
python3 scripts/habits.py --checkin "早起"
python3 scripts/habits.py --checkin "喝水" --amount "8杯"

# 今日状态
python3 scripts/habits.py --today

# 添加习惯
python3 scripts/habits.py --add "早起" --goal "每天7点前起床" --unit "天"
python3 scripts/habits.py --add "喝水" --goal "每天喝8杯水" --unit "杯"
python3 scripts/habits.py --add "读书" --goal "每天读30分钟" --unit "分钟"

# 查看所有习惯
python3 scripts/habits.py --list

# 周报
python3 scripts/habits.py --report week

# 月报
python3 scripts/habits.py --report month

# 删除习惯
python3 scripts/habits.py --delete "早起"

# 未打卡提醒
python3 scripts/habits.py --remind
```

## 示例输出

```
🎯 今日打卡（4月13日）
━━━━━━━━━━━━━━━━━━━━━━
  ☑ 早起          已完成（连续7天）🔥
  ☑ 喝水          6/8杯（还差2杯）
  ☑ 读书          30分钟 ✅
  ☐ 运动          未打卡

📊 本周完成率：
  早起   ▓▓▓▓▓▓▓░  85.7%（6/7天）
  喝水   ▓▓▓▓▓▓▓▓  100%（7/7天）
  读书   ▓▓▓▓▓▓░░  71.4%（5/7天）

⚠️ 今天还需要：
  • 喝水：再喝2杯
  • 运动：跑步30分钟
```

## 数据存储

本地 JSON：`~/.qclaw/workspace/habits.json`
