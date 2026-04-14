"""Batch queue for Pro tier KG extraction via Modal.

Captures text chunks locally, flushes to Modal's batch endpoint periodically.
"""
import json
import os
import time
from pathlib import Path
from typing import Optional


def get_queue_dir() -> Path:
    """Queue directory for pending extractions."""
    d = Path(os.environ.get("REWIND_DATA_DIR", str(Path.home() / ".rewind"))) / "queue"
    d.mkdir(parents=True, exist_ok=True)
    return d


def enqueue(text: str, source: str = "claude-code", metadata: Optional[dict] = None):
    """Add text to the extraction queue."""
    queue_dir = get_queue_dir()
    entry = {
        "text": text[:2000],
        "source": source,
        "metadata": metadata or {},
        "queued_at": time.time(),
    }
    import uuid
    filename = f"{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}.json"
    (queue_dir / filename).write_text(json.dumps(entry))


def flush_queue(
    api_url: str,
    auth_token: str,
    max_batch: int = 50,
) -> dict:
    """Flush queued items to Modal batch extraction endpoint.

    Returns {"extracted": N, "nodes": N, "edges": N, "errors": N}
    """
    import httpx

    queue_dir = get_queue_dir()
    files = sorted(queue_dir.glob("*.json"))[:max_batch]

    if not files:
        return {"extracted": 0, "nodes": 0, "edges": 0, "errors": 0}

    # Load queued texts
    texts = []
    entries = []
    for f in files:
        try:
            entry = json.loads(f.read_text())
            texts.append(entry["text"])
            entries.append({"file": f, "entry": entry})
        except (json.JSONDecodeError, KeyError):
            f.unlink()  # corrupt entry

    if not texts:
        return {"extracted": 0, "nodes": 0, "edges": 0, "errors": 0}

    # Call Modal batch endpoint
    try:
        resp = httpx.post(
            api_url,
            json={"auth_token": auth_token, "texts": texts},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return {"extracted": 0, "nodes": 0, "edges": 0, "errors": len(texts), "error": str(e)}

    # Process results
    results = data.get("results", [])
    total_nodes = 0
    total_edges = 0

    # Write results to local graph
    for i, result in enumerate(results):
        nodes = result.get("nodes", [])
        edges = result.get("edges", [])
        total_nodes += len(nodes)
        total_edges += len(edges)

        # Store extracted graph locally via rewind CLI
        if nodes or edges:
            graph_data = json.dumps({"nodes": nodes, "edges": edges})
            source = entries[i]["entry"].get("source", "claude-code")
            try:
                import subprocess
                subprocess.run(
                    ["rewind", "graph", "import", "--json", graph_data, "--source", source],
                    capture_output=True, text=True, timeout=10,
                )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

    # Clean up processed queue files
    for entry in entries[:len(results)]:
        entry["file"].unlink(missing_ok=True)

    return {
        "extracted": len(results),
        "nodes": total_nodes,
        "edges": total_edges,
        "errors": max(0, len(texts) - len(results)),
    }


def queue_size() -> int:
    """Number of items waiting in the queue."""
    return len(list(get_queue_dir().glob("*.json")))
