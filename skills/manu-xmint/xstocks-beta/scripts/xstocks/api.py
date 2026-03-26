"""Fetch xStocks token list from the API. Supports dependency injection for tests."""

import json
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, List, Optional

BASE_URL = "https://api.xstocks.fi/api/v1/token"


def fetch_page(
    page: int,
    base_url: str = BASE_URL,
    fetcher: Optional[Callable[[int], Dict[str, Any]]] = None,
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Get one page of tokens.
    If fetcher is provided, call fetcher(page) and return the result (for tests).
    Otherwise perform an HTTP GET to base_url (no query params).
    """
    if fetcher is not None:
        return fetcher(page)

    url = base_url
    req = urllib.request.Request(url, method="GET")
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "xstocks-lobster-skill/1.0")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Unexpected status {resp.status} from {url}")
        return json.loads(resp.read().decode())


def fetch_all_pages(
    base_url: str = BASE_URL,
    fetcher: Optional[Callable[[int], Dict[str, Any]]] = None,
    timeout: int = 30,
) -> List[Dict[str, Any]]:
    """
    Fetch all pages and return a single list of token nodes.
    Pagination continues until page.hasNextPage is false.
    """
    all_nodes: List[Dict[str, Any]] = []
    page_num = 0

    while True:
        data = fetch_page(page_num, base_url=base_url, fetcher=fetcher, timeout=timeout)
        nodes = data.get("nodes") or []
        all_nodes.extend(nodes)
        page_info = data.get("page") or {}
        if not page_info.get("hasNextPage", False):
            break
        page_num += 1

    return all_nodes
