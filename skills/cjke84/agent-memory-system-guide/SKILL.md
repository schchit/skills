---
name: agent-memory-system-guide
description: An Agent long-term memory guide for OpenClaw, Codex, and Obsidian workflows. Covers MEMORY.md, daily notes, session recovery, memory distillation, and optional OpenViking support.
---

# Agent Memory System Guide

> 🧠 An Agent long-term memory guide for OpenClaw, Codex, and Obsidian. Use a minimal `MEMORY.md`, daily notes, and archive flow to get started first, then distill and refine over time.

## 触发词

`记忆系统`、`memory-setup`、`搭建记忆`、`记忆架构`

## 5 分钟快速上手

**如果你赶时间，只做三步：**

### 第一步：创建 `MEMORY.md`

```markdown
# MEMORY.md

> 长期记忆。只保留会持续影响协作的事实、偏好和决策。

## User

- Preferred name: K
- Timezone: Asia/Shanghai

## 当前任务

- [ ] 正在做的事

## 决策记录

- YYYY-MM-DD: 决策内容 + 原因

## 踩坑记录

- 问题 → 解决方案
```

### 第二步：创建每日笔记

```markdown
# memory/2026-03-20.md

## 完成
- 分析了网宿科技

## 决策
- 暂不加仓

## 踩坑
- （无）

## 待办
- [ ] 明天要做什么
```

### 第三步：从模板创建 `SESSION-STATE.md` 和 `working-buffer.md`

```markdown
# SESSION-STATE.md

## 当前任务
- 任务名称

## 已完成
- ...

## 卡点
- ...

## 下一步
- ...

## 恢复信息
- 最近一次有效上下文：...
```

```markdown
# working-buffer.md

## 进行中
- ...

## 临时决策
- ...

## 未完成
- ...
```

### （可选）归档到 Obsidian 时使用笔记模板

当你需要把稳定知识写入 Obsidian vault 时，可以使用仓库提供的模板：

- `templates/OBSIDIAN-NOTE.md`：带 frontmatter、wikilink、embeds 的笔记骨架

### 第四步：每次对话开始时

```text
先读 SESSION-STATE.md，再读最近 1-3 天 daily notes，最后才做 memory_search。
memory_search(query="相关关键词")
```

## 核心架构（三层模型）

- `MEMORY.md`：长期记忆，精炼保存
- `memory/YYYY-MM-DD.md`：每日原始记录
- `SESSION-STATE.md`：当前任务真相来源
- `working-buffer.md`：短期工作缓冲
- `templates/SESSION-STATE.md`：恢复状态模板
- `templates/working-buffer.md`：工作缓冲模板
- `templates/OBSIDIAN-NOTE.md`：Obsidian 笔记模板（frontmatter / links / embeds）
- Obsidian：长期归档与备份

## Obsidian 原生约定（frontmatter / Dataview / wikilink / backlinks / embeds / attachments）

当你把稳定知识写入 Obsidian 时，建议遵循下面这些约定，保证可检索、可回链、可复用。

### frontmatter

- 用 YAML frontmatter 固定结构化字段，便于后续查询、筛选、聚合
- 推荐字段见 `templates/OBSIDIAN-NOTE.md`，核心是：`type`、`status`、`tags`、`related`

### Dataview

如果你使用 Dataview 插件，可以直接用 frontmatter 做查询，例如：

```text
TABLE type, status, tags, related
FROM "memory"
WHERE status != "archived"
SORT updated desc
```

### wikilink / backlinks

- 内部引用优先使用 wikilink：`[[SESSION-STATE]]`、`[[MEMORY]]`、`[[2026-03-21]]`
- 同一概念尽量用同一标题或 aliases，backlinks 才会稳定聚合到一起

### embeds / attachments

- 图片：本地资源优先用 `![[image.png]]`，远程资源保留 `![alt](https://...)`
- 引用证据：用 block quote，或用 block embeds `![[note#^block-id]]` 复用证据段
- attachments 建议放在 vault 内可管理的位置（例如 `attachments/`），避免链接失效

## 启动与结束顺序

- 启动时：先读 `SESSION-STATE.md`，再读最近 1-3 天 daily notes，最后才检索本地记忆
- 结束时：先更新 `SESSION-STATE.md`，再把稳定事实蒸馏进 `MEMORY.md`，最后归档 daily notes
- 中断后恢复：优先从 `working-buffer.md` 续接未完成项
- 仓库模板：先复制 `templates/SESSION-STATE.md` 和 `templates/working-buffer.md`，再填入当前任务

## OpenViking 可选增强

- OpenViking 不是强依赖；没有它也能完成核心的断点续接流程
- 有 OpenViking 时，优先把它作为语义召回和摘要补全层
- OpenViking 负责补充相关记忆，`SESSION-STATE.md` 负责保存当前任务真相
- 如果 OpenViking 不可用，直接退回到 `SESSION-STATE.md` + `working-buffer.md` + daily notes 的本地流程

## 维护原则

- 下次对话会用到的 → 保留在本地记忆
- 可能永远用不到但值得保留的 → 归档到 Obsidian
- 记忆膨胀时，先蒸馏再保留

## 兼容性

- OpenClaw-compatible skill
- Codex-compatible skill
- OpenViking-compatible optional enhancement
- Obsidian vault workflows
