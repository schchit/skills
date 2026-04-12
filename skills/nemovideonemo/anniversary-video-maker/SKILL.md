---
name: anniversary-video-maker
version: "1.0.3"
displayName: "Anniversary Video Maker — Turn Photos & Memories Into Heartfelt Celebration Videos"
description: >
  The most common use for anniversary-video-maker is assembling a slideshow of couple photos, wedding clips, and milestone moments into a polished video with music and captions. It handles photo sequencing, transition timing, text overlays, and audio syncing so you don't have to stitch everything together manually. Whether you're marking a first anniversary or a golden one, this skill helps you produce a shareable video that actually looks intentional rather than thrown together. Works with mixed media inputs including images, short clips, and audio tracks.
metadata: {"openclaw": {"emoji": "💍", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome! Let's build a meaningful anniversary video from the photos and memories you already have. Tell me what you're working with — photos, clips, a song — and let's get started.

**Try saying:**
- "Make a 2-minute anniversary slideshow"
- "Add captions to anniversary photos"
- "Sequence clips for wedding anniversary video"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Turn Scattered Memories Into One Beautiful Anniversary Video

Most people have hundreds of photos and clips scattered across phones and drives but no clean way to turn them into something worth watching. The anniversary-video-maker skill is built specifically for that problem — taking a loose collection of memories and producing a cohesive, emotionally resonant video you can actually share at a party, post online, or give as a gift.

You describe what you have — a set of photos, a date range, a song you love, maybe a few captions you want on screen — and the skill maps out a structure: an opening title card, a chronological or thematic sequence of images, timed transitions, and a closing message. It's not a generic slideshow template; the pacing and layout adapt to how many assets you have and what tone you're going for, whether that's sentimental, celebratory, or somewhere in between.

The output is a ready-to-render video plan or script you can take directly into a video editor or automated rendering tool. You get full control over duration, aspect ratio (vertical for Reels, widescreen for TV), and text style — without needing to know anything about video production.

## Routing Your Video Requests

When you describe your anniversary video — whether it's a 25-year golden celebration or a first-year milestone — your request is parsed for key details like photo count, music mood, and dedication text, then routed to the appropriate rendering pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

Anniversary Video Maker processes your uploaded photos and memory captions through a cloud-based media rendering backend that handles transitions, soundtrack syncing, and title card generation at scale. Each render job is queued, processed asynchronously, and returned as a downloadable MP4 with your chosen aspect ratio and resolution.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `anniversary-video-maker`
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

## Quick Start Guide

Getting your first anniversary video off the ground takes less than five minutes if you come prepared. Start by telling the skill three things: how many photos or clips you have, the length you want the final video to be, and the tone — sentimental, upbeat, nostalgic, romantic. That's the minimum needed to generate a usable structure.

If you have a specific song in mind, mention it early — the skill will time the photo transitions to match the song's approximate BPM and natural breaks like chorus drops or quiet bridges. If you don't have a song yet, describe the mood and you'll get a genre and tempo recommendation you can search for.

For best results, group your photos loosely before you start — early memories, middle years, recent moments. You don't need them in perfect order; just knowing the rough categories helps the skill build a narrative arc rather than a random shuffle. Once you have the structure, you can take it into any video editor — CapCut, DaVinci Resolve, iMovie — or use it with an automated rendering tool.

## Performance Notes

The quality of the output scales directly with the specificity of your input. Vague requests like 'make me an anniversary video' will produce a generic structure. Specific requests — '32 photos, 3-minute runtime, our wedding song is Flightless Bird by Iron & Wine, we want the first 30 seconds to be just the early dating years' — produce a detailed, usable plan with precise timing per photo and labeled segments.

For videos with more than 60 photos, it helps to specify whether you want every photo included or a curated selection. The skill can either fit all assets into the timeline or recommend which ones to cut for pacing. Mixing portrait and landscape photos in the same video works fine — just flag it so the layout accounts for different aspect ratios without cropping faces.

If you're targeting a specific platform — Instagram Reels, YouTube, a TV slideshow at a party — mention it upfront. Vertical 9:16, square 1:1, and widescreen 16:9 each have different pacing norms and text safe zones, and the output will be tailored accordingly.
