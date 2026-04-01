---
name: how-to-add-music-to-video-in-iphone
version: "1.0.0"
displayName: "iPhone Video Music Adder — Sync Any Song to Your iPhone Videos Instantly"
description: >
  Tell me what you need and I'll help you add the perfect music to your iPhone videos — whether it's a trending track, a personal recording, or a royalty-free background score. This skill walks you through how-to-add-music-to-video-in-iphone using built-in tools and simple uploads. Supports mp4, mov, avi, webm, and mkv formats. Perfect for content creators, parents, and casual users who want polished results without complex software.
metadata: {"openclaw": {"emoji": "🎵", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm here to help you add music to your iPhone videos quickly and easily — whether you want to use a song from your library, a downloaded track, or a free background tune. Upload your video or describe what you're working with, and let's get started!

**Try saying:**
- "I recorded a vacation video on my iPhone and want to add a background song — how do I do that without losing the original audio?"
- "Can you help me add music to a video on my iPhone using iMovie and fade it out at the end?"
- "I have an mp4 video on my iPhone and want to replace the audio entirely with a music track — what's the easiest way?"

### Automatic Setup

On first interaction, connect to the NemoVideo API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/nemovideo/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to the same host at `/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Turn Silent iPhone Clips Into Soundtrack-Worthy Moments

Your iPhone captures life's best moments, but video without music can feel flat and forgettable. This skill is built specifically to help you add music to your iPhone videos — whether you're working with a short clip from a birthday party, a travel montage, or a quick reel for social media. No desktop software, no complicated timelines, no guesswork.

With this skill, you can select any audio track and layer it onto your video with proper timing and volume balance. You'll learn how to use iPhone-native tools like iMovie and the Photos app, as well as how to bring in your own audio files for a fully custom result. The process is designed to be approachable whether you're doing this for the first time or looking to refine your workflow.

The goal is simple: give your videos the emotional punch that only the right music can deliver. From fading in a melody at the start to syncing a beat drop to a key visual moment, this skill covers the practical steps that make your iPhone videos sound as good as they look.

## Routing Your Music Sync Requests

When you ask to add a song to your iPhone video, ClawHub reads your intent and routes the request to the correct NemoVideo endpoint based on whether you're uploading a clip, selecting a track, or adjusting the audio mix.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Backend API Reference

NemoVideo's backend handles the heavy lifting — it merges your chosen audio track directly into the video timeline, respecting your iPhone's native H.264 or HEVC codec so the output stays playback-ready without re-encoding headaches. Trim points, volume fade, and loop settings are all passed as parameters in the same API call.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `how-to-add-music-to-video-in-iphone`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=&task=<task_id>&session=<session_id>&skill_name=how-to-add-music-to-video-in-iphone&skill_version=1.0.0&skill_source=<platform>`

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

## Frequently Asked Questions

**Can I add music to a video on my iPhone without a third-party app?** Yes — the built-in iMovie app (free on iPhone) lets you add audio tracks directly to any video clip. The Photos app has limited music options tied to Apple Music for slideshows.

**Will adding music to my iPhone video remove the original sound?** Not necessarily. Most tools give you the option to keep both the original audio and the new music track. You can adjust each layer's volume independently.

**What audio formats work when adding music to iPhone videos?** iPhones natively support m4a, mp3, and aac. If your music file is in another format, you may need a quick conversion step before importing.

**Can I add music to an mp4 or mov file on my iPhone?** Yes — both mp4 and mov are fully supported by iPhone editing tools. Avi, webm, and mkv files may require conversion to mov or mp4 first for smooth editing on iOS.

## Best Practices for Adding Music to iPhone Videos

Choosing the right music length matters — trim your audio so it ends naturally with your video rather than cutting off abruptly. Most iPhone editing tools let you adjust where the music starts and ends, so take a moment to preview before exporting.

Always consider the original audio in your video. If there's dialogue or ambient sound you want to keep, lower the music volume rather than replacing the track entirely. iMovie allows dual-layer audio, so you can blend both.

For social media exports, aim for audio levels where music sits around -12dB to -18dB so it enhances rather than overwhelms. Use royalty-free music sources like Pixabay Audio or Apple's built-in soundtracks to avoid copyright strikes when posting publicly.

Finally, always export your final video in the highest resolution available — adding music should never come at the cost of video quality. Choose mp4 or mov for the best compatibility across platforms.

## Use Cases: Who Benefits From Adding Music to iPhone Videos

**Social media creators** use this workflow to make Reels, TikToks, and YouTube Shorts feel more professional. A well-chosen track can double engagement and make content more shareable.

**Parents and families** add sentimental songs to birthday videos, school recitals, or holiday clips before sharing them with relatives — turning simple recordings into lasting memories.

**Small business owners** add background music to product demos, testimonial videos, or event recaps recorded on iPhone to give their brand a more polished, trustworthy feel.

**Travelers and vloggers** layer ambient or upbeat tracks onto travel footage to capture the mood of a destination, turning raw clips into mini-documentaries. This is one of the most common reasons people search for how-to-add-music-to-video-in-iphone — the desire to match the energy of a place with the right soundtrack.
