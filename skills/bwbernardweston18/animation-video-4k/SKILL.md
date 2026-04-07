---
name: animation-video-4k
version: "1.0.0"
displayName: "Animation Video 4K Creator — Render Stunning Ultra-HD Animated Content"
description: >
  Turn your creative concepts into breathtaking animation-video-4k productions with crystal-clear ultra-high-definition output. This skill handles everything from frame interpolation and motion smoothing to color grading and scene composition — all optimized for 4K resolution. Ideal for content creators, studios, and indie animators who demand sharp detail, vibrant color depth, and cinematic quality in every frame.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your animation concept, script, or reference images and I'll help you build a polished 4K animation video. No assets yet? Just describe the scene or style you're going for.

**Try saying:**
- "I want to create a 30-second 4K animated product reveal video for a new sneaker launch — can you help me plan the scene transitions and motion style?"
- "I have a 2D character animation rendered at 1080p and I need guidance on upscaling and optimizing it for 4K output without losing sharpness."
- "Help me create a looping 4K animated background with flowing northern lights and subtle particle effects for use as a live wallpaper."

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Bring Your Animations to Life in True 4K

Creating animation at 4K resolution used to require expensive software, powerful hardware, and hours of rendering time. This skill changes that entirely. Whether you're building a short film, a product explainer, a motion graphic reel, or a looping background animation, the animation-video-4k skill gives you the tools to produce polished, high-resolution results without the steep learning curve.

At its core, this skill is designed to help animators and video creators elevate their work to a professional standard. You can describe a scene, provide reference imagery, or outline a sequence — and the skill will guide you through building out smooth, visually rich animation optimized for 4K display on any screen, from smartphones to 85-inch televisions.

The skill is built for creators at every level. Beginners can describe what they want in plain language and receive structured guidance, while experienced animators can use it to accelerate specific stages of production like timing adjustments, color pipeline decisions, or export format selection. The result is always a 4K-ready animation that looks intentional, polished, and professional.

## Routing Your Animation Render Requests

Each prompt you submit — whether specifying keyframe sequences, motion blur intensity, cel-shading styles, or 4K resolution parameters — is parsed and dispatched to the appropriate rendering pipeline based on animation type and output complexity.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Render API Reference

The backend leverages distributed GPU clusters optimized for ultra-HD frame rendering, handling everything from rigged character animation and particle simulations to procedural texturing at 3840×2160 resolution. Render jobs are queued, processed asynchronously, and returned as fully composited 4K animation sequences with embedded metadata.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `animation-video-4k`
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

## Tips and Tricks

For animation-video-4k projects with lots of motion, enable motion blur on fast-moving elements. At 4K resolution, the extra detail makes motion blur look incredibly realistic and helps the eye track movement naturally — something that looks fine at 1080p can appear jarring and strobing at 4K without it.

When designing text or UI elements for 4K animation, design them at exactly 4K scale from the start. Text that looks crisp at smaller sizes often reveals anti-aliasing issues when blown up to full 4K — use vector-based text rendering whenever your software supports it.

Take advantage of 4K's resolution headroom for creative camera moves. Because you have so many pixels to work with, you can animate a slow digital zoom or pan across a still 4K illustration and it will look like real camera movement — a technique widely used in documentary and explainer animation to add life to static assets without additional animation work.

## Troubleshooting

If your 4K animation output appears blurry or pixelated, the most common cause is a mismatch between your source asset resolution and the 4K export settings. Always ensure your canvas or composition is set to at least 3840x2160 pixels before beginning. Importing 720p or 1080p assets and scaling them up will not produce true 4K quality — start with high-resolution source files wherever possible.

Frame rate inconsistencies are another frequent issue. If your animation looks choppy at 4K, check that your timeline frame rate matches your export frame rate — 24fps, 30fps, or 60fps should be consistent throughout. Mixing frame rates between scenes causes stuttering that becomes more noticeable at higher resolutions.

If rendering times are excessively long, consider breaking your animation into shorter segments and rendering in batches. Large particle systems and complex lighting effects are the biggest performance bottlenecks in 4K animation workflows. Reducing particle count or baking lighting can dramatically cut render time without visible quality loss.

## Best Practices

Always work in a color space that supports the full range of 4K display standards — Rec. 2020 or DCI-P3 are preferred for professional 4K animation video deliverables. Starting in a limited color space and converting later often introduces banding and clipping that is very difficult to correct in post.

Organize your animation project files with a clear folder structure separating assets, compositions, renders, and audio. At 4K resolution, project files grow quickly and disorganized assets lead to broken links and missing textures during final export.

Use proxy workflows during the editing and timing phase. Working with lower-resolution proxies lets you make creative decisions quickly, then swap in full 4K assets only for the final render pass. This approach is standard in professional animation-video-4k production pipelines and saves significant time.

Always export a lossless or near-lossless master file first (ProRes 4444 or DNxHR 444 are solid choices), then compress to your delivery format from that master. Re-compressing an already-compressed 4K file introduces artifacts that are especially visible in smooth gradients and dark scenes.
