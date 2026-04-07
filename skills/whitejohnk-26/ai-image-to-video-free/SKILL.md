---
name: ai-image-to-video-free
version: "1.0.0"
displayName: "AI Image to Video Free — Animate Still Photos Into Stunning Motion Clips"
description: >
  Drop a still photo and watch it come alive — this skill uses ai-image-to-video-free technology to transform static images into fluid, cinematic video clips without any cost. Whether it's a portrait, landscape, product shot, or illustration, describe the motion you want and get a natural-looking animation in seconds. Built for creators, marketers, and storytellers who want professional results without a subscription.
metadata: {"openclaw": {"emoji": "🎞️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me a still image and describe the motion you want, and I'll generate a free AI-animated video clip from it — no image yet? Just describe a scene and I'll work from that.

**Try saying:**
- "Here's a photo of a mountain lake at sunset — can you animate it so the water ripples gently and the clouds drift slowly across the sky?"
- "I have a product photo of a sneaker on a white background. Make a short video where it slowly rotates 360 degrees to show all angles."
- "This is a portrait of a woman outdoors. Can you create a video where her hair moves slightly in the breeze and the background has a soft bokeh shimmer?"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Turn Any Still Image Into a Living, Breathing Video

Still images capture a moment, but video tells a story. This skill bridges that gap by taking any photo you provide and generating smooth, realistic motion from it — panning across a landscape, animating a portrait's subtle expressions, or bringing product details into dynamic focus.

Using this tool, you describe the kind of movement or atmosphere you want, and the skill handles the rest. Want clouds drifting across a sunset photo? A model's hair swaying gently in the wind? A product rotating elegantly on a shelf? Just say so. The output is a short video clip ready to share on social media, embed in a presentation, or use in a larger project.

This is especially useful for content creators working on tight budgets, small business owners who want eye-catching visuals without hiring a production team, and social media managers who need fresh video content daily. No advanced editing knowledge required — just upload your image, describe your vision, and let the skill do the heavy lifting.

## Routing Your Animation Requests

When you submit a still photo for animation, your request is parsed for motion style, duration, and output resolution before being dispatched to the appropriate image-to-video inference pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

All frame interpolation and temporal coherence rendering runs on distributed GPU clusters via the AI Image to Video Free backend, meaning your local device handles zero heavy lifting. Keyframe synthesis, motion vector estimation, and video encoding happen entirely in the cloud before the final clip is streamed back to you.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-image-to-video-free`
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

## Troubleshooting Common Issues

If the generated video doesn't match the motion you described, try being more specific in your prompt. Instead of 'make it move,' say 'slow pan from left to right with a slight zoom in on the subject.' The more directional and descriptive your instruction, the more accurate the output.

If the animation looks unnatural or glitchy around edges — particularly with portraits or objects that have complex outlines — try uploading a higher-resolution image with a clean background. Low-contrast or heavily compressed images can confuse the motion generation process.

For product images, make sure the subject is centered and well-lit. If you're animating a landscape and the horizon looks warped, specify that the camera movement should be horizontal only with no tilt. Iterating with small prompt adjustments usually resolves most visual artifacts within one or two tries.

## Use Cases for AI Image to Video Free

This skill shines across a surprisingly wide range of real-world scenarios. Social media managers use it to repurpose static brand photography into short Reels or TikToks without reshooting content. E-commerce sellers animate product images to show texture, dimension, and detail that flat photos miss — leading to higher engagement and click-through rates.

Photographers and digital artists use it to add a cinematic layer to their portfolios, turning a single compelling image into a looping video that feels alive. Educators and presenters drop historical photos or infographic images into this skill to create attention-grabbing slides that move.

Bloggers and newsletter writers who want to embed video without producing full shoots rely on this skill to generate quick, polished clips from existing image assets. Whether your goal is storytelling, marketing, or simply standing out in a crowded feed, animating your still photos is one of the fastest ways to upgrade your content output.
