#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
from super_memori_common import DB_PATH, LEARNINGS_DIR, MEMORY_DIR, QUEUE_DIR, canonical_memory_files, qdrant_collection_info, qdrant_ok, read_state, semantic_dependencies_available


def main() -> int:
    p = argparse.ArgumentParser(description="Check health of super_memori")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    state = read_state()
    deps = semantic_dependencies_available()
    checks = []

    checks.append({"name": "memory_dir", "ok": MEMORY_DIR.exists(), "detail": str(MEMORY_DIR)})
    checks.append({"name": "canonical_files", "ok": len(canonical_memory_files()) > 0, "detail": len(canonical_memory_files())})

    db_ok = False
    db_err = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        db_ok = True
    except Exception as e:
        db_err = str(e)
    checks.append({"name": "lexical_db", "ok": db_ok, "detail": db_err or str(DB_PATH)})

    qdrant_ready = qdrant_ok()
    qdrant_info = qdrant_collection_info() if qdrant_ready else None
    checks.append({"name": "qdrant", "ok": qdrant_ready, "detail": "reachable" if qdrant_ready else "unreachable"})
    checks.append({"name": "qdrant_collection", "ok": bool(qdrant_info), "detail": qdrant_info.get('points_count') if qdrant_info else None})
    checks.append({"name": "semantic_dependencies", "ok": all(deps.values()), "detail": deps})

    queue_count = len(list(QUEUE_DIR.glob("*.json"))) if QUEUE_DIR.exists() else 0
    checks.append({"name": "queue_backlog", "ok": queue_count < 500, "detail": queue_count})

    lexical_fresh = bool(state.get("lexical_last_indexed_at"))
    checks.append({"name": "lexical_freshness", "ok": lexical_fresh, "detail": state.get("lexical_last_indexed_at")})

    warnings = []
    if not qdrant_ready or not all(deps.values()):
        warnings.append("semantic layer degraded or unavailable")
    elif qdrant_info and int(qdrant_info.get('indexed_vectors_count', 0) or 0) == 0:
        warnings.append("semantic backend reachable but no indexed vectors reported")
    if not lexical_fresh:
        warnings.append("lexical index has not been built yet")
    if queue_count:
        warnings.append(f"queue backlog present: {queue_count}")

    overall = "OK"
    if any(not c["ok"] for c in checks if c["name"] in {"memory_dir", "canonical_files", "lexical_db"}):
        overall = "FAIL"
    elif warnings:
        overall = "WARN"

    payload = {"status": overall, "warnings": warnings, "checks": checks}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"status: {overall}")
        for c in checks:
            print(f"- {c['name']}: {'ok' if c['ok'] else 'fail'} ({c['detail']})")
        if warnings:
            print("warnings:")
            for w in warnings:
                print(f"- {w}")
    return 0 if overall == "OK" else 2 if overall == "WARN" else 3


if __name__ == "__main__":
    raise SystemExit(main())
