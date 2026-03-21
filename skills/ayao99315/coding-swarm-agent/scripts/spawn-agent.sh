#!/bin/bash
# spawn-agent.sh — Dynamically create a new tmux agent session and register it
# Usage: spawn-agent.sh <type> <project_dir>
#   type: codex | claude
#
# Naming convention (written here, never change):
#   Codex backend agents:     codex-1, codex-2, codex-3, codex-4
#   Claude Code frontend:     cc-frontend-1, cc-frontend-2
#   Claude Code plan (fixed): cc-plan        (never auto-spawned)
#   Claude Code review:       cc-review      (never auto-spawned)
#   Codex review:             codex-review   (never auto-spawned)
#
# Exits 0 on success, 1 on failure (already at max / memory block / already exists)

set -euo pipefail

TYPE="${1:?Usage: spawn-agent.sh <codex|claude> <project_dir>}"
PROJECT_DIR="${2:?}"
POOL_FILE="$HOME/.openclaw/workspace/swarm/agent-pool.json"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load limits from pool file
MAX_CODEX=$(python3 -c "import json; d=json.load(open('$POOL_FILE')); print(d['limits']['max_codex'])" 2>/dev/null || echo 4)
MAX_CC=$(python3 -c "import json; d=json.load(open('$POOL_FILE')); print(d['limits']['max_cc_frontend'])" 2>/dev/null || echo 2)

# ── Memory check ──────────────────────────────────────────────────────────
MEM_OUTPUT=$("$SCRIPT_DIR/check-memory.sh" 2>/dev/null || true)
MEM_STATUS=$(echo "$MEM_OUTPUT" | grep "STATUS=" | cut -d= -f2)
FREE_MB=$(echo "$MEM_OUTPUT" | grep "FREE_MB=" | cut -d= -f2)

if [[ "$MEM_STATUS" == "block" ]]; then
  echo "❌ Spawn blocked: insufficient RAM (${FREE_MB}MB free). Not spawning $TYPE agent."
  # Notify
  NOTIFY_TARGET=$(cat "$HOME/.openclaw/workspace/swarm/notify-target" 2>/dev/null || echo "")
  if [[ -n "$NOTIFY_TARGET" ]]; then
    openclaw message send --channel telegram --target "$NOTIFY_TARGET" \
      -m "⚠️ Agent 扩容被阻止：RAM 只剩 ${FREE_MB}MB，暂不新开 $TYPE agent" --silent 2>/dev/null &
  fi
  exit 1
fi

# ── Find next available session name ──────────────────────────────────────
NEW_SESSION=""
NEW_INDEX=0

if [[ "$TYPE" == "codex" ]]; then
  for i in $(seq 1 $MAX_CODEX); do
    NAME="codex-$i"
    if ! tmux has-session -t "$NAME" 2>/dev/null; then
      NEW_SESSION="$NAME"
      NEW_INDEX=$i
      break
    fi
  done
  AGENT_TYPE="codex"
  DOMAIN="backend"
elif [[ "$TYPE" == "claude" ]]; then
  for i in $(seq 1 $MAX_CC); do
    NAME="cc-frontend-$i"
    if ! tmux has-session -t "$NAME" 2>/dev/null; then
      NEW_SESSION="$NAME"
      NEW_INDEX=$i
      break
    fi
  done
  AGENT_TYPE="claude"
  DOMAIN="frontend"
else
  echo "❌ Unknown type: $TYPE (use codex or claude)"
  exit 1
fi

if [[ -z "$NEW_SESSION" ]]; then
  echo "❌ Already at max capacity for $TYPE (max=$( [[ $TYPE == codex ]] && echo $MAX_CODEX || echo $MAX_CC ))"
  exit 1
fi

# ── Create tmux session ────────────────────────────────────────────────────
tmux new-session -d -s "$NEW_SESSION" -c "$PROJECT_DIR"
echo "✅ Created tmux session: $NEW_SESSION"

# ── Register in agent-pool.json ───────────────────────────────────────────
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

python3 -c "
import json
from datetime import datetime, timezone

pool_file = '$POOL_FILE'
with open(pool_file) as f:
    data = json.load(f)

new_agent = {
    'id': '$NEW_SESSION',
    'type': '$AGENT_TYPE',
    'domain': '$DOMAIN',
    'tmux': '$NEW_SESSION',
    'status': 'idle',
    'current_task': None,
    'spawned_at': '$NOW',
    'last_seen': '$NOW'
}

# Remove if already exists (shouldn't happen but be safe)
data['agents'] = [a for a in data['agents'] if a['id'] != '$NEW_SESSION']
data['agents'].append(new_agent)
data['updated_at'] = '$NOW'

with open(pool_file, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'Registered {new_agent[\"id\"]} in agent pool')
"

# Memory warning notification
if [[ "$MEM_STATUS" == "warn" ]]; then
  NOTIFY_TARGET=$(cat "$HOME/.openclaw/workspace/swarm/notify-target" 2>/dev/null || echo "")
  if [[ -n "$NOTIFY_TARGET" ]]; then
    openclaw message send --channel telegram --target "$NOTIFY_TARGET" \
      -m "⚠️ 新开 $NEW_SESSION（RAM 仅剩 ${FREE_MB}MB，注意内存压力）" --silent 2>/dev/null &
  fi
fi

echo "$NEW_SESSION"  # Return session name for caller
exit 0
