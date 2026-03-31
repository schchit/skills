---
name: instagram-reels-editor
version: "1.2.0"
displayName: "Instagram Reels Editor — Edit and Optimize Videos for Instagram Reels with AI"
description: >
  Edit and optimize videos for Instagram Reels with AI — create scroll-stopping vertical content with trending audio sync, animated captions, hook-first editing, aspect ratio conversion, platform-safe text positioning, engagement-optimized pacing, and Reels-native visual effects. NemoVideo understands the Instagram algorithm and audience behavior: front-load the hook in the first 1.5 seconds, add animated captions for the 85%% watching muted, position text within Instagram safe zones, apply trending visual styles, optimize video length for maximum completion rate, and produce content formatted exactly to Instagram Reels specifications. Instagram Reels editor AI, Reels video maker, Instagram video editor, vertical video editor, Reels creator tool, Instagram content maker, short form video editor, Reels optimizer, Instagram video AI.
metadata: {"openclaw": {"emoji": "📱", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Instagram Reels Editor — Create Reels That Stop the Scroll and Feed the Algorithm

Instagram Reels is the platform's fastest-growing format and the primary discovery mechanism for new audiences. Instagram's head of product confirmed that Reels receives preferential algorithmic distribution — a Reel reaches 2-5x more non-followers than a feed post. The opportunity is massive: Reels is how creators, brands, and businesses reach people who have never heard of them. But Reels has its own visual language, its own pacing expectations, and its own algorithmic preferences that differ from YouTube, TikTok, and every other platform. What works on YouTube (slow intros, 16:9 framing, 10+ minute depth) fails catastrophically on Reels (viewers swipe within 1.5 seconds if the hook is not immediate). What works on TikTok (raw, unpolished, trending-audio-dependent) underperforms on Reels (Instagram rewards slightly higher production value and visual aesthetic). The Instagram Reels sweet spot: polished but not corporate, fast-paced but not chaotic, visually striking but not overwhelming, and front-loaded with a hook that stops the thumb mid-scroll. NemoVideo is optimized specifically for Instagram Reels. The AI applies Reels-native editing: hook-first structure (the most compelling visual or statement in the first 1.5 seconds), animated captions positioned in Instagram's safe zone (above the bottom UI bar, below the top status bar), pacing calibrated for Reels attention patterns (faster cuts, shorter segments, more visual variety per second), and aspect ratio conversion that reframes any source footage to perfect 9:16 vertical with intelligent subject tracking.

## Use Cases

1. **Landscape to Reels — Convert Any Video to Vertical (any source)** — A creator has 16:9 YouTube content, product demo footage, or horizontal recordings that need Reels versions. NemoVideo: converts from any aspect ratio to 9:16 with AI subject tracking (faces stay centered, important elements stay visible), repositions any text overlays and graphics for vertical safe zones, adjusts the edit pacing for Reels (tightening cuts, removing pauses that work in long-form but kill retention in Reels), adds animated captions optimized for Instagram's display (above the username/caption area at the bottom), and creates a Reels-native version that feels like it was shot vertically — not an afterthought crop of horizontal content.

2. **Hook-First Edit — Restructure for the Algorithm (15-90s)** — A talking-head video, tutorial, or product reveal starts with an introduction before getting to the good part. On Reels, the good part must be first. NemoVideo: analyzes the video for the most visually compelling or provocative moment, restructures to front-load that moment in the first 1.5 seconds (the "wait for it" moment becomes the opening frame), adds a hook text overlay ("This changed everything..." / "Nobody talks about this..." / "Watch what happens..."), then delivers the context and payoff, and closes with a CTA or conversation prompt. The restructured version captures attention immediately rather than earning it over 10 seconds (which on Reels, is 8.5 seconds too late).

3. **Carousel Reels — Multi-Clip Story (15-60s)** — A creator needs to tell a story, show a process, or present multiple points in a single Reel: "5 tips for..." or "Day in my life" or "Before and after." NemoVideo: structures multiple clips into a cohesive Reel with smooth transitions (swipe-style cuts, zoom transitions, match-cuts), adds numbered overlays for list-style content ("1/5" "2/5" etc. — giving viewers a progress indicator that encourages completion), applies consistent color grading and visual style across all clips (even if shot in different locations and lighting), positions text for each segment within safe zones, paces to maintain engagement throughout (front-loading the most interesting segment to hook, delivering value in the middle, ending with a share-worthy or save-worthy moment), and exports at exact Reels specifications.

4. **Trending Audio Sync — Visual-to-Music Alignment (15-30s)** — A creator has footage that needs to be edited to a trending Instagram audio track — the format that dominates Reels discovery (trending audio + relevant visual = algorithmic boost). NemoVideo: analyzes the trending audio's beat structure and duration, selects and trims clips to match the audio's rhythm (cuts on beats, transitions on drops, slow-motion on dramatic moments), applies the visual editing style commonly paired with the trending audio (each trending audio develops its own visual convention), adds text overlays timed to the audio's narrative (if the audio has a spoken word component), and produces a Reel that feels native to the trend rather than forced. Trend participation that looks effortless because the timing is perfect.

5. **Product Showcase — Shoppable Reels Content (15-30s)** — An e-commerce brand needs product Reels that drive shopping behavior: product reveal, feature highlight, before/after transformation, or unboxing. NemoVideo: creates product-focused vertical content with attention-grabbing opening (the product in action, the transformation result, the aesthetic flat-lay), applies product-flattering color grading (warm for food, clean for tech, vibrant for fashion, soft for beauty), adds product name and price as tasteful overlays (not intrusive — integrated into the visual design), creates satisfying visual moments (the reveal, the texture close-up, the color shift, the before/after split), and closes with a shopping CTA ("Tap to shop" / "Link in bio"). Product content that converts browsers into buyers through visual desire.

## How It Works

### Step 1 — Upload Source Video
Any footage: horizontal, vertical, square, or mixed. Phone recordings, professional footage, screen recordings, or existing content from other platforms.

### Step 2 — Choose Reels Edit Style
Hook-first restructure, landscape-to-vertical conversion, carousel story, trending audio sync, or product showcase.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "instagram-reels-editor",
    "prompt": "Convert a 3-minute 16:9 cooking tutorial into a 45-second Instagram Reel. Hook: open with the finished dish close-up (the most visually stunning moment) for 1.5 seconds with text I made this in 20 minutes. Then rapid-cut the cooking process: 5 key steps, 6-8 seconds each, with step number overlays (1/5, 2/5 etc). Animated TikTok-style captions for every spoken instruction — positioned in Reels safe zone (above bottom 20%%, below top 10%%). Close with the finished dish plating shot + text overlay: Full recipe in caption. Color grade: warm, food-flattering (slightly saturated oranges and greens). Music: upbeat cooking montage. Face tracking on the chef when they speak to camera.",
    "source_format": "16:9",
    "output_format": "9:16",
    "target_duration": 45,
    "hook": {"type": "best-moment-first", "duration": 1.5, "text": "I made this in 20 minutes"},
    "structure": "rapid-step-montage",
    "steps": 5,
    "captions": {"style": "tiktok-animated", "safe_zone": "instagram"},
    "color_grade": "warm-food",
    "music": "upbeat-cooking",
    "tracking": "face",
    "cta": {"text": "Full recipe in caption", "position": "end-card"}
  }'
```

### Step 4 — Preview at Mobile Size
View on a phone or at phone-resolution preview. Verify: text is readable at actual Reels viewing size, captions are above the Instagram UI bar, hook grabs attention in the first 1.5 seconds, pacing feels right for scrolling context. Adjust and re-render.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Reels editing requirements |
| `source_format` | string | | Source aspect ratio |
| `output_format` | string | | "9:16" (Reels standard) |
| `target_duration` | int | | Target length in seconds (15-90) |
| `hook` | object | | {type, duration, text} first-frame hook |
| `structure` | string | | "hook-first", "carousel", "trending-sync", "rapid-montage" |
| `captions` | object | | {style, safe_zone, highlight_color} |
| `color_grade` | string | | Style-specific color treatment |
| `music` | string | | Audio track or style |
| `tracking` | string | | "face", "subject", "product" |
| `trending_audio` | string | | Trending audio reference |
| `cta` | object | | {text, position} |

## Output Example

```json
{
  "job_id": "igreel-20260329-001",
  "status": "completed",
  "source": "16:9 (3:12)",
  "output": "9:16 (0:44)",
  "hook_duration": "1.5s",
  "cuts": 12,
  "captions_rendered": true,
  "safe_zone_compliant": true,
  "outputs": {
    "reel": {"file": "cooking-reel-9x16.mp4", "resolution": "1080x1920", "duration": "0:44"}
  }
}
```

## Tips

1. **The first 1.5 seconds determine if anyone watches the rest** — Instagram users scroll at speed. The hook must be visual (not a title card — a compelling image or action), immediate (no build-up), and curiosity-generating (the viewer must need to know what happens next). Front-load the most striking moment, always.
2. **Animated captions are nearly mandatory on Reels** — 85% of Instagram video is watched muted. Without captions, 85% of your audience receives only the visual component. Animated word-by-word captions (TikTok-style) add a reading engagement layer that measurably increases watch time and completion rate.
3. **Instagram safe zones are different from TikTok safe zones** — Instagram's bottom 20% is covered by username, caption, and engagement buttons. The top 10% is status bar territory. Reels-safe text must live in the middle 70% of the vertical frame. Text outside this zone is partially or fully hidden.
4. **Completion rate is the algorithm's primary signal** — A 30-second Reel that 80% of viewers watch to the end will outperform a 60-second Reel that only 40% complete. Shorter, tighter, higher-engagement-per-second content wins algorithmically. When in doubt, cut shorter.
5. **Trending audio provides algorithmic boost but visual originality provides memorability** — Participating in a trending audio gives the Reel discovery advantage. But what makes viewers follow the account is unique visual execution within the trend. Use trending audio as the vehicle; use original visuals as the identity.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 9:16 | 1080x1920 | Instagram Reels (primary) |
| MP4 9:16 | 1080x1920 | Instagram Stories (repurpose) |
| MP4 1:1 | 1080x1080 | Instagram Feed (alternative) |

## Related Skills

- [ai-video-caption-generator](/skills/ai-video-caption-generator) — Animated Reels captions
- [ai-video-speed-changer](/skills/ai-video-speed-changer) — Speed ramps for Reels
- [ai-video-zoom](/skills/ai-video-zoom) — Zoom effects for emphasis
- [ai-video-thumbnail-maker](/skills/ai-video-thumbnail-maker) — Reels cover images

## Frequently Asked Questions

**What is the ideal Reels length?** — Instagram supports 15-90 second Reels. Data consistently shows that 20-40 seconds is the sweet spot: long enough to deliver value, short enough for high completion rates. Completion rate is the primary algorithmic signal, so a Reel that most viewers finish outperforms a longer Reel that most viewers abandon.

**Can I batch-produce Reels from one long video?** — Yes. Upload a 10-minute YouTube video and NemoVideo extracts multiple standalone Reels: the 5 best moments, each restructured with hook-first editing, vertical framing, and animated captions. One long-form video becomes a week of Reels content.

**Does NemoVideo handle Instagram's cover frame?** — Yes. NemoVideo generates an optimized cover frame for each Reel — a visually striking still from the video with text overlay that looks professional in your Instagram grid. Grid aesthetics matter for profile visitors deciding whether to follow.
