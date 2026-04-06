---
name: self-evolution-cn
description: "自动识别并记录学习、错误和功能需求，支持多 agent 统计和自动提升"
metadata: {"openclaw":{"emoji":"🧠","events":["agent:bootstrap","message:received","tool:after"]}}
---

# Self-Evolution-CN Hook

自动识别并记录学习、错误和功能需求。

## 功能

### 1. 自动识别触发条件

**用户纠正（自动记录到 LEARNINGS.md）：**
- 检测到关键词："不对"、"错了"、"错误"、"不是这样"、"应该是"
- 检测到纠正性表达："No, that's wrong"、"Actually"、"应该是"
- **动作**：自动记录到 .learnings/LEARNINGS.md，类别为 correction

**命令失败（自动记录到 ERRORS.md）：**
- 检测到工具执行失败（非零退出码）
- 检测到错误信息：error、Error、ERROR、failed、FAILED
- **动作**：自动记录到 .learnings/ERRORS.md

**知识缺口（自动记录到 LEARNINGS.md）：**
- 检测到用户提供新信息
- 检测到"我不知道"、"查不到"等表达
- **动作**：自动记录到 .learnings/LEARNINGS.md，类别为 knowledge_gap

**发现更好的方法（自动记录到 LEARNINGS.md）：**
- 检测到"更好的方法"、"更简单"、"优化"等表达
- **动作**：自动记录到 .learnings/LEARNINGS.md，类别为 best_practice

### 2. 自动记录格式

**学习记录：**
```markdown
## [LRN-YYYYMMDD-XXX] 类别

- Agent: <agent_id>
- Logged: 当前时间
- Priority: medium
- Status: pending
- Area: 根据上下文判断

### 摘要
一句话描述

### 详情
完整上下文

### 建议行动
具体修复或改进

### 元数据
- Source: conversation
- Pattern-Key: 自动生成
- Recurrence-Count: 1
```

**错误记录：**
```markdown
## [ERR-YYYYMMDD-XXX] 技能或命令名称

- Agent: <agent_id>
- Logged: 当前时间
- Priority: high
- Status: pending
- Area: 根据上下文判断

### 摘要
简要描述

### 错误
```
错误信息
```

### 上下文
- 尝试的命令/操作
- 使用的输入或参数

### 建议修复
如果可识别，如何解决

### 元数据
- Reproducible: yes
```

### 3. 记录后回复

记录完成后，必须回复：
"已记录到 .learnings/LEARNINGS.md" 或 "已记录到 .learnings/ERRORS.md"

### 4. 提升规则

**多 Agent 统计：**
- 所有 agent 共享学习目录
- 按 `Pattern-Key` 累计 `Recurrence-Count`
- 累计次数 >= 3 时自动提升到 SOUL.md

**提升目标：**
- 行为模式 → SOUL.md
- 工作流改进 → AGENTS.md
- 工具问题 → TOOLS.md

## 配置

无需配置。使用以下命令启用：

```bash
openclaw hooks enable self-evolution-cn
```

## 多 Agent 支持

此 hook 支持多 agent 共享学习目录。所有 agent 的学习记录将存储在共享目录中，并按 `Pattern-Key` 累计 `Recurrence-Count`。

## 环境变量

### SHARED_LEARNING_DIR

指定共享学习目录路径。

```bash
export SHARED_LEARNING_DIR="/root/.openclaw/shared-learning"
```

### AGENT_ID

指定当前 agent ID。

```bash
export AGENT_ID="main"
```

## 执行状态和日志

### 状态文件

**位置**：`$SHARED_LEARNING_DIR/heartbeat-state.json`

**内容（多 agent）：**
```json
{
  "agents": {
    "main": {
      "last_execution_date": "2026-03-26",
      "last_execution_time": "2026-03-26T00:20:00+08:00",
      "status": "completed"
    },
    "bh": {
      "last_execution_date": "2026-03-26",
      "last_execution_time": "2026-03-26T01:00:00+08:00",
      "status": "completed"
    }
  }
}
```

### 日志文件

**位置**：`$SHARED_LEARNING_DIR/logs/heartbeat-daily.log`

**内容（多 agent）：**
```
=== Self-Evolution-CN Daily Review [main]: 2026-03-26 00:20:00 ===
执行日检查...
...

=== Self-Evolution-CN Daily Review [bh]: 2026-03-26 01:00:00 ===
执行日检查...
...
```

### 默认路径

- 状态文件：`/root/.openclaw/shared-learning/heartbeat-state.json`
- 日志文件：`/root/.openclaw/shared-learning/logs/heartbeat-daily.log`

### 查看 Agent 状态

**查看所有 agent 状态：**
```bash
cat $SHARED_LEARNING_DIR/heartbeat-state.json
```

**查看特定 agent 状态：**
```bash
jq '.agents.main' $SHARED_LEARNING_DIR/heartbeat-state.json
```

**查看特定 agent 日志：**
```bash
grep '\[main\]' $SHARED_LEARNING_DIR/logs/heartbeat-daily.log
```
