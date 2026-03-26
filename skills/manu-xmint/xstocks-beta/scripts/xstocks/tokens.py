"""Pure token filtering and formatting. No I/O."""

from typing import Any, Dict, List


def filter_tokens(tokens: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Return tokens whose name or symbol contains query (case-insensitive)."""
    if not query or not query.strip():
        return list(tokens)
    q = query.strip().lower()
    return [
        t
        for t in tokens
        if q in str(t.get("name", "")).lower() or q in str(t.get("symbol", "")).lower()
    ]


def get_solana_addresses(tokens: List[Dict[str, Any]]) -> List[str]:
    """
    Extract Solana deployment addresses from tokens.
    Addresses may be prefixed (e.g. 'svm:...'); they are returned as-is.
    """
    out: List[str] = []
    for t in tokens:
        for dep in t.get("deployments") or []:
            if str(dep.get("network", "")).lower() == "solana":
                addr = dep.get("address")
                if addr:
                    out.append(addr)
    return out


def format_names(tokens: List[Dict[str, Any]]) -> List[str]:
    """Return one line per token: 'Name [SYMBOL]' or just 'Name' if no symbol."""
    lines: List[str] = []
    for t in tokens:
        name = str(t.get("name", "")).strip()
        symbol = str(t.get("symbol", "")).strip()
        if symbol:
            lines.append(f"{name} [{symbol}]")
        else:
            lines.append(name)
    return lines


def find_token_by_solana_address(
    tokens: List[Dict[str, Any]], address: str
) -> Dict[str, Any]:
    """Return the first token whose Solana deployment address matches address.

    Comparison is case-sensitive on the full address string; callers should pass
    the exact mint string they are using (e.g. from wallet balances or swaps).
    Returns {} if no match is found.
    """
    if not address:
        return {}
    for t in tokens:
        for dep in t.get("deployments") or []:
            if str(dep.get("network", "")).lower() == "solana" and address in str(dep.get("address", "")):
                return t
    return {}

