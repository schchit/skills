---
name: video-to-text-free
version: "1.0.0"
displayName: "Video to Text Free — Instant Transcription From Any Video File"
description: >
  Tell me what you need and I'll pull every spoken word out of your video — no subscriptions, no paywalls, no setup. This video-to-text-free skill converts mp4, mov, avi, webm, and mkv files into clean, readable transcripts you can edit, copy, or repurpose immediately. Perfect for content creators, students, journalists, and anyone who needs accurate text from recorded interviews, lectures, meetings, or social clips. Fast, private, and genuinely free to use.
metadata: {"openclaw": {"emoji": "🎙️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm here to transcribe your video into text — completely free, no account needed. Upload your mp4, mov, avi, webm, or mkv file and tell me what you'd like done with the transcript to get started.

**Try saying:**
- "Transcribe this mp4 interview recording and format it as a clean Q&A"
- "Convert my lecture video to text and highlight any key terms mentioned"
- "Extract all spoken dialogue from this webm clip and give me a plain text transcript"

On first use, the skill connects to NemoVideo automatically:
1. Check for `NEMO_TOKEN` env var, or acquire one via `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` (100 free credits)
2. Persist a Client-ID to `~/.config/nemovideo/client_id` for rate-limit tracking (UUID only, no secrets)
3. Create a session and start working immediately

# Turn Any Video Into Words — Instantly

Ever watched a video and wished you could just read it instead? Or recorded an interview and spent hours typing it out by hand? That's exactly the problem this skill solves. Drop in your video file and get back a full transcript — word for word — without touching a single setting or signing up for anything.

This skill is built for real-world use cases: pulling quotes from a recorded webinar, generating subtitles for a short film, turning a lecture recording into study notes, or extracting dialogue from a client call. Whatever the source, the output is clean, structured text you can immediately work with.

Unlike browser-based tools that cap your file length or hide accuracy behind a pricing tier, this video-to-text-free skill gives you full transcription without compromise. It handles casual speech, multiple speakers, and background noise reasonably well — making it a practical everyday tool rather than a demo. Whether you're a solo creator or a researcher processing dozens of clips, this skill fits into your workflow without friction.

### Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEMO_TOKEN` | Auto-acquired on first use (100 free credits, 7-day expiry) | API authentication |
| `NEMO_API_URL` | `https://mega-api-prod.nemovideo.ai` | API base URL |

## Routing Your Transcription Requests

Every video-to-text request is parsed for file format, language hints, and timestamp preferences before being dispatched to the appropriate NemoVideo transcription endpoint.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend accepts uploaded video files or direct URLs, strips the audio track, and runs it through a speech-recognition pipeline that returns a full verbatim transcript with optional word-level timestamps. Supported formats include MP4, MOV, AVI, MKV, and WebM.

**Required headers** on all requests: `X-Skill-Source: $SKILL_NAME`, `X-Skill-Version: $SKILL_VERSION`, `X-Skill-Platform: $SKILL_SOURCE`

**Create session**: `POST $API/api/tasks/me/with-session/nemo_agent` — returns `task_id` and `session_id`

**Send message (SSE)**: `POST $API/run_sse` with `session_id` and user message. Stream responses; ~30% of edits return no text (query state to confirm changes).

**Upload**: `POST $API/api/upload-video/nemo_agent/me/<sid>` — file or URL upload. Supports: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

**Check credits**: `GET $API/api/credits/balance/simple`

**Query state**: `GET $API/api/state/nemo_agent/me/<sid>/latest` — check draft, tracks, generated media

**Export**: `POST $API/api/render/proxy/lambda` — export does NOT cost credits. Poll `GET $API/api/render/proxy/lambda/<id>` until `status: completed`.

**Task link**: `$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### Common Errors

If your token has expired, simply re-authenticate through the ClawHub interface to generate a fresh session token before resubmitting your video. A 'session not found' error means your session has lapsed — start a new session and re-upload your file. Hitting a credit wall? Head to nemovideo.ai to register for a free account and unlock your transcription credits.

## Troubleshooting

If your transcript comes back with gaps or unclear sections, the most common culprit is audio quality in the original video. Background music, overlapping voices, or a low-quality microphone can reduce accuracy. Try uploading a version of the video with the cleanest audio track possible — even running it through a basic noise reduction tool beforehand can make a noticeable difference.

For very long videos, processing may take a moment longer than expected. If the skill appears to stall, check that your file isn't corrupted by playing it in a local media player first. Files that won't play locally won't transcribe correctly either.

If you're uploading an avi or mkv file and getting an error, confirm the file isn't using an uncommon or legacy codec. Re-exporting to mp4 using a tool like VLC or HandBrake usually resolves codec compatibility issues instantly. When in doubt, mp4 is the most reliable format to use with this video-to-text-free skill.

## Common Workflows

One of the most popular ways people use this skill is for content repurposing. Upload a YouTube video or recorded stream, get the transcript, then use it as the basis for a blog post, newsletter, or social media thread — turning one piece of content into several without writing from scratch.

For researchers and journalists, the workflow typically looks like this: record an interview, upload the file, receive the transcript, then copy it into a document for annotation and quoting. It cuts transcription time from hours to minutes and keeps the original wording intact.

Students often upload recorded lectures or study group sessions and ask for the transcript formatted as bullet-point notes. This is a great way to make video content scannable and easier to review before exams.

Podcast creators also use this video-to-text-free skill to generate show notes. Upload the video version of an episode, transcribe it, then ask for a summary of key topics covered — a complete show notes draft in one step.
