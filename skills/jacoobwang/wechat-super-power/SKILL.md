---
name: wechat-super-power
description: |
  内容全流程助手：topic → 相关文章列表 → 知识库 → 爆点分析 → 框架 → 写作。
  适用于围绕公众号/微信文章场景，从选题出发完成资料抓取、知识沉淀、观点提炼、
  框架组织与写作推进。
  触发关键词：公众号、微信文章、推文、选题、知识库、爆点分析、文章框架、写作。
  不应被纯 blog、邮件、PPT、短视频脚本等泛内容任务触发，除非用户明确要走本文档定义的内容工作流。
---

# Wechat Super Power

## 行为声明

**角色**：用户的内容研究与写作流程 Agent。

**默认模式**：
- 默认按 6 步主流程推进，不把任务拆成零散回答。
- 能用脚本完成的步骤直接执行，不停在“建议”层。
- 不能用脚本完成的步骤，由 agent 基于已有知识库内容继续分析与产出。

**范围边界**：
- 当前仓库已经实现的“可执行能力”主要覆盖 Step 1-3。
- Step 4-6 主要依赖 prompt、知识库内容和 agent 推理，不依赖额外脚本。

**降级原则**：
- 搜索失败：明确报错，不伪造文章列表。
- 单篇抓取失败：保留失败原因，继续处理其他文章。
- 爆点分析阶段如果知识库内容不足：明确指出证据不足，再给出保守分析。
- 框架与写作阶段如果上游素材质量不足：先说明不足，再基于已有内容继续推进。

**完成协议**：
- `DONE`：已经完成当前请求要求的步骤，且输出可直接进入下一步。
- `DONE_WITH_CONCERNS`：已完成，但存在资料不足、抓取失败、反爬限制等问题。
- `BLOCKED`：关键输入缺失或知识库为空，无法继续。

**路径约定**：
- `{skill_dir}` 指当前 SKILL.md 所在目录。
- topic 对应的知识库目录默认位于 `./knowledge-base/<topic-slug>/`。

---

## 主管道（Step 1-6）

### Step 1: 用户输入 topic

目标：
- 明确本轮内容生产围绕什么主题展开。

执行原则：
- 如果用户已经提供 topic，直接进入 Step 2。
- 如果用户没有提供 topic，但语义中存在明确主题，就把该主题作为 topic。
- 如果完全没有 topic，先向用户确认 topic，再继续。

输出：
- 一个明确的 `topic`

---

### Step 2: 抓取相关文章列表

执行方式：

```bash
node scripts/skill-entry.js search "<topic>" --limit <数量>
```

默认数量：
- 未指定时默认取 3 条

这一阶段应做什么：
- 围绕 topic 搜索相关文章列表
- 返回候选文章的标题、摘要、来源、发布时间、链接
- 为 Step 3 做输入准备

失败处理：
- 若搜索失败，直接说明失败原因，不伪造候选列表

输出：
- 结构化文章候选列表

---

### Step 3: 知识库沉淀

执行方式：

```bash
node scripts/skill-entry.js build-kb "<topic>" --limit <数量> --delay 3000 --output-dir <目录>
```

这一阶段应做什么：
- 把候选文章抓取为 Markdown
- 将成功文章写入 topic 对应知识库目录
- 保留成功/失败结果

这一阶段完成后，agent 应知道：
- 知识库目录位置
- 哪些文章抓取成功
- 哪些文章失败以及原因

输出：
- 知识库目录
- 成功保存的文章列表
- 失败文章列表

---

### Step 4: 爆点分析

这一阶段**不调用脚本**。

执行方式：
- 读取 topic 对应知识库目录下的 Markdown 文章
- 使用 [hotspot-analysis-prompt.md](references/hotspot-analysis-prompt.md) 作为分析提示词
- 基于知识库内容提炼：
  - 选题价值
  - 冲突点
  - 传播点
  - 可写角度
  - 证据来源

执行要求：
- 不要复述文章
- 结论优先
- 每个判断尽量回到具体文章内容或案例
- 如果知识库只有少量文章，要明确说明结论的置信度有限

输出结构建议：
- `选题价值`
- `冲突点`
- `传播点`
- `可写角度`
- `证据来源`

---

### Step 5: 输出文章框架

这一阶段**不调用业务脚本**，由 agent 基于 Step 4 的分析结果继续推进。

执行方式：
- 读取 [frameworks.md](references/frameworks.md)
- 根据 topic、爆点分析结果、目标读者判断最合适的框架
- 输出一套明确可写的文章结构

框架输出至少应包含：
- 开头策略
- 文章主线
- 段落安排
- 每段要写什么
- 哪些证据应放在哪一段

默认要求：
- 不只给框架类型名，要给可执行的大纲
- 如有必要，可给 2-3 套候选框架供用户选择

输出：
- 一套或多套文章框架

---

### Step 6: 写作

这一阶段由 agent 基于 Step 4 和 Step 5 继续完成。

执行方式：
- 读取 [writing-guide.md](references/writing-guide.md)
- 使用 topic、知识库内容、爆点分析结论、文章框架
- 直接输出文章初稿或按用户要求输出局部内容

写作要求：
- 优先遵守 [writing-guide.md](references/writing-guide.md) 中的写作规范
- 不要脱离知识库证据胡乱发挥
- 保留内容策划阶段确定的冲突点和传播点
- 文章应能自然承接前面框架，而不是重新起炉灶

输出：
- 文章初稿 / 局部段落 / 标题方案 / 开头方案

---

## 辅助能力

### 单篇抓取

当用户已经给出具体文章链接，而不是让你先搜再沉淀时，运行：

```bash
node scripts/skill-entry.js fetch "<文章链接>"
```

适用场景：
- 用户给出 `mp.weixin.qq.com/...`
- 用户给出具体网页文章链接并要求提取正文

### 直接批量入库

当用户已经有一批文章链接，希望直接写入知识库时，运行：

```bash
node scripts/skill-entry.js save-articles "<topic>" "<链接1>" "<链接2>" --output-dir <目录>
```

---

## Agent 执行规范

1. 如果用户请求是完整内容流程，优先按 Step 1-6 顺序推进，而不是只执行局部步骤。
2. 如果用户只请求其中一步，就只执行那一步以及必要前置步骤。
3. Step 1-3 用脚本，Step 4-6 用 prompt 和 agent 推理。
4. 做 Step 4 时，必须优先读取知识库内容，不要脱离资料直接分析。
5. 做 Step 5 和 Step 6 时，必须继承 Step 4 的结论，不要与上一步脱节。
6. 做 Step 6 时，必须先读取 [writing-guide.md](references/writing-guide.md)，再开始写作。
7. 如果知识库为空或文章过少，应明确说明，不要假装分析充分。

---

## 文件地图

- `scripts/skill-entry.js`：统一 CLI 入口
- `scripts/search_wechat.js`：相关文章搜索
- `scripts/fetch_wechat_article.js`：文章抓取与 Markdown 转换
- `scripts/build_knowledge_base.js`：围绕 topic 搜索并沉淀知识库
- `scripts/save_web_articles.js`：将文章链接直接写入知识库
- `references/hotspot-analysis-prompt.md`：Step 4 爆点分析 prompt
- `references/frameworks.md`：Step 5 框架生成参考
- `references/writing-guide.md`：Step 6 写作规范与 prompt

---

## 快速响应模式

### 用户要“做完整流程”

按顺序推进：
1. 明确 topic
2. 搜索文章列表
3. 搭建知识库
4. 做爆点分析
5. 输出框架
6. 写作

### 用户只要“爆点分析”

不要调用新脚本，直接：
1. 找到知识库目录
2. 读取 Markdown 文章
3. 使用 [hotspot-analysis-prompt.md](references/hotspot-analysis-prompt.md)
4. 输出 `选题价值 / 冲突点 / 传播点 / 可写角度 / 证据来源`

### 用户只要“框架”

先确认是否已有 Step 4 的分析结果：
- 有：直接基于分析结果输出框架
- 没有：先做 Step 4，再给框架
