# agent-memory-system-guide

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

GitHub 仓库：[cjke84/agent-memory-system-guide](https://github.com/cjke84/agent-memory-system-guide)

面向 OpenClaw 和 Obsidian 工作流的 Agent 长期记忆搭建指南。

最新发布：[v0.1.0](https://github.com/cjke84/agent-memory-system-guide/releases/tag/v0.1.0)

## 是什么

这个 skill 说明如何给 Agent 搭建长期记忆：用精简的 `MEMORY.md`、每日笔记、记忆蒸馏和 Obsidian 备份组成一套稳定的记忆层。
OpenViking 是可选增强层，用来补充语义召回和摘要。

## 可选增强

如果你后面想补语义召回和摘要，可以再加 OpenViking，但它不是核心流程的必需项。

## 适合谁

- 需要长期记忆的 Agent
- 需要保留每日笔记并蒸馏稳定事实的 Agent
- 想把 Obsidian 作为长期归档的用户

## 怎么用

1. 安装这个 skill。
2. 先复制 `templates/SESSION-STATE.md` 和 `templates/working-buffer.md`，再配合 `MEMORY.md` 和每日笔记使用。
3. 把稳定事实蒸馏进长期记忆，原始记录留在每日笔记里。
4. 将稳定知识归档到 Obsidian。

## Obsidian 原生笔记

- 稳定知识建议用 `templates/OBSIDIAN-NOTE.md`：包含 YAML frontmatter、wikilink、embeds、attachments 约定。
- 如果使用 Dataview，可以按 `type`、`status`、`tags`、`related` 做查询。

## 包含文件

- `SKILL.md`：技能契约与工作流
- `INSTALL.md`：可直接发给 Agent 的安装指令
- `templates/SESSION-STATE.md` 和 `templates/working-buffer.md`：恢复模板
