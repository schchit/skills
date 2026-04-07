---
name: super-memori
description: >
  Local-first hybrid memory skill for OpenClaw agents. Use when the agent needs to find, recall, search, or reuse past knowledge across
  episodic, semantic, procedural, and learning memory; when the user asks things like "what did we do about X", "remember", "find in memory",
  "что мы делали", or "найди в памяти"; when exact match and meaning-based recall both matter; or when designing, operating, or improving
  long-term agent memory on a local Ubuntu host. Includes a built-in self-improvement loop and memory-health guidance for degraded-mode detection,
  backup awareness before major operations, and risk-aware memory changes. Optimized for weak models by exposing a small command surface and clear degraded-mode rules.
---

# Super Memori — v3.2.4 Project Skill

**Status:** v3 baseline with health-reported semantic degradation when Python semantic dependencies are missing. This folder provides a real v3 baseline command surface, keeps older behavior as legacy reference, and documents the exact path to later full-hybrid implementation without pretending semantic layers are always active on every host.

## Execution

## FOR WEAK MODELS — READ THIS FIRST

You have exactly 4 active commands:
- `query-memory.sh [--mode auto|exact|hybrid|learning|recent]` — find past knowledge
- `memorize.sh` — save a useful lesson
- `index-memory.sh` — refresh indexes and process backlog
- `health-check.sh` — verify whether memory is healthy or degraded

Rules:
1. Use only these 4 public commands with their documented flags.
2. Ignore other executable files in the folder unless this skill explicitly sends you to them. Files such as `auto-learner.sh`, `index-daily.sh`, `embed-file.py`, `embed-raw-file.py`, `vector_fallback.py`, and helper Python modules are not part of the weak-model public interface.
3. `This skill explicitly sends you to them` means one of these only: (a) this SKILL.md says `Run <exact file>` in a current maintenance step, (b) a checklist step in this SKILL.md names the exact file, or (c) the user explicitly asks to run that exact file. File mentions in references, examples, architecture notes, or directory listings do not count.
4. When this skill says to read a reference file, that means documentation lookup only. File names mentioned inside documentation are not execution instructions unless a step explicitly says `Run <file>`.
5. Prefer `query-memory.sh --mode auto` unless the mode-selection rules below clearly map the request to another public mode.
6. If health or query output says degraded, surface that fact instead of pretending results are complete.
7. Use `memorize.sh` only for lessons that can change future behavior.

## Memory Health Contract

`health-check.sh` is the gate for trustworthy memory work.

Expected status values:
- `OK` — lexical baseline is healthy
- `WARN` — degraded but still partially usable
- `FAIL` — critical memory layer is unhealthy

**Degraded-mode honesty:**
- If `health-check.sh` returns `WARN`, say memory is degraded before relying on results.
- If query output says degraded, treat results as partial rather than complete.
- Do not imply semantic completeness while degraded.
- Use this warning format: `⚠️ MEMORY DEGRADED: <reason from health-check or query output>. Results are partial.`
- If you continue after `WARN`, state explicitly: `⚠️ Continuing in degraded mode. Risk of incomplete results. Rollback path: <git/backup location>.`

**Before major memory surgery** (policy edits, index changes, mass rewrites, command-contract changes):
1. Run `health-check.sh`.
2. If status is `FAIL`, stop memory-dependent changes and fix health first.
3. If status is `WARN`, continue only with explicit degraded-mode awareness and a rollback path.
4. Verify that canonical files or git history provide rollback before broad edits.

## Core Position

Build memory like an operating system component, not like a demo.

For this skill, the correct design is:
- **Files are canonical truth**
- **SQLite FTS5 handles exact / lexical retrieval**
- **Qdrant handles semantic retrieval**
- **A small CPU reranker is optional quality lift, not the foundation**
- **Weak models only see a tiny public interface**

## Public Command Surface (target v3)

Weak models should only need these four entrypoints:

1. `query-memory.sh` — retrieve memory
2. `memorize.sh` — write a useful learning / correction / lesson
3. `index-memory.sh` — maintain indexes
4. `health-check.sh` — verify memory health

Everything else is internal implementation detail, legacy material, or helper code. Do not call those files directly unless this skill explicitly instructs you to do so for a maintenance task.

## Canonical Rules

1. **Do not treat vector indexes as source of truth.** Markdown/files remain canonical.
2. **Do not require the model to choose backends manually.** `query-memory.sh` must decide auto/exact/semantic/hybrid internally.
3. **Do not hide degraded mode.** If semantic is down and lexical still works, say so explicitly.
4. **Do not memorize every failure.** Only capture failures that teach future behavior.
5. **Treat learning memory as scratch-first, not canonical truth.** A learning entry is provisional until promoted into durable memory.
6. **Before major memory work, review recent learning memory.** Reuse past lessons before making the same mistake again.
7. **Do not mutate memory policy blindly.** For major changes, verify health first and preserve rollback paths.
8. **Do not promise magic.** If a layer is stale, missing, or partial, surface that clearly.

## Retrieval Contract (target behavior)

The future v3 retrieval path is:

```text
query
  → filters (type, time, tags, namespace)
  → lexical retrieval (SQLite FTS5)
  → semantic retrieval (Qdrant, when available / needed)
  → fusion
  → optional rerank
  → deduplicate / diversify
  → results + warnings + freshness state
```

### Default mode
Use `query-memory.sh --mode auto` by default.

**Health integration:** `query-memory.sh` already surfaces degraded state in its output. You do not need to run `health-check.sh` before every query. Use `health-check.sh` before major memory surgery, after suspicious behavior, or when you need to confirm whether degraded results are still trustworthy.

### Mode selection rules (priority order, top to bottom)
1. **Exact match signals** → `query-memory.sh --mode exact`
   - literal paths, config keys, service names, quoted strings, error messages, code identifiers
2. **Recency signals** → `query-memory.sh --mode recent`
   - `recent`, `today`, `yesterday`, `last hour`, `last day`, `last week`
3. **Learning signals** → `query-memory.sh --mode learning`
   - `lesson`, `mistake`, `failure`, `what did we learn`
4. **Everything else** → `query-memory.sh --mode auto`
   - similar past issues, related history, meaning-based recall, open-ended memory questions

**Tie-breaker rule:** if a query matches more than one signal, use the highest-priority matching mode above.

**Do not call `--mode hybrid` directly unless you are debugging the retrieval pipeline as a maintenance task**

## Write / Learning Contract (target behavior)

Use `memorize.sh` only when the new information is likely to help future runs.

### What learning memory is for
Learning memory is the scratch lane for self-improvement:
- reusable failures
- corrections
- lessons
- recurring anti-patterns
- meaningful capability gaps

Learning memory is not durable truth by default. It must earn promotion after repeated reuse or explicit permanence signals.

### Before major memory work
Treat these as major work:
- revising memory policy or retrieval behavior
- changing indexing, health, or command contracts
- retrying a memory task that already failed more than once
- editing SKILL.md, references, or public scripts for this skill

Before major work:
0. Run `health-check.sh` and verify a rollback path exists for the files being changed.
1. Run `query-memory.sh --mode learning --limit 5`.
2. Reuse any clearly matching lesson.
3. If no learning results are found, continue normally.

### Good candidates
- an unexpected failure with a reusable lesson
- a user correction that changes future behavior
- a better repeatable procedure
- a recurring anti-pattern
- a meaningful knowledge gap

### Bad candidates
- expected no-match results
- one-off noise
- weak guesses
- duplicate lessons already recorded
- `checked, nothing relevant`

### Promotion to durable memory

**DO NOT PERFORM PROMOTION.** Promotion is a future/manual process, not an automated command in the current v3 baseline.

For the current skill:
- `memorize.sh` writes stay in learning memory
- weak models must not invent a promotion command
- weak models must not rewrite durable memory automatically as part of normal `memorize.sh` flow
- if a learning seems valuable enough to keep permanently, say only: `Learning <summary> appears valuable for later manual promotion.`
- stop there

### Durable target mapping (future / manual promotion)
Promotion into procedural or semantic memory is a future/manual layer, not a fifth public command.
When a human-approved future/manual promotion happens, use this mapping:
- repeatable commands / debugging steps → procedural memory
- anti-patterns / post-mortems → procedural lessons memory
- durable facts / preferences / infrastructure facts → semantic memory
- decisions with rationale → semantic decisions memory

### Anti-patterns
- Do not auto-log every non-zero exit code.
- Do not duplicate the same lesson in multiple learning records.
- Do not promote one-off context into durable memory.
- Do not attempt to promote learnings without human action.
- Do not invent commands for promotion.
- Do not log that nothing relevant was found.

## Health / Freshness Contract

Health is not only about indexes. Health also means the agent can tell whether learning-memory is being used honestly instead of as a dumping ground, whether degraded mode is safe to continue in, and whether the host-side conditions still support trustworthy memory work.

`health-check.sh` currently reports at least:
- canonical files readable
- lexical index status
- semantic index status
- queue backlog
- last successful index update / freshness state
- degraded state

Advanced checks such as duplicate / orphan risk belong to the fuller semantic layer and should not be claimed until runtime support exists.

`query-memory.sh` currently reports at least:
- `mode_requested`
- `mode_used`
- `degraded`
- `warnings[]`
- `index_fresh`
- `results[]`

### Memory-safe operation rules
- Follow the `WARN` vs `FAIL` rules from the Memory Health Contract before relying on results.
- Before major memory surgery, confirm a rollback path exists and is accessible (`git status`, backup directory listing, or verified canonical file copies).
- Prefer reversible changes to indexing, health scripts, and retrieval contracts.
- Do not schedule recurring maintenance or audits without explicit approval.

## Learning-Memory Position

Inside `super_memori`, learning-memory is a controlled scratch layer:
- `memorize.sh` writes useful learnings
- `query-memory.sh --mode learning` retrieves them
- repeated or critical learnings may later promote into procedural or semantic memory through a future/manual promotion layer
- until promotion happens, learning-memory remains provisional rather than canonical

This keeps self-improvement inside the memory system without turning every temporary lesson into permanent truth.

## Current Folder Meaning

This skill now has two layers:

### 1. Current v3 baseline commands (lexical-first runtime implemented now in skill root)
These are the active public entrypoints:
- `query-memory.sh`
- `memorize.sh`
- `index-memory.sh`
- `health-check.sh`

They implement the lexical-first v3 public surface with health reporting, queue/freshness state, and honest degraded-mode handling for the semantic layer.
Semantic promotion-to-durable-memory and full-hybrid guarantees remain design/runtime work, not a claim about the current host.

### 2. Legacy baseline (`scripts/legacy/` + older helper files)
These preserve the older v2-era behavior and semantic experiments as migration/reference material.

### 3. v3 design references
These references define the later 3.1.x full-hybrid-ready spec and the path toward 4.0.0. Read them before major changes:
- `references/architecture.md` — target architecture
- `references/command-contracts.md` — CLI contracts and exit codes
- `references/retrieval-pipeline.md` — ranking / fusion / degraded behavior
- `references/health-model.md` — what health means for local memory
- `references/weak-model-guidance.md` — how to keep the interface safe for weaker models
- `references/migration-plan.md` — how to move from legacy v2 scripts to v3
- `references/full-hybrid-mode.md` — what must be true before claiming full hybrid mode
- `references/implementation-order.md` — exact weak-model-safe order for finishing hybrid mode later
- `references/release-status.md` — what version labels mean
- `references/roadmap-to-4.0.0.md` — short instruction for completing the later runtime hybrid release

## How to reach full hybrid later

Do not skip steps.
1. [ ] `health-check.sh --json` shows lexical baseline healthy
2. [ ] semantic prerequisites are installed and verified
3. [ ] semantic indexing path is implemented for canonical files
4. [ ] semantic freshness / backlog state is visible
5. [ ] `query-memory.sh --mode hybrid` fuses lexical + semantic results
6. [ ] reranker is added last, as an optional quality layer
7. [ ] health, retrieval, and docs all agree before any 4.0.0 release

## Backup / Exposure / Risk Notes

- Files remain the canonical recovery path if indexes degrade or semantic dependencies disappear.
- If the host is remote, exposed, or lightly backed up, prefer plan-first changes over direct edits to memory scripts.
- If backups or snapshots are unknown, assume caution and avoid irreversible cleanup.
- Health guidance for this skill covers memory reliability, not full host hardening. Use `healthcheck` for broader host security decisions.

## How to use this skill today

### If you need current memory behavior
Use the active root commands:
- `query-memory.sh`
- `memorize.sh`
- `index-memory.sh`
- `health-check.sh`

### If you are improving the skill
Do this order:
1. Run `health-check.sh`
2. Review recent learning-memory if the task is major or previously failed
3. Confirm whether rollback exists (git, backup, untouched canonical files)
4. Read `references/architecture.md`
5. Read `references/command-contracts.md`
6. Read `references/migration-plan.md`
7. Only then patch or replace scripts
8. Re-run health after the patch

## What not to do

- Do not claim semantic retrieval is fully active unless its dependencies and health checks actually pass
- Do not add more public commands for weak models
- Do not make Qdrant the canonical source
- Do not let degraded lexical-only mode fail silently
- Do not auto-log every non-zero exit code as a lesson
- Do not schedule recurring checks or maintenance without explicit approval
- Do not mix architecture notes back into the public command interface

## Design target

The goal is not “the fanciest memory system”.
The goal is:

> **the strongest local memory skill that weak models can use reliably on a CPU-only Ubuntu OpenClaw host**

That is the bar for v3.

## Release interpretation
- **3.0.x** = working lexical-first v3 baseline with monitored semantic degradation
- **3.1.x** = full-hybrid-ready skill spec, prepared so weaker models can finish the semantic stack later in a controlled order; this is a documentation/spec maturity state, not runtime activation
- **4.0.0** = only when runtime-verified full hybrid mode is actually implemented and tested

For the short next-steps instruction, read `references/roadmap-to-4.0.0.md`.
