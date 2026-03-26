---
name: nba-today-pulse
description: Premium timezone-aware NBA intelligence with scene-aware game routing, roster-verified player filtering, and ESPN-first structured fallbacks for live and postgame coverage.
user-invocable: true
metadata: {"openclaw":{"skillKey":"nba-today-pulse","requires":{"bins":["python3"]}}}
---

# NBA Today Pulse

Version: `1.0.2`

Return premium timezone-aware NBA intelligence using the requestor's local date, with scene-aware game routing, roster-verified player filtering, and ESPN-first structured fallbacks for live and postgame coverage. Do not invent scores, lineups, player stats, injuries, or matchup reasons.

This skill is packaged as a self-contained ClawHub bundle. All runtime scripts live inside the bundle directory.

## Goal

- If the user asks for today's NBA games, run:
  - `{baseDir}/tools/nba_pulse_router.py --tz <resolved timezone> --lang <auto> --format markdown`
- If the user asks for a specific date, run:
  - `{baseDir}/tools/nba_pulse_router.py --tz <resolved timezone> --date YYYY-MM-DD --lang <auto> --format markdown`
- If the user asks for a specific team, run:
  - `{baseDir}/tools/nba_pulse_router.py --tz <resolved timezone> --date <optional> --team <resolved team> --lang <auto> --format markdown`
- If the user asks for a preview, prediction, or pregame view, run:
  - `{baseDir}/tools/nba_pulse_router.py --tz <resolved timezone> --date <optional> --team <resolved team> --analysis-mode pregame --lang <auto> --format markdown`
- If the user asks for live direction or in-game analysis, run:
  - `{baseDir}/tools/nba_pulse_router.py --tz <resolved timezone> --date <optional> --team <resolved team> --analysis-mode live --lang <auto> --format markdown`
- If the user asks for a recap, review, or postgame view, run:
  - `{baseDir}/tools/nba_pulse_router.py --tz <resolved timezone> --date <optional> --team <resolved team> --analysis-mode post --lang <auto> --format markdown`

## Rules

- "Today" must be computed from the requestor's timezone, not from a league-default US date
- Timezone priority:
  - explicit IANA timezone such as `Asia/Shanghai`
  - explicit city such as `Shanghai` or `Los Angeles`
  - injected user timezone from the environment
- If no timezone can be resolved, ask the user to provide one
- Output language must match the resolved request language:
  - `lang=zh` -> Chinese
  - `lang=en` -> English
- Player names in the final response must stay grounded in current roster or actual game-participant data
- If a player reference cannot be verified, the response should downgrade to a team-group description instead of guessing
- Pregame lineup handling:
  - show confirmed starters when available
  - if not available, explicitly say they are not confirmed
  - do not predict lineups
- Analysis must be derived only from structured facts:
  - predictor / pickcenter / standings / season series / last five games
  - team statistics / schedule context
  - recent plays / win probability / boxscore / article
- Do not output betting recommendations or gambling-oriented advice
- If the data source is incomplete, degrade gracefully and do not fabricate missing facts
- Do not automatically switch to generic web search when structured sources are incomplete

## Parameter Mapping

- Default parameters:
  - `lang=auto-detect from user input`
  - `format=markdown`
- Examples:
  - `Show today's NBA games in America/Los_Angeles` -> `--tz America/Los_Angeles --lang en`
  - `Show NBA games for 2026-03-25 in Europe/London` -> `--tz Europe/London --date 2026-03-25 --lang en`
  - `Show today's Lakers game in Asia/Shanghai` -> `--tz Asia/Shanghai --team LAL --lang en`
  - `Preview today's Rockets game in Asia/Shanghai` -> `--tz Asia/Shanghai --team HOU --analysis-mode pregame --lang en`
  - `Recap today's Lakers game in Asia/Shanghai` -> `--tz Asia/Shanghai --team LAL --analysis-mode post --lang en`
  - `给我今天的 NBA 赛况，按上海时区` -> `--tz Asia/Shanghai --lang zh`
  - `给出今天森林狼的比赛预测，按上海时区` -> `--tz Asia/Shanghai --team MIN --analysis-mode pregame --lang zh`

## Execution

Prefer running the bundled router script directly:

```bash
python3 {baseDir}/tools/nba_pulse_router.py --tz <resolved timezone> --lang <resolved zh|en> --format markdown
```

## Notes

- This 1.0.2 bundle focuses on natural-language skill usage
- Slash-command routing is intentionally not included in this public release
- Data comes primarily from free ESPN public JSON with structured NBA.com live fallbacks where needed
