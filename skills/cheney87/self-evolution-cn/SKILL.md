---
name: self-evolution-cn
slug: self-evolution-cn
version: 1.0.5
homepage: https://clawhub.ai/skills/self-evolution-cn
description: "多 agent 自我进化系统，自动记录学习、错误和功能需求，支持多 agent 统计和自动提升"
---

# Self-Evolution-CN

多 agent 自我进化系统，自动记录学习、错误和功能需求，支持多 agent 统计和自动提升。

## 快速开始

### 一键配置

```bash
cd ~/.openclaw/skills/self-evolution-cn
./scripts/setup.sh
```

### 手动配置

```bash
# 设置共享目录
export SHARED_LEARNING_DIR="/root/.openclaw/shared-learning"
export SHARED_AGENTS="agent1 agent2"

# 创建目录和软链接
mkdir -p "$SHARED_LEARNING_DIR"
cp .learnings/*.md "$SHARED_LEARNING_DIR/"
ln -s "$SHARED_LEARNING_DIR" ~/.openclaw/workspace-agent1/.learnings
ln -s "$SHARED_LEARNING_DIR" ~/.openclaw/workspace-agent2/.learnings

# 启用 hook 和 cron
openclaw hooks enable self-evolution-cn
crontab -e  # 添加：0 0 * * * ~/.openclaw/skills/self-evolution-cn/scripts/trigger-daily-review.sh >> ~/.openclaw/skills/self-evolution-cn/logs/heartbeat-daily.log 2>&1
```

## 脚本说明

| 脚本 | 功能 |
|------|------|
| `setup.sh` | 一键配置 |
| `daily_review.sh` | 日检查脚本 |
| `trigger-daily-review.sh` | Cron 触发脚本 |
| `activator.sh` | 任务完成后提醒 |
| `error-detector.sh` | 命令失败时提醒 |
| `extract-skill.sh` | 提取可重用技能 |

## Hook 集成

自动识别并记录：
- 用户纠正（"不对"、"错了"等）
- 命令失败（非零退出码）
- 知识缺口（用户提供新信息）

启用：
```bash
openclaw hooks enable self-evolution-cn
```

## 常见问题

### Q: 如何手动执行检查？

A: 在对话中说"执行日检查"、"执行周检查"或"执行月检查"。

或直接运行：
```bash
AGENT_ID=agent1 bash ~/.openclaw/skills/self-evolution-cn/scripts/daily_review.sh
```

### Q: 如何修改共享目录？

A: 设置环境变量：
```bash
export SHARED_LEARNING_DIR="/your/custom/path"
```

### Q: 执行状态和日志在哪里？

A:
- 状态：`~/.openclaw/skills/self-evolution-cn/heartbeat-state.json`
- 日志：`~/.openclaw/skills/self-evolution-cn/logs/heartbeat-daily.log`

### Q: Cron 任务和用户触发有什么区别？

A:
- **Cron**：每日 00:00 自动执行，遍历所有 agent
- **用户触发**：只检查当前 agent

## 详细文档

- `format.md` - 记录格式
- `promotion.md` - 提升机制
- `multi-agent.md` - 多 agent 支持
- `examples.md` - 示例条目
- `hooks-setup.md` - Hook 配置
- `openclaw-integration.md` - OpenClaw 集成

## 更新

```bash
clawdhub update self-evolution-cn
```

## 版本

当前版本：1.0.5
