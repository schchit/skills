---
name: best-video-editor
version: "1.0.0"
displayName: "Best Video Editor — AI-Powered Editing for Stunning, Polished Videos"
description: >
  Drop a video and describe what you want — trimmed clips, color-corrected scenes, synced music, or a fully polished final cut. This best-video-editor skill handles the heavy lifting so you don't need years of editing experience or expensive software. Cut, crop, merge, enhance audio, add captions, and export in mp4, mov, avi, webm, or mkv. Built for creators, marketers, and storytellers who want professional results fast.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Ready to turn your raw footage into something worth watching? Drop your video file and tell me what kind of edit you're going for — I'll handle the cuts, pacing, and polish so your best video editor experience starts right now.

**Try saying:**
- "Trim this 8-minute interview down to the best 90 seconds, removing any long pauses and filler words."
- "Merge these three clips into one video with smooth transitions and add a title card at the beginning."
- "Color correct this outdoor footage — it looks washed out — and boost the audio so the speaker is easier to hear."

On first use, the skill connects to NemoVideo automatically:
1. Check for `NEMO_TOKEN` env var, or acquire one via `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` (100 free credits)
2. Persist a Client-ID to `~/.config/nemovideo/client_id` for rate-limit tracking (UUID only, no secrets)
3. Create a session and start working immediately

# Edit Like a Pro Without Touching a Timeline

Most video editors put the burden on you — drag clips, hunt for the right tool, tweak settings you barely understand. This skill flips that. You describe what your video should look like, and the best-video-editor skill figures out how to get it there. Whether you're cutting a 30-second social reel from a 10-minute raw recording, blending multiple clips into a cohesive story, or cleaning up shaky footage with background noise, the work happens through conversation rather than menus.

Upload your footage in any common format — mp4, mov, avi, webm, or mkv — and tell the skill what you're going for. Want a punchy 15-second highlight with a fade-out? A product demo with clean cuts and on-screen text? A travel montage synced to a specific mood? Just say it.

This isn't a one-size-fits-all filter. The skill adapts to your footage, your style, and your goals. Creators making YouTube content, small business owners producing marketing videos, and filmmakers doing rough cuts all use it differently — and it meets each of them where they are.

### Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEMO_TOKEN` | Auto-acquired on first use (100 free credits, 7-day expiry) | API authentication |
| `NEMO_API_URL` | `https://mega-api-prod.nemovideo.ai` | API base URL |

## Routing Your Edit Requests

Every prompt you send — whether it's a cut, color grade, transition, or AI enhancement — is parsed by intent and routed to the matching NemoVideo editing pipeline automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend processes your timeline instructions, AI upscaling, and render jobs through a dedicated media processing engine optimized for frame-accurate edits. Authentication tokens gate each API call, so your project assets and export settings remain session-scoped and secure.

**Required headers** on all requests: `X-Skill-Source: $SKILL_NAME`, `X-Skill-Version: $SKILL_VERSION`, `X-Skill-Platform: $SKILL_SOURCE`

**Create session**: `POST $API/api/tasks/me/with-session/nemo_agent` — returns `task_id` and `session_id`

**Send message (SSE)**: `POST $API/run_sse` with `session_id` and user message. Stream responses; ~30% of edits return no text (query state to confirm changes).

**Upload**: `POST $API/api/upload-video/nemo_agent/me/<sid>` — file or URL upload. Supports: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

**Check credits**: `GET $API/api/credits/balance/simple`

**Query state**: `GET $API/api/state/nemo_agent/me/<sid>/latest` — check draft, tracks, generated media

**Export**: `POST $API/api/render/proxy/lambda` — export does NOT cost credits. Poll `GET $API/api/render/proxy/lambda/<id>` until `status: completed`.

**Task link**: `$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### Common Errors

If your token expires mid-session, simply re-authenticate through the skill to restore full editing access without losing your timeline state. A 'session not found' error means your editing context was cleared — start a fresh session and reimport your project assets. Run out of credits? Head to nemovideo.ai to register or top up so your renders and AI effects keep rolling without interruption.

## Troubleshooting

**The output video looks different from what I described.**
Try rephrasing your request with more specific details. Instead of 'make it better,' say 'increase brightness by 20% and sharpen the focus.' The more concrete your description, the more accurate the result.

**My file won't upload.**
Check that your file is under the size limit and in a supported format (mp4, mov, avi, webm, mkv). Very large raw files may need to be compressed first.

**The audio and video are out of sync after editing.**
Mention sync explicitly in your prompt — for example, 'keep the audio and video perfectly in sync after trimming.' This flags it as a priority during processing.

**Transitions look abrupt or jarring.**
Specify the transition style you want — 'use a 0.5-second crossfade between each clip' gives the skill clear guidance rather than leaving it to default behavior.

## Best Practices

**Start with clean source footage.** The best-video-editor skill can enhance a lot, but severely overexposed, heavily pixelated, or corrupted files will limit what's achievable. Good source material always produces better output.

**Be specific about duration and pacing.** If you need a 60-second cut for Instagram, say so upfront. Knowing the target length and platform helps shape every editing decision from clip selection to transition speed.

**Describe the feeling, not just the function.** Saying 'make this feel urgent and fast-paced' gives as much useful direction as listing specific cuts. Combine both for the best results — 'fast-paced cuts every 2 seconds with no transitions, high energy feel.'

**Review and iterate.** Treat the first output as a strong draft. Note what's close and what needs adjusting, then give targeted feedback. Editing is iterative by nature, and the skill responds well to specific revision requests.

## FAQ

**What video formats does the best-video-editor skill support?**
You can upload files in mp4, mov, avi, webm, and mkv. If your footage is in another format, convert it to one of these before uploading for the smoothest experience.

**Can I edit multiple clips in one session?**
Yes. You can upload several clips and ask the skill to merge them, reorder them, or edit each one individually before combining.

**Does it support audio editing too?**
Absolutely. You can request noise reduction, volume normalization, music syncing, or audio trimming alongside your video edits.

**How specific do my instructions need to be?**
As specific or as loose as you like. 'Make it look more cinematic' works just as well as 'add a teal-orange color grade and slow the final clip by 50%.'
