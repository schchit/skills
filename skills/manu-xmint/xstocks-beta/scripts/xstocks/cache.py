"""Simple cache for xStocks catalog in /tmp/xstocks.json.

The cache is used to speed up lookups (especially reverse lookup by Solana
token address). It is only refreshed from the API when a lookup misses or
when callers explicitly request a refresh.
"""

import json
import os
from typing import Any, Dict, List

from .api import fetch_all_pages


DEFAULT_CACHE_PATH = "/tmp/xstocks.json"


def _cache_path() -> str:
    """Return cache path, overridable via XSTOCKS_CACHE_PATH for tests."""
    return os.environ.get("XSTOCKS_CACHE_PATH", DEFAULT_CACHE_PATH)


def load_cache() -> List[Dict[str, Any]]:
    """Load catalog from cache if present; return [] if missing or invalid."""
    path = _cache_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except FileNotFoundError:
        return []
    except (OSError, json.JSONDecodeError):
        return []
    return []


def save_cache(nodes: List[Dict[str, Any]]) -> None:
    """Persist catalog to cache path."""
    path = _cache_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(nodes, f)
    except OSError:
        # Caching failures should not break core behavior.
        return


def get_catalog(refresh: bool = False) -> List[Dict[str, Any]]:
    """Return full token catalog, using cache unless refresh is True.

    - If refresh is False, try to load from cache. If cache is empty or missing,
      fetch from API and save.
    - If refresh is True, always fetch from API and overwrite cache.
    """
    if not refresh:
        cached = load_cache()
        if cached:
            return cached
    nodes = fetch_all_pages()
    save_cache(nodes)
    return nodes

