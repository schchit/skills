#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
INTERVAL_SECONDS="${INTERVAL_SECONDS:-60}"
LOG_FILE="${LOG_FILE:-${TMPDIR:-/tmp}/long-run-mode-watchdog.log}"

while true; do
  {
    printf '\n[%s] watchdog tick\n' "$(date '+%Y-%m-%d %H:%M:%S %z')"
    cd "$ROOT/.."
    "$PYTHON_BIN" "$ROOT/scripts/recover_due_tasks.py" --json || true
    LONG_RUN_MODE_AUTO_RESUME="${LONG_RUN_MODE_AUTO_RESUME:-}" OPENCLAW_BIN="${OPENCLAW_BIN:-openclaw}" OPENCLAW_SESSIONS_FILE="${OPENCLAW_SESSIONS_FILE:-}" "$PYTHON_BIN" "$ROOT/scripts/run_keepalive_once.py" --idle-seconds "$INTERVAL_SECONDS" || true
  } >> "$LOG_FILE" 2>&1
  sleep "$INTERVAL_SECONDS"
done
