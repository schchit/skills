---
name: wan-ai
version: "1.0.0"
displayName: "WAN AI Video Generator — Create Stunning AI Videos from Text & Images"
description: >
  Turn your ideas into cinematic video clips with wan-ai, the powerful video generation model built for creators who need results fast. wan-ai transforms text prompts and still images into fluid, high-quality video sequences with remarkable motion consistency. Whether you're producing social content, concept visualizations, or product demos, this skill brings the full capability of WAN AI to your fingertips — no timeline editing, no rendering queues, just describe and generate.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me a text prompt or image and I'll generate a video clip using wan-ai right now. No idea yet? Just describe a scene, a mood, or a subject and I'll handle the rest.

**Try saying:**
- "Generate a video of a lone astronaut walking across a red desert planet at sunset, slow cinematic camera push-in, dust particles in the air"
- "Turn this product photo of a perfume bottle into a short video with soft light ripples and a rotating reveal effect"
- "Create a 4-second clip of a dense forest with morning fog drifting through the trees, birds flying up from the canopy, realistic lighting"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# From Prompt to Video in Seconds

WAN AI is one of the most capable open-source video generation models available, and this skill puts it directly into your workflow. Whether you start with a text description or an existing image, wan-ai produces smooth, visually coherent video clips that hold up to real creative scrutiny — not just demo-reel magic.

Describe a scene, a mood, a camera movement, or a character in motion, and watch wan-ai interpret your intent into actual footage. The model handles temporal consistency exceptionally well, meaning objects and subjects don't randomly warp or flicker between frames the way earlier video AI models often did.

This skill is designed for content creators, marketers, indie filmmakers, game developers, and anyone who needs video assets without the overhead of a full production setup. Use it to prototype ideas quickly, generate B-roll, visualize scripts, or produce short-form social videos that actually look intentional and polished.

## Routing Text and Image Prompts

Each request is parsed to determine whether you're triggering a text-to-video generation, an image-to-video animation, or a style-transfer task, then dispatched to the appropriate WAN AI pipeline automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## WAN AI Cloud API Reference

WAN AI processes all diffusion jobs on distributed cloud inference nodes, meaning your prompts, motion parameters, and reference frames are handled server-side with no local GPU required. Generation latency depends on model variant — WAN 2.1 standard versus turbo — and current queue depth.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `wan-ai`
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

The most common way to use wan-ai is the text-to-video workflow: write a detailed scene description including subject, environment, lighting, camera behavior, and mood, then generate. The more specific your prompt, the more controlled the output — vague prompts produce interesting results but detailed prompts produce usable ones.

Image-to-video is equally powerful. Drop in a still photo or illustration and describe what motion should occur — a character turning their head, a product rotating, a landscape coming alive with wind and movement. WAN AI will animate it while preserving the visual identity of the source image.

For iterative work, generate a clip, review what worked, then refine the prompt and regenerate. Most creators treat the first output as a draft rather than a final product. Adjust motion intensity, camera style, or scene details between rounds to dial in exactly what you need.

## Use Cases

Social media creators use wan-ai to generate eye-catching video content for Reels, TikToks, and YouTube Shorts without filming anything. A strong text prompt can produce scroll-stopping visuals in under a minute.

Marketers and brand teams use it for concept visualization — showing stakeholders what a campaign might look like before committing to a full production budget. It's faster than storyboarding and more convincing than static mockups.

Game developers and concept artists use wan-ai to generate environment flythrough clips, character motion previews, and atmosphere tests for pitches or internal reviews.

Filmmakers use it for pre-visualization — generating rough versions of planned shots to communicate vision to crew, or to experiment with angles and staging before shoot day. It's also useful for generating abstract or VFX-heavy sequences that would be prohibitively expensive to produce practically.

## Quick Start Guide

To get your first video from wan-ai, start with a single clear scene description. Include: what the subject is, where it is, what it's doing, and what the camera is doing. Example: 'A red fox sitting in a snow-covered forest clearing, looking directly at camera, soft overcast light, slow zoom in, photorealistic.'

If you have a source image, attach it and describe the motion you want applied — keep motion descriptions grounded in physics for best results (things that could plausibly move in real life tend to animate more cleanly).

Avoid overly long prompts with conflicting instructions. If you want multiple scenes, generate them separately and combine in post. For stylistic control, include references to visual styles, film stocks, or directors whose aesthetic you want to evoke — wan-ai responds well to these kinds of qualitative cues.

Once you have a clip you like, use it as-is or bring it into your editing software for trimming, color grading, and sound design.
