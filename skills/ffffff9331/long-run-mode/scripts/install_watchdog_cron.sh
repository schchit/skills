#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
INTERVAL="${1:-5}"
LOG_FILE="${LOG_FILE:-${TMPDIR:-/tmp}/long-run-mode-watchdog.log}"

cat <<EOF
# 建议添加到 crontab 的条目（每 ${INTERVAL} 分钟跑一次兜底回收）
# 可选环境变量：PYTHON_BIN、LOG_FILE、OPENCLAW_BIN、OPENCLAW_SESSIONS_FILE、LONG_RUN_MODE_AUTO_RESUME
# 默认只做检查/生成计划；只有显式设置 LONG_RUN_MODE_AUTO_RESUME=1 时才允许自动续跑
*/${INTERVAL} * * * * cd "$ROOT/.." && PYTHON_BIN="$PYTHON_BIN" LOG_FILE="$LOG_FILE" OPENCLAW_BIN="${OPENCLAW_BIN:-openclaw}" OPENCLAW_SESSIONS_FILE="${OPENCLAW_SESSIONS_FILE:-}" LONG_RUN_MODE_AUTO_RESUME="${LONG_RUN_MODE_AUTO_RESUME:-}" "$PYTHON_BIN" "$ROOT/scripts/run_watchdog_once.py" >> "$LOG_FILE" 2>&1
EOF
