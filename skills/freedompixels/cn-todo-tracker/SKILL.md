---
name: cn-todo-tracker
description: |
  中文待办事项管理。添加/完成/查看待办，优先级排序。
  本地存储，无需账号。
  当用户说"待办"、"todo"、"任务清单"、"今天要做什么"时触发。
  Keywords: 待办, todo, 任务, 清单, task, checklist.
metadata: {"openclaw": {"emoji": "✅"}}
---

# ✅ CN Todo Tracker — 中文待办事项

管理你的待办，一件件搞定。

## 核心功能

| 功能 | 说明 |
|------|------|
| 添加待办 | 一句话添加，自动识别优先级 |
| 完成标记 | 标记完成，记录完成时间 |
| 列表查看 | 按优先级排序，今日/本周/全部 |
| 统计 | 完成率、待办趋势 |

## 使用方式

```bash
# 添加待办
python3 scripts/todo.py --add "完成周报" --priority high
python3 scripts/todo.py --add "回复客户邮件" --priority medium
python3 scripts/todo.py --add "整理桌面"

# 完成待办
python3 scripts/todo.py --done 1

# 查看待办
python3 scripts/todo.py --list
python3 scripts/todo.py --today

# 统计
python3 scripts/todo.py --stats
```

## 数据存储

本地 JSON：~/.qclaw/workspace/todos.json