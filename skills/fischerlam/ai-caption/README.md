# ai-caption

[![ClawHub Skill](https://img.shields.io/badge/ClawHub-Skill-blueviolet)](https://clawhub.io)
[![Version](https://img.shields.io/badge/version-1.0.6-blue)](SKILL.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> **AI Caption.**
> 给视频自动加字幕，适合短视频、口播、讲解类内容。
>
> Powered by [Sparki](https://sparki.io).

## What It Does

This skill is a scenario-focused wrapper around Sparki's AI video editing workflow.

- Uploads a video file
- Creates an AI processing job with scene-specific defaults
- Polls until processing completes
- Returns a result download URL

## Quick Start

```bash
export SPARKI_API_KEY="sk_live_your_key_here"
RESULT_URL=$(bash scripts/edit_video.sh my_video.mp4 "24" "add clean readable captions and keep the pacing tight" "9:16")
echo "$RESULT_URL"
```

## Best For
- “帮我加字幕”
- “给这个视频自动上字”
- “add captions / subtitles”
- “让这个视频更适合无声观看”

## Notes
- Requires `SPARKI_API_KEY`
- Uses the same reliable scripts as the cleaned `ai-video-editor` fork
- Supports `9:16`, `1:1`, `16:9`
