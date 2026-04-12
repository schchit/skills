---
name: prd-workflow
description: Complete PRD workflow with integrated review, flowchart, and export. Deep interview → Requirement analysis → PRD generation → Review → Flowchart → Quality check → Word export.
---

# PRD Workflow（完整 PRD 工作流）

**版本**: v4.2.5  
**作者**: gotomanutd  
**更新日期**: 2026-04-08  
**ClawHub**: `clawhub install prd-workflow`  

---

## 🎯 定位

**一站式 PRD 生成技能** - 从模糊需求到完整 PRD 文档 + 流程图 + Word 导出

---

## 🔄 2 阶段执行模式

prd-workflow 采用**2 阶段执行模式**，正确理解这是使用本技能的关键！

### 阶段 0：访谈（OpenClaw AI 手动执行）

```
═══════════════════════════════════════════════════════
阶段 0：访谈过程（OpenClaw AI 手动执行）
═══════════════════════════════════════════════════════

执行者：OpenClaw AI（不是代码模块）
时    机：调用 executeForAI **之前**
输出文件：~/.openclaw/workspace/output/{用户}/{项目}/interview.json
执行方式：逐个提问，等用户回答，构建共享理解
```

**为什么需要阶段 0？**
- ✅ 访谈需要和用户实时交互（逐个提问 → 等用户回答 → 追问）
- ✅ 这是同步交互，不是异步任务
- ✅ 子代理无法进行访谈（不能等待用户回答）
- ✅ 所以访谈必须在当前会话由 OpenClaw AI 自己完成

**核心指令**：
```
Interview me relentlessly about every aspect of this plan until we reach a 
shared understanding. Ask one question at a time, get the answer, then ask the next.
```

**访谈维度**（6 个维度，16-50 个问题）：

| 维度 | 问题数 | 示例问题 |
|------|--------|---------|
| **产品定位** | 3-5 个 | 目标用户是谁？使用场景？ |
| **核心功能** | 3-5 个 | 是否需要产品推荐？数据来源？ |
| **合规要求** | 3-5 个 | 是否需要风险测评？适当性管理？ |
| **技术约束** | 3-5 个 | 使用渠道？现有系统？上线时间？ |
| **业务目标** | 2-3 个 | 解决什么痛点？成功指标？ |
| **用户场景** | 2-5 个 | 谁在什么时候使用？使用频率？ |

**访谈完成条件**：
- ✅ 至少问了 16 个问题
- ✅ 覆盖了 6 个维度
- ✅ 构建了完整的 sharedUnderstanding
- ✅ 用户确认理解正确

**输出格式**：
```json
{
  "sharedUnderstanding": {
    "summary": "需求总结",
    "productPositioning": { "targetUsers": "目标用户", ... },
    "coreFeatures": ["核心功能 1", "核心功能 2"],
    "complianceRequirements": ["合规要求 1", "合规要求 2"]
  },
  "keyDecisions": [
    { "id": "d1", "topic": "决策主题", "decision": "决策内容", "rationale": "决策理由" }
  ],
  "questions": [
    { "question": "问题", "answer": "答案", "followUp": "追问" }
  ]
}
```

---

### 阶段 1：工作流（executeForAI 自动执行）

```
═══════════════════════════════════════════════════════
阶段 1：工作流（executeForAI 自动执行）
═══════════════════════════════════════════════════════

执行者：prd-workflow 代码
时    机：访谈完成后（阶段 0 完成）
输入文件：interview.json（必须存在）
执行方式：自动执行所有步骤
```

**执行流程**：
```
1. 调用 executeForAI('生成 XXX PRD', { mode: 'auto' })
   ↓
2. prdWorkflow 生成执行计划
   执行计划：['precheck', 'interview', 'decomposition', 'prd', 'review', ...]
   ↑ 注意：interview 在执行计划中！
   ↓
3. 执行 interview_module
   - 检查 interview.json 是否存在
   - ✅ 存在 → 读取并验证，继续执行
   - ❌ 不存在 → 报错"访谈未执行"
   ↓
4. 执行后续步骤
   - decomposition（需求拆解）
   - prd（PRD 生成）
   - review（评审）
   - flowchart（流程图）
   - design（UI 设计）
   - prototype（原型）
   - export（Word 导出）
   - image（图片渲染）
   - quality（质量检查）
```

**关键区分**：
- **访谈过程**：OpenClaw AI 手动执行（在 executeForAI 之前）
- **interview_module**：代码模块，只检查 interview.json（在 executeForAI 之内）

---

## 📋 是否需要访谈？

**判断流程**：

```
用户请求
   ↓
检查 interview.json 是否存在？
   ↓
✅ 已存在 → 跳过访谈过程，直接阶段 1
❌ 不存在 → 执行阶段 0（访谈过程）
   ↓
是否有详细业务文档？
   ↓
✅ 有文档 → 简化访谈（3-5 个确认问题）
❌ 无文档 → 完整访谈（16-50 个问题）
```

**场景对比**：

| 场景 | 是否需要访谈 | 访谈方式 | 问题数量 |
|------|------------|---------|---------|
| **首次生成（无文档）** | ✅ 需要 | 完整访谈 | 16-50 个 |
| **首次生成（有文档）** | ⚠️ 简化 | 快速确认 | 3-5 个 |
| **迭代修改** | ❌ 不需要 | 复用已有 | 0 个 |
| **追加功能** | ❌ 不需要 | 复用已有 | 0 个 |
| **只评审/导出** | ❌ 不需要 | 跳过 | 0 个 |

---

## 🚀 使用方法

### ⚠️ 重要提示

**正确启动方式**：
```bash
# ✅ 正确：使用自然语言调用
用 prd-workflow 生成 XXX 的 PRD
调用 prd-workflow 生成 XXX 的完整 PRD
执行 prd-workflow，生成 XXX 的 PRD
```

**错误方式**：
```bash
# ❌ 错误：/skill 命令只读取说明，不执行代码
/skill prd-workflow 我要做一个 XXX
```

**为什么**：
- `/skill` 命令用于**查看技能说明**（类似 `man` 命令）
- 自然语言调用（"用 XXX 做 YYY"）才会**真正执行技能代码**
- prd-workflow 是工作流引擎，需要调用 `executeForAI` 才能启动完整流程

---

### 基础用法

| 场景 | 命令示例 | 执行流程 |
|------|---------|---------|
| **首次生成** | `用 prd-workflow 生成养老规划功能的 PRD` | 阶段 0（访谈）→ 阶段 1（工作流） |
| **完整流程** | `用 prd-workflow 生成养老规划功能的完整 PRD` | 阶段 0（访谈）→ 阶段 1（工作流） |
| **快速版** | `用 prd-workflow 快速生成 PRD` | 阶段 0（简化访谈）→ 阶段 1（lite 流程） |
| **只评审** | `用 prd-workflow 评审已有的 PRD` | 阶段 1（review-only，跳过访谈） |
| **只导出** | `用 prd-workflow 导出 PRD 为 Word` | 阶段 1（export-only，跳过访谈） |
| **设计 + 原型** | `用 prd-workflow 生成 UI 设计和原型` | 阶段 1（design-only，跳过访谈） |
| **迭代修改** | `用 prd-workflow 迭代修改 PRD，追加新需求` | 阶段 1（iteration，复用访谈） |
| **回滚版本** | `用 prd-workflow 回滚到版本 v1.0` | 阶段 1（rollback，恢复版本） |

---

### 完整流程示例

#### 场景 1：首次生成（无文档）

```
用户：用 prd-workflow 生成儿童打字游戏的完整 PRD
   ↓
【阶段 0：访谈过程】
OpenClaw AI：
1. 检查 interview.json → ❌ 不存在
2. 开始访谈（逐个提问）
   - "目标用户年龄段是？"
   - "学习内容重点是拼音还是英文？"
   - "游戏类型偏向教育还是娱乐？"
   - ...（16+ 个问题）
3. 记录用户回答
4. 构建 sharedUnderstanding
5. 写入 interview.json
   ↓
【阶段 1：工作流】
OpenClaw AI：调用 executeForAI('生成儿童打字游戏 PRD', { mode: 'auto' })
   ↓
prd-workflow：
1. 生成执行计划（包含 interview）
2. 执行 interview_module
   - 检查 interview.json → ✅ 存在
   - 读取并验证
3. 执行后续步骤
   - decomposition → prd → review → flowchart → ...
   ↓
输出：完整 PRD + 所有附件
```

---

#### 场景 2：首次生成（有详细业务文档）

```
用户：用 prd-workflow 生成 XXX 的 PRD，这是业务需求文档：[文档内容]
   ↓
【阶段 0：访谈过程（简化）】
OpenClaw AI：
1. 检查 interview.json → ❌ 不存在
2. 读取业务需求文档
3. 快速确认关键点（3-5 个问题）
   - "文档中的目标用户准确吗？"
   - "功能优先级排序对吗？"
   - "有没有文档没提到的约束？"
4. 写入 interview.json
   ↓
【阶段 1：工作流】
OpenClaw AI：调用 executeForAI('生成 XXX PRD', { mode: 'auto' })
   ↓
输出：完整 PRD + 所有附件
```

---

#### 场景 3：迭代修改（已有访谈结果）

```
用户：用 prd-workflow 追加社交功能
   ↓
【阶段 0：访谈过程】
OpenClaw AI：
1. 检查 interview.json → ✅ 已存在
2. 跳过访谈过程（复用已有结果）
   ↓
【阶段 1：工作流】
OpenClaw AI：调用 executeForAI('追加社交功能', { mode: 'iteration' })
   ↓
prd-workflow：
1. 生成执行计划
2. 强制执行 decomposition → prd
3. 创建新版本（v1 → v2）
   ↓
输出：更新后的 PRD（v2 版本）
```

---

### ❌ 错误调用方式

#### 错误 1：使用 `/skill` 命令

```bash
# ❌ 错误
/skill prd-workflow 我要做一个 XXX

# 正确
用 prd-workflow 生成 XXX 的完整 PRD
```

**原因**：`/skill` 命令只读取 SKILL.md 说明，不执行代码。

---

#### 错误 2：启动子代理执行

```javascript
// ❌ 错误
sessions_spawn({
  task: '使用 prd-workflow 生成...',
  runtime: 'subagent'
});

// 正确
// 在当前会话直接调用 executeForAI
const result = await executeForAI('生成 XXX PRD', {
  userId: '李帆',
  mode: 'auto'
});
```

**原因**：子代理无法进行阶段 0（访谈需要和用户实时交互）。

---

#### 错误 3：跳过访谈直接调用

```javascript
// ❌ 错误（interview.json 不存在时）
const result = await executeForAI('生成 XXX PRD', { mode: 'auto' });
// → 报错："访谈未执行！"

// 正确
// 先完成阶段 0（访谈），写入 interview.json
// 再调用阶段 1
```

**原因**：interview_module 会检查 interview.json 是否存在。

---

## 💻 调用示例（开发者）

```javascript
const { executeForAI } = require('./workflows/ai_entry');

// 场景 1：首次生成（完整流程）
const result1 = await executeForAI('生成养老规划 PRD', {
  userId: 'dingtalk-0155522465843896',
  mode: 'auto'
});

// 场景 2：迭代修改
const result2 = await executeForAI('追加社保测算功能', {
  userId: 'dingtalk-0155522465843896',
  mode: 'iteration'
});

// 场景 3：只评审
const result3 = await executeForAI('评审 PRD', {
  userId: 'dingtalk-0155522465843896',
  mode: 'review-only'
});

// 场景 4：清空重来
const result4 = await executeForAI('生成养老规划 PRD', {
  userId: 'dingtalk-0155522465843896',
  mode: 'fresh'
});

// 检查结果
if (result1.success) {
  console.log(`✅ 完成：${result1.message}`);
  console.log(`📁 输出目录：${result1.outputDir}`);
  console.log(`📄 PRD 文件：${result1.prdPath}`);
  console.log(`📊 功能数：${result1.summary.features}`);
  console.log(`📝 字数：${result1.summary.wordCount}`);
} else {
  console.log(`❌ 失败：${result1.error}`);
  console.log(`💡 建议：${result1.suggestion}`);
}
```

---

## 📁 输出位置（三级隔离）

**隔离架构**：
```
~/.openclaw/workspace/output/
└── {用户 ID}/                    ← 第 1 级：用户隔离
    └── {需求名称}/               ← 第 2 级：需求隔离
        ├── interview.json        ← 阶段 0 输出（访谈结果）
        ├── decomposition.json    ← 阶段 1 输出
        ├── prd.json              ← 阶段 1 输出
        ├── PRD.md                ← 阶段 1 输出
        ├── PRD.docx              ← 阶段 1 输出
        └── .versions/            ← 第 3 级：版本管理
            ├── v1/
            │   ├── PRD.md
            │   └── PRD.docx
            └── v2/
                └── ...
```

**完整文件清单**：
```
{用户 ID}/
└── {需求名称}/
    ├── interview.json            # 阶段 0：访谈结果
    ├── decomposition.json        # 阶段 1：需求拆解
    ├── prd.json                  # 阶段 1：PRD 生成
    ├── review.json               # 阶段 1：评审报告
    ├── flowchart.mmd             # 阶段 1：流程图
    ├── design.json               # 阶段 1：UI 设计
    ├── prototype/                # 阶段 1：HTML 原型
    ├── PRD.md                    # 阶段 1：PRD 文档
    ├── PRD.docx                  # 阶段 1：Word 导出
    └── .versions/                # 版本管理
```

---

## 🔧 执行方式（OpenClaw AI 必读）

### ⚠️ OpenClaw AI 必须执行

**如果你是 OpenClaw AI，请务必理解以下内容**：

#### 阶段 0：访谈过程（你手动执行）

**核心指令**：
```
Interview me relentlessly about every aspect of this plan until we reach a 
shared understanding. Walk down each branch of the design tree, resolving 
dependencies between decisions one-by-one. Ask one question at a time, 
get the answer, then ask the next. And finally, if a question can be 
answered by exploring the codebase, explore the codebase instead.
```

**执行方式**：
1. **你自己提问**：不要调用 interview_module 或其他代码
2. **逐个提问**：一次问一个问题，等用户回答后再问下一个（vertical slicing）
3. **追问深度**：根据用户回答追问细节，不要停留在表面
4. **探索分支**：走每个设计分支，"如果选择 A，那么需要决定 X、Y、Z"
5. **构建理解**：将所有问答整理成 sharedUnderstanding
6. **保存结果**：写入 `~/.openclaw/workspace/output/{userId}/{projectName}/interview.json`

**访谈技巧**：
- ✅ **设计树探索**：走每个分支的设计决策（"如果选择 A，那么需要决定 X、Y、Z"）
- ✅ **依赖关系解析**：resolve 决策之间的依赖（"这个决策依赖于前面的 X 决定"）
- ✅ **代码库探索**：能查代码就不问
- ✅ **共享理解确认**：总结并确认（"让我总结一下...以上理解是否准确？"）

---

#### 阶段 1：调用工作流

访谈完成后，调用 `executeForAI` 继续执行：

```javascript
const result = await executeForAI('生成养老规划 PRD', {
  userId: '用户 ID',
  mode: 'auto'
});
```

---

### ❌ 不要做

1. ❌ 不要直接调用 executeForAI 跳过访谈（interview.json 不存在会报错）
2. ❌ 不要使用硬编码的示例数据
3. ❌ 不要只问 1-2 个问题就结束
4. ❌ 不要跳过多轮问答直接生成 PRD
5. ❌ 不要在子代理中调用 executeForAI（无法进行访谈）

---

## ⚙️ 执行模式

**支持 4 种执行模式**，通过 `options.mode` 参数指定：

### 1️⃣ auto 模式（默认）

**用途**：正常执行完整流程

**使用场景**：
- 首次生成 PRD
- 从零开始的需求

**调用示例**：
```javascript
const result = await executeForAI('生成养老规划 PRD', {
  userId: 'dingtalk-0155522465843896',
  mode: 'auto'
});
```

**执行流程**：
```
1. 解析用户需求
2. 生成执行计划（interview → decomposition → prd → ...）
3. 检查已有结果（跳过已完成的技能）
4. 执行剩余技能
5. 返回结果
```

---

### 2️⃣ iteration 模式（迭代）

**用途**：在现有 PRD 基础上追加/修改需求

**使用场景**：
- 追加新功能（"追加社保测算功能"）
- 修改现有逻辑（"修改风险测评规则"）
- 优化已有描述

**调用示例**：
```javascript
const result = await executeForAI('追加社保测算功能', {
  userId: 'dingtalk-0155522465843896',
  mode: 'iteration'
});
```

**执行流程**：
```
1. 分析需求变更（对比新旧需求）
2. 创建当前版本备份（v1 → v2）
3. 强制执行 decomposition（重新拆解）
4. 强制执行 prd（更新 PRD）
5. 可选：执行后续技能（review/flowchart 等）
6. 返回新版本号
```

---

### 3️⃣ fresh 模式（全新）

**用途**：清空重来，删除所有中间结果

**使用场景**：
- 之前的执行结果混乱，需要重新开始
- 需求完全变化，旧结果无用
- 调试/测试需要干净环境

**调用示例**：
```javascript
const result = await executeForAI('生成养老规划 PRD', {
  userId: 'dingtalk-0155522465843896',
  mode: 'fresh'
});
```

**执行流程**：
```
1. 清空输出目录（除 .versions 外）
2. 删除所有中间 JSON 文件
3. 删除 PRD.md
4. 从头开始执行完整流程
```

---

### 4️⃣ rollback 模式（回滚）

**用途**：恢复到历史版本

**使用场景**：
- 迭代后效果不好，想恢复旧版本
- 对比不同版本的效果
- 误操作后恢复

**调用示例**：
```javascript
const result = await executeForAI('回滚到 v1', {
  userId: 'dingtalk-0155522465843896',
  mode: 'rollback',
  version: 'v1'
});
```

**执行流程**：
```
1. 备份当前版本（自动创建 backup-xxx）
2. 恢复指定版本的文件
3. 更新当前 PRD.md
4. 返回成功消息
```

---

### 模式对比表

| 模式 | 用途 | 清空数据 | 创建版本 | 典型场景 |
|------|------|---------|---------|---------|  
| **auto** | 正常执行 | ❌ | ❌ | 首次生成 |
| **iteration** | 迭代修改 | ❌ | ✅ | 追加/修改需求 |
| **fresh** | 清空重来 | ✅ | ❌ | 重新开始 |
| **rollback** | 恢复版本 | ❌ | ✅（备份） | 回滚操作 |

---

## 📋 PRD 结构（prd_template.js 强制约束）

**实际输出结构**：

```markdown
## 1. 需求概述
### 1.1 产品定位
### 1.2 目标用户
### 1.3 业务目标
### 1.4 功能列表

## 2. 全局业务流程
### 2.1 主业务流程图 (Mermaid)
### 2.2 全局业务规则
### 2.3 全局数据定义

## 3. 功能 1: [功能名称]
### 3.1 功能概述
### 3.2 用户场景
### 3.3 业务流程
### 3.4 业务规则
### 3.5 输入输出定义
### 3.6 用户故事
### 3.7 验收标准 (Given-When-Then)
### 3.8 原型设计
### 3.9 异常处理

## 4. 功能 2: [功能名称]
...(同上)

## 非功能需求
### 性能要求
### 安全要求
### 兼容性要求

## 附录
### 术语表
### 参考资料
```

---

## 🔧 核心代码文件

| 文件 | 功能 |
|------|------|
| `workflows/main.js` | 主工作流编排 |
| `workflows/smart_router.js` | 智能路由（识别需求→编排流程） |
| `workflows/data_bus.js` | 数据总线（技能间数据传递）+ 路径安全化 |
| `workflows/data_bus_schema.js` | 数据格式标准化 |
| `workflows/quality_gates.js` | 质量门禁 |
| `workflows/version_manager.js` | 版本管理 |
| `workflows/requirement_diff.js` | 需求对比 |
| `workflows/modules/precheck_module.js` | 环境检查前置化 |
| `workflows/modules/interview_module.js` | 访谈结果检查（不执行访谈） |
| `workflows/image_renderer.js` | 图片渲染服务 |
| `workflows/ai_diagram_extractor.js` | AI 图表提取器 |
| `workflows/prd_template.js` | PRD 模板引擎 |

---

## 🎯 适用场景

### ✅ 推荐使用
| 场景 | 说明 |
|------|------|
| 需求模糊 | 用户只有大致想法，需要深度澄清 |
| 复杂业务 | 涉及多个模块/系统的复杂功能 |
| 金融 PRD | 需要合规检查点的金融产品 |
| 正式交付 | 需要完整文档 + 流程图 + Word 导出 |

### ❌ 不推荐
| 场景 | 推荐替代 |
|------|---------|
| 简单功能 | `prd-generator`（快速模式） |
| 紧急需求 | `prd-generator`（5 模块） |
| 技术方案 | `technical-spec` skill |

---

## 📊 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| **v4.2.4** | **2026-04-08** | **📖 精简 SKILL.md** - 基于 Claude Code 提示词技巧，精简结构，添加示例 |
| **v4.2.3** | **2026-04-07** | **📖 重写 SKILL.md** - 明确 2 阶段执行模式，消除所有矛盾和歧义 |
| **v4.2.2** | **2026-04-07** | **📝 postinstall 添加 adm-zip 依赖检测** - Word 文档图片检查功能完整可用 |
| **v4.2.1** | **2026-04-07** | **📖 更新使用说明** - 增加/skill 命令误区的详细说明 |
| **v4.2.0** | **2026-04-05** | **✅ 验收标准 GWT 格式优化** - 需求拆解不再生成验收标准 + PRD 阶段按功能生成 GWT |
| **v4.0.0** | **2026-04-05** | **🚀 多页面原型系统** - 页面树推断 + 导航组件 + 路由注入 + 多端截图 |
| **v3.0.0** | **2026-04-04** | **🖼️ 图片渲染服务** - Mermaid → PNG 自动渲染 + Word 导出嵌入图片 + 系统 Chrome 支持 |

---

## 🔒 安全说明

**⚠️ ClawHub 安全扫描可能误报"Suspicious"**

**误报原因**：
- 本技能打包了 6 个依赖技能到 `skills/` 目录（正常功能）
- 工作流脚本调用内置技能（正常功能，自动化编排）
- 包含 Python/Node.js 脚本（正常功能，技能执行需要）

**实际安全检查**：
- ✅ **无二进制文件** - 已清理所有 .pyc
- ✅ **无外部 API 调用** - 全部本地执行
- ✅ **无敏感数据** - 无 API Key/密码
- ✅ **无系统文件访问** - 只在 workspace 内操作

**结论**：可以安全使用，误报不影响功能。

---

## 📖 参考资料

- **Matt Pocock Skills**: github.com/mattpocock/skills
  - /grill-me - 深度访谈理念来源
  - /write-a-prd - PRD 生成理念来源
- **OpenClaw Skills**:
  - requirement-reviewer - PRD 评审
  - mermaid-flow - 流程图绘制
  - prd-export - Word 导出
  - htmlPrototype - HTML 原型生成
  - ui-ux-pro-max - UI/UX 设计

---

**技能版本**: 4.2.5  
**许可**: MIT-0  
**发布状态**: ⚠️ 草稿测试中
