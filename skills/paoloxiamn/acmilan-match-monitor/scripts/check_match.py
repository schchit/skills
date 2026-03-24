#!/usr/bin/env python3
"""
AC Milan 昨日比赛检查脚本
数据来源：ESPN 公开 API（无需 token，无地区限制）
AC Milan ESPN ID: 103（意甲联赛 ita.1）
输出：有比赛则打印比赛结果；无比赛则无输出
"""
import json
import subprocess
from datetime import datetime, timedelta, timezone

# 北京时间昨天日期
tz_sh = timezone(timedelta(hours=8))
yesterday = (datetime.now(tz_sh) - timedelta(days=1)).strftime("%Y-%m-%d")

TEAM_ABBR = {
    "MIL": "AC米兰", "INT": "国际米兰", "JUV": "尤文图斯",
    "NAP": "那不勒斯", "LAZ": "拉齐奥", "ROM": "罗马", "ROMA": "罗马",
    "ATA": "亚特兰大", "FIO": "佛罗伦萨", "TOR": "都灵", "BOL": "博洛尼亚",
    "LEC": "莱切", "CAG": "卡利亚里", "UDI": "乌迪内斯",
    "VER": "维罗纳", "SAS": "萨索洛", "PAR": "帕尔马",
    "GEN": "热那亚", "CRE": "克雷莫内塞", "PIS": "比萨",
    "COMO": "科莫", "VEN": "威尼斯",
}

def get_name(abbr):
    return TEAM_ABBR.get(abbr, abbr)

# 查询意甲赛程
result = subprocess.run(
    ["/usr/bin/curl", "-s",
     "https://site.api.espn.com/apis/site/v2/sports/soccer/ita.1/teams/103/schedule?limit=5"],
    capture_output=True, text=True, timeout=15
)

data = json.loads(result.stdout)
events = data.get("events", [])

for e in events:
    date = e.get("date", "")[:10]
    if date != yesterday:
        continue

    short_name = e.get("shortName", "")
    comps = e.get("competitions", [{}])
    home = away = home_score = away_score = ""
    milan_won = False

    for c in comps:
        for comp in c.get("competitors", []):
            abbr = comp.get("team", {}).get("abbreviation", "")
            score = comp.get("score", {})
            score_val = score.get("displayValue", "?") if isinstance(score, dict) else str(score)
            winner = comp.get("score", {}).get("winner", False) if isinstance(comp.get("score"), dict) else False

            if comp.get("homeAway") == "home":
                home = get_name(abbr)
                home_score = score_val
            else:
                away = get_name(abbr)
                away_score = score_val

            if abbr == "MIL" and winner:
                milan_won = True

    result_str = "胜 ✅" if milan_won else ("平 🤝" if home_score == away_score else "负 ❌")
    print(f"⚽ AC米兰 {result_str}")
    print(f"比分：{home} {home_score} - {away_score} {away}")
    print(f"赛事：意甲联赛（Serie A）")
    break
