---
name: facebook-video-editor
version: "1.0.0"
displayName: "Facebook Video Editor — Edit Videos for Facebook Reels Feed Ads and Stories"
description: >
  Edit videos for Facebook using AI — create and optimize video content for Facebook Reels, News Feed, Stories, and Ads with platform-specific formatting, auto-captions for sound-off viewing, thumb-stop hooks, engagement-optimized pacing, and multi-format export. NemoVideo handles the complete Facebook video editing workflow: trim and tighten raw footage, add scroll-stopping text overlays, generate captions that drive watch time in the muted autoplay feed, apply aspect ratio formatting for every Facebook placement, add background music with speech ducking, and export videos that meet Facebook's algorithm preferences for each surface.
metadata: {"openclaw": {"emoji": "📘", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Facebook Video Editor — Videos Optimized for Every Facebook Surface

Facebook is five video platforms in one: the News Feed (muted autoplay, square or landscape), Reels (vertical, sound-on, algorithm-driven discovery), Stories (vertical, ephemeral, casual), In-Stream Ads (pre-roll and mid-roll, unskippable), and Watch (longer-form, intentional viewing). Each surface has different technical specs, different viewer behavior, and different algorithmic signals — a video that performs on Reels may fail completely in the News Feed. Most creators publish one version of a video to all placements and wonder why performance is inconsistent. The answer is format mismatch: a 16:9 video in the Reels tab gets cropped awkwardly; a vertical video in the News Feed gets shrunk to a strip; a video without captions loses 85% of News Feed viewers who watch with sound off. NemoVideo edits videos specifically for each Facebook surface. Upload your raw footage, describe what you want, and the AI produces: News Feed version (square 1:1 with burned-in captions and thumb-stop hook), Reels version (9:16 with trending audio pacing and text overlays), Stories version (9:16 with tap-forward pacing and interactive prompts), and Ad version (multiple aspect ratios with CTA placement). One editing session, every Facebook format covered.

## Use Cases

1. **News Feed — Muted Autoplay Optimization (30-180s)** — A brand has a 90-second product video. NemoVideo edits for the News Feed: crops to 1:1 square (the dominant feed format), adds large burned-in captions because 85% of feed video is watched without sound, creates a thumb-stop first frame (bold text overlay: "This changed how I cook forever" over a visually striking moment), tightens pacing to front-load the most engaging content in the first 3 seconds (Facebook's autoplay hook window), adds subtle background music at -22dB for the 15% who do have sound on, and ends with a clear CTA ("Follow for more" or "Shop now — link in comments"). The video is engineered for muted, distracted, scrolling viewers.
2. **Reels — Algorithm Discovery (15-90s)** — A fitness creator wants Reels reach. NemoVideo produces: 9:16 vertical with face tracking, hook in the first 0.8 seconds ("Stop doing crunches — here's what actually works"), fast-paced cuts every 2-3 seconds matching Reels' consumption rhythm, word-by-word captions with animated highlights, trending-style transitions between exercises, background music synced to cuts, and a loop-friendly ending that connects back to the opening. Reels reward watch time and replays — the edit is optimized for both.
3. **Stories — Tap-Paced Episodic Content (3-5 segments)** — A restaurant wants to showcase a new menu across Stories. NemoVideo creates: 5 story segments (each 8-12 seconds for optimal tap pacing), Segment 1: hook with poll sticker placeholder ("Which dish would you try? 🍕 or 🍝"), Segments 2-4: individual dish showcases with text overlays (dish name, price, one-line description), Segment 5: CTA ("Swipe up to reserve" or "DM us to book"). Each segment is self-contained but flows as a narrative series.
4. **Facebook Ads — Multi-Placement Creative (15-60s)** — An e-commerce brand needs ad creative for Facebook's placement optimizer. NemoVideo produces four versions from one source: 1:1 Feed ad (thumb-stop hook + product benefit + CTA), 9:16 Reels/Stories ad (full-screen immersive product showcase), 16:9 In-Stream ad (pre-roll format with immediate value proposition), and 4:5 Feed ad (Facebook's recommended feed ratio for maximum screen real estate). Each version has the CTA button placement positioned to align with Facebook's overlay zones.
5. **Community Engagement — Discussion Starter (30-60s)** — A community manager needs video posts that drive comments. NemoVideo creates: an opinion-provoking statement as the hook ("Unpopular opinion: breakfast is the least important meal"), supporting points edited with fast pacing and text overlays, an ending that explicitly invites disagreement ("Am I wrong? Tell me in the comments"), and burned-in captions with a question mark emphasis on the final frame. The video is designed to trigger the comment behavior that Facebook's algorithm rewards most heavily.

## How It Works

### Step 1 — Upload Source Video
Any raw footage — phone recording, camera footage, screen capture, existing content. NemoVideo analyzes the content and identifies optimal moments for each Facebook placement.

### Step 2 — Select Facebook Surfaces
Choose which placements to optimize for: News Feed, Reels, Stories, Ads, or all. Each gets a format-specific edit.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "facebook-video-editor",
    "prompt": "Edit a 2-minute raw product demo for Facebook. Produce 3 versions: (1) News Feed 1:1 — thumb-stop hook in first frame, burned-in captions (white text, dark pill), tighten to 60 seconds, CTA: Shop now link in comments. (2) Reels 9:16 — face-tracked crop, word-by-word captions (white + blue #1877F2 highlight), fast cuts every 2.5 sec, trending background music at -14dB, 45 seconds max, loop-friendly ending. (3) Stories — 4 segments of 10 sec each, text overlays with product benefits, swipe-up CTA on final segment.",
    "surfaces": ["news-feed", "reels", "stories"],
    "news_feed": {"aspect": "1:1", "captions": "burned-in", "duration": "60 sec", "cta": "Shop now"},
    "reels": {"aspect": "9:16", "captions": "word-highlight", "duration": "45 sec", "music": "trending"},
    "stories": {"segments": 4, "segment_duration": "10 sec", "cta": "swipe-up"}
  }'
```

### Step 4 — Review and Publish
Preview each surface version. Check caption accuracy, CTA placement, and aspect ratio framing. Publish to each Facebook surface or upload to Ads Manager.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Source description and editing requirements |
| `surfaces` | array | | ["news-feed","reels","stories","ads","watch"] |
| `news_feed` | object | | {aspect, captions, duration, cta, thumb_stop} |
| `reels` | object | | {aspect, captions, duration, music, hook, loop} |
| `stories` | object | | {segments, segment_duration, cta, stickers} |
| `ads` | object | | {placements: ["feed","stories","in-stream"], cta_button} |
| `captions` | object | | {style, text_color, highlight_color, bg} |
| `music` | string | | "trending", "corporate", "upbeat", "none" |
| `music_volume` | string | | "-12dB" to "-22dB" |
| `batch` | array | | Multiple source videos for batch editing |

## Output Example

```json
{
  "job_id": "fve-20260328-001",
  "status": "completed",
  "source_duration": "2:04",
  "outputs": {
    "news_feed": {
      "file": "feed-1x1.mp4",
      "aspect": "1:1",
      "duration": "0:58",
      "resolution": "1080x1080",
      "captions": "burned-in (64 lines)",
      "thumb_stop": "Bold text overlay frame 1"
    },
    "reels": {
      "file": "reels-9x16.mp4",
      "aspect": "9:16",
      "duration": "0:44",
      "resolution": "1080x1920",
      "captions": "word-highlight (52 words)",
      "music": "trending-upbeat at -14dB"
    },
    "stories": {
      "files": ["story-1.mp4", "story-2.mp4", "story-3.mp4", "story-4.mp4"],
      "segment_duration": "10 sec each",
      "resolution": "1080x1920",
      "cta": "Swipe-up on segment 4"
    }
  }
}
```

## Tips

1. **Square 1:1 dominates the News Feed** — It takes 78% more screen real estate than 16:9 in the mobile feed, directly increasing thumb-stop rate. Always crop to 1:1 for feed posts.
2. **Captions are mandatory for News Feed, optional for Reels** — 85% of feed video is watched muted. Reels default to sound-on. Adjust caption strategy per surface instead of applying the same approach everywhere.
3. **Facebook Reels reward the first 0.8 seconds** — Even shorter than TikTok's decision window. The visual hook must land before the viewer's thumb completes the scroll gesture.
4. **Stories tap-through rate drops after segment 3** — Keep story series to 3-5 segments maximum. Front-load the most engaging content in segments 1-2 and place the CTA in the final segment for maximum completion-to-action conversion.
5. **Multi-placement ads need separate creative per format** — Facebook's placement optimizer works best when each placement has a native-feeling creative. One 16:9 video auto-cropped to all placements always underperforms dedicated edits.

## Output Formats

| Format | Aspect | Use Case |
|--------|--------|----------|
| MP4 1:1 | 1080x1080 | News Feed post |
| MP4 4:5 | 1080x1350 | News Feed (max real estate) |
| MP4 9:16 | 1080x1920 | Reels / Stories |
| MP4 16:9 | 1920x1080 | In-Stream / Watch |
| SRT | — | Closed captions upload |

## Related Skills

- [linkedin-video-creator](/skills/linkedin-video-creator) — LinkedIn video production
- [crear-video-ia](/skills/crear-video-ia) — AI video creation (Spanish)
