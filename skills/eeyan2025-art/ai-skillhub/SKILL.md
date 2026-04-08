---
name: ai-skillhub
description: OpenClaw AI SkillHub 核心。当用户在 Discord 发送「!skill 关键词 URL」时自动触发：解析输入 → 提取 URL 内容（视频/音频/网页）→ 判断 Skill 是否已存在（新建或追加）→ 生成/追加 SKILL.md → 自动去重 → 自动分类 → 自动更新 index.md → 推送到 GitHub 仓库。全程无需人工干预。
# ---------------------------------------------------------------------------
# ⚠️ 必读：部署前需要配置以下 4 个环境变量（存储在 VPS 本地，不上传）
# ---------------------------------------------------------------------------
# GITHUB_TOKEN   — GitHub PAT，需 repo 全部权限（push 代码）
# MINIMAX_API_KEY — MiniMax API Key（视频/音频分析 + LLM 调用）
# GITHUB_REPO    — 格式：用户名/仓库名，例如 eeyan2025-art/skillhub
# GITHUB_BRANCH  — 分支名，默认 main
# ClawHub 上发布的 Skill 不包含任何真实密钥，仅含变量占位符
# ---------------------------------------------------------------------------
---

# AI SkillHub — 全自动知识策展系统

```
Discord: !skill 关键词 URL
    ↓
ai-skillhub（统一处理）
    ↓
┌─────────────────────────┐
│ Step 1: parse_input       │ ← 解析 !skill 关键词 URL
│   命令格式：!skill key URL │
└────────────┬──────────────┘
             ▼
┌─────────────────────────┐
│ Step 2: detect_platform   │ ← 判断 URL 平台类型
│   YouTube/Bilibili/微信...│
└────────────┬──────────────┘
             ▼
┌─────────────────────────┐
│ Step 3: extract_content  │ ← 提取内容
│   videos_understand      │ ← 视频
│   audios_understand      │ ← 音频
│   extract_content        │ ← 网页
└────────────┬──────────────┘
             ▼
┌─────────────────────────┐
│ Step 4: generate_skill   │ ← 生成 SKILL.md 内容
│   with LLM               │
└────────────┬──────────────┘
             ▼
┌─────────────────────────┐
│ Step 5: git_operations   │
│   • clone repo           │
│   • check if exists      │
│   • deduplicate          │
│   • append / create new   │
│   • update index         │
│   • push to GitHub       │
└────────────┬──────────────┘
             ▼
          完成！
```

## 命令格式

```
!skill <关键词> <URL>
```

**示例：**
```
!skill python https://bilibili.com/video/BV1xx411n7RS
!skill 法律知识 https://mp.weixin.qq.com/s/xxx
!skill 写作技巧 https://xiaohongshu.com/explore/xxx
```

**可选格式（自动识别）：**
```
【关键词】URL   ← 兼容旧格式
```

## 支持平台

| 平台 | 内容提取 | 备注 |
|------|---------|------|
| YouTube | `videos_understand` | 海外 VPS 必通 |
| Bilibili | `extract_content` + `audios_understand` | 中文内容最佳 |
| 西瓜视频 | `audios_understand` | 音频为主 |
| 微信公众号 | `extract_content` | 网页正文提取 |
| 小红书 | `extract_content` | 图文+视频 |
| 知乎 | `extract_content` | 文章+回答 |
| 任意 URL | `extract_content` | 通用网页 |

## 关键词与 Skill 映射规则

- 关键词 `python` → `skills/python/SKILL.md`
- 关键词 `法律知识` → `skills/法律知识/SKILL.md`
- 关键词用**英文或中文**均可，系统自动规范化

## Step 1: parse_input

解析输入，提取：
- `keyword`：规范化后的关键词（小写、中文保持原样、空格转为 `-`）
- `url`：原始 URL
- `date`：当前日期（格式 YYYY-MM-DD）

## Step 2: detect_platform

根据 URL 判断平台类型，返回对应处理策略。

## Step 3: extract_content

### 视频平台（YouTube、Bilibili）
使用 `videos_understand` 工具分析视频内容，prompt：

```
请完整转录视频内容，输出：
1. 视频主题（一句话）
2. 完整文字稿（关键信息保留）
3. 核心要点（3-5条）
4. 视频摘要（200字内）
```

### 音频内容
使用 `audios_understand` 工具。

### 网页内容
使用 `extract_content_from_websites` 工具，提取标题 + 正文。

## Step 4: generate_skill

调用 LLM 生成标准 SKILL.md 内容：

```json
{
  "prompt": "你是一个 Skill 设计专家。请根据以下内容，生成一个标准 OpenClaw SKILL.md。\n\n【来源内容】\n{content}\n\n【关键词】：{keyword}\n\n要求：\n1. frontmatter: name（{keyword}规范化）、description（触发条件+功能）\n2. 正文：## 工作流程、## 关键步骤、## 核心要点、## 注意事项\n3. 新增内容必须追加在最后，不要破坏已有结构\n4. 详细、可执行、有具体步骤\n5. 输出完整的 SKILL.md 内容（包含完整 frontmatter）",
  "model": "minimax/auto"
}
```

## Step 5: git_operations

### 5.1 克隆仓库
```bash
git clone "https://${GITHUB_TOKEN}@github.com/${GITHUB_REPO}.git" /tmp/skillhub_repo
```

### 5.2 检查 Skill 是否存在
```bash
ls /tmp/skillhub_repo/skills/{keyword}/SKILL.md
```

### 5.3 去重检测
在追加之前，检查新内容是否与已有内容高度重复（相似度 > 80%则跳过）。

### 5.4 追加 / 新建
- **已存在**：在现有 SKILL.md 末尾追加新内容（格式见下方）
- **不存在**：创建新目录和 SKILL.md

追加格式：
```markdown
---

## 【{YYYY-MM-DD}】新增：{来源标题}

{内容摘要}

来源：{URL}
```

### 5.5 自动更新 index.md
在仓库根目录维护 `index.md`（技能索引）：

```markdown
# AI SkillHub 索引

## 技能列表

| 关键词 | 名称 | 更新日期 | 描述 |
|--------|------|---------|------|
| python | Python 技能 | 2026-04-08 | ... |

## 最近更新
- 【2026-04-08】新增 python 技能（来源：bilibili.com/...）
```

### 5.6 推送
```bash
cd /tmp/skillhub_repo
git add .
git commit -m "Update skill [{keyword}] - $(date '+%Y-%m-%d')"
git push origin ${GITHUB_BRANCH:-main}
```

## 自动分类规则

Skill 文件夹按主题分类存放：

```
skills/
├── 编程开发/
│   ├── python/
│   ├── javascript/
│   └── rust/
├── 内容创作/
│   ├── 写作技巧/
│   └── 视频制作/
├── 商业运营/
│   ├── 法律知识/
│   └── 营销策略/
├── 效率工具/
│   └── ai工具/
└── index.md
```

分类由 LLM 根据关键词自动判断，写入 `index.md` 时自动归档。

## 环境变量

```bash
export GITHUB_TOKEN="ghp_xxxxx"       # GitHub Push 权限
export MINIMAX_API_KEY="eyJxxx"        # MiniMax API（用于 LLM 调用）
export GITHUB_REPO="用户名/仓库名"   # 例如：eeyan2025-art/skillhub
export GITHUB_BRANCH="main"
```

## 去重机制

追加新内容前，使用 LLM 判断内容相似度：
- **相似度 < 60%**：正常追加
- **相似度 60-80%**：合并重复部分后追加
- **相似度 > 80%**：跳过，告知用户"内容已存在"

## 错误处理

| 错误 | 处理方式 |
|------|---------|
| URL 无法访问 | 回复用户，提供手动导入方式 |
| 内容提取失败 | 降级使用 `batch_web_search` 获取替代信息 |
| Git push 失败 | 输出本地文件路径，告知用户手动 push |
| Skill 已存在且高度重复 | 回复"已存在，跳过"，提供查看链接 |
| MiniMax API 限流 | 等待 30 秒重试 1 次 |

## 最终用户体验

用户只需要发一条消息：

```
!skill python https://bilibili.com/video/BV1xx411n7RS
```

OpenClaw 自动完成全部流程，完成后回复：

```
✅ Skill 已更新：【python】
📦 来源：bilibili.com/video/BV1xx411n7RS
🔗 https://github.com/eeyan2025-art/skillhub/tree/main/skills/python
📝 已追加新内容（去重后新增 3 条要点）
🏷️ 分类：编程开发 / python
```

用户无需 SSH、无需手动操作，一切自动完成。

---

## 安全说明

本 Skill 需要以下密钥，**均存储在运行 OpenClaw 的 VPS 本地**，不会上传到 ClawHub 或任何第三方服务：

| 变量 | 用途 | 存储位置 |
|------|------|---------|
| `GITHUB_TOKEN` | Push 代码到 GitHub | VPS `~/.openclaw/.env`（不上传） |
| `MINIMAX_API_KEY` | LLM + 音视频分析 | VPS `~/.openclaw/.env`（不上传） |
| `GITHUB_REPO` | 指定目标仓库 | VPS `~/.openclaw/.env`（不上传） |

**ClawHub 上发布的 Skill 文件仅包含变量名占位符（如 `${GITHUB_TOKEN}`），不包含任何真实密钥。** 真实密钥由用户在部署时自行配置到 VPS 本地。
