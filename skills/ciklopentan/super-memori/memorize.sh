#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
from super_memori_common import LEARNINGS_DIR, QUEUE_DIR, VALID_LEARNING_TYPES, MAX_LEARNING_CHARS, ensure_dirs, now_iso


def main() -> int:
    p = argparse.ArgumentParser(description="Record a useful learning entry")
    p.add_argument("text")
    p.add_argument("type", nargs="?", default="lesson")
    p.add_argument("--pending", action="store_true")
    p.add_argument("--reviewed", action="store_true")
    p.add_argument("--tags", default="")
    p.add_argument("--source", default="agent")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.type not in VALID_LEARNING_TYPES:
        print(f"invalid learning type: {args.type}", file=sys.stderr)
        return 4

    ensure_dirs()
    LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)
    day = time.strftime("%Y-%m-%d")
    target = LEARNINGS_DIR / f"{day}.md"
    status = "reviewed" if args.reviewed else "pending"
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    text = args.text.strip()
    truncated = False
    if len(text) > MAX_LEARNING_CHARS:
        text = text[:MAX_LEARNING_CHARS].rstrip() + "\n[truncated]"
        truncated = True

    if target.exists():
        existing = target.read_text(encoding="utf-8", errors="ignore")
        if text.casefold() in existing.casefold():
            payload = {"status": "duplicate", "file": str(target), "type": args.type, "review_status": status}
            print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else f"duplicate skipped: {target}")
            return 0
    else:
        target.write_text(f"# Learnings — {day}\n\n", encoding="utf-8")

    block = (
        f"## {args.type} — {now_iso()}\n"
        f"- status: {status}\n"
        f"- source: {args.source}\n"
        f"- tags: {', '.join(tags) if tags else 'none'}\n\n"
        f"{text}\n\n"
    )
    with target.open("a", encoding="utf-8") as f:
        f.write(block)

    queue_item = QUEUE_DIR / f"learn-{int(time.time())}.json"
    queue_item.write_text(json.dumps({
        "kind": "learning",
        "file": str(target),
        "type": args.type,
        "review_status": status,
        "source": args.source,
        "tags": tags,
        "created_at": now_iso(),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    payload = {"status": "written", "file": str(target), "queue_item": str(queue_item), "type": args.type, "review_status": status, "truncated": truncated}
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else f"written: {target}\nqueued: {queue_item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
