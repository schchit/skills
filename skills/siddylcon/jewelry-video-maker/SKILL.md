---
name: jewelry-video-maker
version: "1.0.0"
displayName: "Jewelry Video Maker — Create Stunning Product Videos That Sell Your Pieces"
description: >
  Turn raw clips and photos of your jewelry into polished, scroll-stopping product videos ready for Instagram, Etsy, TikTok, or your online store. This jewelry-video-maker skill helps designers, boutique owners, and independent jewelers craft cinematic showcases — complete with captions, pacing suggestions, music cues, and shot sequencing tailored to highlight sparkle, texture, and craftsmanship. No video editing background needed.
metadata: {"openclaw": {"emoji": "💍", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your footage details, product photos, or a description of your jewelry collection and I'll map out a complete video concept ready to shoot or edit. No footage yet? Just describe the piece and I'll build the script from scratch.

**Try saying:**
- "I have 10 short clips of a gold layered necklace being worn and laid flat — help me sequence them into a 30-second Instagram Reel with captions and a mood description"
- "Create a product video script for a handmade turquoise ring set, targeting Etsy shoppers, with a warm artisan feel and a call-to-action at the end"
- "I'm launching a holiday collection of diamond earrings — give me a shot list and video structure for a 60-second TikTok that highlights sparkle and gift-giving emotion"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Make Every Piece Shine On Screen

Jewelry is tactile, intimate, and hard to capture digitally — yet video is now the dominant way shoppers discover and fall in love with pieces before buying. This skill bridges that gap by helping you build compelling video narratives around your jewelry, whether you're launching a new collection, promoting a single statement ring, or building a brand aesthetic across your social channels.

With the Jewelry Video Maker skill, you can describe your footage, share image references, or outline what you're trying to communicate — and receive structured video scripts, shot order recommendations, caption copy, transition styles, and platform-specific formatting advice in return. Think of it as a creative director who specializes entirely in jewelry content.

This skill is built for goldsmiths, silver artists, gemstone dealers, handmade jewelry sellers, and luxury brand teams alike. Whether your style is minimalist editorial or warm artisan storytelling, the output adapts to your brand voice and target audience — helping you produce videos that feel intentional, not amateur.

## Routing Your Video Requests

Each request — whether you're generating a rotating solitaire showcase, a lifestyle reel, or a macro close-up of stone setting detail — is parsed by intent and routed to the matching video generation pipeline best suited for your jewelry type and style.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

Jewelry Video Maker runs on a high-resolution cloud rendering backend optimized for capturing metallic finishes, gemstone refractions, and fine detail at the micro level — no local GPU required. Your footage is processed, composited, and delivered via secure API endpoints that handle everything from background removal to motion path animation.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `jewelry-video-maker`
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

Jewelry videos perform best when they lead with motion in the first two seconds — a rotating ring, light catching a stone, or a hand reaching for a pendant. This skill prioritizes that principle when building your video sequences, always recommending a hook shot before any static or lifestyle content.

For platform-specific performance: Instagram Reels and TikTok reward vertical 9:16 framing and fast pacing under 30 seconds, while Etsy listing videos convert better at 15–30 seconds with clear product visibility and no music dependency. Pinterest and website hero videos benefit from slower, cinematic pacing with a 4:5 or 16:9 ratio.

When requesting output, mention your platform so the skill can calibrate caption length, transition speed, and video duration accordingly. If you're repurposing one video across multiple platforms, ask for a multi-format breakdown and the skill will provide adapted versions for each in a single response.

## Quick Start Guide

Getting your first jewelry video concept takes less than two minutes. Start by telling the skill three things: what piece or collection you're featuring, what platform the video is for (Instagram, TikTok, Etsy listing, website hero, etc.), and the feeling you want viewers to walk away with — luxury, handmade warmth, bold fashion, bridal elegance, or otherwise.

If you already have footage, describe your clips briefly — how many you have, whether they're close-ups or lifestyle shots, and if any show the jewelry in motion or being worn. The more context you share, the more tailored your video structure will be.

Not sure where to start? Just paste a link to a jewelry video you admire and say 'make something like this for my [piece type].' The skill will reverse-engineer the structure and adapt it to your product. You can also ask for a shot list first, then come back for the edit sequence and caption copy separately.
