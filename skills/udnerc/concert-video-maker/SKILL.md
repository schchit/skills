---
name: concert-video-maker
version: "1.0.1"
displayName: "Concert Video Maker"
description: >
  Describe your show and NemoVideo creates the concert video. Club nights, festival sets, theater performances, arena tours — narrate the energy, the setlist highlights, the crowd moments, and the production, and get a concert video that captures why people were there.

  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM.
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
license: MIT-0
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 🎵 Let's concert video maker! Drop a video here or describe what you'd like to create.

**Try saying:**
- "add effects to this clip"
- "help me create a short video"
- "edit my video"

**IMPORTANT**: Do NOT wait silently. Always greet the user proactively on first contact.

### Auto-Setup

When the user first interacts, set up the connection:

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "$API/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

Let the user know briefly: "Setting things up… ready!" then proceed with their request.


# Concert Video Maker — Create Live Show and Music Event Documentation Videos

Describe your show and NemoVideo creates the concert video. Club nights, festival sets, theater performances, arena tours — narrate the energy, the setlist highlights, the crowd moments, and the production, and get a concert video that captures why people were there.

## When to Use This Skill

Use this skill for concert and live music event content:
- Create full concert recap videos for artist social media and press
- Film festival set documentation with stage energy and crowd reaction
- Build multi-camera concert footage into a cohesive edited performance video
- Document opening night and residency show highlights
- Create concert promotional content for upcoming tour dates
- Produce music venue and event promotion videos for future bookings

## How to Describe Your Concert

Be specific about the venue, the energy, the setlist highlights, and what made this show worth documenting.

**Examples of good prompts:**
- "Indie rock show at 400-cap venue, sold out. Band is The Hollow Suns. Set was 70 minutes, 14 songs. Highlights: opening song with the lights killing and a single spotlight (the crowd went silent), the mid-set acoustic section on stage floor (singer came down to crowd level), the final 3-song run where the room was completely losing it. Encore was the fan-favorite unreleased track — first time playing it live. Show the room, the band, and especially the crowd in the final songs."
- "Festival mainstage set: electronic producer on the second day of a 3-day festival, 9pm timeslot, about 8,000 people. The set was dark warehouse techno until the third drop when the confetti cannons went off and the crowd went wild. Show the buildup, the cannon moment, the laser rig, and the crowd from stage perspective."
- "String quartet classical concert in a cathedral: all-Bach program, 90 minutes. The acoustic was incredible — no amplification in a 400-year-old space. Show the pre-concert empty cathedral, the quartet's entrance, close-ups of bowing technique during the fast movements, and the standing ovation."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `concert_type` | Show category | `"club_show"`, `"festival_set"`, `"theater"`, `"arena"`, `"classical"`, `"outdoor"` |
| `artist_name` | Performer | `"The Hollow Suns"` |
| `venue_name` | Location | `"Webster Hall"`, `"Glastonbury Pyramid Stage"` |
| `setlist_highlights` | Key moments | `["acoustic section", "confetti drop", "unreleased track"]` |
| `crowd_size` | Audience scale | `"400"`, `"8000"`, `"50000"` |
| `show_crowd` | Audience reaction shots | `true` |
| `show_stage_production` | Lights/pyro/effects | `true` |
| `tone` | Video energy | `"documentary"`, `"hype_reel"`, `"cinematic"`, `"intimate"` |
| `duration_minutes` | Video length | `3`, `5`, `8`, `15` |
| `platform` | Distribution | `"instagram"`, `"youtube"`, `"press_kit"`, `"artist_website"` |

## Workflow

1. Describe the show, highlights, and what made this performance worth documenting
2. NemoVideo structures the concert narrative (pre-show atmosphere → performance → peak moment → close)
3. Artist name, venue, date, and setlist callouts added automatically
4. Export with audio-synced editing and appropriate pacing for the genre

## API Usage

### Club Show Recap Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "concert-video-maker",
    "input": {
      "prompt": "Post-punk band show at The Bowery Electric NYC, 300 capacity, sold out for the third consecutive time. Set was 65 minutes. Show: the pre-show lineup outside (they always line up early), the room filling up, the band walking on with no announcement, the first song which opens with a feedback shriek that parts the crowd, the deep cut at Song 8 where only the hardcore fans knew every word, the ending where the guitarist smashed a cheap guitar they had bought specifically for this, and the crowd staying in the room after the lights came up.",
      "concert_type": "club_show",
      "artist_name": "Static Palms",
      "venue_name": "The Bowery Electric",
      "setlist_highlights": ["no-announcement entrance", "deep cut Song 8", "guitar smash finale"],
      "crowd_size": "300",
      "show_crowd": true,
      "show_stage_production": false,
      "tone": "documentary",
      "duration_minutes": 5,
      "platform": "youtube",
      "hashtags": ["ConcertVideo", "LiveMusic", "PostPunk", "NYCShows", "StaticPalms"]
    }
  }'
```

**Response:**
```json
{
  "job_id": "concert_abc123",
  "status": "processing",
  "estimated_seconds": 110,
  "poll_url": "https://mega-api-prod.nemovideo.ai/v1/jobs/concert_abc123"
}
```

### Festival Set Highlight Reel

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "concert-video-maker",
    "input": {
      "prompt": "Electronic producer set at Primavera Sound Barcelona, second stage, 10,000 capacity, 11pm Saturday slot. This was the peak of the festival weekend for our audience. Show: the stage from audience perspective (you can see the ocean behind the stage), the producer behind the decks with the Barcelona skyline lit up, the confetti drop at the set peak, and the crowd from the stage looking out at 10,000 people with their phones up. The set was 90 minutes of peak-hour techno and it was the best 90 minutes of the year.",
      "concert_type": "festival_set",
      "crowd_size": "10000",
      "show_crowd": true,
      "show_stage_production": true,
      "tone": "hype_reel",
      "duration_minutes": 3,
      "platform": "instagram"
    }
  }'
```

## Tips for Best Results

- **The peak moment is the centerpiece**: Every concert has one moment — the guitar smash, the confetti drop, the crowd going silent — build the video to arrive there and let it breathe
- **Crowd reaction is the proof**: Set `show_crowd: true` — what 8,000 people do during a drop is more compelling than the production alone
- **Venue and capacity set the story**: "Sold out 400-cap room" carries different weight than "one of 50,000 at a festival" — include both the number and the context
- **Show genre-appropriate energy**: Club show documentary is intimate and grainy; festival hype reel is wide shots and production; classical is slow and reverent — set `tone` to match
- **Pre-show and post-show are content too**: The queue outside, the empty room before doors, the crowd lingering after — these frame the show as an event, not just a recording

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| YouTube | 1920×1080 | 5–20 min |
| Instagram Reels | 1080×1920 | 60–90s |
| Press kit | 1920×1080 | 3–5 min |
| Artist website | 1920×1080 | 5–10 min |

## Related Skills

- `live-performance-video` — Broader live performance content beyond concerts
- `band-promo-video` — Promotional content for the artist
- `music-lyric-video` — Song-specific content with lyrics overlay
- `cover-song-video` — Performance content for covers

## Common Questions

**Can I create a concert recap from footage shot on multiple phones?**
Yes — describe the different angles and moments you captured (front row, side stage, balcony). NemoVideo edits multi-source concert footage into a cohesive narrative.

**What length works best for concert content on Instagram?**
60-90 seconds with the peak moment in the first 20 seconds. Show the most impressive 90 seconds of the night — the full set recap goes on YouTube; the hook moment goes on Instagram.

**Can I create content for classical and jazz performances?**
Yes — set `concert_type: "classical"` or describe the specific genre. The pacing, music treatment, and shot style shift to match the genre's aesthetic expectations.
