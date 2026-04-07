---
name: ai-video-editing-anup-sagar
version: "1.0.0"
displayName: "AI Video Editing by Anup Sagar — Smart Cuts, Captions & Creative Edits Powered by AI"
description: >
  Tired of spending hours cutting footage, writing captions, and piecing together video sequences manually? ai-video-editing-anup-sagar brings Anup Sagar's signature editing style and workflow intelligence into a conversational AI skill. Get scene-by-scene edit suggestions, caption drafts, b-roll placement ideas, pacing notes, and storytelling structure — all tailored for YouTube creators, short-form editors, and content teams who want polished results faster.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your footage description, script, or edit problem and I'll give you a full Anup Sagar-style edit plan. No footage yet? Just describe your video idea and I'll map out the structure.

**Try saying:**
- "I have a 10-minute talking-head YouTube video about productivity. Help me plan the cuts, add b-roll suggestions, and write a hook for the first 30 seconds in Anup Sagar's editing style."
- "I'm editing a travel vlog from my Manali trip — 45 minutes of raw footage. Give me a pacing structure, music mood suggestions, and tell me which moments to cut for a 6-minute final edit."
- "Write caption text and on-screen text overlays for a motivational short-form video that mimics the visual storytelling approach Anup Sagar uses in his YouTube Shorts."

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Edit Smarter, Not Harder — Anup Sagar's AI Editing Workflow

If you've ever watched Anup Sagar's videos and wondered how his edits feel so crisp, purposeful, and engaging — this skill brings that editorial thinking directly to your projects. Whether you're working on a YouTube documentary, a talking-head vlog, or a short-form reel, this skill helps you think through your footage the way an experienced editor would.

You can describe your raw footage, your story goal, and your target audience — and get back a structured edit plan: which clips to keep, where to cut for impact, when to use silence, and how to layer music or sound design for emotional effect. It's like having an editing consultant in your corner who understands pacing, narrative arc, and platform-specific formatting.

This skill is built for solo creators, small video teams, and students learning the craft of video editing. Instead of guessing your way through a timeline, you get clear, actionable guidance that reflects real editorial judgment — not just generic advice.

## Smart Edit Request Routing

Every request — whether you're asking for jump cuts, auto-captions, B-roll suggestions, or color grade tweaks — gets parsed by Anup Sagar's intent engine and routed to the matching AI editing pipeline automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing Backend Reference

Anup Sagar's editing backend runs on a distributed cloud inference layer that handles timeline analysis, speech-to-text captioning, and cut-point detection in parallel — so render jobs don't queue behind each other. Heavy operations like scene segmentation and AI voiceover sync are offloaded asynchronously and returned as edit-ready JSON timecodes.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-video-editing-anup-sagar`
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

## Common Workflows

The most popular workflow with ai-video-editing-anup-sagar starts with the 'footage dump' approach: describe every clip you have, its duration, and what happens in it. The skill then returns a prioritized cut list with reasoning — what to keep, what to cut, and what to restructure for narrative flow.

Another common workflow is the 'hook rescue' — you've already edited your video but the first 15 seconds aren't landing. Share your current opening and get a rewritten hook sequence with specific cut points and on-screen text suggestions.

Creators working on series content use this skill to maintain consistency across episodes: establish your tone and format once, then apply it as a template for every new video. This is especially useful for weekly YouTube uploads where speed and consistency both matter.

## Tips and Tricks

When asking for pacing advice, always mention your target audience's attention span and the platform. A 20-minute YouTube deep-dive needs different rhythm than a 60-second Instagram Reel — specifying this upfront saves back-and-forth.

Use the skill to stress-test your edit logic before you start cutting. Describe your planned structure and ask 'does this hold attention?' — you'll often catch weak mid-sections or slow openings before wasting editing time on them.

For Anup Sagar-inspired storytelling specifically, ask the skill to identify the 'emotional peak' of your video and build the edit structure backward from that moment. This technique is a hallmark of his style and works especially well for personal story videos and motivational content.

Finally, use short_prompts for quick wins during a live editing session — fast caption drafts, quick b-roll ideas, or a 10-second outro script when you're in the middle of a deadline crunch.

## Integration Guide

To get the most out of ai-video-editing-anup-sagar, start by describing your project clearly: mention the platform (YouTube, Instagram Reels, LinkedIn), the video length you're targeting, and the core message or story you want to tell. The more context you give, the more precise the edit guidance becomes.

If you're working inside a video editor like DaVinci Resolve, Premiere Pro, or CapCut, you can use this skill alongside your timeline. Generate an edit plan here, then execute it in your software. For caption workflows, paste your transcript or auto-generated subtitles and ask for rewrites, timing suggestions, or on-screen text formatting ideas.

For teams, this skill works well as a pre-edit briefing tool — use it to align on structure before anyone touches the timeline, reducing revision rounds significantly.
