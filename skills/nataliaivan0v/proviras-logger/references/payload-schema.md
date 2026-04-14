# Log Payload Schema

Use this schema to construct the JSON payload before calling log.sh.

## Full structure
{
  "agent_id": "<read from references/config.md>",
  "logged_at": "<current ISO timestamp>",
  "period_start": "<timestamp of last heartbeat>",
  "period_end": "<current timestamp>",
  "tasks": [
    {
      "title": "<short description of what was done>",
      "category": "<email|calendar|file|web|code|other>",
      "outcome": "<completed|failed|partial>",
      "duration_estimate": "<integer minutes if inferrable, else null>",
      "cost_estimate": "<token cost if logged, else null>",
      "skills_used": ["<skill name>", "<skill name>"],
      "summary": "<1-2 plain English sentences describing what happened>"
      "collaborators": ["agt_abc123", "agt_xyz789"]
    }
  ],
  "heartbeat_status": "<active|idle>"
}

## Rules
- tasks should only include work done since period_start
- skills_used should list OpenClaw skill names invoked during the task
- skills_used should be an empty array [] if no skills were invoked
- duration_estimate and cost_estimate are nullable — omit if unknown
- heartbeat_status is active if any tasks were completed, idle if none
- logged_at and period_end are the same timestamp