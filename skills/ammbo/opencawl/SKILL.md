---
name: opencawl
description: Gives your Claw a phone number. Make and manage phone calls via OpenCawl. Use this skill whenever the user asks you to call someone, make a phone call, schedule a call, check on a call, set up inbound phone handling, or review call transcripts or outcomes.
homepage: https://opencawl.com
metadata: {"openclaw": {"emoji": "📞", "requires": {"env": ["OPENCAWL_API_KEY"]}, "primaryEnv": "OPENCAWL_API_KEY"}}
---

# OpenCawl

Gives your Claw a phone number. Make and manage outbound and inbound phone calls via the OpenCawl API, with live telephony handled by ElevenLabs and Twilio.

## Setup

1. Sign up at https://opencawl.com
2. Generate an API key at https://opencawl.com/dashboard/keys
3. Set `OPENCAWL_API_KEY` in your environment or via `skills.entries.opencawl.apiKey` in `~/.openclaw/openclaw.json`
4. Install this skill: `openclaw skills install opencawl`
5. Run `/opencawl setup` to provision a phone number and get the ElevenLabs webhook/tool configuration

---

## Call Architecture

OpenCawl is optimized around one primary mode.

### Outbound and Inbound: Autonomous

OpenClaw dispatches a goal and context to OpenCawl, then moves on. ElevenLabs handles the live conversation and Twilio dialing. Post-call webhooks are the primary completion path; polling is optional fallback.

Best for: appointment setting, lead qualification, outreach, follow-ups, collections — any call with a predictable conversation tree.

```
OpenClaw  →  opencawl.call(to, goal, context)
                    ↓
             OpenCawl + ElevenLabs run the call
                    ↓
             post-call webhook updates status immediately
                    ↓
             OpenClaw receives structured outcome
```

Inbound calls run through the same shared ElevenLabs agent, with per-user prompt, voice, first-message, and task-dispatch settings supplied by OpenCawl.

---

## Commands

### `call` — Make an outbound call

Dispatch a goal-based outbound call. Returns a `call_id` immediately. The call runs async; use `status` to track resolution.

**Parameters:**
- `to` (required): E.164 phone number, e.g. `+15551234567`
- `goal` (required): What the call should accomplish in plain language
- `context` (optional): Background the agent should know — lead source, prior interactions, objections to expect
- `persona` (optional): Voice/personality profile slug (e.g. `professional-friendly`, `direct-confident`)
- `voice_id` (optional): Override voice directly by voice library ID (e.g. `rachel`, `thomas`)
- `max_duration_seconds` (optional): Hard cap on call length in seconds (default: 300, max: 1800)
- `on_completion_webhook` (optional): HTTPS URL OpenCawl will POST the outcome to

**Example:**
```json
{
  "skill": "opencawl",
  "command": "call",
  "to": "+15551234567",
  "goal": "Schedule a 30-minute Workmate demo. Get their name, email, and two availability windows. If they push back, mention we have a 14-day free trial.",
  "context": "Inbound lead from the enterprise landing page. Requested info 2 days ago. Has not replied to follow-up email.",
  "persona": "professional-friendly"
}
```

**Returns:** `call_id`, `status: "ringing"`

---

### `status` — Check call outcome

Poll the status and result of any call.

**Parameters:**
- `call_id` (required): The call ID returned by `call`

**Returns:**
```json
{
  "call_id": "abc123def456",
  "direction": "outbound",
  "status": "completed",
  "outcome": "success",
  "to_number": "+15551234567",
  "goal": "Schedule a 30-minute Workmate demo",
  "persona": "professional-friendly",
  "summary": "Spoke with Jamie Chen. Scheduled demo for Thursday 2pm ET. Email: jamie@acme.com.",
  "extracted": {
    "name": "Jamie Chen",
    "email": "jamie@acme.com",
    "availability": ["Thursday 2pm ET", "Friday 10am ET"]
  },
  "duration_seconds": 187,
  "transcript": "...",
  "recording_url": "https://api.twilio.com/...",
  "created_at": "2026-03-28T14:00:00Z",
  "completed_at": "2026-03-28T14:03:07Z"
}
```

Possible `status` values: `initiated`, `queued`, `ringing`, `in_progress`, `completed`, `failed`, `no_answer`, `voicemail`, `busy`

---

### `calls` — List recent calls

List calls with optional filtering.

**Parameters:**
- `status` (optional): Filter by status
- `from` (optional): ISO date range start
- `to` (optional): ISO date range end
- `limit` (optional): Max results (default: 20, max: 100)
- `cursor` (optional): Pagination cursor from previous response

---

### `hangup` — End a call

Terminate an in-progress call.

**Parameters:**
- `call_id` (required): Call to end
- `reason` (optional): Logged reason (e.g. `"goal_achieved"`, `"no_answer_threshold"`)

---

### `voicemail` — Check voicemail inbox

List and read voicemails left on your OpenCawl number.

**Parameters:**
- `limit` (optional): Max results (default: 10)
- `unread_only` (optional): `true` to filter to unheard messages

---

### `credits` — Check balance

**Returns:** Credit balance, plan name, estimated minutes remaining, next reset date

---

### `setup` — First-time initialization

Reports your current phone number, inbound configuration, gateway config, and ElevenLabs webhook/tool endpoints. Run once after installing the skill.

```
/opencawl setup
```

---

## Personas

Personas define how OpenCawl sounds and behaves on calls. Each persona maps to a voice from the ElevenLabs voice library.

| Slug | Voice | Best For |
|------|-------|----------|
| `professional-friendly` | Emily | B2B outreach, demos, enterprise |
| `direct-confident` | Thomas | Executive outreach, follow-ups |
| `empathetic-support` | Serena | Support, onboarding, check-ins |
| `energetic-sales` | Freya | SMB sales, product promotions |
| `neutral-informational` | Adam | Appointment reminders, surveys |

Pass the persona slug in the `call` command. If omitted, your dashboard voice selection is used. You can also pass `voice_id` directly to use any voice from the library.

See `references/personas.md` for the full voice library and ElevenLabs model recommendations.

---

## Inbound Tasks

To let the shared ElevenLabs agent perform real work during live calls, configure a per-user OpenClaw gateway webhook in OpenCawl settings. The agent uses the OpenCawl task tools to dispatch work and check status.

---

## Configuration Reference

`~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "opencawl": {
        "enabled": true,
        "apiKey": "sk-cawl-...",
        "env": {
          "OPENCAWL_API_URL": "https://opencawl.com",
          "OPENCAWL_DEFAULT_PERSONA": "professional-friendly",
          "OPENCAWL_MAX_DURATION": "300",
          "OPENCAWL_ANNOUNCE_CHANNEL": "telegram"
        }
      }
    }
  }
}
```

---

## Reference Files

- `references/inbound.md` — Inbound autonomous call setup and gateway task-dispatch pattern
- `references/personas.md` — Voice/persona configuration and ElevenLabs voice mapping
- `references/api.md` — Full OpenCawl REST API reference (all endpoints, request/response schemas)
