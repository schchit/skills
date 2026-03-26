# NBA Today Pulse

Version: `1.0.2`

`NBA Today Pulse` 1.0.2 is a self-contained ClawHub skill bundle for premium timezone-aware NBA intelligence with scene-aware game routing, roster-verified player filtering, and ESPN-first structured fallbacks for live and postgame coverage.

This release keeps the public product identity of `NBA Today Pulse` while upgrading the runtime to the v3 router entrypoint. The bundle stays focused on natural-language requests and does not expose a plugin command surface.

## Highlights

- Scene-aware routing for day view, single-game preview, live read, and recap
- Roster-verified player handling that filters stale player names before they reach the final response
- ESPN as the primary structured source, with NBA.com live fallbacks for missing play-by-play and boxscore detail
- Timezone-aware date mapping based on the requestor's local calendar date
- Default in-memory caching only; no persistent cache is enabled by default in the public bundle

## Bundle Layout

```text
nba-today-pulse-v3/
  README.md
  SKILL.md
  TOOLS.md
  tools/
    cache_store.py
    entity_guard.py
    nba_common.py
    nba_teams.py
    provider_espn.py
    provider_nba.py
    timezone_resolver.py
    nba_play_digest.py
    nba_pulse_core.py
    nba_pulse_router.py
    nba_day_snapshot.py
    nba_game_locator.py
    nba_team_roster.py
    nba_game_rosters.py
    nba_game_preview_context.py
    nba_game_live_context.py
    nba_game_recap_context.py
    nba_today_report.py
    nba_advanced_report.py
```

## Installation

This bundle is intended for ClawHub publishing and OpenClaw installation as a self-contained skill directory.

At runtime, the skill executes the bundled router entrypoint:

```bash
python3 {baseDir}/tools/nba_pulse_router.py
```

## Runtime Requirements

- `python3`
- outbound network access to ESPN public JSON endpoints
- outbound network access to NBA.com public endpoints used for live fallbacks

Optional environment variables:

- `OPENCLAW_USER_TIMEZONE`
- `OPENCLAW_TIMEZONE`
- `USER_TIMEZONE`
- `TZ`

## Example Prompts

- `Show today's NBA games in America/Los_Angeles`
- `Show today's Lakers game in Asia/Shanghai`
- `Preview today's Rockets game in Asia/Shanghai`
- `Recap today's Lakers game in Asia/Shanghai`
- `给我今天的 NBA 赛况，按上海时区`
- `给出今天森林狼的比赛预测，按上海时区`

## Packaging Notes

- This public bundle contains the natural-language skill only
- Plugin-based slash-command routing is intentionally excluded
- All bundle scripts are self-contained and resolve imports from the local `tools/` directory
- The public bundle does not enable persistent cache by default
- The bundle contains no private deployment paths, server addresses, SSH commands, or project-internal memory files

## Short Chinese Note

这个 ClawHub 公开包当前默认版本为 `1.0.2`，基于 v3 router 入口构建，重点增强了按场景分流、旧球员脏数据过滤，以及赛中/赛后结构化 fallback。公开包默认不启用持久化缓存，不包含插件或私有运维信息。
