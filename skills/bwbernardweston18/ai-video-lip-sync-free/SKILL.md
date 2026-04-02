---
name: ai-video-lip-sync-free
version: "1.0.0"
displayName: "AI Video Lip Sync Free — Match Any Audio to Video Lips Automatically"
description: >
  Tell me what you need and I'll sync your video's lip movements to any audio track — no expensive software required. This ai-video-lip-sync-free skill analyzes facial motion and aligns mouth movements frame-by-frame to match dubbed audio, voiceovers, or translated speech. Perfect for content creators, educators, and multilingual video producers who want polished, believable results without a studio budget. Upload your clip, provide your audio, and get back a naturally synced video ready to publish.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your video and the audio track you want synced, and I'll match the lip movements frame by frame. No files yet? Just describe your project and we'll figure out the best approach together.

**Try saying:**
- "I have a 3-minute English tutorial video and I've recorded a Spanish voiceover — can you sync the lip movements to the Spanish audio so it looks naturally dubbed?"
- "I recorded a talking-head video but the audio was bad, so I re-recorded the voiceover separately. Can you replace the original lip sync with the new clean audio track?"
- "I want to create a multilingual version of my product demo video. I have the original video and four different language audio files — how do I use this skill to sync each one?"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Sync Lips to Any Audio, Instantly and Free

Getting a video's mouth movements to match a new audio track used to mean expensive post-production software or hours of manual frame editing. This skill changes that entirely. Whether you're dubbing a tutorial into another language, replacing a voiceover, or fixing a dialogue recording that didn't quite land, AI Video Lip Sync Free handles the heavy lifting — analyzing the speaker's facial movements and reshaping them to align naturally with your new audio.

The skill is built for real-world content: talking-head videos, interview footage, educational explainers, social media clips, and short-form content where authentic speech delivery matters. You don't need to be a video editor or have any technical background. Just bring your video and your audio, and the skill does the rest.

This is especially valuable for multilingual creators who want to reach new audiences without the uncanny-valley effect of mismatched lip movements. The result is a video that feels recorded natively in whatever language or voice you've chosen — clean, credible, and ready to share.

## Routing Lip Sync Requests

When you submit a lip sync job, your audio track and source video are parsed and dispatched to the matching synthesis pipeline based on detected face count, audio codec, and frame rate compatibility.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

The backend leverages a distributed inference cluster running wav2lip-based neural rendering, where your video frames and mel-spectrogram data are aligned in real time before the re-timed mouth region is composited back onto the original footage. All processing is stateless per job, meaning each lip sync render is isolated, reproducible, and automatically garbage-collected after delivery.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-video-lip-sync-free`
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

## Performance Notes

Lip sync quality depends heavily on source material. Videos shot in good lighting with a front-facing camera at 1080p or higher will produce the most convincing results. Low-resolution footage, heavy motion blur, or profiles/side angles limit how precisely the facial mesh can be tracked and adjusted.

Audio quality matters equally. A clean, noise-free recording with consistent volume and clear consonant articulation gives the model the phoneme data it needs to drive accurate mouth shapes. Heavily compressed audio or recordings with significant background noise can cause subtle mis-syncs on hard consonant sounds like 'p,' 'b,' and 'm.'

For longer videos (10+ minutes), processing time increases proportionally. If you're working with a lengthy video, consider splitting it into logical segments, syncing each independently, and rejoining them in your editor. This also gives you more control over any sections that need manual review before final export.

## Integration Guide

Getting started with AI Video Lip Sync Free is straightforward. Begin by preparing two assets: your source video file (MP4 or MOV recommended, ideally with a clearly visible speaker face) and your replacement audio track (MP3 or WAV, matched to the same duration or trimmed to the speaking segments you want synced).

Once you share both files with the skill, it will identify the speaker's face, track lip and jaw motion across frames, and warp those movements to align with the phonemes in your new audio. For best results, ensure the speaker's face is well-lit and unobstructed in the source video — glasses, heavy beards, or extreme camera angles can reduce accuracy.

If you're working with a video that has multiple speakers, specify which speaker should be synced. For batch projects — such as producing the same video in five languages — process each audio track as a separate session and label your exports clearly before combining them in your final edit.

## FAQ

**Does this work with any language?** Yes. The lip sync process is driven by audio phonetics and facial motion tracking, not language-specific rules. It performs well across Latin-script languages and has solid support for tonal and non-Latin languages, though results may vary slightly depending on phoneme complexity.

**Will the output look natural or robotic?** For well-shot, well-lit source footage with clean audio, results look natural and broadcast-ready. The skill is designed to avoid the stiff, puppet-like effect common in older tools by using smooth interpolation between mouth positions.

**Can I use this for animated characters or cartoons?** Currently the skill is optimized for live-action human faces. Animated or stylized characters with non-realistic facial geometry are not reliably supported.

**Is there a video length limit?** There's no hard cap, but performance is optimal on clips under 15 minutes. For longer content, segmenting the video before processing is recommended for both speed and quality control.
