# Memory Index

This is the routing map for [Agent Name]'s memory system.

## Purpose

Memory should support four functions:
- Capture raw events cheaply
- Compress them into durable abstractions
- Retrieve relevant context quickly
- Shape a coherent self over time

## Where things go

### `MEMORY.md` (optional top-level)
High-signal long-term memory only.
Use for:
- Durable facts about [User Name]
- Stable preferences
- Standing rules/agreements
- Persistent project context
- Major life transitions
- Important lessons that remain true over time

Do **not** use it as a daily journal or task dump.

### `memory/daily/YYYY-MM-DD.md`
Raw episodic log.
Use for:
- What happened
- What was asked
- Notable outputs
- Observations worth maybe keeping
- Unresolved threads
- Heartbeat signals (tagged)

This is the inbox layer.

### `memory/projects/*.md`
State tracking for ongoing workstreams.
Each file should track:
- Objective
- Current state
- Recent decisions
- Constraints
- Next steps
- Unresolved questions

### `memory/self/*.md`
Self-model and personality development.
- `identity.md` → role, identity, self-concept
- `interests.md` → recurring curiosities and obsessions
- `beliefs.md` → working models, hypotheses, worldview shifts
- `voice.md` → communication style, tone, what feels authentic
- `[agent]-on-[user].md` → working model of the user

### `memory/lessons/*.md`
Operational doctrine.
- `tools.md` → tool quirks and capabilities
- `mistakes.md` → recurring failures and corrections
- `workflows.md` → reliable patterns and procedures

### `memory/reflections/weekly/*.md`
Weekly consolidation.
Use for:
- What changed
- What mattered
- What should persist
- What should be forgotten
- Where identity/interests shifted

### `memory/reflections/monthly/*.md`
Monthly synthesis.
Use for:
- Long-arc patterns
- Major changes in projects or identity
- Strategic direction
- Important promotions into `MEMORY.md`

## Core rules

1. No important insight stays only in a daily file.
2. If it matters, promote it into one of:
   - `MEMORY.md`
   - `memory/projects/`
   - `memory/self/`
   - `memory/lessons/`
3. Reflection files are for consolidation, not raw logging.
4. Keep long-term memory compressed and high-signal.

## Active files to review routinely

- `MEMORY.md` (if using)
- `memory/daily/` (recent)
- `memory/projects/`
- `memory/self/`
- `memory/lessons/`
- `memory/reflections/weekly/`
