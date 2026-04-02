# Cold Memory Schema

Use this reference when you need a compact but retrieval-friendly structure for archived memory.

The goal is not to save everything. The goal is to save the right things in a form that is easy to recall later.

## Recommended layout

```text
memory/
  cold/
    index.md
    tags.json
    _template.md
    topic-a.md
    topic-b.md
```

## Design principles

- Prefer one topic per note.
- Prefer merged notes over many near-duplicates.
- Put the shortest useful summary near the top.
- Store reusable facts, lessons, and rationale instead of chat noise.
- Keep human-readable and machine-readable indexes in sync.

## What a good cold-memory note contains

Each note should answer these questions quickly:
- What is this?
- When should it be used?
- What is the key conclusion?
- How reliable is it?
- Where did it come from?

## Recommended note structure

```md
# Topic title

## TL;DR
- This note is about:
- Use it when:
- Key conclusion:

## Why this matters
1-3 lines.

## Memory type
- fact | experience | background

## Triggers
- phrase 1
- phrase 2

## Use this when
- scenario 1
- scenario 2

## Key facts
- fact 1
- fact 2

## Decisions / lessons
- What to do:
- What to avoid:
- Why:

## Confidence
- high | medium | low

## Last verified
- YYYY-MM-DD

## Related tags
- tag1
- tag2

## Details
Longer supporting context.

## Source context
- file, conversation, or date
```

## `index.md` schema

Use `index.md` as the short human-readable map.

### Recommended entry format

```md
- `topic-a.md` — one-line summary
  - type: fact | experience | background
  - tags: tag1, tag2
  - triggers: phrase 1, phrase 2
  - read when: scenario description
  - confidence: high | medium | low
  - updated: YYYY-MM-DD
```

### Example

```md
- `openclaw-lessons.md` — Reusable OpenClaw mistakes, fixes, and workflow decisions.
  - type: experience
  - tags: openclaw, workflow, troubleshooting
  - triggers: setup issue, pairing problem, repeated mistake
  - read when: debugging repeated setup trouble or designing recurring workflows
  - confidence: high
  - updated: 2026-03-18
```

## `tags.json` schema

Use `tags.json` as the structured retrieval layer.

### Recommended shape

```json
{
  "_meta": {
    "description": "Structured metadata for cold-memory retrieval",
    "version": 2,
    "updated": "YYYY-MM-DD"
  },
  "notes": [
    {
      "title": "Topic title",
      "path": "memory/cold/topic-a.md",
      "type": "fact",
      "summary": "One-line summary",
      "tags": ["tag1", "tag2"],
      "triggers": ["phrase 1", "phrase 2"],
      "scenarios": ["scenario 1", "scenario 2"],
      "confidence": "medium",
      "last_verified": "YYYY-MM-DD",
      "updated": "YYYY-MM-DD"
    }
  ]
}
```

## Field guidance

### `type`
Use one of:
- `fact` — stable information that can be directly reused
- `experience` — lessons, decisions, or troubleshooting knowledge
- `background` — broader context used mainly for synthesis

### `triggers`
Short words or phrases that should make the note worth checking.

Good triggers are:
- likely user wording
- problem labels
- topic aliases
- common shorthand

### `scenarios`
Describe the situations where reading the note materially improves the answer.

### `confidence`
Use:
- `high` — reliable and safe to reuse directly
- `medium` — probably right, but may be stale
- `low` — useful lead, but should be verified before relying on it

### `last_verified`
Use when the information itself was last confirmed.

### `updated`
Use when the note or metadata was last edited.

## Cooling guidance

When transforming recent notes into cold memory:
- compress raw notes into reusable knowledge
- preserve conclusions, not transcript clutter
- merge into an existing topic note when possible
- strengthen triggers and scenarios while updating the indexes

## Retrieval guidance

When recalling:
1. inspect `index.md` for likely candidates
2. use `tags.json` to sharpen matching by trigger and scenario
3. read the top summary before details
4. synthesize for the current task instead of dumping raw note text

## Maintenance guidance

Periodically:
- merge overlapping notes
- remove stale entries
- tighten weak summaries
- update confidence and verification dates
- keep `index.md` and `tags.json` aligned
