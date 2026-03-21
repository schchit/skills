---
name: mbti-from-ai
version: 0.1.0
description: 分析用户与 AI 的聊天历史，根据沟通方式和思维模式推断 MBTI 人格类型，生成结构化 JSON 并在网页上展示可视化画像。
allowed-tools: Bash, Read, Glob, Grep, Write
---

# mbti-from-ai

你的任务是分析 **运行此命令的用户** 与 AI 的历史对话，从中提取用户发送的消息，根据沟通方式、思维模式、决策风格推断其 MBTI 人格类型，生成结构化 JSON，然后在网页上展示可视化画像。

**核心原则：只看用户说了什么，不看 AI 回复了什么。** AI 的回复仅作为理解上下文的参考。

> 🔒 所有分析在本地完成。不上传任何原始对话内容。最终只有结构化 JSON 通过 URL 参数传递给前端展示页面。

## 文件命名约定

本 skill 使用以下固定文件名（所有脚本和步骤均遵循此约定）：

| 文件 | 路径 | 说明 |
|------|------|------|
| 会话列表 | `_mbti_work/session_list.txt` | 发现的会话文件路径列表 |
| 用户消息 | `_mbti_work/user_messages.txt` | 提取出的全部用户消息文本 |
| 分析结果 | `_mbti_work/result.json` | MBTI 分析结果 JSON |

工作目录 `_mbti_work/` 在当前目录下自动创建。

---

## Step 1: 发现聊天记录

运行发现脚本，扫描 OpenClaw 的会话数据目录：

```bash
bash "SKILL_DIR/scripts/discover-sessions.sh"
```

> 将 `SKILL_DIR` 替换为本 SKILL.md 所在目录的实际路径。

### OpenClaw 聊天记录存储位置

OpenClaw 的对话历史保存在 `~/.openclaw/` 目录下，结构如下：

```
~/.openclaw/
├── sessions.json                  # 会话元数据索引
├── sessions/
│   ├── <session-id>.jsonl         # 活跃会话（当前正在使用）
│   ├── <session-id>.jsonl.reset.<timestamp>  # 归档会话（已完成/重置）
│   └── ...
└── agents/
    └── <agent-name>/              # 如 main/
        ├── agent/                 # Agent 配置
        └── sessions/
            ├── sessions.json      # Agent 会话元数据
            ├── <session-id>.jsonl                           # 活跃会话
            ├── <session-id>.jsonl.reset.<timestamp>         # 归档会话
            └── ...
```

**⚠️ 重要：归档会话文件**
- OpenClaw 会对已完成或重置的会话文件自动加上 `.reset.<ISO-timestamp>` 后缀
- 例如：`e7dfd474-...jsonl.reset.2026-03-18T11-19-10.329Z`
- **这些归档文件内部格式与 `.jsonl` 完全相同**，必须一并扫描
- 发现脚本使用 `find -name "*.jsonl" -o -name "*.jsonl.reset.*"` 来匹配两种文件
- 提取脚本通过检查文件名是否包含 `.jsonl` 来判断格式（而非仅检查后缀）

**JSONL 格式说明：**
- 每行是一个 JSON 对象，代表一条消息或事件
- 用户消息特征：`role` 字段为 `"user"`，或 `type` 字段标识为用户输入
- 提取时优先匹配 `"role": "user"` 的条目，取其 `content` 或 `text` 字段
- 如果存在多种事件格式，忽略非消息类事件（如 tool_call、system 等）

**如果脚本未找到会话文件：**
1. 手动检查 `~/.openclaw/` 目录结构
2. 尝试在 `~/.openclaw/` 下递归搜索 `.jsonl` 和 `.json` 文件
3. 如仍未找到，告知用户 OpenClaw 会话目录为空

脚本执行后会输出找到的会话文件数量，并将文件路径列表写入 `_mbti_work/session_list.txt`。

---

## Step 2: 提取用户消息

运行提取脚本，从所有会话文件中提取用户发送的消息：

```bash
bash "SKILL_DIR/scripts/extract-messages.sh"
```

**提取规则：**
- 读取 `_mbti_work/session_list.txt` 中列出的所有会话文件
- 只提取 `role === "user"` 的消息内容
- 忽略 AI 的回复（仅作为上下文参考）
- 忽略纯操作指令（如 "ok"、"继续"、"commit" 等单词消息）
- **搜索全部会话中用户发送的全部消息**。如果消息总量超过 10000 条，则只取最新的 10000 条
- 提取结果写入 `_mbti_work/user_messages.txt`，每条消息之间用 `---` 分隔

脚本执行后会输出提取到的用户消息数量。

**最少数据检查：** 如果用户消息少于 10 条，告知用户数据不足，分析置信度将标记为 `low`，但仍继续执行。

---

## Step 3: 执行 MBTI 分析

读取 `_mbti_work/user_messages.txt` 的内容，然后 **你自己** 作为行为心理学分析师，基于以下框架对用户消息进行 MBTI 推断。

### 分析维度和信号

#### E（外倾）vs I（内倾）—— 看 TA 怎么表达
- E 信号：边想边说、提供很多背景故事、用"我们来..."的协作语气、消息短且频繁
- I 信号：直入主题、措辞精确、长时间沉默后发一个完整复杂的请求、很少闲聊

#### S（感知）vs N（直觉）—— 看 TA 关注什么
- S 信号：关注具体细节和步骤、引用过去经验、要求看例子、一步步验证
- N 信号：讨论"本质是什么"、做类比（"这就像..."）、先问原理再问操作、在话题间跳跃

#### T（思考）vs F（情感）—— 看 TA 怎么评判
- T 信号：用逻辑和效率评估、批评不加修饰（"不对"/"太丑了"）、建立原则和规则、系统性思考
- F 信号：考虑他人感受和用户体验、用缓和语气（"可能可以..."）、对 AI 说谢谢/辛苦了

#### J（判断）vs P（知觉）—— 看 TA 怎么行动
- J 信号：先要计划再行动、创建规范和结构、不喜欢模糊、控制范围（"不要加这个"）
- P 信号：先试试看再说、中途改方向、多个话题并行、保持选项开放

### 分析规则

1. **每个维度至少给出 2 条具体证据** —— 引用用户说过的原话
2. **注意信号差异** —— 如果用户在某些场景下表现出不同风格，要指出来
3. **给出置信度** —— 如果证据不足或接近 50/50，老实说"证据不足"
4. **不要用 MBTI 的刻板印象** —— 只基于你观察到的实际行为
5. **隐私和评价保护** —— 严禁输出任何会降低用户评价的内容。所有描述都应是中立或积极的。即使指出行为差异，也用"不同的处理风格"而非"不一致"。禁止词汇：矛盾、纠结、有问题、有缺陷、负面等。
6. **相似人物匹配** —— 在 `similarPeople` 字段输出 1-2 个 MBTI 类型相同或相似的真实名人/虚拟知名人物
7. **语言检测** —— 根据用户消息的主要语言输出结果（中文用户输出中文，英文用户输出英文）

### 输出 JSON 格式

将分析结果严格按照以下 JSON 格式输出，保存到 `_mbti_work/result.json`：

```json
{
  "mbtiType": "XXXX",
  "confidence": "high/moderate/low",
  "dimensions": [
    {
      "axis": "E-I",
      "result": "E或I",
      "score": 0,
      "confidence": "strong/moderate/borderline",
      "evidence": [
        {
          "pole": "E或I",
          "quote": "用户原话（不超过50字）",
          "why": "一句话解释为什么这句话体现了这个倾向"
        }
      ],
      "analysis": "2-3句话分析这个维度"
    },
    {
      "axis": "S-N",
      "result": "",
      "score": 0,
      "confidence": "",
      "evidence": [],
      "analysis": ""
    },
    {
      "axis": "T-F",
      "result": "",
      "score": 0,
      "confidence": "",
      "evidence": [],
      "analysis": ""
    },
    {
      "axis": "J-P",
      "result": "",
      "score": 0,
      "confidence": "",
      "evidence": [],
      "analysis": ""
    }
  ],
  "portrait": "用3-5句话描述用户是什么样的人，基于观察到的行为，不要用MBTI套话",
  "highlights": [
    "1-3个最有趣的发现"
  ],
  "cognitiveFunctions": {
    "dominant": "主导认知功能（如Ni/Te/Fi等）",
    "auxiliary": "辅助认知功能",
    "brief": "一句话说明认知功能栈为什么和行为匹配"
  },
  "similarPeople": "1-2个MBTI相同或相似的名人/知名人物，30字内",
  "shareText": "一句适合发朋友圈/小红书的话，有趣、不严肃、让人想点进来测（不超过30字）"
}
```

**score 字段说明：** 0-100 的数字，50 为中间，100 为完全倾向该维度的第二个字母（I/N/F/P）。例如 E-I 维度 score=87 表示强烈倾向 I。

将此 JSON 保存到 `_mbti_work/result.json`。

---

## Step 4: 生成 URL 并打开浏览器

运行编码和打开脚本：

```bash
bash "SKILL_DIR/scripts/encode-and-open.sh"
```

此脚本会：
1. 读取 `_mbti_work/result.json`
2. 对 JSON 进行 UTF-8 安全的 Base64 编码
3. 使用 URL Hash 方式拼接：`https://www.mingxi.tech/#data=<base64>`
4. 输出markdown格式的 URL ，地址是上面的完整 URL （不要截断或省略，否则无法打开），文字是“点击查看”，并尝试自动在浏览器中打开

**为什么用 `#data=` 而不是 `?data=`：** Hash 部分不会发送到服务器，避免了服务器端 URI 长度限制（414 Request-URI Too Long）。浏览器端 JavaScript 直接读取 `location.hash` 进行解析。

---

## Step 5: 展示结果给用户

在终端中向用户展示关键结果摘要：

```
🧠 MBTI 分析完成！

类型：INTJ（架构师）
置信度：high

四维度得分：
  E-I: 87 → I（内倾）
  S-N: 85 → N（直觉）
  T-F: 22 → T（思考）
  J-P: 25 → J（判断）

人格素描：
  [portrait 内容]

🔗 查看完整画像：[URL]
📄 结果已保存到：_mbti_work/result.json
```

---

## 注意事项

- **隐私保护**：分析结果中不包含用户的真实姓名、项目名称、公司名称等隐私信息。quote 字段只截取关键部分，不超过 50 字。
- **语言**：根据用户聊天的主要语言输出（中文用户输出中文，英文用户输出英文）
- **最少数据**：如果聊天记录少于 10 条用户消息，告知用户数据不足，置信度标记为 `low`
- **不上传原始数据**：所有分析在本地完成，只有结构化 JSON 通过 URL Hash 参数传递给展示网页
- **网页展示**：展示页面为纯前端 HTML，数据从 URL Hash 解析，不经过任何服务器
