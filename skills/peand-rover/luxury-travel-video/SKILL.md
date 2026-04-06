---
name: luxury-travel-video
displayName: "Luxury Travel Video Maker — AI Premium Destination"
description: >
  Create stunning luxury travel videos showcasing world-class hotels and experiences with AI.
version: 1.0.1
author: nemovideo
tags: [video, ai, nemovideo, travel]
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
metadata:
  requires:
    env: []
    configPaths:
      - "~/.config/nemovideo/"
  primaryEnv: NEMO_TOKEN
---

# Luxury Travel Video Maker — AI Premium Destination

## Overview

Create captivating luxury travel video content using NemoVideo's AI-powered platform. Produce stunning travel and adventure videos that inspire wanderlust and share the beauty of the world.

## Examples

### Example 1: Destination Guide
**Input:** "Create a luxury travel destination guide"
**Output:** Inspiring travel guide with highlights, tips, and stunning visuals

### Example 2: Travel Diary
**Input:** "Make a personal luxury travel travel diary"
**Output:** Authentic personal travel story with narrative arc and memorable moments

### Example 3: Quick Tips
**Input:** "Create top 5 luxury travel tips"
**Output:** Practical, shareable tips video for fellow travelers

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| destination | string | yes | Location, region, or travel theme |
| style | string | no | Style (guide, vlog, documentary, tips) |
| duration | number | no | Target duration in seconds (default: 240) |
| audience | string | no | Target audience (budget, luxury, family, solo) |

## Workflow

1. Describe your destination and travel story
2. NemoVideo AI creates vivid, engaging script and storyboard
3. Stunning destination visuals and travel footage are generated
4. Inspiring narration and atmospheric music are added
5. Export for your travel content platform

## API Reference

```bash
curl -X POST https://api.nemovideo.ai/v1/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a luxury travel video", "duration": 240}'
```

## Tips

1. Lead with the most visually stunning shot as a hook
2. Include practical information such as cost and transport
3. Show authentic local culture and off-the-beaten-path spots
4. Use wide shots for landscape and scale context
5. Add location references and links for easy trip planning

## Output Formats

- MP4 (H.264) — YouTube and travel platform ready
- WebM — Web streaming optimized
- MOV — High quality for travel media

## Related Skills

- beach-vacation-video
- city-guide-video
- cultural-travel-video
