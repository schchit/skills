/**
 * Self-Evolution-CN Hook for OpenClaw
 *
 * 自动识别并记录学习、错误和功能需求。
 * 支持多事件：agent:bootstrap、message:received、tool:after
 */

const fs = require('fs');
const path = require('path');

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

// 检测用户纠正
function detectCorrection(message) {
  const correctionPatterns = [
    /不对|错了|错误|不是这样|应该是/g,
    /No, that's wrong|Actually|should be/gi
  ];
  return correctionPatterns.some(pattern => pattern.test(message));
}

// 检测命令失败
function detectError(output) {
  const errorPatterns = [
    /error|Error|ERROR|failed|FAILED/g,
    /command not found|No such file|Permission denied|fatal/g
  ];
  return errorPatterns.some(pattern => pattern.test(output));
}

// 检测知识缺口
function detectKnowledgeGap(message) {
  const gapPatterns = [
    /我不知道|查不到|不清楚|不确定/g,
    /I don't know|can't find|not sure/gi
  ];
  return gapPatterns.some(pattern => pattern.test(message));
}

// 检测更好的方法
function detectBetterMethod(message) {
  const methodPatterns = [
    /更好的方法|更简单|优化|改进/g,
    /better way|simpler|optimize|improve/gi
  ];
  return methodPatterns.some(pattern => pattern.test(message));
}

// 生成 ID
function generateId(type) {
  const date = new Date();
  const dateStr = date.toISOString().slice(0, 10).replace(/-/g, '');
  const random = Math.random().toString(36).substring(2, 5).toUpperCase();
  return `${type}-${dateStr}-${random}`;
}

// 记录到文件
function recordToFile(type, content) {
  try {
    let filePath;
    if (type === 'LRN') {
      filePath = path.join(SHARED_LEARNING_DIR, 'LEARNINGS.md');
    } else if (type === 'ERR') {
      filePath = path.join(SHARED_LEARNING_DIR, 'ERRORS.md');
    } else if (type === 'FEAT') {
      filePath = path.join(SHARED_LEARNING_DIR, 'FEATURE_REQUESTS.md');
    } else {
      return false;
    }

    // 确保目录存在
    if (!fs.existsSync(SHARED_LEARNING_DIR)) {
      fs.mkdirSync(SHARED_LEARNING_DIR, { recursive: true });
    }

    // 追加内容
    fs.appendFileSync(filePath, content + '\n\n');
    return true;
  } catch (error) {
    console.error('记录失败:', error);
    return false;
  }
}

// 处理消息事件
function handleMessage(event) {
  if (!event.message || typeof event.message !== 'string') {
    return;
  }

  const message = event.message;
  const timestamp = new Date().toISOString();

  // 检测用户纠正
  if (detectCorrection(message)) {
    const id = generateId('LRN');
    const content = `## [${id}] correction

- Agent: ${AGENT_ID}
- Logged: ${timestamp}
- Priority: high
- Status: pending
- Area: conversation

### 摘要
用户纠正了之前的回答

### 详情
${message}

### 建议行动
根据用户的纠正调整回答

### 元数据
- Source: user_feedback
- Pattern-Key: user.correction
- Recurrence-Count: 1
`;
    recordToFile('LRN', content);
    console.log('已记录到 .learnings/LEARNINGS.md');
  }

  // 检测知识缺口
  if (detectKnowledgeGap(message)) {
    const id = generateId('LRN');
    const content = `## [${id}] knowledge_gap

- Agent: ${AGENT_ID}
- Logged: ${timestamp}
- Priority: medium
- Status: pending
- Area: conversation

### 摘要
发现知识缺口

### 详情
${message}

### 建议行动
补充相关知识

### 元数据
- Source: conversation
- Pattern-Key: knowledge.gap
- Recurrence-Count: 1
`;
    recordToFile('LRN', content);
    console.log('已记录到 .learnings/LEARNINGS.md');
  }

  // 检测更好的方法
  if (detectBetterMethod(message)) {
    const id = generateId('LRN');
    const content = `## [${id}] best_practice

- Agent: ${AGENT_ID}
- Logged: ${timestamp}
- Priority: medium
- Status: pending
- Area: conversation

### 摘要
发现更好的方法

### 详情
${message}

### 建议行动
采用更好的方法

### 元数据
- Source: conversation
- Pattern-Key: better.method
- Recurrence-Count: 1
`;
    recordToFile('LRN', content);
    console.log('已记录到 .learnings/LEARNINGS.md');
  }
}

// 处理工具执行事件
function handleToolAfter(event) {
  if (!event.toolOutput || typeof event.toolOutput !== 'string') {
    return;
  }

  const output = event.toolOutput;
  const timestamp = new Date().toISOString();

  // 检测错误
  if (detectError(output)) {
    const id = generateId('ERR');
    const content = `## [${id}] tool_error

- Agent: ${AGENT_ID}
- Logged: ${timestamp}
- Priority: high
- Status: pending
- Area: tools

### 摘要
工具执行失败

### 错误
\`\`\`
${output}
\`\`\`

### 上下文
- 工具：${event.toolName || 'unknown'}
- 参数：${JSON.stringify(event.toolArgs || {})}

### 建议修复
检查工具配置和参数

### 元数据
- Reproducible: yes
- Pattern-Key: tool.error
- Recurrence-Count: 1
`;
    recordToFile('ERR', content);
    console.log('已记录到 .learnings/ERRORS.md');
  }
}

// 主处理函数
const handler = async (event) => {
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
    handleMessage(event);
  }

  // 处理 tool:after 事件
  if (event.type === 'tool' && event.action === 'after') {
    handleToolAfter(event);
  }
};

module.exports = handler;
module.exports.default = handler;
