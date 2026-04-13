# Reference Test Log — super-memori 4.0.0-candidate.12

## 2026-04-12
Validation set for the current candidate line:
- `python3 -m py_compile skills/super_memori/query-memory.sh skills/super_memori/index-memory.sh skills/super_memori/health-check.sh skills/super_memori/audit-memory.sh skills/super_memori/memorize.sh skills/super_memori/scripts/super_memori_common.py skills/super_memori/mine-patterns.py`
- `python3 skills/super_memori/tests/test_temporal_retrieval.py`
- `python3 skills/super_memori/audit-memory.sh --json`
- `cd skills/super_memori && ./health-check.sh --json`
- `cd skills/super_memori && ./index-memory.sh --stats --json`
- `cd skills/super_memori && ./query-memory.sh "relation-aware memory" --mode auto --json --limit 3`
- `cd skills/super_memori && ./memorize.sh --json --reviewed --refines semantic-spine "invalid relation target test" lesson`
- `cd skills/super_memori && ./query-memory.sh "learning memory" --mode learning --json --limit 3`

Observed interpretation:
- The artifact is no longer merely a lexical-first shell; the runtime now contains a real local semantic/hybrid/temporal/audit spine.
- Host reality is still degraded because semantic dependencies/model and built vectors are absent on this machine.
- `query-memory.sh --mode learning` still runs as a learning-oriented lane over the current runtime and reports that host-specific lexical-only execution honestly when semantic readiness is absent.
- `audit-memory.sh` now distinguishes `semantic-unbuilt` host state from stronger integrity drift categories instead of collapsing everything into false `ok` or fake corruption.
- New freeform relation targets are now rejected at write time; remaining broken-relation findings are historical residue from earlier pre-canonical writes.
- The strongest remaining work after this sync pass is equipped-host stable-release validation, not contract drift cleanup.

Additional rerun evidence on 2026-04-12:
- a fresh full 3-cycle / 18-round Dual Thinking rerun from the published `4.0.0-candidate.11` baseline completed honestly
- accepted fixes in that rerun were limited to three narrow contract-clarity hardenings: lexical-authority revocation in the combined degraded WARN state; removal of misleading `zero-findings` host-state wording; and an exit-code `1` override back to the exact Health & Safety Gate degraded notice for that same combined WARN state
- all later confirmatory rounds converged cleanly with no further accepted fixes

Candidate-line conclusion:
- keep this line as `4.0.0-candidate.12`
- do not publish as stable `4.0.0 release` until an equipped host passes the stable-host readiness sequence
