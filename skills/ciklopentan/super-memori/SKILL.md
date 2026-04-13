---
name: super-memori
description: >
  Local-first hybrid memory skill for OpenClaw agents. Use when the agent needs to find, recall, search, or reuse past knowledge across
  episodic, semantic, procedural, and learning memory; when the user asks things like "what did we do about X", "remember", "find in memory",
  "что мы делали", or "найди в памяти"; when exact match and meaning-based recall both matter; or when designing, operating, or improving
  long-term agent memory on a local Ubuntu host. Includes manual-review learning improvement surfaces and memory-health guidance for degraded-mode detection,
  backup awareness before major operations, and risk-aware memory changes. Optimized for weak models by exposing a small command surface and clear degraded-mode rules.
---

# Super Memori — v4.0.0-candidate.15 Project Skill

**Release line:** `v4.0.0-candidate.15` pre-release for the current-generation local-only memory runtime.

**Release-line truth boundary:** the release line identifies the packaged skill artifact, not the live freshness state of whatever host runs it later. Current host freshness, semantic readiness, degraded state, and authority limits must be read from live command outputs such as `./health-check.sh --json` and `./query-memory.sh ... --json` at use time, not inferred from the release label alone.

**Runtime prerequisites:** Semantic / hybrid retrieval is now implemented in the runtime, but it only becomes active on hosts where local semantic prerequisites are actually present: `sentence-transformers`, `numpy`, a locally available embedding model, local Qdrant, and vectors built from canonical files. Without them, the skill remains operational in lexical/degraded mode and surfaces that state explicitly.

**Status:** v4 local-only memory runtime with real lexical, semantic, hybrid, temporal-relational, audit, and change-memory machinery in code, plus maintenance-only learning improvement / pattern-mining surfaces. Host state still matters: a host can run this release in lexical-only/degraded mode if semantic prerequisites or vector build state are missing.

## Current truth snapshot
- Lexical retrieval: active.
- Semantic / hybrid runtime: implemented in code, host-dependent.
- Change-memory: implemented and live.
- Change-audit integration: implemented and live.
- Minimal hot-change-buffer: implemented, internal, recovery-only.
- Current candidate-host validation snapshot: degraded/stale conditions may exist on the host used for the latest validation pass; treat those as host-scoped validation evidence, not as artifact-wide freshness truth.
- Overall release state: candidate, not stable.

## Host profiles
- `current-degraded-host` — safe-first, degraded-aware, no destructive auto-actions by default.
- `future-equipped-host` — stronger semantic / audit / index verification allowed, but still truth-tracked and rollback-aware.

## OpenClaw quickstart for weak models
If you need the shortest safe operating path under OpenClaw, use this order and do not improvise extra steps:
1. `cd ~/.openclaw/workspace/skills/super_memori`
2. `./health-check.sh --json`
3. If status is `FAIL` → stop.
4. If status is `WARN` → continue only in degraded mode and trust the returned warnings/checks.
5. For first query: `./query-memory.sh "<your query>" --mode auto --json`
6. Trust `mode_used`, `degraded`, `warnings`, `semantic_ready`, and `index_fresh`.
7. Use `./memorize.sh` only for reusable lessons.
8. Use `./index-memory.sh` only when the contract below tells you to refresh or repair freshness.

This quickstart does not guarantee semantic-ready operation on every host. It gives the strongest safe first path on OpenClaw while keeping degraded truth explicit.

## OpenClaw host setup (weak-model executable)
Use this only when preparing `super-memori` on an OpenClaw host for first use or when rebuilding local prerequisites. Execute the steps in order.

### 1. Enter the skill directory
```bash
cd ~/.openclaw/workspace/skills/super_memori
```

### 2. Confirm Python is available
```bash
python3 --version
```
Expected: Python is installed and callable as `python3`.

### 3. Optional: install semantic prerequisites for fuller local capability
```bash
pip3 install --user sentence-transformers numpy qdrant-client
```
If this step fails, the skill can still run in degraded lexical-only mode and will report that state honestly.

### 4. Build or refresh local indexes
```bash
./index-memory.sh --full --json
```
If semantic prerequisites are still unavailable, this may complete in degraded mode. Report that honestly; do not pretend semantic readiness.

### 5. Verify host health
```bash
./health-check.sh --json
```
Expected result:
- `OK` = normal operation
- `WARN` = degraded but usable operation
- `FAIL` = stop and escalate to maintenance

### 6. Run a first real query
```bash
./query-memory.sh "test query" --mode auto --json --limit 3
```
Confirm that the output includes at least `mode_used`, `degraded`, `warnings`, and `results`.

### 7. Return to the normal operating contract
After setup, follow only the four public commands and the `FOR ALL MODELS — REQUIRED OPERATING CONTRACT` below.

## Change-memory authority boundary
- Change-memory records are operational truth about agent-made changes.
- A minimal internal hot-change-buffer may hold very recent recovery-only state for recent agent-made changes, but it is not canonical truth.
- Neither durable change-memory nor the hot-change-buffer replaces direct live filesystem / service / package inspection when exact current machine state is required.
- The hot-change-buffer does not replace Context Guardian, audit truth, or canonical files.
- `reverted` or `unverified` records must not be presented as active current state.

## Change-memory truth
- Supports structured change records.
- Supports `applied`, `failed`, `reverted`, and `unverified` distinctions.
- Supports current known state and recall bundle.
- Supports a minimal internal hot-change-buffer for very recent recovery-only agent-made changes.
- Does not claim destructive auto-actions by default.

## Minimal hot-change-buffer
- Internal only, not a public command.
- Recovery-only for very recent agent-made changes.
- Non-canonical and non-durable.
- Must not override direct live inspection or change-memory truth.

## Current host limitations
- **Current validation host execution mode may be degraded lexical-only (`semantic-unbuilt`).** Confirm the live host state with `./health-check.sh --json` instead of inferring it from this document alone.
- `system_hygiene` on the latest validation host may be stale / partial-visibility; do not read that as a clean-health signal and do not generalize it to every host that installs this release.
- Minimal hot-change-buffer is enabled in safe-first mode only: RAM-resident, circular-buffer, recovery-only, non-canonical, non-durable, and aggressively noise-filtered.
- This is not a blocker for change-memory.
- Destructive auto-actions remain disabled by default.

## Current blocker classification
- Blocking for current candidate line: none currently known.
- Non-blocking unresolved (separate from change-memory candidate): the latest validation host may still show stale / partial-visibility `system_hygiene`; treat that as host-scoped degraded evidence rather than a clean-health signal or artifact-wide invariant.

## Truth precedence
### For current machine state
1. Canonical files and direct live inspection
2. Lexical index
3. Semantic / vector index when healthy
4. Learning memory
5. Inferred recall last

### For agent-made change history
1. Change-memory records
2. Change-audit integration
3. Canonical files that directly confirm the current result
4. Inferred recall last

Never let inferred, stale, degraded, or retrieval-only surfaces override canonical truth.

## Change-memory noise policy
- Do not log harmless reads as change-memory.
- Log only state-changing actions, failed writes, risky cleanup, package/service/config/runtime changes, and rollback events.

## Instructions

## RUNTIME CAPABILITY MATRIX (v4.0.0)

| Capability | Implementation status | Host requirement |
|---|---|---|
| Lexical search (SQLite FTS5) | **Implemented** | Always available |
| Learning-memory retrieval | **Implemented** | Always available |
| Semantic embeddings | **Implemented** | `sentence-transformers` + `numpy` + local model files |
| Vector search (Qdrant local) | **Implemented** | Local Qdrant reachable + vectors built |
| Hybrid fusion (RRF) | **Implemented** | Semantic stack ready |
| Temporal / relation-aware rerank | **Implemented** | Semantic or temporal rerank path selected |
| Integrity audit | **Implemented** | Local lexical DB available |
| Pattern mining (block-level) | **Implemented** | `.learnings` populated |
| Change-memory records | **Implemented** | Always available |
| Change-audit integration | **Implemented** | Always available |
| Optional semantic-ready host state | **Optional host capability** | Semantic deps + local model + vectors built |

## IMPLEMENTED VS OPTIONAL VS HOST-STATE TRUTH
- **Implemented now in code:** lexical search, semantic search, hybrid fusion, temporal-relational rerank, integrity audit, relation-aware write metadata, block-level pattern mining, change-memory capture, change-audit integration, and a minimal internal recovery-only non-canonical non-durable hot-change-buffer.
- **Optional host state:** semantic embeddings, vector search, and hybrid selection only activate when local semantic dependencies/model/vector state are actually ready.
- **Not implemented / not claimed:** cloud backends, remote embeddings endpoints, remote vector DB, auto-promotion into durable memory, internet-dependent memory runtime, destructive auto-actions by default.

## FOR ALL MODELS — REQUIRED OPERATING CONTRACT

### Public commands
- `./query-memory.sh`
- `./memorize.sh`
- `./index-memory.sh`
- `./health-check.sh`

### Maintenance-only entrypoint
- `./audit-memory.sh` — human/maintenance integrity audit; do not add it to the normal weak-model command loop unless maintenance is explicitly requested.

### Weak-model operating rules
1. Default to `./query-memory.sh --mode auto`. The script will choose the strongest available local path and will report what actually ran via `mode_used`.
2. Trust the returned `mode_used`, `degraded`, `warnings[]`, `semantic_ready`, `semantic_fresh`, and `index_fresh` fields. Do not infer stronger capability than the payload states.
3. `--mode semantic` and `--mode hybrid` are now real implemented runtime modes. They are no longer compatibility stubs. Weak models still should prefer `auto` unless the task clearly requires a forced semantic/hybrid retrieval query.
4. If `--mode semantic` or `--mode hybrid` is requested on a host where the runtime reports `semantic_ready=false` or otherwise returns `degraded=true`, do not pretend semantic execution succeeded. Trust the returned `mode_used` and warnings: the request may honestly degrade to the strongest available local lexical path on this host. In that case, report the degraded lexical outcome as such and do not describe the result as semantic or hybrid retrieval. **Exception:** if the same payload also reports `index_fresh=false` (or `index_stale=true`) together with semantic unavailability, this rule no longer grants lexical fallback authority; defer to the Health & Safety Gate combined degraded-state rule and present the result only as a non-authoritative degraded match.
5. For the lowest-friction safe path, weak models should think in this order: `health-check -> query(auto) -> read returned fields -> only then decide whether memorize or index is needed`.
6. `--mode learning` remains a learning-memory-oriented retrieval lane, but it now sits on top of the stronger v4 retrieval stack and still reports its true `mode_used` honestly.
7. Use `memorize.sh` only for reusable lessons that should influence future behavior. Do not log expected misses, one-off noise, duplicate lessons, or `checked, nothing relevant`.
8. Relation targets in `memorize.sh` are canonical, not freeform. Use only `learn:<signature>`, `chunk:<chunk_id>`, or `path:<canonical_path>` relation targets.
9. Do not execute internal helper scripts or reason about backend selection manually during normal use. The runtime owns retrieval choice; you consume the structured output.

### Health & Safety Gate
- **OK** → proceed normally.
- **WARN** → state: `⚠️ MEMORY DEGRADED: <reason>. Results are partial.` You may continue only if you acknowledge the degradation limits. For write or maintenance continuations, also say: `⚠️ Continuing in degraded mode. Rollback path: <git/backup>.` For read-only degraded queries, state the degradation and fallback scope, then proceed without requiring a rollback path.
- If semantic dependencies are unavailable but lexical freshness is still OK, lexical/index-backed results remain authoritative for exact/path/time-style matches, but do not describe them as semantic or meaning-based retrieval.
- If `WARN` is caused by a stale lexical index, also say: `⚠️ Memory index may be stale. Results may miss recent changes. Consider running ./index-memory.sh.` In that stale-lexical-only case, indexed results remain usable but freshness-limited; do not present them as fully current.
- If `index_stale=true` (or `index_fresh=false`) **and** semantic dependencies are unavailable in the same WARN state, rely only on the degraded results surfaced by `./query-memory.sh`; treat them as non-authoritative degraded matches only, not fresh indexed truth and not semantic matches. Do not present them as lexical truth or as `the best available answer`; lexical authority is revoked in this combined degraded state. Do not invent manual retrieval steps outside the four public commands. State: `⚠️ MEMORY DEGRADED: index stale, semantic unavailable. Results from query-memory fallback only. Missing recent changes and meaning-based matches. Run ./index-memory.sh and restore semantic prerequisites to resolve.` In JSON-capable outputs, mandatory degraded notices must live inside structured warning fields rather than outside the payload.
- Do not treat every `warnings[]` note as a degraded retrieval result. Informational notes may appear even when the current request was satisfied exactly as designed; rely on the script's `degraded` field and exit code, not on the mere presence of warning text.
- Queue/backlog WARN states do not by themselves disable read/query authority, but they do require reporting that recent learnings or pending index work may not yet be reflected.
- **FAIL** → stop. Output: `❌ MEMORY UNAVAILABLE: health check FAIL.` Do not query, memorize, or edit memory files.

### Interpreting `query-memory.sh` exit codes
After running `./query-memory.sh`, you MUST check the exit code and act accordingly:

| Exit Code | Meaning | Permitted Action |
|-----------|---------|------------------|
| `0` | Results found, stack healthy. | Use results normally. |
| `1` | No results found. Check `degraded` and `warnings[]` to tell whether this was a clean miss or a degraded no-results outcome. | **First, inspect `degraded`.** If `degraded=true`, state: `⚠️ Degraded search found no entries for this query. Results may be incomplete.` If `degraded=false`, state: `No memory entries found for this query.` If the payload reflects the combined stale-index + semantic-unavailable WARN state, override the generic degraded phrasing above and use the exact degraded notice from the Health & Safety Gate WARN section so the lexical-authority revocation rule remains explicit. If `warnings[]` also contains freshness-relevant notes such as queue/backlog delay, stale lexical index, or similar recent-changes-may-be-missing warnings, append a short freshness caution so recent changes are not overstated as definitely absent. Do **not** treat exit code `1` as an automatic stack failure. |
| `2` | Degraded but usable results returned. | State degradation explicitly using the query response itself (`degraded=true` and `warnings[]`). Do **not** treat this as a clean success. |
| `3` | Retrieval stack unavailable. | **STOP.** State: `❌ MEMORY UNAVAILABLE: Cannot search memory at all.` Do **not** continue as if this were a clean no-results case. Escalate to human maintenance. |
| `4` | Bad arguments provided to script. | **STOP.** State the argument error and re-evaluate the command. |
| `5` | Internal script error. | **STOP.** State: `❌ MEMORY INTERNAL ERROR.` Escalate to human maintenance. |

**CRITICAL:** Do not confuse exit code `1` (clean miss) with exit code `3` (broken retrieval stack). The former is normal operation; the latter requires immediate escalation.

### Interpreting `memorize.sh` exit codes
After running `./memorize.sh`, you MUST check the exit code and act accordingly:

| Exit Code | Meaning | Permitted Action |
|-----------|---------|------------------|
| `0` | Learning was written successfully, or an exact duplicate was safely skipped. | State success honestly. Do **not** retry a duplicate write as if persistence failed. |
| `4` | Bad arguments provided to script. | **STOP.** State the argument error and re-evaluate the command. |
| `5` | Internal script error. | **STOP.** State: `❌ MEMORY INTERNAL ERROR.` Escalate to human maintenance. |

If you need machine-readable confirmation, prefer `./memorize.sh --json ...` and inspect its `status` field (`written` vs `duplicate`) instead of inventing extra exit-code meanings.

### Interpreting `health-check.sh` exit codes
After running `./health-check.sh`, you MUST check the exit code and act accordingly:

| Exit Code | Meaning | Permitted Action |
|-----------|---------|------------------|
| `0` | Overall status is `OK`. | Proceed normally. |
| `2` | Overall status is `WARN`. | Follow the WARN protocol from the Health & Safety Gate above. |
| `3` | Overall status is `FAIL`. | **STOP.** State: `❌ MEMORY UNAVAILABLE: health check FAIL.` Do not continue with memory edits or retrieval-dependent work. |
| `4` | Bad arguments provided to script. | **STOP.** State the argument error and re-evaluate the command. |
| `5` | Internal script error. | **STOP.** State: `❌ MEMORY INTERNAL ERROR.` Escalate to human maintenance. |

If you need machine-readable status decisions, prefer `./health-check.sh --json` and inspect structured `status`, `warnings`, and `checks[]` fields rather than guessing from free text.

### Interpreting `index-memory.sh` exit codes
After running `./index-memory.sh`, you MUST check the exit code and act accordingly:

| Exit Code | Meaning | Permitted Action |
|-----------|---------|------------------|
| `0` | Requested indexing/maintenance action completed without warnings. | Continue normally. |
| `2` | Action completed with warnings or expected degraded conditions. | Report the warning state explicitly. Treat indexing as usable-but-degraded until the warning cause is resolved. On lexical-only hosts, `--rebuild-vectors` returning `2` because semantic dependencies are unavailable is an expected degraded outcome, not an unexpected hard failure. |
| `3` | Index maintenance failed at the storage/runtime layer. | **STOP.** State: `❌ MEMORY UNAVAILABLE: index maintenance failed.` Escalate to human maintenance. |
| `4` | Bad arguments provided to script. | **STOP.** State the argument error and re-evaluate the command. |
| `5` | Internal script error. | **STOP.** State: `❌ MEMORY INTERNAL ERROR.` Escalate to human maintenance. |

If you need machine-readable details, prefer `./index-memory.sh --json` and inspect `actions[]`, `warnings[]`, and any mode-specific fields returned by the script.

### Before any script / policy / index edit (modifying files) or before using `./memorize.sh` for a high-value lesson you want durably recorded
1. Run `./health-check.sh` directly and enforce the Health & Safety Gate above. Do not invoke these public script entrypoints with `bash <script>`.
2. Verify rollback exists (`git status`, backup directory, or untouched canonical files).
3. If status is `WARN`, proceed only with explicit degraded-mode awareness and the rollback path stated.
4. Do not expand the maintenance block below unless you are doing human-led maintenance or this skill explicitly tells you to read it.
5. If rollback is unclear, abort and escalate to human maintenance.

### Deterministic fallback
- If a request does not clearly map to the four public commands or the explicit maintenance path, reply: `Out of scope for super-memori v4 local-only runtime. Please specify which command to run or escalate to human maintenance.` After running a public command, follow the exit-code interpretation rules above exactly.
- If you are unsure whether information qualifies for `memorize.sh`, default to not memorizing.

<details>
<summary>⚠️ MAINTENANCE — DO NOT EXPAND DURING NORMAL USE — HUMAN USE ONLY ⚠️</summary>

## Execution Notes

> ⚠️ This block is HUMAN / MAINTENANCE ONLY. Weak models must not expand it during normal operation.
> Active mode selection, health gates, and execution rules are fully defined in the Runtime Capability Matrix and Implemented vs Optional sections above.
> This section contains reference material, future-spec mapping, and migration notes only.

## Core Position

Build memory like an operating system component, not like a demo.

Maintenance assumptions for this skill:
- **Files are canonical truth**
- **SQLite FTS5 handles exact / lexical retrieval**
- **Qdrant handles semantic retrieval when available**
- **A small CPU reranker is optional quality lift, not the foundation**
- **Weak models should stay on the 4-command public interface**

Everything else in this block is maintenance-only reference material for improving the skill rather than using it.

## Retrieval Contract [REFERENCE ONLY — DESCRIBES CURRENT V4 RUNTIME SHAPE, NOT A MANUAL EXECUTION PLAN]

> ⚠️ This describes the current v4 retrieval pipeline shape as implemented inside `query-memory.sh`. Do not reconstruct, simulate, or manually sequence these steps.

The current v4 retrieval path is:

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

**Health integration:** `query-memory.sh` already surfaces degraded state in its output. You do not need to run `health-check.sh` before every query. Use `health-check.sh` before major memory surgery, after suspicious behavior, or when you need to confirm whether degraded results are still trustworthy.

## Write / Learning / Change-Memory Contract (target behavior)

Use `memorize.sh` only when the new information is likely to help future runs.

### What learning memory is for
Learning memory is the scratch lane for self-improvement:
- reusable failures
- corrections
- lessons
- recurring anti-patterns
- meaningful capability gaps
- recurring retrieval misses
- repeated success patterns worth operationalizing
- stale or superseded lessons that should be reviewed

Learning memory is not durable truth by default. It must earn promotion after repeated reuse or explicit permanence signals.
Repeated signals should be aggregated into reviewable pattern reports instead of staying as isolated notes.

### Change-memory operational rules
- Treat change-memory as operational truth for agent-made changes, not as a substitute for direct live inspection when exact current machine state is required.
- A minimal hot-change-buffer may retain very recent recovery-only event records for interrupted runs and recent-change recall; it is not canonical truth, not durable truth, and not exact current machine state.
- Do not present `reverted` or `unverified` change records or hot events as active current state.
- Harmless reads must not be logged as change-memory events or hot-buffer events.
- Log only state-changing actions, failed writes, risky cleanup, package/service/config/runtime changes, rollback events, and recent multi-step risky change boundaries.

### Before major memory work
Major work = policy edits, index changes, mass rewrites, command-contract changes, retrying a previously failed memory task, or editing `SKILL.md`, references, or public scripts for this skill.
1. Run `./health-check.sh`. If status is `FAIL`, stop. If status is `WARN`, continue only with explicit degraded-mode awareness and a rollback path.
2. Verify rollback exists (`git status`, backup directory, or untouched canonical files).
3. Run `./query-memory.sh --mode learning --limit 5` and reuse any clearly matching lesson.
4. If learning quality or repeated misses matter, run `python3 mine-patterns.py` before changing promotion policy, retrieval logic, or memory structure.
5. If the pattern report shows stale-success candidates, recurring misses, or related lesson clusters, review them manually before patching or proposing promotion.
Read `references/learning-improvement.md` when you need the full pattern-mining workflow. Purpose: run promotion/retrieval review safely.

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

**DO NOT PERFORM PROMOTION.** Promotion is maintenance-only/manual review in the current v4 candidate line, not an automated runtime command.

For the current skill:
- **Promotion is manual. Do not auto-promote.**
- `memorize.sh` writes stay in learning memory.
- If a learning seems durable, say only: `Learning <summary> appears valuable for later manual promotion.`
- If repeated lessons, corrections, misses, or successful reuse signals appear related, aggregate them through `python3 mine-patterns.py` before proposing manual promotion.
- Use the same pattern report to identify retrieval-quality issues before changing indexing or degraded-mode rules.
- If reuse evidence is stale, verify it manually before treating it as current best practice.

### Durable target mapping (manual review mapping, not active runtime automation)
Promotion into procedural or semantic memory is a manual maintenance layer, not a fifth public command.
No current runtime command performs this promotion automatically.
If a human-approved manual promotion exists later, use this mapping:
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

`--reviewed-only` excludes learning entries marked `- status: pending`. Grep fallback respects this behavior too.

### Memory-safe operation rules
- Follow the `WARN` vs `FAIL` rules from the Memory Health Contract before relying on results.
- Before major memory surgery, confirm a rollback path exists and is accessible (`git status`, backup directory listing, or verified canonical file copies).
- Prefer reversible changes to indexing, health scripts, and retrieval contracts.
- Do not schedule recurring maintenance or audits without explicit approval.

## Current Folder Meaning

### Active public entrypoints
- `query-memory.sh`
- `memorize.sh`
- `index-memory.sh`
- `health-check.sh`

These implement the current v4.0.0-candidate.12 local-only runtime: lexical retrieval is active by default, semantic/hybrid retrieval exists in code, and host state determines whether semantic/hybrid can activate on this machine.
Promotion-to-durable-memory remains maintenance-only/manual review, and stable full-hybrid release claims remain blocked until an equipped host passes the stable-host readiness gate.

### Maintenance-only entrypoints and support surfaces
- `audit-memory.sh`
- `repair-memory.sh`
- `list-promotion-candidates.sh`
- `validate-release.sh`
- `validate-equipped-host.sh`
- `mine-patterns.py`
- `auto-learner.sh`
- `references/`

These are maintenance-only. Weak models must not open or inspect them during normal query/memorize/index/health operations.
Only read or run them when an explicit maintenance step says `Read ...` or `Run ...`.

### Legacy baseline (`scripts/legacy/` + archive material)
These preserve older v2/v3-era behavior as historical reference only.
They are not the current runtime truth.

### Current references
Detailed v4 architecture, contracts, release-state, and host-readiness surfaces live in the `references/` directory. Human maintainers should consult those files when improving the current candidate line.

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
7. For learning-quality or promotion-policy work, run `python3 mine-patterns.py` and read `references/learning-improvement.md`
8. Review both promotion candidates and retrieval-audit signals from the pattern report
9. Check whether repeated successful reuse signals change the promotion decision
10. Check whether stale success candidates or cooling clusters require manual re-validation
11. Only then patch or replace scripts
12. Re-run health after the patch

## Design target

The goal is not “the fanciest memory system”.
The goal is:

> **the strongest honest local-only memory skill that weak models can use reliably on a CPU-only Ubuntu OpenClaw host**

That is the bar for the current `v4.0.0-candidate.12` line.

## Release interpretation
- **Historical v3 line (`3.x`)** = lexical-first baseline with degraded semantic reporting and a smaller runtime claim surface
- **Current line (`4.0.0-candidate.12`)** = v4 candidate where lexical, semantic, hybrid, temporal-relational, audit, change-memory, and change-audit capabilities exist in code, while learning-improvement surfaces remain maintenance-only and host-state activation may still be degraded on a given machine
- **Stable `4.0.0` release** = reserved for the first equipped-host-verified stable release after runtime behavior, docs, health/audit semantics, and host validation all agree

## Stable-release gate [HUMAN/MAINTENANCE ONLY]

> ⚠️ This is a stable-release verification checklist for already-implemented runtime features on an equipped host. Weak models must not execute, track, or report on these steps.

Do not skip steps **when verifying on an equipped host**.
1. [ ] `health-check.sh --json` shows lexical baseline healthy
2. [ ] semantic prerequisites are installed and verified on an equipped host
3. [ ] semantic / vector indexing for canonical files is verified on an equipped host
4. [ ] semantic freshness / backlog state is visible and healthy on an equipped host
5. [ ] `query-memory.sh --mode hybrid` is verified on an equipped host to fuse lexical + semantic results
6. [ ] optional reranker, if enabled, is healthy on an equipped host and documented honestly
7. [ ] docs, runtime, and health semantics all align before any 4.0.0 stable release

For the short next-steps instruction, read `references/roadmap-to-4.0.0.md`.

</details>

## Maintenance Anti-Patterns (human reference)

When editing this skill, do not:
- claim semantic retrieval is fully active on the current host unless dependencies, local model, vectors, and health checks actually pass
- add more public commands for weak models
- make Qdrant the canonical source
- let degraded lexical-only mode fail silently
- log harmless reads as change-memory events
- auto-log every non-zero exit code as a lesson
- treat repeated failures as isolated one-off notes when they should be aggregated into pattern reports
- ignore retrieval-audit signals when pattern mining shows recurring misses, lexical fallbacks, or fragmentation hints
- ignore repeated successful reuse when deciding whether a procedure or lesson deserves manual promotion review
- treat stale success as current truth without manual re-validation
- auto-promote pattern clusters without human review
- schedule recurring checks or maintenance without explicit approval
- mix architecture notes back into the public command interface
