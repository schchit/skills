---
name: best-ai-for-video-editing
version: "1.0.0"
displayName: "Best AI for Video Editing — Smart Cuts, Captions & Creative Edits in Minutes"
description: >
  Drop a video and describe what you want — and watch it come together fast. This skill is built around the best-ai-for-video-editing workflows: trimming dead air, generating captions, reframing for social, syncing cuts to music, and suggesting creative edits based on your footage. Whether you're a solo creator, marketer, or filmmaker, it handles the tedious parts so you can focus on storytelling. No timeline scrubbing required.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome to your AI-powered video editing assistant — the fastest way to go from raw footage to a polished, publish-ready clip. Tell me what you're working on or drop your video and let's start cutting.

**Try saying:**
- "I have a 12-minute interview recording — help me cut it down to a 3-minute highlight reel with captions for Instagram Reels."
- "My product demo video is too slow in the middle. Can you identify the dull sections and suggest where to trim for better pacing?"
- "I want to turn this horizontal YouTube video into a vertical TikTok clip with auto-generated subtitles and a text hook at the start."

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# Edit Smarter: AI That Actually Understands Your Footage

Most video editing tools make you do all the thinking — you scrub through timelines, manually cut clips, and spend hours on tasks that should take minutes. This skill flips that experience entirely. Describe what you want your video to look like, and it figures out how to get there.

Whether you need a 90-second YouTube video trimmed to a punchy 30-second ad, a talking-head clip cleaned up with auto-captions, or a highlight reel assembled from raw footage, this skill handles the logic behind each decision. It understands pacing, visual storytelling, and platform-specific formatting — so your edits don't just look clean, they feel intentional.

Creators who use the best AI for video editing stop wasting time on repetitive tasks and start spending more energy on the creative choices that actually matter. From first cut to final export, this skill acts as a capable co-editor who never gets tired and always knows what frame to cut on.

## Routing Cuts, Captions & Effects

Each request — whether you're asking for smart jump cuts, auto-captions, B-roll suggestions, or color grade tweaks — is parsed by intent and routed to the specialized AI model best suited for that editing task.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Render Pipeline Reference

Video processing runs through a distributed cloud transcoding backend that handles frame analysis, speech-to-text captioning, and generative edit rendering without taxing your local machine. Large files are chunked into segments, processed in parallel, then reassembled with frame-accurate precision before delivery.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `best-ai-for-video-editing`
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

**Start with your goal, not your footage.** Instead of saying 'here's my video, edit it,' try 'I need a 60-second emotional brand story from this 8-minute founder interview.' That framing produces dramatically sharper suggestions.

**Use it for B-roll planning.** Describe your main talking points and ask the skill to suggest B-roll shot types that would visually support each section — a huge time-saver in pre-production.

**Batch your caption requests.** If you have multiple videos needing captions, list them together with their respective tones and platforms. The skill can handle batch instructions efficiently.

**Ask for multiple cut versions.** Request a 15-second, 30-second, and 60-second version simultaneously. Having three lengths ready means you're prepared for every ad placement or social slot without going back and forth.

## FAQ

**Can this skill edit the video file directly?** It provides precise editing instructions, cut points, caption text, and export recommendations that you can apply in your editor of choice — or use with compatible export integrations.

**What platforms does it optimize for?** It knows the aspect ratios, caption styles, and pacing conventions for YouTube, TikTok, Instagram Reels, LinkedIn, and Twitter/X. Just mention your target platform.

**Can it generate captions in multiple languages?** Yes. Specify the target language and it will produce translated caption files alongside the original transcript.

**Is it useful if I already know how to edit?** Absolutely. Many experienced editors use the best AI for video editing to speed up rough cut decisions, generate caption drafts, and get a second opinion on pacing — not to replace their skills, but to accelerate them.

## Performance Notes

For the best results when using this skill, upload footage in common formats like MP4, MOV, or MKV. Longer videos (over 20 minutes) may take slightly more time to analyze, so breaking raw footage into segments before uploading can speed up the editing suggestions significantly.

When asking for cuts or highlight reels, the more context you give — intended platform, target audience, desired tone — the more precise the output. A vague request like 'make it shorter' will produce a different result than 'cut this to 45 seconds for a LinkedIn ad targeting B2B marketers.'

Audio quality also affects caption accuracy. If your video has background noise or overlapping voices, mention it upfront so the skill can flag low-confidence caption segments for your review rather than silently guessing.
