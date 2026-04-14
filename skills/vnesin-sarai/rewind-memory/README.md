# Rewind Memory — Claude Code Plugin

Persistent memory for Claude Code. Every session builds on the last.

## What it does

- **Automatic context**: When you ask a question, Rewind searches your memory for relevant context from previous sessions
- **Session capture**: File edits, command outputs, and conversation turns are automatically indexed
- **Knowledge graph**: Entities and relationships are extracted and connected across your codebase
- **Semantic search**: Find anything from any previous session with natural language

## Install

```
/plugin install rewind-memory@saraidefence
```

Or manually:
```bash
pip install rewind-memory
git clone https://github.com/saraidefence/rewind-memory.git ~/.claude-plugins/rewind-memory
claude --plugin-dir ~/.claude-plugins/rewind-memory/plugin
```

## Setup

```
/rewind-setup
```

## Commands

| Command | Description |
|---------|-------------|
| `/rewind-setup` | Initialise Rewind for this workspace |
| `/rewind-search <query>` | Search memory across all layers |
| `/rewind-recall <topic>` | Deep multi-layer recall |
| `/rewind-index [path]` | Index files into memory |

## How it works

Rewind Memory uses a layered architecture inspired by biological memory systems:

- **L0 — Sensory** (BM25): Fast keyword search over all indexed content
- **L3 — Knowledge Graph**: Entity extraction and relationship mapping
- **L4 — Semantic** (Vector): Embedding-based similarity search

### Free tier
All processing runs locally. Entity extraction uses heuristics or Ollama (if available with `graph-preflexor` model).

### Pro tier  
Cloud-accelerated embeddings (NV-Embed-v2) and Graph-PReFLexOR KG extraction via Modal serverless GPU.

## Privacy

All data stays local by default. Pro tier cloud features are opt-in and only process text chunks — no conversation content is stored remotely.

## License

MIT — [github.com/saraidefence/rewind-memory](https://github.com/saraidefence/rewind-memory)
