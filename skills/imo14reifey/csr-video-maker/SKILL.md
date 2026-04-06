---
name: csr-video-maker
displayName: "CSR Video Maker — AI Corporate Social Responsibility"
description: >
  Create impactful corporate social responsibility and sustainability videos with AI production.
version: 1.0.2
author: nemovideo
tags: [video, ai, nemovideo, nonprofit]
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

# CSR Video Maker — AI Corporate Social Responsibility

## Overview

Create impactful csr video maker content using NemoVideo's AI-powered platform. Produce emotionally resonant videos that inspire action, build trust, and drive meaningful change.

## Examples

### Example 1: Emotional Appeal
**Input:** "Create a csr emotional appeal"
**Output:** Heartfelt video with real stories, clear impact data, and compelling ask

### Example 2: Impact Report
**Input:** "Make a csr impact report video"
**Output:** Professional results video showing metrics, stories, and future goals

### Example 3: Social Version
**Input:** "Create a 60-second csr for social"
**Output:** Shareable short version optimized for social media amplification

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| cause | string | yes | Mission, campaign, or social impact focus |
| audience | string | no | Target audience (donors, volunteers, public, partners) |
| duration | number | no | Target duration in seconds (default: 120) |
| tone | string | no | Tone (urgent, hopeful, grateful, inspiring) |

## Workflow

1. Describe your cause and campaign goal
2. NemoVideo AI creates emotionally compelling script and storyboard
3. Impactful visuals and beneficiary stories are generated
4. Sincere narration and moving music are added
5. Export for your fundraising and advocacy platforms

## API Reference

```bash
curl -X POST https://api.nemovideo.ai/v1/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a csr video maker", "duration": 120}'
```

## Tips

1. Lead with a specific person or story, not statistics
2. Show the problem clearly before presenting the solution
3. Make the donation or action ask specific and urgent
4. Include social proof from existing donors or volunteers
5. End with gratitude and vision of future impact

## Output Formats

- MP4 (H.264) — Website and campaign platform ready
- WebM — Web streaming optimized
- MOV — High quality for grant applications

## Related Skills

- charity-video-maker
- fundraising-video
- community-event-video
