# Link Transcriber Skill

`link-transcriber` is a minimal Codex-compatible skill for turning Douyin and Xiaohongshu links into a readable summary as quickly as possible.

It is meant to be a free, low-friction entry point: paste a link and get back only the final summary.

It uses the live linkTranscriber service at:

- `https://linktranscriber.store/linktranscriber-api`

The service uses server-side saved platform cookies when they are needed. End users do not need to provide cookies to use this skill.

For local smoke or a private deployment, you can still override the default:

- `LINK_SKILL_API_BASE_URL`
- `LINK_SKILL_SUMMARY_PROVIDER_ID` (optional, default `deepseek`)
- `LINK_SKILL_SUMMARY_MODEL_NAME` (optional, default `deepseek-chat`)

Published ClawHub page:

- `https://clawhub.ai/bobobo2026/link-transcriber-skill-public`

The skill workflow is:

1. accept a Douyin or Xiaohongshu link
2. infer the platform when possible
3. create a transcription task using the server's saved platform cookies when required
4. poll until transcription finishes
5. call the summaries API
6. return only the final summary text

Operational guardrails:

- the stable public endpoint is `https://linktranscriber.store/linktranscriber-api`
- do not swap in a raw server IP for normal public usage
- if the service reports missing platform cookies, treat that as a hosted-service configuration problem instead of asking the end user for cookies by default
- poll through all in-progress statuses, not only `PENDING`

That narrow workflow is intentional. This public skill stays focused on link-to-summary only.

## Install In Codex

Install from this GitHub repository, then restart Codex so it picks up the skill.

You can also open the published ClawHub page:

- `https://clawhub.ai/bobobo2026/link-transcriber-skill-public`

After installation, use it in natural language:

```text
Use $link-transcriber to summarize this link: https://xhslink.com/o/23s4jTem6em
```

## Behavior

- Supports Douyin and Xiaohongshu
- Uses server-side saved platform cookies when needed
- Platform is inferred from the URL when possible
- Built for quick first-use value and easy sharing
- Default summaries provider: `deepseek`
- Default summaries model: `deepseek-chat`
- Final user-facing output is only the summary text
- In-progress task states include `PARSING`, `DOWNLOADING`, `TRANSCRIBING`, `SUMMARIZING`, `FORMATTING`, and `SAVING`

## Local Smoke

Run the example script directly:

```bash
python3 scripts/call_service_example.py 'https://xhslink.com/o/23s4jTem6em'
```

Override the API base URL if needed:

```bash
LINK_SKILL_API_BASE_URL=https://linktranscriber.store/linktranscriber-api \
python3 scripts/call_service_example.py 'https://xhslink.com/o/23s4jTem6em'
```

## Files

- `SKILL.md` - canonical skill behavior
- `agents/openai.yaml` - Codex UI metadata
- `scripts/call_service_example.py` - transcribe + poll + summarize example
- `CLAWHUB.md` - ClawHub-oriented publish copy
