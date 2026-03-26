#!/usr/bin/env python3
"""
List xStocks tokens held by a Solana wallet.

Given a wallet public key, this script:
- Queries Solana mainnet RPC for parsed SPL token accounts
- Extracts token mints and balances
- Uses the xStocks catalog (with /tmp/xstocks.json cache) to attach name/symbol

Stdout: JSON array of portfolio entries, or human-readable lines with --names.
Stderr: logs when --debug.
"""

import json
import sys
import urllib.error
import urllib.request

if __name__ == "__main__":
    import os

    _script_dir = os.path.dirname(os.path.abspath(__file__))
    if _script_dir not in sys.path:
        sys.path.insert(0, _script_dir)

import argparse
from typing import Any, Dict, List

from xstocks import find_token_by_solana_address, get_catalog

_debug = False
SOLANA_RPC = "https://api.mainnet-beta.solana.com"


def log(msg: str, level: str = "info") -> None:
    """Log to stderr: always for level 'error'; otherwise only when --debug is set."""
    if _debug or level == "error":
        print(f'{{"level":"{level}","message":"{msg}"}}', file=sys.stderr, flush=True)


def _rpc_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(SOLANA_RPC, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "xstocks-wallet-tokens/1.0")
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Unexpected status {resp.status} from {SOLANA_RPC}")
        return json.loads(resp.read().decode())


def fetch_parsed_token_accounts(owner: str) -> List[Dict[str, Any]]:
    """Fetch parsed token accounts from both Token Program and Token-2022 Program."""
    programs = [
        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",   # Standard SPL
        "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"    # Token-2022 (used by xStocks, many RWAs, etc.)
    ]
    
    all_accounts = []
    
    for program_id in programs:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                owner,
                {"programId": program_id},
                {"encoding": "jsonParsed", "commitment": "confirmed"},
            ],
        }
        data = _rpc_request(payload)
        if "error" in data:
            raise RuntimeError(f"RPC error for program {program_id}: {data['error']}")
        
        result = data.get("result") or {}
        accounts = result.get("value") or []
        all_accounts.extend(accounts)
    
    return all_accounts


def build_portfolio(owner: str) -> List[Dict[str, Any]]:
    """Return a portfolio of xStocks held by the wallet."""
    log(f"Fetching parsed token accounts for wallet {owner}")
    accounts = fetch_parsed_token_accounts(owner)
    log(f"Found {len(accounts)} token accounts")

    # Load catalog (cache first)
    log("Loading xStocks token catalog (cache first)")
    catalog = get_catalog(refresh=False)

    portfolio: List[Dict[str, Any]] = []
    seen_mints: Dict[str, Dict[str, Any]] = {}

    for acc in accounts:
        account = acc.get("account") or {}
        data = account.get("data") or {}
        parsed = data.get("parsed") or {}
        info = parsed.get("info") or {}
        token_address = info.get("mint")
        token_amount = info.get("tokenAmount") or {}
        ui_amount = token_amount.get("uiAmount", 0)
        if not token_address:
            continue
        # Skip zero-balance accounts
        try:
            if float(ui_amount) == 0.0:
                continue
        except (TypeError, ValueError):
            continue

        if token_address in seen_mints:
            # Aggregate balances if multiple accounts for same mint
            try:
                seen_mints[token_address]["amount"] += float(ui_amount)
            except (TypeError, ValueError):
                pass
            continue

        token = find_token_by_solana_address(catalog, token_address)
        if not token:
            # Try refreshing catalog once if this mint isn't known
            log(
                f"Mint {token_address} not found in cache; refreshing catalog from API",
                "info",
            )
            catalog = get_catalog(refresh=True)
            token = find_token_by_solana_address(catalog, token_address)

        name = str(token.get("name", "")).strip() if token else ""
        symbol = str(token.get("symbol", "")).strip() if token else ""

        # If we still don't have a known xStock (no name), skip this mint entirely.
        if not name:
            log(f"Skipping non-xStock mint {token_address}", "info")
            continue

        entry = {
            "wallet": owner,
            "mint": token_address,
            "amount": float(ui_amount),
            "name": name,
            "symbol": symbol,
        }
        seen_mints[token_address] = entry

    portfolio = list(seen_mints.values())
    log(f"Portfolio entries: {len(portfolio)}")
    return portfolio


def main() -> None:
    parser = argparse.ArgumentParser(
        description="List xStocks tokens held by a Solana wallet"
    )
    parser.add_argument(
        "wallet",
        help="Solana wallet public key (base58)",
    )
    parser.add_argument(
        "--names",
        action="store_true",
        help="Print human-readable lines instead of JSON",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Emit structured logs to stderr",
    )
    args = parser.parse_args()
    global _debug
    _debug = args.debug

    try:
        portfolio = build_portfolio(args.wallet)
    except (urllib.error.URLError, json.JSONDecodeError, RuntimeError) as e:
        log(str(e), "error")
        sys.exit(1)

    if args.names:
        if len(portfolio) == 0:
            print(f"No xStocks available on wallet {args.wallet}")
            return
        for entry in portfolio:
            name = entry.get("name") or ""
            symbol = entry.get("symbol") or ""
            mint = entry.get("mint") or ""
            amount = entry.get("amount") or 0
            print(f"{name} [{symbol}] — {amount} (mint: {mint})")
        return

    json.dump(portfolio, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()

