---
name: vmaker-ai-video-editor-ab-old
version: "1.0.1"
displayName: "Vmaker AI Video Editor — Smart Editing Tools for Fast, Polished Video Output"
description: >
  Getting a clean, edited video out of raw footage takes minutes with vmaker-ai-video-editor-ab-old, not hours of manual cutting and rendering. This skill connects directly to Vmaker's AI-powered editing suite, letting you trim clips, add captions, apply transitions, and export polished videos without touching a timeline manually. The primary use case is rapid video production for screen recordings, tutorials, and short-form content where speed and consistency matter. It handles the repetitive editing decisions so you can focus on what the video actually needs to say.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your Vmaker video link or a description of your footage and I'll edit, caption, or reformat it using vmaker-ai-video-editor-ab-old. No video ready? Just tell me what kind of clip you're working on and we'll plan the edit together.

**Try saying:**
- "I have a 12-minute screen recording in Vmaker — can you remove the silences, add auto-captions, and export it as a 1080p MP4?"
- "Take this tutorial video and cut it down to under 3 minutes by removing filler sections, then add a title card at the beginning."
- "I need this talking-head clip reformatted to 9:16 vertical for Reels, with captions styled in white bold text at the bottom."

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Edit Smarter, Not Harder with Vmaker AI

Vmaker's AI video editor has a lot of capability packed into it — automatic silence removal, caption generation, scene detection, background noise reduction, and more. The vmaker-ai-video-editor-ab-old skill gives you a direct way to tap into those features through conversation, so you can describe what you want done and get it executed without hunting through menus or learning a new interface.

Whether you're editing a screen recording of a product walkthrough, a talking-head tutorial, or a short explainer clip, this skill understands the context of what you're working with and applies the right edits. You can ask it to tighten up pacing, remove filler words, add branded captions, or reformat footage for a specific aspect ratio — all in one workflow.

The result is a production-ready video that looks deliberate and clean, not rushed. It's especially useful when you have a backlog of recordings that need consistent treatment — same caption style, same pacing, same export settings — applied across multiple files without doing each one by hand.

## Routing Edits Through Vmaker AI

When you submit an editing request — whether it's auto-cutting silences, generating subtitles, or applying AI scene transitions — Vmaker AI routes your intent to the appropriate smart editing pipeline based on the detected media type, project timeline state, and selected output preset.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

Vmaker AI's cloud backend handles all render-heavy operations — noise removal, background replacement, auto-reframe, and AI voiceover sync — through distributed processing nodes tied to your account's credit pool. Each API call passes your project token, timeline metadata, and asset references to the processing queue, returning a job ID you can poll for render status.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `vmaker-ai-video-editor-ab-old`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`.

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
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up credits in your account" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register or upgrade your plan to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

## Common Workflows

The most common workflow with vmaker-ai-video-editor-ab-old is the screen recording cleanup pipeline: record a walkthrough or demo, pass it to the skill, and ask for silence removal, auto-captions, and a trimmed intro and outro. This turns a raw 20-minute recording into a tight, watchable 8-minute video in one pass.

Another frequent use case is reformatting long-form content into platform-specific cuts. Give the skill a full-length tutorial and ask it to produce a 60-second highlight clip for LinkedIn, a 15-second teaser for Instagram Stories, and a full version for YouTube — all from the same source file with appropriate aspect ratios and caption adjustments.

For teams producing recurring content like weekly product updates or onboarding videos, vmaker-ai-video-editor-ab-old supports template-style instructions. Describe your standard edit once — specific fonts, caption placement, fade transitions, export resolution — and reuse that instruction set each time you process a new recording to maintain a consistent look across every video.

## Integration Guide

To get started with vmaker-ai-video-editor-ab-old, you'll need an active Vmaker account with at least one video stored in your Vmaker workspace. The skill works by referencing videos via their Vmaker share link or internal project URL — paste that directly into the chat and specify what edits you want applied.

For batch editing workflows, you can supply multiple video links in a single message and define a consistent set of instructions to apply across all of them — useful for processing a series of recorded sessions with the same caption style and export format.

If your video is still in raw recording form and hasn't been processed by Vmaker yet, upload it to your Vmaker dashboard first and allow it to finish processing before passing the link here. The skill reads from Vmaker's processed video data to apply AI edits accurately, so a fully uploaded and indexed file gives the best results.
