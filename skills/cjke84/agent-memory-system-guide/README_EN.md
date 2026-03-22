# agent-memory-system-guide

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

GitHub repository: [cjke84/agent-memory-system-guide](https://github.com/cjke84/agent-memory-system-guide)

An Agent long-term memory guide for OpenClaw, Codex, and Obsidian workflows.

It helps you build a durable memory stack with a compact `MEMORY.md`, daily notes, session recovery files, and Obsidian archiving. OpenViking is included as an optional enhancement for semantic recall and summary support, not as a hard dependency.

Latest release: [v0.1.0](https://github.com/cjke84/agent-memory-system-guide/releases/tag/v0.1.0)

## What it is

This skill explains how to build a durable memory stack for agents: a compact `MEMORY.md`, daily notes, memory distillation, and Obsidian backups.
OpenViking is an optional enhancement for semantic recall and summary support.

## Optional enhancement

OpenViking can be added later if you want semantic recall and summary support, but it is not required for the core workflow.

## Who it is for

- Agents that need persistent memory
- Agents that should keep daily notes and distill stable facts
- Users who want Obsidian as the long-term archive

## How to use

1. Install the skill.
2. Copy `templates/SESSION-STATE.md` and `templates/working-buffer.md`, then use them with `MEMORY.md` and daily notes.
3. Distill stable facts into long-term memory and keep raw notes in daily files.
4. Archive stable knowledge into Obsidian.

## Obsidian-native notes

- Use `templates/OBSIDIAN-NOTE.md` for durable notes: YAML frontmatter, wikilinks, embeds, and attachment conventions.
- With Dataview, you can query your notes by `type`, `status`, `tags`, and `related`.

## Included files

- `SKILL.md`: skill contract and workflow
- `INSTALL.md`: a copy-paste installation prompt for agents
- `templates/SESSION-STATE.md` and `templates/working-buffer.md`: recovery templates
