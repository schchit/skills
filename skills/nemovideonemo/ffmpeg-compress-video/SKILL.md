---
name: ffmpeg-compress-video
version: "1.0.0"
displayName: "FFmpeg Video Compressor — Shrink Files Without Sacrificing Visual Quality"
description: >
  Turn bulky, oversized video files into lean, shareable assets using the power of ffmpeg-compress-video. This skill handles codec selection, bitrate tuning, resolution scaling, and format conversion so you don't have to memorize command-line flags. Ideal for content creators, developers, and media teams who need reliable compression results fast — whether targeting web delivery, mobile playback, or archive storage.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! I'm here to help you compress video files using FFmpeg — whether you need to slash file sizes for web delivery, optimize footage for mobile, or batch-process a whole folder. Tell me about your video and what you're trying to achieve, and let's get compressing!

**Try saying:**
- "Compress this 1.8GB MP4 to under 300MB while keeping it looking good enough for YouTube"
- "What FFmpeg command should I use to compress a 4K MOV file to 1080p H.265 for web streaming?"
- "I need to reduce the file size of 20 videos in a folder — give me a batch FFmpeg compression command"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Compress Any Video Smarter, Not Harder

Video files grow fast — a single 4K recording can balloon into gigabytes before you've even finished editing. The ffmpeg-compress-video skill gives you a conversational way to tackle that problem, letting you describe what you need in plain language and get back precise FFmpeg commands or direct compression results without digging through documentation.

Whether you're reducing a 2GB MP4 down to a streaming-friendly 200MB, converting MOV files for web upload, or batch-compressing footage for a client delivery, this skill understands context. It factors in your target file size, acceptable quality loss, intended platform, and source format to recommend the right combination of codec (H.264, H.265, VP9), CRF values, and audio settings.

This isn't a one-size-fits-all compressor. It adapts to your workflow — whether you're a developer automating a media pipeline, a YouTuber trimming upload times, or an archivist preserving footage at manageable sizes. You describe the goal; the skill handles the technical heavy lifting.

## Routing Your Compression Requests

When you submit a video for compression, ClawHub parses your target bitrate, codec preference (H.264, H.265, AV1), and quality parameters like CRF value to route your job to the appropriate FFmpeg processing pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

The backend spins up isolated FFmpeg instances that handle transcoding with configurable presets — from ultrafast to veryslow — balancing encode time against compression efficiency. Your source container format, audio stream settings, and pixel format are preserved or remuxed according to the output spec you define.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ffmpeg-compress-video`
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

## Integration Guide

The ffmpeg-compress-video skill is designed to fit into real production workflows without friction. If you're using it to generate FFmpeg commands, you can copy the output directly into your terminal, a shell script, or a CI/CD pipeline step. Commands follow standard FFmpeg syntax and are compatible with FFmpeg 4.x and above on Linux, macOS, and Windows.

For developers building automated media pipelines, this skill works well alongside tools like Node.js child_process, Python's subprocess module, or Docker-based FFmpeg containers. Simply pass the generated command as a string to your execution layer. If you're using a task queue like Celery or BullMQ, the commands slot in cleanly as job payloads.

When integrating into a web app or SaaS product, consider pairing this skill with cloud storage triggers — for example, compressing video automatically when a file lands in an S3 bucket or Google Cloud Storage folder. The skill can generate commands tuned for specific output destinations, including HLS streaming segments or progressive MP4 for CDN delivery.

## Troubleshooting

If your compressed video looks blocky or pixelated, the CRF value is likely set too high. For H.264, a CRF between 18–23 gives a good quality-to-size balance; going above 28 typically produces noticeable artifacts. Ask the skill to regenerate the command with a lower CRF if quality is the priority.

Audio desync after compression is a common issue when the source file has a variable frame rate (VFR). Mention that your source is screen-recorded or came from a mobile device — the skill will include the `-vsync vfr` or `-r` flag to normalize the frame rate and keep audio aligned.

If FFmpeg throws a 'codec not supported' error, your installed build may be missing certain encoders (like libx265 or libvpx). The skill can suggest an alternative codec or provide instructions for installing a full-featured FFmpeg build via package managers like Homebrew, apt, or through a static binary download.

For files that refuse to compress smaller despite high CRF values, the source may already be heavily compressed. In this case, ask the skill about resolution downscaling or audio bitrate reduction as alternative size-reduction strategies.

## Use Cases

Content creators uploading to YouTube, Instagram Reels, or TikTok often hit platform file size or bitrate limits. The ffmpeg-compress-video skill helps dial in the exact settings each platform prefers — for instance, H.264 at a 8Mbps cap for YouTube or a sub-15MB MP4 for Instagram direct upload.

Software teams recording screen captures for documentation or bug reports end up with massive files from tools like OBS or Loom exports. This skill trims those recordings down to a fraction of their original size while keeping text and UI elements sharp enough to read.

Filmmakers and video editors working with raw or proxy footage use this skill to create lightweight review copies for client approval — compressing 10-bit ProRes files into H.264 proxies that play smoothly on any device without sending a 40GB file over email.

Archivists and educators managing large video libraries use batch compression workflows to reduce storage costs. The skill can generate looped FFmpeg commands that process entire directories, applying consistent compression settings across hundreds of files in a single run.
