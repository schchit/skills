# LinkTranscriber ClawHub Publish Notes

This skill is now published on ClawHub:

- `https://clawhub.ai/bobobo2026/link-transcriber-skill-public`

- Canonical skill source: `SKILL.md`
- Canonical UI metadata: `agents/openai.yaml`
- Public API base URL: `https://linktranscriber.store/linktranscriber-api`
- Override only when needed: `LINK_SKILL_API_BASE_URL`
- Script overrides: `LINK_SKILL_API_BASE_URL`, `LINK_SKILL_SUMMARY_PROVIDER_ID`, `LINK_SKILL_SUMMARY_MODEL_NAME`
- Supported platforms in this minimal version: Douyin and Xiaohongshu only
- Inputs: `url` and inferred or confirmed `platform`
- Behavior: create a transcription task, let the server use its saved platform cookies when needed, poll the task result, call summaries, return only the final summary text
- Positioning: quick, free entry point for link summarization, not a full product surface

When preparing old-channel listing copy, keep it minimal:

- collects the link first
- relies on server-side saved platform cookies
- creates a transcription task through the service API
- calls the summaries API after transcription completes
- returns only the final summary text
