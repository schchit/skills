# Wechat Super Power

一个面向 OpenClaw Skills 的内容全流程助手项目：

`topic -> 相关文章列表 -> 知识库 -> 爆点分析 -> 框架 -> 写作`

## 定位

这个项目不是单纯的“文章搜索工具”，而是一个围绕公众号/微信文章场景设计的内容工作流 skill。

它的目标是让 agent 能围绕一个 topic，连续完成：

1. 抓取相关文章列表
2. 把文章沉淀进知识库
3. 基于知识库做爆点分析
4. 输出文章框架
5. 推进写作

## Onboarding Flow

完整流程分为 6 步：

1. 用户输入 `topic`
2. 抓取相关文章列表
3. 知识库沉淀
4. 爆点分析
5. 输出文章框架
6. 写作

其中：

- Step 1-3 已有脚本支持
- Step 4-6 由 agent 基于知识库内容和 prompt 继续推进

## 当前已实现范围

### Step 1-3 可执行能力

搜索相关文章：

```bash
node scripts/skill-entry.js search "<topic>" --limit 5
```

抓取单篇文章：

```bash
node scripts/skill-entry.js fetch "<文章链接>"
```

按 topic 搭建知识库：

```bash
node scripts/skill-entry.js build-kb "<topic>" --limit 5 --delay 3000 --output-dir ./knowledge-base
```

直接批量入库：

```bash
node scripts/skill-entry.js save-articles "<topic>" "<链接1>" "<链接2>" --output-dir ./knowledge-base
```

### Step 4 Prompt

第 4 步“爆点分析”不通过脚本执行，而是由 agent 直接读取知识库目录中的 Markdown 文章，再使用：

[hotspot-analysis-prompt.md](/Users/link/App/wechat-super-power/references/hotspot-analysis-prompt.md)

输出内容建议：

- `选题价值`
- `冲突点`
- `传播点`
- `可写角度`
- `证据来源`

### Step 5 参考

第 5 步“框架”参考：

[frameworks.md](/Users/link/App/wechat-super-power/references/frameworks.md)

### Step 6 Prompt

第 6 步“写作”参考：

[writing-guide.md](/Users/link/App/wechat-super-power/references/writing-guide.md)

## 项目结构

```text
.
├── README.md
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── hotspot-analysis-prompt.md
│   ├── frameworks.md
│   └── writing-guide.md
└── scripts/
    ├── build_knowledge_base.js
    ├── fetch_wechat_article.js
    ├── save_web_articles.js
    ├── search_wechat.js
    └── skill-entry.js
```

## 关键文件

- [SKILL.md](/Users/link/App/wechat-super-power/SKILL.md)：agent 的主工作流说明
- [skill-entry.js](/Users/link/App/wechat-super-power/scripts/skill-entry.js)：统一 CLI 入口
- [build_knowledge_base.js](/Users/link/App/wechat-super-power/scripts/build_knowledge_base.js)：Step 3 知识库搭建
- [save_web_articles.js](/Users/link/App/wechat-super-power/scripts/save_web_articles.js)：已有链接直接入库
- [fetch_wechat_article.js](/Users/link/App/wechat-super-power/scripts/fetch_wechat_article.js)：文章抓取与 Markdown 转换
- [hotspot-analysis-prompt.md](/Users/link/App/wechat-super-power/references/hotspot-analysis-prompt.md)：Step 4 爆点分析 prompt
- [frameworks.md](/Users/link/App/wechat-super-power/references/frameworks.md)：Step 5 框架参考
- [writing-guide.md](/Users/link/App/wechat-super-power/references/writing-guide.md)：Step 6 写作规范与 prompt

## 使用建议

如果用户要走完整流程，推荐 agent 按以下顺序推进：

1. 明确 topic
2. 搜索相关文章
3. 搭建知识库
4. 读取知识库做爆点分析
5. 基于分析结果输出框架
6. 读取 [writing-guide.md](/Users/link/App/wechat-super-power/references/writing-guide.md) 后进入写作

如果用户只要局部能力，也可以只执行对应步骤，但应尽量复用前一步的结果，而不是重新起一套流程。
