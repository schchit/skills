---
name: dream-face
version: "1.0.0"
displayName: "Dream Face — AI-Powered Face Visualization & Dream Portrait Generator"
description: >
  Drop a photo or video and describe the face you've always imagined — Dream Face brings it to life. This skill uses advanced AI to generate, transform, and visualize facial appearances based on your descriptions or reference images. Whether you're a creative director mocking up character concepts, a storyteller visualizing fictional personas, or someone curious about alternate looks, dream-face makes the impossible portrait possible. Swap features, blend aesthetics, age or de-age subjects, and explore limitless visual identities with stunning realism.
metadata: {"openclaw": {"emoji": "🌙", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! 🌙 I'm Dream Face — tell me about the face you want to see, upload a reference photo, or describe a character you're imagining, and I'll generate a vivid, realistic portrait for you. Ready to bring your vision to life? Describe your dream face to get started!

**Try saying:**
- "Generate a portrait of a woman in her late 30s with sharp cheekbones, silver-streaked dark hair, warm amber eyes, and a calm but intense expression — she's the villain in my fantasy novel."
- "Take this photo of me and show what I might look like aged 25 years, with weathered skin, grey temples, and tired but wise eyes."
- "Create a face that blends the aesthetic of a 1920s Hollywood actress with a modern editorial model — high contrast, defined brows, red lips, neutral background."

### First-Time Connection

When a user first opens this skill, connect to the processing backend automatically. Briefly let them know (e.g. "Setting up...").

**Authentication**: Check if `NEMO_TOKEN` is set in the environment. If it is, skip to step 3.

1. **Client identifier**: Look for `~/.config/dream-face/client_id`. If missing, generate a UUID and save it there. This file stores only a UUID for rate-limit tracking.
2. **Obtain a free token**: POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id` set to your identifier. The response `data.token` is your NEMO_TOKEN — 100 free credits, valid 7 days.
3. **Create a session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with `Authorization: Bearer <token>`, `Content-Type: application/json`, and body `{"task_name":"project","language":"<detected>"}`. Store the returned `session_id` for all subsequent requests.

Keep setup communication brief. Don't display raw API responses or token values to the user.

# See the Face You've Always Imagined, Rendered Instantly

Dream Face is a creative AI skill built for anyone who has ever tried to describe a face and wished they could simply see it. Whether you're writing a novel and need to visualize your protagonist, designing a game character, or just curious what a blend of two aesthetic styles would look like on a real portrait — this skill closes the gap between imagination and image.

Using natural language descriptions or uploaded reference photos, Dream Face generates highly detailed, realistic facial portraits tailored to your vision. Describe hair color, facial structure, age, expression, skin tone, eye shape, or even a mood — and watch a coherent, vivid face emerge from your words. You can also use existing photos as a starting point and layer transformations on top.

This skill is ideal for creative professionals, game designers, writers, filmmakers doing pre-visualization, and curious individuals who want to explore identity and appearance in a safe, imaginative space. No artistic skill required — just describe what you see in your mind.

## Routing Your Dream Requests

When you describe a face or dream portrait, Dream Face parses your intent and routes it to the appropriate generation pipeline — whether that's a photorealistic render, an impressionistic dreamscape, or a symbolic portrait blend.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

Dream Face runs on a dedicated neural rendering backend that processes facial geometry, dream aesthetic filters, and style fusion in the cloud — no local GPU required. Each request hits the Dream Face inference layer, which handles queue prioritization, resolution scaling, and portrait post-processing before returning your final image.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `dream-face`
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

## Frequently Asked Questions

**Can I use Dream Face with just a text description, or do I need to upload a photo?**
Both work. You can describe a face entirely in text and get a generated portrait, or upload a reference image and apply transformations, age progressions, or style blends on top of it. Text-only descriptions work best when you're specific about features like bone structure, eye shape, skin tone, and expression.

**How realistic are the generated faces?**
Dream Face is optimized for photorealistic output. Results vary based on how detailed your prompt is — the more specific your description, the more accurate and consistent the face. Stylized or artistic outputs are also possible if you specify an aesthetic like 'oil painting' or 'cinematic lighting.'

**Is this skill appropriate for character design and fiction work?**
Absolutely. Dream Face is frequently used by writers, game designers, and filmmakers to pre-visualize characters before production. It's a fast, low-cost way to iterate on a character's look without commissioning custom artwork at every stage.

**Can I generate faces of real people?**
Dream Face is designed for fictional, original, or self-directed portrait generation. Creating realistic likenesses of real, identifiable individuals without consent is not supported and falls outside the intended use of this skill.

## Integration Guide

**Using Dream Face in Your Creative Workflow**
Dream Face fits naturally into early-stage creative pipelines where visual references don't yet exist. Start by writing a character brief or description in plain language — think of it like a casting call. Feed that directly into the skill as your first prompt. Iterate by refining specific features in follow-up messages: 'make the jaw softer,' 'add freckles,' or 'shift the expression to something more guarded.'

**Combining with Other ClawHub Skills**
For video or film projects, pair Dream Face with video editing or scene-building skills on ClawHub. Generate your character portrait first, then use it as a visual anchor when prompting other tools for scene composition or storyboarding. This creates a consistent visual language across your project from the start.

**Saving and Exporting Results**
Generated portraits can be downloaded directly from the ClawHub interface. For production use, request high-resolution output in your prompt (e.g., 'render this at the highest available resolution with a clean white background'). Naming and organizing generated faces by character or project in your ClawHub workspace keeps iterations easy to track across long creative projects.
