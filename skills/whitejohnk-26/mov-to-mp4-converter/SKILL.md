---
name: mov-to-mp4-converter
version: "1.0.0"
displayName: "MOV to MP4 Converter — Fast, Lossless Video Format Conversion Tool"
description: >
  Tired of MOV files refusing to play on Android devices, Windows Media Player, or social media platforms? The mov-to-mp4-converter skill handles the entire conversion process for you — no software installs, no manual codec hunting. Drop in your MOV file, get back a universally compatible MP4. Supports batch conversions, custom resolution outputs, and quality preservation. Built for content creators, social media managers, and anyone stuck with QuickTime files that won't cooperate.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! Ready to convert your MOV files into MP4s that actually play everywhere? Upload your file or describe what you need — let's get your video into a compatible format right now.

**Try saying:**
- "Convert this MOV file to MP4 while keeping the original 1080p resolution and audio quality."
- "I have a batch of 12 MOV recordings from my iPhone — can you convert all of them to MP4 for uploading to YouTube?"
- "Convert my MOV to MP4 but compress it under 50MB so I can attach it to an email."

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Turn Stubborn MOV Files Into Universal MP4s Instantly

Apple's MOV format is great inside the QuickTime ecosystem — but the moment you try to upload a MOV to YouTube, share it on Discord, or play it on a non-Apple device, things fall apart fast. Incompatibility errors, blank previews, and rejected uploads are frustrating time-wasters, especially when you're on a deadline.

The MOV to MP4 Converter skill exists to eliminate that friction entirely. It takes your MOV files and re-encodes them into MP4 — the format that works virtually everywhere, from Instagram Reels to Zoom recordings to email attachments. You stay in control of quality settings, so you're not forced to trade file compatibility for visual fidelity.

Whether you're a filmmaker exporting from Final Cut Pro, a marketer repurposing recorded demos, or just someone trying to send a video to a friend without it breaking — this skill handles the conversion cleanly and quickly. No desktop software required, no confusing export menus, and no surprise quality degradation.

## Routing Your Conversion Requests

When you submit a MOV file, the skill parses your codec preferences, target bitrate, and container settings before dispatching the job to the appropriate transcoding pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Transcoding API Reference

The backend leverages a distributed FFmpeg-powered cloud engine to remux QuickTime MOV containers into MPEG-4 format, preserving the original H.264 or HEVC video stream and AAC audio track without re-encoding unless a lossy compression parameter is explicitly set. Conversion jobs are queued, processed in parallel, and returned via a signed download URL valid for 24 hours.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `mov-to-mp4-converter`
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

## Tips and Tricks

For screen recordings exported as MOV from QuickTime or macOS Screenshot, use H.264 encoding rather than H.265 when converting to MP4. H.265 offers better compression but has inconsistent browser and platform support, while H.264 MP4 files play reliably in virtually every environment.

If you're converting MOV files specifically for social media, request a vertical crop (9:16 aspect ratio) during conversion rather than doing it as a separate step. Combining format conversion and aspect ratio adjustment in one pass saves time and avoids a second quality loss cycle.

For long MOV files like lectures or webinar recordings, consider splitting the output into chapters or segments during conversion. Large single MP4 files above 2GB can cause issues on certain upload platforms, and segmenting makes editing and re-uploading much more manageable.

## Performance Notes

Conversion speed depends heavily on the source MOV file's resolution, duration, and codec. A 10-minute 1080p MOV from an iPhone typically converts in under two minutes. 4K ProRes MOV files from professional cameras take considerably longer due to the raw data volume involved — expect 5–10x the conversion time compared to standard HD files.

Lossless or near-lossless conversion preserves the original quality but results in larger MP4 file sizes. If your goal is web delivery or streaming, a moderate compression setting (CRF 18–23 in H.264 terms) will produce files that are visually indistinguishable from the source while being significantly smaller.

Batch conversions of many short MOV clips process more efficiently than a single large file in some cases. If you're working with a large library of short clips — like social media snippets or product demo segments — submitting them as a batch rather than one at a time will yield faster overall throughput.

## Troubleshooting

If your converted MP4 has no audio, the original MOV likely used AAC or PCM audio in a format that wasn't mapped correctly during conversion. Try re-running the conversion with explicit audio codec settings — specifying AAC output usually resolves this.

Blurry or pixelated output typically means the bitrate was set too low during encoding. MOV files from iPhones and cameras often carry very high bitrates, and compressing aggressively without adjusting resolution first will visibly degrade quality. Match the output bitrate closer to the source for best results.

If the MP4 plays fine on desktop but fails to upload to Instagram or TikTok, check the frame rate. Those platforms prefer 30fps or 60fps. MOV files recorded at 24fps or non-standard rates sometimes need a frame rate normalization pass before the upload succeeds.
