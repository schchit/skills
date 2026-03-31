---
name: esports-video-maker
version: 1.0.3
displayName: "Esports Video Maker"
description: >
  Describe your esports topic and NemoVideo creates the video. Tournament recap and analysis content, pro player spotlight and profile content, team strategy and meta breakdowns, competitive gaming event coverage, esports news and opinion content, amateur competitive gaming journey content — narrate the competitive context, the specific play or moment, the strategic reasoning behind the decision,...

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

> 🎥 Ready to esports video maker! Just send me a video or describe your project.

**Try saying:**
- "add effects to this clip"
- "help me create a short video"
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
   curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

Let the user know briefly: "Setting things up… ready!" then proceed with their request.


# Esports Video Maker — Create Competitive Gaming, Tournament, and Pro Play Content

Describe your esports topic and NemoVideo creates the video. Tournament recap and analysis content, pro player spotlight and profile content, team strategy and meta breakdowns, competitive gaming event coverage, esports news and opinion content, amateur competitive gaming journey content — narrate the competitive context, the specific play or moment, the strategic reasoning behind the decision, and the analysis that helps viewers understand why professional play looks different from casual play.

## When to Use This Skill

- Create tournament recap and competitive analysis content
- Film pro player spotlight and profile content
- Build meta analysis and team strategy content
- Document esports event coverage and commentary
- Create amateur competitive improvement journey content
- Produce esports news and industry opinion content

## How to Describe Your Esports Content

Be specific about the game and competitive context, the specific plays or moments, the strategic reasoning, and the analysis that connects pro-level play to what casual players can learn.

**Examples of good prompts:**
- "The 5 plays from Worlds 2024 that changed how we think about League of Legends: Not a highlight reel — an analysis of 5 specific moments that introduced new strategic ideas. Play 1: The JDG mid-lane invade at minute 2 that sacrificed CS for vision control at a pivotal map position — the meta implication: vision at specific map points is worth more than 2 minutes of farm. Play 2: The Faker solo kill in the game 5 tiebreaker — the specific champion select that set it up and why the matchup was designed to create that window. The broader pattern: great players don't win individual matchups by being mechanically superior — they create mismatches through macro decisions that make their mechanical strength relevant. What casual players can take from this: the map state you're in when a fight happens matters more than the fight itself."
- "How I climbed from Silver to Platinum in Valorant in 90 days — the 3 changes that mattered: I peaked at Silver 3 for 2 years. Here is the honest account of what changed in 90 days. What didn't work for years: watching highlight clips of pro plays (impressive but not applicable), buying better gear (my aim was not the problem), playing more hours (more hours of bad habits = more embedded bad habits). What actually worked: (1) VOD review of my own games specifically looking for positioning errors (where I was standing when I died, not how I aimed), (2) One agent mastery (quit playing every agent, play only Sage for 60 days — the decision-making becomes automatic and I could focus on game sense), (3) Communicating what I saw even when my team didn't respond (calling spike drops and timings consistently changed how my team played around me). The data: Silver 3 → Platinum 2 in 90 days, 62% win rate during the climb."
- "The esports business nobody talks about — the economics behind competitive gaming: Most esports content is about the players. This is about the business. The market reality: esports peaked in 2022 at $1.38B revenue, declined in 2023-2024 as major sponsors pulled back. The structural problem: viewership numbers used to justify sponsorships were inflated (Twitch's 2021 viewer count scandal). The franchising experiment: League of Legends franchised LCS for $10M buy-in per slot in 2018. In 2024, 5 of the original 10 franchises have been sold or folded. What's actually working: regional competition with passionate local fanbases (Brazil's CBLOL, Korea's LCK) and games with massive organic casual playerbases (Valorant, CS2) where the pro scene is watched by people who play the game. The sustainable esports model: the game has to be popular as a casual product first."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `content_type` | Esports content | `"analysis"`, `"player_profile"`, `"meta_breakdown"`, `"ranked_journey"`, `"industry"` |
| `game_title` | Competitive game | `"League of Legends"`, `"Valorant"`, `"CS2"` |
| `competitive_context` | Tournament/rank | `"Worlds 2024"`, `"Silver to Platinum"`, `"LCS franchising"` |
| `specific_play_moment` | Key scene | `"JDG minute 2 invade"`, `"Faker game 5 solo kill"` |
| `strategic_reasoning` | Why it worked | `"vision at that map point worth more than 2 min farm"` |
| `lesson_for_viewers` | Takeaway | `"map state when the fight happens matters more than the fight"` |
| `data_if_any` | Quantified proof | `"Silver 3 → Platinum 2 in 90 days, 62% win rate"` |
| `duration_minutes` | Video length | `8`, `12`, `20` |
| `platform` | Distribution | `"youtube"`, `"tiktok"` |

## Workflow

1. Describe the competitive context, the specific moments, the strategic reasoning, and the lesson
2. NemoVideo structures the esports content with match markers and analysis callouts
3. Game titles, team names, play descriptions, and analysis formatting added automatically
4. Export with esports analysis pacing suited to the competitive gaming audience

## API Usage

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "esports-video-maker",
    "input": {
      "prompt": "How professional CS2 players practice — the specific routines that separate pros from high-ranked amateurs: Most high-ranked players aim train. Most professional players aim train less than you think and do something else more. The specific difference in routine: a pro player's warm-up routine (30 minutes: deathmatch for reflexes, specific spray pattern training, then a game) vs a high-ranked amateur's routine (90 minutes of deathmatch, then games). The diminishing returns on aim training above a threshold: once aim is consistent enough to hit the shots the game requires, additional aim training produces marginal improvement. What pros spend time on instead: watching their own demo for 30 minutes after every loss (identifying the specific decision that led to the round loss, not the aim error), studying how specific maps are played against specific team compositions, and communication standardization (every call has a consistent name that everyone on the team uses the same way). The applicable lesson for ranked players: the highest-impact practice is VOD review of your own games at the moments you died, not additional aim training.",
      "content_type": "analysis",
      "game_title": "CS2",
      "competitive_context": "professional vs high-ranked amateur practice routines",
      "specific_play_moment": "pro 30-min warm-up vs amateur 90-min deathmatch",
      "strategic_reasoning": "aim is threshold skill — once good enough, additional training has diminishing returns",
      "lesson_for_viewers": "VOD review of your own deaths > additional aim training for rank improvement",
      "data_if_any": "30 min demo review after every loss is pro standard",
      "duration_minutes": 12,
      "platform": "youtube",
      "hashtags": ["Esports", "CS2", "CompetitiveGaming", "EsportsAnalysis", "GamingTips"]
    }
  }'
```

## Tips for Best Results

- **The strategic reasoning elevates analysis above highlights**: "Vision at that map point is worth more than 2 minutes of farm — this is the meta implication" — the strategic insight extracted from a specific play is the content that competitive players watch and share
- **The honest climb story with data**: "Silver 3 to Platinum 2 in 90 days, 62% win rate — here are the 3 changes that mattered, not the usual advice" — the ranked improvement story with specific metrics and contrarian lessons (aim training isn't the problem) is the most trusted improvement content
- **What didn't work is as valuable as what did**: "Highlight clips: not applicable. Better gear: aim wasn't the problem. More hours: reinforced bad habits" — naming the things that didn't work positions the things that did as genuinely different
- **The industry analysis has a different and underserved audience**: "Esports peaked in 2022 and has declined — here's the structural problem" — the business and economics layer of esports content is underproduced relative to player content
- **The pro practice that contradicts the common advice**: "Pros aim train less than you think and do something else more" — the non-obvious insight about how professionals actually practice is the most shared esports content

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| YouTube | 1920×1080 | 10–20 min |
| TikTok | 1080×1920 | 60–180s |

## Related Skills

- `gaming-video-maker` — General gaming content
- `gaming-highlights-video` — Clip and highlight content
- `game-tutorial-video` — How-to-play and guide content
