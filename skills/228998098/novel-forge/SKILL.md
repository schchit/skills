---
name: novel-forge
description: Long-form novel workflow for creating, continuing, resuming, and repairing serialized fiction with externalized project state, role-to-model mapping, worldbuilding, character sheets, outlines, style sampling, chapter drafting, consistency review, and memory tracking. Use when the user asks to start a novel project, continue or resume a draft, recover from truncation, assign models to roles, generate canon or chapters, review for consistency, or maintain a long-running fiction project across many chapters. Supports single-agent or multi-agent execution, with multi-agent as the default.
---

# Novel Forge

**Version:** v1.0.0

## Overview / 技能简介

Use this skill to run long-form fiction as a **stateful pipeline**, not as chat memory.
It helps with novel project setup, continuation, truncated recovery, model-role mapping, canon building, chapter drafting, and consistency review.

**中文卖点：** 让你用文件化状态稳定连载长篇小说，支持新建、续写、断档恢复和多角色模型分工。

## Quick start / 快速开始

## 使用示例 / Examples

1. `帮我新建一个小说项目，题材是奇幻冒险，默认多 agent`
2. `继续写这本小说，从上次断开的地方接着写`
3. `从第5章恢复，并帮我检查当前角色和模型分工`

- New novel: say `help me start a novel project` / `帮我新建一个小说项目`
- Continue novel: say `continue novel <title>` / `继续写《标题》`
- Resume a truncation: say `resume from chapter 3` / `从第3章断档处继续`
- If you want multiple agents, the skill will ask you to map roles to models first.
- If you want single-agent, say so explicitly; otherwise multi-agent is the default.

## 中文说明

这是一个给**长篇小说连载**用的技能。它会把小说状态放在文件里，而不是只靠聊天记录记忆。

你可以直接这样说：
- `帮我新建一个小说项目`
- `继续写《寄魂》`
- `从第5章断档处恢复`
- `帮我检查这个小说技能是否适合继续写`

如果你选择多 agent，系统会先让你确认角色和模型分工；如果你不特别说明，默认按多 agent 流程来处理。

## Core contract

- Keep the project state in files.
- Keep the main session lightweight.
- Use writer and reviewer stages for prose when multi-agent is active.
- Never let the main session silently author or rewrite canon prose.
- Never assume missing facts; read or ask.

## Where state lives

Treat these as the source of truth:
- `project.json`
- `worldbuilding.md`
- `characters.md`
- `outline.md`
- `style.md`
- `memory.md`
- `chapters/*.md`
- `state/current.json` when present

Prefer `state/current.json` for fast recovery and chapter-boundary checks when it exists.

For the operational state machine and run order, see:
- `references/state-machine.md`
- `references/runbook.md`
- `references/schemas.md`
- `references/workflow.md`

## When to use this skill

Use this skill when the user wants to:
- start a new long-form fiction project
- continue or resume a novel
- recover from a truncated or partial chapter
- assign models to orchestration/writing/review roles
- generate worldbuilding, character dossiers, outlines, or style samples
- draft chapters with consistency checks
- maintain memory and canon across many chapters

## Operating rules

1. If the request is a continuation/resume, discover candidate projects first and let the user choose when needed.
2. If multi-agent is active, inspect the current model inventory and ask for a role→model mapping.
3. Persist the chosen mapping in project state.
4. Confirm title, genre/audience, target length, taboo list, premise, execution mode, and checkpoint before canon generation.
5. Build canon in order: worldbuilding → characters → outline → style → chapters.
6. Do not parallelize phase 0 canon work if it depends on previous canon.
7. Draft one chapter beat at a time.
8. In multi-agent mode, run writer → reviewer → orchestrator. In single-agent mode, keep the same state-machine discipline but collapse the writing stages into one controlled pass.
9. After acceptance, sync chapter summary, memory, and state together.

## Anti-drift rules

- Use only the smallest relevant canon slice.
- Prefer explicit character states and open loops over implied memory.
- Keep style rules compact and persistent.
- Treat reviewer output as required, not optional.
- If provenance is missing or ambiguous, stop.

## Writing constraints

Default all prose stages to:
- concrete actions
- body language
- sensory detail
- character-specific diction
- scene-local observations

Avoid:
- template transitions
- repetitive contrast formulas
- abstract summary piles
- explanatory filler
- symmetrical machine-like paragraphs

## Output shape

For planning tasks, output a compact structure such as:
- Project brief
- Model assignment
- Canon status
- Outline / beat sheet
- Risks / conflicts
- Next action

For writing tasks, keep stages distinct:
- Chapter goal
- Chapter writer draft
- Review notes
- Revision summary
- Memory update

## Failure behavior

- If a required fact is missing, ask.
- If the resume checkpoint is unclear, stop.
- If the reviewer has no draft, treat the workflow as incomplete.
- If the main session is about to write the chapter directly in multi-agent mode, hand off to the writer stage instead.

## Resources

Read the referenced files only when needed:
- `references/state-machine.md`
- `references/runbook.md`
- `references/schemas.md`
- `references/workflow.md`
- `references/prompts.md`
- `references/examples.md`
- `scripts/build_context_pack.py`
- `scripts/discover_projects.py`
- `scripts/scaffold_project.py`
