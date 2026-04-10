---
name: skill-manager-all-in-one
description: |
  一站式管理 OpenClaw 技能的创建、修改、发布，维护与审计，覆盖完整生命周期。
  Manage OpenClaw skills end to end: create, modify, publish, maintain, and audit across the full lifecycle.
  触发词：技能管理、创建技能、发布技能、技能审核、技能清单、skill management。
---

# Skill Manager All In One | 一站式技能管理器

## 核心原则 | Core Rules

1. **Local first, network second** — 先检查本地已安装技能，再搜索网络。
2. **User approval first** — 未经明确确认，不要发布、更新、删除、隐藏或实质性改写技能。
3. **Be concrete** — 汇报时写清楚准确路径、准确命令、准确版本变化。
4. **One by one, confirm one by one** — 涉及多个文件/版本/技能时，必须逐个处理、逐个确认。禁止批量操作。
5. **Publish like a product** — 发布文本应像正式发布说明，而非聊天记录。
6. **Output quality** — 名称、描述、changelog 和文案都必须干净、可发布。
7. **For AI and humans** — 技能正文应兼顾 agent 与人类可读性。
8. **Publish then verify** — 发布后必须验证结果符合预期。
9. **No batch unless asked** — 只有用户明确要求时才能批量操作。

## 技能生命周期 | Skill Lifecycle

```
Phase 1: 制作/修改/优化
Phase 2: 发布前验证（两步验证）
Phase 3: 发布后维护
```

### Phase 1: 制作 / 修改 / 优化

- **权威参考**：`skill-creator` 技能（底层规则）
- **草稿目录**：`~/.openclaw/workspace/temp-skills/<slug>/`
- **完成标准**：内容完整、代码安全、本地验证通过

### Phase 2: 发布前验证（两步验证）

**所有发布/升版操作必须经过两步验证。**

#### 第一步：检查与汇报
1. 核对清单（通用 + 平台专项）
2. 文件大小检查（>50MB 需报告）
3. 平台专项检查
4. 拟定 Changelog

#### 第二步：详细汇报 → 等待确认
| 项目 | 内容 |
|------|------|
| Skill name + slug | 准确拼写 |
| 目标平台 | **ClawHub** / **GitHub** / 其他 |
| 当前版本 | 来自平台 inspect 命令 |
| 新版本号 | 递增（如适用） |
| Changelog | 英中文双语 |
| 文件大小 | 是否超 50MB |
| 核对清单 | 逐项 ✅/⚠️ |
| 发布命令 | 平台对应命令 |

**确认标志**：用户明确回复「好」「确认」「上传」等。

⚠️ **每次修改后，都必须从第一步重新开始。**

### Phase 3: 发布后维护

- **ClawHub**：`clawhub inspect <slug>` 验证
- **GitHub**：`git log` 验证
- **隐藏/恢复/删除**：执行前报告 + 执行后验证

---

## 发布平台专项 | Platform Guide

> **读取对应 reference 文件获取完整流程和清单。**

### 市场平台：ClawHub
- **文件**：`references/clawhub-publish.md`
- **验证**：`clawhub inspect <slug>`
- **上传限制**：50MB，坏符号链接检查

### 独立仓库：GitHub
- **文件**：`references/github-publish.md`
- **验证**：`git log`
- **安全约束**：严禁未经确认擅自 push

> 扩展新平台时，在 `references/` 下创建新文件，并在本节添加引用。

---

## 技能制作/修改清单 | Checklist

> 完整内容见下方或 `skill-creator` 技能。

### 通用规范 | General
| # | 检查项 | 说明 |
|---|---------|------|
| ① | 去标识化 | 无个人信息、内部路径、私有凭证 |
| ② | 安全性 | 无注入风险、无过度权限、无数据外传 |
| ③ | 逻辑科学性 | 结构清晰、路径准确、模块化 |
| ④ | 语言规范 | 英文骨架 + 中文辅助 |
| ⑤ | 名称规则 | slug 格式、display name 格式 |
| ⑥ | Changelog | 英文在前，禁止私人纠错 |

### 平台专项 | Platform
| 平台 | 检查项 |
|------|---------|
| **ClawHub** | 坏符号链接、运行时产物、Embedding 500 应急 |
| **GitHub** | git status、无未提交变更、commit 规范、Release Notes 规范 |

---

## 技能目录体系 | Directory System

| 目录 | 路径 |
|------|------|
| 正式技能 | `~/.openclaw/workspace/skills/` |
| 插件技能 | `~/.openclaw/extensions/` |
| 临时草稿 | `~/.openclaw/workspace/temp-skills/<slug>/` |
| 工作区资源 | `~/.openclaw/workspace/projects/<name>/` |

---

## 管理操作索引 | Operations Index

| 操作 | 命令/流程 |
|------|-----------|
| **上传 ClawHub** | 读 `references/clawhub-publish.md` → 两步验证 → `clawhub publish` |
| **上传 GitHub** | 读 `references/github-publish.md` → 两步验证 → `git push` |
| **创建 GitHub Release** | 读 `references/github-publish.md` → 两步验证 → `gh release create` |
| 查看 ClawHub | `clawhub inspect <slug>` |
| 升版 | 版本递增 → Phase 2 两步验证 |
| 隐藏 | `clawhub hide <slug>` → 验证 |
| 删除 | `clawhub delete <slug>` → 验证 |
| 搜索技能 | 本地优先 → `clawhub search` |

---

## 文件分工 | File Responsibilities

| 文件 | 职责 |
|------|--------|
| **SKILL.md** | 本文件 — 核心原则、生命周期、操作索引 |
| `references/clawhub-publish.md` | ClawHub 发布完整流程和清单 |
| `references/clawhub-inspect.md` | ClawHub 详情查看 |
| `references/github-publish.md` | GitHub 上传完整流程和清单 |
| `references/promotion.md` | 宣传推广专项 |
| `references/search-and-audit.md` | 搜索与审计专项 |
| `references/clawflows-workflow.md` | ClawFlows 格式规范 |

---

## 实用说明 | Practical Notes

- 执行敏感操作前，用 `clawhub --help` 核对当前 CLI 行为
- `skill-creator` 是底层规则权威来源
