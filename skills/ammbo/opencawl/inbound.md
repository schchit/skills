# Inbound Call Handling

Inbound calls support two modes configured via `POST /api/phone/configure`:

| Mode | How it works |
|------|-------------|
| `autonomous` (default) | Preferred mode. ElevenLabs handles the live call loop with OpenCawl-provided per-user overrides. |
| `voicemail_only` | Caller goes straight to voicemail. Transcription available if enabled. |

---

## Autonomous Setup

### 1. Configure your number

Via the OpenCawl dashboard:

- `https://opencawl.com/dashboard/settings` for inbound mode, prompt, greeting, voicemail, and gateway configuration
- `https://opencawl.com/dashboard/numbers` for dedicated-number provisioning

Set `gateway_token` as well if your gateway requires bearer auth.

### 2. Configure ElevenLabs

Follow `ELEVENLABS_TWILIO_SETUP.md` and configure:

- one shared ElevenLabs agent
- Twilio personalization webhook
- post-call webhook
- task tool endpoints
- shared Twilio number import
- any dedicated numbers you provision through OpenCawl

---

## Live Call Pattern

Each inbound autonomous call follows this loop:

```
1. Caller speaks
2. ElevenLabs calls OpenCawl personalization webhook
3. OpenCawl returns the user's voice, prompt, greeting, and dynamic variables
4. ElevenLabs runs the live call loop
5. If real work is needed, ElevenLabs calls OpenCawl task tools
6. OpenCawl dispatches the task to the user's OpenClaw gateway webhook
7. The gateway completes the task through OpenCawl
8. ElevenLabs continues the call using the returned task state
9. After hangup, ElevenLabs sends transcript and analysis to OpenCawl
```

---

## Gateway Completion

The user's OpenClaw gateway completes dispatched tasks by POSTing back to OpenCawl:

```json
{
  "task_id": "task_123",
  "status": "completed",
  "summary": "Rescheduled for Tuesday at 2pm.",
  "result": {
    "appointment_time": "Tuesday 2pm"
  }
}
```

---

## Prompt Guidance

Keep the user-level inbound prompt short and durable. Good default shape:

```text
You are OpenCawl for this user.
Be concise and natural on the phone.
Confirm the requested task before acting.
Use the OpenCawl task tools for external actions.
Do not claim success until a tool or downstream system confirms it.
```

`turn_relay`, `/api/openclaw/respond`, and `/api/openclaw/turns` are deprecated and should not be used for new setups.
