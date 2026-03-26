#!/usr/bin/env python3
"""Team alias helpers for NBA_TR."""

from __future__ import annotations

import re

TEAM_ALIASES: dict[str, list[str]] = {
    "ATL": ["atl", "hawks", "atlanta", "atlanta hawks", "老鹰", "亚特兰大老鹰"],
    "BOS": ["bos", "celtics", "boston", "boston celtics", "凯尔特人", "波士顿凯尔特人"],
    "BKN": ["bkn", "nets", "brooklyn", "brooklyn nets", "篮网", "布鲁克林篮网"],
    "CHA": ["cha", "hornets", "charlotte", "charlotte hornets", "黄蜂", "夏洛特黄蜂"],
    "CHI": ["chi", "bulls", "chicago", "chicago bulls", "公牛", "芝加哥公牛"],
    "CLE": ["cle", "cavaliers", "cavs", "cleveland", "cleveland cavaliers", "骑士", "克利夫兰骑士"],
    "DAL": ["dal", "mavericks", "mavs", "dallas", "dallas mavericks", "独行侠", "达拉斯独行侠", "小牛"],
    "DEN": ["den", "nuggets", "denver", "denver nuggets", "掘金", "丹佛掘金"],
    "DET": ["det", "pistons", "detroit", "detroit pistons", "活塞", "底特律活塞"],
    "GSW": ["gsw", "warriors", "golden state", "golden state warriors", "勇士", "金州勇士"],
    "HOU": ["hou", "rockets", "houston", "houston rockets", "火箭", "休斯顿火箭"],
    "IND": ["ind", "pacers", "indiana", "indiana pacers", "步行者", "印第安纳步行者"],
    "LAC": ["lac", "clippers", "la clippers", "los angeles clippers", "快船", "洛杉矶快船"],
    "LAL": ["lal", "lakers", "la lakers", "los angeles lakers", "湖人", "洛杉矶湖人"],
    "MEM": ["mem", "grizzlies", "memphis", "memphis grizzlies", "灰熊", "孟菲斯灰熊"],
    "MIA": ["mia", "heat", "miami", "miami heat", "热火", "迈阿密热火"],
    "MIL": ["mil", "bucks", "milwaukee", "milwaukee bucks", "雄鹿", "密尔沃基雄鹿"],
    "MIN": ["min", "timberwolves", "wolves", "minnesota", "minnesota timberwolves", "森林狼", "明尼苏达森林狼"],
    "NOP": ["nop", "pelicans", "new orleans", "new orleans pelicans", "鹈鹕", "新奥尔良鹈鹕"],
    "NYK": ["nyk", "knicks", "new york", "new york knicks", "尼克斯", "纽约尼克斯"],
    "OKC": ["okc", "thunder", "oklahoma city", "oklahoma city thunder", "雷霆", "俄克拉荷马城雷霆"],
    "ORL": ["orl", "magic", "orlando", "orlando magic", "魔术", "奥兰多魔术"],
    "PHI": ["phi", "76ers", "sixers", "philadelphia", "philadelphia 76ers", "76人", "费城76人"],
    "PHX": ["phx", "suns", "phoenix", "phoenix suns", "太阳", "菲尼克斯太阳"],
    "POR": ["por", "trail blazers", "blazers", "portland", "portland trail blazers", "开拓者", "波特兰开拓者"],
    "SAC": ["sac", "kings", "sacramento", "sacramento kings", "国王", "萨克拉门托国王"],
    "SAS": ["sas", "spurs", "san antonio", "san antonio spurs", "马刺", "圣安东尼奥马刺"],
    "TOR": ["tor", "raptors", "toronto", "toronto raptors", "猛龙", "多伦多猛龙"],
    "UTA": ["uta", "jazz", "utah", "utah jazz", "爵士", "犹他爵士"],
    "WAS": ["was", "wizards", "washington", "washington wizards", "奇才", "华盛顿奇才"],
}

TEAM_DISPLAY = {
    "ATL": "Atlanta Hawks",
    "BOS": "Boston Celtics",
    "BKN": "Brooklyn Nets",
    "CHA": "Charlotte Hornets",
    "CHI": "Chicago Bulls",
    "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks",
    "DEN": "Denver Nuggets",
    "DET": "Detroit Pistons",
    "GSW": "Golden State Warriors",
    "HOU": "Houston Rockets",
    "IND": "Indiana Pacers",
    "LAC": "LA Clippers",
    "LAL": "Los Angeles Lakers",
    "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat",
    "MIL": "Milwaukee Bucks",
    "MIN": "Minnesota Timberwolves",
    "NOP": "New Orleans Pelicans",
    "NYK": "New York Knicks",
    "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic",
    "PHI": "Philadelphia 76ers",
    "PHX": "Phoenix Suns",
    "POR": "Portland Trail Blazers",
    "SAC": "Sacramento Kings",
    "SAS": "San Antonio Spurs",
    "TOR": "Toronto Raptors",
    "UTA": "Utah Jazz",
    "WAS": "Washington Wizards",
}

PROVIDER_ABBR_MAP = {
    "GS": "GSW",
    "SA": "SAS",
    "NO": "NOP",
    "NY": "NYK",
    "UTAH": "UTA",
}

ESPN_TEAM_IDS = {
    "ATL": "1",
    "BOS": "2",
    "BKN": "17",
    "CHA": "30",
    "CHI": "4",
    "CLE": "5",
    "DAL": "6",
    "DEN": "7",
    "DET": "8",
    "GSW": "9",
    "HOU": "10",
    "IND": "11",
    "LAC": "12",
    "LAL": "13",
    "MEM": "29",
    "MIA": "14",
    "MIL": "15",
    "MIN": "16",
    "NOP": "3",
    "NYK": "18",
    "OKC": "25",
    "ORL": "19",
    "PHI": "20",
    "PHX": "21",
    "POR": "22",
    "SAC": "23",
    "SAS": "24",
    "TOR": "28",
    "UTA": "26",
    "WAS": "27",
}

NBA_TEAM_IDS = {
    "ATL": "1610612737",
    "BOS": "1610612738",
    "BKN": "1610612751",
    "CHA": "1610612766",
    "CHI": "1610612741",
    "CLE": "1610612739",
    "DAL": "1610612742",
    "DEN": "1610612743",
    "DET": "1610612765",
    "GSW": "1610612744",
    "HOU": "1610612745",
    "IND": "1610612754",
    "LAC": "1610612746",
    "LAL": "1610612747",
    "MEM": "1610612763",
    "MIA": "1610612748",
    "MIL": "1610612749",
    "MIN": "1610612750",
    "NOP": "1610612740",
    "NYK": "1610612752",
    "OKC": "1610612760",
    "ORL": "1610612753",
    "PHI": "1610612755",
    "PHX": "1610612756",
    "POR": "1610612757",
    "SAC": "1610612758",
    "SAS": "1610612759",
    "TOR": "1610612761",
    "UTA": "1610612762",
    "WAS": "1610612764",
}

_SORTED_ALIASES = sorted(
    ((alias, abbr) for abbr, aliases in TEAM_ALIASES.items() for alias in aliases),
    key=lambda item: len(item[0]),
    reverse=True,
)


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def normalize_team_input(value: str | None) -> str | None:
    if not value:
        return None
    normalized = _normalize(value)
    upper_value = value.strip().upper()
    if upper_value in TEAM_ALIASES:
        return upper_value
    for alias, abbr in _SORTED_ALIASES:
        if normalized == alias:
            return abbr
    return None


def extract_team_from_text(text: str | None) -> str | None:
    normalized_text = _normalize(text or "")
    for alias, abbr in _SORTED_ALIASES:
        if re.search(rf"(?<![a-z]){re.escape(alias)}(?![a-z])", normalized_text):
            return abbr
    return None


def canonicalize_team_abbr(value: str | None) -> str:
    normalized = (value or "").strip().upper()
    return PROVIDER_ABBR_MAP.get(normalized, normalized)


def provider_team_id(abbr: str | None, provider: str) -> str | None:
    canonical = canonicalize_team_abbr(abbr)
    if provider == "espn":
        return ESPN_TEAM_IDS.get(canonical)
    if provider == "nba":
        return NBA_TEAM_IDS.get(canonical)
    return None
