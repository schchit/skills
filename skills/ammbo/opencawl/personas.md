# Personas & Voice Configuration

Personas define how OpenCawl sounds and behaves on calls. Each persona maps to a voice from the ElevenLabs voice library configured in OpenCawl.

---

## Built-in Personas

| Slug | Voice | Style | Best For |
|------|-------|-------|----------|
| `professional-friendly` | Emily | Calm, professional | B2B outreach, demos, enterprise |
| `direct-confident` | Thomas | Clear, authoritative | Executive outreach, follow-ups |
| `empathetic-support` | Serena | Soft, soothing | Support, onboarding, check-ins |
| `energetic-sales` | Freya | Gentle, upbeat | SMB sales, product promotions |
| `neutral-informational` | Adam | Deep, clear default | Appointment reminders, surveys |

Pass a persona slug in the `call` command's `persona` field. If omitted, your dashboard voice selection is used.

---

## Voice Library

OpenCawl includes 20 curated ElevenLabs voices available to Starter and Pro plans. Free plan users get the default voice (Adam).

| ID | Name | Gender | Category | Accent |
|----|------|--------|----------|--------|
| `default` | Adam | Male | Default | American |
| `rachel` | Rachel | Female | Conversational | American |
| `domi` | Domi | Female | Conversational | American |
| `bella` | Bella | Female | Conversational | American |
| `antoni` | Antoni | Male | Conversational | American |
| `elli` | Elli | Female | Conversational | American |
| `josh` | Josh | Male | Conversational | American |
| `arnold` | Arnold | Male | Conversational | American |
| `sam` | Sam | Male | Conversational | American |
| `emily` | Emily | Female | Professional | American |
| `thomas` | Thomas | Male | Professional | American |
| `charlie` | Charlie | Male | Professional | Australian |
| `charlotte` | Charlotte | Female | Professional | British |
| `james` | James | Male | Professional | Australian |
| `lily` | Lily | Female | Friendly | British |
| `george` | George | Male | Friendly | British |
| `freya` | Freya | Female | Friendly | American |
| `daniel` | Daniel | Male | Authoritative | British |
| `serena` | Serena | Female | Calm | American |
| `michael` | Michael | Male | Conversational | American |

Use any voice ID directly via the `voice_id` parameter in the `call` command.

---

## Voice Cloning (Pro Only)

Pro plan users can clone their own voice via the dashboard at https://opencawl.com/dashboard/voice. Upload audio samples and OpenCawl creates a custom ElevenLabs voice. Cloned voices appear in the voice library with a `clone_` prefix.

---

## ElevenLabs Voice Mapping

OpenCawl uses ElevenLabs for all speech synthesis. Each voice in the library maps to an ElevenLabs voice ID.

**Recommended ElevenLabs models for calls:**
- `eleven_turbo_v2_5` — lowest latency, best for turn-based inbound where response time matters
- `eleven_multilingual_v2` — highest quality, best for outbound where latency is less critical
- `eleven_flash_v2_5` — ultra-low latency, use when inbound turn response time is critical

---

## Persona in API Calls

Pass the persona slug in any `call` command:

```json
{
  "to": "+15551234567",
  "goal": "Qualify the lead and book a demo",
  "persona": "professional-friendly"
}
```

Or use `voice_id` directly:

```json
{
  "to": "+15551234567",
  "goal": "Qualify the lead and book a demo",
  "voice_id": "rachel"
}
```

Priority: `persona` > `voice_id` > user's dashboard voice selection > default (Adam).

If both `persona` and `voice_id` are provided, persona wins.
