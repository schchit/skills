# super_memori v3 — Architecture

## Objective
Build a local-first hybrid memory system for OpenClaw agents where files are canonical, retrieval is hybrid, and degraded modes remain useful.

## Canonical layers
1. Markdown/files in `memory/` are the source of truth.
2. SQLite FTS5 is the lexical / metadata index.
3. Qdrant is the semantic index.
4. Optional CPU reranker improves final ranking but is not required for core operation.

## Why this architecture
- Files survive index corruption and remain readable to humans.
- SQLite FTS5 is strong for exact/path/tag/command recall.
- Qdrant is strong for semantic recall and filtered vector retrieval.
- Weak models perform best when the retrieval logic is hidden behind a small CLI surface.

## Recommended pipeline
```text
query
  → hard filters
  → lexical retrieval (FTS5)
  → semantic retrieval (Qdrant)
  → fusion
  → optional rerank
  → dedupe/diversity pass
  → result bundle
```

## Storage model
- Canonical memory remains file-based.
- Chunk metadata lives in SQLite.
- Embeddings live in Qdrant.
- Queue/backlog state lives locally on disk.

## Required degraded modes
- Qdrant down → lexical-only mode with warning
- reranker unavailable → no-rerank mode with warning
- stale vectors → lexical + warning
- lexical DB damaged → emergency grep fallback if possible

## Target environment
- Ubuntu
- CPU-only host
- OpenClaw agent controlled by weaker models
- Local-first operation with no mandatory external APIs

## Non-goals for initial v3
- graph database first
- autonomous self-rewrite of memory policy
- many public scripts
- canonical storage inside vector DB
