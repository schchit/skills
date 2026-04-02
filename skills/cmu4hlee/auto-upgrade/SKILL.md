---
name: auto-upgrade
description: 自动化系统检查与技能更新。使用 cron 定时任务实现定期健康检查、技能更新、配置同步。适用于需要持续自我优化的部署场景。
metadata:
  openclaw:
    emoji: "🔄"
    requires:
      bins: ["git", "curl"]
---

# Auto-Upgrade Skill

## 快速使用

```bash
# 手动运行检查
auto-upgrade --check

# 更新所有技能
auto-upgrade --update-skills

# 系统健康检查
auto-upgrade --health

# 完整迭代
auto-upgrade --full
```

## Cron 定时配置

### 每日健康检查
```bash
# 每天 9:00 检查系统状态
cron.add({
  name: "daily-healthcheck",
  schedule: { kind: "cron", expr: "0 9 * * *" },
  payload: { kind: "systemEvent", text: "auto-upgrade --health" }
})
```

### 每周技能更新
```bash
# 每周日凌晨 3:00 更新技能
cron.add({
  name: "weekly-skill-update",
  schedule: { kind: "cron", expr: "0 3 * * 0" },
  payload: { kind: "systemEvent", text: "auto-upgrade --update-skills" }
})
```

### 月度系统升级
```bash
# 每月1日凌晨 4:00 完整升级
cron.add({
  name: "monthly-upgrade",
  schedule: { kind: "cron", expr: "0 4 1 * *" },
  payload: { kind: "systemEvent", text: "auto-upgrade --full" }
})
```

## 功能说明

| 参数 | 功能 |
|------|------|
| `--check` | 检查当前版本、依赖、配置 |
| `--update-skills` | 从 ClawHub 更新所有技能 |
| `--update-openclaw` | 更新 OpenClaw 核心 |
| `--health` | 健康检查（磁盘、内存、进程） |
| `--full` | 完整迭代（检查+更新+健康） |
| `--backup` | 备份配置和数据 |

## 输出示例

```
=== System Check ===
✓ OpenClaw version: latest
✓ Dependencies: up to date
✓ Config: valid
✓ Disk: 45% used
✓ Memory: 8GB / 16GB

=== Skill Status ===
✓ sql-assistant: v1.2.3
✓ weather: v1.0.1
✓ healthcheck: v2.0.0
```

## 自定义配置

在 `config/auto-upgrade.json` 中设置：

```json
{
  "auto_update": true,
  "skill_update": true,
  "health_check": true,
  "notify_channel": "main",
  "backup_before_update": true,
  "allowed_updates": ["patch", "minor"],
  "blocked_skills": ["custom-skill"]
}
```
