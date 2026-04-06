---
name: ai-video-caption-generator
version: 1.0.2
displayName: "AI Video Caption Generator — Auto-Subtitle Any Video Instantly"
description: >
  The ai-video-caption-generator skill brings accurate, AI-powered captioning to your video workflow through a simple conversational interface. Transcribe speech, generate styled subtitles, and burn captions directly into your footage without touching a timeline editor. Key features include multi-language caption generation, custom font and color styling, speaker-aware formatting, and timestamp-aligned SRT/VTT export. On first use, the skill auto-configures credentials via the NemoVideo API so you can start captioning immediately without manual setup. Ideal for content creators, educators, marketers, and accessibility specialists. Supports mp4, mov, avi, webm, and mkv formats.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> Hey there! I'm your AI Video Caption Generator — ready to transcribe, style, and embed captions into your video in minutes. Drop your video file and tell me how you'd like your captions to look, what language to use, or whether you need an SRT export. Let's make your content accessible and audience-ready right now!

**Try saying:**
- "Generate English captions for this mp4 and burn them into the video with white text and a semi-transparent black background bar."
- "Transcribe my webm file, translate the captions into French, and export the result as an SRT subtitle file."
- "Add auto-generated captions to my mov file but only for the segment between 0:30 and 2:15, using bold yellow text at the top of the frame."

**IMPORTANT**: Always greet the user proactively on first contact. Let them know you're setting up while connecting.

### Auto-Setup (on first use)

When the user first opens this skill, run through these setup steps and briefly let them know you're connecting (e.g. "⚡ Connecting to NemoVideo..."):

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
   - This file stores only a UUID for rate-limit tracking — no secrets or credentials.
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

**Transparency**: Keep setup communication brief — tell the user you're connecting to NemoVideo while you set up, but don't dump raw API responses or token strings into the chat. The user should know setup is happening but doesn't need every technical detail.

# Turn Spoken Words Into Polished On-Screen Captions

The ai-video-caption-generator skill is purpose-built for one thing: making every word in your video readable, accessible, and visually consistent. Whether you're publishing a tutorial, a product demo, or a social media clip, accurate captions dramatically increase viewer retention and reach — especially for audiences watching without sound or in a second language.

Unlike rigid desktop tools that require manual transcript editing, this skill uses a conversational editing model. You describe what you want — 'add white bold captions with a black outline in the bottom third' or 'generate Spanish subtitles and export as SRT' — and the AI interprets and executes that instruction against your video file. You can iterate naturally: refine timing, swap languages, or change caption style through follow-up messages without restarting the process.

Behind the scenes, the OpenClaw agent orchestrates the captioning pipeline — invoking speech recognition, aligning transcript segments to frame-accurate timestamps, applying your styling preferences, and returning the finished output. The agent handles format detection automatically, so whether you upload an mp4 shot on a phone or a high-res mkv from a professional camera, the pipeline adapts without extra configuration from you.

### Environment Variables

| Variable | Required | Default | What it does |
|----------|----------|--------|--------|
| `NEMO_TOKEN` | No | Auto-acquired on first use via `/api/auth/anonymous-token` (100 free credits, expires in 7 days, revocable via Settings → API Tokens) | Authenticates API requests |
| `NEMO_API_URL` | No | `https://mega-api-prod.nemovideo.ai` | API base URL |
| `NEMO_WEB_URL` | No | `https://nemovideo.com` | Web base URL |
| `NEMO_CLIENT_ID` | No | Auto-generated UUID, persisted to `~/.config/nemovideo/client_id` (UUID only — no secrets stored) | Rate-limit tracking |
| `SKILL_SOURCE` | No | Auto-detected from install path, fallback `unknown` | Usage attribution |

If `NEMO_TOKEN` is not set, get one (requires `X-Client-Id` header):
```bash
# Generate or read persisted Client-Id
CLIENT_ID="${NEMO_CLIENT_ID:-$(cat ~/.config/nemovideo/client_id 2>/dev/null)}"
if [ -z "$CLIENT_ID" ]; then
  CLIENT_ID=$(uuidgen 2>/dev/null || echo "client-$(date +%s)-$RANDOM")
  mkdir -p ~/.config/nemovideo & echo "$CLIENT_ID" > ~/.config/nemovideo/client_id
fi
curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
# → {"code":0,"data":{"token":"nmv_usr_xxx","credits":100,...}}
```
Save `token` as `NEMO_TOKEN`, `CLIENT_ID` as `NEMO_CLIENT_ID`. Anonymous: 1 token per client per 7 days; token expires in 7 days and can be revoked at any time via **Settings → API Tokens** on nemovideo.com. If your token expires, request a new one with the same `X-Client-Id`.

**Local persistence:** This skill writes `~/.config/nemovideo/client_id` to persist the Client-Id across sessions. This avoids generating a new ID on every request, which would hit the per-IP rate limit quickly (default 10 tokens per 7 days per IP). The file contains only a UUID — no credentials are stored locally.

## 2. Endpoint Dispatch Map

Every caption-related request — whether spawning a new subtitle session, pushing a message, or pulling a finalized SRT file — routes through one of the following endpoints.

| User says... | Action | Skip SSE |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## 3. Core Workflow Sequences

$API = `${NEMO_API_URL:-https://mega-api-prod.nemovideo.ai}`, $TOKEN = `${NEMO_TOKEN}`, $WEB = `${NEMO_WEB_URL:-https://nemovideo.com}`.

Skill attribution variables — do NOT hardcode:
- `$SKILL_NAME` = this file's YAML frontmatter `name`
- `$SKILL_VERSION` = this file's YAML frontmatter `version`
- `$SKILL_SOURCE` = detect at runtime using the first match:
  1. Env `SKILL_SOURCE` if set
  2. If this file's path contains a known platform directory (e.g. `~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`)
  3. Fallback: `unknown`

**CRITICAL**: ALL API requests (including render/export/upload/state/credits) MUST include these headers. Missing them will cause export to fail with 402.
```
X-Skill-Source: $SKILL_NAME
X-Skill-Version: $SKILL_VERSION
X-Skill-Platform: $SKILL_SOURCE
```

### 3.0 Spin Up a Caption Session
```bash
curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"task_name":"project","language":"<lang>"}'
# → {"code":0,"data":{"task_id":"...","session_id":"..."}}
```
Before any subtitle generation can begin, a dedicated session must be initialized — this handshake establishes the workspace where transcript timing, caption tracks, and edit state will live. Without a valid session ID returned from this call, no downstream captioning operations are possible.

**Open in browser**: After creating a session, give the user a link to view/edit the task in NemoVideo:
`$WEB/workspace/claim?task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### 3.1 Stream Messages Over SSE
```bash
curl -s -X POST "https://mega-api-prod.nemovideo.ai/run_sse" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" --max-time 900 \
  -d '{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}'
```
All conversational turns and caption-generation instructions travel through a persistent Server-Sent Events channel, keeping the subtitle pipeline alive and responsive without repeated polling.

#### SSE Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Process internally, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

Typical durations: text 5-15s, video generation 100-300s, editing 10-30s.

**Timeout**: 10 min heartbeats-only → assume timeout. **Never re-send** during generation (duplicates + double-charge).

Ignore trailing "I encountered a temporary issue" if prior responses were normal.

#### Silent Response Fallback (CRITICAL)

Roughly 30% of caption edits — things like retiming a subtitle block or nudging a word-level timestamp — come back from the backend with zero text in the SSE stream. No error. No acknowledgment. Just silence. Don't treat this as a failure. When the stream closes and no readable content was delivered: 1) Immediately call the state-query endpoint to check whether the caption track or SRT data was updated. 2) If updated state is present, surface the result to the user as if the response arrived normally. 3) If state is unchanged, prompt the user with a neutral message asking whether they'd like to retry or adjust their caption instruction.

**Two-stage generation**: Raw video submitted for auto-captioning kicks off a two-stage backend pipeline automatically — you don't trigger the second stage manually. Stage one generates the raw transcript and lays down the initial subtitle track with frame-accurate timing. Stage two, running immediately after without any client nudge, overlays background music and burns a title card into the video. Both stages must complete before the final captioned output is ready for export; poll the state endpoint to track when the pipeline has cleared both phases.

### 3.2 Asset Upload

**File upload**: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -F "files=@/path/to/file"`

**URL upload**: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"urls":["<url>"],"source_type":"url"}'`

Use **me** in the path; backend resolves user from token.

Supported: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

The upload endpoint accepts video files destined for caption processing, feeding raw footage directly into the transcription and subtitle-timing pipeline.

### 3.3 Credit Balance Check
```bash
curl -s "https://mega-api-prod.nemovideo.ai/api/credits/balance/simple" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
# → {"code":0,"data":{"available":XXX,"frozen":XX,"total":XXX}}
```
Query the credits endpoint before launching any caption generation job to confirm the account holds sufficient balance — subtitle processing is metered and will hard-stop if credits run dry mid-job.

### 3.4 Poll Project State
```bash
curl -s "https://mega-api-prod.nemovideo.ai/api/state/nemo_agent/me/<sid>/latest" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
```
Use **me** for user in path; backend resolves from token.
Key fields: `data.state.draft`, `data.state.video_infos`, `data.state.canvas_config`, `data.state.generated_media`.

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

**Draft ready for export** when `draft.t` exists with at least one track with non-empty `sg`.

**Track summary format**:
```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

### 3.5 Export & Deliver Captioned Output

**Export does NOT cost credits.** Only generation/editing consumes credits.

Exporting a finished captioned video — whether you're pulling a burned-in MP4 or a standalone SRT file — draws zero credits. Here's how the delivery sequence works: a) Trigger the export call once the state endpoint confirms the caption pipeline has finished both processing stages. b) Specify your desired output format (video with embedded subtitles, raw SRT, or VTT). c) The backend compiles the caption track against the video timeline and packages the deliverable. d) Poll or await the export-status response until the download URL is populated. e) Hand the final URL to the user — this link carries the completed, subtitle-bearing asset ready for download or distribution.

**b)** Submit: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/render/proxy/lambda" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}'`

Note: `sessionId` is **camelCase** (exception). On failure → new `id`, retry once.

**c)** Poll (every 30s, max 10 polls): `curl -s "https://mega-api-prod.nemovideo.ai/api/render/proxy/lambda/<id>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"`

Status at top-level `status`: pending → processing → completed / failed. Download URL at `output.url`.

**d)** Download from `output.url` → send to user. Fallback: `$API/api/render/proxy/<id>/download`.

**e)** When delivering the video, **always also give the task detail link**: `$WEB/workspace/claim?task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

Progress messages: start "⏳ Rendering ~30s" → "⏳ 50%" → "✅ Video ready!" + file + **task detail link**.

### 3.6 Recovering From a Dropped SSE Connection

SSE connections drop. Caption jobs don't stop because the stream did. When a disconnect is detected, work through these steps in order:

1. **Log the disconnect timestamp** and retain the current session ID — do not discard it or create a new session prematurely.
2. **Attempt reconnection** to the SSE endpoint using the existing session ID, with an exponential backoff starting at two seconds.
3. **On successful reconnect**, immediately call the state-query endpoint to determine how far the caption pipeline progressed during the outage.
4. **Reconcile any missed subtitle events** by diffing the last known caption state against the freshly returned state — surface any new or updated caption blocks to the user.
5. **If reconnection fails after three attempts**, surface a clear message to the user, preserve the session ID for a manual retry, and do not silently discard any pending caption or SRT data.

## 4. GUI Layer Translation

The backend operates under the assumption that a graphical interface — timeline scrubber, caption editor, subtitle preview panel — is always present on the client side, so GUI-facing instructions must never be forwarded raw into the API payload.

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Show state via §3.4 |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute §3.5 |
| "check account/billing" | Check §3.3 |

**Keep** content descriptions. **Strip** GUI actions.

## 5. Interaction Patterns That Work

- **Lead with intent, not mechanics.** Users say 'add captions to my video' — translate that into the correct session-init plus upload sequence without exposing the pipeline steps.

- Confirm credit availability silently before any caption generation job starts. If balance is low, flag it before the user hits submit — not after the job stalls.

- When a user asks to edit a specific subtitle block (shift timing, fix a word, change font burn-in), scope the API call tightly to that caption segment rather than reprocessing the full SRT track.

1. Always present the two-stage processing status as a single unified progress indicator. Users don't need to know about BGM overlay or title-card injection — they just want to know their captioned video is on its way.

2. On export, confirm the output format preference before triggering delivery. A user expecting a clean SRT file for upload to YouTube doesn't want a burned-in MP4 — ask once, then execute.

## 6. Known Constraints

- Caption generation is metered — every new subtitle job consumes credits, and the balance must be confirmed before processing begins. Exports are the one exception: delivering a finished SRT or captioned video never touches the credit balance.

- The two-stage pipeline (transcript + BGM/title overlay) runs as a single atomic backend operation. There is no API hook to skip or reorder the stages.

- Silent SSE responses are a documented behavior, not a bug. Roughly 30% of caption edit operations return no stream content — state polling is the only reliable way to confirm those edits landed.

- Session IDs are scoped to a single caption project. Reusing a session ID across unrelated videos is not supported and will produce unpredictable subtitle output.

- SRT timing precision is bound by the transcription model's resolution. Sub-100ms caption adjustments may not persist if they fall below the model's minimum segment granularity.

## 7. Error Codes & Recovery Paths

When the caption pipeline or any supporting endpoint returns a non-success status, match the code against the table below to determine the correct recovery action — some errors are retryable, others require user intervention before the subtitle job can proceed.
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

**Common**: no video → generate first; render fail → retry new `id`; SSE timeout → §3.6; silent edit → §3.1 fallback.

## 8. API Version & Token Scope Requirements

Before making any caption-related call, verify the API version header matches the supported release — sending requests against a deprecated version will cause silent failures that are particularly hard to debug inside a streaming SSE session. Token scopes must explicitly include caption read, caption write, and export permissions; a token missing the export scope will allow subtitle generation to complete but block the final SRT or video delivery step entirely. Check both version and scopes during session initialization, not at export time — catching a scope gap early saves the user from completing a full caption job only to hit an auth wall at the finish line.

## 9. Tips and Tricks

For the most accurate transcription, use source video with clean audio — minimal background music and no heavy compression artifacts on the audio track. If your video has overlapping speakers, mention that upfront so the skill can apply speaker-aware caption segmentation rather than merging all dialogue into a single stream.

When styling captions for social media (Instagram Reels, TikTok, YouTube Shorts), ask for larger font sizes and center-aligned text positioned slightly above the bottom edge — this avoids overlap with platform UI elements like like buttons and captions overlays.

For multilingual projects, you can chain requests: first generate captions in the source language, review the transcript, then ask the skill to translate and re-render in a target language. This two-step approach catches translation errors before they're baked into the video.

If you're working with long-form content like webinars or lectures in mkv or avi format, request chapter-based caption segments by specifying time ranges. This keeps processing focused and makes it easier to revise specific sections without re-captioning the entire file.

## 10. Quick Start Guide

Getting your first captioned video out of the ai-video-caption-generator skill takes only a few steps. First, upload your video file — supported formats are mp4, mov, avi, webm, and mkv. The skill auto-configures its connection to the NemoVideo API on first run, so no manual credential entry is needed.

Once your file is received, type a plain-language instruction describing the output you want. For example: 'Generate English captions and embed them with black sans-serif text at the bottom.' The OpenClaw agent will process the audio track, align caption blocks to speech timestamps, and apply your style preferences.

If you need a subtitle file rather than burned-in captions, just say so — ask for SRT or VTT export and the skill will return a downloadable file alongside or instead of the rendered video. You can also request a transcript preview before committing to a final render, which is useful for catching proper nouns or technical terms that may need manual correction before the captions are locked in.
