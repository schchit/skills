#!/usr/bin/env python3
"""Compact play-by-play digest helpers for NBA_TR."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def _format_play(play: dict[str, Any]) -> str:
    period = play.get("period")
    clock = play.get("clock") or ""
    text = play.get("text") or play.get("description") or ""
    prefix = " ".join(part for part in (f"P{period}" if period else "", clock) if part).strip()
    return f"{prefix} {text}".strip()


def build_play_digest(game: dict[str, Any], *, lang: str, limit: int = 5) -> dict[str, Any]:
    plays = game.get("playTimeline") or []
    scoring = [play for play in plays if play.get("scoringPlay") or play.get("scoreValue")]
    recent = [_format_play(play) for play in scoring[-limit:]]
    turning_point = ""
    if scoring:
        turning_point = _format_play(scoring[-1])
    summary = (
        "未从结构化源确认到足够的回合细节。"
        if lang == "zh" and not recent
        else (
            "Structured play detail is currently unavailable."
            if not recent
            else (
                f"压缩为 {len(recent)} 个关键回合。"
                if lang == "zh"
                else f"Compressed to {len(recent)} key plays."
            )
        )
    )
    return {
        "summary": summary,
        "turningPoint": turning_point,
        "plays": recent,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Digest play timeline JSON into compact key plays.")
    parser.add_argument("--lang", default="zh", choices=("zh", "en"))
    parser.add_argument("--limit", type=int, default=5)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = json.load(sys.stdin)
    print(json.dumps(build_play_digest(payload, lang=args.lang, limit=args.limit), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
