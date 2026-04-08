---
name: free-image-to-video-ai-generator
version: "1.0.0"
displayName: "Free Image to Video AI Generator — Animate Your Photos Into Stunning Videos"
description: >
  Tell me what you need and I'll turn your still images into dynamic, eye-catching videos using AI — no editing software or technical skills required. This free-image-to-video-ai-generator skill breathes life into photos, product shots, illustrations, and artwork by adding motion, transitions, and cinematic effects. Perfect for content creators, small business owners, social media managers, and anyone who wants scroll-stopping video content without a budget.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Send me your image and I'll animate it into a compelling AI-generated video in seconds. No image yet? Just describe the scene or subject and I'll guide you from there.

**Try saying:**
- "Here's a product photo of my handmade candles — can you turn it into a short video with a warm, glowing motion effect for Instagram?"
- "I have 8 travel photos from my Japan trip. Can you combine them into a 30-second video with smooth transitions and a cinematic feel?"
- "Convert this portrait photo into a video with a subtle zoom-in effect and soft background blur, suitable for a LinkedIn post."

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Turn Still Photos Into Captivating Videos Instantly

Most people have folders full of great photos that never get the attention they deserve. Static images scroll past in a fraction of a second, but video stops thumbs and holds attention. This skill bridges that gap by transforming your existing images into polished, motion-rich videos — completely free and powered by AI.

Whether you're working with a single portrait, a batch of product photos, a travel gallery, or a piece of digital art, this skill analyzes your image and applies intelligent motion effects, zoom dynamics, smooth transitions, and optional text overlays to produce a video that feels professionally crafted. You don't need to know anything about frame rates, keyframes, or video codecs.

The result is a shareable video file ready for Instagram Reels, TikTok, YouTube Shorts, presentations, or client deliverables. What used to require expensive software and hours of manual work now takes seconds. This is image-to-video creation the way it should be — fast, free, and genuinely useful.

## Routing Your Animation Requests

When you submit a photo for animation, your request is parsed for motion style, duration, and output resolution, then dispatched to the appropriate AI video synthesis pipeline based on those parameters.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

All image-to-video inference runs on distributed GPU clusters via the backend API, handling frame interpolation, motion vector generation, and video encoding entirely in the cloud so nothing heavy runs on your device. Each rendered clip is temporarily stored on the server and streamed back as an MP4 once the diffusion pass completes.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `free-image-to-video-ai-generator`
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

Getting the best results from the free-image-to-video-ai-generator comes down to a few simple habits. First, use high-resolution images whenever possible — at least 1080px on the shortest side. Blurry or low-light photos will produce videos that look muddy, even with AI enhancement.

Be specific about the mood or motion style you want. 'Slow zoom with a warm color grade' will get you a much better result than just 'make it a video.' Think about where the video will be displayed — vertical 9:16 for TikTok and Reels, square 1:1 for feed posts, and 16:9 for YouTube or presentations.

If you're animating a batch of photos, try to keep consistent lighting and color tones across your images so the transitions feel natural. And don't overlook the power of adding a simple text overlay or caption — it dramatically increases engagement on social platforms without cluttering the visual.

## Use Cases

**E-commerce and Product Marketing:** Bring product photos to life with subtle motion and zoom effects that make listings stand out on platforms like Etsy, Shopify, and Amazon. A short video of a rotating product or a glowing candle flame converts far better than a static image.

**Real Estate Listings:** Turn interior and exterior photos into a smooth property walkthrough video without hiring a videographer. This is especially useful for rental listings and quick social media promotions.

**Social Media Content Creation:** Content creators who batch-shoot photos can now repurpose entire shoots into Reels, TikToks, and YouTube Shorts without touching a timeline editor. One photoshoot can generate a week's worth of video content.

**Event Recaps and Memories:** Wedding photographers, event planners, and families can compile highlight photos into a moving slideshow-style video that feels more personal and shareable than a static album link. Great for anniversary posts, graduation announcements, and milestone celebrations.

## FAQ

**Is this really free to use?** Yes — the free-image-to-video-ai-generator skill is available at no cost. You can convert images to video without subscriptions or hidden fees.

**What image formats are supported?** JPG, PNG, and WebP are the most reliable formats. Very large RAW files may need to be exported as JPG first for best results.

**How long will the generated video be?** For a single image, videos typically range from 5 to 15 seconds depending on the motion style. For multi-image batches, the length scales with the number of photos and transition settings you choose.

**Can I use the videos commercially?** Videos you generate from your own original images are yours to use. If you're using stock photos, check the licensing terms of the original image source before publishing commercially.

**Does the AI add music automatically?** Music is not added by default to avoid copyright issues, but you can request background audio suggestions or royalty-free track recommendations to pair with your video.
