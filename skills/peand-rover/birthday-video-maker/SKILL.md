---
name: birthday-video-maker
version: "1.0.0"
displayName: "Birthday Video Maker — Personalized Tribute Videos Photo Slideshows and Surprise Reels for Any Age"
description: >
  It is the week before your parent's seventieth birthday. You have four hundred photos spanning fifty years on your phone, a folder of childhood videos from a digitized VHS tape, and a group chat with thirty family members who each want to contribute a short clip. The party planner wants a ten-minute tribute video to play at the venue during dinner. Your sibling wants a one-minute version to post publicly. The grandchildren want a looping slideshow for the photo booth. Birthday Video Maker handles the entire production from a single upload: it organizes the photos and videos into a chronological story, applies decade-appropriate visual styles (faded tones for early childhood, full saturation for recent years), incorporates the contributed family clips with smooth transitions, generates title cards for each life chapter, syncs everything to a chosen soundtrack, and exports all three formats simultaneously. No timeline editor, no render queue, no coordinating thirty family members' file submissions manually.
metadata: {"openclaw": {"emoji": "🎂", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Birthday Video Maker — Tribute Videos, Slideshows, and Surprise Reels

## Use Cases

1. **Milestone Birthday Tributes** — Seventieth, eightieth, ninetieth birthdays call for a life retrospective. Birthday Video Maker assembles decades of photos and videos into a chronological narrative with chapter titles, era-matched visual styles, and a narration track generated from your written notes about each period of the honoree's life.

2. **Surprise Party Video** — Friends and family each record a ten-second "happy birthday" clip on their phones. Birthday Video Maker combines all submissions into a single polished reel with consistent audio levels, coordinated transitions, and a title sequence — the kind of production that normally requires a dedicated video editor to assemble.

3. **Kids' Birthday Content** — One-year-old to sweet sixteen: parents capturing the party want a same-day reel for Instagram Stories and a longer keepsake video for the family archive. Birthday Video Maker edits the party footage into a short social reel and a full three-to-five minute family film with a single request.

4. **Corporate Milestone Celebrations** — Employee work anniversaries, retirement send-offs, and team celebrations need a professional tribute video that won't look like a personal slideshow. Birthday Video Maker applies clean, professional styling with animated lower-thirds, brand-consistent color palette, and an appropriate corporate tone.

## How It Works

1. **Upload your media** — Photos, videos, family-submitted clips. Supports mixed formats and quality levels.
2. **Describe the story** — "Tribute video for my dad's 70th birthday. Organize chronologically from childhood to now. Chapter titles for each decade. Funny tone for the first half, sentimental for the second."
3. **Select output formats** — Full tribute film, social reel, looping slideshow, or all three simultaneously.
4. **Download and share** — Each format exports at the correct spec for its destination (venue display, Instagram, photo booth loop).

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "birthday-video-maker",
    "input": {
      "media_urls": ["https://...photos.zip", "https://...family-clips/"],
      "subject": "Dad'\''s 70th birthday",
      "tone": "funny-then-sentimental",
      "outputs": ["10min tribute film", "1min social reel", "looping slideshow"],
      "music_url": "https://...birthday-song.mp3"
    }
  }'
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `media_urls` | array | Photos, videos, or zip archives of submitted clips |
| `subject` | string | Who the video is for and the occasion |
| `tone` | string | `funny`, `sentimental`, `professional`, `funny-then-sentimental` |
| `outputs` | array | Requested formats: tribute film, social reel, slideshow |
| `music_url` | string | Optional: specific song for the soundtrack |
| `chapters` | array | Optional: custom chapter titles for each life period |

## Tips

- Label contributed clips by sender name so Birthday Video Maker can add name lower-thirds to each submission
- Include at least one photo per decade for a complete chronological story
- Specify the venue screen aspect ratio (16:9 for most projection screens, 9:16 for phone-based slideshows)
- For surprise videos, collect submissions via a shared folder link and upload the whole folder in one go
- Mention the honoree's name and key life facts in the subject field to improve generated narration accuracy
