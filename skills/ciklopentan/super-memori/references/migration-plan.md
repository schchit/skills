# super_memori v3 — Migration Plan

## Current state
The root scripts in this skill folder now implement the v3 public command surface baseline. Older v2 behavior is preserved under `scripts/legacy/` and helper files for migration/reference.

## Migration goal
Move from a mixed grep/vector prototype to a hybrid local-memory subsystem with explicit contracts, freshness reporting, and weak-model-safe operation.

## Recommended phases

### Phase 1 — Stabilize public interface
- Keep the root public surface at four commands
- Keep lexical retrieval, health, queue, and freshness working
- Stop making stronger semantic claims than implementation supports

### Phase 2 — Introduce lexical registry
- Add SQLite metadata + FTS5
- Keep files canonical
- Route exact/path/tag retrieval through lexical index

### Phase 3 — Formalize semantic layer
- Keep Qdrant as derived semantic backend
- Add freshness reporting and degraded-mode warnings
- Stop mixing backend claims in user-facing text
- Meet the conditions described in `full-hybrid-mode.md`

### Phase 4 — Add quality/ops layer
- Optional CPU reranker
- queue/backlog handling
- stronger health checks
- duplicate/orphan detection
- Follow `implementation-order.md` exactly when weaker models finish the remaining work

## Rule during migration
Never claim "v3 implemented" until scripts match the new command contracts and health model.
