---
name: huo15-doc-template
displayName: 火一五文档技能
description: 火一五文档技能 — 专业 Word 文档生成与 OpenClaw 工作区配置生成。支持从模板或结构化数据快速生成提案、报告、合同、会议纪要等 Word 文档。触发词：写 Word、写文档、生成 Word、创建 Word、生成文档、docx、提案、报告、合同、会议纪要。
version: 1.2.0
dependencies:
  scripts: ./scripts/
---

# SKILL.md - huo15-doc-template

> 火一五文档技能 — 专业 Word 文档生成与 OpenClaw 工作区配置生成

---

## 两大功能

### 1. Word 文档生成（主动触发）

当用户要求创建或编辑 Word 文档时，主动使用本技能。

**支持文档类型：**
| 类型 | 模板 | 说明 |
|------|------|------|
| `proposal` | 提案 | 蓝色标题，适合商务提案、项目方案 |
| `report` | 报告 | 深蓝标题，适合项目报告、工作汇报 |
| `contract` | 合同 | 黑色标题，适合合同协议类文档 |
| `minutes` | 会议纪要 | 绿色标题，适合会议记录 |
| `generic` | 通用 | 默认模板 |

**触发词：**
- "写 Word"、"生成 Word"、"创建 Word"、"编辑 Word"
- "写文档"、"生成文档"、"编辑文档"、"创建文档"
- "生成提案"、"写报告"、"起草合同"、"会议纪要"
- ".docx"、"Word 文档"、"Word 模板"

### 2. OpenClaw 配置生成（原有功能）

从客户调查问卷自动生成 OpenClaw 引导文件。

**触发词：**
- "生成配置"、"生成引导文件"
- "生成问卷配置"、"生成工作区"
- "帮我配置 OpenClaw"、"初始化工作区"

---

## Word 文档生成

### 使用方式

**交互式（推荐）：**
```
用户：帮我写一份项目提案
助手：请问文档标题是什么？
用户：OpenClaw 插件开发提案
助手：请输入文档内容（支持 Markdown 格式，# 标题 - 列表等）
用户：# 项目背景\n- OpenClaw 是一个...\n# 技术方案\n- 采用 Node.js 开发
助手：[调用 create-word-doc.py 生成文档]
```

**脚本直接调用：**
```bash
bash scripts/create-word-doc.py <输出路径> <标题> <内容> <模板类型>

# 示例：生成项目提案
bash scripts/create-word-doc.py proposal.docx "插件开发提案" \
  "# 项目背景\n- OpenClaw 插件市场潜力巨大" \
  proposal

# 示例：生成会议纪要
bash scripts/create-word-doc.py meeting.docx "2026年4月周会" \
  "# 与会人员\n- 张三\n# 议题\n- 项目进度" \
  minutes
```

### Python 方式

```bash
python3 scripts/create-word-doc.py output.docx "标题" "内容" proposal
```

### 输出特性

- 自动添加页脚（青岛火一五信息科技有限公司 | www.huo15.com）
- 支持 Markdown 格式（`#` 标题、`-` 列表、`1.` 编号列表）
- 多级标题自动映射为 Word 样式
- 1.5 倍行距，清晰易读

---

## OpenClaw 配置生成

### 使用方式

```bash
bash scripts/generate-config.sh <问卷JSON路径> [输出目录]
```

示例：

```bash
bash scripts/generate-config.sh ./customer问卷.json ~/.openclaw/workspace
```

### 生成的文件

| 文件 | 说明 |
|------|------|
| `SOUL.md` | AI 人格定义（语气、风格、定位） |
| `IDENTITY.md` | AI 身份信息（名字、头像、角色） |
| `USER.md` | 用户信息（姓名、公司、职位、作息、偏好） |
| `AGENTS.md` | 工作区规则（启动顺序、红线规则） |
| `BOOTSTRAP.md` | 首次对话引导脚本 |
| `HEARTBEAT.md` | 定期心跳检查任务列表 |
| `TOOLS.md` | 常用工具配置 |
| `MEMORY.md` | 长期记忆文件 |
| `memory/YYYY-MM-DD.md` | 每日记忆目录 |

### 问卷 JSON 格式

```json
{
  "name": "张三",
  "company": "某某公司",
  "role": "技术总监",
  "timezone": "Asia/Shanghai",
  "personality": "jarvis",
  "language": "中文",
  "replyStyle": "简洁直接",
  "workSchedule": {
    "workStart": "09:30",
    "workEnd": "18:00",
    "lunchBreak": "12:00-13:00",
    "restDays": "周末双休",
    "canDisturbAfterHours": false,
    "sleepReminderTime": "23:00"
  },
  "tools": ["Claude", "GitHub", "钉钉"],
  "projects": ["OpenClaw技能开发", "Odoo实施"]
}
```

---

## 相关技能

- `huo15-knowledge-base` — 知识库管理
- `huo15-mit-48h-learning-method` — 学习框架
- `huo15-plan-mode` — 计划模式
