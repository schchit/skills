---
name: museum-tour-video
version: "1.0.0"
displayName: "Museum Tour Video — Create Virtual Museum Tour and Cultural Institution Promotional Videos for Visitor Engagement"
description: >
  Your museum has a permanent collection that took 80 years to assemble, a traveling exhibition opening next month, and an education program that serves 12,000 school children a year — and your social media presence is three photos of gallery openings that attracted 47 likes combined. Museum Tour Video creates virtual tour and promotional videos for museums, art galleries, science centers, and cultural institutions: showcases permanent and traveling exhibitions with the cinematic presentation that reflects the quality of your collection, creates virtual tour content that serves remote visitors and drives in-person attendance from audiences who discovered your museum online, and exports videos for your website, YouTube, Google Arts & Culture, and the school district outreach that fills your education program calendar.
metadata: {"openclaw": {"emoji": "🏛️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Museum Tour Video — Bring Your Collection to the World and the World to Your Collection

## Use Cases

1. **Virtual Exhibition Tours** — Remote visitors, school groups that can't afford field trips, and international audiences who will never visit in person can experience your collection through virtual tour videos. Museum Tour Video creates narrated exhibition walkthrough videos for Google Arts & Culture, your website, and YouTube that build global awareness and drive in-person visits from nearby audiences.

2. **Traveling Exhibition Promotion** — Temporary exhibitions have a limited run and require concentrated promotion to maximize attendance. Create exhibition preview videos showing highlights, artist interviews, and curatorial context for social media campaigns and email marketing in the weeks before opening.

3. **School and Education Program Marketing** — School administrators and teachers booking field trips and in-school programs respond to videos that show the student experience, curriculum connections, and learning outcomes. Museum Tour Video creates education program videos for district outreach that fill your school program calendar months in advance.

4. **Membership and Donor Cultivation** — Museum members and major donors respond to behind-the-scenes content that makes them feel connected to the institution. Create exclusive curator tours, conservation lab access videos, and acquisition announcement content for your membership newsletter and donor stewardship program.

## How It Works

Upload your gallery footage and exhibition materials, describe your target audience and program highlights, and Museum Tour Video creates a professional virtual tour or promotional video ready for every channel your institution uses.

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"skill": "museum-tour-video", "input": {"institution": "City Natural History Museum", "exhibition": "Ancient Egypt: Treasures of the Nile", "format": "virtual-tour", "platform": "youtube"}}'
```
