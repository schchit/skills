#!/usr/bin/env python3
"""Shared context builders for scene-specific NBA_TR scripts."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta
from typing import Any

from entity_guard import blocked_names, fallback_matchup_text, filter_headlines, filter_named_lines, verified_player_names
from nba_advanced_report import build_analysis, render_analysis_block
from nba_common import NBAReportError
from nba_play_digest import build_play_digest
from nba_teams import extract_team_from_text, normalize_team_input, provider_team_id
from nba_today_report import build_report_payload, render_detail_blocks, render_markdown as render_day_markdown, render_team_lines
from provider_espn import extract_roster_players as extract_espn_roster_players
from provider_espn import fetch_scoreboard, fetch_team_roster, fetch_team_schedule
from provider_nba import (
    extract_boxscore_players,
    extract_play_actions,
    extract_roster_players as extract_nba_roster_players,
    extract_scoreboard_games,
    find_game_id_by_matchup,
    fetch_live_boxscore,
    fetch_play_by_play,
    fetch_scoreboard as fetch_nba_scoreboard,
    fetch_team_roster as fetch_nba_team_roster,
)
from timezone_resolver import extract_timezone_hint, resolve_timezone

LANG_EN_PATTERNS = [r"\bin english\b", r"\benglish\b", r"\blang\s*=\s*en\b", r"\ben\b", r"\b英文\b"]
LANG_ZH_PATTERNS = [r"\bin chinese\b", r"\bchinese\b", r"\blang\s*=\s*zh\b", r"\bzh\b", r"\b中文\b"]
DATE_PATTERN = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
PREGAME_PATTERNS = [r"预测", r"看法", r"前瞻", r"\bpreview\b", r"\bpredict(?:ion)?\b", r"\banaly[sz]e\b"]
LIVE_PATTERNS = [r"赛中", r"正在进行", r"走势", r"实时", r"\blive\b", r"\bin-game\b", r"\bmomentum\b"]
POST_PATTERNS = [r"复盘", r"回顾", r"赛后", r"\brecap\b", r"\bpostgame\b", r"\breview\b"]


def contains_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def detect_lang(command: str) -> str:
    lowered = command.strip()
    if contains_any(lowered, LANG_EN_PATTERNS):
        return "en"
    if contains_any(lowered, LANG_ZH_PATTERNS):
        return "zh"
    zh_chars = len(re.findall(r"[\u4e00-\u9fff]", lowered))
    en_words = len(re.findall(r"\b[a-zA-Z][a-zA-Z'-]*\b", lowered))
    return "zh" if zh_chars > en_words else "en"


def detect_analysis_mode(command: str) -> str:
    lowered = command.strip()
    if contains_any(lowered, PREGAME_PATTERNS):
        return "pregame"
    if contains_any(lowered, LIVE_PATTERNS):
        return "live"
    if contains_any(lowered, POST_PATTERNS):
        return "post"
    return "auto"


def command_options(command: str) -> dict[str, str | None]:
    date_match = DATE_PATTERN.search(command)
    timezone_hint = extract_timezone_hint(command)
    return {
        "lang": detect_lang(command),
        "analysis_mode": detect_analysis_mode(command),
        "date": date_match.group(1) if date_match else None,
        "team": extract_team_from_text(command),
        "tz": timezone_hint.name if timezone_hint else None,
    }


def _report_args(*, tz: str | None, date_text: str | None, team: str | None, lang: str) -> argparse.Namespace:
    return argparse.Namespace(
        tz=tz,
        date=date_text,
        team=team,
        view="game" if team else "day",
        lang=lang,
        format="json",
        base_url=None,
    )


def build_scene_report(*, tz: str | None, date_text: str | None, team: str | None, lang: str) -> dict[str, Any]:
    return build_report_payload(_report_args(tz=tz, date_text=date_text, team=team, lang=lang))


def _target_date(date_text: str | None, tz: str | None) -> datetime.date:
    resolved_tz = resolve_timezone(tz)
    if date_text:
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    return datetime.now(resolved_tz.tzinfo).date()


def locate_game(*, tz: str | None, date_text: str | None, team: str, base_url: str | None = None) -> dict[str, Any]:
    team_abbr = normalize_team_input(team)
    if not team_abbr:
        raise NBAReportError("未能识别球队缩写。", kind="invalid_arguments")

    target_date = _target_date(date_text, tz)
    resolved_tz = resolve_timezone(tz)
    for offset in (-1, 0, 1):
        provider_date = (target_date + timedelta(days=offset)).strftime("%Y%m%d")
        try:
            payload = fetch_scoreboard(provider_date, base_url=base_url)["data"]
        except NBAReportError:
            payload = {}
        for event in payload.get("events") or []:
            competition = (event.get("competitions") or [{}])[0]
            event_date = competition.get("date") or event.get("date")
            if not event_date:
                continue
            local_date = datetime.fromisoformat(event_date.replace("Z", "+00:00")).astimezone(resolved_tz.tzinfo).date()
            if local_date != target_date:
                continue
            competitors = competition.get("competitors") or []
            abbrs = {str(((item.get("team") or {}).get("abbreviation")) or "").upper() for item in competitors}
            if team_abbr in abbrs:
                return {
                    "eventId": str(event.get("id") or ""),
                    "source": "espn_scoreboard",
                    "event": event,
                }

    espn_team_id = provider_team_id(team_abbr, "espn")
    if espn_team_id:
        try:
            schedule_payload = fetch_team_schedule(espn_team_id, base_url=base_url)["data"]
            for event in schedule_payload.get("events") or []:
                raw_date = str(event.get("date") or "")
                if raw_date:
                    local_date = datetime.fromisoformat(raw_date.replace("Z", "+00:00")).astimezone(resolved_tz.tzinfo).date()
                    if local_date == target_date:
                        return {
                            "eventId": str(event.get("id") or ""),
                            "source": "espn_team_schedule",
                            "event": event,
                        }
        except NBAReportError:
            pass

    try:
        nba_payload = fetch_nba_scoreboard(target_date.isoformat())["data"]
        for game in extract_scoreboard_games(nba_payload):
            if team_abbr in {game.get("awayAbbr"), game.get("homeAbbr")}:
                return {
                    "eventId": str(game.get("gameId") or ""),
                    "source": "nba_scoreboard",
                    "event": game,
                }
    except NBAReportError:
        pass

    raise NBAReportError("当前条件下未找到对应比赛。", kind="not_found")


def fetch_team_roster_snapshot(team_abbr: str) -> dict[str, Any]:
    espn_team_id = provider_team_id(team_abbr, "espn")
    nba_team_id = provider_team_id(team_abbr, "nba")
    if espn_team_id:
        try:
            payload = fetch_team_roster(espn_team_id)
            players = extract_espn_roster_players(payload["data"])
            if players:
                return {
                    "team": team_abbr,
                    "players": players,
                    "source": "espn",
                    "dataFreshness": payload.get("dataFreshness", "fresh"),
                }
        except NBAReportError:
            pass
    if nba_team_id:
        try:
            payload = fetch_nba_team_roster(nba_team_id)
            players = extract_nba_roster_players(payload["data"])
            return {
                "team": team_abbr,
                "players": players,
                "source": "nba",
                "dataFreshness": payload.get("dataFreshness", "fresh"),
            }
        except NBAReportError:
            pass
    return {
        "team": team_abbr,
        "players": [],
        "source": "unavailable",
        "dataFreshness": "fresh",
    }


def fetch_game_rosters(game: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        game["away"]["abbr"]: fetch_team_roster_snapshot(game["away"]["abbr"]),
        game["home"]["abbr"]: fetch_team_roster_snapshot(game["home"]["abbr"]),
    }


def apply_roster_guard(game: dict[str, Any], roster_snapshots: dict[str, dict[str, Any]], *, lang: str) -> dict[str, Any]:
    rosters_by_abbr = {abbr: snapshot.get("players") or [] for abbr, snapshot in roster_snapshots.items()}
    allowed_names = verified_player_names(game, rosters_by_abbr)
    original_candidate_lines: list[str] = []
    for group in (game.get("leaders") or {}, game.get("starters") or {}, game.get("keyPlayers") or {}):
        for lines in group.values():
            original_candidate_lines.extend(lines or [])
    blocked = blocked_names(original_candidate_lines, allowed_names)

    game["leaders"] = {
        abbr: filter_named_lines(lines or [], allowed_names)
        for abbr, lines in (game.get("leaders") or {}).items()
    }
    game["starters"] = {
        abbr: filter_named_lines(lines or [], allowed_names)
        for abbr, lines in (game.get("starters") or {}).items()
    }
    game["keyPlayers"] = {
        abbr: filter_named_lines(lines or [], allowed_names)
        for abbr, lines in (game.get("keyPlayers") or {}).items()
    }
    game["headlines"] = filter_headlines(game.get("headlines") or [], blocked)
    game["startersConfirmed"] = bool(game["starters"].get(game["away"]["abbr"])) and bool(game["starters"].get(game["home"]["abbr"]))
    game["verifiedPlayers"] = sorted(allowed_names)
    game["rosters"] = roster_snapshots
    if blocked:
        game["forceFallbackMatchup"] = True
    if blocked or not any(game["leaders"].values()):
        game["fallbackMatchup"] = fallback_matchup_text(game, lang=lang)
    return game


def _player_line_from_boxscore(player: dict[str, Any]) -> str:
    name = player.get("displayName") or ""
    stats = player.get("stats") or {}
    parts = [name]
    if stats.get("points") is not None:
        parts.append(f"{stats['points']} PTS")
    if stats.get("rebounds") is not None:
        parts.append(f"{stats['rebounds']} REB")
    if stats.get("assists") is not None:
        parts.append(f"{stats['assists']} AST")
    return " | ".join(str(part) for part in parts if part)


def augment_game_with_nba_live(game: dict[str, Any], *, requested_date: str) -> dict[str, Any]:
    game_id = find_game_id_by_matchup(requested_date, game["away"]["abbr"], game["home"]["abbr"])
    if not game_id:
        return {"source": None, "dataFreshness": "fresh", "fallbackLevel": "none"}
    meta = {"source": None, "dataFreshness": "fresh", "fallbackLevel": "none"}
    if not game.get("playTimeline"):
        try:
            payload = fetch_play_by_play(game_id)
            actions = extract_play_actions(payload["data"])
            game["playTimeline"] = [
                {
                    "id": str(item.get("actionNumber") or ""),
                    "text": item.get("description") or "",
                    "shortDescription": item.get("description") or "",
                    "period": item.get("period"),
                    "clock": item.get("clock"),
                    "homeScore": item.get("homeScore"),
                    "awayScore": item.get("awayScore"),
                    "scoreValue": None,
                    "scoringPlay": True if item.get("homeScore") or item.get("awayScore") else False,
                    "teamId": item.get("teamId") or "",
                    "playerName": item.get("playerName") or "",
                }
                for item in actions
            ]
            game["recentPlays"] = [item["text"] for item in game["playTimeline"][-4:] if item.get("text")]
            meta = {"source": "nba_live", "dataFreshness": payload.get("dataFreshness", "fresh"), "fallbackLevel": "nba_live"}
        except NBAReportError:
            pass
    if not any((game.get("keyPlayers") or {}).values()) or not any((game.get("starters") or {}).values()):
        try:
            payload = fetch_live_boxscore(game_id)
            players_by_team = extract_boxscore_players(payload["data"])
            for abbr, players in players_by_team.items():
                if not game["starters"].get(abbr):
                    starters = [player["displayName"] for player in players if player.get("starter")]
                    game["starters"][abbr] = starters[:5]
                if not game["keyPlayers"].get(abbr):
                    lines = [_player_line_from_boxscore(player) for player in players]
                    game["keyPlayers"][abbr] = [line for line in lines if line][:3]
            meta = {"source": "nba_live", "dataFreshness": payload.get("dataFreshness", "fresh"), "fallbackLevel": "nba_live"}
        except NBAReportError:
            pass
    return meta


def build_game_scene(
    *,
    tz: str | None,
    date_text: str | None,
    team: str,
    lang: str,
    analysis_mode: str,
) -> dict[str, Any]:
    report = build_scene_report(tz=tz, date_text=date_text, team=team, lang=lang)
    game = report["games"][0]
    roster_snapshots = fetch_game_rosters(game)
    game = apply_roster_guard(game, roster_snapshots, lang=lang)
    sources = ["espn"]
    freshness = "fresh"
    fallback_level = "none"
    if analysis_mode in {"live", "post", "auto"} and (not game.get("playTimeline") or not any((game.get("keyPlayers") or {}).values())):
        augment_meta = augment_game_with_nba_live(game, requested_date=report["requestedDate"])
        if augment_meta.get("source"):
            sources.append("nba_live")
            freshness = augment_meta.get("dataFreshness", freshness)
            fallback_level = augment_meta.get("fallbackLevel", fallback_level)
    analysis = build_analysis(game, analysis_mode, report["labels"])
    if game.get("forceFallbackMatchup") and game.get("fallbackMatchup"):
        analysis["keyMatchup"] = game["fallbackMatchup"]
    elif not analysis.get("keyMatchup") and game.get("fallbackMatchup"):
        analysis["keyMatchup"] = game["fallbackMatchup"]
    digest = build_play_digest(game, lang=lang)
    return {
        "report": report,
        "game": game,
        "analysis": analysis,
        "digest": digest,
        "sources": sources,
        "fallbackLevel": fallback_level,
        "dataFreshness": freshness,
    }


def render_game_scene_markdown(scene: dict[str, Any]) -> str:
    report = scene["report"]
    game = scene["game"]
    analysis = scene["analysis"]
    labels = report["labels"]
    lines = [
        f"# {labels['title_game']} ({report['requestedDate']})",
        f"> {labels['timezone']}: {report['timezone']}",
        f"> {labels['requested_date']}: {report['requestedDate']}",
        f"> {labels['view']}: game",
        f"> {labels['filter_team']}: {report['teamFilter']}",
        "",
        labels["local_tip"],
        "",
    ]
    lines.extend(render_team_lines(game, labels))
    lines.append("")
    lines.extend(render_detail_blocks(game, labels))
    lines.extend(render_analysis_block(analysis, labels))
    if scene["digest"]["plays"]:
        lines.extend(["", "## 回合摘要" if report["lang"] == "zh" else "## Play Digest", ""])
        for item in scene["digest"]["plays"]:
            lines.append(f"- {item}")
    lines.extend(
        [
            "",
            f"> sources: {', '.join(scene['sources'])}",
            f"> fallbackLevel: {scene['fallbackLevel']}",
            f"> dataFreshness: {scene['dataFreshness']}",
        ]
    )
    return "\n".join(lines)


def render_day_scene(*, tz: str | None, date_text: str | None, lang: str) -> str:
    report = build_scene_report(tz=tz, date_text=date_text, team=None, lang=lang)
    return render_day_markdown(report)


def scene_payload(scene: dict[str, Any]) -> dict[str, Any]:
    game = scene["game"]
    return {
        "eventId": game["eventId"],
        "requestedDate": scene["report"]["requestedDate"],
        "statusState": game["statusState"],
        "teams": {
            "away": game["away"],
            "home": game["home"],
        },
        "verifiedPlayers": game.get("verifiedPlayers") or [],
        "rosters": game.get("rosters") or {},
        "analysis": scene["analysis"],
        "digest": scene["digest"],
        "sources": scene["sources"],
        "fallbackLevel": scene["fallbackLevel"],
        "dataFreshness": scene["dataFreshness"],
    }
