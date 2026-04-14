---
name: rewind-memory
description: Persistent, bio-inspired memory for AI agents. 5-layer architecture (L0-L4) with BM25 keyword search, knowledge graph, vector similarity, and HybridRAG fusion. Remembers everything across sessions. Triggers on "agent memory", "persistent memory", "remember across sessions", "rewind memory", "memory search", "knowledge graph", "recall previous".
---

# Rewind Memory — Persistent Memory for AI Agents

Give your agent memory that survives sessions, compactions, and restarts.

## What It Does

- **L0 Sensory Buffer** — BM25 keyword search over all indexed content
- **L1 System Memory** — core files loaded every session
- **L2 Orchestrator** — fuses all layers with unified multi-signal scoring
- **L3 Knowledge Graph** — entity extraction, relationships, spreading activation
- **L4 Vector Search** — semantic similarity via sqlite-vec

## Install

```bash
pip install rewind-memory
```

## Quick Start

```bash
rewind doctor          # auto-diagnose + build index
rewind ingest ./docs/  # index your files
rewind search "what did we decide about auth?"
rewind watch-sessions  # real-time conversation capture
```

## OpenClaw Integration

```bash
# Native hook (recommended — survives updates)
rewind-openclaw hook

# Or configure memory_search routing
rewind-openclaw setup
```

## MCP Server

```json
{
  "mcpServers": {
    "rewind": { "command": "rewind-mcp" }
  }
}
```

6 tools: memory_search, memory_store, memory_extract, memory_stats, memory_feedback, graph_traverse.

## Pro Upgrade

Pro adds L5 (communications), L6 (documents), NV-Embed-v2 4096-dim cloud embeddings, cross-encoder reranking, and bio-inspired lifecycle (decay, consolidation, pruning).

```bash
pip install rewind-memory-pro
```

## Links

- [Documentation](https://www.saraidefence.com/docs)
- [GitHub](https://github.com/saraidefence/rewind-memory)
- [PyPI](https://pypi.org/project/rewind-memory/)

Built by [SARAI Defence](https://saraidefence.com). Patent pending.
