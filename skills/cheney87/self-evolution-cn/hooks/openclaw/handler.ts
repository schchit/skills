/**
 * Self-Evolution-CN Hook for OpenClaw
 *
 * 自动识别并记录学习、错误和功能需求。
 * 支持多事件：agent:bootstrap、message:received、tool:after
 */

import type { HookHandler } from 'openclaw/hooks';

// 获取共享学习目录
const SHARED_LEARNING_DIR = process.env.SHARED_LEARNING_DIR || '/root/.openclaw/shared-learning';

// 获取当前 agent ID
const AGENT_ID = process.env.AGENT_ID || 'main';

// 自动识别和记录的提醒内容
const REMINDER_CONTENT = `
## 自我进化提醒

**自动识别和记录规则：**

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
\`\`\`markdown
## [LRN-YYYYMMDD-XXX] 类别

- Agent: ${AGENT_ID}
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
\`\`\`

**错误记录：**
\`\`\`markdown
## [ERR-YYYYMMDD-XXX] 技能或命令名称

- Agent: ${AGENT_ID}
- Logged: 当前时间
- Priority: high
- Status: pending
- Area: 根据上下文判断

### 摘要
简要描述

### 错误
\`\`\`
错误信息
\`\`\`

### 上下文
- 尝试的命令/操作
- 使用的输入或参数

### 建议修复
如果可识别，如何解决

### 元数据
- Reproducible: yes
\`\`\`

### 3. 记录后回复

记录完成后，必须回复：
"已记录到 .learnings/LEARNINGS.md" 或 "已记录到 .learnings/ERRORS.md"

### 4. 提升规则

**多 Agent 统计：**
- 所有 agent 共享学习目录
- 按 \`Pattern-Key\` 累计 \`Recurrence-Count\`
- 累计次数 >= 3 时自动提升到 SOUL.md

**提升目标：**
- 行为模式 → SOUL.md
- 工作流改进 → AGENTS.md
- 工具问题 → TOOLS.md

### 5. 共享目录

共享目录：${SHARED_LEARNING_DIR}
当前 Agent：${AGENT_ID}
`.trim();

const handler: HookHandler = async (event) => {
  // 事件结构的安全检查
  if (!event || typeof event !== 'object') {
    return;
  }

  // 处理 agent:bootstrap 事件
  if (event.type === 'agent' && event.action === 'bootstrap') {
    // 上下文的安全检查
    if (!event.context || typeof event.context !== 'object') {
      return;
    }

    // 将提醒作为虚拟引导文件注入
    if (Array.isArray(event.context.bootstrapFiles)) {
      event.context.bootstrapFiles.push({
        path: 'SELF_EVOLUTION_REMINDER.md',
        content: REMINDER_CONTENT,
        virtual: true,
      });
    }
  }

  // 处理 message:received 事件
  if (event.type === 'message' && event.action === 'received') {
    // TODO: 实现自动识别和记录逻辑
    // 这里需要实现检测用户纠正、知识缺口、发现更好的方法等
  }

  // 处理 tool:after 事件
  if (event.type === 'tool' && event.action === 'after') {
    // TODO: 实现自动识别和记录逻辑
    // 这里需要实现检测命令失败等
  }
};

export default handler;
