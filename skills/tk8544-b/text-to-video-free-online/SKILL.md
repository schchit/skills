---
name: text-to-video-free-online
version: "1.0.0"
displayName: "Text to Video Free Online — Turn Written Prompts Into Shareable Videos Instantly"
description: >
  Type a scene, a story idea, or a product description — and watch it become a video in seconds. This text-to-video-free-online skill transforms plain written prompts into dynamic video content without any software downloads, subscriptions, or editing experience required. Perfect for content creators, educators, small business owners, and social media marketers who need fast, visual storytelling without the production overhead.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welcome! You're one text prompt away from a finished video — describe your scene, story, or message and I'll help you bring it to life using text-to-video-free-online. Ready? Type your idea below and let's create something worth watching.

**Try saying:**
- "Create a 30-second promotional video for a local coffee shop using this description: cozy atmosphere, hand-crafted lattes, open 7am–8pm, located in downtown Austin"
- "Turn this blog post intro into a short explainer video: 'Climate change is accelerating faster than most models predicted. Here's what that means for coastal cities by 2040.'"
- "Generate a motivational video with upbeat energy for a fitness brand — the theme is 'No excuses, just results' and it should feel high-intensity and bold"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# From Words on a Screen to Videos Worth Watching

Most people have ideas they want to share visually but no practical way to bring them to life quickly. Hiring editors is expensive. Learning video software takes weeks. And generic stock footage rarely captures what you actually mean. That's exactly the gap this skill fills.

With text-to-video-free-online, you describe what you want — a product showcase, a short explainer, a social media clip, a motivational reel — and the skill handles the heavy lifting of turning that description into a coherent, watchable video. You're not limited to templates or locked into a rigid structure. The output reflects your words, your tone, and your intent.

This is especially useful for marketers testing campaign concepts, educators building lesson content, and creators who need to publish consistently without burning hours on post-production. Whether you're scripting a 15-second ad or a 2-minute brand story, the process starts with nothing more than a text prompt and ends with a video ready to share.

## Routing Your Video Prompts

When you submit a written prompt, ClawHub parses the scene description, style tags, and duration parameters before dispatching the generation request to the appropriate free-tier rendering pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Rendering API Reference

The backend leverages distributed GPU clusters to process your text-to-video jobs asynchronously, converting natural language prompts into rendered video frames via diffusion-based synthesis models. Free online sessions are queued through a shared inference layer, so render times scale with current platform load.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `text-to-video-free-online`
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

Text-to-video generation works best when your input is specific rather than vague. A prompt like 'make a video about nature' will produce something generic, while 'create a calming 20-second video showing a forest at dawn with soft light filtering through trees' gives the system enough detail to produce something genuinely usable.

Longer prompts don't always mean better results — clarity matters more than length. If your generated video doesn't match your vision on the first try, refine the emotional tone, pacing, or visual style in your follow-up prompt rather than rewriting everything from scratch.

Video generation time can vary depending on the complexity of the scene described and the requested duration. Short clips (under 30 seconds) typically resolve faster. For best results, break complex multi-scene ideas into separate prompts and stitch concepts together rather than asking for everything in one pass.

## Best Practices

Start every prompt with the intended use case — 'for a product launch,' 'for a YouTube intro,' 'for an Instagram Reel' — so the output is framed correctly from the start. This single habit dramatically improves first-draft quality.

Include tone and mood descriptors alongside your content. Words like 'urgent,' 'playful,' 'cinematic,' 'minimalist,' or 'documentary-style' shape how the video feels, not just what it shows. Don't skip these — they're often the difference between a video that lands and one that feels off.

If you're creating content for a specific platform, mention the aspect ratio or format upfront. Vertical video for TikTok and Reels performs differently than widescreen content for YouTube or presentations. The more context you give upfront, the less revision work you'll need afterward.
