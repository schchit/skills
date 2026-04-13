#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
SKILL="$ROOT/SKILL.md"
MODES="$ROOT/references/modes.md"
EXAMPLES="$ROOT/references/examples.md"

require_present() {
  local needle="$1" file="$2"
  if ! grep -Fq "$needle" "$file"; then
    echo "[FAIL] missing '$needle' in $file" >&2
    exit 1
  fi
}

require_absent() {
  local needle="$1" file="$2"
  if grep -Fq "$needle" "$file"; then
    echo "[FAIL] unexpected stale '$needle' in $file" >&2
    exit 1
  fi
}

require_present 'set `ORCHESTRATOR_MODE: multi`' "$SKILL"
require_present 'set `ORCHESTRATOR_MODE: multi`' "$MODES"
require_present '`ORCHESTRATOR_MODE: multi`' "$EXAMPLES"
require_present 'MODE:` stays the semantic task mode' "$EXAMPLES"
require_present '#### Round-Limit & Stop Precedence' "$SKILL"
require_present '### Round-Limit & Stop Precedence' "$ROOT/references/runtime-contract.md"
require_present 'If the user explicitly authorized a higher round count' "$SKILL"
require_present 'If the user explicitly authorized a higher round count' "$ROOT/references/runtime-contract.md"
require_present 'do not emit a user-facing progress reply between cycles' "$SKILL"
require_present 'do not emit a user-facing progress reply between cycles' "$ROOT/references/runtime-contract.md"
require_present 'continue immediately into that `NEXT_ACTION`' "$SKILL"
require_present 'continue immediately into that `NEXT_ACTION`' "$ROOT/references/runtime-contract.md"
require_present 'multi-cycle-no-intercycle-reply' "$ROOT/references/reference-scenarios.md"
require_present 'no-idle-after-completed-step' "$ROOT/references/reference-scenarios.md"
require_absent 'MODE: alternating-multi-orchestrator' "$EXAMPLES"
require_absent '`alternating-multi-orchestrator` when the user explicitly requested alternation before round 1.' "$MODES"

echo '[OK] reference alignment passed'
