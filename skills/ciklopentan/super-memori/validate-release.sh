#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
STRICT=0
if [[ "${1:-}" == "--strict" ]]; then
  STRICT=1
fi

python3 ../skill-creator-canonical/scripts/quick_validate.py "$ROOT"
python3 ../skill-creator-canonical/scripts/validate_weak_models.py "$ROOT"
python3 tests/test_temporal_retrieval.py
python3 tests/test_relation_target_validation.py
python3 tests/test_repair_plan.py
python3 tests/test_semantic_unbuilt_state.py
python3 tests/test_promotion_candidates.py
python3 tests/test_hot_change_buffer.py
python3 tests/test_evals_surface.py
python3 repair-memory.sh --classify --json >/tmp/super-memori-repair-classify.json
python3 audit-memory.sh --json >/tmp/super-memori-audit.json
./health-check.sh --json >/tmp/super-memori-health.json || true

python3 - <<'PY'
import json, pathlib, sys
root = pathlib.Path('/tmp')
audit = json.loads((root / 'super-memori-audit.json').read_text())
health = json.loads((root / 'super-memori-health.json').read_text())
checks = {item.get('name'): item for item in health.get('checks', [])}
if audit.get('broken_relations'):
    raise SystemExit('release gate blocked: broken_relations present')
if audit.get('vector_state') not in {'ok', 'semantic-unbuilt', 'stale-vectors'}:
    raise SystemExit(f"release gate blocked: unexpected vector_state {audit.get('vector_state')}")
if health.get('status') == 'FAIL':
    raise SystemExit('release gate blocked: health FAIL')
for forbidden_name in ('canonical_files', 'lexical_fts'):
    item = checks.get(forbidden_name)
    if item and not item.get('ok', False):
        raise SystemExit(f'release gate blocked: critical WARN surface {forbidden_name} is not ok')
print('[OK] release gate baseline checks passed')
PY

if [[ "$STRICT" == "1" ]]; then
  python3 - <<'PY'
import json, pathlib
root = pathlib.Path('/tmp')
health = json.loads((root / 'super-memori-health.json').read_text())
audit = json.loads((root / 'super-memori-audit.json').read_text())
if health.get('status') not in {'OK', 'WARN'}:
    raise SystemExit('strict gate blocked: invalid health state')
if audit.get('vector_state') == 'orphan-vectors':
    raise SystemExit('strict gate blocked: orphan-vectors drift present')
print('[OK] strict release gate checks passed')
PY
fi
