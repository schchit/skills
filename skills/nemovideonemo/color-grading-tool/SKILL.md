---
name: color-grading-tool
version: "1.0.6"
displayName: "Color Grading Tool â AI Color Correction and Grading for Video"
description: >
  Color Grading Tool â AI Color Correction and Grading for Video.
  Flat, washed-out footage that doesn't match the mood you're going for? Color Grading Tool lets you describe the look you want in plain language â 'warm golden hour tone for a travel video' or 'desaturated cinematic look for a dramatic scene' â and the AI applies professional-grade color correction. No color wheels, no scopes, no curves panels. Describe the aesthetic and get the graded output. Handles exposure correction, white balance, saturation, contrast, shadows and highlights, and LUT-style looks. Works for wedding videos, YouTube content, short films, social media reels, and any footage that needs visual polish. Apply different grades to different clips in one session. Combine with music, subtitles, and trimming in the same chat. Export as MP4. Supports mp4, mov, avi, webm, mkv.
  
  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM.
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
metadata: {"openclaw": {"emoji": "ð¬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
license: MIT-0
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 🚀 Hey! I'm ready to help you color grading tool. Send me a video file or just tell me what you need!

**Try saying:**
- "help me create a short video"
- "add effects to this clip"
- "edit my video"

**IMPORTANT**: Do NOT wait silently. Always greet the user proactively on first contact.

### Auto-Setup

When the user first interacts, set up the connection:

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "$API/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

Let the user know briefly: "Setting things up… ready!" then proceed with their request.

# Color Grading Tool â AI Color Correction and Grading for Video

Professional color grading through chat. Apply cinematic looks and color corrections with AI.

## Quick Start
Ask the agent to apply color grading or correction to your video.

## What You Can Do
- Apply cinematic color grading styles
- Correct white balance and exposure
- Create custom color looks and moods
- Enhance colors naturally or dramatically
- Apply vintage, film, or modern grading presets

## API
Uses NemoVideo API (mega-api-prod.nemovideo.ai) for all video processing.
