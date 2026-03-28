---
name: vyasagraph
description: Give your AI agent persistent memory — both short-term (SESSION-STATE) and long-term (VyasaGraph knowledge graph). Eliminates agentic amnesia. Stores entities, relations, and observations with semantic vector search. No server required.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": [] },
        "install":
          [
            {
              "id": "node",
              "kind": "node",
              "package": "vyasagraph",
              "label": "Install VyasaGraph (npm)",
            },
          ],
      },
  }
---

# VyasaGraph — Persistent Agent Memory

**No more agentic amnesia.** VyasaGraph gives your agent two memory layers:

1. **SESSION-STATE** (RAM) — hot context for the current session. Survives context compaction.
2. **VyasaGraph** (hard drive) — permanent knowledge graph with semantic vector search. Persists across sessions.

## Setup

```bash
npm install vyasagraph
```

Copy the SESSION-STATE template to your workspace root:

```bash
cp node_modules/vyasagraph/SESSION-STATE-TEMPLATE.md SESSION-STATE.md
```

Set your OpenAI API key (for semantic embeddings — text search works without it):

```bash
# .env
OPENAI_API_KEY=sk-...
```

## Wire into your agent

Add this to your **MEMORY.md** (or equivalent instruction file):

```markdown
## FIRST ACTION EVERY MESSAGE — MANDATORY
1. READ `SESSION-STATE.md` for hot context from current session
2. WRITE to SESSION-STATE.md BEFORE responding if user gives new decisions, deadlines, or context
3. SEARCH VyasaGraph: `const results = await vg.smartSearch('topic', 5);`
4. THEN respond with loaded context

## AUTO-RECORD — EVERY CONVERSATION
When the user shares substantive information, record it in that same reply:
- New facts about people → addObservations()
- Decisions or strategies → createEntities() + addObservations()
- Status changes → updateEntity()

## SESSION-STATE vs VyasaGraph
- SESSION-STATE = CPU cache (hot, ephemeral, write-ahead log)
- VyasaGraph = hard drive (permanent, semantic search, cross-session)
- Both required. Neither replaces the other.
```

Add this to your **SOUL.md**:

```markdown
## Memory System
I use a two-layer memory stack:
1. SESSION-STATE.md — working memory for the current session. I read this at the start of every message and update it before responding with anything important.
2. VyasaGraph — long-term knowledge graph. Stores entities, relations, and observations with semantic search. I search this on every substantive message.

If the user tells me something I didn't know before, I write it to VyasaGraph in that same reply.
```

## Basic Usage

```javascript
import * as vg from 'vyasagraph/src/index.js';

// Initialize
await vg.init('memory.db');

// Store knowledge
await vg.createEntities([{
  name: 'Alice (user)',
  entityType: 'Person',
  observations: ['Software engineer', 'Based in Berlin', 'Prefers concise answers']
}]);

// Add facts as you learn them
await vg.addObservations([{
  entityName: 'Alice (user)',
  contents: ['Leading the platform redesign project']
}]);

// Semantic search
const results = await vg.smartSearch('engineering Berlin', 5);

// Always close
await vg.close();
```

## Project Tracking (v3)

```javascript
await vg.createEntities([{
  name: 'P01 - Website redesign',
  entityType: 'Project',
  observations: ['Modernise company website'],
  metadata: {
    status: 'Active',      // Not Started | Active | On Hold | Blocked | Complete
    priority: 'High',
    category: 'Work',
    nextAction: 'Finalise wireframes'
  }
}]);

// Get formatted task board
const board = await vg.formatAsVtasks();
```

## Full docs

- GitHub: https://github.com/minopop/vyasagraph
- npm: https://www.npmjs.com/package/vyasagraph
- INSTALL.md (bundled) — full wiring guide for SOUL.md / MEMORY.md
