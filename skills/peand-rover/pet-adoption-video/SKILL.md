---
name: pet-adoption-video
version: "1.0.4"
displayName: "Pet Adoption Video Creator — Craft Heartfelt Videos That Get Pets Adopted Faster"
description: >
  Tired of manually piecing together shelter footage and struggling to write captions that actually move people to adopt? The pet-adoption-video skill helps rescue groups, shelters, and foster families produce compelling adoption videos with the right structure, storytelling flow, and emotional hooks. From scripting a 60-second reel to writing on-screen text for a senior dog's profile, this skill handles the creative heavy lifting so more animals find homes.
metadata: {"openclaw": {"emoji": "🐾", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome to your pet adoption video assistant — let's create a video that helps this animal find their forever home! Share the pet's details, any footage or photos you have, and what platform you're posting to so we can get started.

**Try saying:**
- "Write a 60-second adoption video script for a 3-year-old shy tabby cat named Miso who loves blankets and slow mornings"
- "Give me a scene-by-scene outline for a foster dog's Instagram Reel that highlights her playful side and good behavior with kids"
- "Create on-screen text and caption ideas for a senior beagle's adoption video that addresses common concerns about older dogs"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Turn Shelter Footage Into Adoption-Ready Stories

Every animal in a shelter deserves a video that shows their real personality — not just a shaky clip with no context. The pet-adoption-video skill helps you build videos that tell a pet's story in a way that resonates with potential adopters scrolling through social media or a rescue organization's website.

Whether you're working with raw footage from a phone, a set of photos, or just a written description of the pet, this skill helps you shape it into a structured, emotionally engaging video concept. You'll get scene-by-scene outlines, caption suggestions, voiceover scripts, and on-screen text ideas tailored to the specific animal — their breed, age, quirks, and adoption needs.

This is especially useful for small rescues and foster networks that don't have a dedicated media team. Instead of spending hours figuring out what to say or how to sequence clips, you can focus on the animals while this skill handles the storytelling framework that drives real adoption outcomes.

## How Your Video Requests Flow

When you describe a pet's personality, story, or shelter details, the skill routes your request to the appropriate video template engine — whether that's a tearjerker rescue narrative, an upbeat playful profile, or a senior pet spotlight.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Backend API Reference

Pet adoption video processing runs through ClawHub's media rendering pipeline, which stitches together shelter-provided footage, AI-generated captions, and adoption call-to-action overlays in the cloud — no local rendering required. Heavy tasks like b-roll sequencing and voiceover sync are handled server-side so your final shareable video is ready in seconds.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `pet-adoption-video`
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

Most users come to this skill with one of three starting points: raw footage they need to structure, a pet profile they want to turn into a video concept, or a finished video that needs better captions and on-screen text.

For footage-based projects, share a description of what clips you have — length, what the pet is doing, the setting — and the skill will suggest a scene order, transition cues, and a voiceover or text overlay script that fits the footage you've already captured.

For profile-to-video workflows, paste in the pet's shelter bio or foster notes and specify the platform (TikTok, Instagram, Facebook, rescue website). You'll get a tailored script with an emotional opening hook, a middle section showcasing personality, and a clear call-to-action that tells viewers exactly how to adopt.

For caption and overlay work, share your existing video concept or rough cut description and the skill will generate platform-optimized captions, hashtag suggestions, and on-screen text timed to key moments in the video.

## Quick Start Guide

Getting your first pet adoption video script takes less than two minutes. Start by telling the skill three things: the pet's basic info (name, species, breed, age), their standout personality traits or backstory, and where the video will be posted.

From there, specify the video length you're targeting. A 15-30 second TikTok needs a very different structure than a 2-minute Facebook feature video. If you're unsure, ask the skill to recommend a format based on the platform and the pet's story.

Once you have a script or outline, you can ask for variations — a more upbeat tone for a playful puppy, a gentler and slower-paced version for a timid or special-needs animal. You can also request separate versions for different platforms from the same core content, so one session can produce assets for Instagram, TikTok, and your rescue's website all at once.
