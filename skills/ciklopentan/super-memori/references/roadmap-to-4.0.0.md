# super_memori — Roadmap to 4.0.0

## Purpose
This is the short instruction for turning the current `super_memori` release into a **true full-hybrid runtime release** later.

Use this roadmap when the goal is no longer documentation/spec quality, but an actual verified `4.0.0` runtime.

## 7-step roadmap

### 1. Freeze and verify the baseline
Run:
```bash
health-check.sh --json
index-memory.sh --stats --json
query-memory.sh --json "deepseek"
```
Do not start hybrid work until lexical baseline is healthy.

### 2. Install and verify semantic prerequisites
Confirm all of these:
- Qdrant reachable
- embedding dependencies installed
- vector collection exists
- local CPU embedding path works

If any prerequisite fails, stop and fix it before moving on.

### 3. Implement semantic indexing for canonical files
Add a deterministic path from canonical memory files to vector upserts.
Do not move canonical truth out of markdown/files.

### 4. Add semantic freshness + backlog visibility
Track and surface:
- last semantic index build
- semantic stale age
- semantic queue backlog
- semantic degraded state

### 5. Implement hybrid retrieval inside `query-memory.sh`
The runtime must do this internally:
- lexical retrieve
- semantic retrieve
- candidate fusion
- unified result bundle

Do not make weaker models choose the backend.

### 6. Add reranker last
Only after hybrid retrieval works.
Reranker is a quality layer, not the foundation.
It must degrade safely if unavailable.

### 7. Re-test and only then release `4.0.0`
A release may be called `4.0.0` only if all are true:
- lexical search verified
- semantic search verified
- hybrid search verified
- health-check distinguishes healthy hybrid vs degraded mode
- documentation matches runtime reality

## Hard rule
Do not call the skill full hybrid just because Qdrant is running.
It is full hybrid only when retrieval, freshness, health, and docs all agree.
