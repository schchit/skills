# Heartbeat Cooling Playbook

Use this reference when heartbeat is maintaining cold memory.

The job is not to scan everything. The job is to do a light pass over recent notes and turn only the durable parts into reusable archived memory.

## Objective

During heartbeat, perform **cooling**:
- inspect recent daily notes
- find low-frequency, high-value items
- compress them into reusable cold-memory notes
- update the indexes
- stay quiet unless the result is actually worth surfacing

## Lightweight workflow

1. Read `memory/heartbeat-state.json`.
2. Check whether a cold-memory pass happened recently.
3. Read only the most recent 1-3 daily notes.
4. Identify candidate items worth cooling.
5. Decide whether each item should be ignored, merged, or archived as a new note.
6. Update the target cold note.
7. Update `memory/cold/index.md` and `memory/cold/tags.json`.
8. Update `memory/heartbeat-state.json`.
9. Notify the user only if something clearly valuable was archived or newly relevant.

## Decision rule: ignore, merge, or create

### Ignore
Do nothing if the item is:
- one-off chatter
- temporary status
- emotionally noisy but not reusable
- obvious enough that it does not need preserving
- sensitive material that should never be archived

### Merge into an existing note
Merge when:
- the topic already exists in `memory/cold/`
- the new item strengthens or updates an existing lesson
- the note can become sharper without becoming bloated

### Create a new cold-memory note
Create one only if:
- the topic is distinct
- the content is likely useful after 30 days
- it carries a reusable fact, lesson, or background summary

## What to extract from a daily note

Do not copy daily notes verbatim. Extract:
- stable facts
- decision rationale
- lessons learned
- reusable workflow steps
- warnings and pitfalls
- triggers that future-you is likely to search by

## Compression rule

A good cooled note should be:
- shorter than the source notes
- more reusable than the source notes
- easier to scan than the source notes
- clearer about when to recall it

If the cold note is not better than the raw daily note, the cooling failed.

## Good candidate examples

### Example: troubleshooting lesson
Daily note says:
- spent 20 minutes because a skill path was guessed from memory and was wrong

Cooled note should say:
- do not guess installed skill paths; verify the actual directory before using a workspace skill

### Example: stable reference
Daily note says:
- found the correct Hong Kong Chow Tai Fook gold price page

Cooled note should say:
- remembered stable link for Hong Kong Chow Tai Fook gold price lookup
- include trigger phrases and confidence

## Index update rules

After creating or updating a cold note:
- ensure `index.md` has a concise human-readable entry
- ensure `tags.json` contains matching structured metadata
- align summary, type, tags, triggers, scenarios, confidence, and dates

## When heartbeat should notify the user

Notify only if at least one is true:
- a clearly valuable memory was successfully archived
- the archived item is strongly relevant to the current active topic
- the archived lesson will likely save repeated future work

Otherwise reply with the quiet heartbeat acknowledgment.

## Anti-patterns

Avoid these mistakes:
- scanning the whole cold archive every heartbeat
- dumping raw archive contents into chat
- archiving everything that looks mildly useful
- creating duplicate notes for the same topic
- storing secrets or sensitive vulnerability details
- confusing recent warm memory with durable cold memory

## Suggested state tracking

In `memory/heartbeat-state.json`, track lightweight timestamps such as:
- `coldMemoryScan`
- `coldMemoryArchive`
- `coldMemoryIndexRefresh`

Use these to avoid repeated work inside short time windows.
