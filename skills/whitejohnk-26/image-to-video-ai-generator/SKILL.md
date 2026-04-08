---
name: image-to-video-ai-generator
version: "1.0.0"
displayName: "Image to Video AI Generator — Animate Still Photos Into Stunning Motion Videos"
description: >
  Breathe life into static images by turning them into fluid, cinematic video clips in seconds. This image-to-video-ai-generator skill takes your photos, illustrations, or AI-generated art and transforms them into animated sequences with realistic motion, smooth transitions, and customizable pacing. Ideal for content creators, marketers, social media managers, and designers who want to produce eye-catching video content without complex editing software.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome! I turn your still images into dynamic, motion-filled video clips using AI — no editing software needed. Drop an image and tell me the style of animation you want to get started!

**Try saying:**
- "Here's a product photo of my sneakers — can you animate it with a slow 360-degree rotation and a subtle zoom-in effect for an Instagram reel?"
- "I have a landscape painting I'd like turned into a video with a cinematic parallax drift and soft cloud movement in the background — about 6 seconds long."
- "Take this portrait photo and create a short looping video with a gentle breathing effect and a slow push-in toward the subject's face."

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# From Still Frame to Moving Story — Instantly

Static images tell a moment. Videos tell a story. This skill bridges that gap by taking any image you provide — a product photo, a portrait, a landscape, an illustration — and generating a video clip that moves, breathes, and engages viewers in ways a flat image simply cannot.

Whether you're building a social media reel, animating a hero image for a landing page, or creating a slideshow that flows like a film, this tool handles the heavy lifting. You describe the motion style you want — a slow zoom, a parallax drift, a dramatic pan — and the AI interprets your image's content to produce natural-looking movement that fits the scene.

This skill is built for speed and creative flexibility. You don't need to storyboard, keyframe, or export from a timeline editor. Just bring your image and your vision, and within moments you'll have a video ready to share, embed, or build upon. It's the fastest path from a single photo to a scroll-stopping video clip.

## Motion Request Routing Logic

When you submit a still image for animation, your request is parsed for motion parameters — including frame duration, camera movement style, and interpolation intensity — then dispatched to the appropriate rendering pipeline based on resolution and complexity.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

All image-to-video synthesis runs on distributed GPU clusters via the animation backend, which handles optical flow estimation, temporal frame generation, and video encoding entirely in the cloud. Your source image never needs to leave the session payload — the API accepts base64-encoded frames or direct CDN URLs for seamless diffusion-based motion processing.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `image-to-video-ai-generator`
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

## Troubleshooting

If the generated video motion looks unnatural or jittery, the most common cause is an image with very low contrast between the subject and background. Try providing an image where the main subject is clearly separated from the background, or specify a simpler motion style like a slow zoom rather than a full parallax.

If the animation ignores part of your image — for example, not moving a sky element you expected to animate — try describing the specific region in your prompt more explicitly. Instead of 'make the clouds move,' try 'animate the upper third of the image with slow drifting cloud motion from left to right.'

For looping videos that feel seamless, request a motion style that returns to its starting position — such as a slow zoom that eases back out, or a drift that reverses gently. Abrupt-ending clips are harder to loop cleanly. If your output has an unexpected color shift or vignette, it may be related to the motion blur style applied — specify 'no vignette' or 'preserve original color grading' in your prompt to override default stylistic choices.

## Performance Notes

The quality of the generated video depends significantly on the input image. High-resolution images with clear subjects and well-defined edges produce the most convincing motion — the AI has more detail to work with when simulating depth and movement. Low-resolution or heavily compressed images may result in softer motion or visible artifacts around fine details like hair or foliage.

Complex motion requests on images with busy backgrounds — such as animating a crowd scene or a highly detailed illustration — may take longer to process and can occasionally produce inconsistent results in peripheral areas. For best output, start with a clear focal subject and a relatively uncluttered background.

Video length also affects processing time. Clips under 8 seconds generate quickly and maintain high fidelity. Longer sequences may require breaking the animation into segments for optimal quality. Portrait-oriented images (9:16) and square images (1:1) are natively supported for social media formats.

## Use Cases

This image-to-video-ai-generator skill fits naturally into a wide range of creative and professional workflows. E-commerce brands use it to animate product photos into short showcase clips for platforms like TikTok, Instagram Reels, and Pinterest Video Pins — dramatically increasing engagement compared to static listings.

Digital marketers use it to turn hero images and campaign visuals into motion ads without hiring a video production team. A single well-composed brand photo can become a 5-second bumper ad or a looping background video for a landing page.

Artists and illustrators use it to bring their work to life for portfolio showcases, NFT presentations, or social media promotion. A finished illustration animated with a subtle parallax effect feels entirely new without altering the original artwork.

Content creators building slideshows, memorial videos, travel recaps, or educational content use it to stitch animated image clips together into cohesive narrative videos that feel polished and intentional.
