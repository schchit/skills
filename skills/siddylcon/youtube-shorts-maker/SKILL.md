---
name: youtube-shorts-maker
version: "1.0.4"
displayName: "YouTube Shorts Maker — Create and Edit YouTube Shorts with AI"
description: >
  YouTube Shorts Maker — Create and Edit YouTube Shorts with AI.
  YouTube Shorts has its own rules: vertical format, strong hook in the first 3 seconds, captions for silent viewing, and duration under 60 seconds. YouTube Shorts Maker handles all of it. Upload horizontal footage or start from scratch — the AI reframes, cuts, adds captions, selects audio, and exports a Shorts-optimized file. Describe the hook and content: 'open with the most surprising moment, then explain it in 45 seconds with captions.' Handles auto-captioning, viral transition styles, trending audio integration, and thumbnail frame selection. Works for creators repurposing long-form content, brands building Shorts presence, and anyone targeting YouTube's short-form algorithm. Export as MP4 at YouTube Shorts specs.
  
  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM. Free trial available.
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
license: MIT-0
---

# YouTube Shorts Maker — Create and Edit YouTube Shorts with AI

Specialized creator for YouTube Shorts. Make engaging vertical videos optimized for Shorts format.

## Quick Start
Ask the agent to create or edit a YouTube Shorts video.

## What You Can Do
- Create videos in YouTube Shorts 9:16 format (max 60s)
- Add attention-grabbing hooks for first 3 seconds
- Generate captions and text overlays
- Optimize pacing for short-form content
- Export with YouTube Shorts metadata

## API
Uses NemoVideo API (mega-api-prod.nemovideo.ai) for all video processing.
