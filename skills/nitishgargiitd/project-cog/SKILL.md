---
name: project-cog
description: "Persistent knowledge workspaces for agents. Upload documents, build AI-processed context trees, retrieve structured knowledge. Works with CellCog chats or standalone as agent memory. Persists across sessions. Use for shared docs, team knowledge, or domain-specific context. Powered by CellCog."
metadata:
  openclaw:
    emoji: "📂"
    os: [darwin, linux, windows]
    requires:
      bins: [python3]
      env: [CELLCOG_API_KEY]
author: CellCog
homepage: https://cellcog.ai
dependencies: [cellcog]
---

# Project Cog - Knowledge Workspaces for Agents

Persistent knowledge that survives across sessions — upload documents, build context trees, retrieve structured knowledge.

---

## Prerequisites

This skill requires the `cellcog` skill for SDK setup and API calls.

```bash
clawhub install cellcog
```

**Read the cellcog skill first** for SDK setup. This skill shows you what's possible.

**OpenClaw agents (fire-and-forget — recommended for long tasks):**
```python
result = client.create_chat(
    prompt="[your task prompt]",
    notify_session_key="agent:main:main",
    task_label="my-task",
    chat_mode="agent",
    project_id="your_project_id",  # Attach project context
)
```

**All other agents (blocks until done):**
```python
result = client.create_chat(
    prompt="[your task prompt]",
    task_label="my-task",
    chat_mode="agent",
    project_id="your_project_id",
)
```

See the **cellcog** mothership skill for complete SDK API reference.

---

## What CellCog Has Internally

1. **Context Tree System** — AI processes uploaded documents into hierarchical, searchable knowledge structures.
2. **Signed URL Retrieval** — Secure access to uploaded documents via time-limited URLs.
3. **Persistent Storage** — Project knowledge survives across sessions and chats.
4. **Multi-Agent Access** — Team agents share the same project knowledge base.

---

## Two Usage Modes

### 1. CellCog Chat Context
Attach a project to a CellCog chat with `project_id`. The agent automatically has access to all project documents and context trees during the conversation.

### 2. Standalone Agent Memory
Use project workspaces as persistent memory for any OpenClaw agent — upload work documents, research, and context that your agent can retrieve across sessions without CellCog chats.

---

## What You Can Do

- Upload documents (PDF, DOCX, XLSX, images, code files)
- Build AI-processed context trees for structured retrieval
- Share knowledge across team agents
- Persist project context across sessions
- Retrieve documents with signed URLs

---

## Chat Mode

**Use `chat_mode="agent"`** for project management.

---

## Related Skills

- **code-cog** — Coding agent (benefits from project context)
- **cowork-cog** — Direct machine access
- **research-cog** — Deep research (can feed findings into projects)
