---
name: onkos
version: 1.4.0
description: 支持2000章规模的AI长篇小说创作伙伴，通过6级分层摘要、SQLite事实相关性引擎、本地语义检索和多角色协作实现600万字级连贯性保证；当用户需要创作小说、管理长篇创作项目、检查情节连贯性、构建角色心理模型、追踪伏笔回收时使用
dependency:
  python:
    - jieba>=0.42.1
    - onnxruntime>=1.16.0
  system:
    - mkdir -p onkos/assets/models
---

# Onkos - 长篇小说创作伙伴

## 任务目标
- 本 Skill 用于: 基于智能体协作的长篇小说创作，支持2000章（600万字）规模的连贯性保证
- 能力包含: 6级分层上下文压缩、事实相关性引擎、知识图谱、角色心理建模、伏笔追踪、质量审计、事实变更自动检测
- 触发条件: 用户希望创作小说、管理创作项目、检查故事连贯性、构建角色设定、追踪伏笔

## 前置准备
- 依赖: `jieba>=0.42.1`, `onnxruntime>=1.16.0`
- ONNX 语义模型下载（首次使用前执行一次）:
  ```bash
  python scripts/semantic_model.py --action download
  ```
  未下载时自动降级为FTS5关键词搜索

## 交互模型

用户通过自然语言对话使用本Skill，智能体负责识别意图并自动编排脚本调用。用户无需了解任何命令或参数。

### 意图识别总览

| 意图类别 | 典型表达 | 核心操作 | 详见 |
|---------|---------|---------|------|
| 规划 | "我要写一部玄幻小说"/"加个势力"/"建个新角色"/"导入设定文档" | init -> 构建世界 -> 建模角色 / import-settings | [workflows.md](references/workflows.md#规划类工作流) |
| 创作 | "写第15章"/"继续写"/"这段换个写法" | for-creation -> 创作 -> 存储 -> 提取 -> 变更检测 -> 录入 | 本文档下方 |
| 查询 | "林风境界是什么"/"之前发生了什么"/"有哪些角色" | get-fact / search / list-chars | [workflows.md](references/workflows.md#查询类工作流) |
| 检查 | "检查连贯性"/"有没有矛盾"/"伏笔该收了" | audit / check-continuity / overdue-hooks | [workflows.md](references/workflows.md#检查类工作流) |
| 修改 | "改一下第10章"/"把青云宗改成天剑宗" | analyze-revision -> 修订 -> 更新 | [workflows.md](references/workflows.md#修改类工作流) |
| 分支 | "加个支线"/"宗门大比这条线怎么样了" | add-plot / create-branch | [workflows.md](references/workflows.md#分支类工作流) |
| 风格 | "分析一下风格"/"这两段风格像不像" | analyze-style / compare-style | [workflows.md](references/workflows.md#风格类工作流) |
| 管理 | "进度怎么样"/"归档旧事实" | arc-progress / archive-facts | [workflows.md](references/workflows.md#管理类工作流) |

### 帮助指令

用户输入以下任意表达时，智能体输出帮助信息:
- `/帮助` `/help` `/指令列表` `/命令列表` `/?`

**输出模板**（智能体直接渲染以下内容）:

```
OnKos 快捷指令一览（输入 /指令详情 <名> 查看详情）

【系统】 /帮助(help) /指令详情 /状态(status)
【规划】 /创建项目(init) /导入设定(import-settings) /预览设定(preview-settings) /更新设定(update-settings) /删除设定(delete-settings) /添加节点(add-node) /添加关系(add-edge) /创建角色(create-char) /创建阶段 /创建弧线
【创作】 /写(write) /续写 /存储(store) /提取实体 /检测事实变更 /录入事实 /种伏笔 /更新摘要 /完成章节
【查询】 /查事实 /查所有事实 /搜索(search) /相关事实 /获取上下文 /列出角色 /列出伏笔 /列出弧线 /列出节点
【检查】 /检查 /OOC检测 /审计(audit) /伏笔 /伏笔统计 /矛盾 /覆盖检查 /预算
【修改】 /修订 /更新事实 /回收伏笔 /放弃伏笔 /归档事实 /完成弧线
【分支】 /添加情节 /创建支线 /检查支线 /情节时间线
【风格】 /分析风格 /比较风格 /角色提示词
【管理】 /进度(progress) /建议(suggest) /统计 /图谱统计 /查节点 /查路径 /查邻居

提示: 也可以直接用自然语言描述需求，如"写第15章"、"检查一下连贯性"
括号内为英文别名，如 /help /write /store /search /audit /progress /suggest
```

用户输入 `/指令详情 <名称>` 时，智能体在 [references/command_index.md](references/command_index.md) 中查找对应指令并展示完整定义。

### 快捷指令与英文别名

用户可输入 `/` 开头的快捷指令精确触发操作，支持中文和英文两种写法。

| 中文 | 英文别名 | 说明 |
|------|---------|------|
| `/帮助` | `/help` | 显示帮助 |
| `/状态` | `/status` | 项目状态 |
| `/写` | `/write` | 写新章节 |
| `/续写` | `/continue` | 继续写 |
| `/存储` | `/store` | 存储章节 |
| `/搜索` | `/search` | 搜索记忆 |
| `/查事实` | `/fact` | 查询事实 |
| `/检查` | `/check` | 连贯性检查 |
| `/审计` | `/audit` | 质量审计 |
| `/进度` | `/progress` | 弧线进度 |
| `/建议` | `/suggest` | 建议下一步 |
| `/统计` | `/stats` | 记忆统计 |
| `/修订` | `/revise` | 修订章节 |
| `/分析风格` | `/style` | 风格分析 |
| `/检测事实变更` | `/detect-changes` | 检测事实变更 |

**所有指令的完整定义**（参数、步骤、示例）见 [references/command_index.md](references/command_index.md)。

---

## 创作类意图（核心工作流）

当用户要写新章节、续写、修改写法时，执行以下流程。这是最核心的工作流。

### 写新章节（完整流程）

**用户说**: "写第15章" / "继续写下一章" / "帮我写林风突破的场景"

智能体按以下8步执行，**不可跳步**:

1. **获取上下文** [脚本]
   - 调用 `for-creation`，传入 chapter 和 query（用章节核心事件作为查询词）
   - 可选传入 `max_facts`（默认80）控制相关事实数量上限
   - 返回: 全书摘要 -> 当前阶段/弧线摘要 -> 前章摘要 -> 相关事实 -> 活跃伏笔

2. **阅读大纲** [智能体]
   - 检查 outline/ 目录下对应章节的大纲
   - 如无大纲，主动向用户确认本章节要写什么

3. **创作正文** [智能体]
   - 以 Writer 角色创作，结合上下文、大纲、角色性格
   - 参考创作指南 [references/creation_guide.md](references/creation_guide.md)

4. **存储章节** [脚本]
   - 调用 `store-chapter`，传入 chapter 和 content
   - 系统自动按场景分割入库

5. **提取实体** [脚本]
   - 调用 `extract-entities`，传入 content 和 genre
   - 题材选项: `fantasy`/`urban`/`wuxia`/`scifi`，不指定时从项目配置读取
   - 返回: 角色名/地点/物品/事件，含置信度(high/medium/low)

6. **检测事实变更** [脚本 + 智能体]
   - [脚本] 调用 `detect-fact-changes`，传入 content、chapter、genre
   - 返回: 提取的实体名列表 + 各实体当前有效事实（按实体分组）
   - [智能体] 对比章节内容与现有事实，识别三类变更:
     - **新事实**: 章节中出现但事实库无记录的实体/属性/值
     - **更新事实**: 章节中同一属性值已变化（如境界提升、位置转移）
     - **冲突事实**: 章节内容与已有事实矛盾
   - [智能体] 生成变更建议列表，向用户确认后批量执行

7. **录入事实与伏笔** [脚本 + 智能体]
   - [脚本] 调用 `set-fact` 录入确认的事实变更（注意选择正确的 importance）
   - [脚本] 调用 `plant-hook` 种埋新伏笔（如有）

8. **更新摘要** [脚本]
   - [脚本] 调用 `store-summary`，更新 chapter 级摘要
   - 每10章左右应补充 arc 级摘要

### 续写当前章节

**用户说**: "继续写" / "再写一段"

智能体操作: 同写新章节的步骤3-8，从上次内容继续创作。

### 换种写法

**用户说**: "这段换个写法" / "写得太平淡了，改一下"

智能体操作: 纯自然语言处理，根据用户反馈调整风格重写。必要时参考 `style_learner` 的风格分析结果。

---

## 核心概念

事实3级重要性（permanent/arc-scoped/chapter-scoped）、摘要6级分层（book/phase/arc/volume/chapter/scene）、角色5种定位（protagonist/antagonist/mentor/sidekick/npc）、节点5种类型（person/faction/location/item/event）。详细说明见 [references/creation_guide.md](references/creation_guide.md)。

---

## 资源索引
- 引擎: [memory_engine.py](scripts/memory_engine.py)(场景/检索/摘要/弧线) [fact_engine.py](scripts/fact_engine.py)(事实) [context_retriever.py](scripts/context_retriever.py)(6级上下文) [arc_manager.py](scripts/arc_manager.py)(进度/建议)
- 存储: [knowledge_graph.py](scripts/knowledge_graph.py)(图谱) [hook_tracker.py](scripts/hook_tracker.py)(伏笔) [semantic_model.py](scripts/semantic_model.py)(ONNX)
- 辅助: [character_simulator.py](scripts/character_simulator.py)(角色OOC) [style_learner.py](scripts/style_learner.py)(风格) [plot_brancher.py](scripts/plot_brancher.py)(情节) [entity_extractor.py](scripts/entity_extractor.py)(实体) [quality_auditor.py](scripts/quality_auditor.py)(审计)
- 导入: [settings_importer.py](scripts/settings_importer.py)(Markdown设定批量导入)
- 项目: [project_initializer.py](scripts/project_initializer.py)(初始化) [command_executor.py](scripts/command_executor.py)(统一入口，支持英文别名)
- 参考: [agent_roles.md](references/agent_roles.md)(8角色模板) [creation_guide.md](references/creation_guide.md)(创作指南+核心概念) [workflows.md](references/workflows.md)(规划/查询/检查/修改/管理/分支/风格工作流) [command_index.md](references/command_index.md)(58指令索引) [command_reference.md](references/command_reference.md)(参数速查) [settings_format.md](references/settings_format.md)(设定文件格式规范)

## 注意事项
- 所有数据统一存储在 `data/novel_memory.db`（知识图谱、伏笔、弧线均在SQLite）
- ONNX语义检索为可选增强，未下载时自动降级到FTS5关键词搜索
- 每章完成后的标准流程: 存储->提取实体->检测事实变更->录入事实->检查伏笔->更新摘要（不可跳步）
- 修订已写章节前**必须先执行** `analyze-revision`，避免连锁错误
- 修订章节时**必须先清理旧数据**（`clear-chapter`），否则场景/事实/伏笔会累积膨胀
- `store-chapter` 和 `store-scene` 支持 `replace=True` 参数，先删除旧场景再录入
- `chapter-complete` 默认启用替换模式，自动覆盖旧场景
- `plant-hook` 自动去重：同描述的open伏笔已存在时返回已有ID
- 智能体应主动推进创作，而非被动等待指令；主动建议下一步、主动发现问题
- 调用脚本时，通过 `command_executor` 统一入口，使用Python风格参数名（下划线），内部自动映射
- 具体脚本的参数名和格式，查阅 [references/command_reference.md](references/command_reference.md)
- 智能体在创作流程中切换8个角色之一，详见 [references/agent_roles.md](references/agent_roles.md)
- `arc-progress` 和 `suggest-next` 的 current_chapter 参数可选，省略时自动推断最新章节号
- `detect-fact-changes` 整合实体提取+事实检索，返回结构化对比数据，智能体负责语义分析和变更决策
- `check-continuity` 和 `audit` 支持自动从数据库读取章节内容（无需手动传content）
- `import-settings` 自动去除实体名中的类型后缀（如"碧落宫 (faction)" → "碧落宫"）
- 关系格式支持多种写法: `A → B: 关系` / `A -> B: 关系` / `A --关系--> B`
- OOC检测增强关键词匹配：除精确匹配外，增加禁止行为核心动词的语义近似检测
