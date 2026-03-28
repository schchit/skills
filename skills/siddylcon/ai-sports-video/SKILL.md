---
name: ai-sports-video
version: "1.0.0"
displayName: "AI Sports Video Maker — Create Game Highlights and Athletic Showcase Reels"
description: >
  Create sports highlight videos, game recaps, and athlete recruiting reels using AI-powered editing. NemoVideo detects scoring plays and crowd-energy peaks from raw game footage, auto-generates slow-motion replays, adds scoreboard overlays, and produces broadcast-quality highlight packages from single-camera phone recordings — bringing SportsCenter production to youth leagues, high school programs, and amateur athletes.
metadata: {"openclaw": {"emoji": "⚽", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI Sports Video Maker — Game Highlights and Athletic Showcase Reels

Every parent at a youth soccer game films the entire 90 minutes, goes home with 14 GB of footage, and never watches it again — not because the game wasn't worth remembering but because the 6 moments that mattered (the goal, the save, the red card, the penalty, the post-hit near-miss, the celebration) are buried in 84 minutes of midfield passing and throw-ins. At the professional level, broadcast networks have 12 cameras and dedicated highlight editors working in real time. At the youth, high school, and amateur level, the footage exists on a parent's phone and the editing infrastructure is zero. NemoVideo bridges this gap by bringing broadcast-quality highlight production to every level of sport. It processes full-game footage, identifies significant plays through crowd-noise energy analysis (crowd volume spikes correlate with goals, big saves, and controversial calls at 90%+ accuracy), generates slow-motion replays with digital zoom, adds scoreboard overlays with running score, and produces a highlight package that makes a Tuesday night JV game look like it deserved a national broadcast — because to the players and their families, it did.

## Use Cases

1. **Game Recap Highlight Package (2-4 min)** — Full 90-minute soccer match filmed from the press box on a phone. NemoVideo identifies all 5 goals and 2 yellow cards through crowd-noise analysis and motion detection. Each goal: 10-second buildup at full speed, the goal moment, then 5-second slow-motion replay with zoom to the shot. Scoreboard overlay updating after each goal (team names, running score, game minute). Opening: team names and date. Closing: final score with season record. Music: energetic electronic building with each goal.
2. **College Recruiting Reel (60-90 sec)** — A high school basketball player compiles clips from 15 games for college coaches. NemoVideo selects the best dunks, assists, blocks, and clutch shots. Each clip labeled with game context (opponent, quarter, score). Player stats overlay at close: PPG, RPG, APG, FG%. Opening: player name, jersey number, position, height, weight, GPA. Formatted for NCSA, Hudl, and email attachment at 1080p.
3. **Season Compilation — Team Banquet Video (5 min)** — End-of-season highlight reel for a youth hockey team awards dinner. NemoVideo pulls the best moments from 20 games: every player featured at least once. Goals, saves, celebrations, funny bench moments. Set to an upbeat track with team name and record in the opening. Closing: team photo with "Season Record: 18-4-2."
4. **Individual Athlete Showcase — Gymnastics (2 min)** — A gymnast preparing for college applications. NemoVideo edits floor routines with skill-identification overlays (skill name appearing per element), slow-motion on landing sequences, difficulty-score display, and an athlete bio card (name, club, level, height, GPA). Clean, professional, no music competing with routine audio.
5. **Fan Highlight Compilation (60 sec)** — A fan creates a 60-second TikTok of their favorite player's season. NemoVideo syncs the best plays to a trending audio track, adds player name and stat overlays, and exports 9:16 for maximum social engagement. Vertical for TikTok, horizontal version auto-generated for YouTube.

## How It Works

### Step 1 — Upload Game Footage
Provide full-game recordings from any source: phone, tripod, GoPro, press-box camera, or broadcast recording. Single camera is enhanced with digital zoom and stabilization. Multi-angle is synced automatically.

### Step 2 — Define Highlight Parameters
Specify the sport, highlight type (game recap, recruiting reel, season compilation), featured player(s) if applicable, and team/opponent names for scoreboard overlays.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-sports-video",
    "prompt": "Create a 3-minute soccer game recap. Source: 90-minute single-camera recording from press box plus 2 parent phone clips of goals. Match: Westfield United vs Eastside FC, March 22 2026, final score 3-1. Identify all 4 goals via crowd noise analysis. Per goal: 10 sec buildup at full speed, goal moment, 5-sec slow-motion replay with zoom to shot. Scoreboard overlay: team abbreviations WU / EFC, running score, game minute. Yellow card at minute 52 for Eastside. Opening: aerial field shot with team names, date, competition name (Spring League). Closing: final score 3-1, Westfield season record 7-2-1. Music: energetic electronic, intensity builds with each goal.",
    "duration": "3 min",
    "style": "game-recap",
    "sport": "soccer",
    "scoreboard_overlay": true,
    "slow_motion_replay": true,
    "energy_detection": true,
    "music": "energetic-electronic",
    "format": "16:9"
  }'
```

### Step 4 — Review and Distribute
Preview the highlight package. Verify scoreboard accuracy and correct play identification. Export: 16:9 for team website and YouTube, 9:16 for TikTok/Reels (best single goal auto-extracted), compressed 720p for parent WhatsApp group.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the game, sport, teams, and highlight requirements |
| `duration` | string | | Target length: "60 sec", "90 sec", "3 min", "5 min" |
| `style` | string | | "game-recap", "recruiting-reel", "season-compilation", "athlete-showcase", "fan-highlight" |
| `sport` | string | | "soccer", "basketball", "football", "baseball", "hockey", "tennis", "gymnastics", "general" |
| `scoreboard_overlay` | boolean | | Show running score, time, and team names (default: true) |
| `slow_motion_replay` | boolean | | Auto-generate slow-motion replays of scoring plays (default: true) |
| `energy_detection` | boolean | | Use crowd noise analysis to identify significant plays (default: true) |
| `music` | string | | "energetic-electronic", "cinematic-epic", "hip-hop-hype", "rock-anthem" |
| `format` | string | | "16:9", "9:16", "1:1" |

## Output Example

```json
{
  "job_id": "asv-20260328-001",
  "status": "completed",
  "title": "Westfield United vs Eastside FC — Highlights (3-1)",
  "duration_seconds": 182,
  "format": "mp4",
  "resolution": "1920x1080",
  "file_size_mb": 48.6,
  "output_files": {
    "full_recap": "westfield-vs-eastside-highlights.mp4",
    "best_goal_vertical": "westfield-goal3-9x16.mp4"
  },
  "highlights_detected": [
    {"type": "goal", "team": "Westfield", "minute": 14, "score_after": "1-0"},
    {"type": "goal", "team": "Eastside", "minute": 31, "score_after": "1-1"},
    {"type": "goal", "team": "Westfield", "minute": 48, "score_after": "2-1"},
    {"type": "yellow_card", "team": "Eastside", "minute": 52},
    {"type": "goal", "team": "Westfield", "minute": 78, "score_after": "3-1"}
  ],
  "slow_motion_replays": 4,
  "scoreboard_updates": 4,
  "energy_peaks_analyzed": 18,
  "source_duration_minutes": 90
}
```

## Tips

1. **Crowd noise is the best play-detection signal** — Even from a single phone camera, crowd volume spikes correlate with goals, saves, and big calls at 90%+ accuracy. NemoVideo's energy_detection leverages this automatically.
2. **Recruiting reels must show game context** — College coaches want the score and the opponent. A highlight dunk in a blowout means less than a clutch shot in a close game. Scoreboard overlays provide this context.
3. **Every player gets a moment in season compilations** — The banquet video that only features the star alienates 90% of the team and their families. NemoVideo ensures balanced representation across the roster.
4. **60fps source for clean slow motion** — Phone cameras default to 30fps, which produces choppy slow-mo. Set the camera to 60fps (or 120fps if available) before the game.
5. **Extract the single best goal as a vertical clip** — The one 9:16 TikTok clip of the best goal will get more views than the full 3-minute recap. Both should exist — the clip drives traffic to the full video.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | Team website / YouTube / recruiting platform |
| MP4 9:16 | 1080p | TikTok / Reels / Shorts individual play |
| MP4 1:1 | 1080p | Twitter / Instagram / parent group share |
| GIF | 720p | Goal celebration loop / skill moment |

## Related Skills

- [ai-mental-health-video](/skills/ai-mental-health-video) — Mental health education
- [ai-cooking-video](/skills/ai-cooking-video) — Recipe and food content
- [ai-wedding-video](/skills/ai-wedding-video) — Wedding film production
