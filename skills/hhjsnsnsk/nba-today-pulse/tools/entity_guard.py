#!/usr/bin/env python3
"""Entity validation helpers for verified player output."""

from __future__ import annotations

import re
from typing import Any

PLAYER_SEPARATORS = (" (", " |", " -")


def normalize_player_name(value: str | None) -> str:
    text = re.sub(r"\s+", " ", (value or "").strip()).casefold()
    return text


def extract_primary_name(text: str | None) -> str:
    value = (text or "").strip()
    for separator in PLAYER_SEPARATORS:
        if separator in value:
            return value.split(separator, 1)[0].strip()
    return value


def roster_names(roster_items: list[dict[str, Any]] | None) -> set[str]:
    names: set[str] = set()
    for item in roster_items or []:
        display_name = item.get("displayName") or item.get("shortName")
        normalized = normalize_player_name(display_name)
        if normalized:
            names.add(normalized)
    return names


def boxscore_names(game: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for lines in (game.get("starters") or {}).values():
        for item in lines or []:
            normalized = normalize_player_name(item)
            if normalized:
                names.add(normalized)
    for lines in (game.get("leaders") or {}).values():
        for item in lines or []:
            normalized = normalize_player_name(extract_primary_name(item))
            if normalized:
                names.add(normalized)
    for lines in (game.get("keyPlayers") or {}).values():
        for item in lines or []:
            normalized = normalize_player_name(extract_primary_name(item))
            if normalized:
                names.add(normalized)
    for play in game.get("playTimeline") or []:
        for key in ("playerName", "secondaryPlayerName", "tertiaryPlayerName"):
            normalized = normalize_player_name(play.get(key))
            if normalized:
                names.add(normalized)
    return names


def verified_player_names(game: dict[str, Any], rosters_by_abbr: dict[str, list[dict[str, Any]]]) -> set[str]:
    names: set[str] = set()
    roster_backed_names: set[str] = set()
    for roster in rosters_by_abbr.values():
        roster_backed_names.update(roster_names(roster))
    if roster_backed_names:
        names.update(roster_backed_names)
        for play in game.get("playTimeline") or []:
            for key in ("playerName", "secondaryPlayerName", "tertiaryPlayerName"):
                normalized = normalize_player_name(play.get(key))
                if normalized:
                    names.add(normalized)
        return names
    names.update(boxscore_names(game))
    return names


def filter_named_lines(lines: list[str], allowed_names: set[str]) -> list[str]:
    if not lines or not allowed_names:
        return lines[:]
    filtered: list[str] = []
    for line in lines:
        primary_name = normalize_player_name(extract_primary_name(line))
        if not primary_name or primary_name in allowed_names:
            filtered.append(line)
    return filtered


def filter_headlines(headlines: list[str], blocked_names: set[str]) -> list[str]:
    if not blocked_names:
        return headlines[:]
    results: list[str] = []
    blocked = [name for name in blocked_names if name]
    for headline in headlines:
        lowered = normalize_player_name(headline)
        if any(name in lowered for name in blocked):
            continue
        results.append(headline)
    return results


def blocked_names(candidate_lines: list[str], allowed_names: set[str]) -> set[str]:
    blocked: set[str] = set()
    for line in candidate_lines:
        primary = normalize_player_name(extract_primary_name(line))
        if primary and primary not in allowed_names:
            blocked.add(primary)
    return blocked


def fallback_matchup_text(game: dict[str, Any], *, lang: str) -> str:
    away_abbr = game.get("away", {}).get("abbr") or "AWAY"
    home_abbr = game.get("home", {}).get("abbr") or "HOME"
    if lang == "zh":
        return f"{away_abbr} 后场/锋线轮换 vs {home_abbr} 后场/锋线轮换"
    return f"{away_abbr} backcourt/wing group vs {home_abbr} backcourt/wing group"
