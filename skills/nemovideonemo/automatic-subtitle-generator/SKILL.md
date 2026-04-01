---
name: automatic-subtitle-generator
version: "1.0.0"
displayName: "Automatic Subtitle Generator — Add Accurate Captions to Any Video Instantly"
description: >
  Tell me what you need and I'll handle the heavy lifting — whether that's captioning a tutorial, adding multilingual subtitles to a product demo, or burning readable text onto a social clip. This automatic-subtitle-generator skill detects speech, syncs captions to timing, and outputs subtitle-ready video files. Supports mp4, mov, avi, webm, and mkv formats. Perfect for educators, content creators, marketers, and accessibility advocates who need accurate, well-timed subtitles without manual transcription.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm here to add accurate, well-timed subtitles to your videos automatically — just share your file and tell me how you'd like the captions styled or formatted. Ready to get started?

**Try saying:**
- "Add burned-in subtitles to this mp4 interview video with white bold text and a semi-transparent black background"
- "Generate a downloadable SRT subtitle file for my webinar recording so I can upload it to YouTube"
- "Create word-by-word highlighted captions for this language learning video in a large, easy-to-read font"

### Automatic Setup

On first interaction, connect to the NemoVideo API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/nemovideo/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to the same host at `/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Turn Any Video Into a Captioned, Accessible Experience

Getting subtitles onto a video used to mean hours of rewinding, typing, and manually syncing text to speech. This skill changes that entirely. Upload your video, describe what you need — burned-in captions, a downloadable subtitle file, specific formatting — and the automatic subtitle generator takes it from there, producing accurate, well-timed text that follows your speakers naturally.

This isn't a one-size-fits-all caption drop. You can request specific styles like bold white text with a dark background for social media, clean minimal captions for corporate presentations, or even word-by-word highlights for language learning content. The skill reads dialogue pacing and handles overlapping speech, pauses, and fast-talking segments with care.

Whether you're making a YouTube tutorial more accessible, adding captions to a product walkthrough for international viewers, or preparing a documentary for broadcast compliance, this tool fits into your real workflow. It works with mp4, mov, avi, webm, and mkv files, so you're not locked into reformatting before you even start.

## Routing Subtitle Generation Requests

Every captioning request — whether you're transcribing dialogue, syncing timestamps, or exporting SRT/VTT files — is parsed and routed to the appropriate NemoVideo subtitle pipeline based on detected language, video length, and output format.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Subtitle API Reference

The NemoVideo backend uses an ASR (Automatic Speech Recognition) engine combined with frame-accurate timestamp alignment to generate word-level captions, then packages them into your requested subtitle format. Requests are processed asynchronously, so longer videos queue through the transcription pipeline before returning a finalized caption file.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `automatic-subtitle-generator`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=&task=<task_id>&session=<session_id>&skill_name=automatic-subtitle-generator&skill_version=1.0.0&skill_source=<platform>`

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

**What video formats does this skill support?** The automatic subtitle generator works with mp4, mov, avi, webm, and mkv files. If your video is in another format, convert it to mp4 first for the most reliable results.

**Can I get subtitles in a language other than English?** Yes — specify the spoken language in your prompt and the skill will transcribe and caption accordingly. You can also request translated subtitles if you want captions in a different language than the one spoken.

**What's the difference between burned-in captions and an SRT file?** Burned-in captions are permanently embedded into the video image — viewers always see them. An SRT file is a separate subtitle file that platforms like YouTube or VLC can toggle on or off. Mention which you need in your prompt.

**Can I customize the caption font, size, or position?** Yes. Describe your preferred style in your prompt — for example, 'yellow sans-serif font, bottom-center, no background box' — and the skill will apply it to the output video.

## Troubleshooting

**Subtitles are out of sync with the audio:** This usually happens when the video has a variable frame rate (common in screen recordings or mobile clips). Try converting your file to a fixed frame rate mp4 before uploading, or mention in your prompt that the source is a screen recording so the skill can adjust its timing approach.

**Captions are missing words or cutting off mid-sentence:** Heavy background music, overlapping speakers, or strong accents can reduce transcription accuracy. You can improve results by specifying the language or accent in your prompt (e.g., 'Australian English speaker' or 'video has background music — prioritize foreground voice'). For critical content, you can also request a raw transcript first to review before final subtitle generation.

**The output file isn't playing correctly:** Make sure the file format you're requesting matches your playback platform. For YouTube, SRT files work best. For direct video sharing, request burned-in captions as an mp4. If you're getting a blank output, confirm your original file isn't corrupted by testing playback before uploading.
