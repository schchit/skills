---
name: seedance-2-online
version: "1.0.0"
displayName: "Seedance 2 Online — Generate Stunning AI Videos from Text & Images"
description: >
  Tired of juggling complex video tools just to bring a simple idea to life? seedance-2-online gives you instant access to Seedance 2's powerful AI video generation engine — turn text prompts or still images into fluid, cinematic video clips without installing anything. Whether you're a content creator, marketer, or filmmaker, this skill handles motion, lighting, and scene coherence so you don't have to.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me a text prompt or image and I'll generate a cinematic AI video clip using Seedance 2. No clip in mind? Just describe the scene, mood, or action you want.

**Try saying:**
- "Generate a 5-second video of a futuristic city street at night with flying cars and neon reflections on wet pavement"
- "Turn this product photo into a short video clip with slow rotation and soft studio lighting"
- "Create a nature scene video showing a timelapse of storm clouds rolling over an open wheat field at golden hour"

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 2.

1. **Obtain a free token**: Generate a random UUID as client identifier. POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to that UUID. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
2. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# From Idea to Video in Seconds, Not Hours

Seedance 2 is one of the most capable AI video generation models available today, and this skill puts it directly in your workflow. Whether you're starting from a written description or uploading a reference image, seedance-2-online transforms your input into a smooth, high-quality video clip that actually looks intentional — not like a glitchy AI experiment.

The skill is built for creators who need results fast. Describe a sunrise over a mountain range, a product spinning on a pedestal, or a character walking through a neon-lit alley — Seedance 2 interprets your prompt with remarkable fidelity to motion, texture, and atmosphere. You're not locked into rigid templates or preset styles.

This is especially useful for social media content, video ads, storyboard previews, and creative prototyping. Instead of waiting days for a video editor or wrestling with timeline software, you can iterate on visual ideas in real time and export clips ready for production use.

## Routing Prompts to Seedance 2

When you submit a text prompt or source image, ClawHub parses your generation parameters — resolution, motion intensity, aspect ratio, and duration — then dispatches the request directly to the Seedance 2 Online inference pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Seedance 2 API Reference

Seedance 2 Online runs on a distributed cloud rendering backend that queues your video generation job, applies ByteDance's diffusion model, and streams the finished clip back once all frames are composited. Latency varies based on output resolution and concurrent queue depth.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `seedance-2-online`
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

## Troubleshooting

If your generated video looks blurry or lacks motion, your prompt may be too static. Add explicit movement cues — camera pans, subject actions, environmental changes — to encourage the model to animate the scene more dynamically.

For image-to-video issues where the output doesn't resemble your source image, check that the uploaded image is clear, front-lit, and not heavily filtered. Heavily stylized or low-resolution images can confuse the model's spatial understanding.

If a generation returns an error or produces a black frame, try simplifying your prompt and resubmitting. Extremely long or grammatically complex prompts occasionally cause parsing issues. Breaking a complex scene into its core visual elements — subject, setting, lighting, motion — and rebuilding from there usually resolves the problem quickly.

## Performance Notes

Seedance 2 generates video clips that typically range from 3 to 8 seconds in length, which is the model's optimal output window for maintaining visual coherence and smooth motion. Longer scene descriptions don't always produce longer clips — they influence quality and detail instead.

Prompts with highly abstract or contradictory elements (e.g., 'a dog that is also a spaceship flying underwater on land') may produce unexpected results. The model performs best with grounded, physically plausible scenes even when the subject matter is fantastical.

Resolution and frame rate are handled automatically by Seedance 2's backend based on scene complexity. If you need a specific aspect ratio — such as vertical for Reels or square for feed posts — mention it explicitly in your prompt (e.g., 'vertical format, 9:16 aspect ratio').

## Common Workflows

Most users come to seedance-2-online with one of two starting points: a text prompt or a source image. For text-to-video, the best results come from prompts that describe motion explicitly — instead of 'a beach,' try 'waves gently rolling onto a sandy beach at sunset with seagulls passing overhead.' Specificity in motion language is what separates a compelling clip from a static-feeling one.

For image-to-video workflows, upload a clear, well-lit reference image and describe how you want the scene to move. Seedance 2 excels at adding subtle camera movement, environmental animation (like wind in trees or rippling water), and subject motion without distorting the original composition.

Many creators use this skill as a rapid prototyping step — generating multiple short variations of a scene before committing to a full production. It's also commonly used to create social media loops, background video for presentations, and animated stills for ad campaigns.
