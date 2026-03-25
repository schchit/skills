#!/usr/bin/env python3
"""Fetch and filter CLS Telegraph items for Iran tracker."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests


DEFAULT_TIMEOUT = 20
CLS_COL_TITLE = "标题"
CLS_COL_CONTENT = "内容"
CLS_COL_LEVEL = "等级"
CLS_COL_TAGS = "标签"
CLS_COL_TIME = "发布时间"
CLS_COL_DATE = "发布日期"

IRAN_CORE_KEYWORDS = ["iran", "iranian", "tehran", "islamic republic", "伊朗", "德黑兰"]
FOCUS_GEO_KEYWORDS = ["iran", "iranian", "tehran", "strait of hormuz", "hormuz", "persian gulf", "伊朗", "德黑兰", "霍尔木兹", "波斯湾"]
WAR_TOPIC_KEYWORDS = ["war", "strike", "airstrike", "missile", "drone", "military", "troop", "attack", "conflict", "retaliation", "ground operation", "战争", "空袭", "导弹", "无人机", "军事", "部队", "袭击", "冲突", "报复", "地面行动"]
ECON_TOPIC_KEYWORDS = ["oil", "gas", "lng", "energy", "export", "supply", "production", "sanction", "shipping", "economy", "inflation", "tanker", "石油", "原油", "天然气", "能源", "出口", "供给", "产量", "制裁", "航运", "经济", "通胀", "油轮"]
DIPLO_TOPIC_KEYWORDS = ["president", "prime minister", "foreign minister", "defense minister", "diplomat", "talks", "negotiation", "ceasefire", "statement", "remarks", "united nations", "un ", "总统", "总理", "外长", "防长", "外交", "谈判", "停火", "声明", "表态", "联合国"]
CLS_NOISE_KEYWORDS = ["market wrap", "premarket", "stocks to watch", "stock market", "app store", "盘前要闻", "股市"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch CLS Telegraph items for Iran tracker.")
    parser.add_argument("--output", help="Optional path to write filtered CLS items as JSON.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum filtered items to return.")
    return parser.parse_args()


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "iran-war-tracker-cls/1.0"})
    return session


def normalize_text(value: Any) -> str:
    return str(value or "").strip()


def lowered_text(parts: list[Any]) -> str:
    return " ".join(normalize_text(part) for part in parts if normalize_text(part)).lower()


def has_any_keyword(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def topic_matches(text: str) -> set[str]:
    matches: set[str] = set()
    if has_any_keyword(text, WAR_TOPIC_KEYWORDS):
        matches.add("war")
    if has_any_keyword(text, ECON_TOPIC_KEYWORDS):
        matches.add("economy")
    if has_any_keyword(text, DIPLO_TOPIC_KEYWORDS):
        matches.add("diplomacy")
    return matches


def is_iran_war_related(text: str, allowed_topics: set[str] | None = None) -> bool:
    if not has_any_keyword(text, IRAN_CORE_KEYWORDS):
        return False
    matches = topic_matches(text)
    if not matches:
        return False
    if allowed_topics is None:
        return True
    return bool(matches & allowed_topics)


def relevance_score(text: str) -> int:
    score = 0
    if has_any_keyword(text, IRAN_CORE_KEYWORDS):
        score += 3
    score += len(topic_matches(text)) * 2
    if has_any_keyword(text, ["hormuz", "strait of hormuz", "霍尔木兹"]):
        score += 2
    return score


def compact_snippet(value: Any, limit: int = 180) -> str:
    text = " ".join(normalize_text(value).split())
    for marker in ["...", ". ", "! ", "? ", "\n"]:
        if marker in text:
            text = text.split(marker, 1)[0].strip()
            break
    return text[: limit - 1].rstrip() + "…" if len(text) > limit else text


def unique_lines(items: list[str], limit: int | None = None) -> list[str]:
    seen: list[str] = []
    for item in items:
        value = normalize_text(item)
        if value and value not in seen:
            seen.append(value)
        if limit is not None and len(seen) >= limit:
            break
    return seen


def cls_telegraphs(session: requests.Session, timeout: int = DEFAULT_TIMEOUT) -> pd.DataFrame:
    current_time = int(time.time())
    url = "https://www.cls.cn/nodeapi/telegraphList"
    params = {"app": "CailianpressWeb", "category": "", "lastTime": current_time, "last_time": current_time, "os": "web", "refresh_type": "1", "rn": "2000", "sv": "7.7.5"}
    text = session.get(url, params=params, timeout=timeout).url.split("?")[1]
    text_bytes = text if isinstance(text, bytes) else bytes(text, "utf-8")
    sha1 = hashlib.sha1(text_bytes).hexdigest()
    params["sign"] = hashlib.md5(sha1.encode()).hexdigest()
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=utf-8",
        "Host": "www.cls.cn",
        "Pragma": "no-cache",
        "Referer": "https://www.cls.cn/telegraph",
        "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    }
    data = session.get(url, headers=headers, params=params, timeout=timeout).json()
    df = pd.DataFrame(data["data"]["roll_data"])
    df = df[["title", "content", "level", "subjects", "ctime"]]
    df["ctime"] = pd.to_datetime(df["ctime"], unit="s", utc=True).dt.tz_convert("Asia/Shanghai")
    df.columns = [CLS_COL_TITLE, CLS_COL_CONTENT, CLS_COL_LEVEL, CLS_COL_TAGS, CLS_COL_TIME]
    df.sort_values([CLS_COL_TIME], ascending=False, inplace=True)
    df.reset_index(inplace=True, drop=True)
    df[CLS_COL_TAGS] = [",".join([t["subject_name"] for t in tags]) if tags else "" for tags in df[CLS_COL_TAGS].to_numpy()]
    df[CLS_COL_DATE] = df[CLS_COL_TIME].dt.date.astype(str)
    df[CLS_COL_TIME] = df[CLS_COL_TIME].dt.strftime("%H:%M:%S")
    return df


def filter_cls_items(df: pd.DataFrame, limit: int = 20) -> list[dict[str, Any]]:
    if df.empty:
        return []
    ranked: list[tuple[int, dict[str, Any]]] = []
    for item in df.to_dict("records"):
        title = normalize_text(item.get(CLS_COL_TITLE, ""))
        content = normalize_text(item.get(CLS_COL_CONTENT, ""))
        tags = normalize_text(item.get(CLS_COL_TAGS, ""))
        title_text = lowered_text([title])
        primary_text = lowered_text([title, tags])
        full_text = lowered_text([title, content, tags])
        if has_any_keyword(title_text, CLS_NOISE_KEYWORDS):
            continue
        if not is_iran_war_related(full_text, allowed_topics={"war", "economy", "diplomacy"}):
            continue
        if not has_any_keyword(primary_text, FOCUS_GEO_KEYWORDS):
            continue
        trimmed = dict(item)
        trimmed[CLS_COL_TITLE] = compact_snippet(title, limit=90)
        trimmed[CLS_COL_CONTENT] = compact_snippet(content, limit=120)
        ranked.append((relevance_score(full_text), trimmed))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in ranked[:limit]]


def cls_lines(items: list[dict[str, Any]], limit: int) -> list[str]:
    lines = []
    for item in items:
        line = " | ".join(part for part in [normalize_text(item.get(CLS_COL_TIME, "")), normalize_text(item.get(CLS_COL_TITLE, "")), normalize_text(item.get(CLS_COL_CONTENT, ""))] if part)
        if line:
            lines.append(line)
    return unique_lines(lines, limit)


def main() -> int:
    args = parse_args()
    session = get_session()
    filtered = filter_cls_items(cls_telegraphs(session), limit=args.limit)
    if args.output:
        Path(args.output).write_text(json.dumps(filtered, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(json.dumps(filtered, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
