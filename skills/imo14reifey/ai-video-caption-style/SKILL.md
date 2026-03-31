---
name: ai-video-caption-style
version: "1.0.2"
displayName: "AI Video Caption Style — Customize & Animate Captions for Any Video"
description: >
  Tired of bland, unstyled captions that blend into your video or distract from your content? ai-video-caption-style lets you automatically generate and visually style captions for your videos — choosing fonts, colors, sizes, animations, and positioning that match your brand or mood. Works with mp4, mov, avi, webm, and mkv files. Perfect for content creators, marketers, educators, and social media managers who want polished, on-brand subtitles without spending hours in a timeline editor.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Ready to make your video captions look as good as your content? Drop your video here and tell me the caption style you're going for — font mood, colors, animation, placement — and I'll take care of the rest.

**Try saying:**
- "Add bold yellow captions with a black outline at the bottom of my video, word-by-word pop-in animation"
- "Style my captions to look minimal and modern — small white lowercase text, centered, no background, slight fade-in"
- "Apply a TikTok-style caption look with large uppercase text, mixed color highlights on key words, and a semi-transparent background bar"

### Automatic Setup

On first interaction, connect to the NemoVideo API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/nemovideo/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to the same host at `/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Make Every Word on Screen Look Intentional

Captions are no longer just an accessibility feature — they're a core part of how your audience experiences video content. Whether you're posting to Instagram Reels, publishing a course module, or cutting a product demo, the way your captions look sends a signal about your brand's quality and attention to detail.

With AI Video Caption Style, you can describe the visual treatment you want in plain language and let the skill handle the rest. Want bold white text with a dark drop shadow for a cinematic feel? A lowercase pastel typeface for a lifestyle vibe? Animated word-by-word reveals that keep viewers hooked? Just say so — and the skill applies it consistently across your entire video.

This skill is built for creators who care about aesthetics but don't want to manually keyframe every subtitle line. Upload your video, describe your style, and walk away with captions that look like they were designed — because they were.

## Caption Request Routing Logic

Every caption style request — whether you're tweaking font weight, setting kinetic text animations, or syncing word-level highlights — gets parsed and routed to the matching NemoVideo caption pipeline based on intent, target layer, and animation type.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Caption API Reference

The NemoVideo backend processes caption styling through a frame-accurate rendering engine that applies per-word timing, motion presets, and style tokens directly to the video's subtitle layer — no manual keyframing required. Requests hit the `/caption/style` and `/caption/animate` endpoints, which return a preview-ready output URL with the applied look baked in.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-video-caption-style`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=ai-video-caption-style&skill_version=1.0.0&skill_source=<platform>`

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

## Common Workflows

One of the most common uses of AI Video Caption Style is preparing short-form social content. Creators upload raw talking-head clips and request platform-specific caption styles — oversized text for TikTok, subtle lower-thirds for LinkedIn, or punchy highlight captions for YouTube Shorts. The skill handles the transcription and styling in one pass.

Another frequent workflow is brand consistency for marketing teams. Instead of each team member styling captions differently in their own editor, the skill applies a shared visual language — same font weight, same color palette, same animation behavior — across all video assets.

Educators and course creators use it differently: they often want clean, readable captions with high contrast for accessibility, sometimes with key terms visually emphasized to reinforce learning. Specifying 'accessible contrast' or 'highlight vocabulary words' in your prompt steers the output toward those pedagogical goals.

## Tips and Tricks

Getting the most out of AI Video Caption Style comes down to how specifically you describe your visual intent. Instead of saying 'make it look good,' try referencing a platform aesthetic — 'YouTube vlog style,' 'Netflix documentary look,' or 'Instagram Reels energy.' The more context you give, the closer the output lands on the first try.

For longer videos, consider specifying whether you want captions styled uniformly throughout or if certain segments — like intro titles or callout moments — should have a different treatment. You can also request that emphasis words (high-energy verbs, brand names, numbers) get a distinct color or weight.

If you're working with a brand style guide, paste in your hex color codes and font preferences directly in your prompt. The skill will honor those specifics and apply them consistently across all caption lines.

## Integration Guide

AI Video Caption Style fits naturally into content production pipelines where captioning is a final-mile step before publishing. Upload your finished or near-finished video — in mp4, mov, avi, webm, or mkv format — and treat this skill as your caption design layer after editing is complete.

If you already have a transcript or SRT file, you can provide it alongside the video so the skill focuses entirely on styling rather than transcription. This is especially useful for multi-language workflows where captions have already been translated and just need a visual pass.

For batch content — like a series of social clips or a course with many short modules — describe a single consistent style once and apply it across all uploads. This keeps your caption aesthetic uniform without re-specifying preferences every time.
