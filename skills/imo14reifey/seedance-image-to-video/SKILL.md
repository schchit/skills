---
name: seedance-image-to-video
version: "1.0.0"
displayName: "Seedance Image to Video — Animate Still Photos Into Fluid AI Videos"
description: >
  Tired of static images that fail to capture attention in a scroll-heavy world? seedance-image-to-video transforms your still photos and artwork into smooth, cinematic AI-generated videos in seconds. Upload any image — a portrait, landscape, product shot, or illustration — and watch it come alive with natural motion. Perfect for content creators, marketers, social media managers, and designers who want eye-catching video content without filming a single frame.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome! I can animate any still image into a smooth, AI-generated video using Seedance Image to Video. Drop your photo and tell me what kind of motion or mood you're after — let's bring it to life!

**Try saying:**
- "Animate my product photo with motion"
- "Turn landscape photo into video"
- "Bring this portrait to life"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Turn Any Photo Into a Living, Breathing Video

Static images are forgettable. Videos stop the scroll. Seedance Image to Video bridges that gap by taking your existing photos and generating fluid, AI-powered video clips that feel genuinely cinematic — no camera, no studio, no editing timeline required.

Whether you're working with a product photograph you want to animate for an ad, a portrait you'd like to bring to life, or a piece of digital art you want to showcase in motion, this skill handles the heavy lifting. You simply provide the image, describe the motion or mood you're going for, and receive a ready-to-share video clip.

This is especially powerful for social media content, where video consistently outperforms static posts across every major platform. Instead of sourcing stock footage or hiring a videographer, you can generate polished motion content directly from your existing image library — saving hours of production time while maintaining full creative control over the look and feel.

## Routing Your Animation Requests

When you submit a still image with a motion prompt, Seedance parses your intent and routes the request to the appropriate video generation pipeline based on resolution, motion intensity, and clip duration parameters.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Seedance API Backend Reference

Seedance Image to Video runs on a cloud-based diffusion backend that processes your source frame and motion descriptor to synthesize temporally consistent video output — no local GPU required. Frame interpolation and motion flow are handled server-side, so render times depend on queue load and selected output quality tier.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `seedance-image-to-video`
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

## Quick Start Guide — Your First Image to Video in Minutes

Getting started with seedance-image-to-video is straightforward. First, select the image you want to animate — this can be a JPEG, PNG, or similar format. Make sure it's the best available resolution you have.

Next, write a short motion description alongside your image. Think about: direction of movement (zoom in, pan left, rotate), atmosphere (stormy, calm, energetic), and any specific elements you want animated (hair, water, clouds, smoke). A single focused sentence is often enough to get a strong result.

Once you send the image and prompt, the skill will process your request and return a generated video clip. Review the output — if the motion feels too subtle or the direction is off, simply reply with an adjustment like 'make the zoom slower' or 'add more wind movement to the trees.' Iteration is fast, so don't hesitate to refine until it matches your vision.

## Best Practices for Seedance Image to Video

The quality of your output depends heavily on both the source image and how clearly you describe the desired motion. Start with high-resolution images — blurry or low-quality photos will produce noticeably softer video results. Sharp edges, good lighting, and clear subjects give the AI the most to work with.

When describing motion, be specific rather than vague. Instead of saying 'make it move,' try 'add a slow parallax zoom with the foreground drifting slightly left.' The more directional and atmospheric your prompt, the more intentional the final video will feel.

For product and commercial use cases, neutral or gradient backgrounds tend to animate more cleanly than busy, cluttered scenes. If your image has a complex background, consider describing the motion focus on the subject itself — for example, 'keep the background static while the product rotates gently.' This helps the AI prioritize where the movement should live.
