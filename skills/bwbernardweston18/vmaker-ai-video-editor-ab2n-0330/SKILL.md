---
name: vmaker-ai-video-editor-ab2n-0330
version: "1.0.0"
displayName: "Vmaker AI Video Editor — Edit, Enhance & Export Videos Automatically"
description: >
  Turn raw footage into polished, publish-ready videos without spending hours in a timeline. The vmaker-ai-video-editor skill brings intelligent editing to your workflow — trimming dead air, adding captions, syncing cuts to rhythm, and applying scene-aware enhancements. Built for content creators, marketers, and teams who need fast turnaround without sacrificing quality. Works with mp4, mov, avi, webm, and mkv files.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Ready to turn your raw footage into something worth sharing? Drop your video file and tell me what kind of edit you're looking for — I'll use Vmaker AI Video Editor to trim, enhance, and shape it into exactly what you need. What are we working on today?

**Try saying:**
- "Take this 45-minute Zoom recording and cut it down to a 10-minute highlight reel, removing filler words and long pauses."
- "Add auto-generated captions to my product demo video and sync them with the speaker's voice."
- "Edit this raw interview footage into a punchy 60-second social media clip with a clean intro and outro."

### First-Time Connection

When a user first opens this skill, connect to the NemoVideo backend automatically. Briefly let them know (e.g. "Connecting to NemoVideo...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 3.

1. **Client identifier**: Look for `~/.config/nemovideo/client_id`. If missing, generate a UUID and save it there. This file stores only a UUID for rate-limit tracking.
2. **Obtain a free token**: POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to your identifier. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
3. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Smart Video Editing That Actually Understands Your Footage

Most video editing tools make you do the work — scrubbing through timelines, manually placing cuts, hunting for the right moment. The Vmaker AI Video Editor skill flips that experience. You bring the footage, describe what you want, and the skill handles the heavy lifting: identifying the best takes, removing awkward pauses, and assembling a coherent edit that matches your intent.

Whether you're turning a 30-minute screen recording into a tight 5-minute tutorial, or transforming a shaky product demo into something you'd actually post on LinkedIn, this skill adapts to your content type. It understands context — interviews get different treatment than product showcases, and social clips get optimized differently than long-form YouTube content.

Vmaker AI Video Editor is especially useful for solo creators and small marketing teams who don't have a dedicated editor on staff. Instead of outsourcing or spending a weekend cutting clips, you can describe your vision in plain language and get a structured, ready-to-export result in a fraction of the time.

## Routing Edits and Enhancements

When you describe a cut, caption, background music swap, or AI enhancement, Vmaker AI maps your intent to the matching NemoVideo endpoint and fires the request automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Under the Hood

Vmaker AI Video Editor is powered by the NemoVideo backend, which handles timeline processing, AI scene detection, auto-captioning, and render jobs through a secure token-based API. Every trim, enhance, or export command you issue gets translated into a structured NemoVideo API call behind the scenes.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `vmaker-ai-video-editor`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=vmaker-ai-video-editor&skill_version=1.0.0&skill_source=<platform>`

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

Getting started with the Vmaker AI Video Editor skill is straightforward. Begin by uploading your video file — supported formats include mp4, mov, avi, webm, and mkv. Files under 2GB tend to process fastest, so if you're working with long recordings, consider trimming the source to the relevant section before uploading.

Once your file is in, describe your editing goal in plain language. Be specific about the output you want: mention the target duration, the platform it's headed for (YouTube, Instagram, LinkedIn), the tone (professional, casual, energetic), and any must-keep moments. The more context you give, the more accurate the edit.

After the skill processes your request, you'll receive an edited version along with a summary of what was changed — cuts made, captions added, enhancements applied. You can then request adjustments in a follow-up message, such as tightening a specific section or changing the pacing of the intro.

## Best Practices

For the cleanest results with Vmaker AI Video Editor, start with the highest quality source file you have. Compressed or heavily artifacted videos limit what the AI can do — original exports from your camera or screen recorder always outperform re-exported copies.

When writing your editing prompt, avoid vague instructions like 'make it better.' Instead, anchor your request to a specific outcome: 'Remove all sections where the presenter is not speaking,' or 'Keep only the product demonstration portion and cut the Q&A.' Specificity translates directly into edit accuracy.

If you're producing content for multiple platforms from the same source clip, process them as separate requests with platform-specific instructions rather than asking for everything at once. A 16:9 YouTube cut and a 9:16 Reels version require different framing and pacing decisions, and treating them individually gives you tighter control over each output.
