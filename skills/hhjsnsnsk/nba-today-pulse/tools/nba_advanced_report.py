#!/usr/bin/env python3
"""Render NBA reports with advanced pregame, live, and postgame analysis."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from nba_common import NBAReportError  # noqa: E402
from nba_today_report import (  # noqa: E402
    I18N,
    build_report_payload,
    format_counts_summary,
    render_detail_blocks,
    render_team_lines,
    safe_float,
    validate_args,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Return NBA report with advanced analysis.")
    parser.add_argument("--tz", help="IANA timezone, UTC offset, or city hint")
    parser.add_argument("--date", help="Requested local date in YYYY-MM-DD; defaults to today in requestor timezone")
    parser.add_argument("--team", help="Optional team abbreviation or alias")
    parser.add_argument("--view", default="day", choices=("day", "game"), help="Render daily overview or a single game")
    parser.add_argument("--lang", default="zh", choices=("zh", "en"), help="Response language")
    parser.add_argument("--format", default="markdown", choices=("markdown", "json"), help="Output format")
    parser.add_argument("--base-url", help="Override ESPN base URL for testing")
    parser.add_argument(
        "--analysis-mode",
        default="auto",
        choices=("auto", "pregame", "live", "post"),
        help="Choose analysis logic automatically or force a specific mode.",
    )
    return parser.parse_args(argv)


def parse_record_text(value: str | None) -> tuple[int, int] | None:
    text = (value or "").strip()
    if "-" not in text:
        return None
    wins_text, losses_text = text.split("-", 1)
    try:
        return int(wins_text), int(losses_text)
    except ValueError:
        return None


def parse_period_score(value: str | None) -> int:
    try:
        return int((value or "0").strip())
    except ValueError:
        return 0


def abbr_by_team_id(game: dict[str, Any], team_id: str | None) -> str | None:
    if not team_id:
        return None
    if game["home"].get("id") == team_id:
        return game["home"]["abbr"]
    if game["away"].get("id") == team_id:
        return game["away"]["abbr"]
    return None


def standings_for_side(game: dict[str, Any], side: str) -> dict[str, Any]:
    team_id = game[side].get("id") or ""
    return game.get("standings", {}).get(team_id) or {}


def last_five_for_side(game: dict[str, Any], side: str) -> dict[str, Any]:
    team_id = game[side].get("id") or ""
    return game.get("lastFiveGames", {}).get(team_id) or {}


def season_stats_for_side(game: dict[str, Any], side: str) -> dict[str, str]:
    return game.get("teamSeasonStats", {}).get(game[side]["abbr"]) or {}


def schedule_context_for_side(game: dict[str, Any], side: str) -> dict[str, Any]:
    return game.get("teamScheduleContext", {}).get(game[side]["abbr"]) or {}


def injury_burden(game: dict[str, Any], side: str) -> float:
    burden = 0.0
    for item in game.get("injuries", {}).get(game[side]["abbr"], []):
        lowered = item.lower()
        if "out" in lowered or "缺阵" in lowered:
            burden += 1.5
        elif "doubt" in lowered:
            burden += 1.25
        elif "question" in lowered or "questionable" in lowered or "成疑" in lowered:
            burden += 1.0
        elif "day-to-day" in lowered or "每日观察" in lowered:
            burden += 0.5
    return burden


def compare_metric(game: dict[str, Any], metric: str, higher_is_better: bool = True) -> str | None:
    home_value = safe_float(season_stats_for_side(game, "home").get(metric))
    away_value = safe_float(season_stats_for_side(game, "away").get(metric))
    if home_value is None or away_value is None or home_value == away_value:
        return None
    better_side = "home" if home_value > away_value else "away"
    if not higher_is_better:
        better_side = "away" if better_side == "home" else "home"
    return better_side


def matchup_text(game: dict[str, Any], labels: dict[str, str]) -> str | None:
    away_leader = (game.get("leaders", {}).get(game["away"]["abbr"]) or [None])[0]
    home_leader = (game.get("leaders", {}).get(game["home"]["abbr"]) or [None])[0]
    if away_leader and home_leader:
        return f"{game['away']['abbr']} {away_leader} vs {game['home']['abbr']} {home_leader}"
    return None


def resolve_mode(game: dict[str, Any], requested_mode: str) -> str:
    state_to_mode = {"pre": "pregame", "in": "live", "post": "post"}
    actual_mode = state_to_mode.get(game["statusState"], "pregame")
    if requested_mode == "auto":
        return actual_mode
    if requested_mode != actual_mode:
        return actual_mode
    return requested_mode


def make_summary_line(game: dict[str, Any], labels: dict[str, str], favored_side: str | None, strength: int) -> str:
    if favored_side is None:
        return "两队赛前信号接近，属于胶着对局。" if labels["timezone"] == "请求方时区" else "The pregame indicators are tightly split, so this profiles as a close matchup."
    favored_abbr = game[favored_side]["abbr"]
    if labels["timezone"] == "请求方时区":
        if strength >= 4:
            return f"倾向 {favored_abbr}，赛前信号优势较明确。"
        if strength >= 2:
            return f"倾向 {favored_abbr}，但比赛仍有波动空间。"
        return f"{favored_abbr} 略占上风，整体仍接近五五开。"
    if strength >= 4:
        return f"{favored_abbr} has the clearer pregame edge."
    if strength >= 2:
        return f"{favored_abbr} has the better pregame case, but the matchup still has swing potential."
    return f"{favored_abbr} holds a slight edge, but the game still profiles as close."


def build_pregame_analysis(game: dict[str, Any], labels: dict[str, str]) -> dict[str, Any]:
    scores = {"home": 0, "away": 0}
    reasons: list[tuple[int, str]] = []
    predictor = game.get("predictor") or {}
    pickcenter = game.get("pickcenter") or {}

    home_projection = predictor.get("homeProjection")
    away_projection = predictor.get("awayProjection")
    if home_projection is not None and away_projection is not None:
        diff = abs(home_projection - away_projection)
        favored_side = "home" if home_projection > away_projection else "away"
        scores[favored_side] += 2 if diff >= 10 else 1
        if labels["timezone"] == "请求方时区":
            reasons.append((3, f"ESPN predictor: {game[favored_side]['abbr']} {max(home_projection, away_projection):.1f}%"))
        else:
            reasons.append((3, f"ESPN predictor gives {game[favored_side]['abbr']} {max(home_projection, away_projection):.1f}%"))

    for side in ("home", "away"):
        last_five = last_five_for_side(game, side)
        if last_five:
            scores[side] += 0
    home_last_five = last_five_for_side(game, "home")
    away_last_five = last_five_for_side(game, "away")
    if home_last_five and away_last_five:
        home_wins = int(home_last_five.get("wins") or 0)
        away_wins = int(away_last_five.get("wins") or 0)
        if home_wins != away_wins:
            favored_side = "home" if home_wins > away_wins else "away"
            scores[favored_side] += 2 if abs(home_wins - away_wins) >= 2 else 1
            if labels["timezone"] == "请求方时区":
                reasons.append((2, f"近5场状态: {game[favored_side]['abbr']} {max(home_wins, away_wins)}-{min(home_wins, away_wins)}"))
            else:
                reasons.append((2, f"Recent form: {game[favored_side]['abbr']} is {max(home_wins, away_wins)}-{min(home_wins, away_wins)} over the last five"))

    home_standings = standings_for_side(game, "home")
    away_standings = standings_for_side(game, "away")
    home_pct = safe_float(home_standings.get("winPercent"))
    away_pct = safe_float(away_standings.get("winPercent"))
    if home_pct is not None and away_pct is not None and home_pct != away_pct:
        favored_side = "home" if home_pct > away_pct else "away"
        scores[favored_side] += 2 if abs(home_pct - away_pct) >= 0.08 else 1
        if labels["timezone"] == "请求方时区":
            reasons.append((2, f"赛季战绩边际更好: {game[favored_side]['abbr']}"))
        else:
            reasons.append((2, f"Season profile edge: {game[favored_side]['abbr']} has the stronger record"))

    home_rest = schedule_context_for_side(game, "home")
    away_rest = schedule_context_for_side(game, "away")
    home_rest_days = home_rest.get("restDays")
    away_rest_days = away_rest.get("restDays")
    if home_rest_days is not None and away_rest_days is not None and home_rest_days != away_rest_days:
        favored_side = "home" if home_rest_days > away_rest_days else "away"
        scores[favored_side] += 1
        if labels["timezone"] == "请求方时区":
            reasons.append((1, f"赛程边际: {game[favored_side]['abbr']} 休整更充分"))
        else:
            reasons.append((1, f"Scheduling edge: {game[favored_side]['abbr']} comes in with more rest"))

    home_injury = injury_burden(game, "home")
    away_injury = injury_burden(game, "away")
    if home_injury != away_injury:
        favored_side = "home" if home_injury < away_injury else "away"
        scores[favored_side] += 1
        if labels["timezone"] == "请求方时区":
            reasons.append((1, f"可用性边际: {game[favored_side]['abbr']} 伤病压力更小"))
        else:
            reasons.append((1, f"Availability edge: {game[favored_side]['abbr']} carries less injury risk"))

    profile_points = {"home": 0, "away": 0}
    for metric in ("avgPoints", "fieldGoalPct", "threePointPct", "assistTurnoverRatio"):
        winner = compare_metric(game, metric)
        if winner:
            profile_points[winner] += 1
    if profile_points["home"] != profile_points["away"]:
        favored_side = "home" if profile_points["home"] > profile_points["away"] else "away"
        scores[favored_side] += 1
        if labels["timezone"] == "请求方时区":
            reasons.append((1, f"进攻指标更优: {game[favored_side]['abbr']}"))
        else:
            reasons.append((1, f"Offensive profile edge: {game[favored_side]['abbr']}"))

    season_series = game.get("seasonSeries") or []
    if season_series:
        series = season_series[0]
        summary = str(series.get("summary") or "")
        if game["home"]["abbr"] in summary and "lead" in summary.lower():
            scores["home"] += 1
        elif game["away"]["abbr"] in summary and "lead" in summary.lower():
            scores["away"] += 1

    favored_side: str | None = None
    if scores["home"] != scores["away"]:
        favored_side = "home" if scores["home"] > scores["away"] else "away"
    strength = abs(scores["home"] - scores["away"])
    sorted_reasons = [text for _, text in sorted(reasons, key=lambda item: item[0], reverse=True)[:4]]
    analysis = {
        "mode": "pregame",
        "summary": make_summary_line(game, labels, favored_side, strength),
        "reasons": sorted_reasons,
        "trend": (
            f"{game[favored_side]['abbr']} 更像是赛前占优的一方。"
            if labels["timezone"] == "请求方时区" and favored_side
            else (
                f"{game[favored_side]['abbr']} has the stronger pregame lean."
                if favored_side
                else ("暂时没有明确赛前倾向。" if labels["timezone"] == "请求方时区" else "No clear pregame lean stands out.")
            )
        ),
        "turningPoint": "",
        "keyMatchup": matchup_text(game, labels) or "",
        "signals": {
            "homeScore": scores["home"],
            "awayScore": scores["away"],
            "pickcenter": pickcenter,
        },
    }
    return analysis


def summarize_recent_run(game: dict[str, Any]) -> tuple[str | None, int]:
    scoring_plays = [play for play in game.get("playTimeline", [])[-8:] if play.get("scoringPlay")]
    if not scoring_plays:
        return None, 0
    points = {"home": 0, "away": 0}
    for play in scoring_plays:
        side = "home" if play.get("teamId") == game["home"].get("id") else "away"
        points[side] += int(play.get("scoreValue") or 0)
    if points["home"] == points["away"]:
        return None, 0
    side = "home" if points["home"] > points["away"] else "away"
    return side, abs(points["home"] - points["away"])


def win_probability_edge(game: dict[str, Any]) -> tuple[str | None, float | None]:
    timeline = game.get("winProbabilityTimeline") or []
    if not timeline:
        return None, None
    last_value = timeline[-1].get("homeWinPercentage")
    if last_value is None:
        return None, None
    if last_value > 0.5:
        return "home", float(last_value)
    if last_value < 0.5:
        return "away", float(1 - last_value)
    return None, float(last_value)


def biggest_swing_text(game: dict[str, Any], winner_side: str | None = None) -> str:
    timeline = game.get("winProbabilityTimeline") or []
    if len(timeline) < 2:
        return ""
    play_lookup = {play.get("id"): play for play in game.get("playTimeline", []) if play.get("id")}
    best_entry: tuple[float, dict[str, Any]] | None = None
    previous = timeline[0]
    for current in timeline[1:]:
        previous_value = previous.get("homeWinPercentage")
        current_value = current.get("homeWinPercentage")
        if previous_value is None or current_value is None:
            previous = current
            continue
        delta = current_value - previous_value
        if winner_side == "away":
            delta *= -1
        elif winner_side is None:
            delta = abs(delta)
        if best_entry is None or delta > best_entry[0]:
            best_entry = (delta, current)
        previous = current
    if not best_entry or best_entry[0] <= 0:
        return ""
    play = play_lookup.get(best_entry[1].get("playId") or "")
    if not play:
        return ""
    prefix = " ".join(part for part in (f"P{play.get('period')}" if play.get("period") else "", play.get("clock") or "") if part).strip()
    return f"{prefix} {play.get('text')}".strip()


def build_live_analysis(game: dict[str, Any], labels: dict[str, str]) -> dict[str, Any]:
    home_score = parse_period_score(game["home"].get("score"))
    away_score = parse_period_score(game["away"].get("score"))
    margin = abs(home_score - away_score)
    leading_side = "home" if home_score > away_score else "away" if away_score > home_score else None
    wp_side, wp_value = win_probability_edge(game)
    run_side, run_margin = summarize_recent_run(game)
    reasons: list[str] = []
    if leading_side:
        if labels["timezone"] == "请求方时区":
            reasons.append(f"当前比分: {game[leading_side]['abbr']} 领先 {margin} 分")
        else:
            reasons.append(f"Live score: {game[leading_side]['abbr']} leads by {margin}")
    if wp_side and wp_value is not None:
        percent = wp_value * 100
        if labels["timezone"] == "请求方时区":
            reasons.append(f"实时胜率倾向: {game[wp_side]['abbr']} 约 {percent:.1f}%")
        else:
            reasons.append(f"Win probability edge: {game[wp_side]['abbr']} around {percent:.1f}%")
    if run_side and run_margin:
        if labels["timezone"] == "请求方时区":
            reasons.append(f"近期攻势: {game[run_side]['abbr']} 近段净胜 {run_margin} 分")
        else:
            reasons.append(f"Recent run: {game[run_side]['abbr']} is +{run_margin} over the latest scoring stretch")

    if leading_side and ((margin >= 8 and (game.get("period") or 0) >= 4) or (wp_side == leading_side and (wp_value or 0) >= 0.75)):
        summary = (
            f"{game[leading_side]['abbr']} 当前更像是在掌控比赛走向。"
            if labels["timezone"] == "请求方时区"
            else f"{game[leading_side]['abbr']} currently looks in control of the game."
        )
    elif leading_side:
        summary = (
            f"{game[leading_side]['abbr']} 暂时占优，但比赛仍在可逆转区间。"
            if labels["timezone"] == "请求方时区"
            else f"{game[leading_side]['abbr']} holds the edge, but the game is still in swing range."
        )
    else:
        summary = "比赛仍然非常胶着。" if labels["timezone"] == "请求方时区" else "The game remains tightly contested."

    key_players: list[str] = []
    for side in ("away", "home"):
        entries = game.get("keyPlayers", {}).get(game[side]["abbr"]) or []
        if entries:
            key_players.append(f"{game[side]['abbr']} {entries[0]}")

    analysis = {
        "mode": "live",
        "summary": summary,
        "reasons": reasons[:4],
        "trend": (
            f"{game[leading_side]['abbr']} 目前更接近终盘优势方。"
            if labels["timezone"] == "请求方时区" and leading_side
            else (
                f"{game[leading_side]['abbr']} is better positioned right now."
                if leading_side
                else ("两队都还在争夺主动权。" if labels["timezone"] == "请求方时区" else "Both teams are still fighting for control.")
            )
        ),
        "turningPoint": biggest_swing_text(game),
        "keyMatchup": " / ".join(key_players[:2]),
        "signals": {
            "margin": margin,
            "leadingSide": leading_side,
            "winProbabilitySide": wp_side,
            "recentRunSide": run_side,
        },
    }
    return analysis


def decisive_period_text(game: dict[str, Any], winner_side: str, labels: dict[str, str]) -> str:
    away_scores = [parse_period_score(value) for value in game["away"].get("linescores") or []]
    home_scores = [parse_period_score(value) for value in game["home"].get("linescores") or []]
    if not away_scores or not home_scores:
        return ""
    best_period = None
    best_margin = -1
    for index, (away_score, home_score) in enumerate(zip(away_scores, home_scores), start=1):
        diff = home_score - away_score
        winner_margin = diff if winner_side == "home" else -diff
        if winner_margin > best_margin:
            best_margin = winner_margin
            best_period = index
    if best_period is None or best_margin <= 0:
        return ""
    if labels["timezone"] == "请求方时区":
        return f"第 {best_period} 节净胜 {best_margin} 分"
    return f"Quarter {best_period}: +{best_margin}"


def build_post_analysis(game: dict[str, Any], labels: dict[str, str]) -> dict[str, Any]:
    home_score = parse_period_score(game["home"].get("score"))
    away_score = parse_period_score(game["away"].get("score"))
    winner_side = "home" if home_score > away_score else "away"
    loser_side = "away" if winner_side == "home" else "home"
    margin = abs(home_score - away_score)
    decisive_period = decisive_period_text(game, winner_side, labels)
    turning_point = biggest_swing_text(game, winner_side=winner_side)
    reasons = [
        (
            f"最终比分差 {margin} 分，{game[winner_side]['abbr']} 收下比赛。"
            if labels["timezone"] == "请求方时区"
            else f"{game[winner_side]['abbr']} won by {margin} points."
        )
    ]
    if decisive_period:
        if labels["timezone"] == "请求方时区":
            reasons.append(f"决定性阶段: {decisive_period}")
        else:
            reasons.append(f"Decisive stretch: {decisive_period}")
    winner_key_player = (game.get("keyPlayers", {}).get(game[winner_side]["abbr"]) or [None])[0]
    if winner_key_player:
        if labels["timezone"] == "请求方时区":
            reasons.append(f"关键球员: {game[winner_side]['abbr']} {winner_key_player}")
        else:
            reasons.append(f"Lead performer: {game[winner_side]['abbr']} {winner_key_player}")
    article = game.get("article") or {}
    if article.get("headline"):
        reasons.append(str(article["headline"]))

    summary = (
        f"{game[winner_side]['abbr']} 从整体走向上更稳定地掌控了比赛。"
        if labels["timezone"] == "请求方时区"
        else f"{game[winner_side]['abbr']} controlled the broader game flow more consistently."
    )
    trend = (
        f"{game[winner_side]['abbr']} 在关键时段压住了 {game[loser_side]['abbr']}。"
        if labels["timezone"] == "请求方时区"
        else f"{game[winner_side]['abbr']} separated during the decisive stretch against {game[loser_side]['abbr']}."
    )
    return {
        "mode": "post",
        "summary": summary,
        "reasons": reasons[:4],
        "trend": trend,
        "turningPoint": turning_point,
        "keyMatchup": matchup_text(game, labels) or "",
        "signals": {
            "winner": game[winner_side]["abbr"],
            "margin": margin,
            "decisivePeriod": decisive_period,
        },
    }


def build_analysis(game: dict[str, Any], requested_mode: str, labels: dict[str, str]) -> dict[str, Any]:
    mode = resolve_mode(game, requested_mode)
    if mode == "pregame":
        analysis = build_pregame_analysis(game, labels)
    elif mode == "live":
        analysis = build_live_analysis(game, labels)
    else:
        analysis = build_post_analysis(game, labels)
    game["analysisSignals"] = analysis.get("signals") or {}
    game["analysisSummary"] = analysis
    return analysis


def render_analysis_block(analysis: dict[str, Any], labels: dict[str, str]) -> list[str]:
    lines = [f"## {labels['advanced_section']}", ""]
    lines.append(f"- {labels['analysis_summary']}: {analysis['summary']}")
    if analysis.get("trend"):
        lines.append(f"- {labels['analysis_trend']}: {analysis['trend']}")
    if analysis.get("keyMatchup"):
        lines.append(f"- {labels['analysis_key_matchup']}: {analysis['keyMatchup']}")
    if analysis.get("turningPoint"):
        lines.append(f"- {labels['analysis_turning_point']}: {analysis['turningPoint']}")
    if analysis.get("reasons"):
        lines.append(f"- {labels['analysis_reasons']}: {' / '.join(analysis['reasons'])}")
    lines.extend(["", labels["analysis_deep_note"]])
    return lines


def render_markdown(report: dict[str, Any], analysis_mode: str) -> str:
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
        analysis = build_analysis(game, analysis_mode, labels)
        lines.extend(render_team_lines(game, labels))
        lines.append("")
        lines.extend(render_detail_blocks(game, labels))
        lines.extend(render_analysis_block(analysis, labels))
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
            analysis = build_analysis(game, analysis_mode, labels)
            lines.extend(render_team_lines(game, labels))
            lines.append(f"- {labels['analysis_summary']}: {analysis['summary']}")
            if analysis.get("reasons"):
                lines.append(f"- {labels['analysis_reasons']}: {' / '.join(analysis['reasons'][:3])}")
            lines.append("")
    lines.append(labels["analysis_deep_note"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        validate_args(args)
        report = build_report_payload(args)
        for game in report["games"]:
            build_analysis(game, args.analysis_mode, report["labels"])
        if args.format == "json":
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(render_markdown(report, args.analysis_mode))
        return 0
    except NBAReportError as exc:
        print(f"[{exc.kind}] {exc}", file=sys.stderr)
        return 2 if exc.kind == "invalid_arguments" else 1


if __name__ == "__main__":
    sys.exit(main())
