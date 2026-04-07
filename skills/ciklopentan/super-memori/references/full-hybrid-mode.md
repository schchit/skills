# super_memori — Full Hybrid Mode

## Purpose
Define the **next complete target state** of `super_memori` where lexical, semantic, fusion, rerank, freshness, and health all operate as one coherent local-memory subsystem.

This file is intentionally a **design + implementation contract**, not a claim that the current host already runs all layers.

## Full Hybrid Definition
A full-hybrid `super_memori` run means:
1. canonical files are readable
2. lexical registry/index is healthy
3. semantic backend is healthy
4. embeddings can be generated locally
5. lexical + semantic candidates are fused
6. optional reranker can refine the final candidate set
7. degraded states are surfaced explicitly

## Target runtime flow
```text
query-memory.sh --mode auto "query"
  → normalize query
  → apply hard filters
  → lexical retrieval (SQLite FTS5)
  → semantic retrieval (Qdrant)
  → fuse candidate sets
  → optional rerank (top-N only)
  → dedupe/diversify
  → return results + warnings + freshness
```

## Full-Hybrid Readiness Checklist
A host is only in full-hybrid mode if **all** are true:
- `health-check.sh` reports lexical DB healthy
- `health-check.sh` reports Qdrant reachable
- embedding dependencies are installed
- vector collection exists and is populated
- lexical freshness is current
- semantic freshness is current
- backlog queue is within threshold
- `query-memory.sh --mode hybrid --json` returns `mode_used=hybrid` without semantic degradation warnings

## Semantic Layer Requirements
The semantic layer must support:
- local embeddings on CPU
- vector upsert/update
- vector search with payload filters
- freshness visibility
- explicit degraded mode when unavailable
- a fixed embedding contract (dimension + normalization + rebuild rules)

## Fusion Contract
The skill should eventually implement one deterministic fusion method:
- reciprocal rank fusion, or
- weighted lexical + semantic merge

Default recommendation:
- lexical candidates: top 20
- semantic candidates: top 20
- rerank candidates: top 10 after fusion
- if semantic returns no usable candidates, continue lexical-only and warn

This must happen inside `query-memory.sh`, not inside model reasoning.

## Rerank Requirements
Reranking is optional for baseline operation but required for full-hybrid quality mode.

Rules:
- rerank only small candidate sets
- skip rerank for exact/path-heavy queries
- do not block the whole query if reranker is unavailable
- surface reranker degradation as a warning, not a silent failure

## Weak-Model Implementation Order
When a weaker model is asked to finish hybrid mode later, it should follow this exact order:
1. run `health-check.sh`
2. verify lexical baseline still passes
3. verify semantic dependencies are installed
4. verify vector collection exists
5. implement semantic indexing path
6. verify semantic freshness reporting
7. implement hybrid candidate fusion
8. verify hybrid query output
9. only then add reranker
10. re-run health and retrieval tests

## Acceptance Criteria for Full Hybrid Mode
A release can claim full hybrid mode only if all are true:
- lexical search works
- semantic search works
- hybrid search works
- health check distinguishes lexical-only vs hybrid-ready
- queue/backlog is monitored
- stale semantic state is surfaced
- at least one live test proves hybrid mode selected automatically
- documentation matches the actual runtime behavior

## Anti-Patterns
Do not call the skill full-hybrid if any of these are true:
- semantic dependencies are missing
- vector collection exists but is stale and unreported
- reranker is required for all queries
- the model must manually choose lexical vs semantic backend
- degraded states are only visible in logs, not in command output
