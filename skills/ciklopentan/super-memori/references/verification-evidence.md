# Verification Evidence — super-memori 4.0.0-candidate.12

## Current line classification
- line: `4.0.0-candidate.12`
- reason: runtime architecture has crossed the lexical-first v3 boundary and now includes real local semantic indexing/search, hybrid fusion, temporal-relational rerank, integrity audit, and relation-aware learning writes
- frozen historical line: `3.4.9 release`
- current host state: degraded lexical-only operation because local semantic dependencies/model and built vectors are absent on this host

## Accepted structural upgrades in this line
1. Added a real local semantic runtime spine in code:
   - local embedding model loading with `local_files_only=True`
   - semantic readiness/freshness state
   - local Qdrant collection management
   - semantic index rebuild and semantic search
2. Added real hybrid quality logic:
   - reciprocal-rank fusion
   - diversity pass
   - temporal/recency shaping
   - source-confidence weighting
   - conflict-state handling
   - relation-aware rerank pressure
3. Added integrity/audit surfaces:
   - `audit-memory.sh`
   - `index-memory.sh --audit`
   - vector-state classification (`semantic-unbuilt`, `stale-vectors`, `orphan-vectors`)
   - stronger `health-check.sh` integrity visibility
4. Added relation-aware learning writes and evolution metadata:
   - stable signatures
   - `source_confidence`
   - `conflict_status`
   - canonical relation targets
   - rejection of new freeform relation labels
5. Reworked pattern mining from file-level noise toward block-level clustering with relation/conflict/review-status summaries.
6. Reclassified the skill contract and release surfaces onto an honest v4 candidate pre-release line.
7. Fresh 3-cycle / 18-round rerun from `4.0.0-candidate.11` accepted three additional micro-fixes:
   - explicit lexical-authority revocation in the combined stale-index + semantic-unavailable WARN state
   - full removal of the misleading `zero-findings` host-state token from current-host wording
   - explicit exit-code `1` override back to the exact Health & Safety Gate degraded notice for that same combined WARN state

## Current host-observed truth
- lexical index: working
- lexical freshness: working after refresh
- semantic deps/model: missing on this host
- qdrant reachable: yes
- qdrant collection populated: no
- semantic vectors: absent
- semantic host state: degraded / unbuilt
- integrity audit: warns honestly about `semantic-unbuilt` vector state and legacy broken relation targets from earlier non-canonical writes

## Validation evidence recorded so far
### code syntax / runtime compile
Command:
- `python3 -m py_compile skills/super_memori/query-memory.sh skills/super_memori/index-memory.sh skills/super_memori/health-check.sh skills/super_memori/audit-memory.sh skills/super_memori/memorize.sh skills/super_memori/scripts/super_memori_common.py skills/super_memori/mine-patterns.py`
Observed result:
- no syntax failures

### temporal retrieval eval
Command:
- `python3 skills/super_memori/tests/test_temporal_retrieval.py`
Observed result:
- `[OK] temporal retrieval rerank cases passed`

### integrity audit surface
Command:
- `python3 skills/super_memori/audit-memory.sh --json`
Observed result:
- `status=warn`
- `vector_state=semantic-unbuilt`
- no orphan chunks
- no orphan FTS chunks
- missing vectors reported explicitly
- legacy non-canonical relation targets still flagged as broken relation residue

### host health surface
Command:
- `cd skills/super_memori && ./health-check.sh --json`
Observed result:
- `status=WARN`
- warnings reflect semantic host degradation and integrity drift visibility
- lexical DB / FTS healthy
- semantic-ready not claimed

### negative relation-target validation
Command:
- `cd skills/super_memori && ./memorize.sh --json --reviewed --refines semantic-spine "invalid relation target test" lesson`
Observed result:
- exit code `4`
- invalid freeform relation target rejected as intended

## Release honesty rule for this line
- Do not call this line stable `4.0.0 release` yet.
- It is the current `4.0.0-candidate.12` line until an equipped host proves semantic-ready execution via `validate-equipped-host.sh` and the stable-host readiness sequence.
- Historical `3.x` remains historical only; it is no longer the current runtime truth.
- Current host WARN is publish-compatible only if the release surface explicitly states that semantic-ready behavior is implemented in code but not active on hosts lacking the required local dependencies/model/vector build.
