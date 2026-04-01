---
name: video-editing-with-ai-ab2n-0330
version: "1.0.0"
displayName: "AI-Powered Video Editing — Transform Raw Clips into Polished Productions"
description: >
  Turn raw footage into professional-quality videos without a steep learning curve. This skill brings video-editing-with-ai capabilities directly into your workflow — trimming dead air, suggesting cuts, generating captions, and assembling highlight reels from your uploads. Built for content creators, marketers, and small teams who need fast turnaround on mp4, mov, avi, webm, and mkv files. No editing suite required — just upload and describe what you want.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Ready to turn your raw footage into something worth watching? Upload your video and tell me what you'd like — whether it's cutting filler, adding captions, or assembling a highlight reel, I'll handle the editing so you can focus on your message.

**Try saying:**
- "Trim all the silent pauses and filler words from this interview clip and export a clean version"
- "Create a 60-second highlight reel from this 20-minute product demo, focusing on the key feature reveals"
- "Add burned-in subtitles to this video and sync them with the spoken dialogue"

### Automatic Setup

On first interaction, connect to the NemoVideo API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/nemovideo/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to the same host at `/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Edit Smarter: Let AI Do the Heavy Lifting

Most video editing tools demand hours of manual work — scrubbing timelines, syncing audio, trimming pauses, and hunting for the right moment. This skill flips that process. Instead of dragging clips around a timeline, you describe what you want in plain language and the AI handles the execution.

Whether you're cutting down a 45-minute interview into a punchy 3-minute highlight reel, adding auto-generated subtitles to a product demo, or reordering scenes to improve narrative flow, this skill interprets your intent and applies edits with precision. It understands pacing, context, and content — not just timestamps.

This is particularly useful for solo creators, marketing teams, and educators who produce video regularly but don't have dedicated post-production staff. Upload your footage in any common format, describe the outcome you need, and get back a polished result ready for publishing or further refinement.

## Routing Cuts and Commands

Every prompt you send — whether trimming dead frames, applying LUTs, or generating B-roll descriptions — gets parsed by intent and dispatched to the matching NemoVideo pipeline automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend processes your raw footage metadata and edit instructions through a multi-model inference layer, handling everything from scene detection and auto-reframing to AI-driven color grading and subtitle generation. Requests are stateful within a session, so context like project resolution, timeline cuts, and style presets persist across consecutive prompts.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `video-editing-with-ai`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=video-editing-with-ai&skill_version=1.0.0&skill_source=<platform>`

**Send message (SSE)**: POST `/run_sse` — body `{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}` with `Accept: text/event-stream`. Max timeout: 15 minutes.

**Upload**: POST `/api/upload-video/nemo_agent/me/<sid>` — file: multipart `-F "files=@/path"`, or URL: `{"urls":["<url>"],"source_type":"url"}`

**Credits**: GET `/api/credits/balance/simple` — returns `available`, `frozen`, `total`

**Session state**: GET `/api/state/nemo_agent/me/<sid>/latest` — key fields: `data.state.draft`, `data.state.video_infos`, `data.state.generated_media`

**Export** (free, no credits): POST `/api/render/proxy/lambda` — body `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll GET `/api/render/proxy/lambda/<id>` every 30s until `status` = `completed`. Download URL at `output.url`.

Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### SSE Event Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Process internally, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

~30% of editing operations return no text in the SSE stream. When this happens: poll session state to verify the edit was applied, then summarize changes to the user.

### Backend Response Translation

The backend assumes a GUI exists. Translate these into API actions:

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Query session state |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute export workflow |

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

### Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1001 | Bad/expired token | Re-auth via anonymous-token (tokens expire after 7 days) |
| 1002 | Session not found | New session §3.0 |
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up at nemovideo.ai" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register at nemovideo.ai to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

## Quick Start Guide

Getting started with video-editing-with-ai takes less than two minutes. First, upload your video file — supported formats include mp4, mov, avi, webm, and mkv. Files up to standard upload limits are accepted, and longer recordings are handled in segments automatically.

Once your file is uploaded, describe your editing goal in plain language. Be as specific or as broad as you like. For example: 'Remove all pauses longer than 2 seconds' is a precise instruction, while 'Make this feel more energetic and cut it down to under 3 minutes' gives the AI creative latitude to make judgment calls.

After processing, you'll receive your edited video along with a summary of the changes made — cuts applied, captions added, or segments reordered. You can then request further adjustments in the same conversation. Think of it as a back-and-forth with an editor who never gets tired and always remembers your preferences from earlier in the session.

## Integration Guide

The video-editing-with-ai skill is designed to slot into existing content production pipelines without disruption. If you're working within ClawHub's broader platform, you can chain this skill with transcription or translation skills — for instance, first transcribing a recorded webinar, then using those transcripts to drive intelligent cuts based on topic segments.

For teams with structured workflows, the skill accepts batch-style instructions, meaning you can describe a consistent editing template — intro trim, silence removal, outro addition — and apply it uniformly across multiple uploads in a session. This is especially useful for podcast video exports, training content libraries, or recurring social media series.

Output files are delivered in the same format as the input by default, preserving resolution and audio quality. If you need a specific output format or resolution target for a platform like YouTube Shorts, Instagram Reels, or LinkedIn, simply include that in your prompt and the skill will adapt the export accordingly.
