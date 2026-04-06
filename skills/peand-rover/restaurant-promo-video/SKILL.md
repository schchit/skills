---
name: restaurant-promo-video
version: 1.0.4
displayName: "Restaurant Promo Video Maker"
description: >
  Describe your restaurant and NemoVideo creates the promo video. Showcase your signature dishes, your kitchen, your atmosphere — and get a 30-60 second video ready for Instagram, Google Business, DoorDash, or your own website.

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

> 🎵 Ready to restaurant promo video! Just send me a video or describe your project.

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


# Restaurant Promo Video Maker — Create Marketing and Menu Content for Food Businesses

Describe your restaurant and NemoVideo creates the promo video. Showcase your signature dishes, your kitchen, your atmosphere — and get a 30-60 second video ready for Instagram, Google Business, DoorDash, or your own website.

## When to Use This Skill

Use this skill for restaurant and food business marketing content:
- Create social media promo videos for new menu launches
- Film restaurant ambiance and atmosphere showcase videos
- Build delivery app listing videos for DoorDash, UberEats, or Grubhub
- Create grand opening announcement videos for new locations
- Produce seasonal menu or limited-time offer promotion videos
- Generate video content for Google Business Profile and restaurant websites

## How to Describe Your Restaurant

Be specific about the cuisine, signature dishes, atmosphere, and what makes you different.

**Examples of good prompts:**
- "Italian trattoria in downtown Chicago: signature dishes are house-made tagliatelle with truffle butter, wood-fired branzino, and the tiramisu table-side. Warm candlelit interior, exposed brick. Video for Instagram — make it feel date-night romantic, 30 seconds."
- "Fast casual Korean BBQ spot: self-serve KBBQ at $28/person all-you-can-eat. Show the tabletop grills, the meat quality (wagyu, pork belly, brisket), the banchan spread. TikTok video, energetic, show the grill smoke."
- "New bakery grand opening: sourdough loaves, laminated croissants, seasonal fruit tarts. Small artisan shop, local ingredients sourced within 50 miles. Video for Google Business Profile and local Instagram — neighborhood feel."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `promo_type` | Video purpose | `"social_media"`, `"grand_opening"`, `"menu_launch"`, `"delivery_listing"`, `"website"` |
| `cuisine_type` | Food style | `"italian"`, `"korean"`, `"mexican"`, `"american"`, `"bakery"` |
| `signature_dishes` | Key items to feature | `["tagliatelle truffle", "wood-fired branzino", "tiramisu"]` |
| `atmosphere` | Venue vibe | `"romantic"`, `"casual"`, `"fast_casual"`, `"upscale"`, `"family"` |
| `include_cta` | Call to action | `"reserve_now"`, `"order_online"`, `"visit_us"` |
| `duration_seconds` | Video length | `15`, `30`, `60` |
| `platform` | Target platform | `"instagram"`, `"tiktok"`, `"google_business"`, `"website"` |

## Workflow

1. Describe the restaurant concept, signature dishes, and atmosphere
2. NemoVideo builds the visual narrative (ambiance → dishes → CTA)
3. Restaurant name, dish labels, and call-to-action overlaid automatically
4. Export in format optimized for your marketing channel

## API Usage

### Instagram Restaurant Promo

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "restaurant-promo-video",
    "input": {
      "prompt": "Upscale sushi omakase in San Francisco: 18-course chef-curated menu at $185/person. Feature the nigiri plating (uni, otoro, wagyu hand roll), the intimate 12-seat bar setting, the chef interaction. Premium feel — slow motion on the uni placement, close-up on the glistening fish. Instagram for affluent food audience.",
      "promo_type": "social_media",
      "cuisine_type": "japanese",
      "signature_dishes": ["uni nigiri", "otoro", "wagyu hand roll"],
      "atmosphere": "upscale",
      "include_cta": "reserve_now",
      "duration_seconds": 30,
      "platform": "instagram",
      "hashtags": ["Omakase", "SushiSF", "FineFood", "ChefExperience"]
    }
  }'
```

**Response:**
```json
{
  "job_id": "promo_ghi789",
  "status": "processing",
  "estimated_seconds": 85,
  "poll_url": "https://mega-api-prod.nemovideo.ai/v1/jobs/promo_ghi789"
}
```

### Grand Opening Announcement Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "restaurant-promo-video",
    "input": {
      "prompt": "Grand opening of Mariscos La Costa in East LA: seafood-focused Mexican restaurant, specialty is aguachile negro (black), tostadas with marlin ceviche, and their signature whole fried snapper. Family-owned, opening March 29. Neighborhood feel, community excitement, show the kitchen and the owners. CTA: join us opening weekend.",
      "promo_type": "grand_opening",
      "cuisine_type": "mexican",
      "signature_dishes": ["aguachile negro", "marlin ceviche tostada", "whole fried snapper"],
      "atmosphere": "family",
      "include_cta": "visit_us",
      "duration_seconds": 45,
      "platform": "instagram",
      "voiceover": true
    }
  }'
```

## Tips for Best Results

- **Lead with your most photogenic dish**: The video's opening 3 seconds determines if people stop scrolling — put your best dish first
- **Atmosphere description shapes the visual mood**: "candlelit romantic" vs "energetic fast casual" gets completely different music, pacing, and color grading
- **Include the price point if it's a selling point**: "$28 KBBQ all-you-can-eat" or "$185 omakase" — pricing context sets expectations and attracts the right customers
- **CTA at the end**: Always set `include_cta` — whether it's "reserve now", "order online", or "visit us", restaurant promos need a clear next step
- **Platform affects format**: Instagram wants aesthetic and slow pans; TikTok wants fast cuts and steam/sizzle moments

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| Instagram Reels | 1080×1920 | 15–60s |
| TikTok | 1080×1920 | 15–60s |
| Google Business | 1920×1080 | 30–60s |
| Website Hero | 1920×1080 | 30–90s |

## Related Skills

- `food-vlog-maker` — Story-driven food content (less promotional, more personal)
- `recipe-video-maker` — Show how your signature dishes are made
- `tiktok-content-maker` — General short-form social content
- `product-photography-enhance` — Improve food photography before video

## Common Questions

**Can I create videos for a delivery app listing?**
Set `promo_type: "delivery_listing"` and describe your top 3-5 items with clear visual appeal. NemoVideo formats the output for DoorDash and UberEats menu video specs.

**What if I want to show the kitchen and chef?**
Describe it in the prompt ("show the kitchen, the chef plating, the open-flame grill"). NemoVideo incorporates back-of-house content naturally into the restaurant narrative.

**Can small restaurants with limited photos use this?**
Yes — describe the dishes and atmosphere in detail even without photos. NemoVideo generates a representative visual from the description. For best results, upload 3-5 actual dish photos.
