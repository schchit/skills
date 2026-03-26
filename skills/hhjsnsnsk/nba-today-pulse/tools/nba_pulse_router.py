#!/usr/bin/env python3
"""Unified router for scene-specific NBA context scripts."""

from __future__ import annotations

import argparse
import json

from nba_pulse_core import build_game_scene, command_options, render_day_scene, render_game_scene_markdown, scene_payload


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Route a natural-language NBA request to the minimal scene builder.")
    parser.add_argument("--command", default="")
    parser.add_argument("--tz")
    parser.add_argument("--date")
    parser.add_argument("--team")
    parser.add_argument("--lang")
    parser.add_argument("--analysis-mode", choices=("auto", "pregame", "live", "post"))
    parser.add_argument("--format", default="markdown", choices=("markdown", "json"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    detected = command_options(args.command or "")
    lang = args.lang or str(detected["lang"])
    analysis_mode = args.analysis_mode or str(detected["analysis_mode"])
    date_text = args.date or (str(detected["date"]) if detected["date"] else None)
    team = args.team or (str(detected["team"]) if detected["team"] else None)
    tz = args.tz or (str(detected["tz"]) if detected["tz"] else None)

    if not team:
        rendered = render_day_scene(tz=tz, date_text=date_text, lang=lang)
        if args.format == "json":
            print(json.dumps({"markdown": rendered, "view": "day"}, ensure_ascii=False, indent=2))
        else:
            print(rendered)
        return 0

    scene = build_game_scene(tz=tz, date_text=date_text, team=team, lang=lang, analysis_mode=analysis_mode)
    if args.format == "json":
        print(json.dumps(scene_payload(scene), ensure_ascii=False, indent=2))
    else:
        print(render_game_scene_markdown(scene))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
