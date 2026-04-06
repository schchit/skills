---
name: whisk
version: "1.0.0"
displayName: "Whisk — AI-Powered Video Style Remixer That Transforms Your Footage"
description: >
  Drop a video and describe the look you're after — Whisk reads your footage and remixes its visual style, pacing, and mood on the fly. Whether you want to turn a flat travel clip into a cinematic reel or give a product demo a punchy editorial feel, Whisk handles the creative heavy lifting. Key features include style transfer, tone adjustments, and rhythm-matched cuts. Built for content creators, marketers, and social editors. Supports mp4, mov, avi, webm, and mkv.
metadata: {"openclaw": {"emoji": "🌀", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Whisk is ready to remix your video's style, pacing, and mood based on your creative direction. Drop your clip and tell me the look you're going for — let's transform your footage.

**Try saying:**
- "Make this travel vlog feel more cinematic — warmer tones, slower cuts, and a golden hour mood"
- "Turn this product demo into a fast-paced social ad with punchy cuts and a high-energy feel"
- "Give this interview clip a clean, editorial look — neutral tones, tight pacing, professional vibe"

### Getting Connected

Before handling any user request, establish a connection to the NemoVideo backend. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Ensure a client identifier exists at `~/.config/nemovideo/client_id` (create one as a UUID if needed)
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Remix Your Video's Look Without Starting Over

Most video editing tools ask you to make decisions upfront — pick a template, choose a filter, drag a preset. Whisk works differently. You bring your existing footage, describe the vibe you want, and Whisk figures out how to get you there. It reads what's already in your video — the lighting, the cuts, the energy — and reshapes it around your creative direction.

This isn't about slapping a color grade on top. Whisk analyzes the structure and pacing of your clip, then applies style changes that feel intentional rather than cosmetic. Want a moody, slow-burn feel for a behind-the-scenes video? A fast, punchy rhythm for a product launch? Whisk translates those descriptions into real edits.

It's designed for people who have good footage but need help making it look the way they imagined. Solo creators, small marketing teams, and social media editors all use Whisk to close the gap between what they shot and what they envisioned — without needing a full post-production pipeline.

## How Whisk Routes Your Requests

When you drop a style prompt or upload footage, Whisk parses your intent and routes it to the matching remix pipeline — style transfer, motion restyle, or frame interpolation — based on keywords and clip metadata.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

Whisk runs on the NemoVideo backend, which handles frame-level diffusion rendering and temporal consistency across your clip. Every remix job is queued as a NemoVideo task, so render times scale with clip length and style complexity.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `whisk`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=whisk&skill_version=1.0.0&skill_source=<platform>`

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

A typical Whisk session starts with uploading your clip — mp4, mov, avi, webm, or mkv all work — and describing the style outcome you want. Be as specific or as loose as you like: 'make it feel like a 90s music video' works just as well as 'cooler tones, tighter cuts, more contrast.'

From there, Whisk processes the footage and returns a remixed version. Many users iterate once or twice — asking for more warmth, a slightly faster pace, or a different energy in the opening seconds. The back-and-forth is fast, so refining toward the final look doesn't take long.

For teams, a common workflow is to run the same clip through Whisk with two or three different style prompts, then compare outputs before deciding which direction to develop further. This makes Whisk useful not just as a finishing tool but as a creative exploration step early in the editing process.

## Use Cases

Whisk fits naturally into a range of creative workflows. Travel and lifestyle creators use it to elevate raw footage shot on phones or entry-level cameras — describing a cinematic or documentary feel and letting Whisk reshape the edit accordingly. Marketing teams drop in product videos and ask for style variations to test across different platforms, getting a punchy Instagram cut and a slower, more polished LinkedIn version from the same source clip.

Event videographers use Whisk to quickly reframe highlight reels — shifting tone between emotional and energetic depending on the client. Educators and course creators use it to make talking-head footage feel more engaging without reshooting. Whisk is also popular among social media managers who need to repurpose a single video into multiple formats and moods without hiring an editor for each variation.
