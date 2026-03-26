#!/usr/bin/env python3
"""
List xStocks tokens on Solana from api.xstocks.fi (mainnet).

Uses a local cache at /tmp/xstocks.json for the full catalog and only displays
tokens that have a Solana deployment. Supports:
- name/symbol filtering
- listing Solana mint addresses
- reverse lookup by mint (via --lookup-address)
"""

import json
import sys
import urllib.error

# Allow running as python3 scripts/list_xstocks.py from repo root (path has scripts/)
# or as python3 list_xstocks.py from scripts/ (path has .)
if __name__ == "__main__":
    import os

    _script_dir = os.path.dirname(os.path.abspath(__file__))
    if _script_dir not in sys.path:
        sys.path.insert(0, _script_dir)

import argparse

from xstocks import (
    find_token_by_solana_address,
    get_catalog,
)
from xstocks.tokens import filter_tokens, format_names, get_solana_addresses

_debug = False


def log(msg: str, level: str = "info") -> None:
    """Log to stderr: always for level 'error'; otherwise only when --debug is set."""
    if _debug or level == "error":
        print(f'{{"level":"{level}","message":"{msg}"}}', file=sys.stderr, flush=True)


def _only_solana(tokens):
    """Return only tokens that have at least one Solana deployment."""
    filtered = []
    for t in tokens:
        for dep in t.get("deployments") or []:
            if str(dep.get("network", "")).lower() == "solana":
                filtered.append(t)
                break
    return filtered


def main() -> None:
    parser = argparse.ArgumentParser(description="List xStocks tokens on Solana")
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Output single-line JSON (default: pretty-print)",
    )
    parser.add_argument(
        "--names",
        action="store_true",
        help='Print one line per token: "Name [SYMBOL]" instead of JSON',
    )
    parser.add_argument(
        "--filter",
        metavar="TEXT",
        help="Case-insensitive substring filter on name or symbol",
    )
    parser.add_argument(
        "--solana-address-only",
        action="store_true",
        help="With --filter, print only Solana deployment addresses (one per line)",
    )
    parser.add_argument(
        "--lookup-address",
        metavar="MINT",
        help="Given a Solana token address, print the matching xStock name/symbol",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Emit structured logs to stderr",
    )
    args = parser.parse_args()
    global _debug
    _debug = args.debug
    pretty = not args.compact

    log("Loading xStocks token catalog (cache first)")
    try:
        all_nodes = get_catalog(refresh=False)
    except (urllib.error.URLError, json.JSONDecodeError, RuntimeError) as e:
        log(f"Failed to load catalog: {e}", "error")
        sys.exit(1)

    # Restrict to tokens that have a Solana deployment
    sol_tokens = _only_solana(all_nodes)
    log(f"Catalog has {len(all_nodes)} tokens; {len(sol_tokens)} with Solana deployments")

    if args.lookup_address:
        # For lookup, we still rely on Solana deployments, but we want to search
        # the full catalog to avoid accidental misses if cache changed.
        token = find_token_by_solana_address(all_nodes, args.lookup_address)
        if not token:
            log(
                "Address not found in cache; refreshing catalog from API for lookup",
                "info",
            )
            try:
                all_nodes = get_catalog(refresh=True)
            except (urllib.error.URLError, json.JSONDecodeError, RuntimeError) as e:
                log(f"Failed to refresh catalog for lookup: {e}", "error")
                sys.exit(1)
            token = find_token_by_solana_address(all_nodes, args.lookup_address)
        if not token:
            log("No xStock found for the given Solana address", "error")
            sys.exit(1)
        name = str(token.get("name", "")).strip()
        symbol = str(token.get("symbol", "")).strip()
        out = {"mint": args.lookup_address, "name": name, "symbol": symbol, "id": token.get("id")}
        # Human-friendly by default; use --compact to get raw JSON
        if pretty:
            print(f"{name} [{symbol}] (mint: {args.lookup_address})")
        else:
            json.dump(out, sys.stdout, separators=(",", ":"))
            print()
        return

    tokens = _only_solana(filter_tokens(sol_tokens, args.filter or ""))
    if args.filter:
        log(f'Filter "{args.filter}" matched {len(tokens)} Solana xStocks')

    if args.solana_address_only:
        if not args.filter:
            log("--solana-address-only requires --filter", "error")
            sys.exit(1)
        sol_addrs = get_solana_addresses(tokens)
        if not sol_addrs:
            log("No Solana deployment found for the given filter", "error")
            sys.exit(1)
        log(f"Found {len(sol_addrs)} Solana deployment address(es)")
        for addr in sol_addrs:
            print(addr)
        return

    if args.names:
        for line in format_names(tokens):
            print(line)
        return

    log(f"Returning {len(tokens)} Solana xStocks")
    if pretty:
        json.dump(tokens, sys.stdout, indent=2)
    else:
        json.dump(tokens, sys.stdout, separators=(",", ":"))
    print(file=sys.stdout)


if __name__ == "__main__":
    main()

