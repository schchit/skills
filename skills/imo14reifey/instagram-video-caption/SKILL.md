---
name: instagram-video-caption
version: 1.3.1
displayName: "Instagram Video Caption — Auto Generate Captions for Reels, Stories and IGTV"
description: >
  Automatically generate and burn captions into Instagram videos — Reels, Stories, and IGTV. NemoVideo transcribes speech with word-level timing, styles captions in Instagram's native aesthetic (bold centered text, word-by-word highlight, gradient backgrounds), crops and positions text to avoid Instagram's UI overlay zones, and exports at the exact resolutions and aspect ratios Instagram prefers — so captions look native, not pasted on, and every sound-off viewer stays watching.
metadata: {"openclaw": {"emoji": "📸", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# Instagram Video Caption — Auto Captions for Reels, Stories and IGTV

Instagram is a sound-off platform. 70% of Stories are watched on mute. Reels autoplay silently in the Explore feed. IGTV begins playing without audio in the grid preview. Every video without captions is a video that 70% of the audience scrolls past because they can't understand what's being said. Instagram's built-in auto-caption feature exists but it's limited: one font style, no word-by-word animation, no custom colors, and it frequently breaks on fast speech, accents, or background noise. Creators who want captions that match their brand aesthetic — specific fonts, colors, animation styles, and positioning — need external tools. NemoVideo generates Instagram-native captions: transcription tuned to Instagram's audio compression artifacts, text styling that matches the platform's visual language (bold, centered, high-contrast), safe-zone positioning that avoids Instagram's UI overlays (username tag at the bottom, like/comment buttons on the right), and word-by-word highlight animation that matches the cadence TikTok trained viewers to expect. The captions feel like they were added in Instagram's native editor — because NemoVideo understands Instagram's specific design constraints.

## Use Cases

1. **Reels — Word-by-Word Highlight Captions (15-90s)** — A creator's 30-second Reel needs captions that match the trending style: 3-4 words displayed at a time, each word highlighting as it's spoken, bold white text with a slight drop shadow on a semi-transparent dark pill behind the text block, positioned in the center of the frame (not the bottom, where Instagram's UI elements appear). NemoVideo: transcribes at word-level precision, generates the animated highlight, positions text in the Instagram safe zone (20% from bottom to clear the username/caption overlay), and exports 1080x1920 at Instagram's preferred 30fps H.264 codec. The captions look platform-native.
2. **Stories — Quick Auto-Caption with Brand Colors (15s per slide)** — A brand posts 5 Story slides, each a 15-second clip with a team member speaking. NemoVideo: transcribes each clip, applies the brand's fonts and colors (e.g., white text with coral highlight on transparent background), positions text in the upper-center safe zone (Stories have tap targets on the sides and bottom), and exports all 5 slides as separate files ready for sequential posting.
3. **IGTV — Full Sentence Captions for Long-Form (2-15 min)** — A 10-minute interview needs sentence-by-sentence captions for IGTV. NemoVideo: transcribes the full conversation, identifies speaker changes (interviewer vs. guest), labels each subtitle line with the speaker name in a different color, uses a clean sans-serif font at readable size (not too large for long sentences), positions in the lower-third with solid dark background bar, and exports with embedded SRT metadata for Instagram's caption toggle.
4. **Bilingual Captions — Reach International Audience (any length)** — A Spanish-speaking creator wants English captions to reach the US audience. NemoVideo: transcribes the Spanish audio, translates to English with context-aware accuracy, displays English captions in the center with Spanish in smaller text above, and styles both in the creator's brand colors. One video serves both markets without separate posts.
5. **Carousel Reels — Consistent Caption Style Across Clips (3-10 clips)** — A fitness creator posts a carousel of 5 exercise demo Reels. NemoVideo: applies identical caption styling across all 5 clips (same font, same color, same position, same animation speed), ensuring the carousel looks cohesive when viewers swipe through. Batch-processed in one command.

## How It Works

### Step 1 — Upload Instagram Video
Provide the video. NemoVideo detects the format and analyzes audio quality, background noise level, and speech cadence to optimize transcription accuracy for Instagram's audio compression.

### Step 2 — Choose Caption Style
Select from Instagram-native styles: word-highlight (Reels trending), bold-centered (Stories), sentence-lower-third (IGTV), or custom. Set colors, font, and position.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "instagram-video-caption",
    "prompt": "Add word-by-word highlight captions to a 30-second Reel. Style: bold white text, yellow highlight on active word, semi-transparent dark pill background. Position: center (Instagram safe zone, 20%% from bottom). Font: bold sans-serif 52px. Language: English. Remove filler words. Export 1080x1920 30fps H.264.",
    "style": "word-highlight",
    "text_color": "#FFFFFF",
    "highlight_color": "#FFD700",
    "background": "pill-dark-transparent",
    "position": "center-safe",
    "font_size": 52,
    "language": "en",
    "remove_fillers": true,
    "instagram_format": "reels",
    "resolution": "1080x1920",
    "fps": 30
  }'
```

### Step 4 — Preview and Post
Preview the captioned video. Check that text doesn't overlap Instagram UI elements. Adjust styling or timing. Export and post.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Caption requirements and styling |
| `style` | string | | "word-highlight", "bold-centered", "sentence-lower-third", "karaoke", "minimal" |
| `text_color` | string | | Hex color (default: "#FFFFFF") |
| `highlight_color` | string | | Active word color (default: "#FFD700") |
| `background` | string | | "pill-dark-transparent", "full-bar", "outline-only", "none" |
| `position` | string | | "center-safe", "top", "bottom-safe", "custom" |
| `font_size` | integer | | Pixels (default: 48) |
| `language` | string | | "auto", "en", "es", "fr", "de", "ja", "ko", "pt", "ar" |
| `translate_to` | string | | Add translated caption in second language |
| `remove_fillers` | boolean | | Remove um/uh/like (default: false) |
| `instagram_format` | string | | "reels", "stories", "igtv" |
| `batch` | array | | Multiple videos for consistent styling |

## Output Example

```json
{
  "job_id": "ivc-20260328-001",
  "status": "completed",
  "duration_seconds": 31,
  "format": "mp4",
  "resolution": "1080x1920",
  "fps": 30,
  "file_size_mb": 8.4,
  "output_url": "https://mega-api-prod.nemovideo.ai/output/ivc-20260328-001.mp4",
  "captions": {
    "language": "en",
    "word_count": 68,
    "lines": 18,
    "style": "word-highlight (white/#FFD700)",
    "position": "center-safe (20% from bottom)",
    "fillers_removed": 3,
    "safe_zone": "verified — no UI overlap"
  }
}
```

## Tips

1. **Center positioning beats bottom positioning on Instagram** — Instagram's username, caption text, and action buttons occupy the bottom 15% of Reels. Captions placed there get covered. Center-safe positioning (20% from bottom) stays visible.
2. **52px font is the sweet spot for Reels** — Smaller text strains mobile eyes. Larger text limits words per line. 48-54px bold sans-serif is readable on every phone screen without limiting display to 2 words per line.
3. **Word-by-word highlight is the #1 engagement driver** — The animated highlight creates a reading rhythm that anchors attention. Viewers who would scroll past static text stay to read the highlighted words.
4. **Remove fillers for polish, keep them for authenticity** — "Um" and "uh" in captions look unprofessional for brands. But for personal creators going for a casual vibe, keeping them makes the captions feel authentic. Choose based on your brand.
5. **Batch-process carousels for visual consistency** — Different caption styling across carousel slides looks amateur. Processing all slides with identical settings produces a cohesive, branded carousel.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 9:16 | 1080x1920 | Reels / Stories |
| MP4 16:9 | 1920x1080 | IGTV landscape |
| MP4 4:5 | 1080x1350 | Instagram feed video |
| SRT | — | Instagram's caption toggle |

## Related Skills

- [subtitle-video-generator](/skills/subtitle-video-generator) — General subtitle generation
- [tiktok-video-editor-online](/skills/tiktok-video-editor-online) — TikTok editing
- [text-to-speech-ai](/skills/text-to-speech-ai) — AI voiceover
