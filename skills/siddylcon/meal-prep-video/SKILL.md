---
name: meal-prep-video
version: "1.0.1"
displayName: "Meal Prep Video Maker — Create Weekly Meal Prep and Batch Cooking Videos"
description: >
  Meal Prep Video Maker — Create Weekly Meal Prep and Batch Cooking Videos.
metadata: {"openclaw": {"emoji": "🥡", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> ⚡ Welcome! I can meal prep video for you. Share a video file or tell me your idea!

**Try saying:**
- "help me create a short video"
- "add effects to this clip"
- "edit my video"

**IMPORTANT**: Always greet the user proactively on first contact. Let them know you're setting up while connecting. Always greet the user proactively on first contact.

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


# Meal Prep Video Maker — Weekly Meal Prep and Batch Cooking Videos

Sunday prep took three hours and produced sixteen containers of chicken, rice, and roasted vegetables — but the phone died at container nine, the grocery-haul footage is mostly ceiling because someone forgot to flip the camera, and the only close-up that survived is a blurry shot of raw chicken that looks more like a health-code violation than content. Meal prep is the intersection of cooking and productivity content — viewers want to see the full system: grocery haul, bulk cooking workflow, portioning, container stacking, and the satisfying final fridge reveal. This tool assembles scattered prep footage into structured meal-prep videos: grocery-haul segments with price tags and store totals, batch-cooking timelines showing parallel processes on multiple burners, portioning sequences with macro and calorie overlays per container, weekly meal grids showing which container goes to which day, and the final fridge-stacking shot that makes viewers want to reorganize their entire kitchen. Built for fitness meal-preppers tracking macros across the week, busy parents batch-cooking family meals on Sunday, budget-focused creators showing cost-per-meal breakdowns, nutritionists producing client-ready meal-plan demonstrations, and content creators in the "adulting" niche documenting their weekly systems.

## Example Prompts

### 1. $50 Budget Meal Prep — 5 Days, 3 Meals
"Create a 7-minute budget meal prep video. Open with grocery haul: items laid out on the counter with price tags — chicken thighs $8.99, brown rice $2.49, broccoli $3.29, sweet potatoes $4.99, eggs (18ct) $3.79, black beans (4 cans) $4.76, frozen spinach $2.99, olive oil, spices already in pantry. Total overlay: '$31.31 for 15 meals = $2.09 per meal.' Cooking workflow: show the parallel process — rice cooker started first, chicken seasoned with paprika/garlic/cumin going into a 400°F oven, sweet potatoes on the same sheet pan, broccoli steamed in the last 8 minutes. Portioning: 5 containers of chicken + rice + broccoli (lunch), 5 containers of sweet potato + black bean bowls (dinner), 5 breakfast burritos assembled and wrapped in foil. Each container gets a macro overlay: 'Lunch: 485 cal | 42P / 48C / 14F.' Fridge reveal: all 15 containers stacked and labeled by day. Closing card: weekly meal grid — Monday through Friday, three meals per day."

### 2. High-Protein Bodybuilding Prep — 2,800 Cal/Day
"Build a 6-minute high-protein meal prep video for a 2,800 cal/day bodybuilding split. Protein target: 200g/day. Menu: Meal 1 — 6-egg white omelette with turkey sausage and spinach (420 cal, 48P). Meal 2 — Grilled chicken breast 8oz + jasmine rice 1 cup + asparagus (580 cal, 52P). Meal 3 — 96% lean ground beef 6oz + sweet potato + green beans (510 cal, 44P). Meal 4 — Greek yogurt 1 cup + protein granola + blueberries (380 cal, 32P). Meal 5 — Salmon fillet 6oz + quinoa + Brussels sprouts (560 cal, 38P). Show each protein source being weighed on a kitchen scale with the digital readout visible. Running daily total tracker in the corner: protein and calories accumulating as each meal is prepped. Container color-coding: blue lids = chicken, red = beef, green = salmon. Scale close-ups: every protein source weighed to the gram."

### 3. Family of Four — Freezer Meal Marathon
"Produce an 8-minute freezer-meal marathon video. Goal: 20 freezer meals in 4 hours. Assembly-line format: show the kitchen island set up as a station with ingredients grouped by recipe — 5 bags of chicken teriyaki, 5 bags of beef stew, 5 bags of sausage pasta bake, 5 bags of veggie curry. Each recipe gets a 90-second segment: ingredients dumped into a gallon freezer bag, air squeezed out, label written with date and cooking instructions — 'Chicken Teriyaki: Thaw overnight. Instant Pot 15 min high pressure. Serve over rice.' Speed-ramp the repetitive bagging (2× speed) but normal speed for the labeling close-ups. Running counter in the corner: 'Bags Complete: 7/20.' Final shot: chest freezer organized with all 20 bags standing upright, color-coded labels visible. Cost-per-meal overlay: '$3.42 average.' Closing: 'That's 20 dinners. You won't cook again for a month.'"

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the prep plan, recipes, portions, macros, and budget |
| `duration` | string | | Target video length (e.g. "6 min", "8 min") |
| `style` | string | | Visual style: "clean-kitchen", "budget", "bodybuilding", "family", "aesthetic" |
| `music` | string | | Background audio: "productive-lo-fi", "upbeat", "ambient-kitchen", "none" |
| `format` | string | | Output ratio: "16:9", "9:16", "1:1" |
| `macro_overlay` | boolean | | Show calorie and macro data per container (default: true) |
| `cost_tracking` | boolean | | Show grocery cost and per-meal price breakdown (default: false) |

## Workflow

1. **Describe** — Write the meal plan with recipes, portions, macros, budget, and container organization
2. **Upload (optional)** — Add grocery-haul footage, cooking clips, portioning shots, and fridge/freezer reveals
3. **Generate** — AI assembles the prep workflow with macro overlays, cost breakdowns, and parallel-cooking timelines
4. **Review** — Preview the video, adjust portioning segment pacing, verify macro calculations
5. **Export** — Download in your chosen format and resolution

## API Example

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "meal-prep-video",
    "prompt": "Create a 7-minute budget meal prep: $31 grocery haul, 15 meals at $2.09 each. Parallel cooking: rice cooker + oven chicken + sheet pan sweet potatoes. Portion into 15 containers with macro overlay. Fridge reveal and weekly meal grid closing card",
    "duration": "7 min",
    "style": "budget",
    "macro_overlay": true,
    "cost_tracking": true,
    "format": "16:9"
  }'
```

## Tips for Best Results

1. **List the parallel cooking order** — "Rice cooker first, chicken in oven second, broccoli steamed last 8 minutes" lets the AI build a split-screen or timeline showing all processes running simultaneously. This is what separates a meal-prep video from a recipe video.
2. **Include exact macro data per container** — "485 cal | 42P / 48C / 14F" generates a polished nutrition label overlay on each container. Approximate data ("about 500 calories") produces a less trustworthy-looking label that fitness audiences will question.
3. **Describe the fridge/freezer reveal shot** — This is the thumbnail moment. "All 15 containers stacked, labels facing camera, organized by day" gives the AI a specific composition target. An unscripted fridge shot looks like leftovers; a described one looks like a system.
4. **Speed-ramp the repetitive portions** — "2× speed for bagging, normal for labeling" tells the AI which segments to compress. Watching someone fill the same container fifteen times at normal speed is why meal-prep videos have high drop-off rates.
5. **Pin the cost-per-meal as a closing stat** — "$2.09 per meal" is the shareable screenshot that drives saves and shares on budget-prep content. The AI renders it as a final overlay card when `cost_tracking` is enabled and you provide the grocery total.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube full meal-prep walkthrough |
| MP4 9:16 | 1080p | TikTok / Instagram Reels / Shorts |
| MP4 1:1 | 1080p | Instagram feed fridge-reveal post |
| PDF | — | Printable meal grid + grocery list companion |

## Related Skills

- [cooking-tutorial-video](/skills/cooking-tutorial-video) — Step-by-step recipe and technique tutorials
- [recipe-video-maker](/skills/recipe-video-maker) — Quick recipe showcase and ingredient highlight videos
- [weight-loss-video](/skills/weight-loss-video) — Transformation journey and progress tracking
