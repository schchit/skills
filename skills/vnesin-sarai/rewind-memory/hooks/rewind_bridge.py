"""Bridge between Claude Code hooks and Rewind Memory.

Handles config loading, data dir resolution, and calling the rewind CLI/library.
"""
import json
import os
import subprocess
from pathlib import Path


def get_data_dir() -> Path:
    """Resolve Rewind data directory."""
    # Check env var first
    if d := os.environ.get("REWIND_DATA_DIR"):
        return Path(d)
    # Check project-level .rewind/
    cwd = Path.cwd()
    if (cwd / ".rewind").exists():
        return cwd / ".rewind"
    # Default: ~/.rewind/
    return Path.home() / ".rewind"


def get_config() -> dict:
    """Load Rewind config from data dir."""
    data_dir = get_data_dir()
    config_file = data_dir / "config.yaml"
    if config_file.exists():
        try:
            import yaml
            return yaml.safe_load(config_file.read_text()) or {}
        except ImportError:
            pass
    return {}


REWIND_API_URL = os.environ.get("REWIND_API_URL", "http://localhost:8031")


def rewind_search(query: str, top_k: int = 5) -> list[dict]:
    """Search Rewind memory via HybridRAG API (all layers L0-L6).

    Primary: calls the HybridRAG orchestrator which fuses results from
    L0 (BM25), L1 (core files), L3 (Neo4j KG), L4 (vector ANN),
    L5 (Qdrant), and L6 (doc store) via Reciprocal Rank Fusion.

    Fallback: if HybridRAG is unreachable, falls back to the rewind CLI.
    """
    try:
        import urllib.request
        import urllib.parse
        params = urllib.parse.urlencode({"q": query, "limit": top_k})
        url = f"{REWIND_API_URL}/search?{params}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data.get("results", data if isinstance(data, list) else [])
    except Exception:
        pass
    # Fallback to CLI if API unreachable
    try:
        result = subprocess.run(
            ["rewind", "search", query, "--limit", str(top_k), "--json"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return []


def rewind_store(text: str, source: str = "claude-code", metadata: dict | None = None) -> bool:
    """Store a memory chunk via Rewind."""
    try:
        cmd = ["rewind", "remember", text]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def rewind_ingest_file(path: str) -> dict:
    """Ingest a file into Rewind memory."""
    try:
        result = subprocess.run(
            ["rewind", "ingest", path],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return {}
