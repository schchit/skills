# NBA Today Pulse Tool Notes

Version: `1.0.2`

This public bundle returns premium timezone-aware NBA intelligence with scene-aware game routing, roster-verified player filtering, and ESPN-first structured fallbacks for live and postgame coverage.

## Environment Variables

- `OPENCLAW_USER_TIMEZONE`
- `OPENCLAW_TIMEZONE`
- `USER_TIMEZONE`
- `TZ`

Notes:

- Any one valid timezone variable is sufficient
- If no timezone can be resolved, the tool asks the user to provide one
- The public bundle does not require persistent cache and does not enable disk cache by default

## Common Commands

```bash
python3 {baseDir}/tools/nba_pulse_router.py --tz Asia/Shanghai --date 2026-03-25 --lang zh --format markdown
python3 {baseDir}/tools/nba_pulse_router.py --tz America/Los_Angeles --date 2026-03-25 --lang en --format markdown
python3 {baseDir}/tools/nba_pulse_router.py --tz Asia/Shanghai --date 2026-03-25 --team LAL --lang zh --format markdown
python3 {baseDir}/tools/nba_pulse_router.py --tz Asia/Shanghai --date 2026-03-25 --team HOU --analysis-mode pregame --lang zh --format markdown
python3 {baseDir}/tools/nba_pulse_router.py --tz Asia/Shanghai --date 2026-03-25 --team LAL --analysis-mode live --lang zh --format markdown
python3 {baseDir}/tools/nba_pulse_router.py --tz Asia/Shanghai --date 2026-03-25 --team CHA --analysis-mode post --lang zh --format markdown
```

## Semantic Contract

- `today` means the requestor's local calendar date, not ESPN's default league date
- The router inspects `D-1 / D / D+1` candidate scoreboards and filters games into the local date
- Specifying a team switches to a single-game scene
- `--analysis-mode auto|pregame|live|post` selects the scene; `auto` follows the actual game state
- Public output must stay grounded in structured facts and must not invent missing details
- Player names should be verified against current roster or actual game-participant data before appearing in the final response
- If ESPN live/post detail is incomplete, the runtime may fall back to NBA.com live boxscore or play-by-play data
- The bundle does not provide betting picks or gambling recommendations
- The bundle does not automatically switch to generic web search

## Current Data Sources

- `GET {espnBaseUrl}/scoreboard?dates=YYYYMMDD`
- `GET {espnBaseUrl}/summary?event=<eventId>`
- `GET {espnBaseUrl}/teams/<teamId>/roster`
- `GET {espnBaseUrl}/teams/<teamId>/injuries`
- `GET {espnBaseUrl}/teams/<teamId>/statistics`
- `GET {espnBaseUrl}/teams/<teamId>/schedule`
- `GET {nbaStatsBaseUrl}/scoreboardv2?...`
- `GET {nbaStatsBaseUrl}/commonteamroster?...`
- `GET {nbaLiveBaseUrl}/boxscore/boxscore_<gameId>.json`
- `GET {nbaLiveBaseUrl}/playbyplay/playbyplay_<gameId>.json`
