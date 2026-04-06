---
name: youtube-video-editor-online-free
version: "1.0.0"
displayName: "YouTube Video Editor Online Free — Edit, Trim & Export YouTube-Ready Videos"
description: >
  Tell me what you need and I'll help you shape your footage into a polished YouTube video — no software downloads required. This youtube-video-editor-online-free skill lets you trim clips, cut dead air, add text overlays, adjust pacing, and prepare your content for YouTube's exact specs. Works with mp4, mov, avi, webm, and mkv files. Built for creators who want fast, clean edits without wrestling with complex timelines or paid subscriptions.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Ready to turn your raw footage into a YouTube-ready video? Upload your clip and tell me what you want — trim, cut, clean up, or restructure — and let's get your content ready to publish.

**Try saying:**
- "Trim the first 45 seconds of this vlog and remove the section between 3:10 and 3:40 where I stumble over my words"
- "Cut this 25-minute recording down to under 15 minutes by removing the slow parts and long pauses"
- "Add a text overlay that says 'Subscribe for more!' in the last 10 seconds of this YouTube video"

On first use, the skill connects to NemoVideo automatically:
1. Check for `NEMO_TOKEN` env var, or acquire one via `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` (100 free credits)
2. Persist a Client-ID to `~/.config/nemovideo/client_id` for rate-limit tracking (UUID only, no secrets)
3. Create a session and start working immediately

# Edit YouTube Videos Instantly — No Downloads Needed

Creating content for YouTube means juggling tight pacing, viewer retention, and platform requirements — all before you even hit upload. This skill is built specifically for that workflow. Whether you're a solo creator trimming a gaming session, a small business cutting a product walkthrough, or a vlogger cleaning up a travel diary, you get a focused editing environment designed around YouTube's needs.

Upload your raw footage in mp4, mov, avi, webm, or mkv format and describe what you want done. Need the first 30 seconds cut? Want to remove a stumbled sentence in the middle? Need the video trimmed to under 15 minutes for standard accounts? Just say it in plain language and the skill handles the rest.

This isn't a generic video tool repurposed for YouTube — it's built with YouTube creators in mind. That means attention to aspect ratios, export quality settings that won't get flagged for compression artifacts, and a workflow that respects your time. You stay focused on your content; the editing mechanics stay out of your way.

### Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEMO_TOKEN` | Auto-acquired on first use (100 free credits, 7-day expiry) | API authentication |
| `NEMO_API_URL` | `https://mega-api-prod.nemovideo.ai` | API base URL |

## Routing Edit Requests Intelligently

When you describe a YouTube editing task — trimming dead air, cutting a highlight reel, adding captions, or exporting in 16:9 — ClawHub parses your intent and routes it directly to the appropriate NemoVideo editing pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference Guide

The NemoVideo backend powers all browser-based timeline edits, frame-accurate trims, and YouTube-optimized exports without requiring a desktop install. It processes your footage in the cloud, applies your cut points or transitions, and returns a render-ready file sized for YouTube upload.

**Required headers** on all requests: `X-Skill-Source: $SKILL_NAME`, `X-Skill-Version: $SKILL_VERSION`, `X-Skill-Platform: $SKILL_SOURCE`

**Create session**: `POST $API/api/tasks/me/with-session/nemo_agent` — returns `task_id` and `session_id`

**Send message (SSE)**: `POST $API/run_sse` with `session_id` and user message. Stream responses; ~30% of edits return no text (query state to confirm changes).

**Upload**: `POST $API/api/upload-video/nemo_agent/me/<sid>` — file or URL upload. Supports: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

**Check credits**: `GET $API/api/credits/balance/simple`

**Query state**: `GET $API/api/state/nemo_agent/me/<sid>/latest` — check draft, tracks, generated media

**Export**: `POST $API/api/render/proxy/lambda` — export does NOT cost credits. Poll `GET $API/api/render/proxy/lambda/<id>` until `status: completed`.

**Task link**: `$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### Common Errors

If your token expires mid-session, simply re-authenticate through ClawHub to resume your edit without losing your timeline. A 'session not found' response means your editing session timed out — start a fresh session and re-import your footage. If you're out of credits, head to nemovideo.ai to register or upgrade your plan and unlock continued access to free YouTube video editing tools.

## Performance Notes for Large or Long-Form Files

For videos longer than 20 minutes or files larger than 2GB, breaking your edit requests into logical segments improves accuracy and processing speed. Instead of describing every cut at once, start with the structural edits — removing large unwanted sections — then refine with smaller cuts in a second pass.

Highly compressed source files (such as heavily re-encoded mp4s or low-bitrate avi exports) may show minor quality reduction after editing. Whenever possible, upload the highest-quality version of your original footage to preserve sharpness through the editing process.

Webm files recorded directly from screen capture tools are fully supported and often produce clean results for tutorial and gaming content. If you notice any sync issues between audio and video in your source file, mention it upfront so the skill can account for it during the edit rather than after.

## Best Practices for YouTube Video Editing

When editing for YouTube, pacing is everything. Viewers decide within the first 30 seconds whether to keep watching, so always review your opening cut first — trim any slow intros or dead air before the main content begins. A tight hook in the first 15 seconds dramatically improves average view duration.

For talking-head or tutorial videos, removing filler words, long pauses, and repeated takes makes a significant difference without requiring heavy post-production. When describing your edits, be specific: mention timestamps, speaker names, or describe the scene so the skill can locate the right sections accurately.

Export your final video in mp4 format at 1080p or higher for best YouTube quality. If your source file is in mov, avi, webm, or mkv, the skill handles conversion automatically — just specify your target resolution and YouTube will do the rest on its end during processing.
