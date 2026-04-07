#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
from super_memori_common import DB_PATH, QDRANT_COLLECTION, QUEUE_DIR, ensure_db, qdrant_ok, rebuild_lexical_index, read_state, semantic_dependencies_available, write_state


def main() -> int:
    p = argparse.ArgumentParser(description="Maintain super_memori indexes")
    p.add_argument("--incremental", action="store_true")
    p.add_argument("--full", action="store_true")
    p.add_argument("--rebuild-fts", action="store_true")
    p.add_argument("--rebuild-vectors", action="store_true")
    p.add_argument("--stats", action="store_true")
    p.add_argument("--vacuum", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    state = read_state()
    payload = {"actions": [], "warnings": []}

    if args.stats:
        conn = ensure_db()
        payload["lexical_entries"] = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        payload["lexical_chunks"] = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        payload["db_path"] = str(DB_PATH)
        payload["state"] = state
        payload["semantic_ready"] = qdrant_ok() and all(semantic_dependencies_available().values())
    else:
        if args.full or args.incremental or args.rebuild_fts or not any([args.full, args.incremental, args.rebuild_fts, args.rebuild_vectors, args.vacuum]):
            stats = rebuild_lexical_index(full=bool(args.full or args.rebuild_fts))
            payload["actions"].append({"lexical_index": stats})
        queue_processed = 0
        queue_errors = 0
        processed_dir = QUEUE_DIR / 'processed'
        processed_dir.mkdir(parents=True, exist_ok=True)
        if QUEUE_DIR.exists():
            for item in sorted(QUEUE_DIR.glob('*.json')):
                try:
                    data = json.loads(item.read_text(encoding='utf-8'))
                    target = processed_dir / item.name
                    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
                    item.unlink()
                    queue_processed += 1
                except Exception:
                    queue_errors += 1
            if queue_processed:
                payload["actions"].append({"queue_processed": queue_processed})
            if queue_errors:
                payload["warnings"].append(f"queue items with processing errors: {queue_errors}")
        if args.rebuild_vectors:
            state["semantic_last_requested_rebuild"] = __import__('time').strftime('%Y-%m-%dT%H:%M:%S%z')
            write_state(state)
            if not qdrant_ok():
                payload["warnings"].append("qdrant unavailable; semantic rebuild not executed")
            if not all(semantic_dependencies_available().values()):
                payload["warnings"].append("semantic dependencies missing; semantic rebuild not executed")
            payload["actions"].append({"semantic_rebuild": "requested"})
        if args.vacuum:
            conn = ensure_db()
            conn.execute("VACUUM")
            payload["actions"].append({"vacuum": "done"})

    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
