#!/usr/bin/env python3
"""skills-audit/scripts/skills_watch_and_notify.py

面向“开箱即用”的 skills 目录监控脚本（增量 / 无变化不发 / 低 token）。

策略：
- 本地做增量：复用 skills_audit.py 的 state.json 做 diff。
- 无变化不发：目录没变化就不输出任何内容（供 cron 的 noOutputNoDelivery 使用）。
- 阈值合并：建议由 cron 频率控制；默认每分钟跑一次即为“每分钟汇总一次”。
- 模型只做异常/需要解释时介入：本脚本不调用模型，只输出结构化变化列表。

输出：
- 有变化：输出若干行纯文本（新增/变更/删除）。
- 无变化：不输出。

依赖：
- 同目录下的 skills_audit.py
- 产生/更新：~/.openclaw/skills-audit/logs.ndjson 与 state.json

用法：
  python3 skills/skills-audit/scripts/skills_watch_and_notify.py \
    --workspace /root/.openclaw/workspace

说明：
- 本脚本“只负责产生消息文本”，真正的发送由 OpenClaw cron 的 delivery 完成。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def run(argv: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(argv, capture_output=True, text=True)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


def load_recent_risks(logs_path: Path) -> dict[str, str]:
    risk_by_slug: dict[str, str] = {}
    if not logs_path.exists():
        return risk_by_slug

    try:
        lines = logs_path.read_text("utf-8").splitlines()
    except Exception:
        return risk_by_slug

    for line in reversed(lines[-1000:]):
        try:
            rec: dict[str, Any] = json.loads(line)
        except Exception:
            continue
        slug = str(rec.get("slug") or "").strip()
        if not slug or slug in risk_by_slug:
            continue
        risk = rec.get("risk") or {}
        level = str((risk or {}).get("level") or "unknown").strip().lower() or "unknown"
        risk_by_slug[slug] = level

    return risk_by_slug


def risk_label(level: str) -> str:
    mapping = {
        "low": "🟢 低",
        "medium": "🟢 中",
        "high": "🟡 高",
        "extreme": "🔴 极高",
        "unknown": "⚪ 未知",
    }
    return mapping.get(level, f"⚪ {level or '未知'}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", default="/root/.openclaw/workspace")
    ap.add_argument("--who", default="cron")
    ap.add_argument("--channel", default="local")
    args = ap.parse_args()

    workspace = Path(args.workspace).resolve()
    audit_py = workspace / "skills" / "skills-audit" / "scripts" / "skills_audit.py"

    rc, out, err = run([
        sys.executable,
        str(audit_py),
        "scan",
        "--workspace",
        str(workspace),
        "--who",
        args.who,
        "--channel",
        args.channel,
    ])
    if rc != 0:
        # 失败时也不要刷屏到微信（由 cron 平台/运维自行看日志）
        print(err or out, file=sys.stderr)
        return rc

    # skills_audit.py 最后一行会输出 JSON summary
    try:
        summary = json.loads(out.splitlines()[-1]) if out else {}
    except Exception:
        summary = {}

    skills_dir = workspace / "skills"

    def is_real_skill(name: str) -> bool:
        d = skills_dir / name
        try:
            return (d / "_meta.json").is_file() or (d / "SKILL.md").is_file()
        except Exception:
            return False

    added = [x for x in (summary.get("added") or []) if is_real_skill(x)]
    changed = [x for x in (summary.get("changed") or []) if is_real_skill(x)]

    # Important: use the diff returned by skills_audit.py directly.
    # Do NOT re-read updated state.json here, otherwise this round's add/change/remove
    # can be swallowed after scan updates the baseline.
    removed_raw = summary.get("removed") or []
    removed = [x for x in removed_raw if x not in {"skills"}]

    if not (added or changed or removed):
        return 0

    import datetime as dt

    skills_dir = workspace / "skills"
    logs_path = Path("/root/.openclaw/skills-audit/logs.ndjson")
    now_bj = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).replace(microsecond=0)
    recent_risks = load_recent_risks(logs_path)

    def fmt_skill_list(items: list[str]) -> list[str]:
        rows: list[str] = []
        for x in items[:200]:
            level = recent_risks.get(x, "unknown")
            rows.append(f"• {x}｜风险等级：{risk_label(level)}")
        return rows

    def append_section(lines: list[str], title: str, items: list[str]) -> None:
        if not items:
            return
        lines.append(f"【{title}】")
        lines.extend(fmt_skill_list(items))
        lines.append("")

    lines: list[str] = []
    lines.append("【Skills 监控提醒】")
    lines.append("检测到 skills 目录发生变更")
    lines.append("")

    append_section(lines, "新增", added)
    append_section(lines, "变更", changed)
    append_section(lines, "删除", removed)

    lines.append(f"📁 路径：{skills_dir}")
    lines.append(f"🕒 时间：{now_bj.strftime('%Y-%m-%d %H:%M:%S')} (Asia/Shanghai)")
    lines.append(f"🧾 审计日志：{logs_path}")

    # Trim trailing blank line
    while lines and lines[-1] == "":
        lines.pop()

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
