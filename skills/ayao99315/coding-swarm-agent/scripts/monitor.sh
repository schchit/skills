#!/bin/bash
# Agent Swarm Monitor — run via cron every 3 minutes
# Checks tmux sessions for status changes and signals OpenClaw

SIGNAL_FILE="/tmp/agent-swarm-signals.jsonl"
SESSIONS=("cc-plan" "codex-1" "cc-frontend" "cc-review" "codex-review")
STATE_DIR="/tmp/agent-swarm-state"
mkdir -p "$STATE_DIR"

check_agent() {
  local session=$1
  local output
  output=$(tmux capture-pane -t "$session" -p 2>/dev/null | tail -30)

  # Session doesn't exist
  if [[ -z "$output" ]]; then
    echo "dead"
    return
  fi

  local last_lines
  last_lines=$(echo "$output" | tail -5)

  # Still running (active output)
  if echo "$last_lines" | grep -qE "⏳|Thinking|Working|✻ Worked|Compiling|Building"; then
    echo "running"
    return
  fi

  # Possibly waiting for input
  if echo "$output" | grep -qE "\?$|确认|请提供|需要.*信息|Please (provide|confirm|specify)|Yes.*No|which.*should"; then
    echo "waiting_input"
    return
  fi

  # Error detected
  if echo "$output" | grep -qiE "^error|FATAL|panic|Exception|Traceback|command not found"; then
    echo "error"
    return
  fi

  # Idle (prompt visible, no activity)
  if echo "$last_lines" | grep -qE "^❯\s*$|^\\\$\s*$"; then
    echo "idle"
    return
  fi

  echo "unknown"
}

changed=false

for session in "${SESSIONS[@]}"; do
  status=$(check_agent "$session")
  prev_file="$STATE_DIR/$session.status"
  prev_status=""
  [[ -f "$prev_file" ]] && prev_status=$(cat "$prev_file")

  if [[ "$status" != "$prev_status" ]]; then
    echo "$status" > "$prev_file"
    ts=$(date +%s)
    echo "{\"agent\":\"$session\",\"status\":\"$status\",\"prev\":\"$prev_status\",\"time\":$ts}" >> "$SIGNAL_FILE"
    changed=true
  fi
done

# Also check for new commits
PROJECT_DIR=$(cat ~/.openclaw/workspace/swarm/project-dir 2>/dev/null)
if [[ -n "$PROJECT_DIR" && -d "$PROJECT_DIR/.git" ]]; then
  last_commit_file="$STATE_DIR/last-commit"
  current_commit=$(cd "$PROJECT_DIR" && git rev-parse --short HEAD 2>/dev/null)
  prev_commit=""
  [[ -f "$last_commit_file" ]] && prev_commit=$(cat "$last_commit_file")

  if [[ -n "$current_commit" && "$current_commit" != "$prev_commit" ]]; then
    echo "$current_commit" > "$last_commit_file"
    commit_msg=$(cd "$PROJECT_DIR" && git log --oneline -1 2>/dev/null)
    ts=$(date +%s)
    echo "{\"event\":\"new_commit\",\"hash\":\"$current_commit\",\"message\":\"$commit_msg\",\"time\":$ts}" >> "$SIGNAL_FILE"
    changed=true
  fi
fi

# If anything changed, notify OpenClaw main session
if [[ "$changed" == "true" ]]; then
  # Read the latest signals and send notification
  latest=$(tail -5 "$SIGNAL_FILE")
  openclaw system event --text "Agent swarm status change detected. Check signals." --mode now 2>/dev/null || true
fi
