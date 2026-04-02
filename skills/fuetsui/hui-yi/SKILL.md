---
name: hui-yi
description: Manage cold memory for long-term recall: archive low-frequency but high-value information into structured files, retrieve only the most relevant archived context when it will materially improve an answer, and maintain a lightweight recall system during heartbeat or memory maintenance work. Use when the task involves remembering, recalling prior notes, curating long-term knowledge, designing a memory workflow, moving inactive context out of chat, or deciding what should be preserved for future reuse.
---

# Hui Yi

Use this skill to build and operate a **cold-memory system**: information worth keeping, but not worth keeping in active context all the time.

The point is not to store more. The point is to **remember better**.

## Core objective

Optimize for these outcomes:
- archive useful knowledge with low maintenance cost
- recall the right old context at the right time
- avoid loading irrelevant history
- keep active context clean

Cold memory should behave like an external memory layer, not like a junk drawer.

## Memory layers

Work across three layers:

1. **Active context**
   - current chat, current task, immediate working notes
   - keep minimal

2. **Warm memory**
   - recent daily files, current project notes, near-term context
   - check this first for anything recent or ongoing

3. **Cold memory**
   - older but still valuable knowledge
   - use for stable facts, reusable lessons, historical decisions, durable background

Prefer files over “mental notes”. If something should survive reset, write it down.

## What belongs in cold memory

Cold memory is for **low-frequency, high-value** information.

### Good candidates

Archive material like:
- old project decisions and the reasons behind them
- troubleshooting conclusions that may be reused
- workflows that worked and should be repeated later
- durable user preferences too detailed for a short profile
- long research summaries likely to matter again
- background context that improves future answers but does not belong in active chat

### Do not archive

Never store:
- secrets, tokens, API keys, passwords, auth material
- sensitive exploit details or vulnerability instructions
- one-off status chatter
- low-value conversation fragments
- speculative claims with no clear future use

## Memory object types

When archiving, classify the note first. Use the type to decide format and retrieval expectations.

### 1. Fact memory
Short, stable, directly reusable information.

Examples:
- a path
- a reference URL
- a standing preference
- a naming convention

### 2. Experience memory
Lessons learned from doing something.

Examples:
- a troubleshooting result
- a mistake to avoid
- a workflow pattern that worked
- a decision rationale

This is often the most valuable type.

### 3. Background memory
Larger context that helps future synthesis.

Examples:
- project history
- topic research summary
- long-term context for a person, tool, or system

## Archiving threshold

Do **not** archive by default. Archive only if at least one of these is true:
- it is likely to still matter after 30 days
- it contains a reusable lesson or workflow
- it would noticeably improve a future answer or decision
- the user explicitly asks to remember or preserve it

If none apply, keep it out of cold memory.

## Storage layout

Prefer this structure:

- `memory/cold/` — archived notes
- `memory/cold/index.md` — human-readable index
- `memory/cold/tags.json` — structured retrieval metadata
- `memory/cold/_template.md` — starter note template
- `memory/heartbeat-state.json` — maintenance timestamps

Keep one note per topic where possible. Favor merging over creating lots of near-duplicate files.

## Retrieval principle

Recall archived knowledge only when it will **materially improve** the current answer.

Do not retrieve old notes just because they exist.

Ask:
- Would prior context improve correctness?
- Would it improve continuity?
- Would it save the user from re-explaining something important?
- Would it help avoid a repeated mistake?

If not, skip recall.

## Recall workflow

Follow this sequence:

1. Check the current conversation first.
2. Check warm memory next if the topic may be recent.
3. Decide whether archived knowledge would materially help.
4. If yes, inspect `memory/cold/index.md` and then `memory/cold/tags.json` for likely matches.
5. Read only the most relevant notes.
6. Prefer summary sections before detailed sections.
7. Synthesize for the present task.
8. If recall exposed stale or weak structure, update the relevant note or index.

Default behavior: answer the current need first. Surface archived context only as support.

## Retrieval heuristics

Recall is more likely useful when:
- the user says “remember”, “回忆一下”, “之前”, “以前那次”, “你有记录吗”
- the task depends on historical decisions or earlier troubleshooting
- a note’s triggers or scenarios clearly match the current request
- the answer quality would noticeably improve with prior context

Recall is less likely useful when:
- the question is simple and present-focused
- old context would mostly distract
- the archive is broad but the user request is narrow

## Index-first retrieval

Use two levels of indexing:

### `memory/cold/index.md`
Human-readable, short, scannable.

Each entry should include:
- file path or note name
- one-line summary
- type
- tags
- triggers
- read when
- confidence
- updated date

### `memory/cold/tags.json`
Machine-friendly structured metadata.

Use it to store fields like:
- `title`
- `path`
- `type`
- `summary`
- `tags`
- `triggers`
- `scenarios`
- `confidence`
- `last_verified`
- `updated`

Prefer `index.md` for human inspection and `tags.json` for targeted retrieval.

## Note design

Each cold-memory note should be **layered** so recall is cheap.

Preferred structure:

```md
# Topic title

## TL;DR
- what this note is
- when it matters
- key conclusion

## Why this matters
1-3 lines.

## Memory type
- fact | experience | background

## Triggers
- words or phrases that should make this note worth checking

## Use this when
- scenarios where this note materially helps

## Key facts
- stable facts

## Decisions / lessons
- what to do
- what to avoid
- why

## Confidence
- high | medium | low

## Last verified
- YYYY-MM-DD

## Related tags
- tag1
- tag2

## Details
Longer context if needed.
```

Important rules:
- Put the shortest useful summary near the top.
- Write for retrieval, not for narrative beauty.
- Preserve lessons and rationale, not raw transcript noise.
- Update old notes instead of creating duplicates when the topic is the same.

## Cooling workflow

During maintenance, “cool” recent notes into reusable memory rather than copying them verbatim.

### Cooling process

1. Review recent daily notes.
2. Identify low-frequency, high-value content.
3. Remove noise and one-off context.
4. Extract stable facts, lessons, and decision rationale.
5. Merge into an existing cold note if the topic already exists.
6. Otherwise create a new focused note from the template.
7. Update `index.md` and `tags.json`.

The cold note should be **more reusable and more compressed** than the original daily note.

## Heartbeat integration

Heartbeat is for light maintenance, not constant recall.

Appropriate heartbeat actions:
- check the last 1-3 daily notes for content worth cooling
- update a cold note that now has a clearer summary
- refresh index metadata if notes changed
- surface archived knowledge only if it is strongly relevant to the current topic

Avoid:
- reading the whole archive every time
- re-surfacing old notes without a clear trigger
- spamming the user with memory trivia

## Maintenance and pruning

Cold memory quality decays if nothing is cleaned up.

Periodically:
- merge duplicate notes
- remove stale or superseded entries
- strengthen summaries and triggers
- update confidence or verification dates
- simplify the index if it becomes cluttered

Favor a smaller, sharper archive over a large fuzzy one.

## Output behavior after recall

After recalling archived memory:
1. answer the current question first
2. mention the recalled context only if it adds value
3. summarize the relevant point instead of dumping the note
4. show raw archive contents only if the user asks

Cold memory exists to improve the answer, not to show off that memory exists.

## References

Read these only when needed:
- `references/cold-memory-schema.md` — default schema, note structure, index design, and metadata model
- `references/heartbeat-cooling-playbook.md` — practical heartbeat workflow for cooling recent notes into cold memory

## References

Read these only when needed:
- `references/cold-memory-schema.md` — note/index/metadata schema for designing or refactoring the archive structure
- `references/heartbeat-cooling-playbook.md` — practical heartbeat workflow for cooling recent notes into cold memory

## Working style

Be conservative about recall and selective about storage.

That means:
- archive less, but archive better
- prioritize reusable experience over raw logs
- retrieve by trigger and scenario, not by guessing filenames
- prefer summaries before full-note reads
- keep live context clean
