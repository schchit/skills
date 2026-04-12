---
name: self-evolution-cn
slug: self-evolution-cn
version: 2.0.0
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
| `daily_review.sh` | 自动统计与提升（每日 00:00 执行） |
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

A: 直接运行：
```bash
bash ~/.openclaw/skills/self-evolution-cn/scripts/daily_review.sh
```

### Q: 如何控制是否启用自动提升？

A: 设置环境变量 `AUTO_PROMOTE_ENABLED`：
```bash
# 禁用自动提升（仅统计）
AUTO_PROMOTE_ENABLED=false bash ~/.openclaw/skills/self-evolution-cn/scripts/daily_review.sh

# 启用自动提升（默认）
AUTO_PROMOTE_ENABLED=true bash ~/.openclaw/skills/self-evolution-cn/scripts/daily_review.sh
```

### Q: 如何修改共享目录？

A: 设置环境变量：
```bash
export SHARED_LEARNING_DIR="/your/custom/path"
```

### Q: 执行状态和日志在哪里？

A:
- 状态：`$SHARED_LEARNING_DIR/heartbeat-state.json`
- 日志：`$SHARED_LEARNING_DIR/logs/heartbeat-daily.log`

## 详细文档

- `references/format.md` - 记录格式
- `references/promotion.md` - 提升机制
- `references/multi-agent.md` - 多 agent 支持
- `references/hooks-setup.md` - Hook 配置
- `references/openclaw-integration.md` - OpenClaw 集成
- `hooks/openclaw/HOOK.md` - Hook 说明

## 更新

```bash
clawdhub update self-evolution-cn
```

## 版本

当前版本：2.0.0

### 更新日志

**v2.0.0 (2026-04-07)**
- 优化提升格式，去除冗余元数据
- 根据 Area 字段自动映射到对应的二级标题
- 修复 Area 字段提取逻辑
- 更新文档说明
- 精简所有说明文档
- 修复 Pattern-Key 匹配逻辑
- 添加无效 Pattern-Key 过滤

**v1.0.6 (2026-04-06)**
- 初始版本
