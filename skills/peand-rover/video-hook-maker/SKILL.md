---
name: video-hook-maker
version: "1.0.0"
displayName: "Video Hook Maker — Generate Scroll-Stopping Hooks for YouTube TikTok and Reels"
description: >
  Generate scroll-stopping video hooks using AI — create opening lines, text overlays, and first-frame strategies that grab attention in the first 1-2 seconds. NemoVideo analyzes your video's topic and audience to produce multiple hook variations: controversial statements, curiosity gaps, surprising statistics, direct challenges, story openers, and visual surprises — each designed to stop the scroll and maximize the critical first-impression retention that determines whether platforms push your video or bury it.
metadata: {"openclaw": {"emoji": "🪝", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Video Hook Maker — The First 2 Seconds Decide Everything

Every social media platform makes the same decision about your video within 1-2 seconds: push it to more people, or let it die. YouTube measures click-through rate on the thumbnail and retention in the first 30 seconds. TikTok tracks swipe-away rate in the first 1.5 seconds. Instagram measures the initial skip rate on Reels. The hook — the first thing the viewer sees and hears — determines the outcome of this algorithmic judgment. A strong hook gets the video shown to 10,000 people. A weak hook gets it shown to 200. Same content, same editing, same value — the only difference is whether the first sentence stopped the scroll. Most creators know hooks matter. Few know how to write them consistently. The difference between "Hey guys, today I want to talk about investing" (weak) and "Your bank is lying to you about how money works" (strong) is the difference between 500 views and 50,000 views. NemoVideo generates multiple hook variations for any video topic, each using a proven psychological trigger: curiosity gaps that demand resolution, controversial claims that provoke engagement, statistics that shatter assumptions, direct challenges that feel personal, and story openings that activate narrative investment. The creator picks the strongest hook; the algorithm rewards the choice.

## Use Cases

1. **YouTube Video — 5 Hook Variations (any topic)** — Topic: "5 Money Habits That Keep You Poor." NemoVideo generates: (A) Controversial: "Your financial advisor is making money by keeping you poor." (B) Curiosity gap: "There's one money habit that millionaires do daily — and it's the opposite of what you'd expect." (C) Statistic: "78% of Americans will retire with less than $50,000 in savings. Here's the habit that separates the other 22%." (D) Direct challenge: "You're doing at least 3 of these — and the fifth one is the one that's actually ruining you." (E) Story: "I was $47,000 in debt at 26. Three years later I had $200,000 invested. The change started with one habit." Creator tests all 5 as different video intros.
2. **TikTok — Ultra-Short Hook + Text Overlay (1.2 sec)** — Topic: "Productivity hack." NemoVideo generates: verbal hook ("Stop making to-do lists. Right now.") + text overlay ("THIS changed everything ⬇️") + visual direction (look directly at camera, lean in, slight pause after "right now"). The entire hook is designed to fire in 1.2 seconds — the TikTok decision window.
3. **Product Ad — Attention + Problem (3 sec)** — Product: noise-canceling earbuds. NemoVideo generates: (A) "Your AirPods can't do this." + visual: hand covering ear in noisy environment. (B) "I wore these on a 14-hour flight and forgot I had them in." (C) "Every other earbud company is lying about noise cancellation. Let me show you." Each hook names the problem and promises the solution in under 3 seconds.
4. **Explainer Video — Curiosity-First Hook (5-8 sec)** — Topic: "How does WiFi actually work?" NemoVideo generates: "WiFi is not what you think it is. It's not radio waves from your router to your phone — well, it is, but the way it actually works is so much weirder. And by the end of this video, you'll understand something that 99% of engineers get wrong." The hook creates a curiosity gap and an open loop that demands resolution.
5. **Batch Hooks — Content Calendar (10-20 hooks)** — A creator has 10 video topics for the month. NemoVideo generates 3 hook variations per topic — 30 hooks total. The creator selects the strongest for each, with backup hooks available for A/B testing thumbnails and titles.

## How It Works

### Step 1 — Provide Video Topic
Describe: the video's subject, target audience, platform, and tone. The more context, the more targeted the hooks.

### Step 2 — Set Hook Parameters
Choose: number of variations, hook styles (controversial, curiosity, statistic, story, challenge), duration constraint, and whether to include text overlay and visual direction.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "video-hook-maker",
    "prompt": "Generate 5 hook variations for a YouTube video about why most diets fail. Target audience: women 25-40 who have tried and quit multiple diets. Tone: empathetic but direct. Include: verbal hook, text overlay suggestion, and visual direction for each. Duration: 3-5 seconds per hook.",
    "topic": "why most diets fail",
    "audience": "women 25-40, diet-experienced",
    "tone": "empathetic-direct",
    "variations": 5,
    "hook_styles": ["controversial", "curiosity", "statistic", "story", "direct-challenge"],
    "include": ["verbal", "text-overlay", "visual-direction"],
    "platform": "youtube",
    "duration": "3-5 sec"
  }'
```

### Step 4 — Select and Apply
Review all variations. Pick the strongest. Apply as the video's opening — either record it yourself or feed it into NemoVideo's video production pipeline.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Topic and audience context |
| `topic` | string | | Video subject |
| `audience` | string | | Target viewer demographic and mindset |
| `tone` | string | | "empathetic", "aggressive", "humorous", "authoritative", "casual" |
| `variations` | integer | | Number of hook versions (default: 5) |
| `hook_styles` | array | | ["controversial","curiosity","statistic","story","direct-challenge","question"] |
| `include` | array | | ["verbal","text-overlay","visual-direction","thumbnail-text"] |
| `platform` | string | | "youtube", "tiktok", "reels", "ad" |
| `duration` | string | | "1.2 sec" (TikTok), "3-5 sec" (YouTube), "2-3 sec" (ad) |
| `batch_topics` | array | | Multiple topics for batch hook generation |

## Output Example

```json
{
  "job_id": "vhm-20260328-001",
  "status": "completed",
  "topic": "Why Most Diets Fail",
  "hooks": [
    {
      "style": "controversial",
      "verbal": "Your nutritionist doesn't want you to know this — because if you did, you'd never need them again.",
      "text_overlay": "They don't want you to know this 🤫",
      "visual": "Direct eye contact, slight head shake, leaning toward camera",
      "duration": "4.2 sec"
    },
    {
      "style": "curiosity",
      "verbal": "There's one thing every failed diet has in common — and it's not willpower, it's not carbs, and it's not calories.",
      "text_overlay": "It's NOT what you think ⬇️",
      "visual": "Counting off on fingers: not willpower, not carbs, not calories. Pause. Direct look.",
      "duration": "4.8 sec"
    },
    {
      "style": "statistic",
      "verbal": "95% of diets fail within one year. But it's not because people lack discipline — it's because the diets themselves are designed wrong.",
      "text_overlay": "95% fail. Here's why. 📊",
      "visual": "Animated stat counter 0→95%, then pivot to direct address",
      "duration": "5.0 sec"
    },
    {
      "style": "story",
      "verbal": "Three years ago I weighed 210 pounds, I'd tried every diet on the internet, and I was about to give up forever. Then my doctor said seven words that changed everything.",
      "text_overlay": "7 words that changed everything",
      "visual": "Old photo briefly shown, then current self, lean in on 'seven words'",
      "duration": "5.5 sec"
    },
    {
      "style": "direct-challenge",
      "verbal": "If you've ever quit a diet and blamed yourself — stop. It wasn't your fault. And I can prove it in the next 8 minutes.",
      "text_overlay": "It's NOT your fault ❤️",
      "visual": "Empathetic eye contact, hand gesture on 'stop', confident nod on 'prove it'",
      "duration": "4.5 sec"
    }
  ]
}
```

## Tips

1. **Test multiple hooks on the same video** — Upload the same video with different hooks as unlisted videos, then check retention graphs. The hook with the highest 5-second retention wins. Replace the public video's hook with the winner.
2. **Controversy gets clicks, empathy gets watch time** — A controversial hook drives high CTR but can cause early drop-off if the content doesn't deliver. Pair controversial hooks with empathetic, value-dense content.
3. **Text overlay + verbal hook = double anchoring** — The viewer reads AND hears the hook simultaneously. Two channels of attention capture beat one. Always pair spoken hooks with on-screen text for maximum retention.
4. **The hook is a promise the video must keep** — "I'll reveal the one strategy that works" creates an obligation. If the video doesn't deliver a clear, satisfying answer, viewers feel cheated and leave negative signals. Strong hooks demand strong content.
5. **Platform timing is non-negotiable** — TikTok: 1.2 seconds. Reels: 1.5 seconds. YouTube: 5-8 seconds. A YouTube-paced hook on TikTok loses the viewer before the first sentence finishes.

## Output Formats

| Format | Content | Use Case |
|--------|---------|----------|
| JSON | Structured hooks with metadata | API pipeline / automation |
| TXT | Plain text hooks | Teleprompter / recording |
| MD | Formatted with visual notes | Creative review |
| CSV | Hook + style + duration | Spreadsheet tracking / A-B testing |

## Related Skills

- [ai-video-script-generator](/skills/ai-video-script-generator) — Full script writing
- [ai-video-summarizer](/skills/ai-video-summarizer) — Video summarization
- [talking-avatar-video](/skills/talking-avatar-video) — Avatar video production
