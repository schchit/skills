---
name: openclaw-reporter
description: |
  Opt-in reporter for the OpenClaw global claw heatmap.
  On first use, ASKS the user for consent before registering.
  Sends a heartbeat (platform + model only) when the skill is loaded.
  Task reports are only sent when the user explicitly mentions completing a task.
  Data collected: user-chosen claw name, OS platform, model name, generic task category.
  Credentials: the server returns an apiKey on registration, which is stored locally
  in ~/.openclaw/config.json and sent as a Bearer token in subsequent requests.
  No file paths, code, tool names, or project-specific data is ever sent.
requirements:
  network: true
  writeFiles:
    - "~/.openclaw/config.json"
  binaries:
    - curl
    - uname
  env:
    - name: CLAUDE_MODEL
      required: false
      description: "Current Claude model identifier. Used to report which model is active. Falls back to 'unknown' if not set."
hooks:
  SessionStart:
    - hooks:
        - type: command
          command: "CONFIG=\"$HOME/.openclaw/config.json\"; [ -f \"$CONFIG\" ] && KEY=$(grep -o '\"apiKey\"[[:space:]]*:[[:space:]]*\"[^\"]*\"' \"$CONFIG\" | head -1 | sed 's/.*\"\\([^\"]*\\)\"$/\\1/') && [ -n \"$KEY\" ] && curl -s -o /dev/null --max-time 5 -X POST 'https://kymr.top/api/v1/heartbeat' -H 'Content-Type: application/json' -H \"Authorization: Bearer $KEY\" -d \"{\\\"platform\\\":\\\"$(uname -s | tr '[:upper:]' '[:lower:]')\\\",\\\"model\\\":\\\"${CLAUDE_MODEL:-unknown}\\\"}\" 2>/dev/null || true"
          timeout: 10
---

# OpenClaw Reporter

This skill lets you participate in the OpenClaw global claw activity heatmap. It reports **minimal, non-code** activity data to visualize worldwide AI agent usage. Note: as with any HTTPS request, the server can observe your IP address.

## How It Works

- **Heartbeat**: Sent once when the skill is loaded (`SessionStart` hook). No other automated hooks are used — no `PostToolUse`, no `Stop` hooks.
- **Task report**: Sent **only** when the user explicitly mentions completing a task or asks for a report. The agent calls the task API directly — no automated scripts.
- **Registration**: One-time setup requiring explicit user consent (see below).

## Data Disclosure

This skill sends the following data to `https://kymr.top/` (the OpenClaw Market production server; server-side source code is in this repository under `app/api/v1/`):

| Data Field | Example | Purpose |
|---|---|---|
| Claw Name | `CoolClaw42` (user-chosen) | Your display name on the heatmap |
| Platform | `darwin`, `linux` | OS type for heatmap stats |
| Model | `claude-sonnet-4-6` | Model usage stats |
| Task summary | `"Completed a task"` | Generic activity indicator |

**Stored locally:** Registration returns an `apiKey` from the server, saved in `~/.openclaw/config.json` with `chmod 600` (owner-only access). The endpoint URL (`https://kymr.top/`) is hardcoded — not read from the config file — so a modified config cannot redirect telemetry.

**Visible to the server:** Your IP address is visible on every HTTPS request (inherent to any network call). The server uses IP for approximate geolocation on the heatmap — no more precise than city-level.

**Never sent:** system usernames, file paths, code snippets, project names, tool names, tool arguments, tool results, or secrets.

## Configuration

Config is stored at `~/.openclaw/config.json` (permissions `600`). No external scripts are deployed — the heartbeat is sent inline via the `SessionStart` hook command.

## First-Time Setup (Requires User Consent)

If `~/.openclaw/config.json` does not exist, follow these steps:

### Step 1: Ask for consent

Use the AskUserQuestion tool:

- Question: "OpenClaw Reporter wants to register a claw name and send a heartbeat (platform + model only) to https://kymr.top/ when the skill loads. Task reports are only sent when you explicitly mention completing a task. The server will issue an API key stored locally at ~/.openclaw/config.json. No file paths, code, tool names, or project data is sent. Allow?"
- Options: "Yes, register" / "No, skip"

**If the user selects "No, skip":** do NOT register and do NOT ask again in this session. Stop here.

### Step 2: Ask for a claw name

If the user consented, use AskUserQuestion again:

- Question: "Pick a name for your claw on the heatmap! (1-30 chars, letters/numbers/hyphens/underscores only, e.g. CoolClaw, NightCrawler, CodeClaw)"
- Let the user type a custom name via the "Other" option (no preset options needed, but provide a few fun suggestions as options)
- Options: "CoolClaw" / "CodeClaw" / "NightCrawler"

Use whatever the user provides as the claw name.

### Step 3: Register and save config

After receiving the name (stored as `CLAW_NAME`), run the following:

```bash
# --- OpenClaw Registration ---
set -e

OPENCLAW_ENDPOINT="https://kymr.top"
CLAW_NAME="USER_CHOSEN_NAME_HERE"

# Validate claw name: only allow alphanumeric, hyphens, underscores (1-30 chars).
# This whitelist ensures $CLAW_NAME is safe for shell interpolation and JSON embedding.
if ! echo "$CLAW_NAME" | grep -qE '^[A-Za-z0-9_-]{1,30}$'; then
  echo "Error: Claw name must be 1-30 characters, alphanumeric/hyphens/underscores only."
  exit 1
fi

mkdir -p ~/.openclaw

# Register with the server
# Safe: CLAW_NAME is validated above to contain only [A-Za-z0-9_-]
RESPONSE=$(curl -s -X POST "$OPENCLAW_ENDPOINT/api/v1/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"$CLAW_NAME\",
    \"platform\": \"$(uname -s | tr '[:upper:]' '[:lower:]')\",
    \"model\": \"${CLAUDE_MODEL:-unknown}\"
  }")

# Extract fields from JSON response using grep/sed (no python3 needed)
CLAW_ID=$(echo "$RESPONSE" | grep -o '"clawId"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/')
API_KEY=$(echo "$RESPONSE" | grep -o '"apiKey"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/')

if [ -z "$API_KEY" ]; then
  echo "Error: Registration failed. Server response: $RESPONSE"
  exit 1
fi

# Write config file
cat > ~/.openclaw/config.json << CFGEOF
{
  "clawId": "$CLAW_ID",
  "apiKey": "$API_KEY",
  "name": "$CLAW_NAME"
}
CFGEOF
chmod 600 ~/.openclaw/config.json

echo "Registered as: $CLAW_NAME"
```

## Task Reporting (Manual Only)

Task reports are **never sent automatically**. Only send a task report when the user explicitly mentions completing a task, finishing work, or asks to report activity.

When triggered, run:

```bash
CONFIG="$HOME/.openclaw/config.json"
[ -f "$CONFIG" ] || { echo "OpenClaw not registered."; exit 0; }
KEY=$(grep -o '"apiKey"[[:space:]]*:[[:space:]]*"[^"]*"' "$CONFIG" | head -1 | sed 's/.*"\([^"]*\)"$/\1/')
[ -z "$KEY" ] && { echo "No API key found."; exit 0; }
curl -s -o /dev/null --max-time 5 -X POST 'https://kymr.top/api/v1/task' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $KEY" \
  -d "{\"summary\":\"Completed a task\",\"model\":\"${CLAUDE_MODEL:-unknown}\"}" 2>/dev/null \
  && echo "Task reported." || echo "Task report failed (non-blocking)."
```

## Opt-Out / Unregister

To stop all OpenClaw reporting:

```bash
rm -f ~/.openclaw/config.json
rmdir ~/.openclaw 2>/dev/null
echo "OpenClaw fully uninstalled."
```

After deletion, no heartbeats or task reports will be sent. The skill will ask for consent again if re-enabled.

## Behavior Rules

1. **User consent is REQUIRED** before first registration — never register silently
2. If the user declines registration, respect the decision and do not ask again in the same session
3. Heartbeat is sent automatically via the `SessionStart` hook when the skill is loaded — this is the ONLY automated action
4. **Task reports are manual only** — only send when the user explicitly mentions completing a task or asks to report
5. If any OpenClaw request fails, continue normally — never interrupt the user's workflow
6. Never include identifying information in task summaries
7. **No external scripts**: all logic is inline or executed by the agent directly
8. **No system-level modifications**: never write to `~/.claude/settings.json` or any file outside `~/.openclaw/`
