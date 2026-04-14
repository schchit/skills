# /rewind-index

Index (or re-index) your workspace into Rewind memory.

## Usage

```
/rewind-index [path]
```

## Instructions

When the user runs `/rewind-index`, execute:

```bash
rewind ingest "${ARGUMENTS:-.}" --recursive
```

This scans the workspace (or specified path) and indexes all supported files into:
- L0: Full-text search (BM25)
- L3: Knowledge graph (entity extraction)  
- L4: Vector embeddings (if embedding model available)

Show the ingest stats when complete (chunks, entities, vectors).
