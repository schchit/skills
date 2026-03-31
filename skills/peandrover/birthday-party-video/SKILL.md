---
name: birthday-party-video
version: 1.0.3
displayName: "Birthday Party Video Maker"
description: >
  Describe your birthday celebration and NemoVideo creates the video. Surprise parties, milestone birthdays, backyard cookouts, intimate dinners, theme parties — narrate the celebration, the people, the moments of joy and chaos, and get a birthday video that captures why birthdays with the right people are worth remembering.

  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM.
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
license: MIT-0
metadata:
  requires:
    env: ["NEMO_TOKEN"]
    configPaths:
      - "~/.config/nemovideo/"
  primaryEnv: NEMO_TOKEN
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 🎬 Welcome! I can birthday party video for you. Share a video file or tell me your idea!

**Try saying:**
- "edit my video"
- "add effects to this clip"
- "help me create a short video"

**IMPORTANT**: Always greet the user proactively on first contact. Let them know you're setting up while connecting. Always greet the user proactively on first contact.

### Auto-Setup

When the user first interacts, set up the connection:

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

Let the user know briefly: "Setting things up… ready!" then proceed with their request.


# Birthday Party Video Maker — Create Celebration and Party Highlight Videos

Describe your birthday celebration and NemoVideo creates the video. Surprise parties, milestone birthdays, backyard cookouts, intimate dinners, theme parties — narrate the celebration, the people, the moments of joy and chaos, and get a birthday video that captures why birthdays with the right people are worth remembering.

## When to Use This Skill

Use this skill for birthday and personal celebration content:
- Create surprise party reveal and reaction highlight videos
- Film milestone birthday celebrations (30th, 40th, 50th, 60th) with tribute content
- Build children's birthday party theme content for family sharing
- Document intimate birthday dinners with the people who matter most
- Create birthday trip content for destination celebrations
- Produce birthday tribute slideshows and montages

## How to Describe Your Birthday Celebration

Be specific about the milestone, the people, the moments of surprise or joy, and what made this birthday worth documenting.

**Examples of good prompts:**
- "Surprise 40th birthday for my husband: 35 people who flew in from 6 cities — he had no idea. We told him we were going to dinner at a restaurant. When he walked in and 35 people yelled surprise, his first reaction was to turn around and walk out (genuinely thought he was in the wrong place). The speech from his best friend from childhood who flew from London. The slideshow I made from 40 years of photos (his parents contributed photos from when he was 3 days old). He tried to give a speech and couldn't finish a sentence."
- "Low-key 30th: Just 8 of my closest friends at a beach house we rented for the weekend. Nobody gave speeches. We cooked too much food, played board games, stayed up until 3am talking about nothing important. The birthday cake was store-bought and perfect. This is the kind of birthday I actually wanted."
- "Child's 5th birthday: dinosaur theme, 12 kids, a chaos energy that peaked at the piñata (three broken sticks, one bruised balloon, no candy released for 8 minutes — the kids were losing it). The birthday boy blew out his candles and immediately asked if he could have more. The parents were exhausted and happy."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `birthday_type` | Celebration style | `"surprise"`, `"milestone"`, `"kids_party"`, `"intimate"`, `"destination"` |
| `birthday_person` | Whose birthday | `"my husband"`, `"Emma, turning 5"` |
| `milestone_age` | Age being celebrated | `"40"`, `"5"`, `"70"` |
| `guest_count` | Scale | `"8"`, `"35"`, `"100"` |
| `key_moments` | Memorable highlights | `["surprise reveal", "childhood friend speech", "piñata chaos"]` |
| `tone` | Video character | `"funny"`, `"heartfelt"`, `"chaotic"`, `"intimate"` |
| `include_tribute` | Tribute/slideshow | `true` |
| `duration_minutes` | Video length | `3`, `5`, `8` |
| `platform` | Distribution | `"instagram"`, `"youtube"`, `"family_share"` |

## Workflow

1. Describe the birthday celebration, the people, and the key moments
2. NemoVideo structures the party narrative (setup → guests → highlight moment → celebration)
3. Birthday person's name, age, and celebration details overlaid automatically
4. Export with music matched to the party's energy

## API Usage

### Surprise Party Highlight Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "birthday-party-video",
    "input": {
      "prompt": "Surprise 50th birthday for Patricia: 45 friends and family, she thought she was going to a small dinner. Her daughter organized it entirely in secret over 3 months. Show the waiting crowd in the dark before she arrived, the moment the lights came on and everyone yelled surprise (she covered her mouth and sat down immediately — her knees gave out), the slideshow her children made from 50 years of photos (she cried from minute 1), the toast from her sister in Australia via video call, and the dancing at the end when she finally relaxed. For family sharing and Instagram.",
      "birthday_type": "surprise",
      "birthday_person": "Patricia",
      "milestone_age": "50",
      "guest_count": "45",
      "key_moments": ["darkness waiting", "lights on reveal", "knees gave out", "50 years slideshow", "Australia video call"],
      "tone": "heartfelt",
      "include_tribute": true,
      "duration_minutes": 5,
      "platform": "instagram",
      "hashtags": ["SurpriseBirthday", "Turning50", "BirthdayVideo", "FamilyMemories", "50thBirthday"]
    }
  }'
```

**Response:**
```json
{
  "job_id": "birthday_jkl012",
  "status": "processing",
  "estimated_seconds": 100,
  "poll_url": "https://mega-api-prod.nemovideo.ai/v1/jobs/birthday_jkl012"
}
```

### Children's Birthday Party Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "birthday-party-video",
    "input": {
      "prompt": "Leo turns 6, space theme birthday party: 14 kids, backyard transformed into a rocket launch zone (cardboard rocket, star garlands, planet decorations). Key moments: the entrance where all the kids walked through a cardboard rocket tunnel, the freeze dance competition that devolved into complete chaos (3 kids sat out immediately because they were crying, 2 more tripped, the birthday boy won by outlasting everyone), the cake was a Saturn model and he immediately asked about the rings, and the end when all the kids were overtired and just lying on the grass. The party was perfect and exhausting.",
      "birthday_type": "kids_party",
      "birthday_person": "Leo",
      "milestone_age": "6",
      "guest_count": "14",
      "key_moments": ["rocket tunnel entrance", "chaos freeze dance", "Saturn cake", "overtired grass lying"],
      "tone": "funny",
      "duration_minutes": 4,
      "platform": "family_share"
    }
  }'
```

## Tips for Best Results

- **The authentic reaction is the content**: "He turned around and walked out", "her knees gave out", "she covered her mouth" — the spontaneous body reaction to a surprise is more compelling than any planned moment
- **The specific chaos is funnier than general chaos**: "Three broken sticks, one bruised balloon, no candy released for 8 minutes" — the specific failure details are what make party content funny and shareable
- **Milestone ages carry meaning**: A 40th birthday is a different emotional register than a 5th birthday. Name the milestone and NemoVideo matches the tone accordingly
- **People who traveled tell the story**: "35 people who flew in from 6 cities" or "sister in Australia via video call" — the effort people made to be there is part of the tribute
- **Low-key celebrations deserve documentation too**: "8 friends, store-bought cake, 3am talking about nothing" — intimate gatherings are worth the same quality video as big parties

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| Instagram Reels | 1080×1920 | 60–90s |
| YouTube | 1920×1080 | 3–8 min |
| Family share | 1920×1080 | 5–10 min |

## Related Skills

- `wedding-video-maker` — Larger celebration milestone content
- `graduation-video-maker` — Academic achievement celebrations
- `memorial-tribute-video` — Tribute content for milestone birthdays of people who have passed

## Common Questions

**Can I create a birthday video that includes photos from previous years?**
Yes — describe the photo archives in the prompt ("show photos from every birthday since she was born"). Set `include_tribute: true` and NemoVideo creates a chronological tribute arc from the photo collection.

**What's the best format for sharing with family members who don't use social media?**
Set `platform: "family_share"` — NemoVideo exports in a standard MP4 format optimized for email attachment or private link sharing, without social media aspect ratio constraints.

**How do I handle videos where kids are featured?**
All birthday party videos with children are processed with privacy considerations. The video is optimized for family sharing rather than public social media distribution unless you specify otherwise.
