---
name: video-format-converter
version: "1.0.0"
displayName: "Video Format Converter — Convert, Compress & Reformat Videos Instantly"
description: >
  Tell me what you need and I'll help you convert any video into the exact format, resolution, or codec your project demands. This video-format-converter skill handles everything from quick MP4-to-MOV swaps to bulk format migrations across entire libraries. Convert for web delivery, social media specs, broadcast standards, or device compatibility — without hunting through settings menus. Whether you're a content creator prepping uploads or a developer building a media pipeline, this skill speaks your language.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! I'm your video format converter assistant — ready to help you convert, reformat, or compress any video file for any platform or purpose. Tell me what format you're working with and where you need to take it, and let's get started!

**Try saying:**
- "Convert my MKV files to MP4 with H.264 encoding while keeping the original audio quality"
- "What's the best format and bitrate settings to export a video for Instagram Reels without losing quality?"
- "I need to batch convert a folder of MOV files to WebM for a web project — walk me through the fastest way to do it"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Convert Any Video Format Without the Guesswork

Dealing with incompatible video formats is one of those problems that should have been solved a decade ago — yet here we are, still wrestling with codecs, containers, and bitrate settings every time a client sends the wrong file type. This skill exists to end that friction.

The video-format-converter skill lets you describe what you're starting with and where you need to end up. Say you've got a batch of MKV files that need to become H.264 MP4s for a streaming platform, or a ProRes master that needs a compressed H.265 version for archiving — just tell it what you need and get precise, actionable conversion instructions or automated workflows tailored to your setup.

This isn't a one-size-fits-all tool. It accounts for frame rate, aspect ratio, audio codec compatibility, container limitations, and platform-specific requirements like YouTube's preferred specs or Instagram's size caps. Whether you're converting a single clip or planning a large-scale format standardization project, this skill gives you clear steps and smart recommendations without the trial-and-error.

## Routing Your Conversion Requests

When you submit a video conversion job, ClawHub parses your target format, codec preferences, and resolution parameters to route the request to the optimal processing pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

Video Format Converter runs on a distributed cloud transcoding backend that handles container remuxing, codec re-encoding, and bitrate normalization in parallel across multiple nodes. Large files are chunked and processed concurrently, so even 4K source footage or high-bitrate MKV files move through the pipeline without bottlenecking.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `video-format-converter`
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

The video-format-converter skill is designed to slot into the tools and workflows you're already using. If you're working with FFmpeg — the industry-standard command-line converter — this skill can generate precise, ready-to-run commands based on your input and output requirements, saving you from memorizing flag syntax.

For teams using Adobe Premiere, DaVinci Resolve, or Final Cut Pro, the skill can recommend export presets and codec settings that match your downstream delivery specs. It understands the difference between editing-friendly formats (like ProRes or DNxHD) and delivery formats (like H.264 or AV1), and will guide you toward the right choice for each stage of your pipeline.

Developers building media processing applications can use this skill to map out conversion logic, understand container and codec compatibility matrices, and troubleshoot format-related errors. Whether you're integrating FFmpeg into a Node.js backend or configuring a cloud media transcoding service, this skill provides the format knowledge layer your pipeline needs.

## Common Workflows

One of the most frequent use cases is social media preparation — taking a high-resolution master file and converting it to platform-optimized versions for YouTube (H.264, up to 4K), TikTok (MP4, 9:16 aspect ratio), and LinkedIn (under 5GB, MP4 preferred) all from a single source file. This skill walks you through each platform's specs and flags anything your source file might be missing.

Another common workflow is archive conversion — taking older formats like AVI, WMV, or Flash video (FLV) and migrating them to modern, space-efficient containers like MKV with H.265 encoding. This can dramatically reduce storage costs while preserving visual quality.

For video editors, the proxy workflow is a recurring need: converting large RAW or 4K footage into lightweight proxy files for smooth editing, then relinking to the original high-res files at export. This skill can outline the exact conversion settings to create proxies that match your editing software's expectations and keep your timeline clean.
