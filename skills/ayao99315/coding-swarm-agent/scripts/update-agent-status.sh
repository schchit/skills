#!/bin/bash
# update-agent-status.sh — Update a single agent's status in agent-pool.json
# Usage: update-agent-status.sh <session_id> <status> [task_id]
#   status: idle | busy | dead
#   task_id: current task (empty string to clear)

set -euo pipefail

SESSION_ID="${1:?Usage: update-agent-status.sh <session_id> <status> [task_id]}"
NEW_STATUS="${2:?}"
CURRENT_TASK="${3:-}"

POOL_FILE="$HOME/.openclaw/workspace/swarm/agent-pool.json"
[[ ! -f "$POOL_FILE" ]] && exit 0

python3 -c "
import json
from datetime import datetime, timezone

pool = json.load(open('$POOL_FILE'))
now = datetime.now(timezone.utc).isoformat()
found = False

for a in pool['agents']:
    if a['id'] == '$SESSION_ID' or a['tmux'] == '$SESSION_ID':
        a['status'] = '$NEW_STATUS'
        a['last_seen'] = now
        a['current_task'] = '$CURRENT_TASK' if '$CURRENT_TASK' else None
        found = True
        break

if not found:
    # Agent not in pool yet (e.g. pre-existing fixed session) — add it
    pass

pool['updated_at'] = now
with open('$POOL_FILE', 'w') as f:
    json.dump(pool, f, indent=2, ensure_ascii=False)
" 2>/dev/null || true

exit 0
