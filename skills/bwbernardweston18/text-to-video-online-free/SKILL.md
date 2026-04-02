---
name: text-to-video-online-free
version: "1.0.0"
displayName: "Text to Video Online Free — Turn Written Ideas Into Engaging Videos Instantly"
description: >
  Tell me what you need and I'll help you transform plain text into compelling videos — no software downloads, no paywalls, no experience required. This text-to-video-online-free skill is built for creators, marketers, educators, and small business owners who need fast, polished video content straight from a script or idea. Type a concept, a product description, a blog post, or a story — and get a structured video ready to share. Key features include scene-by-scene storyboarding, caption generation, voiceover scripting, and platform-specific formatting for YouTube, TikTok, Instagram, and more.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Paste your script, idea, or topic and I'll build you a complete text-to-video-online-free production plan with scenes, captions, and voiceover copy. No script yet? Just describe what your video should be about.

**Try saying:**
- "I have a 300-word product description for my skincare brand — can you turn it into a 60-second video script with scene-by-scene instructions for TikTok?"
- "Convert this blog post introduction into a YouTube Shorts video with on-screen text, a hook in the first 3 seconds, and a call-to-action at the end."
- "I want to make a free online video explaining how compound interest works for a beginner audience — write the full narration script and scene breakdown."

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# From Blank Page to Finished Video in Minutes

Most people have ideas worth sharing but get stuck the moment they think about turning those ideas into video. The editing software feels overwhelming. The production costs feel out of reach. And the time investment feels impossible. That's exactly the gap this skill was built to close.

With this text-to-video-online-free skill, you start with words — a sentence, a paragraph, a full script — and walk away with a structured, production-ready video plan. You'll get scene breakdowns, on-screen text suggestions, voiceover narration drafts, background music mood direction, and caption copy all generated from your input. It's like having a video producer on call who never charges by the hour.

Whether you're launching a product, teaching a concept, promoting an event, or just telling a story, this skill adapts to your content type and target platform. No prior video experience needed. No API keys. No account setup. Just paste your text and start creating.

## Routing Your Video Generation Requests

When you submit a text prompt, ClawHub parses your script, scene descriptions, and style preferences before routing the job to the appropriate text-to-video rendering pipeline based on duration, resolution, and available free-tier capacity.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

The backend leverages distributed cloud GPU clusters to handle prompt tokenization, frame synthesis, and audio-visual sync in real time — so your free online video renders without any local processing overhead. API calls follow a queued job model, returning a render_id you can poll for status until your MP4 is ready to preview or download.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `text-to-video-online-free`
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

This text-to-video-online-free skill is designed to slot seamlessly into your existing content workflow without requiring any technical setup. Once you have your video script, scene breakdown, or narration copy generated here, you can take that output directly into free online video tools like Canva Video, CapCut, InVideo, or Clipchamp — all of which accept text-based scene instructions and caption files.

For teams using content calendars or social media schedulers, the structured output format (scene number, visual description, on-screen text, voiceover line) maps cleanly into spreadsheet workflows or content briefs. You can also feed the generated narration scripts into free text-to-speech tools like ElevenLabs' free tier or Google's TTS to produce voiceovers without recording anything yourself.

If you're building a repeatable content pipeline, use this skill to batch-generate scripts for an entire content series at once — just provide your topic list and preferred format, and you'll have a full week of video content planned in one session.

## Quick Start Guide

Getting your first video out of this skill takes less than two minutes. Start by pasting any existing text — a product page, a how-to article, a social media caption, or even a rough idea written in plain language. Then specify your target platform (YouTube, Instagram Reels, TikTok, LinkedIn) and your desired video length (15 seconds, 60 seconds, 3 minutes).

The skill will return a complete scene-by-scene breakdown with visual direction, on-screen text for each scene, a voiceover script, and suggested pacing. If you don't have existing text, simply describe your video topic in one or two sentences — for example, 'A video explaining the benefits of cold showers for a fitness audience' — and the skill will generate the full script from scratch.

Once you receive your output, copy the scene breakdown into your preferred free online video editor and match visuals to each scene. Your text-to-video-online-free production is ready to film, animate, or assemble using stock footage — no budget required.
