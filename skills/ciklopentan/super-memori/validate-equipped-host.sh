#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

./index-memory.sh --incremental --json
./index-memory.sh --rebuild-vectors --json
./query-memory.sh "agent memory" --mode hybrid --json --limit 3 | tee /tmp/super-memori-equipped-query.json
./validate-release.sh --strict
./scripts/release-prep.sh

python3 - <<'PY'
import json, pathlib
payload = json.loads(pathlib.Path('/tmp/super-memori-equipped-query.json').read_text())
if payload.get('mode_used') != 'hybrid':
    raise SystemExit(f"equipped-host validation failed: mode_used={payload.get('mode_used')}")
if not payload.get('semantic_ready'):
    raise SystemExit('equipped-host validation failed: semantic_ready=false')
if payload.get('degraded'):
    raise SystemExit('equipped-host validation failed: degraded=true')
print('Host is fully equipped and v4.0.0 hybrid mode is operational.')
print('Semantic retrieval: ACTIVE')
print('Vector state: HEALTHY')
PY
