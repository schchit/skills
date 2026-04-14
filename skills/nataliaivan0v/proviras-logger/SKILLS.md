---
name: proviras-logger
description: Run on every heartbeat to summarize completed tasks and log them to your analytics dashboard. Triggers automatically during heartbeat cycles to track agent productivity, task outcomes, activity summaries, and which skills were used per task.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - PROVIRAS_USER_ID
      bins:
        - curl
    primaryEnv: PROVIRAS_USER_ID
    emoji: "📊"
---

# Proviras Logger

## Purpose
On every heartbeat, summarize what you have done since the last heartbeat and POST it to the proviras API.

## Workflow
1. Read today's memory log at memory/YYYY-MM-DD.md
2. Check if an agent ID exists in references/config.md
3. If no agent ID exists, run scripts/register.sh to register this agent and save the returned agent_id to references/config.md
4. Summarize tasks completed since the last heartbeat into structured JSON — for each task, include which OpenClaw skills were invoked to complete it
5. Run scripts/log.sh with the JSON payload
6. If the POST succeeds, respond ANALYTICS_OK
7. If the POST fails, note the failure quietly and continue

## Output format
- When constructing the log payload, read references/payload-schema.md for the exact JSON structure required. Construct the payload from today's memory log before calling scripts/log.sh.
- Pass the constructed JSON as the first argument to log.sh: bash scripts/log.sh "$PAYLOAD"