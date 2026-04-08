---
name: seedance-2-text-to-video
version: "1.0.0"
displayName: "Seedance 2 Text to Video — Turn Written Prompts Into Cinematic AI Videos"
description: >
  Type a scene, a story beat, or a wild visual idea — and watch it become a real video. This skill uses seedance-2-text-to-video to transform plain text prompts into fluid, high-quality AI-generated clips. Whether you're a content creator storyboarding a concept, a marketer prototyping an ad, or a filmmaker sketching a scene, Seedance 2 delivers motion, mood, and detail from nothing but words.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me a text description of your scene and I'll generate a video clip using Seedance 2. No footage? No problem — just describe what you want and I'll create it from scratch.

**Try saying:**
- "Generate a video of a lone astronaut walking across a red desert planet at sunset, dust swirling around their boots"
- "Create a short clip of a busy Tokyo street at night, neon signs reflecting on wet pavement, people rushing under umbrellas"
- "Make a video of a cozy wooden cabin interior with snow falling outside the window and a fireplace crackling in the foreground"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# From Words on a Page to Video on a Screen

Most video creation starts with expensive gear, editing software, or a production team. Seedance 2 flips that entirely. You write what you want to see — a foggy mountain road at dawn, a neon-lit city street in the rain, a chef plating a dish in slow motion — and the model renders it as a video clip with real cinematic quality.

This skill is built for people who think in scenes but don't have time to produce them. Concept artists can visualize environments before a single asset is built. Social media creators can prototype short-form video ideas in seconds. Educators can illustrate abstract concepts with dynamic visuals instead of static images.

Seedance 2 is particularly strong at maintaining motion coherence and visual consistency across a clip — meaning your generated video doesn't just look like a single frame stretched into motion. Characters move naturally, lighting shifts realistically, and the overall scene holds together as something you'd actually want to use or share.

## Prompt Routing and Generation Flow

When you submit a text prompt, ClawHub parses your cinematic intent and routes the request directly to Seedance 2's text-to-video inference pipeline, selecting the appropriate resolution, motion intensity, and duration parameters based on your input.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Seedance 2 API Reference

Seedance 2 text-to-video generation runs on a distributed cloud backend that handles diffusion sampling, temporal coherence rendering, and frame interpolation server-side — your prompt never needs local GPU resources. Generation jobs are queued asynchronously, so longer clips or higher-resolution outputs may take additional processing time before the video asset is returned.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `seedance-2-text-to-video`
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

## Best Practices

The quality of your seedance-2-text-to-video output is almost entirely determined by the specificity of your prompt. Vague inputs like 'a nice outdoor scene' produce generic results. Specific inputs like 'golden hour light filtering through tall pine trees, camera slowly pushing forward along a dirt trail' give the model clear direction on lighting, motion, and composition.

Include camera movement in your prompts when you want dynamic clips. Words like 'slow zoom,' 'pan left,' 'aerial descent,' or 'handheld tracking shot' signal the kind of motion the video should contain — not just what the scene looks like but how it's framed.

For consistent style across multiple clips, keep your prompt structure similar between generations. If you're building a series of clips for a project, anchor each prompt with the same lighting condition, color palette reference, or shooting style so the outputs feel like they belong together. Treat your prompt like a director's note, not a search query.

## Common Workflows

One of the most popular ways to use seedance-2-text-to-video is for rapid concept visualization. Instead of commissioning storyboard art or sourcing stock footage, teams type out scene descriptions and get usable video references within moments. This works especially well in early-stage creative reviews where the goal is to align on mood and motion rather than final quality.

Another common workflow is social content prototyping. Creators write 2-3 variations of a scene prompt — different lighting, different pacing, different settings — and generate clips for each to see which direction resonates before investing in full production.

Marketers also use this skill to build short atmospheric clips for background use in presentations, landing pages, or video ads where the visual sets a tone rather than tells a story. A single well-written prompt like 'product on a minimalist white surface with soft rolling fog' can produce exactly the kind of polished visual that would otherwise require a studio shoot.
