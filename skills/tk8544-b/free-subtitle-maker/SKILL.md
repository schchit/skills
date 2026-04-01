---
name: free-subtitle-maker
version: "1.0.0"
displayName: "Free Subtitle Maker — Auto-Generate & Burn Subtitles Into Any Video"
description: >
  Drop a video and describe your subtitle style — this free-subtitle-maker skill transcribes your audio, formats the captions, and burns them directly into your footage. Works with mp4, mov, avi, webm, and mkv files. Choose font style, size, placement, and color, or let the defaults handle it. Built for content creators, educators, and social media teams who need accurate, readable subtitles without paid software or complex workflows.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Ready to add subtitles to your video for free? Upload your mp4, mov, or other video file and tell me your caption preferences — font, color, placement, or just leave it to the defaults — and I'll burn accurate subtitles directly into your footage.

**Try saying:**
- "Add white subtitles with a black outline at the bottom of this mp4 tutorial video"
- "Generate subtitles for my interview clip and use a large bold font so it's easy to read on mobile"
- "Burn captions into this webm product demo — keep the style clean and minimal, centered at the bottom"

### Automatic Setup

On first interaction, connect to the NemoVideo API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/nemovideo/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to the same host at `/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Turn Any Video Into a Captioned, Accessible Masterpiece

Getting subtitles onto a video used to mean juggling transcription services, SRT files, and video editors — all before you could share a single clip. This free-subtitle-maker skill collapses that entire process into one step. Upload your video, describe any preferences you have for how the subtitles should look, and walk away with a fully captioned file ready to publish.

The skill listens to your video's audio track, breaks it into timed segments, and overlays clean, readable text directly onto the frames. Whether you're subtitling a tutorial, a short film, a product demo, or a social reel, the output is a polished video file — not a separate caption file you still have to attach somewhere.

This tool is especially valuable for creators working across languages or accessibility requirements. Subtitles increase watch time, improve comprehension for non-native speakers, and make content usable in sound-off environments like social feeds. You don't need an account with a transcription platform or a video editing subscription — just your video and a prompt.

## Routing Subtitle Generation Requests

Every user request — whether auto-generating SRT captions, burning hardcoded subtitles, or adjusting font and timing — is parsed and routed to the matching NemoVideo endpoint based on the detected action type.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Backend Reference

Free Subtitle Maker runs entirely on the NemoVideo backend, which handles speech-to-text transcription, subtitle rendering, and frame-accurate burn-in encoding without requiring any local processing. All subtitle jobs — including multi-language captions and styled text overlays — are queued, processed, and returned as downloadable video files through the NemoVideo pipeline.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `free-subtitle-maker`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=free-subtitle-maker&skill_version=1.0.0&skill_source=<platform>`

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

## Use Cases

This free-subtitle-maker skill fits naturally into a wide range of real-world workflows. Educators recording lecture videos or screencasts can add subtitles to make content accessible to students with hearing impairments or those studying in a second language. A single upload-and-prompt workflow replaces what used to require dedicated captioning software.

Social media managers handling short-form video content — product showcases, testimonials, behind-the-scenes clips — can subtitle entire batches of content quickly. Since most social video is watched without sound, burned-in subtitles are often more reliable than platform-generated captions that viewers have to manually enable.

Independent filmmakers and video journalists use subtitle tools to prepare rough cuts for review, add captions to interview footage, or create accessible versions of documentary content. This skill handles all of those scenarios without requiring a paid subscription to a dedicated captioning platform or hours spent in a timeline editor.

## Performance Notes

Subtitle accuracy depends heavily on audio clarity. Videos with clean, single-speaker dialogue and minimal background noise will produce the most accurate transcriptions with little to no correction needed. Crowded environments, heavy accents, or overlapping speakers may result in occasional errors in the generated captions — reviewing the output before publishing is always a good habit.

File size and video length affect processing time. Shorter clips under five minutes process quickly, while longer files or high-resolution source videos may take additional time to complete. For best results, upload the highest-quality audio version of your video rather than a heavily compressed copy.

Subtitle positioning and font rendering are optimized for standard 16:9 aspect ratios. Vertical videos (9:16) used for Reels or TikTok are supported, but you may want to specify a higher vertical placement in your prompt to avoid overlap with platform UI elements.
