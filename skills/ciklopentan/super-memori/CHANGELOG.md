# Changelog

## 4.0.0-candidate.15 - 2026-04-13
- Fixed a real weak-model operator-risk seam in rule #4: forced semantic/hybrid fallback wording now explicitly yields to the combined degraded-state lexical-authority revocation rule when `index_fresh=false` (or `index_stale=true`) and semantic is unavailable together.
- Advanced the candidate line to `4.0.0-candidate.15` after this narrow contract fix.
- No public command expansion, no stable-release claim, no policy-gate overfitting.

## 4.0.0-candidate.13 - 2026-04-13
- Tightened release-truth wording so the packaged release line is explicitly separated from live host freshness, semantic readiness, and degraded authority state at use time.
- Reframed current-host degraded/stale wording as validation-host evidence instead of artifact-wide truth, reducing operator risk that a published version label is misread as a claim about every installed host.
- Tightened `validate-release.sh` so non-FAIL WARN publication is no longer an undifferentiated pass: release gating now explicitly blocks critical WARN surfaces such as unreadable canonical files or unavailable lexical FTS even if overall health is not `FAIL`.
- Synced `_meta.json` publish policy to the stronger host-scoped WARN interpretation and advanced the release line to `4.0.0-candidate.13`.
- No public command expansion, no stable-release claim, no forced freshness-window policy invented without stronger evidence.

## 4.0.0-candidate.12 - 2026-04-12
- Ran a fresh full 3-cycle / 18-round Dual Thinking rerun from the published `4.0.0-candidate.11` baseline using alternating AI Orchestrator and Qwen Orchestrator, including honest recovery handling for polluted Qwen sessions that repeated already-landed findings.
- Accepted three real micro-fixes from the new rerun:
  - in the combined stale-index + semantic-unavailable WARN state, degraded matches are now explicitly non-authoritative and lexical authority is revoked
  - removed the misleading `zero-findings` token from current-host `system_hygiene` wording so weak models cannot misread stale partial visibility as clean health
  - tightened the `query-memory.sh` exit code `1` no-results row so the combined stale-index + semantic-unavailable WARN state must reuse the exact degraded notice from the Health & Safety Gate rather than a weaker generic template
- Remaining Qwen suggestions about extra warning duplication or verbatim symmetry in other rows were reviewed and rejected as optional documentation polish, not material contract seams.
- Confirmatory rounds 10-18 produced clean convergence proof with no further accepted fixes.
- No public command expansion, no stable-release claim, no architecture rewrite.

## 4.0.0-candidate.11 - 2026-04-12
- Added an inline `OpenClaw quickstart for weak models` directly to `SKILL.md` so weak OpenClaw operators have a shortest safe path without cross-reading multiple files.
- Added an inline `OpenClaw host setup (weak-model executable)` section to `SKILL.md` with only real commands (`cd`, `python3 --version`, `pip3 install --user sentence-transformers numpy qdrant-client`, `./index-memory.sh --full --json`, `./health-check.sh --json`, `./query-memory.sh ...`).
- Added an explicit lowest-friction weak-model decision order: `health-check -> query(auto) -> read returned fields -> only then decide whether memorize or index is needed`.
- Retained the previously accepted weak-model honesty hardening: forced `semantic` / `hybrid` retrieval on unequipped hosts must be described through returned `mode_used`, `degraded`, and `semantic_ready` fields rather than overstated as semantic success.
- Retained the clarified hot-change-buffer durability wording (`RAM-resident`, `circular-buffer`, `non-durable`) and the synced WARN publish-qualification terminology.
- Final convergence result for the extended review scope: repeated DeepSeek/Qwen confirmatory rounds found no new material blocker after these weak-model/OpenClaw improvements.
- No runtime logic changes, no public command expansion, no stable-release claim.

## 4.0.0-candidate.10 - 2026-04-12
- Applied the accepted narrow SKILL.md wording cleanup for the hot-buffer truth line.
- Changed `very recent recovery-only recent changes` to `very recent recovery-only agent-made changes`.
- Narrowed the weak-model forced-mode contract so requested `semantic` / `hybrid` retrieval on an unequipped host must be reported via returned `mode_used`, `degraded`, and `semantic_ready` fields rather than being over-described as semantic success.
- Tightened the hot-change-buffer wording from `RAM-first, rotational` to `RAM-resident, circular-buffer, ... non-durable` to remove false durability implications.
- Synced WARN publish qualification terminology to the actual observed health-check shape (`lexical_freshness: ok=false`, `semantic_dependencies: ok=false`) instead of the older `: fail` shorthand.
- No runtime logic changes, no public command changes, no hot-buffer scope expansion.

## 4.0.0-candidate.9 - 2026-04-12
- Added a minimal safe-first Phase 1 internal hot-change-buffer for very recent agent-made changes.
- Buffer is RAM-first, rotational, recovery-only, non-canonical, aggressively noise-filtered, and bounded to a 32 MiB default target (64/128 MiB optional, 128 MiB max in this phase).
- Added only the minimal internal functions required for Phase 1: recent hot-event record/update/query, interrupted-sequence detection, recovery bundle assembly, compaction, and health reporting.
- Integrated the hot buffer into write/change logging, recent-change query routing, health reporting, minimal audit reporting, and maintenance compaction without adding any new public command.
- Explicitly kept hot-buffer truth below canonical files, durable change-memory, direct live inspection, Context Guardian, and audit truth.
- Added targeted Phase 1 eval coverage and passed strict release validation.

## 4.0.0-candidate.8 - 2026-04-12
- Completed the originally requested full review scope: 3 cycles total with 18 rounds of alternating Dual Thinking pressure-testing using AI Orchestrator and Qwen Orchestrator.
- Cycle 2 found and landed the last real post-`candidate.7` micro-fixes; cycle 3 then served as a clean no-new-issues convergence proof with 6 additional rounds and no new required changes.
- Moved `Change-memory truth` below `Change-memory authority boundary` to reduce weak-model reading-order risk.
- Changed weak-model rule #3 from `forced semantic/hybrid maintenance check` to `forced semantic/hybrid retrieval query` so normal forced retrieval does not get misclassified as maintenance.
- Normalized `system_hygiene` wording across `Current truth snapshot`, `Current host limitations`, and `Current blocker classification` to the clearer `zero-findings (stale state expected)` phrasing.
- Final campaign verdict after all 3 cycles: no remaining material seam in the skill artifact; release remains candidate, not stable.

## 4.0.0-candidate.7 - 2026-04-12
- Ran a strict 6-round Dual Thinking pressure test of the near-final candidate with alternating AI Orchestrator and Qwen Orchestrator, including one honest Qwen recovery round after session pollution repeated an already-fixed finding.
- Accepted only micro-fixes, with no public command expansion and no scope rewrite.
- Foregrounded current-host truth as `Current host execution mode: degraded lexical-only (semantic-unbuilt)` so weak models cannot miss that this host is still degraded.
- Disambiguated the maintenance note so it points directly to the Runtime Capability Matrix and Implemented-vs-Optional sections instead of the vague phrase `visible contract above`.
- Narrowed WARN continuation rules so read-only degraded queries do not require an invented rollback path, while write/maintenance continuations still require explicit rollback awareness.
- Anchored the stable-release checklist explicitly to equipped-host verification and clarified that unresolved `system_hygiene` status is separate from the non-blocking change-memory candidate classification.
- Replaced `file-derived fallback matches` with `degraded retrieval fallback matches` in the combined stale-index + semantic-unavailable WARN rule so fallback wording stays honest about the retrieval source.
- Final closure verdict for this candidate line: accept with micro-fixes landed; release remains candidate, not stable.

## 4.0.0-candidate.6 - 2026-04-12
- Prepared the next candidate release surface after the SKILL contract cleanup pass, without changing the public command surface or stable-release claim level.
- Release truth for this candidate is explicit: change-memory is implemented and live; change-audit integration is implemented and live; current host remains degraded / safe-first; `system_hygiene` remains stale / zero-findings on the current host; overall release remains candidate, not stable.
- Candidate-line documentation is now aligned around the cleaned current `SKILL.md` contract without introducing a new major refactor.

## 4.0.0-candidate.1 - 2026-04-12
- Published the current-generation local-only runtime as an explicit pre-release candidate so the stable `4.0.0` line remains reserved for the first equipped-host validation pass.
- This release contains the upgraded v4 runtime: local semantic spine, hybrid fusion, temporal-relational rerank, integrity audit, relation-aware writes, repair surface, telemetry, regression pack, release-prep, host-profile shaping, and stable-host readiness guidance.
- Host-state limitation remains explicit: this reference host is semantic-unbuilt, so the release is publish-honest as a candidate/pre-release, not as a stable full-hybrid tag.

## 4.0.0 - 2026-04-12
- Opened the new `4.0.0` candidate line because the runtime is no longer a lexical-first shell: local semantic indexing/search, hybrid fusion, temporal-relational rerank, integrity audit, and relation-aware learning writes now exist in code.
- Added a real local semantic spine: local embedding loading (`local_files_only=True`), semantic readiness/freshness, local Qdrant collection management, semantic rebuild, and semantic search.
- Added real hybrid quality logic: reciprocal-rank fusion, diversity control, temporal/recency shaping, source-confidence weighting, conflict-state handling, and relation-aware rerank pressure.
- Added integrity/audit surfaces: `audit-memory.sh`, `index-memory.sh --audit`, lexical/semantic drift detection, vector-state classification (`semantic-unbuilt`, `stale-vectors`, `orphan-vectors`), and stronger health visibility.
- Added relation-aware write/evolution paths: `memorize.sh` now records stable signatures, source-confidence, conflict status, canonical relation targets, and rejects new freeform relation labels.
- Reworked `mine-patterns.py` to cluster learning blocks instead of whole files and surface relation/conflict/review-status summaries for local memory evolution.
- Synced the skill contract to the new runtime truth: `semantic` and `hybrid` are real implemented modes, `auto` remains the default weak-model route, and release surfaces now distinguish implemented capability from host-state activation.
- Added host-profile shaping for `standard` vs `max` local operation without changing the weak-model public interface.
- Known candidate-line limitation: this host is still semantic-degraded because local embedding dependencies/model and built vectors are absent; the runtime reports that state honestly and does not overclaim semantic-ready operation.

## 3.4.9 - 2026-04-12
- Ran 6 additional full Dual Thinking cycles (36 planned rounds) on top of the published `3.4.8` baseline, using clean-room fresh consultant sessions from cycle 2 onward to reduce session-pollution repeats.
- Accepted only real post-`3.4.8` contract-clarity fixes that survived direct verification; rejected repeated, polluted, or code-false findings.
- Explicitly scoped direct `query-memory.sh --mode semantic` and `--mode hybrid` as compatibility/maintenance-only underlying CLI modes, keeping the active weak-model routing surface at `auto|exact|learning|recent`.
- Made `query-memory.sh` exit-code handling more self-contained and weak-model safe: exit `2` no longer borrows `health-check.sh` WARN semantics, and exit `1` now preserves freshness cautions when `warnings[]` still reports backlog/index-staleness conditions.
- Surfaced freshness-relevant warning categories directly in the visible contract so weak models do not need maintenance-fold context to apply the clean-miss caution rule.
- Tightened visible wording for literal accuracy on the historical lexical-first line before the later v4 candidate reclassification.
- Final closure outcome after the extra 6-cycle campaign: no remaining material blocker for the historical `v3.4.x` release line before the later v4 candidate reclassification.

## 3.4.8 - 2026-04-12
- Ran a fresh 6-round Dual Thinking review of `super-memori` with alternating AI Orchestrator and Qwen Orchestrator, including one honest Qwen recovery round after session pollution repeated an already-fixed finding.
- Added the missing public `memorize.sh` outcome contract and aligned it to real script behavior.
- Added explicit public `health-check.sh` and `index-memory.sh` exit-code handling for weak-model safety.
- Stabilized bad-arguments handling in `memorize.sh`, `health-check.sh`, and `index-memory.sh` so documented `4` paths are real rather than aspirational.
- Made `index-memory.sh` return exit code `2` when warnings are present, so degraded/partial maintenance runs are machine-visible.
- Tightened `query-memory.sh` exit-code `1` wording so weak models must inspect `degraded` first and frame degraded no-results honestly.
- Clarified that `index-memory.sh --rebuild-vectors` returning `2` on lexical-only hosts is an expected degraded outcome, not a hard failure.
- This release remains publish-compatible on a WARN host only because the skill explicitly documents lexical-first degraded operation and does not claim semantic-ready behavior on every host.

## 3.4.7 - 2026-04-11
- Applied the recovered Qwen round-4 documentation fix: replaced the stale `lexical_freshness=fail` phrase in `SKILL.md` with the actual query payload fields `index_stale=true` / `index_fresh=false`.
- Synced `references/verification-evidence.md` header to the accepted `3.4.7` state.

## 3.4.6 - 2026-04-11
- Tightened the new `query-memory.sh` exit-code contract after live validation exposed one more nuance: `exit 1` can occur on a degraded host when no results are returned.
- Clarified in both `SKILL.md` and `references/command-contracts.md` that weak models must inspect `degraded` and `warnings[]` alongside `exit 1` instead of assuming a fully healthy clean miss.

## 3.4.5 - 2026-04-11
- Continued the 6-round Dual Thinking rerun with a real consultant-backed fix from DeepSeek round 3.
- Added an explicit `query-memory.sh` exit-code interpretation table to the public `SKILL.md` contract so weak models can distinguish clean no-results (`1`) from a broken retrieval stack (`3`).
- Bound deterministic fallback handling to those exit-code rules instead of leaving post-command interpretation implicit.

## 3.4.4 - 2026-04-11
- Continued the 6-round Dual Thinking rerun with a real consultant-backed fix from Qwen round 2.
- Refactored `query-memory.sh` exit routing so documented codes are now honest: `4` bad arguments, `3` retrieval stack unavailable, `5` internal error, `2` only for degraded-but-usable results, `1` for clean no-results.
- Separated informational host-state warnings from real degraded execution, so `warnings[]` no longer automatically imply `degraded=true`.
- Version-locked verification evidence to `3.4.4` and replaced placeholder validation notes with concrete observed results.

## 3.4.3 - 2026-04-11
- Continued the 6-round Dual Thinking rerun with a real consultant-backed fix from DeepSeek round 1.
- Clarified that `--mode learning` is a lexical lookup over learning-memory entries in v3.x, not a separate semantic retrieval engine.
- Changed `query-memory.sh` so JSON output preserves `mode_used=learning` for learning-mode requests instead of collapsing them to `exact`.
- Synced the public skill contract and command-contract reference to that learning-mode reality.

## 3.4.2 - 2026-04-11
- Restarted Cycle 2 6-round Dual Thinking rerun from the published `v3.4.1` baseline under the corrected full-inline consultant method.
- Bound the worst-case double-degraded read path explicitly to degraded `query-memory.sh` surfaced fallback results instead of undefined direct file access.
- Aligned the mandatory double-degraded warning string across the Health & Safety Gate and command-contract surface.
- Added explicit structured-warning rule: mandatory degraded notices must live inside `warnings[]` in JSON mode rather than outside the payload.

## 3.4.1 - 2026-04-11
- Cycle 1 additional 6-round Dual Thinking rerun from the published `v3.4.0` baseline.
- Synced `references/command-contracts.md` to the actual `health-check.sh` implementation: real exit codes (`0/2/3/4/5`), required human-readable output contract, required JSON fields, and explicit weak-model interpretation rule.
- Rejected speculative escalations that relied on non-existent files or non-literal terms instead of the current artifact.

## 3.4.0 - 2026-04-11
- Ran a fresh Dual Thinking review cycle for `super-memori` with alternating AI Orchestrator and Qwen Orchestrator.
- Closed the runtime authority gap for the double-degraded WARN state: when lexical freshness is stale and semantic dependencies are unavailable at the same time, canonical markdown files are now the only authoritative source, and returned matches must be described as lexical / grep-derived file matches only.
- Clarified that `query-memory.sh --mode auto` remains valid on degraded hosts only as the script-selected degraded lexical path, not as an implicit guarantee of successful hybrid retrieval.
- Added the minimum honest ClawHub publish surface for this skill: `_meta.json`, `.clawhubignore`, `CHANGELOG.md`, `PACKAGING_CHECKLIST.md`, and release evidence files.
- Added explicit release-health policy: `FAIL` blocks publication, while `WARN` is publish-compatible only when it reflects documented optional/degraded host conditions and the release surface does not imply semantic-ready or fully healthy baseline. On this host, current `WARN` is due to stale lexical freshness plus unavailable semantic dependencies, which is documented degraded operation rather than a false healthy claim.
- Made the WARN publish exception deterministic in release evidence: qualification now records observed health-check state/fields (`WARN`, `lexical_freshness: fail`, `semantic_dependencies: fail`, no `FAIL`) instead of relying on free-text judgment alone.

## 3.3.3 - 2026-04-11
- Previous local release surface prepared during the same hardening pass; superseded by 3.4.0 after registry version collisions on 3.3.2 and 3.3.3, with no new semantic/runtime claim changes.

## 3.3.1 - 2026-04-09
- Added explicit degraded-mode prerequisite note for semantic / hybrid retrieval.
- Kept the public interface constrained to four commands for weak-model safety.
- Preserved lexical-first baseline with honest degraded-mode reporting when semantic retrieval is unavailable.
