---
name: ai-text-to-video
version: "1.0.0"
displayName: "AI Text to Video Generator — Turn Written Ideas Into Engaging Videos Instantly"
description: >
  Tell me what you need and I'll transform your written content into compelling video scripts, storyboards, and production-ready prompts using ai-text-to-video intelligence. Whether you're converting a blog post, ad copy, social caption, or raw idea into a visual narrative, this skill breaks down your text and maps it to scenes, voiceover cues, and visual directions. Built for content creators, marketers, and educators who want to skip the blank-canvas struggle and go straight to producing.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome — let's turn your text into a video worth watching. Paste your content, describe your idea, or share a script draft and I'll generate a full scene-by-scene video breakdown with visual cues, voiceover guidance, and on-screen text suggestions ready for production.

**Try saying:**
- "I have a 600-word blog post about sustainable packaging — can you turn it into a 60-second video script with scene descriptions and voiceover lines?"
- "Convert this product launch announcement into a storyboard for a 30-second Instagram Reel, including visual direction for each scene and suggested on-screen text."
- "I have a slide deck outline for a training video on onboarding new employees — help me turn it into a full narrated video script with scene transitions and timing guidance."

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# From Words on a Page to Video That Moves People

Most people have the words — the product description, the story, the pitch — but no clear path from text to a finished video. That gap is exactly what this skill was built to close. By analyzing the structure, tone, and intent of your written content, it generates scene-by-scene breakdowns, on-screen text suggestions, visual mood guidance, and voiceover scripts that you can hand directly to a video editor or AI video tool.

This isn't about slapping your text on a slideshow. The skill reads between the lines — identifying which parts of your writing should be shown visually, which should be spoken aloud, and which work best as titles or captions. The result is a production blueprint that respects the original message while making it genuinely watchable.

Content marketers use it to repurpose long-form articles into short-form video content. Educators turn lecture notes into structured lesson videos. Entrepreneurs convert pitch decks and landing page copy into investor or customer-facing video narratives. Whatever your text contains, this skill helps you see it as a video before a single frame is shot.

## Prompt Routing and Scene Dispatch

When you submit a text prompt, the skill parses your input for scene intent, visual tone, and narrative structure, then routes each segment to the appropriate video synthesis pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

All video generation requests are processed through a distributed cloud rendering backend that handles diffusion model inference, keyframe interpolation, and audio-visual sync at scale. Rendered video assets are temporarily stored in a secure session bucket and streamed back to your interface upon completion.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ai-text-to-video`
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

## Use Cases

AI text to video conversion fits into more workflows than most people initially expect. The most common use is repurposing written content — taking a newsletter, article, or social post and restructuring it as a video that communicates the same message in a format audiences actually finish watching.

Marketers use it to generate video ad scripts from existing ad copy, ensuring the visual and spoken elements align with the brand's messaging. Educators and course creators convert lecture notes or curriculum outlines into structured video lessons with clear segment breaks and narration cues. YouTubers and podcasters use it to script video versions of their audio or written content without starting from scratch.

Startups and solo founders find it particularly useful for turning pitch decks or one-pagers into explainer video scripts they can record themselves or hand to a freelancer. The skill adapts to the length, tone, and audience of whatever text you bring — short-form social, long-form documentary style, or anything in between.

## Performance Notes

The quality of the video output depends heavily on the quality and clarity of the input text. Vague or loosely structured text will produce a usable but more generic video structure — the skill will make reasonable assumptions, but specificity always wins. If your text has a clear beginning, middle, and end, the scene breakdown will reflect that naturally.

For very long documents (1,000+ words), it helps to indicate upfront the target video length and platform — a 90-second LinkedIn video and a 10-minute YouTube tutorial require very different pacing and scene density. Mentioning tone (conversational, authoritative, cinematic) also sharpens the output significantly.

The skill does not render or export actual video files — it produces scripts, storyboards, scene descriptions, and production notes that you feed into a video creation tool or share with an editor. Think of it as the pre-production layer that makes everything downstream faster and more focused.

## Tips and Tricks

Start by telling the skill the platform and duration before pasting your text. 'This is for a 45-second TikTok' gives the skill the constraints it needs to make smart decisions about what to cut, what to emphasize, and how to pace scene transitions.

If your text is dense or technical, ask for a 'simplified visual script' — the skill will translate complex language into approachable on-screen visuals and plain-spoken voiceover without losing the core meaning. This is especially useful for B2B content being adapted for general audiences.

Use the storyboard mode when you want a visual-first output — each scene gets a description of what should appear on screen, not just what should be said. This is the format most video editors and AI video generators like Runway or Pika expect as input.

Finally, if you're not happy with the first pass, describe what's off — 'make it more energetic', 'cut it to three scenes', 'add a stronger call to action at the end' — and the skill will revise specifically rather than regenerating from scratch.
