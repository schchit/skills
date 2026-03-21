#!/bin/bash
# update-task-status.sh — Atomically update a task's status in active-tasks.json
# Usage: update-task-status.sh <task_id> <new_status> [commit_hash] [tokens_json] [tmux_session]
#
# tokens_json: optional JSON string e.g. '{"input":1234,"output":567,"cache_read":0,"cache_write":0}'
# This updates active-tasks.json synchronously before any follow-up handling.

set -euo pipefail

TASK_ID="${1:?Usage: update-task-status.sh <task_id> <status> [commit_hash] [tokens_json] [tmux_session]}"
NEW_STATUS="${2:?}"
COMMIT_HASH="${3:-}"
TOKENS_JSON="${4:-}"
TMUX_SESSION="${5:-}"

TASKS_FILE="$HOME/.openclaw/workspace/swarm/active-tasks.json"
LOCK_FILE="${TASKS_FILE}.lock"

# Ensure flock is available (macOS: installed via util-linux but not in default PATH)
export PATH="/opt/homebrew/opt/util-linux/bin:$PATH"

if [[ ! -f "$TASKS_FILE" ]]; then
  echo "ERROR: $TASKS_FILE not found" >&2
  exit 1
fi

# Update task status + commit + tokens + timestamp, and auto-unblock dependents.
# Uses flock to serialize concurrent writers (e.g. multiple agents finishing at
# nearly the same time).
# Special behaviour when new_status == "running":
#   - pending/failed/retrying → running claims the task (check-and-set)
#   - running → running is treated as heartbeat and only refreshes updated_at
#   - Other running transitions exit with code 2 so dispatch.sh skips duplicate dispatch
exec 200>"$LOCK_FILE"
flock -x 200

set +e
python3 -c "
import json, sys
from datetime import datetime, timezone

task_id = '$TASK_ID'
new_status = '$NEW_STATUS'
commit_hash = '$COMMIT_HASH'
tokens_raw = '''$TOKENS_JSON'''
tmux_session = '$TMUX_SESSION'

with open('$TASKS_FILE', 'r') as f:
    data = json.load(f)

now = datetime.now(timezone.utc).isoformat()
updated = False

# Parse tokens JSON (safe fallback)
tokens = None
if tokens_raw.strip():
    try:
        tokens = json.loads(tokens_raw.strip())
    except Exception:
        pass

for t in data.get('tasks', []):
    if t['id'] == task_id:
        current_status = t.get('status', '')

        if new_status == 'running':
            if current_status == 'running':
                t['updated_at'] = now
                if tmux_session:
                    t['tmux'] = tmux_session
                updated = True
                break
            elif current_status not in ('pending', 'failed', 'retrying'):
                print(f'SKIP: {task_id} already {current_status} (race-condition guard)', file=sys.stderr)
                sys.exit(2)

        t['status'] = new_status
        t['updated_at'] = now
        if new_status == 'running' and tmux_session:
            t['tmux'] = tmux_session
        if commit_hash and commit_hash != 'none':
            if 'commits' not in t:
                t['commits'] = []
            if commit_hash not in t['commits']:
                t['commits'].append(commit_hash)
        # Persist token usage — accumulate across attempts
        if tokens:
            prev = t.get('tokens', {'input': 0, 'output': 0, 'cache_read': 0, 'cache_write': 0})
            t['tokens'] = {
                'input':       prev.get('input', 0)       + tokens.get('input', 0),
                'output':      prev.get('output', 0)      + tokens.get('output', 0),
                'cache_read':  prev.get('cache_read', 0)  + tokens.get('cache_read', 0),
                'cache_write': prev.get('cache_write', 0) + tokens.get('cache_write', 0),
            }
        updated = True
        break

if not updated:
    print(f'WARN: task {task_id} not found in active-tasks.json', file=sys.stderr)
    sys.exit(0)

# Auto-unblock: if new_status is 'done', scan blocked tasks
if new_status == 'done':
    done_ids = {t['id'] for t in data['tasks'] if t['status'] == 'done'}
    unblocked = []
    for t in data['tasks']:
        if t['status'] == 'blocked':
            deps = set(t.get('depends_on', []))
            if deps and deps.issubset(done_ids):
                t['status'] = 'pending'
                t['updated_at'] = now
                unblocked.append(t['id'])
    if unblocked:
        print(f'Unblocked: {unblocked}')

data['updated_at'] = now

with open('$TASKS_FILE', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

token_str = ''
if tokens:
    token_str = f' | tokens: in={tokens.get(\"input\",0)} out={tokens.get(\"output\",0)} cache_r={tokens.get(\"cache_read\",0)} cache_w={tokens.get(\"cache_write\",0)}'
print(f'{task_id} -> {new_status}' + (f' (commit: {commit_hash})' if commit_hash else '') + token_str)
"
UTS_EC=$?
set -e

flock -u 200
exec 200>&-

# If task just became done, check milestone completion in background
if [[ "$NEW_STATUS" == "done" && "${UTS_EC:-0}" == "0" ]]; then
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  "$SCRIPT_DIR/milestone-check.sh" "$TASK_ID" 2>/dev/null &
fi

# Propagate Python exit code (flock subshell swallows it otherwise)
exit ${UTS_EC:-0}
