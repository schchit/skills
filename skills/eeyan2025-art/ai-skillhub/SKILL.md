---
name: ai-skillhub
description: AI SkillHub 核心。当用户发送「!skill 关键词 URL」或「!skill URL」时触发：提取内容 → 生成摘要 → 推送 GitHub。
---

# AI SkillHub — 知识策展系统

## 命令格式

支持两种格式：
- `!skill <关键词> <URL>` — 指定关键词
- `!skill <URL>` — 自动从内容标题生成关键词

---

## 第零步：立即回复

收到命令后**第一件事**是回复用户：

```
收到！正在处理「{URL}」，预计 1-3 分钟...
```

---

## Step 1: 解析输入

判断格式：
- 两个参数（关键词 + URL）→ keyword 和 url 都已确定
- 一个参数（只有 URL）→ url 已确定，keyword 在 Step 3 从标题自动生成

---

## Step 2: 提取网页正文

调用 `web_fetch` 工具（这是正确工具，直接 HTTP 获取，不需要浏览器）：

```json
{
  "url": "{url}",
  "extractMode": "markdown"
}
```

`web_fetch` 会自动用 Chrome User-Agent 发送 HTTP GET，对微信公众号、知乎等公开文章有效。

如果是 B站/YouTube 视频 URL（包含 bilibili.com 或 youtube.com/watch），跳过此步骤，进入 Step 2B。

### Step 2B: 视频字幕提取（仅限 B站/YouTube）

用 `exec` 工具运行字幕提取：

```json
{
  "tool": "exec",
  "command": "python3 ~/.openclaw/scripts/yt_transcript.py {url} 2>&1"
}
```

---

## Step 3: 确定关键词

如果输入只有 URL（无关键词），从 Step 2 返回的标题中提取 2-4 个核心词作为关键词（用连字符连接）。

例：标题"只需要一个CLI，Agent就可以下载公众号" → 关键词 = "opencli-agent-下载"

---

## Step 4: 保存原始内容

用 `exec` 工具把完整内容写入文件：

```json
{
  "tool": "exec",
  "command": "cat > /tmp/raw_content.md << 'RAWEOF'\n# 原始内容记录\n\n## 来源\n- URL: {url}\n- 关键词: {keyword}\n- 时间: $(date '+%Y-%m-%d %H:%M')\n\n## 内容\n\n{Step 2 返回的完整内容}\nRAWEOF"
}
```

---

## Step 5: 生成摘要

调用 `llm-task` 工具：

```json
{
  "prompt": "你是知识策展专家。根据以下文章内容，生成一份结构化技能卡片（Markdown 格式，中文），包含：\n1. 核心要点（3-5条）\n2. 关键概念\n3. 实用价值\n4. 适合人群",
  "input": "{Step 2 返回的完整内容}"
}
```

---

## Step 6: 推送 GitHub

用 `exec` 工具执行 git 操作：

```json
{
  "tool": "exec",
  "command": "cd /tmp && rm -rf skillhub_repo && git clone \"https://${GITHUB_TOKEN}@github.com/${GITHUB_REPO}.git\" skillhub_repo && mkdir -p skillhub_repo/skills/{keyword} && cp /tmp/raw_content.md skillhub_repo/skills/{keyword}/原始内容.md && git -C skillhub_repo add . && git -C skillhub_repo -c user.email=bot@skill.ai -c user.name=SkillBot commit -m 'Add skill [{keyword}]' && git -C skillhub_repo push origin ${GITHUB_BRANCH:-main} && rm -rf /tmp/skillhub_repo",
  "timeout": 120
}
```

---

## Step 7: 完成通知

回复用户（纯文字，不要输出 JSON 或 XML）：

```
✅ Skill 已完成：【{keyword}】
📄 原始内容：skills/{keyword}/原始内容.md
🧠 技能摘要：skills/{keyword}/SKILL.md
📦 来源：{url}
```

---

## 工具使用规则（必须遵守）

| 需要做什么 | 使用的工具 |
|-----------|-----------|
| 获取网页/文章内容 | `web_fetch` |
| 运行 shell 命令（git、文件操作）| `exec` |
| AI 摘要/分析 | `llm-task` |

- `extract_content_from_websites`、`audios_understand`、`search` 等工具**不存在**，禁止调用
- 所有工具调用都会被系统执行，**不要把工具调用当文字输出**
- 每步完成后发一条简短进度消息给用户
