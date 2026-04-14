# /rewind-recall

Recall context about a topic from all memory layers.

## Usage

```
/rewind-recall <topic>
```

## Instructions

When the user runs `/rewind-recall`, perform a deep search across all memory layers:

```bash
rewind search "$ARGUMENTS" --limit 10 
```

This searches:
- L0: Keyword matches (BM25)
- L3: Knowledge graph entities and relationships
- L4: Semantic similarity (vector search)

Present results grouped by layer, showing how the topic connects across the user's codebase, previous sessions, and stored knowledge.

If the knowledge graph has relevant entities, show the relationship path.
