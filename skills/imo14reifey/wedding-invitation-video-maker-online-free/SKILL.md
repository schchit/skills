---
name: wedding-invitation-video-maker-online-free
version: "1.0.0"
displayName: "Wedding Invitation Video Maker Online Free — Create Beautiful Wedding Invites with AI"
description: >
  Create stunning wedding invitation videos for free using AI — personalized animated invitations with couple's names, wedding date and venue details, photo slideshows, elegant typography, romantic music, and RSVP information. NemoVideo generates broadcast-quality wedding invites from your details alone: choose from romantic, modern, rustic, or traditional styles, add your favorite photos, customize colors to match your theme, and share via WhatsApp, Instagram, or email — replacing expensive printed invitations with shareable video invites that guests actually watch.
metadata: {"openclaw": {"emoji": "💍", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Wedding Invitation Video Maker Online Free — Beautiful Wedding Invites with AI

Printed wedding invitations cost $3-$8 per card, plus envelopes, plus postage — $500-$1,500 for 200 guests. They take 2-4 weeks to design, print, and mail. Half arrive after the guest has already heard through the grapevine. The other half sit on a counter until the RSVP deadline passes. Video wedding invitations solve every problem printed invitations create: they cost nothing to distribute (WhatsApp, Instagram, email), they arrive instantly, they're more engaging (guests actually watch a 30-second video instead of glancing at a card), they contain all the information in one shareable format (date, time, venue, dress code, RSVP link), and they can be updated if details change — no reprinting, no re-mailing. NemoVideo creates personalized wedding invitation videos from your details: couple's names and photos, wedding date and time, venue name and address, dress code, RSVP information, and your choice of style. The AI generates elegant animated typography, photo transitions, romantic background music, and coordinated color themes — producing an invitation video that looks like it was designed by a professional studio, shareable to every guest in seconds.

## Use Cases

1. **Classic Romantic — Elegant Animation (30-45s)** — A couple wants a traditional-feeling invitation with modern delivery. NemoVideo creates: soft golden typography animating the couple's names ("Sarah & James"), the wedding date appearing with a gentle fade ("June 14, 2026"), venue details with an animated map pin, engagement photos transitioning with soft dissolves, romantic piano music underneath, and an RSVP card with QR code at the end. The elegance of a calligraphy invitation with the convenience of a WhatsApp forward.
2. **Modern Minimalist — Clean and Bold (20-30s)** — A couple with a contemporary aesthetic wants something sleek. NemoVideo produces: bold sans-serif typography on a clean white background, names in large black text with a single accent color matching their wedding palette, minimal animation (text slides in, pauses, slides out), one hero photo of the couple with a subtle parallax effect, and a modern electronic-ambient music bed. Less is more — the video feels designed, not decorated.
3. **Destination Wedding — Travel Theme (30-60s)** — A couple hosting a destination wedding in Bali wants the invitation to build excitement about the location. NemoVideo generates: opening with a dramatic aerial shot of Bali (AI-generated or stock), transitioning to the couple's photos, venue details with embedded Google Maps directions, travel tips ("Fly into Ngurah Rai International Airport"), hotel block information, a 5-day itinerary preview, and tropical acoustic guitar music. The invitation doubles as a travel planning resource.
4. **Rustic/Boho — Nature-Inspired (30-45s)** — A barn wedding with wildflower themes. NemoVideo creates: watercolor flower animations framing the text, handwritten-style script font for names, earthy color palette (sage green, dusty rose, cream), photos displayed in organic shapes (not rectangles), and gentle acoustic folk guitar. The video feels like opening a hand-painted envelope.
5. **Save-the-Date — Teaser Version (15-20s)** — Before the full invitation, a quick save-the-date video. NemoVideo generates: couple's photo with animated text overlay ("Save the Date"), date in large elegant typography, "Formal invitation to follow" tagline, and 15 seconds of romantic music. Short enough for an Instagram Story, memorable enough to actually save.

## How It Works

### Step 1 — Provide Wedding Details
Enter: couple's names, wedding date, ceremony time, venue name and address, dress code, RSVP deadline, RSVP method (link, email, phone), and any additional details (reception follows, plus-ones welcome, etc.).

### Step 2 — Choose Style and Upload Photos
Pick a style: romantic, modern, rustic, destination, or custom. Upload 3-8 photos of the couple. Choose your color palette or let NemoVideo match it to your photos.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "wedding-invitation-video-maker-online-free",
    "prompt": "Create a romantic wedding invitation video. Couple: Sarah Chen & James Park. Date: Saturday, June 14, 2026 at 4:00 PM. Venue: The Grand Ballroom, Rosewood Hotel, 123 Garden Lane, Napa Valley, CA. Dress code: Black tie optional. RSVP by May 15 at sarahandjames2026.com. Style: classic romantic with golden typography. Colors: ivory, gold, and blush pink. Music: gentle piano with strings. Duration: 35 seconds. Include 5 engagement photos. End with QR code linking to RSVP page.",
    "couple": "Sarah Chen & James Park",
    "date": "Saturday, June 14, 2026",
    "time": "4:00 PM",
    "venue": "The Grand Ballroom, Rosewood Hotel",
    "address": "123 Garden Lane, Napa Valley, CA",
    "dress_code": "Black tie optional",
    "rsvp_deadline": "May 15, 2026",
    "rsvp_url": "sarahandjames2026.com",
    "style": "classic-romantic",
    "colors": ["ivory", "gold", "blush-pink"],
    "music": "piano-strings-romantic",
    "photos": 5,
    "duration": "35 sec",
    "format": "9:16"
  }'
```

### Step 4 — Preview and Share
Preview the invitation. Adjust: typography, photo order, music, timing, or colors. Export in multiple formats: 9:16 for WhatsApp/Instagram Stories, 16:9 for email/website, and 1:1 for Instagram feed. Share instantly to every guest.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Wedding details and style preferences |
| `couple` | string | | Couple's names |
| `date` | string | | Wedding date |
| `time` | string | | Ceremony time |
| `venue` | string | | Venue name |
| `address` | string | | Venue address |
| `dress_code` | string | | Dress code |
| `rsvp_deadline` | string | | RSVP by date |
| `rsvp_url` | string | | RSVP website or contact |
| `style` | string | | "classic-romantic", "modern-minimal", "rustic-boho", "destination", "custom" |
| `colors` | array | | Wedding color palette |
| `music` | string | | "piano-strings", "acoustic-guitar", "electronic-ambient", "orchestral" |
| `photos` | integer | | Number of photos to include |
| `duration` | string | | "15 sec" (save-the-date) to "60 sec" (full invitation) |
| `format` | string | | "9:16", "16:9", "1:1" |
| `qr_code` | string | | URL for RSVP QR code |

## Output Example

```json
{
  "job_id": "wiv-20260328-001",
  "status": "completed",
  "couple": "Sarah Chen & James Park",
  "event_date": "June 14, 2026",
  "duration_seconds": 35,
  "format": "mp4",
  "resolution": "1080x1920",
  "file_size_mb": 8.2,
  "output_url": "https://mega-api-prod.nemovideo.ai/output/wiv-20260328-001.mp4",
  "invitation_details": {
    "style": "classic-romantic",
    "typography": "golden serif (Playfair Display)",
    "colors": "ivory / gold / blush pink",
    "photos_included": 5,
    "music": "piano-strings-romantic (royalty-free)",
    "qr_code": "embedded at 0:30-0:35",
    "sections": ["couple names", "date & time", "venue", "dress code", "RSVP"]
  },
  "additional_exports": {
    "instagram_story": "1080x1920 (9:16)",
    "email_embed": "1920x1080 (16:9)",
    "instagram_post": "1080x1080 (1:1)"
  }
}
```

## Tips

1. **9:16 vertical is the primary format** — Most guests will receive and watch the invitation on their phone via WhatsApp or Instagram. Vertical video fills the full screen. Export 16:9 as secondary for email embeds.
2. **35 seconds is the sweet spot** — Shorter than 25 seconds feels rushed and misses details. Longer than 45 seconds loses attention. 30-40 seconds delivers all essential information at a comfortable reading pace.
3. **Golden typography on dark backgrounds reads as elegant** — The classic wedding invitation aesthetic translates directly to video. Gold or cream serif fonts on navy, forest green, or charcoal backgrounds feel timeless and formal.
4. **End with a QR code for instant RSVP** — Guests watching on their phone can screenshot the QR code and scan it immediately. This reduces RSVP friction by 80% compared to "visit our website" text.
5. **Export all three formats** — 9:16 for WhatsApp/Instagram, 16:9 for email, 1:1 for Instagram feed. One generation produces all three — maximum reach across every channel guests use.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 9:16 | 1080x1920 | WhatsApp / Instagram Stories / TikTok |
| MP4 16:9 | 1920x1080 | Email embed / website / TV display |
| MP4 1:1 | 1080x1080 | Instagram feed / Facebook |
| GIF | 720p | Save-the-date preview |
| JPG | 1080p | Still frame for printed backup |

## Related Skills

- [free-youtube-video-editor](/skills/free-youtube-video-editor) — YouTube editing free
- [video-maker-free](/skills/video-maker-free) — Free video maker
- [free-video-generator-ai](/skills/free-video-generator-ai) — AI video generation
