---
name: ai-video-loop
version: 1.0.1
displayName: "AI Video Loop — Create Seamless Looping Videos and Cinemagraphs with AI"
description: >
  Create seamless looping videos and cinemagraphs with AI — produce perfect loops from any footage for social media backgrounds, website heroes, digital signage, presentation backgrounds, and mesmerizing content. NemoVideo analyzes motion and creates invisible loop points: boomerang loops, forward-reverse cycles, cinemagraphs with isolated motion, infinite scroll effects, and crossfade seamless loops. Looping video maker, seamless loop creator, video loop tool, cinemagraph maker, boomerang video, infinite loop video, GIF loop maker, looping background video.
metadata: {"openclaw": {"emoji": "🔄", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# AI Video Loop — Videos That Never End and Never Bore

A seamless loop is hypnotic. The human brain is wired to detect patterns and anticipate endings — when a video loops perfectly with no visible seam, the brain enters a satisfied observation state. This is why looping content consistently outperforms linear content for: watch time (viewers watch loops 3-5x longer than their actual duration), website engagement (hero video loops keep visitors on pages 2.5x longer than static images), digital signage (looping content requires zero interaction and holds attention passively), and social media (Instagram and TikTok auto-loop short content, and perfect loops get replayed obsessively). Creating a seamless loop is technically challenging. The last frame must transition invisibly into the first frame. Any motion, lighting change, or camera movement that does not return to its starting position creates a visible jump at the loop point. Professional loopers shoot with the loop in mind — starting and ending in the same position. But most footage was not shot for looping. NemoVideo creates seamless loops from any footage using AI analysis: finding the optimal loop window where start and end frames match, applying crossfade blending at the loop point, stabilizing any drift, and optionally creating cinemagraphs where only selected areas move while the rest stays still.

## Use Cases

1. **Website Hero — Looping Background Video (3-10s loop)** — A SaaS company's landing page needs a hero background: abstract motion that creates visual interest without distracting from the content overlay. NemoVideo: takes 30 seconds of atmospheric footage (flowing liquid, abstract particles, gentle light movement), identifies the best 5-second window for seamless looping, applies crossfade blending at the loop seam (invisible transition), exports as a web-optimized loop (H.264, small file size, autoplay-ready). The hero background that runs infinitely without buffering, loading, or visible repetition.

2. **Social Media — Satisfying Infinite Loop (3-15s)** — A creator films a satisfying process: paint pouring, dominos falling, cake decorating. NemoVideo: analyzes the footage for the moment where end state most closely matches start state, creates a seamless forward-reverse (boomerang) loop where the process appears to repeat infinitely, applies smooth speed curves at the reversal points (no jarring speed change), and exports as both video loop (MP4) and GIF. The satisfying loop content that viewers watch 10+ times without realizing they are looping.

3. **Cinemagraph — Living Photo (endless)** — A coffee shop photo where only the steam from the cup moves. NemoVideo: takes 5-10 seconds of video, identifies the motion region (steam rising), freezes everything else (cup, table, background as still image), loops only the steam movement seamlessly, exports as a cinemagraph (video file that looks like a photo with subtle motion). The living photograph format that stops social media scrollers because their brain detects motion in what appears to be a still image.

4. **Digital Signage — Retail Display Loop (5-30s)** — A retail store needs looping content for their display screens: product showcases, brand imagery, promotional messages. NemoVideo: takes product footage, creates seamless loops for each product (rotating product loops, animated feature highlights, promotional text cycles), sets loop duration to 10-15 seconds per product, sequences multiple loops into a playlist, and exports at display resolution. Professional digital signage content that runs 24/7 without visible repetition.

5. **Presentation — Animated Background Slides (3-8s per slide)** — A presenter needs animated backgrounds for their keynote slides — static enough to not distract, dynamic enough to feel premium. NemoVideo: generates subtle motion loops for each slide theme (gentle gradient animation, floating particles, slow light movement, abstract waves), ensures each loop is perfectly seamless (no jump when the presentation software auto-replays), exports as optimized video files for PowerPoint/Keynote background insertion. The presentation backgrounds that make every slide feel like a premium production.

## How It Works

### Step 1 — Upload Footage
Video clip that you want to loop. Any length — NemoVideo finds the best loop window within the footage.

### Step 2 — Choose Loop Type
Seamless forward loop (clip plays forward, loops back to start), boomerang (forward then reverse), cinemagraph (isolated motion region), or crossfade blend loop.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-loop",
    "prompt": "Create a seamless 6-second loop from a 20-second clip of ocean waves on a beach. The loop should be invisible — no jump or flash at the loop point. Crossfade blend the last 1 second into the first 1 second. Maintain natural wave rhythm. Also create a cinemagraph version: freeze the sky and sand, only loop the water motion. Export both as MP4 (for web hero) and GIF (for email). Web version: max 2MB file size for fast loading.",
    "loop_type": "seamless-crossfade",
    "loop_duration": 6,
    "crossfade_duration": 1.0,
    "cinemagraph": {"freeze": ["sky", "sand"], "animate": ["water"]},
    "outputs": [
      {"format": "mp4", "use": "web-hero", "max_size": "2MB"},
      {"format": "gif", "use": "email"}
    ]
  }'
```

### Step 4 — Verify the Loop
Watch the loop 5+ times. If you cannot detect the seam, it is seamless. Adjust crossfade duration if needed. Deploy to website, social, or signage.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Loop description and requirements |
| `loop_type` | string | | "seamless-crossfade", "boomerang", "cinemagraph", "forward-repeat" |
| `loop_duration` | integer | | Target seconds per loop cycle |
| `crossfade_duration` | float | | Seconds of crossfade blend (default: 0.5) |
| `cinemagraph` | object | | {freeze: [...], animate: [...]} region control |
| `speed_curve` | string | | "linear", "ease", "ease-in-out" for boomerang |
| `outputs` | array | | [{format, use, max_size}] |
| `repeat_count` | integer | | Preview loops (default: 3) |

## Output Example

```json
{
  "job_id": "avl-20260328-001",
  "status": "completed",
  "source_duration": "0:20",
  "loop_duration": "6.0s",
  "loop_type": "seamless-crossfade",
  "crossfade": "1.0s",
  "seam_visibility": "imperceptible",
  "outputs": {
    "web_hero": {"file": "waves-loop.mp4", "size": "1.8MB", "duration": "6s"},
    "email_gif": {"file": "waves-loop.gif", "size": "4.2MB", "duration": "6s"},
    "cinemagraph": {"file": "waves-cinemagraph.mp4", "size": "1.2MB", "frozen": ["sky", "sand"], "animated": ["water"]}
  }
}
```

## Tips

1. **Crossfade duration of 0.5-1.5 seconds eliminates most loop seams** — Too short and the transition is visible. Too long and the blended section looks ghostly. 0.5-1.0 seconds for fast motion, 1.0-1.5 seconds for slow motion.
2. **Cinemagraphs stop scrollers because motion in stillness is uncanny** — The human brain is primed to detect motion. A "photo" where one element moves creates a double-take that stops the scroll. Cinemagraphs consistently achieve 2-3x higher engagement than static images.
3. **Website hero loops must be under 3MB for performance** — A beautiful 50MB loop that takes 5 seconds to load increases bounce rate. Optimize for file size: 5-8 second loop, 720p resolution, H.264 compression. Beauty that loads instantly.
4. **Boomerang loops work best with symmetric motion** — A ball bouncing, a wave crashing, a person jumping — motions that naturally return to their starting position create the most satisfying boomerangs. Asymmetric motion (walking, driving) creates awkward reversal moments.
5. **Test the loop by watching it 10 times** — If you cannot detect the seam after 10 consecutive plays, no viewer will ever notice. If you can detect it even once, adjust the crossfade or find a better loop window.

## Output Formats

| Format | Size | Use Case |
|--------|------|----------|
| MP4 | Optimized | Website hero / digital signage |
| GIF | Variable | Email / social preview |
| WebM | Small | Web background (modern browsers) |
| MOV ProRes | Large | Professional compositing |

## Related Skills

- [ai-video-effects](/skills/ai-video-effects) — Video effects
- [ai-video-filters](/skills/ai-video-filters) — Video filters
- [ai-video-rotate](/skills/ai-video-rotate) — Video rotation
