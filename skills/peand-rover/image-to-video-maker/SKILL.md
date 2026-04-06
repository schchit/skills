---
name: image-to-video-maker
version: "1.0.0"
displayName: "Image to Video Maker — Transform Still Photos Into Dynamic Video Slideshows"
description: >
  Tired of static photos sitting in folders, never getting the attention they deserve? The image-to-video-maker skill on ClawHub breathes life into your still images by converting them into polished, shareable videos — no editing software required. Upload your photos, set your preferred duration and transitions, and get back a smooth video ready for social media, presentations, or personal projects. Supports mp4, mov, avi, webm, and mkv output formats. Perfect for content creators, marketers, photographers, and anyone who wants to turn a photo collection into a compelling visual story.
metadata: {"openclaw": {"emoji": "🎞️", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Ready to turn your photos into a video that actually gets watched? Share your images and tell me how you'd like your video to look — let's build something great together.

**Try saying:**
- "Turn these 12 product photos into a 30-second promotional video with smooth fade transitions"
- "Create a travel video slideshow from my vacation photos, showing each image for 3 seconds with a cinematic feel"
- "Make a birthday tribute video using these 20 family photos, ordered chronologically with gentle transitions"

### Quick Start Setup

This skill connects to NemoVideo's cloud backend. On first use, set up the connection automatically and let the user know ("Connecting to NemoVideo...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Read `~/.config/nemovideo/client_id` or generate a UUID and save it there
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `/api/tasks/me/with-session/nemo_agent` at the same host with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Turn Your Best Photos Into Videos Worth Watching

Most people have hundreds of photos that never get shared simply because a single image doesn't tell the whole story. The image-to-video-maker skill changes that by stitching your still photos together into a flowing video that captures attention and communicates a narrative — whether it's a travel recap, a product showcase, a real estate walkthrough, or a family memory reel.

With this skill, you stay in control of the creative direction. You can specify how long each image should appear on screen, choose the order photos are displayed, and describe the mood or pacing you're going for. The result is a video that feels intentional and professional, not like an auto-generated slideshow from a decade-old app.

This tool is built for real-world use cases: social media content creators who need quick turnaround, small business owners showcasing products without a video budget, photographers delivering client galleries in a new format, and everyday users who just want to make something memorable. Whatever your reason, image-to-video-maker gets you from a folder of photos to a finished video in minutes.

## Routing Your Slideshow Requests

Each request — whether you're uploading photos, setting transition styles, adjusting timing, or exporting your final video — is parsed and routed to the matching NemoVideo endpoint based on the action type detected in your message.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend handles frame sequencing, Ken Burns motion effects, transition rendering, and audio sync to stitch your still images into a polished video slideshow. All processing happens server-side, so output quality and render speed depend on your active NemoVideo plan tier.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `image-to-video-maker`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=&task=<task_id>&session=<session_id>&skill_name=image-to-video-maker&skill_version=1.0.0&skill_source=<platform>`

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

## FAQ

**How many images can I include in one video?** There's no hard cap, but for smooth performance and a watchable result, most users work with between 5 and 60 images per video. Very large batches may benefit from being split into segments.

**Can I add music or audio to my image video?** Yes — you can describe the type of background music you want, or mention if you'd like a silent video. If you have a specific audio file in mind, note that in your prompt.

**What aspect ratio will the video be?** By default, the output is optimized for landscape (16:9), which works well for most platforms. If you need a square (1:1) format for Instagram or vertical (9:16) for TikTok or Reels, just specify that in your request.

**Will the skill work with screenshots or graphics, not just photos?** Absolutely. The image-to-video-maker handles any still image file — photographs, illustrations, screenshots, infographics, or design mockups all work as source material.

## Troubleshooting

**Images appear out of order in the final video:** Make sure to specify the sequence explicitly when uploading. You can number your files or describe the desired order in your prompt (e.g., 'start with the exterior shots, then move to interiors').

**Video output looks blurry or pixelated:** This usually happens when the source images are low resolution. For best results, use photos that are at least 1080px on the shortest side. If you're working with older or compressed images, mention this upfront so the output settings can be adjusted accordingly.

**The video is too long or too short:** You can control pacing by specifying how many seconds each image should display. If you didn't set a duration and the result feels off, simply ask for a revised version with a specific timing (e.g., '2 seconds per image' or 'fit everything into 60 seconds').

**Unsupported file format on playback:** The image-to-video-maker supports mp4, mov, avi, webm, and mkv. If your device or platform has trouble playing the output, request a specific format in your next prompt.

## Quick Start Guide

**Step 1 — Gather your images:** Collect the photos or graphics you want to include. For the best output, use consistently sized images and remove any duplicates or low-quality shots before uploading.

**Step 2 — Describe your vision:** In your prompt, tell the skill how long the video should be, how long each image should appear, what kind of transitions you prefer (fade, slide, cut, etc.), and whether you want any text overlays or audio.

**Step 3 — Specify your output format:** Choose from mp4, mov, avi, webm, or mkv depending on where you plan to use the video. If you're unsure, mp4 is the most universally compatible choice.

**Step 4 — Review and refine:** Once your first video is generated, watch it through and note anything you'd like adjusted — timing, order, pacing, or format. You can iterate quickly by describing what needs to change in a follow-up message. Most users get to a final result within two or three rounds of feedback.
