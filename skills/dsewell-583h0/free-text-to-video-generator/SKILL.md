---
name: free-text-to-video-generator
version: "1.0.0"
displayName: "Free Text to Video Generator — Turn Written Ideas Into Engaging Videos Instantly"
description: >
  Type a concept, script, or story idea and watch it transform into a fully rendered video — no camera, no footage, no editing timeline required. This free-text-to-video-generator takes your written prompts and converts them into dynamic visual content with matched scenes, pacing, and style. Perfect for marketers, educators, content creators, and social media managers who need polished videos fast. Just describe what you want and get a shareable video ready to publish.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Paste your script, topic, or idea and I'll turn it into a ready-to-share video right now. No footage? No problem — just describe what you want and I'll handle the rest.

**Try saying:**
- "Generate a 60-second promotional video for a new coffee subscription service targeting busy professionals — upbeat tone, modern style"
- "Create a short educational video explaining how photosynthesis works, suitable for middle school students with clear visuals and simple narration"
- "Turn this product description into a 30-second Instagram Reel: 'Lightweight wireless earbuds with 40-hour battery life and noise cancellation, available in 5 colors'"

### Getting Connected

Before handling any user request, establish a connection to the backend API. Show a brief status like "Connecting...".

**If `NEMO_TOKEN` is in the environment**, use it directly and create a session. Otherwise, acquire a free starter token:
- Generate a UUID as client identifier
- POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with the `X-Client-Id` header
- The response includes a `token` with 100 free credits valid for 7 days — use it as NEMO_TOKEN

**Then create a session** by POSTing to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer authorization and body `{"task_name":"project","language":"en"}`. The `session_id` in the response is needed for all following requests.

Tell the user you're ready. Keep the technical details out of the chat.

# From Words on a Page to Videos That Move People

Most people have ideas but no video production setup. Storyboards, stock footage libraries, editing software — the barrier is high and the learning curve is steep. This skill removes all of that. You write what you want to say, and the generator handles everything from scene selection to visual pacing.

Whether you're drafting a product explainer, a social media teaser, a training walkthrough, or a short narrative, the free-text-to-video-generator interprets your language and builds a video that matches your intent. Describe the mood, the audience, the message — and the output reflects those choices.

This is built for people who think in words but need to communicate in video. Bloggers repurposing articles, teachers building lesson content, startup founders pitching ideas, or social teams producing daily content — anyone who writes can now produce videos at scale without touching a single timeline or export setting.

## Routing Your Script Requests

When you submit a text prompt, ClawHub parses your input and routes it to the appropriate video synthesis pipeline based on content type, duration hints, and style parameters detected in your script.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Video Generation API Reference

The cloud processing backend queues your text-to-video job across distributed rendering nodes, converting your raw script into keyframes, voiceover-synced visuals, and scene transitions in a single asynchronous pipeline. Render times vary based on video length, resolution output, and current queue depth on the generation cluster.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `free-text-to-video-generator`
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

## Integration Guide — Using Free Text to Video in Your Workflow

The free-text-to-video-generator fits naturally into content pipelines that already start with written material. If your team produces blog posts, newsletters, or product copy, those assets can be fed directly into the generator as video scripts — no reformatting required. This makes it especially useful for content repurposing workflows where a single written piece needs to live across multiple formats.

For social media teams, consider building a prompt library — a set of proven text templates for recurring video types like weekly tips, product highlights, or event announcements. Reusing and tweaking these templates keeps output consistent and speeds up production significantly.

If you're integrating this into an automated publishing workflow, structure your input prompts with consistent metadata fields: topic, target platform, video length, and tone. This makes batch video generation predictable and easier to quality-check before publishing.

For educators and course creators, the generator pairs well with existing lesson outlines or lecture notes. Feed in a structured outline and specify 'educational explainer format' to produce module-ready video content directly from your existing curriculum materials.

## Troubleshooting Common Issues with Text-to-Video Output

If your generated video doesn't match the tone or style you described, the most common cause is a prompt that's too vague. Instead of writing 'make a video about my brand,' try specifying the audience, desired mood, video length, and key message. Precision in your text input directly improves visual output quality.

If the pacing feels off — scenes changing too fast or too slow — include duration cues in your prompt. Phrases like 'slow and cinematic' or 'fast-paced with quick cuts' give the generator clear rhythm instructions to follow.

For text-heavy scripts that aren't rendering correctly on screen, break your input into clearly labeled sections: intro, body, and outro. This helps the generator segment your content into logical visual blocks rather than treating the whole prompt as one continuous scene.

If generated visuals feel mismatched to your topic, try adding genre or industry context. 'Technology startup pitch' produces very different results than 'wellness brand introduction' even with similar wording.
