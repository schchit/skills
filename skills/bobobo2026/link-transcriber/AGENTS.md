# AGENTS

## Project Snapshot

This repository is the public distribution repo for the `link-transcriber` skill.

Current purpose:

- distribute a Codex-compatible public skill
- support Douyin and Xiaohongshu link summarization
- call the live `linkTranscriber` API
- rely on server-side saved platform cookies when needed
- return only the final summary text to the end user

This repo is intentionally small and should stay focused on the skill distribution surface only.

## Invocation Guardrails

- For current product behavior, use this repo's `SKILL.md` as the stable contract.
- Do not use `web/skill/` as the current source of truth; it is legacy migration reference only.
- Default to `https://linktranscriber.store/linktranscriber-api` for public use.
- If the hosted service reports missing platform cookies, treat it as a server-side configuration issue rather than asking the end user for cookies by default.
- Poll until a true final state arrives. In-progress states are broader than `PENDING` and include `PARSING`, `DOWNLOADING`, `TRANSCRIBING`, `SUMMARIZING`, `FORMATTING`, and `SAVING`.

## Current Status

What is already done:

- `SKILL.md` is valid and installed locally in Codex
- `agents/openai.yaml` exists and matches the current skill behavior
- `scripts/call_service_example.py` supports:
  - infer platform from URL
  - create transcription task
  - poll transcription task
  - call summaries API
  - print only final summary text
- `scripts/check_service_health.py` is the preferred hosted-service health check path for this repo
- API base URL is intentionally configurable:
  - default public origin: `https://linktranscriber.store/linktranscriber-api`
  - set `LINK_SKILL_API_BASE_URL` only when an override is required
  - avoid raw IPs and plain HTTP in public copy
- Xiaohongshu and Douyin cookies are expected to be managed on the hosted service side for production use
- real API smoke has already succeeded against Xiaohongshu
- public GitHub repo has already been created and pushed:
  - `https://github.com/bobobo2026/link-transcriber-skill`

ClawHub status:

- CLI login is valid
- publish succeeded on `2026-04-01`
- canonical slug should match the skill name for new installs
- published version:
  - `0.1.6`
- published slug:
  - `link-transcriber`
- published page:
  - `https://clawhub.ai/bobobo2026/link-transcriber`
- legacy published slug:
  - `link-transcriber-skill-public`

## Source Of Truth

Behavior source of truth:

- [SKILL.md](/Users/yibo/Documents/company/IdeaProjects/KnowledgeOS/skill/SKILL.md)

Codex UI metadata source of truth:

- [agents/openai.yaml](/Users/yibo/Documents/company/IdeaProjects/KnowledgeOS/skill/agents/openai.yaml)

Public repo overview:

- [README.md](/Users/yibo/Documents/company/IdeaProjects/KnowledgeOS/skill/README.md)

ClawHub-oriented copy:

- [CLAWHUB.md](/Users/yibo/Documents/company/IdeaProjects/KnowledgeOS/skill/CLAWHUB.md)

Smoke / example runner:

- [scripts/check_service_health.py](/Users/yibo/Documents/company/IdeaProjects/KnowledgeOS/skill/scripts/check_service_health.py)
- [scripts/call_service_example.py](/Users/yibo/Documents/company/IdeaProjects/KnowledgeOS/skill/scripts/call_service_example.py)
- [scripts/update_local_skill.sh](/Users/yibo/Documents/company/IdeaProjects/KnowledgeOS/skill/scripts/update_local_skill.sh)

## Key Product Behavior

Supported platforms:

- `douyin`
- `xiaohongshu`

Not supported in this repo’s current public skill positioning:

- YouTube
- raw transcription JSON as the default user-facing result

End-user behavior:

1. user provides a link
2. skill relies on server-side saved platform cookies when needed
3. skill infers platform when possible
4. skill creates transcription task
5. skill polls until transcription finishes
6. skill calls summaries API
7. skill returns only `summary_markdown`

## Live API Details

Public API base URL:

- default: `https://linktranscriber.store/linktranscriber-api`
- override with `LINK_SKILL_API_BASE_URL` when needed

Health check:

- `GET /api/sys_check`

Transcription create:

- `POST /api/service/transcriptions`

Transcription lookup:

- `GET /api/service/transcriptions/{task_id}`

Summary generation:

- `POST /api/service/summaries`

Default summary settings:

- `provider_id=deepseek`
- `model_name=deepseek-chat`

## Validation Commands

Validate skill structure:

```bash
python3 /Users/yibo/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  /Users/yibo/Documents/company/IdeaProjects/KnowledgeOS/skill
```

Compile script:

```bash
python3 -m compileall /Users/yibo/Documents/company/IdeaProjects/KnowledgeOS/skill/scripts
```

Check hosted service health:

```bash
python3 /Users/yibo/Documents/company/IdeaProjects/KnowledgeOS/skill/scripts/check_service_health.py
```

Run live smoke:

```bash
python3 /Users/yibo/Documents/company/IdeaProjects/KnowledgeOS/skill/scripts/call_service_example.py \
  'https://xhslink.com/o/23s4jTem6em'
```

Optional API base override:

```bash
LINK_SKILL_API_BASE_URL=https://linktranscriber.store/linktranscriber-api \
python3 /Users/yibo/Documents/company/IdeaProjects/KnowledgeOS/skill/scripts/call_service_example.py \
  'https://xhslink.com/o/23s4jTem6em'
```

## Follow-ups

Immediate:

- verify one real Douyin smoke path in addition to Xiaohongshu

Short-term:

- add one concrete “natural language user examples” section to `README.md`
- verify Codex installation from the public GitHub repo on a clean machine or clean Codex profile

Optional:

- add a lightweight changelog section in `README.md`
- add a second smoke example for explicit platform selection

## Constraints

- Keep this repo focused on public skill distribution only
- Do not pull backend implementation, deployment docs, or unrelated project history into this repo
- Do not reintroduce unrelated workflow positioning into public skill copy
- Prefer updating `SKILL.md`, `agents/openai.yaml`, `README.md`, and `CLAWHUB.md` together so public descriptions stay aligned
