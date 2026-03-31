---
name: ai-video-resize
version: 1.0.1
displayName: "AI Video Resize — Resize and Reframe Videos for Every Platform with AI"
description: >
  Resize and reframe videos for every platform with AI — convert 16:9 landscape to 9:16 vertical, 1:1 square, 4:5 tall, and any custom aspect ratio with intelligent subject tracking. NemoVideo does not just crop — it reframes: tracking faces, following action, centering key elements, and ensuring nothing important is cut off. One source video becomes platform-native versions for YouTube, TikTok, Instagram Reels, Instagram Feed, LinkedIn, Facebook, Twitter, and Pinterest simultaneously. Resize video AI, reframe video, video aspect ratio changer, landscape to portrait video, video format converter, multi-platform video resize, smart crop video.
metadata: {"openclaw": {"emoji": "📐", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# AI Video Resize — One Video. Every Platform. Every Aspect Ratio.

Every platform demands a different shape. YouTube: 16:9 landscape. TikTok: 9:16 vertical. Instagram Reels: 9:16. Instagram Feed: 1:1 or 4:5. LinkedIn: 16:9 or 1:1. Facebook: 16:9, 1:1, or 4:5. Pinterest: 2:3 or 9:16. Twitter: 16:9 or 1:1. A single video published to all major platforms needs 4-6 different aspect ratio versions. The traditional approach: open editing software, duplicate the project, manually reposition the frame for each aspect ratio, adjust text overlay positions, re-render each version. For one video: 30-60 minutes of reformatting work. For 10 videos per week: 5-10 hours of purely mechanical reformatting — no creative value, just pixel pushing. Simple cropping is not the answer. Center-cropping a 16:9 video to 9:16 cuts off 75% of the frame. If the speaker is positioned off-center, they are partially or completely cropped out. If text overlays are at the edges, they disappear. If the action moves laterally, it leaves the visible frame. Intelligent reframing is required: tracking the most important element in every frame (usually a face or the primary subject) and positioning the crop window to keep it visible regardless of aspect ratio changes. NemoVideo reframes intelligently. The AI identifies subjects, tracks faces, follows action, repositions text overlays, and ensures visual coherence at every aspect ratio. One upload produces every platform version with every element properly framed.

## Use Cases

1. **YouTube to TikTok — Horizontal to Vertical (any length)** — A creator publishes a 16:9 YouTube video and needs a 9:16 TikTok version. Simple center-crop would cut the speaker's face in half (they are positioned left-of-center for rule-of-thirds composition). NemoVideo: tracks the speaker's face throughout the video, positions the vertical crop window to keep their face centered at all times, follows any lateral movement (when they walk or gesture off-center), repositions lower-third text overlays from the bottom-left to bottom-center (visible in vertical), and adjusts caption positions for the vertical safe zone. A YouTube video that was composed for horizontal becomes a TikTok that feels like it was shot for vertical.

2. **Multi-Platform Export — One Video, Six Formats (any length)** — A brand produces a product launch video in 16:9. It needs to be posted on YouTube (16:9), TikTok (9:16), Instagram Reels (9:16), Instagram Feed (1:1), LinkedIn (16:9), and Facebook (4:5). NemoVideo: generates all 6 versions from one source, each with intelligent reframing (subject tracking per aspect ratio), repositioned text overlays (titles, CTAs, captions), adjusted safe zones per platform (TikTok's bottom 15% is covered by UI), and platform-specific caption positioning. Six platform-native versions from one production.

3. **Presentation to Social — Slides to Vertical (per slide)** — A conference presentation was recorded in 16:9 with speaker + slides. The slides need to be shared on LinkedIn and Instagram. NemoVideo: detects slide content areas, crops to focus on the slide content (removing empty margins and the speaker when slides are the focus), alternates between speaker-focused framing and slide-focused framing based on content importance, and exports vertical versions with optimized text readability. Widescreen presentations become mobile-readable social content.

4. **E-Commerce — Product Photos to Every Ad Format (batch)** — An online store has 16:9 product lifestyle photos that need to become video ads across platforms. NemoVideo: applies subtle Ken Burns motion to each photo, reframes for each ad format (9:16 for TikTok ads, 1:1 for Facebook feed, 4:5 for Instagram feed, 16:9 for YouTube pre-roll), ensures the product remains centered and prominent in every aspect ratio, and adds platform-specific CTA overlays positioned in the correct safe zone per format. One product photo becomes ads for every platform.

5. **Archive Reformatting — Old 4:3 Content to Modern Formats (batch)** — A media company has a library of 4:3 (standard definition era) content that needs to be distributed on modern 16:9 and 9:16 platforms. NemoVideo: intelligently reframes 4:3 to 16:9 (adds subtle background blur on sides or AI-extends the frame), reframes to 9:16 for vertical distribution (subject tracking within the narrower vertical window), preserves the original framing intent, and batch-processes the entire library. Legacy content accessible on modern platforms.

## How It Works

### Step 1 — Upload Source Video
Any aspect ratio: 16:9, 4:3, 1:1, 9:16, ultrawide, or custom. NemoVideo accepts any source shape.

### Step 2 — Select Target Formats
Choose target aspect ratios and platforms. NemoVideo applies intelligent reframing for each.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-resize",
    "prompt": "Resize a 16:9 talking-head YouTube video to all social formats. Speaker is positioned left-of-center. Text overlays at bottom-left need repositioning for vertical. Captions at bottom need to move to vertical safe zone. Generate: 9:16 (TikTok/Reels — face tracking, captions repositioned above platform UI zone), 1:1 (Instagram/LinkedIn — speaker centered), 4:5 (Instagram feed — speaker centered, more headroom). Keep all text readable. Export all at 1080p.",
    "source_ratio": "16:9",
    "targets": [
      {"ratio": "9:16", "platforms": ["tiktok", "reels"], "tracking": "face", "safe_zone": "tiktok"},
      {"ratio": "1:1", "platforms": ["instagram-feed", "linkedin"], "tracking": "face"},
      {"ratio": "4:5", "platforms": ["instagram-feed"], "tracking": "face"}
    ],
    "reposition_overlays": true,
    "resolution": "1080p"
  }'
```

### Step 4 — Verify Framing
Preview each version. Check: subject is never cut off, text is always readable, no important visual elements are outside the frame. Download all versions.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Source description and resize requirements |
| `source_ratio` | string | | "16:9", "4:3", "1:1", "9:16" |
| `targets` | array | | [{ratio, platforms, tracking, safe_zone}] |
| `tracking` | string | | "face", "subject", "action", "center" |
| `reposition_overlays` | boolean | | Move text/captions for new aspect ratios |
| `background_fill` | string | | "blur", "black", "ai-extend", "mirror" for letterbox areas |
| `resolution` | string | | "720p", "1080p", "4K" |
| `batch` | array | | Multiple videos |

## Output Example

```json
{
  "job_id": "avr-20260328-001",
  "status": "completed",
  "source": "16:9 (1920x1080)",
  "outputs": {
    "tiktok_reels": {"file": "video-9x16.mp4", "resolution": "1080x1920", "tracking": "face"},
    "instagram_square": {"file": "video-1x1.mp4", "resolution": "1080x1080", "tracking": "face"},
    "instagram_tall": {"file": "video-4x5.mp4", "resolution": "1080x1350", "tracking": "face"}
  },
  "overlays_repositioned": 4,
  "frames_tracked": "all"
}
```

## Tips

1. **Face tracking is essential for talking-head resizing** — A speaker positioned off-center in 16:9 will be cropped out in 9:16 without face tracking. Always enable face tracking for any video with people.
2. **Platform safe zones differ — and matter** — TikTok's bottom 15% is covered by username, caption, and music info. Instagram Reels has different overlay positions. Caption positioning must account for these per-platform UI elements.
3. **Multi-format from one source saves 5-10 hours per week** — Manual reformatting for each platform is the most tedious video production task. Automating it with AI reframing eliminates hours of mechanical work with zero quality loss.
4. **1:1 square is the most versatile single format** — If forced to choose one format that works acceptably everywhere, 1:1 square displays well on Instagram, Facebook, LinkedIn, and Twitter without severe cropping on any platform.
5. **Text overlay repositioning prevents invisible CTAs** — A "Subscribe" button designed for bottom-left of a 16:9 frame will be completely outside a 9:16 crop. Always enable overlay repositioning when resizing.

## Output Formats

| Format | Resolution | Platform |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / LinkedIn / website |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts / Stories |
| MP4 1:1 | 1080x1080 | Instagram / Facebook / LinkedIn |
| MP4 4:5 | 1080x1350 | Instagram feed |
| MP4 2:3 | 1000x1500 | Pinterest |

## Related Skills

- [ai-video-rotate](/skills/ai-video-rotate) — Video rotation
- [ai-video-effects](/skills/ai-video-effects) — Video effects
- [ai-video-filters](/skills/ai-video-filters) — Video filters
