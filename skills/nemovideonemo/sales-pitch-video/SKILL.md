---
name: sales-pitch-video
displayName: "Sales Pitch Video Maker — AI Revenue Content"
description: >
  Create persuasive sales pitch and product demo videos with AI-powered conversion content.
version: 1.0.2
author: nemovideo
tags: [video, ai, nemovideo, business]
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
metadata:
  requires:
    env: []
    configPaths:
      - "~/.config/nemovideo/"
  primaryEnv: NEMO_TOKEN
---

# Sales Pitch Video Maker — AI Revenue Content

## Overview

Create impactful sales pitch video content using NemoVideo's AI-powered platform. Produce professional business videos that communicate vision, build credibility, and drive results.

## Examples

### Example 1: Standard Format
**Input:** "Create a professional sales pitch"
**Output:** Polished business video with clear structure, strong messaging, and professional visuals

### Example 2: Investor Version
**Input:** "Make a sales pitch for investors"
**Output:** Data-driven video with market opportunity, traction metrics, and compelling ask

### Example 3: Social Version
**Input:** "Create a 90-second sales pitch for LinkedIn"
**Output:** Professional social version optimized for LinkedIn and business audiences

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| company | string | yes | Company name, stage, or business focus |
| audience | string | no | Target audience (investors, customers, partners, team) |
| duration | number | no | Target duration in seconds (default: 120) |
| tone | string | no | Tone (formal, confident, inspiring, data-driven) |

## Workflow

1. Describe your company and presentation goal
2. NemoVideo AI creates compelling script and storyboard
3. Professional business visuals and graphics are generated
4. Confident narration and corporate music are added
5. Export for your business presentation platform

## API Reference

```bash
curl -X POST https://api.nemovideo.ai/v1/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a sales pitch video", "duration": 120}'
```

## Tips

1. Lead with the problem you solve, not your product features
2. Use specific numbers and metrics wherever possible
3. Keep slides and visuals simple and impactful
4. Practice the narrative before finalizing the video
5. Tailor the ask clearly to the specific audience

## Output Formats

- MP4 (H.264) — Presentation and streaming ready
- WebM — Web platform optimized
- MOV — High quality for investor meetings

## Related Skills

- startup-culture-video
- brand-story-video
- corporate-video-maker
