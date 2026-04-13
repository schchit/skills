---
name: pixverse-ai
version: "1.0.0"
displayName: "PixVerse AI Video Generator — Create Stunning AI Videos from Text & Images"
description: >
  Tired of spending hours trying to produce cinematic video content without a film crew or budget? PixVerse AI changes that entirely. This skill connects you directly to pixverse-ai's powerful video generation engine, letting you turn text prompts and static images into fluid, high-quality video clips in seconds. Whether you're a content creator, marketer, or storyteller, pixverse-ai handles motion, style, and scene composition automatically — so you focus on the idea, not the execution.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome to your PixVerse AI video studio — where a single sentence can become a cinematic clip. Tell me what you want to create and I'll generate it for you right now!

**Try saying:**
- "Generate a short video of a lone astronaut walking across a red Martian desert at golden hour with dramatic cinematic lighting"
- "Turn this product photo into an animated video clip with slow floating motion and a soft glowing background for an Instagram ad"
- "Create a 5-second video of a futuristic city skyline at night with flying cars and neon reflections on wet streets"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Turn Words and Images Into Cinematic Video Instantly

Creating video content used to mean cameras, editing software, and hours of post-production. PixVerse AI flips that model on its head. With this skill, you describe a scene — or drop in a reference image — and watch it transform into a dynamic, motion-rich video clip ready to share.

The pixverse-ai engine understands creative intent. You can describe mood, movement, camera angles, and visual style in plain language, and the system interprets those cues to produce something that actually looks intentional. Want a slow cinematic pan across a neon-lit cityscape? A product floating in a dreamy abstract space? A character walking through an autumn forest? Just say it.

This skill is built for creators who move fast — social media managers needing eye-catching reels, indie filmmakers prototyping scenes, brands producing short-form ads, or anyone who wants to stop being limited by production resources. PixVerse AI gives you a creative studio in a single conversation.

## How PixVerse Routes Your Prompts

Every request you send — whether it's a text-to-video prompt or an image upload — is parsed and dispatched to the appropriate PixVerse generation pipeline based on your chosen motion style, aspect ratio, and video duration settings.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## PixVerse API Backend Reference

PixVerse processes all video generation jobs on its cloud-based diffusion infrastructure, meaning renders happen server-side and your clip is queued, generated, and returned as a streamable URL — no local GPU required. Generation times vary depending on resolution, motion intensity, and current server load.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `pixverse-ai`
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

## Best Practices for PixVerse AI Video Generation

Getting the most out of pixverse-ai comes down to how you write your prompts. Vague inputs produce vague results — the more specific your description of setting, lighting, motion, and mood, the more precise and cinematic your output will be.

Always include a visual style reference when possible. Phrases like 'shot on 35mm film,' 'soft bokeh background,' 'high contrast noir lighting,' or 'Wes Anderson symmetrical framing' give the model strong aesthetic direction to work with.

For image-to-video tasks, use clean, well-lit source images with a clear subject. PixVerse AI reads the composition of your image and builds motion around it — a cluttered or low-resolution input will limit what it can do. Cropped, portrait-oriented images work especially well for character animation prompts.

Keep your motion descriptions grounded. 'Camera slowly pushes in' works better than 'epic dramatic zoom explosion.' Subtle, intentional motion tends to produce more polished, usable results than over-the-top action descriptors.

## Quick Start Guide — Your First PixVerse AI Video in Minutes

Getting started with pixverse-ai through this skill is straightforward. You don't need any accounts, software, or technical setup — just bring your idea.

Step 1: Write a scene description. Think of it like directing a shot. Include the subject, environment, lighting condition, and any camera movement you want. Example: 'A white ceramic coffee cup on a wooden table, steam rising slowly, warm morning sunlight from the left, shallow depth of field.'

Step 2: Optionally attach a reference image. If you have a product photo, character illustration, or landscape image you want animated, share it alongside your prompt. PixVerse AI will use it as the visual foundation.

Step 3: Specify output intent if relevant. Mention if this is for a social media reel, a presentation loop, a cinematic teaser, or an ad — this context helps shape pacing and style.

That's it. Submit your request and your video will be generated and ready to download or iterate on. If you want changes, just describe what to adjust and we'll regenerate.
