#!/usr/bin/env python3
"""Budget skill - AI handles all logic via SKILL.md"""
import os, json
SKILL_DIR = os.path.expanduser("~/.openclaw/skills/budget")
DATA_DIR = os.path.expanduser("~/Documents/02_Personal/01_Budget")

def read(path):
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    return {} if "budget" in path or "goals" in path else []

def write(path, data):
    with open(path, 'w') as f: json.dump(data, f, indent=2)

def path(file, month=""):
    m = month.replace("-","")
    return {
        "budget": f"{DATA_DIR}/data/budget_{m}.json",
        "expense": f"{DATA_DIR}/data/expense_{m}.json",
        "goals": f"{DATA_DIR}/data/goals.json",
        "pools": f"{DATA_DIR}/config/pools.json",
        "config": f"{DATA_DIR}/config/config.json",
    }[file]

if __name__ == "__main__":
    print("按SKILL.md规则处理：记账/预算/查询/存钱目标")
