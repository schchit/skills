#!/bin/bash
# health-check.sh — Inspect all active agent sessions and detect stuck/dead agents
# Usage: health-check.sh
#
# Called by: HEARTBEAT.md / cron (every ~15 min during active swarm)
# Checks:
#   1. For each "running" task: is its tmux session alive? Any recent output?
#   2. Sessions idle > STUCK_MINUTES with a running task → mark stuck, notify
#   3. Sessions where tmux pane shows shell prompt ($) but task still "running" → agent exited silently
#   4. Update agent-pool.json status accordingly

set -euo pipefail

STUCK_MINUTES=15
TASKS_FILE="$HOME/.openclaw/workspace/swarm/active-tasks.json"
POOL_FILE="$HOME/.openclaw/workspace/swarm/agent-pool.json"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
NOTIFY_TARGET=$(cat "$HOME/.openclaw/workspace/swarm/notify-target" 2>/dev/null || echo "")
NOW_TS=$(date +%s)

if [[ ! -f "$TASKS_FILE" ]]; then
  echo "No active swarm. Exiting."
  exit 0
fi

# Check if swarm is active (any running/pending tasks)
HAS_ACTIVE=$(python3 -c "
import json
tasks = json.load(open('$TASKS_FILE'))['tasks']
print('yes' if any(t['status'] in ('running','pending','reviewing') for t in tasks) else 'no')
")

if [[ "$HAS_ACTIVE" == "no" ]]; then
  echo "No active tasks. Skipping health check."
  exit 0
fi

echo "🔍 Running health check..."

ISSUES_FOUND=false

# Get all running tasks with their tmux sessions
python3 -c "
import json
tasks = json.load(open('$TASKS_FILE'))['tasks']
for t in tasks:
    if t['status'] == 'running' and t.get('tmux'):
        print(f\"{t['id']}|{t['tmux']}|{t.get('updated_at','')}\")
" | while IFS="|" read -r TASK_ID TMUX_SESSION UPDATED_AT; do

  # Check if tmux session exists
  if ! tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
    echo "💀 $TASK_ID: tmux session '$TMUX_SESSION' is DEAD (task still marked running)"
    ISSUES_FOUND=true
    # Update pool
    python3 -c "
import json
from datetime import datetime, timezone
pool = json.load(open('$POOL_FILE'))
now = datetime.now(timezone.utc).isoformat()
for a in pool['agents']:
    if a['tmux'] == '$TMUX_SESSION':
        a['status'] = 'dead'
        a['last_seen'] = now
with open('$POOL_FILE', 'w') as f:
    json.dump(pool, f, indent=2, ensure_ascii=False)
" 2>/dev/null || true

    if [[ -n "$NOTIFY_TARGET" ]]; then
      openclaw message send --channel telegram --target "$NOTIFY_TARGET" \
        -m "💀 $TASK_ID ($TMUX_SESSION): tmux session 已死亡但任务仍标 running，请检查" --silent 2>/dev/null &
    fi
    continue
  fi

  # Capture last 5 lines of pane output
  PANE_OUTPUT=$(tmux capture-pane -t "$TMUX_SESSION" -p 2>/dev/null | tail -5 | tr '\n' ' ')

  # Check if agent finished silently (pane shows shell prompt with no active process)
  # Look for patterns like "$ " or "❯ " at end of output (shell waiting for input)
  if echo "$PANE_OUTPUT" | grep -qE '(\$\s*$|❯\s*$|%\s*$)'; then
    echo "⚠️ $TASK_ID ($TMUX_SESSION): agent may have exited (shell prompt visible)"
    echo "   Last output: $PANE_OUTPUT"
    ISSUES_FOUND=true
    if [[ -n "$NOTIFY_TARGET" ]]; then
      openclaw message send --channel telegram --target "$NOTIFY_TARGET" \
        -m "⚠️ $TASK_ID ($TMUX_SESSION): agent 可能已退出但未触发 on-complete。请检查 tmux。" --silent 2>/dev/null &
    fi
    continue
  fi

  # Check if stuck (no status update for > STUCK_MINUTES)
  if [[ -n "$UPDATED_AT" ]]; then
    # Parse ISO8601 to epoch
    UPDATED_TS=$(python3 -c "
from datetime import datetime
import sys
try:
    dt = datetime.fromisoformat('$UPDATED_AT'.replace('Z','+00:00'))
    print(int(dt.timestamp()))
except:
    print(0)
" 2>/dev/null || echo 0)

    ELAPSED=$(( NOW_TS - UPDATED_TS ))
    STUCK_SECS=$(( STUCK_MINUTES * 60 ))

    if [[ $ELAPSED -gt $STUCK_SECS ]]; then
      ELAPSED_MIN=$(( ELAPSED / 60 ))
      echo "⏱️ $TASK_ID ($TMUX_SESSION): no status update for ${ELAPSED_MIN}min (threshold: ${STUCK_MINUTES}min)"
      echo "   Last output: $PANE_OUTPUT"
      ISSUES_FOUND=true
      if [[ -n "$NOTIFY_TARGET" ]]; then
        openclaw message send --channel telegram --target "$NOTIFY_TARGET" \
          -m "⏱️ $TASK_ID ($TMUX_SESSION): 已 ${ELAPSED_MIN} 分钟无进展，可能卡住了。最近输出：$PANE_OUTPUT" --silent 2>/dev/null &
      fi
    else
      echo "✅ $TASK_ID ($TMUX_SESSION): active (last update ${ELAPSED}s ago)"
    fi
  fi

done

# Update last_seen for all live sessions in pool
python3 -c "
import json, subprocess
from datetime import datetime, timezone

pool_file = '$POOL_FILE'
if not __import__('os').path.exists(pool_file):
    exit()

pool = json.load(open(pool_file))
now = datetime.now(timezone.utc).isoformat()

for a in pool['agents']:
    result = subprocess.run(['tmux', 'has-session', '-t', a['tmux']], capture_output=True)
    if result.returncode == 0:
        a['last_seen'] = now
        if a['status'] == 'dead':
            a['status'] = 'idle'  # session was recreated
    else:
        if a['status'] != 'dead':
            a['status'] = 'dead'

pool['updated_at'] = now
with open(pool_file, 'w') as f:
    json.dump(pool, f, indent=2, ensure_ascii=False)
print('Pool updated.')
" 2>/dev/null || true

echo "🔍 Health check complete."
exit 0
