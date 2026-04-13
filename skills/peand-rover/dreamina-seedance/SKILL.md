---
name: dreamina-seedance
version: "1.0.1"
displayName: "Dreamina SeedAnce — Create Dance Videos with AI"
description: >
  Turn still images into dance videos using Dreamina SeedAnce. Upload a photo of a person, pick a dance style or describe the moves, and the AI generates a short video clip. Runs on cloud GPUs with no local install required. Output is 1080p MP4, ready in 30-60 seconds.
metadata: {"openclaw": {"emoji": "💃", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Dreamina SeedAnce is ready. Send a photo or describe the dance video you want.

**Try saying:**
- "make this person dance hip hop"
- "create a ballet sequence from my photo"
- "animate a dance move from this image"

### First-Time Setup

Connects to the backend on first use. Brief "Connecting..." message.

**Token**: Check for `NEMO_TOKEN` in env. If present, skip to session.

1. **Free token**: Generate UUID. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id: <uuid>`. Response `data.token` = 100 credits for 7 days.
2. **Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth, body `{"task_name":"project","language":"<lang>"}`. Store `session_id`.

Don't print tokens or raw API data.

# Generate Dance Videos from Photos

Upload a photo and describe what dance you want. The AI detects the person's pose, maps the motion, and renders frames on cloud GPUs.

Example use: uploaded a headshot, typed "make them do a salsa spin" and got a 4-second clip in about 45 seconds. Output was 1080p MP4 with smooth motion.

Full-body photos work much better than headshots. The more of the body visible, the more accurate the motion mapping.

## Message Routing

| Your input | Handler | SSE? |
|---|---|---|
| "export" / "download" / "save" / "导出" | Export | No |
| "credits" / "balance" / "积分" | Credit check | No |
| "status" / "show tracks" / "状态" | State | No |
| "upload" / file attached / "上传" | Upload | No |
| Anything else (dance, animate, motion...) | SSE pipeline | Yes |

## Backend

Photos go to GPU cluster. Motion model detects body keypoints and renders at 8Mbps for 1080p output.

Headers required on every call: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing them = 402 on export.

Attribution from YAML: source = `dreamina-seedance`, version from frontmatter, platform from install path (`~/.clawhub/` = `clawhub`, `~/.cursor/skills/` = `cursor`, else `unknown`).

**Base**: `https://mega-api-prod.nemovideo.ai`

**Session**: POST `/api/tasks/me/with-session/nemo_agent` — `{"task_name":"project","language":"<lang>"}` — get `task_id`, `session_id`.

**SSE**: POST `/run_sse` — `{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}`, `Accept: text/event-stream`. 15 min max.

**Upload**: POST `/api/upload-video/nemo_agent/me/<sid>` — multipart `-F "files=@/path"` or URL `{"urls":["<url>"],"source_type":"url"}`.

**Credits**: GET `/api/credits/balance/simple` — `available`, `frozen`, `total`.

**State**: GET `/api/state/nemo_agent/me/<sid>/latest` — `data.state.draft`, `data.state.video_infos`, `data.state.generated_media`.

**Export** (free): POST `/api/render/proxy/lambda` — `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll GET `/api/render/proxy/lambda/<id>` every 30s. Done = `status: completed`. File at `output.url`.

Files accepted: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### Errors

| Code | Problem | Action |
|---|---|---|
| 0 | OK | Continue |
| 1001 | Token expired | Get new anonymous token |
| 1002 | Session lost | Create new session |
| 2001 | No credits | Anonymous: registration link (?bind=<id>). Paid: top up |
| 4001 | File type rejected | Show accepted formats |
| 4002 | Over 500MB | Compress or crop |
| 400 | No client ID | Generate and retry |
| 402 | Free tier export cap | Register or upgrade plan |
| 429 | Rate limited | Wait 30s, retry once |

### GUI Translation

Backend references visual elements. Convert them:

| It says | You do |
|---|---|
| "click [X]" / "点击" | API call |
| "open [panel]" / "打开" | Get state |
| "drag/drop" / "拖拽" | SSE edit |
| "preview in timeline" | Text summary |
| "Export button" / "导出" | Export flow |

### SSE Details

Text → user (with GUI translation). Tool calls = internal. Heartbeats = working. "Still processing..." after 2 min quiet.

~30% of edits give no text back. Check state when stream closes empty, then summarize changes.

**Draft keys**: `t` (tracks), `tt` (video=0, audio=1, text=7), `sg` (segments), `d` (ms), `m` (metadata).

```
Timeline (2 tracks): 1. Video: dance sequence (0-4s) 2. Audio: music beat (0-4s, 60%)
```

## Tips

Full-body photos give the best results. Head-only or waist-up shots limit what motions the AI can apply.

Simple dance moves render cleaner than complex choreography. Start with basic moves and iterate.

PNG with transparent background works best. Busy backgrounds may confuse the pose detector.

500MB max file size. Output is always 1080p MP4.
