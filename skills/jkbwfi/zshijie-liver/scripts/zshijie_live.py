#!/usr/bin/env python3
"""Resolve Z视介 channel/cid to live URL and print URL-only response."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys

BASE_URL = "https://zmtv.cztv.com/cmsh5-share/prod/cztv-tvLive/index.html?pageId={cid}"

CHANNEL_TO_CID = {
    "浙江卫视": "101",
    "钱江都市": "102",
    "经济生活": "103",
    "教科影视": "104",
    "民生休闲": "106",
    "新闻": "107",
    "少儿频道": "108",
    "浙江国际": "110",
    "好易购": "111",
    "之江纪录": "112",
}

ALIASES = {
    "浙江卫视": "浙江卫视",
    "浙江卫视频道": "浙江卫视",
    "浙江卫视直播": "浙江卫视",
    "卫视": "浙江卫视",
    "钱江都市": "钱江都市",
    "钱江都市频道": "钱江都市",
    "钱江都市直播": "钱江都市",
    "钱江": "钱江都市",
    "经济生活": "经济生活",
    "经济生活频道": "经济生活",
    "教科影视": "教科影视",
    "教科影视频道": "教科影视",
    "民生休闲": "民生休闲",
    "民生休闲频道": "民生休闲",
    "新闻": "新闻",
    "新闻频道": "新闻",
    "少儿频道": "少儿频道",
    "少儿直播": "少儿频道",
    "少儿": "少儿频道",
    "浙江国际": "浙江国际",
    "浙江国际频道": "浙江国际",
    "国际": "浙江国际",
    "好易购": "好易购",
    "之江纪录": "之江纪录",
    "之江纪录频道": "之江纪录",
    "纪录": "之江纪录",
}

CID_TO_CHANNEL = {cid:channel for channel, cid in CHANNEL_TO_CID.items()}
SUPPORTED_CIDS = tuple(sorted(CID_TO_CHANNEL.keys()))

ACTION_WORDS = (
    "打开",
    "进入",
    "播放",
    "收看",
    "观看",
    "看",
    "切到",
    "切换到",
    "我要",
    "请",
    "帮我",
)

NOISE_WORDS = (
    "直播间",
    "直播",
    "电视频道",
    "电视台",
    "频道",
    "在线",
)


def normalize(text: str) -> str:
    normalized = text.strip().replace("\u3000", " ").lower()
    normalized = re.sub(r"\s+", "", normalized)
    normalized = re.sub(r"[，,。.!?？:：;；\"'“”‘’【】\[\]\(\)（）\-_/|]+", "", normalized)
    for word in ACTION_WORDS:
        normalized = normalized.replace(word, "")
    for word in NOISE_WORDS:
        normalized = normalized.replace(word, "")
    return normalized


NORMALIZED_ALIAS_LOOKUP = {normalize(alias): channel for alias, channel in ALIASES.items()}


def resolve_by_channel(channel_input: str) -> tuple[str, str]:
    normalized_input = normalize(channel_input)
    channel = NORMALIZED_ALIAS_LOOKUP.get(normalized_input)
    if channel:
        return channel, CHANNEL_TO_CID[channel]

    # Fallback: user input may contain surrounding words, match by contained alias.
    for alias, mapped_channel in sorted(
        NORMALIZED_ALIAS_LOOKUP.items(), key=lambda item: len(item[0]), reverse=True
    ):
        if alias and alias in normalized_input:
            channel = mapped_channel
            break

    if not channel:
        supported = ", ".join(CHANNEL_TO_CID.keys())
        raise ValueError(f"Unknown channel '{channel_input}'. Supported channels: {supported}")
    return channel, CHANNEL_TO_CID[channel]


def resolve_by_cid(cid_input: str) -> tuple[str, str]:
    cid = cid_input.strip()
    if cid not in CID_TO_CHANNEL:
        supported = ", ".join(SUPPORTED_CIDS)
        raise ValueError(f"Unsupported cid '{cid_input}'. Supported cids: {supported}")
    return CID_TO_CHANNEL[cid], cid


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve Z视介 channel/cid to live URL.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--channel", help="Channel name, e.g. 浙江卫视")
    group.add_argument("--cid", help="Channel cid, e.g. 101")
    group.add_argument("--list", action="store_true", help="List supported channels and cids")
    parser.add_argument(
        "--open",
        dest="open_page",
        action="store_true",
        default=True,
        help="Open URL in default browser (default: true)",
    )
    parser.add_argument(
        "--no-open",
        dest="open_page",
        action="store_false",
        help="Do not open URL in browser",
    )
    parser.add_argument("--json", action="store_true", help="Print result in JSON format")
    return parser.parse_args()


def print_channels(json_mode: bool) -> None:
    items = [{"channel": channel, "cid": cid} for channel, cid in CHANNEL_TO_CID.items()]
    if json_mode:
        print(json.dumps({"channels": items}, ensure_ascii=False))
        return
    for item in items:
        print(f"{item['channel']}\t{item['cid']}")


def print_error(message: str, json_mode: bool) -> None:
    if json_mode:
        print(json.dumps({"error": message}, ensure_ascii=False), file=sys.stderr)
        return
    print(f"error={message}", file=sys.stderr)


def try_open_url(url: str) -> None:
    if sys.platform == "darwin":
        cmd = ["open", url]
    elif sys.platform.startswith("linux"):
        if not shutil.which("xdg-open"):
            return
        cmd = ["xdg-open", url]
    elif sys.platform.startswith("win"):
        cmd = ["cmd", "/c", "start", "", url]
    else:
        return

    try:
        subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
    except Exception:
        return


def main() -> int:
    args = parse_args()

    if args.list:
        print_channels(args.json)
        return 0

    try:
        if args.channel:
            _channel, cid = resolve_by_channel(args.channel)
        else:
            _channel, cid = resolve_by_cid(args.cid or "")
    except ValueError as err:
        print_error(str(err), args.json)
        return 2

    url = BASE_URL.format(cid=cid)
    result: dict[str, object] = {"url": url}

    if args.open_page:
        try_open_url(url)

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(result["url"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
