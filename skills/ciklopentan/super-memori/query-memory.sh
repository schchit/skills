#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
from super_memori_common import grep_fallback, lexical_search, qdrant_ok, read_state, semantic_dependencies_available


def main() -> int:
    p = argparse.ArgumentParser(description="Query local memory")
    p.add_argument("query")
    p.add_argument("--mode", default="auto", choices=["auto", "exact", "semantic", "hybrid", "recent", "learning"])
    p.add_argument("--type", dest="memory_type", default="all", choices=["episodic", "semantic", "procedural", "learning", "buffer", "all"])
    p.add_argument("--json", action="store_true")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--from", dest="date_from")
    p.add_argument("--to", dest="date_to")
    p.add_argument("--tags")
    p.add_argument("--reviewed-only", action="store_true")
    args = p.parse_args()

    warnings = []
    state = read_state()
    deps = semantic_dependencies_available()
    semantic_ready = qdrant_ok() and deps["sentence_transformers"] and deps["numpy"]

    if not semantic_ready:
        warnings.append("semantic layer unavailable; lexical-only mode active")

    mode_used = args.mode
    if args.mode == "auto":
        mode_used = "hybrid" if semantic_ready else "exact"
    elif args.mode in {"semantic", "hybrid", "learning"} and not semantic_ready:
        warnings.append(f"requested mode '{args.mode}' degraded to lexical search")
        mode_used = "exact"

    lexical_results = []
    if mode_used in {"exact", "hybrid", "recent", "learning"}:
        try:
            lexical_results = lexical_search(args.query, memory_type=("learning" if args.mode == "learning" else args.memory_type), limit=args.limit)
        except Exception as e:
            warnings.append(f"lexical index unavailable: {e}")

    if not lexical_results:
        fallback_type = "learning" if args.mode == "learning" else args.memory_type
        lexical_results = grep_fallback(args.query, memory_type=fallback_type, limit=args.limit)
        if lexical_results:
            warnings.append("using grep fallback")

    degraded = bool(warnings)
    payload = {
        "query": args.query,
        "mode_requested": args.mode,
        "mode_used": mode_used,
        "degraded": degraded,
        "warnings": warnings,
        "index_fresh": bool(state.get("lexical_last_indexed_at")),
        "results": lexical_results[: args.limit],
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"mode_requested: {payload['mode_requested']}")
        print(f"mode_used: {payload['mode_used']}")
        print(f"degraded: {str(payload['degraded']).lower()}")
        if warnings:
            print("warnings:")
            for w in warnings:
                print(f"- {w}")
        print("results:")
        for idx, item in enumerate(payload["results"], 1):
            print(f"{idx}. [{item.get('memory_type','unknown')}] {item.get('source_path','?')}")
            print(f"   {item.get('snippet','').strip()}")

    if payload["results"]:
        return 2 if degraded else 0
    return 1 if not degraded else 2


if __name__ == "__main__":
    raise SystemExit(main())
