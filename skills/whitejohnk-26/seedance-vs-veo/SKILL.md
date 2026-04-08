---
name: seedance-vs-veo
version: "1.0.0"
displayName: "Seedance vs Veo — Compare AI Video Generators Side by Side"
description: >
  Just drop a text prompt and this skill runs it through both Seedance and Veo, returning 2 MP4 clips for direct comparison. It's built for teams deciding which model to standardize on before committing to API costs. Each output includes frame rate, resolution (up to 1080p), and generation time so you're comparing actual numbers, not impressions.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "greeting_v2"}}
---

## Getting Started

> Paste a video prompt and I'll generate one MP4 from Seedance and one from Veo for side-by-side review. No prompt? Describe the scene you want to test.

**Try saying:**
- "Run 'a red sports car drifting on a rain-slicked road at night' through both Seedance and Veo and show me the MP4s"
- "Compare how Seedance and Veo handle the prompt 'a hummingbird hovering near a flower in slow motion' — I need to see motion quality differences"
- "Test this prompt on both models: 'a chef plating a dish in a modern kitchen' — include generation time and resolution in the results"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Run One Prompt, Get Two AI Videos Back

Type a single text prompt — say, "a cyclist riding through a foggy forest at dawn" — and the skill sends it to both Seedance and Veo simultaneously. You get 2 MP4 files, each labeled with model name, resolution, and generation time in seconds.

The comparison covers motion consistency, text adherence, and artifact frequency across a 3–8 second clip range. It doesn't rewrite your prompt for either model. What you write is what both models receive, keeping the test fair.

Results land in a side-by-side layout with metadata attached. You can re-run the same prompt 3 times to check output variance per model.

## Routing Prompts Between Models

Your input gets parsed for model-specific keywords — 'Seedance' routes to ByteDance's API endpoint, 'Veo' routes to Google DeepMind's endpoint, and anything ambiguous triggers a side-by-side comparison job that fires both simultaneously.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## API Calls and GPU Queues

Each generation request hits the respective cloud rendering pipeline — Seedance queues on ByteDance's distributed GPU cluster while Veo processes through Google's TPU-backed infrastructure, so wait times differ based on each provider's current load. Response payloads return a signed video URL, generation latency in milliseconds, and the exact prompt echo used after any internal rewriting.

Headers are derived from this file's YAML frontmatter. `X-Skill-Source` is `seedance-vs-veo`, `X-Skill-Version` comes from the `version` field, and `X-Skill-Platform` is detected from the install path (`~/.clawhub/` = `clawhub`, `~/.cursor/skills/` = `cursor`, otherwise `unknown`).

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`.

**Send message (SSE)**: POST `/run_sse` — body `{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}` with `Accept: text/event-stream`. Max timeout: 15 minutes.

**Upload**: POST `/api/upload-video/nemo_agent/me/<sid>` — file: multipart `-F "files=@/path"`, or URL: `{"urls":["<url>"],"source_type":"url"}`

**Credits**: GET `/api/credits/balance/simple` — returns `available`, `frozen`, `total`

**Session state**: GET `/api/state/nemo_agent/me/<sid>/latest` — key fields: `data.state.draft`, `data.state.video_infos`, `data.state.generated_media`

**Export** (free, no credits): POST `/api/render/proxy/lambda` — body `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll GET `/api/render/proxy/lambda/<id>` every 30s until `status` = `completed`. Download URL at `output.url`.

Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### Reading the SSE Stream

Text events go straight to the user (after GUI translation). Tool calls stay internal. Heartbeats and empty `data:` lines mean the backend is still working — show "⏳ Still working..." every 2 minutes.

About 30% of edit operations close the stream without any text. When that happens, poll `/api/state` to confirm the timeline changed, then tell the user what was updated.

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

### Error Codes

- `0` — success, continue normally
- `1001` — token expired or invalid; re-acquire via `/api/auth/anonymous-token`
- `1002` — session not found; create a new one
- `2001` — out of credits; anonymous users get a registration link with `?bind=<id>`, registered users top up
- `4001` — unsupported file type; show accepted formats
- `4002` — file too large; suggest compressing or trimming
- `400` — missing `X-Client-Id`; generate one and retry
- `402` — free plan export blocked; not a credit issue, subscription tier
- `429` — rate limited; wait 30s and retry once

## Quick Start Guide

Write a prompt between 10 and 80 words. Shorter prompts under 15 words tend to produce more variance between models, which makes the comparison more informative.

Submit it here — don't adjust phrasing for either model. The skill sends the identical string to both Seedance and Veo, then returns 2 labeled MP4 files, each capped at 1080p and between 3–8 seconds long.

Check the metadata block attached to each file. It lists model name, resolution, aspect ratio, and wall-clock generation time in seconds. Use those numbers when writing up your evaluation, not subjective impressions.

Re-run the same prompt 3 times if you need variance data. Output consistency differs between the two models, and a single run won't show that.

## Troubleshooting

If one MP4 returns blank or corrupted, the model timed out — generation cutoff is 90 seconds per model. Resubmit the prompt once before assuming a model-side failure.

Prompts over 150 characters sometimes cause Veo to truncate scene elements. Split long prompts into a core scene description (under 100 characters) plus a style note to keep both models working from equivalent inputs.

If both clips look identical, your prompt is likely too generic. Add at least 2 specific visual details — lighting condition, subject motion, camera angle — to create testable differences between the models' outputs.

Resolution mismatches (e.g., one file at 720p and one at 1080p) aren't a bug. The two models don't share a resolution default. Check the metadata block on each file rather than eyeballing clip size.
