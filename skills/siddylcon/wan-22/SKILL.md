---
name: wan-22
version: "1.0.0"
displayName: "WAN 2.2 Video Generator — Create Stunning AI Videos from Text & Images"
description: >
  Drop a text prompt or reference image and watch WAN 2.2 bring it to life as a fluid, cinematic video clip. This skill taps into the wan-22 model to generate short-form video content with remarkable motion coherence and visual fidelity. Whether you're prototyping a scene, building social content, or exploring creative concepts, wan-22 handles everything from dynamic landscapes to character animation stubs — all from a simple description.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! I'm your WAN 2.2 video generation assistant — ready to turn your text prompts or images into smooth, cinematic AI video clips. Tell me what scene you want to bring to life, and let's start generating!

**Try saying:**
- "Generate a 4-second video of a golden retriever running through a sunlit wheat field, slow motion, cinematic depth of field"
- "Create a video from this product image showing it rotating on a sleek dark surface with soft studio lighting"
- "Make a short video clip of a futuristic city skyline at dusk with flying vehicles and neon reflections on wet streets"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# Turn Words and Images Into Moving Scenes

WAN 2.2 is a state-of-the-art video generation model designed to bridge the gap between your imagination and a finished video clip. Unlike older generation tools that produce jittery or incoherent motion, WAN 2.2 focuses on temporal consistency — meaning objects, lighting, and movement flow naturally from one frame to the next.

With this skill, you can generate videos from plain text descriptions, use a starting image as a visual anchor, or combine both for precise creative control. The results are short clips suitable for social media, concept visualization, storyboarding, or simply exploring what AI-generated video looks like at its current frontier.

This skill is built for creators, marketers, indie filmmakers, and curious experimenters who want to move fast. You don't need a production budget or a render farm — just describe what you want to see moving on screen, and WAN 2.2 does the heavy lifting.

## Routing Text and Image Prompts

When you submit a request, ClawHub detects whether you're running a text-to-video or image-to-video generation and routes it to the correct WAN 2.2 inference pipeline automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## WAN 2.2 API Reference

WAN 2.2 processes all generation jobs on a distributed cloud GPU backend, handling diffusion sampling, motion synthesis, and frame rendering remotely so your device never carries the compute load. Generation times vary based on resolution, frame count, and current queue depth.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `wan-22`
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

**Product Visualization:** Attach a product photo and prompt WAN 2.2 to animate it — rotating, zooming, or placing it in a lifestyle context. This is popular for e-commerce teams who need quick video assets without a studio shoot.

**Storyboard Animatics:** Feed WAN 2.2 a sequence of scene descriptions one at a time to generate rough motion clips for each beat of your story. It's not a replacement for full production, but it dramatically accelerates the pre-visualization phase.

**Social Media Content:** Generate looping-style background videos, abstract motion graphics, or short narrative clips tailored to platform formats. Pair a strong visual prompt with a specific aspect ratio note for best results.

**Creative Exploration:** Use WAN 2.2 as a brainstorming tool — generate several interpretations of an abstract concept to discover unexpected visual directions before committing to a full production pipeline.

## Quick Start Guide

Getting your first WAN 2.2 video is straightforward. Start by writing a clear, visual prompt — describe the subject, setting, lighting, camera style, and any motion you want. The more specific you are, the more control you have over the output. For example, instead of 'a car driving,' try 'a red sports car accelerating down a coastal highway at sunset, low camera angle, motion blur on wheels.'

If you have a reference image, attach it alongside your prompt. WAN 2.2 will use it as a visual starting frame and animate outward from there, preserving key visual elements like color palette and composition.

Once you submit, the model processes your request and returns a downloadable video clip. If the result isn't quite right, refine your prompt — try adjusting the motion description, changing the camera perspective, or specifying a mood like 'dramatic,' 'serene,' or 'energetic.' Iteration is fast, so don't hesitate to run multiple variations.
