#!/usr/bin/env python3
"""Render NBA today's games using requestor timezone-aware filtering."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from nba_common import NBAReportError  # noqa: E402
from nba_teams import TEAM_DISPLAY, canonicalize_team_abbr, normalize_team_input  # noqa: E402
from provider_espn import fetch_scoreboard, fetch_summary, fetch_team_schedule, fetch_team_statistics  # noqa: E402
from timezone_resolver import ResolvedTimezone, resolve_timezone  # noqa: E402

I18N = {
    "zh": {
        "title_day": "NBA 今日赛况",
        "title_game": "NBA 单场赛况",
        "timezone": "请求方时区",
        "requested_date": "请求日期",
        "view": "视图",
        "status_final": "已结束",
        "status_live": "进行中",
        "status_pre": "未开赛",
        "no_games": "该时区当天没有 NBA 比赛。",
        "final_section": "已结束比赛",
        "live_section": "进行中比赛",
        "pre_section": "未开赛比赛",
        "overview": "总览",
        "local_tip": "以下时间均为请求方本地时间。",
        "start_time": "开赛时间",
        "venue": "场馆",
        "broadcasts": "转播",
        "records": "战绩",
        "score_by_period": "各节比分",
        "leaders": "球队领袖",
        "starters": "首发名单",
        "lineup_unconfirmed": "首发尚未公布或当前免费数据源不可确认。",
        "injuries": "伤病",
        "recent_plays": "近期关键回合",
        "hotspots": "热点",
        "key_players": "关键球员",
        "status": "状态",
        "latest": "今日",
        "none": "无",
        "filter_team": "目标球队",
        "clock": "比赛时间",
        "team_stats": "球队数据",
        "data_note": "热点仅基于结构化赛况事实，不额外编造。",
        "counts_summary": "总场次",
        "advanced_section": "高阶分析",
        "analysis_summary": "分析摘要",
        "analysis_reasons": "核心依据",
        "analysis_trend": "走势判断",
        "analysis_turning_point": "转折点",
        "analysis_key_matchup": "关键对位",
        "analysis_deep_note": "高阶分析仅基于结构化比赛与球队数据，不提供投注建议。",
    },
    "en": {
        "title_day": "NBA Daily Report",
        "title_game": "NBA Game Report",
        "timezone": "Requestor Timezone",
        "requested_date": "Requested Date",
        "view": "View",
        "status_final": "Final",
        "status_live": "Live",
        "status_pre": "Scheduled",
        "no_games": "No NBA games fall on the requestor's local date.",
        "final_section": "Final Games",
        "live_section": "Live Games",
        "pre_section": "Scheduled Games",
        "overview": "Overview",
        "local_tip": "All times below are in the requestor's local timezone.",
        "start_time": "Start Time",
        "venue": "Venue",
        "broadcasts": "Broadcasts",
        "records": "Records",
        "score_by_period": "Score by Period",
        "leaders": "Team Leaders",
        "starters": "Starting Lineups",
        "lineup_unconfirmed": "Starting lineups are not yet confirmed or cannot be confirmed from the free data source.",
        "injuries": "Injuries",
        "recent_plays": "Recent Key Plays",
        "hotspots": "Hotspots",
        "key_players": "Key Players",
        "status": "Status",
        "latest": "today",
        "none": "None",
        "filter_team": "Target Team",
        "clock": "Game Clock",
        "team_stats": "Team Stats",
        "data_note": "Hotspots are derived only from structured game facts.",
        "counts_summary": "Game Counts",
        "advanced_section": "Advanced Analysis",
        "analysis_summary": "Analysis Summary",
        "analysis_reasons": "Key Reasons",
        "analysis_trend": "Direction",
        "analysis_turning_point": "Turning Point",
        "analysis_key_matchup": "Key Matchup",
        "analysis_deep_note": "Advanced analysis is derived from structured game and team data, not betting advice.",
    },
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Return NBA daily status for the requestor's local date.")
    parser.add_argument("--tz", help="IANA timezone, UTC offset, or city hint")
    parser.add_argument("--date", help="Requested local date in YYYY-MM-DD; defaults to today in requestor timezone")
    parser.add_argument("--team", help="Optional team abbreviation or alias")
    parser.add_argument("--view", default="day", choices=("day", "game"), help="Render daily overview or a single game")
    parser.add_argument("--lang", default="zh", choices=("zh", "en"), help="Response language")
    parser.add_argument("--format", default="markdown", choices=("markdown", "json"), help="Output format")
    parser.add_argument("--base-url", help="Override ESPN base URL for testing")
    return parser.parse_args(argv)


def validate_args(args: argparse.Namespace) -> None:
    if args.date:
        try:
            datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError as exc:
            raise NBAReportError("date 参数格式不合法，必须为 YYYY-MM-DD", kind="invalid_arguments") from exc


def parse_iso_datetime(value: str) -> datetime:
    normalized = (value or "").strip().replace("Z", "+00:00")
    if not normalized:
        raise NBAReportError("比赛时间字段缺失。", kind="invalid_data")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def format_local_datetime(value: datetime, tz: ResolvedTimezone) -> str:
    return value.astimezone(tz.tzinfo).strftime("%Y-%m-%d %H:%M %Z")


def localize_status_detail(status_state: str, status_detail: str, labels: dict[str, str]) -> str:
    if status_state == "pre":
        return labels["status_pre"]
    if status_state == "in":
        return status_detail or labels["status_live"]
    if status_state == "post":
        return status_detail or labels["status_final"]
    return status_detail or labels["status_pre"]


def build_game_counts(games: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"total": len(games), "pre": 0, "in": 0, "post": 0}
    for game in games:
        state = game.get("statusState")
        if state in counts:
            counts[state] += 1
    return counts


def format_counts_summary(counts: dict[str, int], labels: dict[str, str]) -> str:
    if labels["timezone"] == "请求方时区":
        return (
            f"{labels['counts_summary']}: 共 {counts['total']} 场 / "
            f"{labels['status_pre']} {counts['pre']} / "
            f"{labels['status_live']} {counts['in']} / "
            f"{labels['status_final']} {counts['post']}"
        )
    return (
        f"{labels['counts_summary']}: {counts['total']} total / "
        f"{labels['status_pre']} {counts['pre']} / "
        f"{labels['status_live']} {counts['in']} / "
        f"{labels['status_final']} {counts['post']}"
    )


def record_summary(competitor: dict[str, Any]) -> str | None:
    records = competitor.get("records") or []
    if records:
        summary = records[0].get("summary")
        if summary:
            return str(summary)
    return None


def parse_linescores(competitor: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for item in competitor.get("linescores") or []:
        value = item.get("displayValue") or item.get("value")
        if value is not None:
            values.append(str(value))
    return values


def extract_summary_leaders(summary: dict[str, Any]) -> dict[str, list[str]]:
    by_team: dict[str, list[str]] = {}
    for entry in summary.get("leaders") or []:
        team = entry.get("team") or {}
        abbr = canonicalize_team_abbr(team.get("abbreviation"))
        if not abbr:
            continue
        lines: list[str] = []
        for leader in entry.get("leaders") or []:
            athlete = leader.get("leaders", [{}])[0].get("athlete", {})
            athlete_name = athlete.get("displayName") or athlete.get("shortName")
            display_value = leader.get("leaders", [{}])[0].get("displayValue")
            if athlete_name and display_value:
                lines.append(f"{athlete_name} ({display_value})")
        if lines:
            by_team[str(abbr)] = lines[:3]
    return by_team


def extract_injuries(summary: dict[str, Any]) -> dict[str, list[str]]:
    by_team: dict[str, list[str]] = defaultdict(list)
    for entry in summary.get("injuries") or []:
        team = entry.get("team") or {}
        abbr = canonicalize_team_abbr(team.get("abbreviation"))
        if not abbr:
            continue
        for injury in entry.get("injuries") or []:
            athlete = injury.get("athlete") or {}
            name = athlete.get("displayName") or athlete.get("shortName")
            status = injury.get("status") or injury.get("type") or {}
            status_text = status.get("description") if isinstance(status, dict) else status
            detail = injury.get("detail") or injury.get("description")
            parts = [part for part in (name, status_text, detail) if part]
            if parts:
                by_team[str(abbr)].append(" - ".join(str(part) for part in parts))
    return dict(by_team)


def extract_starters_and_players(summary: dict[str, Any]) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    starters: dict[str, list[str]] = {}
    key_players: dict[str, list[str]] = {}
    boxscore = summary.get("boxscore") or {}
    for team_group in boxscore.get("players") or []:
        team = team_group.get("team") or {}
        abbr = canonicalize_team_abbr(team.get("abbreviation"))
        if not abbr:
            continue
        team_starters: list[str] = []
        spotlights: list[str] = []
        for stat_group in team_group.get("statistics") or []:
            keys = stat_group.get("keys") or []
            for athlete_entry in stat_group.get("athletes") or []:
                athlete = athlete_entry.get("athlete") or {}
                name = athlete.get("displayName") or athlete.get("shortName")
                if not name:
                    continue
                if athlete_entry.get("starter"):
                    team_starters.append(str(name))
                stats = athlete_entry.get("stats") or []
                if not stats or not keys:
                    continue
                stat_map = {key: stats[index] for index, key in enumerate(keys) if index < len(stats)}
                points = stat_map.get("points")
                rebounds = stat_map.get("rebounds")
                assists = stat_map.get("assists")
                summary_parts = [name]
                if points is not None:
                    summary_parts.append(f"{points} PTS")
                if rebounds is not None:
                    summary_parts.append(f"{rebounds} REB")
                if assists is not None:
                    summary_parts.append(f"{assists} AST")
                if len(summary_parts) > 1:
                    spotlights.append(" | ".join(summary_parts))
            if team_starters or spotlights:
                break
        starters[str(abbr)] = team_starters[:5]
        key_players[str(abbr)] = spotlights[:5]
    return starters, key_players


def extract_recent_plays(summary: dict[str, Any], limit: int = 4) -> list[str]:
    recent: list[str] = []
    for play in (summary.get("plays") or [])[-limit:]:
        text = play.get("text")
        period = play.get("period", {}).get("displayValue") or play.get("period", {}).get("number")
        clock = play.get("clock", {}).get("displayValue")
        if text:
            prefix = " ".join(part for part in (f"P{period}" if period else "", clock or "") if part).strip()
            recent.append(f"{prefix} {text}".strip())
    return recent


def extract_headlines(event: dict[str, Any], summary: dict[str, Any]) -> list[str]:
    headlines: list[str] = []
    competition = (event.get("competitions") or [{}])[0]
    for item in competition.get("headlines") or []:
        headline = item.get("shortLinkText") or item.get("description") or item.get("text")
        if headline:
            headlines.append(str(headline))
    news = summary.get("news") or []
    if isinstance(news, dict):
        for item in news.get("articles") or []:
            if isinstance(item, dict) and item.get("headline"):
                headlines.append(str(item["headline"]))
    elif isinstance(news, list):
        for item in news:
            if isinstance(item, dict) and item.get("headline"):
                headlines.append(str(item["headline"]))
            elif isinstance(item, str) and item.strip():
                headlines.append(item.strip())
    deduped: list[str] = []
    seen: set[str] = set()
    for headline in headlines:
        key = headline.casefold()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(headline)
    return deduped[:3]


def extract_team_stats(summary: dict[str, Any]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    boxscore = summary.get("boxscore") or {}
    for entry in boxscore.get("teams") or []:
        team = entry.get("team") or {}
        abbr = canonicalize_team_abbr(team.get("abbreviation"))
        if not abbr:
            continue
        stats: list[str] = []
        for stat in entry.get("statistics") or []:
            label = stat.get("label") or stat.get("abbreviation")
            value = stat.get("displayValue")
            if label and value:
                stats.append(f"{label}: {value}")
        result[str(abbr)] = stats[:6]
    return result


def safe_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_int(value: Any) -> int | None:
    parsed = safe_float(value)
    if parsed is None:
        return None
    return int(parsed)


def extract_predictor(summary: dict[str, Any]) -> dict[str, Any] | None:
    predictor = summary.get("predictor")
    if not isinstance(predictor, dict):
        return None
    home_team = predictor.get("homeTeam") or {}
    away_team = predictor.get("awayTeam") or {}
    home_projection = safe_float(home_team.get("gameProjection"))
    away_projection = safe_float(away_team.get("gameProjection"))
    if home_projection is None and away_projection is None:
        return None
    return {
        "header": predictor.get("header") or "",
        "homeTeamId": str(home_team.get("id") or ""),
        "awayTeamId": str(away_team.get("id") or ""),
        "homeProjection": home_projection,
        "awayProjection": away_projection,
    }


def extract_pickcenter(summary: dict[str, Any]) -> dict[str, Any] | None:
    pickcenter_entries = summary.get("pickcenter") or []
    if not pickcenter_entries:
        return None
    entry = pickcenter_entries[0]
    if not isinstance(entry, dict):
        return None
    return {
        "provider": ((entry.get("provider") or {}).get("name")) or "",
        "details": entry.get("details") or "",
        "spread": safe_float(entry.get("spread")),
        "overUnder": safe_float(entry.get("overUnder")),
        "homeMoneyLine": safe_int((((entry.get("homeTeamOdds") or {}).get("moneyLine")))),
        "awayMoneyLine": safe_int((((entry.get("awayTeamOdds") or {}).get("moneyLine")))),
    }


def extract_article(summary: dict[str, Any]) -> dict[str, str] | None:
    article = summary.get("article")
    if not isinstance(article, dict):
        return None
    headline = article.get("headline") or article.get("title")
    if not headline:
        return None
    return {
        "type": str(article.get("type") or ""),
        "headline": str(headline),
        "description": str(article.get("description") or ""),
        "source": str(article.get("source") or ""),
    }


def extract_standings_snapshot(summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    snapshots: dict[str, dict[str, Any]] = {}
    standings = summary.get("standings") or {}
    groups = standings.get("groups") or []
    for group in groups:
        entries = ((group.get("standings") or {}).get("entries")) or []
        for index, entry in enumerate(entries, start=1):
            team_id = str(entry.get("id") or "")
            if not team_id:
                continue
            stats = {stat.get("name"): stat.get("displayValue") for stat in entry.get("stats") or [] if stat.get("name")}
            snapshots[team_id] = {
                "rank": index,
                "team": entry.get("team") or "",
                "wins": stats.get("wins"),
                "losses": stats.get("losses"),
                "winPercent": stats.get("winPercent"),
                "gamesBehind": stats.get("gamesBehind"),
                "streak": stats.get("streak"),
            }
    return snapshots


def extract_last_five_snapshot(summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for entry in summary.get("lastFiveGames") or []:
        team = entry.get("team") or {}
        team_id = str(team.get("id") or "")
        abbr = canonicalize_team_abbr(team.get("abbreviation"))
        events = entry.get("events") or []
        wins = 0
        losses = 0
        recent_scores: list[str] = []
        for event in events[:5]:
            winner = str(event.get("winner") or "").lower() == "true"
            if winner:
                wins += 1
            else:
                losses += 1
            if event.get("score"):
                recent_scores.append(str(event["score"]))
        if team_id:
            result[team_id] = {
                "abbr": abbr,
                "record": f"{wins}-{losses}",
                "wins": wins,
                "losses": losses,
                "scores": recent_scores[:5],
            }
    return result


def flatten_team_statistics_payload(payload: dict[str, Any]) -> dict[str, str]:
    results = ((payload.get("results") or {}).get("stats") or {}).get("categories") or []
    flattened: dict[str, str] = {}
    for category in results:
        for stat in category.get("stats") or []:
            name = stat.get("name")
            display_value = stat.get("displayValue")
            if name and display_value is not None:
                flattened[str(name)] = str(display_value)
    return flattened


def extract_schedule_context(schedule_payload: dict[str, Any], event_id: str, start_time_utc: datetime) -> dict[str, Any]:
    events = schedule_payload.get("events") or []
    parsed_events: list[tuple[datetime, dict[str, Any]]] = []
    for event in events:
        try:
            parsed_events.append((parse_iso_datetime(event.get("date")), event))
        except NBAReportError:
            continue
    parsed_events.sort(key=lambda item: item[0])

    previous_event: dict[str, Any] | None = None
    next_event: dict[str, Any] | None = None
    for event_time, event in parsed_events:
        if str(event.get("id")) == event_id:
            continue
        if event_time < start_time_utc:
            previous_event = event
        elif event_time > start_time_utc and next_event is None:
            next_event = event

    def summarize_event(event: dict[str, Any] | None) -> dict[str, Any] | None:
        if not event:
            return None
        competition = (event.get("competitions") or [{}])[0]
        status = (competition.get("status") or {}).get("type") or {}
        return {
            "eventId": str(event.get("id") or ""),
            "shortName": str(event.get("shortName") or ""),
            "date": str(event.get("date") or ""),
            "status": str(status.get("state") or ""),
            "detail": str(status.get("detail") or status.get("description") or ""),
        }

    context: dict[str, Any] = {
        "previousGame": summarize_event(previous_event),
        "nextGame": summarize_event(next_event),
        "restDays": None,
        "isBackToBack": False,
    }
    if previous_event and previous_event.get("date"):
        previous_date = parse_iso_datetime(previous_event.get("date")).date()
        current_date = start_time_utc.date()
        rest_days = max((current_date - previous_date).days - 1, 0)
        context["restDays"] = rest_days
        context["isBackToBack"] = rest_days == 0
    return context


def extract_play_timeline(summary: dict[str, Any], limit: int = 600) -> list[dict[str, Any]]:
    timeline: list[dict[str, Any]] = []
    plays = summary.get("plays") or []
    for play in plays[-limit:]:
        timeline.append(
            {
                "id": str(play.get("id") or ""),
                "text": str(play.get("text") or ""),
                "shortDescription": str(play.get("shortDescription") or ""),
                "period": safe_int(((play.get("period") or {}).get("number"))),
                "clock": str(((play.get("clock") or {}).get("displayValue")) or ""),
                "homeScore": safe_int(play.get("homeScore")),
                "awayScore": safe_int(play.get("awayScore")),
                "scoreValue": safe_int(play.get("scoreValue")),
                "scoringPlay": bool(play.get("scoringPlay")),
                "teamId": str(((play.get("team") or {}).get("id")) or ""),
            }
        )
    return timeline


def extract_win_probability(summary: dict[str, Any], limit: int = 600) -> list[dict[str, Any]]:
    timeline: list[dict[str, Any]] = []
    entries = summary.get("winprobability") or []
    for entry in entries[-limit:]:
        timeline.append(
            {
                "playId": str(entry.get("playId") or ""),
                "homeWinPercentage": safe_float(entry.get("homeWinPercentage")),
                "tiePercentage": safe_float(entry.get("tiePercentage")),
            }
        )
    return timeline


def build_hotspots(game: dict[str, Any], labels: dict[str, str]) -> list[str]:
    hotspots: list[str] = []
    if game["statusState"] == "post":
        leaders = game["leaders"]
        for team_abbr in (game["away"]["abbr"], game["home"]["abbr"]):
            if leaders.get(team_abbr):
                hotspots.append(f"{team_abbr}: {leaders[team_abbr][0]}")
        if game["headlines"]:
            hotspots.append(game["headlines"][0])
    elif game["statusState"] == "in":
        if game["recentPlays"]:
            hotspots.append(game["recentPlays"][-1])
        leaders = game["leaders"]
        home_abbr = game["home"]["abbr"]
        away_abbr = game["away"]["abbr"]
        if leaders.get(home_abbr):
            hotspots.append(f"{home_abbr}: {leaders[home_abbr][0]}")
        if leaders.get(away_abbr):
            hotspots.append(f"{away_abbr}: {leaders[away_abbr][0]}")
    else:
        if game["startersConfirmed"]:
            hotspots.append(
                f"{labels['starters']}: "
                f"{game['away']['abbr']} {', '.join(game['starters'].get(game['away']['abbr']) or [])} / "
                f"{game['home']['abbr']} {', '.join(game['starters'].get(game['home']['abbr']) or [])}"
            )
        elif game["injuries"].get(game["away"]["abbr"]) or game["injuries"].get(game["home"]["abbr"]):
            away_injuries = game["injuries"].get(game["away"]["abbr"]) or []
            home_injuries = game["injuries"].get(game["home"]["abbr"]) or []
            first_injury = (away_injuries + home_injuries)[0] if (away_injuries or home_injuries) else None
            if first_injury:
                hotspots.append(first_injury)
    return hotspots[:3]


def enrich_game(
    event: dict[str, Any],
    summary: dict[str, Any],
    resolved_tz: ResolvedTimezone,
    labels: dict[str, str],
    team_statistics: dict[str, dict[str, str]],
    team_schedule_context: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    competition = (event.get("competitions") or [{}])[0]
    competitors = competition.get("competitors") or []
    home = next((item for item in competitors if item.get("homeAway") == "home"), {})
    away = next((item for item in competitors if item.get("homeAway") == "away"), {})
    status = competition.get("status") or event.get("status") or {}
    status_type = status.get("type") or {}
    start_time_utc = parse_iso_datetime(competition.get("date") or event.get("date"))
    leaders = extract_summary_leaders(summary)
    injuries = extract_injuries(summary)
    starters, key_players = extract_starters_and_players(summary)
    team_stats = extract_team_stats(summary)
    standings = extract_standings_snapshot(summary)
    last_five_games = extract_last_five_snapshot(summary)
    home_team_id = str((home.get("team") or {}).get("id") or "")
    away_team_id = str((away.get("team") or {}).get("id") or "")
    raw_status_detail = status_type.get("detail") or status_type.get("description") or ""
    status_state = status_type.get("state") or "pre"
    game = {
        "eventId": str(event.get("id")),
        "shortName": event.get("shortName") or "",
        "statusState": status_state,
        "statusDetail": localize_status_detail(status_state, raw_status_detail, labels),
        "displayStatusLocal": localize_status_detail(status_state, raw_status_detail, labels),
        "rawStatusDetail": raw_status_detail,
        "displayClock": status.get("displayClock") or "",
        "period": status.get("period"),
        "startTimeUtc": start_time_utc.isoformat(),
        "startTimeLocal": format_local_datetime(start_time_utc, resolved_tz),
        "startLocalDate": start_time_utc.astimezone(resolved_tz.tzinfo).date().isoformat(),
        "venue": (((summary.get("gameInfo") or {}).get("venue") or {}).get("fullName")) or (((competition.get("venue") or {}).get("fullName"))),
        "broadcasts": [item.get("names", [None])[0] or item.get("market") for item in competition.get("broadcasts") or [] if item],
        "away": {
            "id": away_team_id,
            "abbr": canonicalize_team_abbr((away.get("team") or {}).get("abbreviation")),
            "displayName": ((away.get("team") or {}).get("displayName")) or "",
            "score": away.get("score"),
            "record": record_summary(away),
            "linescores": parse_linescores(away),
        },
        "home": {
            "id": home_team_id,
            "abbr": canonicalize_team_abbr((home.get("team") or {}).get("abbreviation")),
            "displayName": ((home.get("team") or {}).get("displayName")) or "",
            "score": home.get("score"),
            "record": record_summary(home),
            "linescores": parse_linescores(home),
        },
        "leaders": leaders,
        "injuries": injuries,
        "starters": starters,
        "keyPlayers": key_players,
        "recentPlays": extract_recent_plays(summary),
        "headlines": extract_headlines(event, summary),
        "teamStats": team_stats,
        "predictor": extract_predictor(summary),
        "pickcenter": extract_pickcenter(summary),
        "standings": standings,
        "lastFiveGames": last_five_games,
        "seasonSeries": summary.get("seasonseries") or [],
        "article": extract_article(summary),
        "teamSeasonStats": {
            canonicalize_team_abbr((away.get("team") or {}).get("abbreviation")): team_statistics.get(away_team_id) or {},
            canonicalize_team_abbr((home.get("team") or {}).get("abbreviation")): team_statistics.get(home_team_id) or {},
        },
        "teamScheduleContext": {
            canonicalize_team_abbr((away.get("team") or {}).get("abbreviation")): team_schedule_context.get(away_team_id) or {},
            canonicalize_team_abbr((home.get("team") or {}).get("abbreviation")): team_schedule_context.get(home_team_id) or {},
        },
        "playTimeline": extract_play_timeline(summary),
        "winProbabilityTimeline": extract_win_probability(summary),
        "analysisSignals": {},
        "analysisSummary": {},
    }
    game["startersConfirmed"] = bool(game["starters"].get(game["away"]["abbr"])) and bool(game["starters"].get(game["home"]["abbr"]))
    game["hotspots"] = build_hotspots(game, labels)
    return game


def load_candidate_events(target_date: date, resolved_tz: ResolvedTimezone, base_url: str | None) -> list[dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}
    for offset in (-1, 0, 1):
        provider_date = (target_date + timedelta(days=offset)).strftime("%Y%m%d")
        payload = fetch_scoreboard(provider_date, base_url=base_url)["data"]
        for event in payload.get("events") or []:
            event_id = str(event.get("id"))
            if not event_id:
                continue
            competition = (event.get("competitions") or [{}])[0]
            start_time_utc = parse_iso_datetime(competition.get("date") or event.get("date"))
            local_date = start_time_utc.astimezone(resolved_tz.tzinfo).date()
            if local_date == target_date:
                candidates[event_id] = event
    return list(candidates.values())


def build_report_payload(args: argparse.Namespace) -> dict[str, Any]:
    labels = I18N[args.lang]
    resolved_tz = resolve_timezone(args.tz)
    target_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else datetime.now(resolved_tz.tzinfo).date()
    team_filter = normalize_team_input(args.team)
    target_view = "game" if team_filter else args.view
    events = load_candidate_events(target_date, resolved_tz, args.base_url)
    games: list[dict[str, Any]] = []
    team_statistics_cache: dict[str, dict[str, str]] = {}
    team_schedule_cache: dict[str, dict[str, Any]] = {}
    for event in events:
        event_id = str(event.get("id"))
        summary_payload = fetch_summary(event_id, base_url=args.base_url)["data"]
        if target_view == "game":
            competition = (event.get("competitions") or [{}])[0]
            start_time_utc = parse_iso_datetime(competition.get("date") or event.get("date"))
            for competitor in competition.get("competitors") or []:
                team = competitor.get("team") or {}
                team_id = str(team.get("id") or "")
                if not team_id:
                    continue
                if team_id not in team_statistics_cache:
                    try:
                        team_statistics_cache[team_id] = flatten_team_statistics_payload(
                            fetch_team_statistics(team_id, base_url=args.base_url)["data"]
                        )
                    except NBAReportError:
                        team_statistics_cache[team_id] = {}
                if team_id not in team_schedule_cache:
                    try:
                        team_schedule_cache[team_id] = extract_schedule_context(
                            fetch_team_schedule(team_id, base_url=args.base_url)["data"],
                            event_id,
                            start_time_utc,
                        )
                    except NBAReportError:
                        team_schedule_cache[team_id] = {}
        games.append(enrich_game(event, summary_payload, resolved_tz, labels, team_statistics_cache, team_schedule_cache))

    games.sort(key=lambda item: item["startTimeUtc"])
    if team_filter:
        games = [game for game in games if team_filter in {game["home"]["abbr"], game["away"]["abbr"]}]

    view = target_view
    if view == "game":
        if not games:
            raise NBAReportError("当前条件下未找到对应比赛。", kind="not_found")
        if len(games) > 1 and not team_filter:
            raise NBAReportError("单场视图需要指定球队，否则当天存在多场比赛。", kind="invalid_arguments")
        games = [games[0]]

    game_counts = build_game_counts(games)

    return {
        "timezone": resolved_tz.name,
        "timezoneSource": resolved_tz.source,
        "requestedDate": target_date.isoformat(),
        "view": view,
        "lang": args.lang,
        "teamFilter": team_filter,
        "games": games,
        "gameCounts": game_counts,
        "labels": labels,
    }


def render_team_lines(game: dict[str, Any], labels: dict[str, str]) -> list[str]:
    away = game["away"]
    home = game["home"]
    lines = [
        f"### {away['abbr']} {away['score'] or ''} @ {home['abbr']} {home['score'] or ''}".replace("  ", " ").strip(),
        f"- {labels['status']}: {game.get('displayStatusLocal') or game['statusDetail']}",
        f"- {labels['start_time']}: {game['startTimeLocal']}",
    ]
    if game["statusState"] == "in" and game.get("displayClock"):
        lines.append(f"- {labels['clock']}: Q{game.get('period') or '?'} {game['displayClock']}")
    if game.get("venue"):
        lines.append(f"- {labels['venue']}: {game['venue']}")
    if game.get("broadcasts"):
        lines.append(f"- {labels['broadcasts']}: {', '.join([item for item in game['broadcasts'] if item])}")
    lines.append(
        f"- {labels['records']}: {away['abbr']} {away.get('record') or labels['none']} / "
        f"{home['abbr']} {home.get('record') or labels['none']}"
    )
    if away.get("linescores") or home.get("linescores"):
        lines.append(
            f"- {labels['score_by_period']}: "
            f"{away['abbr']} {'-'.join(away.get('linescores') or []) or labels['none']} / "
            f"{home['abbr']} {'-'.join(home.get('linescores') or []) or labels['none']}"
        )
    if game["startersConfirmed"]:
        lines.append(
            f"- {labels['starters']}: "
            f"{away['abbr']} {', '.join(game['starters'].get(away['abbr']) or [])} / "
            f"{home['abbr']} {', '.join(game['starters'].get(home['abbr']) or [])}"
        )
    elif game["statusState"] == "pre":
        lines.append(f"- {labels['starters']}: {labels['lineup_unconfirmed']}")
    return lines


def render_detail_blocks(game: dict[str, Any], labels: dict[str, str]) -> list[str]:
    lines: list[str] = []
    if game["leaders"]:
        lines.append(f"#### {labels['leaders']}")
        for abbr in (game["away"]["abbr"], game["home"]["abbr"]):
            lines.append(f"- {abbr}: {', '.join(game['leaders'].get(abbr) or [labels['none']])}")
        lines.append("")
    if game["keyPlayers"]:
        lines.append(f"#### {labels['key_players']}")
        for abbr in (game["away"]["abbr"], game["home"]["abbr"]):
            if game["keyPlayers"].get(abbr):
                lines.append(f"- {abbr}: {', '.join(game['keyPlayers'][abbr][:3])}")
        lines.append("")
    if game["teamStats"]:
        lines.append(f"#### {labels['team_stats']}")
        for abbr in (game["away"]["abbr"], game["home"]["abbr"]):
            if game["teamStats"].get(abbr):
                lines.append(f"- {abbr}: {', '.join(game['teamStats'][abbr][:4])}")
        lines.append("")
    if game["injuries"]:
        lines.append(f"#### {labels['injuries']}")
        for abbr in (game["away"]["abbr"], game["home"]["abbr"]):
            if game["injuries"].get(abbr):
                lines.append(f"- {abbr}: {'; '.join(game['injuries'][abbr][:4])}")
        lines.append("")
    if game["recentPlays"] and game["statusState"] == "in":
        lines.append(f"#### {labels['recent_plays']}")
        for item in game["recentPlays"]:
            lines.append(f"- {item}")
        lines.append("")
    if game["hotspots"]:
        lines.append(f"#### {labels['hotspots']}")
        for item in game["hotspots"]:
            lines.append(f"- {item}")
        lines.append("")
    return lines


def render_markdown(report: dict[str, Any]) -> str:
    labels = report["labels"]
    games = report["games"]
    game_counts = report["gameCounts"]
    title = labels["title_game"] if report["view"] == "game" else labels["title_day"]
    lines = [
        f"# {title} ({report['requestedDate']})",
        f"> {labels['timezone']}: {report['timezone']}",
        f"> {labels['requested_date']}: {report['requestedDate']}",
        f"> {labels['view']}: {report['view']}",
    ]
    if report.get("teamFilter"):
        lines.append(f"> {labels['filter_team']}: {report['teamFilter']}")
    if report["view"] == "day":
        lines.append(f"> {format_counts_summary(game_counts, labels)}")
    lines.extend(["", labels["local_tip"], ""])

    if not games:
        lines.append(f"- {labels['no_games']}")
        return "\n".join(lines)

    if report["view"] == "game":
        game = games[0]
        lines.extend(render_team_lines(game, labels))
        lines.append("")
        lines.extend(render_detail_blocks(game, labels))
        lines.append(labels["data_note"])
        return "\n".join(lines)

    grouped: dict[str, list[dict[str, Any]]] = {"post": [], "in": [], "pre": []}
    for game in games:
        grouped[game["statusState"]].append(game)

    for state, heading in (("in", labels["live_section"]), ("post", labels["final_section"]), ("pre", labels["pre_section"])):
        section_games = grouped.get(state) or []
        if not section_games:
            continue
        lines.extend([f"## {heading}", ""])
        for game in section_games:
            lines.extend(render_team_lines(game, labels))
            if game["hotspots"]:
                hotspot = " / ".join(game["hotspots"])
                lines.append(f"- {labels['hotspots']}: {hotspot}")
            lines.append("")
    lines.append(labels["data_note"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        validate_args(args)
        report = build_report_payload(args)
        payload = report if args.format == "json" else render_markdown(report)
        if args.format == "json":
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(payload)
        return 0
    except NBAReportError as exc:
        print(f"[{exc.kind}] {exc}", file=sys.stderr)
        return 2 if exc.kind == "invalid_arguments" else 1


if __name__ == "__main__":
    sys.exit(main())
