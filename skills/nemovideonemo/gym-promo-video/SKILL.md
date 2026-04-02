---
name: gym-promo-video
version: "1.0.0"
displayName: "Gym Promotional Video — Create Gym Membership and Fitness Studio Promotional Videos for Member Acquisition"
description: >
  Your gym has new equipment, a renovated locker room, four certified trainers, and a January membership special that nobody outside your existing members knows about. The gym three miles away with identical equipment is running fifteen-second videos on Instagram showing their floor at peak hours, their trainers spotting members on PRs, and a countdown to their membership offer — and they signed up forty new members last month. Gym Promotional Video creates membership acquisition and facility showcase videos for gyms, fitness studios, and boutique fitness concepts: tours the facility highlighting equipment and amenities, showcases trainer credentials and class formats, builds urgency around membership offers and seasonal promotions, and exports vertical ads for Meta and TikTok alongside horizontal videos for YouTube pre-roll and your website homepage.
  NemoVideo gives gym owners and fitness studio marketers a fast path to professional membership promotion videos: describe your facility, membership offer, and target member, upload your gym footage, and receive polished promotional videos ready for Meta and TikTok ads, your Google Business listing, and the local social media campaigns that fill your membership roster.
  Gym Promotional Video gives fitness facility operators a repeatable content system for every moment in the membership marketing calendar — new year campaigns, summer body promotions, equipment additions, trainer introductions, and the ongoing social content that keeps your gym top of mind for the local residents who are one compelling video away from walking through your door.
metadata: {"openclaw": {"emoji": "🏋️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Gym Promotional Video — Fill Your Membership Roster

## Use Cases

1. **Membership Drive Campaigns** — January new year campaigns, summer body promotions, and back-to-school specials. Gym Promotional Video creates urgency-driven membership offer videos with limited-time pricing, facility highlights, and a clear call-to-action for social media ads and email campaigns.

2. **Facility Tour Videos** — Prospective members want to see the space before they visit. A professional facility tour video on your Google Business listing, website, and social profiles reduces the barrier to first visit and increases the conversion rate from online search to in-person trial.

3. **Trainer and Class Showcase** — Group fitness classes, personal training packages, and specialty programs each need their own promotional video. Showcase instructor energy, class format, and the community atmosphere that differentiates your studio from the big-box gym down the street.

4. **Corporate Wellness Partnerships** — Pitching gym membership benefits to local employers requires a professional overview video. Gym Promotional Video creates corporate wellness pitch videos highlighting group rates, flexible access, and the employee health outcomes that justify the benefit cost.

## How It Works

Upload your facility and class footage, describe your membership offer, and Gym Promotional Video edits and exports platform-ready promotional videos for every channel in your member acquisition strategy.

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"skill": "gym-promo-video", "input": {"footage_urls": ["https://..."], "offer": "First month free with annual membership", "platform": "instagram"}}'
```
