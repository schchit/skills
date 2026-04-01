---
name: music-video-maker-bwbe
version: "1.0.0"
displayName: "Music Video Maker BWBE — Create Stunning Sync'd Music Videos from Your Footage"
description: >
  Drop a video clip and describe the vibe you're going for — music-video-maker-bwbe handles the rest. This skill transforms raw footage into polished music videos with beat-synced cuts, visual effects, and cinematic pacing. Upload your clips in mp4, mov, avi, webm, or mkv format, describe your track's energy, and get a professionally styled music video output. Built for artists, content creators, and videographers who want high-impact results without a full editing suite.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm here to help you turn your footage into a real music video using music-video-maker-bwbe. Upload your clip, tell me about the song's energy and style, and let's build something worth watching.

**Try saying:**
- "Take this live performance clip and cut it to feel like a high-energy punk music video with fast cuts and gritty color grading"
- "I have a sunset rooftop session in mp4 — make it look like a cinematic lo-fi music video with warm tones and slow transitions"
- "Edit this dance footage into a music video style with beat-synced cuts and a neon aesthetic"

### Quick Start Setup

This skill connects to NemoVideo's cloud backend. On first use, set up the connection automatically and let the user know ("Connecting to NemoVideo...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Read `~/.config/nemovideo/client_id` or generate a UUID and save it there
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `/api/tasks/me/with-session/nemo_agent` at the same host with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Turn Raw Clips Into Beat-Driven Music Videos

Music-video-maker-bwbe is built for one purpose: taking the footage you already have and shaping it into a music video that actually feels like one. Whether you're an independent artist shooting on a phone or a videographer working with studio-quality clips, this skill bridges the gap between raw material and finished visual storytelling.

The skill analyzes your video content and applies music-video-specific editing logic — tight cuts on the beat, color grading that matches mood, transitions that feel intentional rather than accidental. You describe the energy of your track, and the output reflects it. Dark and moody? High-energy and chaotic? Lo-fi and nostalgic? The skill adapts its approach based on your creative direction.

No timeline scrubbing, no manual keyframing, no render queues. You upload your footage, describe what you need, and music-video-maker-bwbe produces a cohesive visual piece ready for sharing, pitching, or publishing. It's the fastest path from raw clips to a music video that holds attention.

## Routing Your Creative Requests

Every clip upload, beat-sync instruction, and cut request is parsed and routed to the appropriate NemoVideo pipeline stage — whether that's scene assembly, audio waveform alignment, or final render export.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Backend Reference

Music Video Maker BWBE runs on the NemoVideo API, which handles frame-accurate audio sync, multi-clip sequencing, and dynamic cut generation timed to your track's BPM and transients. All render jobs, session tokens, and credit consumption are managed server-side through NemoVideo's infrastructure.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `music-video-maker-bwbe`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=music-video-maker-bwbe&skill_version=1.0.0&skill_source=<platform>`

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
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up at nemovideo.ai" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register at nemovideo.ai to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

## Common Workflows

Most users come to music-video-maker-bwbe with one of three starting points: a single continuous take, multiple short clips from a shoot, or a mix of performance and B-roll footage. Each workflow plays out differently.

For single-take footage, the skill identifies natural movement peaks, facial expressions, and visual anchors to create the illusion of a multi-angle edit. For multi-clip projects, it sequences and trims based on the energy description you provide, building a narrative arc across the material. For performance-plus-B-roll combinations, it intercuts between the two in a way that mirrors professional music video structure.

A typical session looks like this: upload your file (mp4, mov, avi, webm, or mkv), describe the song's genre and mood in plain language, specify any must-keep moments, and receive a cut that reflects your vision. Revision prompts let you push the style further or dial it back without starting over.

## Best Practices

The more specific your description, the better the output from music-video-maker-bwbe. Vague prompts like 'make it look cool' produce generic results. Instead, reference the song's tempo, emotional tone, and any visual references you have in mind — even naming a genre or era helps significantly.

Shoot with editing in mind when you can. Clips with clear movement, varied framing, and at least 10–15 seconds of usable footage give the skill more to work with. Extremely shaky or underexposed footage will limit what's achievable.

If your footage includes dialogue or ambient audio you want preserved, flag that upfront. Music-video-maker-bwbe will treat those moments as anchor points rather than cutting through them. For best color results, upload footage that hasn't already been heavily processed — flat or log profiles give the skill the most flexibility to apply the right grade for your chosen aesthetic.

## Integration Guide

Music-video-maker-bwbe fits naturally into a content production pipeline at the post-production stage. After your shoot is wrapped and your raw files are organized, bring them directly into this skill before any manual editing — it's most effective when working with unprocessed source material.

For artists releasing on platforms like YouTube, Instagram Reels, or TikTok, the skill can be prompted to optimize pacing and aspect ratio for each destination. Mention your target platform in the prompt and the output will reflect those format expectations.

If you're working with a music producer or label, the skill can serve as a rapid visualization tool — producing a rough-cut music video from demo footage before a full production budget is committed. This makes it useful not just for final delivery but for pitching and creative alignment early in the process. Supported formats — mp4, mov, avi, webm, and mkv — ensure compatibility across virtually all camera systems and export pipelines.
