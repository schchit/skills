---
name: ai-photo-editor
version: "1.0.0"
displayName: "AI Photo Editor — Smart Edits, Retouching & Visual Enhancements in Seconds"
description: >
  Transform ordinary snapshots into polished, professional-quality images without touching a slider. This ai-photo-editor skill handles everything from background removal and color grading to skin retouching, object erasure, and style transformations. Whether you're a content creator fixing product shots, a photographer batch-editing portraits, or someone who just wants great-looking photos — describe what you need and get precise editing guidance or AI-driven results instantly.
metadata: {"openclaw": {"emoji": "🖼️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome to your AI Photo Editor — whether you're retouching portraits, cleaning up product images, or transforming a photo's entire mood, I'm here to make it happen fast. Drop your photo or describe the edit you have in mind to get started!

**Try saying:**
- "Remove background from product photo"
- "Retouch and brighten this portrait"
- "Add cinematic color grade to photo"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Edit Photos Like a Pro, No Experience Needed

Most photo editing tools bury their best features under complex menus and steep learning curves. This skill cuts straight to the result — you describe what you want your photo to look like, and it walks you through exactly how to get there or generates the edit directly.

Whether you're working on a single hero image for a campaign or cleaning up a whole batch of product photos, the ai-photo-editor skill adapts to your workflow. Need to remove a distracting background element? Brighten up a dark indoor portrait? Add a cinematic color grade to a travel shot? Just tell it what you're going for.

This isn't a one-size-fits-all filter. It understands context — the difference between retouching a headshot for LinkedIn versus editing a moody shot for Instagram. You stay in creative control while the heavy lifting gets handled for you, saving hours of manual work and second-guessing.

## Routing Your Edit Requests

Each prompt you send — whether it's a background swap, skin retouching, or exposure correction — is parsed by intent classification and routed to the matching enhancement pipeline automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Processing API Reference

All image transformations run through a GPU-accelerated cloud backend that handles RAW decoding, non-destructive layer processing, and AI model inference in a single render pass. Processed outputs are returned as high-resolution exports without compression artifacts.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-photo-editor`
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

## Quick Start Guide

Getting your first edit done takes less than a minute. Start by either uploading a photo directly or describing the image you're working with — include details like lighting conditions, subject type (portrait, product, landscape), and the platform you're editing for.

Next, tell the skill what outcome you want. Be as specific or as loose as you like: 'make it look professional' works just as well as 'increase contrast by 20%, add a slight vignette, and desaturate the background.' The more context you give, the more tailored the result.

For batch editing workflows, describe the consistent style you want applied across multiple images — the skill can generate a reusable editing recipe or preset logic you can apply repeatedly. Start with one image to dial in the look, then scale it across your full set.

## Tips and Tricks

Reference a visual style you love to get faster, more accurate results. Instead of describing every adjustment, say 'edit this to look like a VSCO A4 preset' or 'give it the same muted tones as a Wes Anderson film' — the skill understands aesthetic shorthand.

When retouching portraits, specify the end use. A headshot for a corporate website needs different treatment than a fashion editorial — mentioning the destination helps calibrate how aggressive or subtle the retouching should be.

For object or background removal, describe what should stay in the image, not just what should go. Saying 'keep only the sneaker on a transparent background' produces cleaner results than 'remove everything around the shoe.'

If an edit isn't quite right on the first pass, describe what's off rather than starting over — 'the skin looks too smooth, dial it back' or 'the shadows are too crushed' gives the skill enough to refine without losing the work already done.

## Common Workflows

**E-commerce Product Photography:** Upload raw product shots and request consistent background removal, shadow addition, and color normalization across your catalog. This workflow is popular for Shopify and Amazon sellers who need uniform visuals without a studio setup.

**Portrait & Headshot Retouching:** Send a portrait and specify the platform — LinkedIn, dating app, press kit — and the skill will recommend or apply the right level of retouching, from natural skin smoothing to full studio-finish polishing.

**Social Media Content Creation:** Describe the platform (Instagram grid, Pinterest pin, Facebook ad) and the skill optimizes not just the edit but also crop ratios, saturation levels, and contrast for how images render on each platform's feed.

**Before/After Restoration:** Upload old, damaged, or low-resolution photos and request restoration — the skill can guide color correction, scratch removal, and upscaling to bring archival images back to life for print or digital sharing.
