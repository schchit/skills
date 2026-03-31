---
name: video-enhancer-ai
version: "1.0.0"
displayName: "Video Enhancer AI — Enhance Video Quality with AI Color Grading and Lighting Fix"
description: >
  Enhance video quality with AI — improve color grading, fix lighting problems, adjust brightness and contrast, correct white balance, boost saturation, reduce grain, and apply cinematic looks to any footage. NemoVideo transforms dull flat footage from phones and webcams into broadcast-quality video with professional color science: auto white balance correction, exposure optimization, shadow and highlight recovery, color consistency across cuts, skin tone protection, and cinematic LUT application. Make any video look professionally shot and color graded without manual editing.
metadata: {"openclaw": {"emoji": "✨", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Video Enhancer AI — Make Any Video Look Professionally Shot

The difference between amateur-looking video and professional-looking video is almost never the camera — it is the color grading. A $1,000 phone camera and a $5,000 cinema camera shooting the same scene will look nearly identical after professional color grading. But without color grading, the phone footage looks flat, slightly green, underexposed in shadows, and overexposed in highlights. The cinema camera footage has the same problems — just at a higher resolution. Color grading is the transformation that makes footage look cinematic, professional, and intentional. It is also the most time-consuming step in post-production: manually adjusting exposure curves, white balance, color channels, saturation, contrast, shadows, highlights, and skin tones — across every clip, with consistency between shots. A 10-minute video with 30 cuts requires 30 individual color grades that need to match each other. Professional colorists charge $50-200/hour. NemoVideo applies broadcast-quality color enhancement automatically. Upload footage shot on any device — phone, webcam, GoPro, DSLR, drone — and the AI analyzes each frame: corrects white balance drift, optimizes exposure (recovering blown highlights and crushed shadows), enhances color vibrance while protecting skin tones, reduces sensor grain without losing detail, and applies a cinematic look matched to the content type (warm for lifestyle, clean for corporate, moody for drama). Every cut is color-matched to its neighbors for seamless consistency.

## Use Cases

1. **Phone Footage → Broadcast Quality (any length)** — A creator recorded a 15-minute video on an iPhone in mixed lighting: some clips under warm tungsten, others under cool fluorescent, others in natural daylight. NemoVideo: corrects white balance per clip (warm → neutral, cool → neutral, daylight → optimal), matches color temperature across all 30+ cuts so the video feels like one continuous shoot, optimizes exposure (lifts underexposed indoor shadows, recovers overexposed window highlights), enhances color vibrance by 15-20% while keeping skin tones natural, reduces phone sensor grain in low-light clips, and applies a warm-clean cinematic grade across the entire video. The footage looks like it was shot on a cinema camera in a controlled environment.
2. **Webcam → Professional Meeting Quality (any length)** — A remote worker records presentations on a $50 webcam in a home office with overhead fluorescent lighting. NemoVideo: corrects the green color cast from fluorescent lights, brightens the face by lifting midtone exposure, adds subtle warm toning to create an approachable look, balances the background exposure (prevents the window from blowing out), reduces webcam noise in shadow areas, and applies a clean-professional grade. The $50 webcam footage looks like a proper studio setup.
3. **GoPro/Action Cam → Cinematic Adventure (any length)** — GoPro footage from a mountain bike ride looks flat and desaturated (action cameras compress aggressively). NemoVideo: applies a vivid adventure grade (boosted greens for foliage, enhanced blue sky, warm skin tones), recovers dynamic range in high-contrast scenes (bright sky + dark forest floor), corrects the slight fisheye barrel distortion color shift, reduces action-compression artifacts, and maintains fast-motion clarity. Action camera footage with cinema-grade color.
4. **Drone → Professional Aerial (any length)** — Drone footage of a property or landscape looks flat out of camera. NemoVideo: applies landscape-optimized color grading (enhanced golden hour warmth, deep blue sky, vibrant vegetation), corrects exposure for aerial challenges (harsh downward shadows, reflective surfaces), color-matches clips from different times of day (morning flight to afternoon flight), and applies subtle haze reduction for clearer long-distance shots. Real estate, travel, and documentary drone footage with magazine-quality color.
5. **Batch Enhancement — Multi-Camera Consistency (multiple clips)** — A wedding videographer has footage from 3 cameras (two DSLRs and a mirrorless) with different color science. NemoVideo batch-processes all clips: analyzes each camera's color profile, normalizes all footage to a single color baseline, applies a consistent wedding-grade look (warm, romantic, skin-flattering), matches exposure levels across all cameras, and exports a color-consistent batch ready for editing. Three cameras become one visual style.

## How It Works

### Step 1 — Upload Footage
Any camera, any quality. The AI detects: camera type, lighting conditions, color cast, exposure problems, and noise level.

### Step 2 — Choose Enhancement Level
Select: auto (AI decides everything), specific corrections (white balance, exposure, grain), or a cinematic look (warm, cool, moody, vibrant).

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "video-enhancer-ai",
    "prompt": "Enhance a 12-minute phone video shot in mixed indoor lighting. Fix white balance drift between clips (some warm tungsten, some cool fluorescent). Optimize exposure: lift shadows in dark indoor clips, recover highlights near windows. Enhance color vibrance 15-20%% while protecting skin tones. Reduce phone sensor grain in low-light clips. Apply warm-clean cinematic grade. Color-match all cuts for consistency. Export 1080p.",
    "enhancement": "auto-full",
    "white_balance": "auto-correct-per-clip",
    "exposure": "optimize",
    "color_vibrance": "+15-20%%",
    "skin_tone_protection": true,
    "grain_reduction": "moderate",
    "cinematic_look": "warm-clean",
    "color_match": true,
    "format": "16:9"
  }'
```

### Step 4 — Compare and Export
Preview: before/after comparison for each clip. Adjust any parameter. Export the enhanced footage.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the footage and desired enhancement |
| `enhancement` | string | | "auto-full", "color-only", "exposure-only", "custom" |
| `white_balance` | string | | "auto-correct", "warm", "cool", "daylight", "tungsten" |
| `exposure` | string | | "optimize", "brighten", "darken", "+1 stop", "-0.5 stop" |
| `color_vibrance` | string | | "+10%", "+20%", "+30%" |
| `skin_tone_protection` | boolean | | Keep skin tones natural (default: true) |
| `grain_reduction` | string | | "none", "light", "moderate", "heavy" |
| `cinematic_look` | string | | "warm-clean", "cool-moody", "vivid", "film-emulation", "none" |
| `color_match` | boolean | | Match colors across all clips (default: true) |
| `batch` | array | | Multiple clips for batch processing |

## Output Example

```json
{
  "job_id": "vea-20260328-001",
  "status": "completed",
  "source_duration": "12:08",
  "clips_analyzed": 34,
  "enhancements_applied": {
    "white_balance_corrected": "28 of 34 clips (82%)",
    "exposure_optimized": "34 of 34 clips (100%)",
    "color_vibrance": "+18% average",
    "skin_tones": "protected (natural range maintained)",
    "grain_reduction": "moderate on 12 low-light clips",
    "cinematic_look": "warm-clean applied globally",
    "color_matched": "all 34 clips matched to reference"
  },
  "output": {
    "file": "enhanced-1080p.mp4",
    "resolution": "1920x1080",
    "duration": "12:08"
  }
}
```

## Tips

1. **White balance correction has the biggest visual impact** — A slight green cast from fluorescent lights makes footage look amateur instantly. Correcting to neutral or slightly warm transforms the perceived quality more than any other single adjustment.
2. **Skin tone protection prevents the "Instagram filter" look** — Boosting saturation without skin protection makes people look orange, red, or unnatural. AI skin detection ensures faces look healthy and natural even when the rest of the frame gets vivid color enhancement.
3. **Grain reduction should be moderate, not maximum** — Some grain adds organic texture that viewers associate with cinematic quality. Heavy grain removal produces a waxy, artificial look. Moderate reduction removes distracting noise while preserving natural texture.
4. **Color matching across cuts is what makes multicam footage feel cohesive** — When every cut has a slightly different color temperature, the video feels fragmented. Color matching normalizes all clips to one consistent look, making cheap multicam setups feel like professional productions.
5. **The cinematic look should match the content** — Warm-clean for lifestyle and food. Cool-moody for drama and tech. Vivid for travel and nature. Film-emulation for creative and artistic. The wrong look undermines the content even if the color quality is technically excellent.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 | 1080p / 4K | Enhanced master for editing |
| MP4 16:9 | 1080p | YouTube / website |
| MP4 9:16 | 1080x1920 | TikTok / Reels |
| MOV ProRes | 4K | Professional post-production |

## Related Skills

- [music-video-maker](/skills/music-video-maker) — Music video creation
- [video-editor-japonais](/skills/video-editor-japonais) — Japanese video editor
