# super_memori v3 — Retrieval Pipeline

## Default behavior
Use `--mode auto` unless a more specific mode is clearly required.

## Chunking contract
All retrieval layers must work against the same chunking model.
- Target chunk size: ~1200 characters
- Overlap: ~150 characters
- Canonical chunk id: hash of `{entry_id}:{chunk_index}:{chunk_prefix}`
- Chunk source of truth: canonical markdown/file content after frontmatter stripping
- Lexical and semantic indexes must refer to the same chunk granularity

## Embedding contract
Full hybrid mode should standardize on one CPU-friendly embedding profile unless explicitly changed.
- Default model family: multilingual small embedding model
- Expected vector size must be fixed per collection
- Cosine-ready normalization must be consistent across all vectors
- Model changes require explicit reindex/rebuild

## Stage 1 — Hard filters
Apply memory type, time range, tags, namespace, and reviewed-state filters before retrieval.

## Stage 2 — Lexical retrieval
Use SQLite FTS5/BM25 for exact strings, commands, paths, identifiers, tags, and high-precision retrieval.
Default candidate budget: top 20.

## Stage 3 — Semantic retrieval
Use Qdrant for meaning-based recall, paraphrases, and similar-past-problem lookups.
Default candidate budget: top 20.
Semantic candidates below the chosen minimum score should be discarded.

## Stage 4 — Fusion
Combine lexical and semantic candidates using reciprocal-rank fusion or equivalent weighted merging.
Default recommendation: RRF.
If semantic returns no usable candidates, continue lexical-only and surface a warning.

## Stage 5 — Optional rerank
Rerank only the short candidate list. Skip rerank for exact/path-heavy queries.
Recommended rerank budget: top 10 fused candidates.

## Stage 6 — Diversity pass
Prevent near-duplicate final results. Prefer a mix of exact, fresh, and authoritative matches.
Default rule: avoid flooding the final set with many chunks from the same source file.

## Stage 7 — Result bundle
Return snippets, source paths, scores, warnings, freshness state, and degraded flags.

## Execution decision tree
```text
query
  → hard filters
  → lexical retrieval (always)
  → semantic available?
      yes → semantic retrieval → fusion
      no  → warning → lexical-only
  → reranker available and needed?
      yes → rerank top fused candidates
      no  → skip rerank
  → diversity pass
  → result bundle
```

## Degraded behavior
- If semantic is unavailable but lexical works, return lexical results and say so.
- If lexical is unavailable but emergency grep works, return grep fallback and say so.
- Never silently downgrade quality.
