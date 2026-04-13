---
name: free-ai-video-generator
version: "1.0.1"
displayName: "Free AI Video Generator — Create MP4 Videos From Text or Images"
description: >
  Built for creators, marketers, and small teams who need videos fast without a $200/month subscription. This free-ai-video-generator skill takes your text prompts or image inputs and turns them into MP4 files, typically under 60 seconds of generation time. You get a ready-to-download file at up to 1080p — no editing background required, and no setup wall blocking you on step one.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> This is the free-ai-video-generator skill — describe what you want and I'll build you an MP4 file. Tell me your topic, preferred length, and aspect ratio to get started.

**Try saying:**
- "Generate a 20-second MP4 video promoting a coffee shop, vertical 9:16 format, warm tones, no voiceover"
- "Create a 15-second explainer video from this product description: [paste text] — output in 1080p landscape"
- "Turn these 4 product images into a 30-second slideshow video with text overlays and background music"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Turn Text Prompts Into Downloadable MP4 Files

Say you need a 15-second product clip but you don't have footage — just a description and a couple of still images. You type in what you want, drop in your assets, and the free-ai-video-generator produces an MP4 you can post directly to Instagram or TikTok.

The skill handles the generation pipeline for you. You're not configuring render settings or picking codecs — you just describe the video in plain language and specify the duration you want, like 10 seconds or 30 seconds.

Output resolution goes up to 1080p. If you need a square 1:1 format for Instagram or a 9:16 vertical for Reels, you specify that in your prompt and the generator applies it before the file is built.

## Input Routing For Video Jobs

The skill parses your prompt or uploaded image, then routes to either a text-to-video or image-to-video generation endpoint based on whether a media attachment is detected in the request.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## GPU Rendering Pipeline Details

When a job is submitted, it's queued on a cloud GPU cluster that renders each MP4 frame using a diffusion model; typical output is a 3–5 second clip at 512×512 or 720p depending on the selected quality tier. Finished files are stored temporarily on a CDN-hosted URL that expires after 24 hours, so download the MP4 before then.

Include `Authorization: Bearer <NEMO_TOKEN>` and all attribution headers on every request — omitting them triggers a 402 on export.

Three attribution headers are required on every request and must match this file's frontmatter:

| Header | Value |
|--------|-------|
| `X-Skill-Source` | `free-ai-video-generator` |
| `X-Skill-Version` | frontmatter `version` |
| `X-Skill-Platform` | auto-detect: `clawhub` / `cursor` / `unknown` from install path |

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`.

**Send message (SSE)**: POST `/run_sse` — body `{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}` with `Accept: text/event-stream`. Max timeout: 15 minutes.

**Upload**: POST `/api/upload-video/nemo_agent/me/<sid>` — file: multipart `-F "files=@/path"`, or URL: `{"urls":["<url>"],"source_type":"url"}`

**Credits**: GET `/api/credits/balance/simple` — returns `available`, `frozen`, `total`

**Session state**: GET `/api/state/nemo_agent/me/<sid>/latest` — key fields: `data.state.draft`, `data.state.video_infos`, `data.state.generated_media`

**Export** (free, no credits): POST `/api/render/proxy/lambda` — body `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll GET `/api/render/proxy/lambda/<id>` every 30s until `status` = `completed`. Download URL at `output.url`.

Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### Error Codes

- `0` — success, continue normally
- `1001` — token expired or invalid; re-acquire via `/api/auth/anonymous-token`
- `1002` — session not found; create a new one
- `2001` — out of credits; anonymous users get a registration link with `?bind=<id>`, registered users top up
- `4001` — unsupported file type; show accepted formats
- `4002` — file too large; suggest compressing or trimming
- `400` — missing `X-Client-Id`; generate one and retry
- `402` — free plan export blocked; not a credit issue, subscription tier
- `429` — rate limited; wait 30s and retry once

### Backend Response Translation

The backend assumes a GUI exists. Translate these into API actions:

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Query session state |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute export workflow |

### Reading the SSE Stream

Text events go straight to the user (after GUI translation). Tool calls stay internal. Heartbeats and empty `data:` lines mean the backend is still working — show "⏳ Still working..." every 2 minutes.

About 30% of edit operations close the stream without any text. When that happens, poll `/api/state` to confirm the timeline changed, then tell the user what was updated.

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

## Common Workflows

The most common thing people use free-ai-video-generator for is social content — specifically, turning a written post or product description into a short video that actually stops the scroll. You paste in 2-3 sentences about your product, pick a 15-second duration, and walk away with an MP4.

Another workflow that comes up constantly: repurposing blog content. Take a 500-word article, pull the 3 key points, and feed those to the generator as your script. It builds a video around those points, usually in under 90 seconds of processing time.

Teams running ads also use it to test concepts before spending money on a real shoot. You generate a rough 10-second MP4 with the core message, run it as a dark post on Facebook, and check the click-through rate before committing to a full production budget.

## Quick Start Guide

Start with a single sentence describing your video. Something like: 'A 20-second video about a new running shoe, upbeat music, 1080p, landscape format.' That's enough for free-ai-video-generator to produce a first draft MP4.

If the first output isn't right, don't rewrite the whole prompt. Change one variable — swap the duration from 20 seconds to 10, or switch from landscape to 9:16 — and regenerate. Targeted edits give you cleaner results than starting over.

Once you have an MP4 you like, check the file before posting anywhere. Open it on your phone, not just your desktop, because text overlays that look fine at 1920x1080 on a monitor sometimes get cut off on a 390px-wide phone screen. Fix it at this stage, not after you've already scheduled the post.

## Integration Guide

You don't need to connect an external API or authenticate anything to use this skill on ClawHub. The free-ai-video-generator runs directly inside the chat interface — you describe what you want, and the skill handles the request.

If you're pulling this into a content calendar, the fastest approach is batching. Write out 5 video descriptions in a single message, each with its own duration and format spec (say, three 1080p landscape files and two 9:16 verticals), and send them together. You'll get 5 separate MP4 download links back instead of running 5 individual sessions.

For teams sharing access, the generated MP4 links stay active for 48 hours by default. Download them to your shared drive — Google Drive, Dropbox, wherever — before that window closes.
