---
name: pixabay-music-ab2n-0330
version: "1.0.0"
displayName: "Pixabay Music Finder — Discover & Add Free Royalty-Free Tracks to Your Videos"
description: >
  Tell me what you need and I'll find the perfect royalty-free track from Pixabay's vast music library to match your video's mood, pace, or theme. This pixabay-music skill searches, previews, and pairs background music with your video content — covering genres from cinematic and ambient to upbeat and lo-fi. Whether you're a content creator, marketer, or filmmaker, you get instant access to free-to-use music without copyright headaches. Supports mp4, mov, avi, webm, and mkv video formats.
metadata: {"openclaw": {"emoji": "🎵", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm here to help you find the perfect royalty-free music from Pixabay for your video project. Tell me the mood, genre, or style you're going for — and let's find a track that makes your footage come alive! 🎶

**Try saying:**
- "Find me a calm, ambient instrumental track from Pixabay for a meditation video I'm editing"
- "I need an upbeat, energetic song from Pixabay to use as background music in my fitness reel"
- "Search Pixabay for a cinematic orchestral track that fits a dramatic travel documentary"

### Automatic Setup

On first interaction, connect to the NemoVideo API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/nemovideo/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to the same host at `/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Your Videos Deserve a Soundtrack That Actually Fits

Finding the right background music for a video used to mean hours of browsing stock sites, second-guessing licenses, and hoping the track doesn't get your content flagged. The pixabay-music skill cuts through all of that by connecting you directly to Pixabay's curated library of royalty-free tracks — free for personal and commercial use, no strings attached.

Describe the feeling you want your video to carry — tense and dramatic, warm and nostalgic, energetic and punchy — and this skill surfaces tracks that genuinely match. You can search by mood, genre, tempo, or even the type of scene you're scoring. Think 'upbeat corporate background for a product demo' or 'soft acoustic guitar for a travel montage' and get results that actually make sense.

Once you've found the right track, the skill can guide you through pairing it with your video file. It works with all common video formats including mp4, mov, avi, webm, and mkv, making it a practical tool whether you're editing a YouTube vlog, a brand reel, a short film, or social media content.

## How Your Music Requests Route

When you describe a mood, genre, or tempo — say 'upbeat acoustic' or 'cinematic ambient' — ClawHub parses your intent and fires the right Pixabay Music API call to surface matching royalty-free tracks instantly.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Backend Reference

All Pixabay music searches and video attachment actions run through the NemoVideo backend, which handles API authentication, track metadata retrieval, and direct embedding of royalty-free audio into your video projects. Your session token keeps everything linked — lose it, and the pipeline stalls.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `pixabay-music`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=pixabay-music&skill_version=1.0.0&skill_source=<platform>`

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

## Frequently Asked Questions

**Can I use Pixabay music in commercial projects?** Yes. Tracks available through Pixabay are released under the Pixabay License, which allows use in commercial and non-commercial projects without requiring attribution — though crediting the artist is always appreciated.

**How specific can my music search be?** Quite specific. You can describe a mood ('melancholic and slow'), a genre ('jazz with piano'), an energy level ('high-tempo EDM'), or even a scenario ('background music for a cooking tutorial'). The more detail you give, the better the match.

**What video formats does this skill support?** The pixabay-music skill works with mp4, mov, avi, webm, and mkv files, covering the most common formats used by creators and editors.

**Will the music loop or cut off mid-video?** The skill helps you select tracks with appropriate length or suggests loopable options for longer videos so the audio fits naturally without awkward endings.

## Best Practices for Getting Great Results

**Be descriptive about your scene, not just the genre.** Instead of asking for 'happy music,' try 'cheerful background music for a kids' birthday party montage.' The more context you give about what's happening on screen, the more accurately the skill can match the emotional tone of the track to your footage.

**Consider your video's pacing.** A fast-cut action sequence needs a track with a strong beat and consistent tempo, while a slow nature timelapse benefits from something atmospheric and evolving. Mention your edit's pace when searching — it makes a real difference.

**Preview before committing.** Pixabay offers full previews for every track. Use this skill to narrow down your top two or three options, then listen against your actual footage before making a final choice. What sounds great in isolation sometimes clashes with dialogue or sound effects.

**Check track length early.** If your video is three minutes long, filtering for tracks over two and a half minutes saves you from needing to loop or awkwardly fade out. Mention your video's runtime upfront to get better-suited suggestions from the start.
