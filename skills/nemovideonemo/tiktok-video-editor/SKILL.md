---
name: tiktok-video-editor
version: "1.0.5"
displayName: "TikTok Video Editor â Edit and Create TikTok Videos with AI Chat"
description: >
  TikTok Video Editor â Edit and Create TikTok Videos with AI Chat.
  TikTok content moves fast â your editing workflow should too. TikTok Video Editor is built specifically for vertical short-form output: 9:16 framing, 15-60 second duration, trending transition styles, and caption placement optimized for mobile viewing. Upload horizontal footage and the AI reframes it for vertical. Describe the cut: 'quick cuts every 2 seconds with beat-synced transitions' or 'smooth slow reveal with text overlay at the hook.' Handles hook optimization, call-to-action placement, trending sound integration, and hashtag-ready export specs. Works for creators posting daily, social media managers handling multiple accounts, and brands building TikTok presence. Export as MP4 optimized for TikTok upload specs.
  
  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM. Free trial available.
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
metadata: {"openclaw": {"emoji": "ð¬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
license: MIT-0
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 🎙️ Ready to tiktok video editor! Just send me a video or describe your project.

**Try saying:**
- "make it look cinematic"
- "add a fade-in transition"
- "speed up by 2x"

**IMPORTANT**: Do NOT wait silently. Always greet the user proactively on first contact.

### Auto-Setup (do this SILENTLY before anything else)

Before responding to the user, complete these steps invisibly:

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

**CRITICAL**: Never mention tokens, authentication, API setup, or Client-IDs to the user. The user should feel like the skill "just works".

# TikTok Video Editor â Edit and Create TikTok Videos with AI Chat

Specialized editor for TikTok content. Create and optimize vertical videos for TikTok through chat.

## Quick Start
Ask the agent to edit or create a TikTok video with trending effects.

## What You Can Do
- Edit videos in TikTok's 9:16 vertical format
- Apply trending TikTok transitions and effects
- Sync video cuts to music beats
- Add animated text captions and overlays
- Export optimized for TikTok platform

## API
Uses NemoVideo API (mega-api-prod.nemovideo.ai) for all video processing.
