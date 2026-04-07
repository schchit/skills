---
name: seedance-ai-video-maker
version: "1.0.0"
displayName: "Seedance AI Video Maker — Turn Ideas Into Stunning Videos in Minutes"
description: >
  Tired of spending hours wrestling with complex video editing tools just to produce something that looks amateur? seedance-ai-video-maker takes your ideas, scripts, images, or prompts and transforms them into polished, dynamic videos without the steep learning curve. Generate cinematic scenes, animate still images, create product showcases, or build social-ready content — all through natural language. Built for creators, marketers, and storytellers who need results fast.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me a prompt, script, or image and I'll generate a compelling video using seedance-ai-video-maker. No footage? Just describe the vibe, subject, and style you want.

**Try saying:**
- "Create a 15-second product showcase video for a minimalist leather wallet, using warm lighting, slow zoom effects, and a luxury lifestyle feel."
- "Animate this product photo into a short looping video clip with a subtle parallax motion effect suitable for an Instagram ad."
- "Generate a cinematic travel video clip showing a sunrise over misty mountains with an emotional, sweeping atmosphere — no text, just visuals."

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Create Cinematic Videos From Pure Imagination

seedance-ai-video-maker is a next-generation video creation skill that bridges the gap between your creative vision and a finished, shareable video. Whether you're a solo content creator, a small business owner, or a marketing professional, this skill lets you describe what you want and watch it come to life — no timeline scrubbing, no keyframe headaches, no rendering queues that eat up your afternoon.

With seedance-ai-video-maker, you can generate video clips from text prompts, animate still photos into fluid motion sequences, produce product demo videos from a simple description, or craft short-form social content tailored to platforms like TikTok, Instagram Reels, and YouTube Shorts. The AI understands context, mood, pacing, and visual style — so you spend less time explaining and more time publishing.

This skill is especially powerful for teams that need to move fast. Prototype a campaign video before committing to a full production budget. Test multiple visual styles in minutes. Repurpose a blog post into an engaging video summary. seedance-ai-video-maker removes the bottleneck between ideation and execution, making video creation genuinely accessible to anyone with a story to tell.

## Routing Your Video Prompts

Every request you send — whether it's a text-to-video prompt, image animation, or style transfer — gets routed to Seedance's generation pipeline based on the selected model tier and output resolution.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Seedance API Backend Reference

Seedance processes all video generation jobs on its distributed cloud inference nodes, handling frame interpolation, motion synthesis, and audio-visual sync entirely server-side. Your prompts and source assets are temporarily staged during rendering, then delivered as downloadable MP4 outputs once the job completes.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `seedance-ai-video-maker`
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

## Best Practices for seedance-ai-video-maker

The more specific your prompt, the better your output. Instead of saying 'make a nature video,' try 'create a 10-second clip of golden-hour light filtering through a dense forest with slow camera movement and a peaceful tone.' Specificity in mood, camera motion, lighting, and subject gives the AI clearer creative direction.

When working with images, use high-resolution source files with a clear focal point. Cluttered or low-contrast images tend to produce less fluid animations. If you're building a multi-scene video, describe each scene separately and indicate transitions or pacing cues like 'cut to,' 'fade in,' or 'slow push forward.'

For social media content, always specify your target platform and aspect ratio upfront — vertical 9:16 for Reels and TikTok, square 1:1 for feed posts, or widescreen 16:9 for YouTube. This saves revision time and ensures the composition is optimized from the first generation.

## Use Cases That Shine With seedance-ai-video-maker

E-commerce brands use seedance-ai-video-maker to produce scroll-stopping product videos without hiring a videographer. A simple product image plus a style description can yield a professional-looking clip ready for paid social ads within minutes.

Content creators and influencers use it to rapidly prototype video concepts before filming, or to generate B-roll-style visuals that complement talking-head footage. It's also a go-to for filling content calendars during slow production weeks.

Agencies and freelancers leverage it to pitch clients with animated mockups and video concepts early in the creative process — setting expectations and winning approvals before any real production budget is spent. Educators and course creators use it to build engaging visual explainers from lesson outlines, turning dry text content into watchable, shareable video summaries.

## Tips and Tricks to Get More From Your Videos

Use style anchors in your prompts to guide the visual language. Phrases like 'shot on 35mm film,' 'drone footage aesthetic,' 'soft pastel color grade,' or 'high-contrast editorial look' dramatically shift the output without requiring any manual color work.

If you want consistent branding across multiple clips, describe your brand palette and visual identity in each prompt — for example, 'use deep navy and warm gold tones with clean sans-serif typography overlays.' Repetition of these cues across sessions helps maintain visual coherence.

Don't overlook the power of motion keywords. Words like 'drift,' 'orbit,' 'zoom burst,' 'handheld shake,' or 'locked-off static' give the AI specific camera behavior instructions. Combining motion style with subject and mood creates videos that feel intentional rather than randomly generated.
