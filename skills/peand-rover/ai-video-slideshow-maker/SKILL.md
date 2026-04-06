---
name: ai-video-slideshow-maker
version: 1.0.1
displayName: "AI Video Slideshow Maker — Create Stunning Photo and Video Slideshows with Music"
description: >
  Create stunning photo and video slideshows with music using AI — transform photo collections into cinematic video stories with Ken Burns motion effects, beat-synced transitions, animated text overlays, and emotionally matched background music. NemoVideo turns static photos into living memories: applying intelligent motion to every image (pan, zoom, parallax), timing transitions to the music's rhythm, adding contextual text (dates, locations, captions), and producing the slideshow format that makes birthdays anniversaries weddings travel recaps and year-in-review content emotional and shareable. AI slideshow maker, photo to video, photo slideshow with music, picture video maker, memory video creator, photo montage video, slideshow video generator, photo video editor, image to video maker.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# AI Video Slideshow Maker — Static Photos Become Moving Stories

Every phone contains thousands of photos that never become anything. They sit in camera rolls, organized by date but never by story. The birthday party photos stay scattered among 47 other days of photos. The vacation collection lives as 200 unedited images no one will scroll through. The year's highlights are buried in a gallery of 5,000 photos that no single person will ever review. A slideshow transforms this archive into something watchable, shareable, and emotional. Photos arranged in narrative order, set to music, with motion that brings static images to life and transitions that create rhythm — suddenly those scattered camera roll images become a 3-minute film that makes people cry at birthday parties, laugh at year-end gatherings, and feel the emotions of moments they had almost forgotten. The Ken Burns effect (the slow pan and zoom across a still image) was revolutionary when introduced in documentary filmmaking because it proved that static images could create cinematic emotion when given motion and musical context. Every photo slideshow uses this principle: motion transforms observation into experience. A photo of a sunset is pretty. That same photo slowly zooming out to reveal the couple watching it, timed to a musical swell, is cinema. NemoVideo creates slideshows with the production quality of professional memorial videos and wedding films: intelligent motion on every photo, music-synced transitions, contextual text, and emotional arc from first image to last.

## Use Cases

1. **Wedding Slideshow — Love Story in Photos (3-8 min)** — The wedding slideshow is a tradition: photos from childhood through courtship to the wedding day, set to a meaningful song, played during the reception. NemoVideo: arranges photos in chronological narrative (childhood → meeting → dating → engagement → wedding), applies appropriate Ken Burns motion to each photo (slow gentle movements for intimate photos, wider pans for group shots, zoom-in on faces for emotional close-ups), syncs photo transitions to the music's rhythm (clean dissolves on gentle musical moments, cuts on beats for energetic sections), adds date and location text where appropriate (subtle, elegant typography that does not overpower the photos), and produces the slideshow that makes the room cry. The most emotionally charged 5 minutes of any wedding reception.

2. **Birthday Celebration — Year in Moments (2-5 min)** — A birthday slideshow collecting the year's best moments: milestones, celebrations, everyday joys, funny moments, group photos with friends and family. NemoVideo: curates the optimal photo sequence (mixing emotional moments with fun ones, building toward a climactic final section), applies varied motion to prevent visual monotony (pan left on one photo, zoom in on the next, slow zoom out on the third), matches the musical energy to the photo content (upbeat music during party photos, gentle music during sentimental moments), adds birthday-themed text elements ("The Year of [Name]", age milestone displays), and produces a celebration video that makes the birthday person feel loved and everyone else feel connected to the memories.

3. **Travel Recap — Journey in Stills (2-5 min)** — A trip documented in 200 photos needs a 3-minute recap that captures the journey's highlights and emotional arc. NemoVideo: selects the strongest photos from a large collection (or uses all photos provided), arranges in journey order (departure → destinations → experiences → return), applies travel-appropriate motion (wide pans on landscape photos, slow zooms on food and detail shots, parallax effects on layered compositions), adds location text as the journey progresses (city names, country flags, date stamps), syncs to an energetic travel soundtrack, and produces a trip summary that makes viewers want to book a flight.

4. **Memorial Tribute — Celebrating a Life (5-15 min)** — Memorial slideshows celebrate a person's life through photos spanning decades. NemoVideo: arranges photos chronologically across a lifetime (childhood → youth → career → family → later years), applies gentle, respectful motion (slower movements, longer display times than celebration slideshows — giving viewers time to absorb each image), syncs to emotionally appropriate music (classical, acoustic, or the person's favorite songs), adds life-milestone captions ("1965 — First Day of School", "1988 — Wedding Day"), and produces a tribute that honors a life through its visual record. The slideshow that helps a room grieve and celebrate simultaneously.

5. **Year in Review — Annual Highlight Reel (3-5 min)** — Companies, creators, families, and individuals produce annual recaps: the best moments of the past year compiled into a shareable retrospective. NemoVideo: organizes photos by month or theme (January → February → ... December, or Work → Travel → Family → Fun), applies consistent but varied motion across all photos, adds monthly or thematic title cards, syncs transitions to an energetic year-end soundtrack, includes data overlays if desired ("247 coffees consumed", "12 countries visited"), and produces the annual recap that performs well on social media and serves as a personal time capsule.

## How It Works

### Step 1 — Upload Photos
Photo collection (5-500 images). Optionally pre-ordered, or let NemoVideo arrange by metadata (date, location) or content analysis.

### Step 2 — Choose Music and Style
Background music (upload a track or choose from mood-matched options), slideshow style, text overlay preferences, and duration target.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-video-slideshow-maker",
    "prompt": "Create a 4-minute wedding slideshow from 60 photos. Chronological order: childhood (10 photos), meeting and dating (15 photos), engagement (10 photos), wedding day (25 photos). Music: romantic acoustic track building to emotional climax at the wedding section. Ken Burns motion on every photo: gentle slow zoom on portrait shots, slow pan on landscape shots, zoom-to-faces on group shots. Transitions: smooth dissolves synced to music beats, 3-second display per photo average (longer for key moments). Text overlays: elegant white serif font — opening title Their Story, section titles (How It All Began, The Adventure, The Big Day), closing title Forever Starts Now. Fade in from black, fade out to white at end. Export 16:9.",
    "photos": 60,
    "sections": [
      {"name": "How It All Began", "photos": "1-10"},
      {"name": "The Adventure", "photos": "11-25"},
      {"name": "The Promise", "photos": "26-35"},
      {"name": "The Big Day", "photos": "36-60"}
    ],
    "motion": {"type": "ken-burns", "style": "gentle-varied"},
    "music": {"mood": "romantic-acoustic-building", "climax_section": "The Big Day"},
    "transitions": {"type": "dissolve", "sync": "music-beats"},
    "text": {"font": "serif-elegant", "color": "#FFFFFF", "titles": true},
    "duration": "4:00",
    "output": {"format": "16:9", "resolution": "1080p"}
  }'
```

### Step 4 — Review Emotional Arc
Watch the complete slideshow. Check: does the emotional arc build appropriately (gentle start, emotional crescendo, satisfying conclusion)? Are photo display times adequate (not rushing through important images)? Does the music sync feel intentional? Is the overall duration appropriate for the audience context? Adjust pacing and re-render.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Slideshow requirements |
| `photos` | int | | Number of photos |
| `sections` | array | | [{name, photos}] narrative sections |
| `motion` | object | | {type, style, speed} Ken Burns config |
| `music` | object | | {mood, track, climax_section} |
| `transitions` | object | | {type, sync, duration} |
| `text` | object | | {font, color, titles, captions} |
| `duration` | string | | Target total duration |
| `output` | object | | {format, resolution} |

## Output Example

```json
{
  "job_id": "avslw-20260329-001",
  "status": "completed",
  "photos": 60,
  "sections": 4,
  "duration": "4:08",
  "transitions": 59,
  "music_sync": "beat-matched",
  "output": {"file": "wedding-slideshow.mp4", "resolution": "1920x1080"}
}
```

## Tips

1. **3-5 seconds per photo is the sweet spot** — Under 2 seconds and the viewer cannot process the image. Over 7 seconds and attention wanes on a static composition (even with Ken Burns motion). Average 3-5 seconds, with important photos getting 5-7 seconds and transitional photos getting 2-3 seconds.
2. **Ken Burns motion transforms static photos into cinematic moments** — A photo displayed statically feels like a slideshow. A photo with slow, deliberate pan or zoom feels like a film. The motion creates the illusion of depth and dimension that makes viewers feel immersed rather than observing.
3. **Music is 50% of the emotional impact** — The same photos with upbeat music feel celebratory. With melancholic music, they feel nostalgic. With dramatic music, they feel epic. The music choice determines the slideshow's entire emotional character. Choose music that matches the intended emotional experience, not just the occasion.
4. **Beat-synced transitions make slideshows feel professionally produced** — Random-timed transitions feel like a software auto-play. Transitions that land on musical beats feel choreographed and intentional. This single technique elevates a slideshow from "photo auto-play" to "produced video."
5. **Vary the motion to prevent visual fatigue** — If every photo zooms in, the repetition becomes hypnotic and disengaging. Alternate: zoom in → pan left → zoom out → pan right → hold with subtle movement. Variation maintains visual interest across dozens of photos.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p | TV / projector / YouTube |
| MP4 9:16 | 1080x1920 | Instagram Stories / TikTok |
| MP4 1:1 | 1080x1080 | Instagram / Facebook |
| MP4 16:9 | 4K | Premium display |

## Related Skills

- [ai-video-music-sync](/skills/ai-video-music-sync) — Music synchronization
- [ai-video-text-overlay](/skills/ai-video-text-overlay) — Text graphics
- [ai-video-collage-maker](/skills/ai-video-collage-maker) — Multi-video layouts
- [video-montage-maker](/skills/video-montage-maker) — Video montage
