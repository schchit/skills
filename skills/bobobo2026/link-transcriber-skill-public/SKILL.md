---
name: link-transcriber
description: Use this skill when a user wants to submit a Douyin or Xiaohongshu link to the linkTranscriber transcription API, let the server use its saved platform cookies, wait for transcription to finish through all in-progress states, then call the summaries API and return only the final summary markdown to the user.
---

# Link Transcriber

## Overview

This skill is intentionally narrow.

Public API base URL:

- default: `https://linktranscriber.store/linktranscriber-api`
- set `LINK_SKILL_API_BASE_URL` only when you need to override that trusted HTTPS origin
- avoid raw IPs and plain HTTP for public use

Optional runtime overrides:

- `LINK_SKILL_API_BASE_URL`
- `LINK_SKILL_SUMMARY_PROVIDER_ID` (default: `deepseek`)
- `LINK_SKILL_SUMMARY_MODEL_NAME` (default: `deepseek-chat`)

Use it to:

- collect a Douyin or Xiaohongshu link
- rely on server-side saved platform cookies when needed
- infer or confirm the platform
- create a transcription task
- poll the task until it succeeds
- call the summaries API
- return only the final summary text to the user

Hard requirements:

- use `https://linktranscriber.store/linktranscriber-api` by default
- do not replace the trusted HTTPS origin with a raw IP unless the operator explicitly sets `LINK_SKILL_API_BASE_URL`
- treat `skill/` in this workspace as the stable source of truth
- do not fall back to `web/skill/` for current product behavior

## When To Use It

Trigger this skill when the user wants to:

- summarize a Douyin link
- summarize a Xiaohongshu link
- get a concise AI-generated summary after transcription
- receive only the final summary output instead of the raw transcription payload

Do not use this skill for:

- YouTube links
- `/api/generate_note`
- returning the full raw transcription JSON by default
- any workflow outside the final summary result

## Required Inputs

This skill needs:

1. `url`
2. `platform`

Infer `platform` when possible:

- `douyin` for `douyin.com` or `v.douyin.com`
- `xiaohongshu` for `xiaohongshu.com` or `xhslink.com`

If the platform cannot be inferred reliably, ask the user to specify `douyin` or `xiaohongshu`.

## Workflow

1. Check whether the user provided `url`.
2. Infer `platform` from the link when possible.
3. If `url` is missing, ask for it and stop.
4. If `platform` cannot be inferred, ask for it and stop.
5. Create a transcription task with `POST /api/service/transcriptions`:

Use `https://linktranscriber.store/linktranscriber-api` by default. If `LINK_SKILL_API_BASE_URL` is set, use that override instead.

```json
{
  "url": "https://...",
  "platform": "xiaohongshu"
}
```

6. Extract `data.task_id` from the creation response.
7. Poll `GET /api/service/transcriptions/{task_id}` until the task reaches a final successful state.
   Keep polling while status is any non-final in-progress value such as:
   `PENDING`, `PARSING`, `DOWNLOADING`, `TRANSCRIBING`, `SUMMARIZING`, `FORMATTING`, `SAVING`.
8. Call `POST /api/service/summaries` with:

```json
{
  "transcription_task_id": "task-id",
  "provider_id": "deepseek",
  "model_name": "deepseek-chat"
}
```

9. Return only `data.summary_markdown` to the user.

The public skill should not ask end users to provide platform cookies by default. Cookie handling belongs to the server-side configuration layer.

## Output Rules

- The final user-facing result should be the summary text only.
- Prefer returning `data.summary_markdown` exactly as produced by the summaries API.
- Do not return raw transcription payload unless the user explicitly asks for debugging details.
- Do not add action cards or custom wrappers around the summary.

## Error Handling

- If `url` is missing, ask for the link.
- If the platform cannot be inferred, ask whether it is `douyin` or `xiaohongshu`.
- If transcription task creation fails, return the upstream error clearly.
- If the upstream service reports missing platform cookies, treat that as a server-side configuration issue.
- If the upstream service reports missing platform cookies, do not redirect that requirement to the end user as the default next step. Explain that the hosted service is missing required cookie configuration.
- If polling ends in failure, return the task error instead of calling summaries.
- If summary generation fails, return the upstream summary API error.

## Example Prompt

Use $link-transcriber to summarize this Xiaohongshu link. I want only the final summary result:

- `url`: `https://xhslink.com/...`
