#!/bin/bash
# Per-Agent Memory Compression Skill - Universal Installer v1.2.1
# Auto-discovers agents and registers compression tasks with full feature set

set -e

echo "🎯 Installing Per-Agent Memory Compression Skill (Universal) v1.2.1"
echo ""

# 1. Pre-checks
echo "🔍 Running pre-installation checks..."

if ! command -v openclaw &> /dev/null; then
  echo "❌ openclaw CLI not found in PATH"
  exit 1
fi

if ! openclaw agents list --json &> /dev/null; then
  echo "❌ openclaw agents list failed - is Gateway running?"
  exit 1
fi

echo "✅ Pre-checks passed"
echo ""

# 2. Discover agents with workspaces
AGENTS_JSON=$(openclaw agents list --json 2>&1)

AGENTS=$(echo "$AGENTS_JSON" | jq -r '.[] | select(.workspace != null) | "\(.id)=\(.workspace)"' 2>/dev/null)
if [ -z "$AGENTS" ]; then
  echo "❌ No agents with workspace found"
  exit 1
fi

echo "📋 Discovered agents:"
echo "$AGENTS" | while IFS='=' read -r id ws; do
  echo "  ✅ $id → $ws"
done
echo ""

# 3. Define domain context for known agents
declare -A DOMAIN_CONTEXT
DOMAIN_CONTEXT[main]="general (main agent - overall user context)"
DOMAIN_CONTEXT[hrbp]="HR/work-related (hrbp agent - professional, career, organizational development)"
DOMAIN_CONTEXT[parenting]="Parenting/family (parenting agent - children, education, family dynamics)"
DOMAIN_CONTEXT[decoration]="Renovation/decoration (decoration agent - construction, materials, project management)"
# Default for unknown agents
DOMAIN_CONTEXT[default]="agent-specific (adapt based on agent's identity and role)"

# 4. Staggered schedule offsets (minutes from 03:00 Sunday)
OFFSETS=(0 30 60 90 120 150 180 210 240 270)

INDEX=0
TASK_IDS=()
echo "$AGENTS" | while IFS='=' read -r agent_id workspace; do
  OFFSET=${OFFSETS[$INDEX]}
  INDEX=$((INDEX + 1))
  
  HOUR=$((3 + OFFSET / 60))
  MINUTE=$((OFFSET % 60))
  CRON="${MINUTE} ${HOUR} * * 0"
  
  TASK_NAME="per_agent_compression_${agent_id}"
  
  # Check if task exists
  if openclaw cron list --json 2>/dev/null | jq -e --arg name "$TASK_NAME" '.jobs[] | select(.name == $name)' >/dev/null; then
    echo "  ⚠️  Task $TASK_NAME already exists, skipping"
    continue
  fi
  
  echo "  📝 Creating: $TASK_NAME ($CRON)"
  
  # Determine domain context
  DOMAIN="${DOMAIN_CONTEXT[$agent_id]:-$DOMAIN_CONTEXT[default]}"
  
  # Use a concise but informative message (within CLI limits)
  # Full details are in the skill README; this summary ensures task works out of the box.
  MSG="AUTONOMOUS: Weekly per-agent memory consolidation for '$agent_id'.\n\nWorkspace: $workspace\nDAILY_NOTES_DIR: {WORKSPACE}/memory\nPROCESSED_DIR: {WORKSPACE}/memory/processed\nSTATE_FILE: {WORKSPACE}/memory/.compression_state.json\nTARGET_FILES: USER.md, IDENTITY.md, SOUL.md, MEMORY.md\n\nDOMAIN_CONTEXT: \"$DOMAIN\"\n\nEXECUTION PLAN:\n1) Pre-check paths\n2) Load/init state (last_compressed_date, processed_notes)\n3) List notes: YYYY-MM-DD.md, date<today-7, not processed\n4) Sort oldest first, limit 5\n5) Each note: read, extract preferences/decisions/info, dedupe (same date), append to targets with date header (### [YYYY-MM-DD])\n6) Move note to processed/, update state\n7) Save state, clean buffer\n8) Announce summary (processed count, remaining old notes count)\n\nIMPORTANT: Extract ONLY factual/explicit info. Append only. Continue on error. See skill README for full details.\n\nExecute without waiting."
  
  if openclaw cron add \
    --name "$TASK_NAME" \
    --cron "$CRON" \
    --tz "Asia/Shanghai" \
    --agent "main" \
    --message "$MSG" \
    --model "openrouter/stepfun/step-3.5-flash:free" \
    --timeout 1200 \
    --session "isolated" \
    --announce \
    --channel "dingtalk-connector" \
    --to "05566651511149398" \
    --best-effort-deliver 2>&1; then
    
    TASK_IDS+=("$TASK_NAME")
  else
    echo "    ❌ Failed to create task $TASK_NAME"
  fi
done

echo ""
echo "✅ Installation complete!"
echo ""
if [ ${#TASK_IDS[@]} -gt 0 ]; then
  echo "📋 Created ${#TASK_IDS[@]} task(s):"
  for tid in "${TASK_IDS[@]}"; do
    echo "   - $tid"
  done
  echo ""
  echo "💡 Note: Task messages are concise but contain all essential logic."
  echo "💡 For full execution plan details, see: /root/.openclaw/workspace/skills/per-agent-compression-universal/README.md"
  echo "💡 Verify: openclaw cron list | grep per_agent_compression"
  echo "💡 Uninstall: ./uninstall.sh"
else
  echo "⚠️  No new tasks were created (all may already exist)"
fi
