#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Iterable, Optional

WORKSPACE = Path(os.environ.get("OPENCLAW_WORKSPACE", str(Path.home() / ".openclaw/workspace"))).expanduser()
SKILL_DIR = Path(__file__).resolve().parent.parent
MEMORY_DIR = WORKSPACE / "memory"
LEARNINGS_DIR = WORKSPACE / ".learnings"
INDEX_STATE_DIR = MEMORY_DIR / "index-state"
QUEUE_DIR = MEMORY_DIR / "queue"
DB_PATH = INDEX_STATE_DIR / "memory.db"
STATE_JSON = INDEX_STATE_DIR / "state.json"
QDRANT_URL = os.environ.get("SUPER_MEMORI_QDRANT_URL", "http://127.0.0.1:6333")
QDRANT_COLLECTION = os.environ.get("SUPER_MEMORI_QDRANT_COLLECTION", "memories")
EMBED_MODEL = os.environ.get("SUPER_MEMORI_EMBED_MODEL", "intfloat/multilingual-e5-small")

MEMORY_TYPES = ["episodic", "semantic", "procedural", "learning", "buffer"]
VALID_LEARNING_TYPES = {"error", "correction", "lesson", "insight"}
MAX_LEARNING_CHARS = 4000
CHUNK_TARGET_CHARS = 1200
CHUNK_OVERLAP_CHARS = 150


def ensure_dirs() -> None:
    INDEX_STATE_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    (QUEUE_DIR / "processed").mkdir(parents=True, exist_ok=True)
    LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)


def now_ts() -> float:
    return time.time()


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def read_state() -> dict:
    ensure_dirs()
    if STATE_JSON.exists():
        try:
            return json.loads(STATE_JSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def write_state(state: dict) -> None:
    ensure_dirs()
    tmp = STATE_JSON.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(STATE_JSON)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_memory_files() -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    if MEMORY_DIR.exists():
        for mem_type in ["episodic", "semantic", "procedural"]:
            d = MEMORY_DIR / mem_type
            if d.exists():
                for path in sorted(d.rglob("*.md")):
                    files.append((mem_type, path))
        buffer = MEMORY_DIR / "working-buffer.md"
        if buffer.exists():
            files.append(("buffer", buffer))
    if LEARNINGS_DIR.exists():
        for path in sorted(LEARNINGS_DIR.rglob("*.md")):
            files.append(("learning", path))
    memory_md = WORKSPACE / "MEMORY.md"
    if memory_md.exists():
        files.append(("semantic", memory_md))
    return files


def strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].lstrip("\n")
    return text


def chunk_text(text: str, chunk_size: int = CHUNK_TARGET_CHARS, overlap: int = CHUNK_OVERLAP_CHARS) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def ensure_db() -> sqlite3.Connection:
    ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS entries (
          entry_id TEXT PRIMARY KEY,
          source_path TEXT NOT NULL UNIQUE,
          memory_type TEXT NOT NULL,
          content_hash TEXT NOT NULL,
          tags_json TEXT NOT NULL DEFAULT '[]',
          created_at TEXT,
          updated_at TEXT,
          indexed_at TEXT NOT NULL,
          reviewed INTEGER NOT NULL DEFAULT 1,
          importance INTEGER NOT NULL DEFAULT 3,
          namespace TEXT NOT NULL DEFAULT 'default'
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
          chunk_id TEXT PRIMARY KEY,
          entry_id TEXT NOT NULL,
          chunk_index INTEGER NOT NULL,
          text TEXT NOT NULL,
          token_estimate INTEGER NOT NULL,
          char_count INTEGER NOT NULL,
          FOREIGN KEY(entry_id) REFERENCES entries(entry_id) ON DELETE CASCADE
        )
        """
    )
    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
          chunk_id UNINDEXED,
          text,
          content=''
        )
        """
    )
    conn.commit()
    return conn


def extract_tags(text: str) -> list[str]:
    for line in text.splitlines()[:5]:
        if line.lower().startswith("#tags:"):
            tags = line.split(":", 1)[1]
            return [t.strip() for t in tags.split(",") if t.strip()]
    return []


def rebuild_lexical_index(full: bool = False) -> dict:
    conn = ensure_db()
    changed = 0
    seen_paths = set()
    for mem_type, path in canonical_memory_files():
        seen_paths.add(str(path))
        raw = path.read_text(encoding="utf-8", errors="ignore")
        text = strip_frontmatter(raw)
        content_hash = sha256_text(text)
        row = conn.execute("SELECT entry_id, content_hash FROM entries WHERE source_path = ?", (str(path),)).fetchone()
        if row and row["content_hash"] == content_hash and not full:
            continue
        entry_id = row["entry_id"] if row else sha256_text(str(path))
        conn.execute("DELETE FROM chunks_fts WHERE chunk_id IN (SELECT chunk_id FROM chunks WHERE entry_id = ?)", (entry_id,))
        conn.execute("DELETE FROM chunks WHERE entry_id = ?", (entry_id,))
        conn.execute(
            """
            INSERT INTO entries(entry_id, source_path, memory_type, content_hash, tags_json, created_at, updated_at, indexed_at, reviewed, importance, namespace)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(entry_id) DO UPDATE SET
              source_path=excluded.source_path,
              memory_type=excluded.memory_type,
              content_hash=excluded.content_hash,
              tags_json=excluded.tags_json,
              updated_at=excluded.updated_at,
              indexed_at=excluded.indexed_at
            """,
            (
                entry_id,
                str(path),
                mem_type,
                content_hash,
                json.dumps(extract_tags(raw), ensure_ascii=False),
                time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(path.stat().st_ctime)),
                time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(path.stat().st_mtime)),
                now_iso(),
                1,
                3,
                "default",
            ),
        )
        chunks = chunk_text(text)
        for idx, chunk in enumerate(chunks):
            chunk_id = sha256_text(f"{entry_id}:{idx}:{chunk[:80]}")
            conn.execute(
                "INSERT INTO chunks(chunk_id, entry_id, chunk_index, text, token_estimate, char_count) VALUES(?, ?, ?, ?, ?, ?)",
                (chunk_id, entry_id, idx, chunk, max(1, len(chunk) // 4), len(chunk)),
            )
            conn.execute("INSERT INTO chunks_fts(chunk_id, text) VALUES(?, ?)", (chunk_id, chunk))
        changed += 1
    missing = conn.execute("SELECT source_path, entry_id FROM entries").fetchall()
    for row in missing:
        if row["source_path"] not in seen_paths:
            conn.execute("DELETE FROM chunks_fts WHERE chunk_id IN (SELECT chunk_id FROM chunks WHERE entry_id = ?)", (row["entry_id"],))
            conn.execute("DELETE FROM chunks WHERE entry_id = ?", (row["entry_id"],))
            conn.execute("DELETE FROM entries WHERE entry_id = ?", (row["entry_id"],))
    conn.commit()
    state = read_state()
    state["lexical_last_indexed_at"] = now_iso()
    state["lexical_entries"] = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    state["lexical_chunks"] = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    state["canonical_files_count"] = len(canonical_memory_files())
    write_state(state)
    return {
        "changed_entries": changed,
        "entries": state["lexical_entries"],
        "chunks": state["lexical_chunks"],
        "indexed_at": state["lexical_last_indexed_at"],
    }


def qdrant_ok() -> bool:
    try:
        with urllib.request.urlopen(f"{QDRANT_URL}/collections", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def qdrant_collection_info() -> Optional[dict]:
    try:
        with urllib.request.urlopen(f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}", timeout=3) as r:
            if r.status != 200:
                return None
            data = json.loads(r.read().decode("utf-8", "ignore"))
            return data.get("result")
    except Exception:
        return None


def semantic_dependencies_available() -> dict:
    import importlib.util
    return {
        "sentence_transformers": bool(importlib.util.find_spec("sentence_transformers")),
        "numpy": bool(importlib.util.find_spec("numpy")),
    }


def lexical_search(query: str, memory_type: str = "all", limit: int = 5) -> list[dict]:
    conn = ensure_db()
    terms = [t.strip() for t in query.replace('"', ' ').split() if t.strip()]
    if not terms:
        return []
    fts_query = " OR ".join(f'"{term}"' for term in terms)
    params: list[object] = []
    sql = """
    SELECT e.source_path, e.memory_type, e.updated_at, c.chunk_id, c.text AS snippet,
           bm25(chunks_fts) AS rank
    FROM chunks_fts
    JOIN chunks c ON c.rowid = chunks_fts.rowid
    JOIN entries e ON e.entry_id = c.entry_id
    WHERE chunks_fts MATCH ?
    """
    params.append(fts_query)
    if memory_type != "all":
        sql += " AND e.memory_type = ?"
        params.append(memory_type)
    sql += " ORDER BY rank LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, tuple(params)).fetchall()
    results = []
    for row in rows:
        item = dict(row)
        snippet = (item.get("snippet") or "").strip().replace("\n", " ")
        item["snippet"] = snippet[:280] + ("..." if len(snippet) > 280 else "")
        results.append(item)
    return results


def grep_fallback(query: str, memory_type: str = "all", limit: int = 5) -> list[dict]:
    search_paths: list[Path] = []
    if memory_type == "all":
        search_paths = [MEMORY_DIR / "episodic", MEMORY_DIR / "semantic", MEMORY_DIR / "procedural", LEARNINGS_DIR]
        if (MEMORY_DIR / "working-buffer.md").exists():
            search_paths.append(MEMORY_DIR / "working-buffer.md")
        if (WORKSPACE / "MEMORY.md").exists():
            search_paths.append(WORKSPACE / "MEMORY.md")
    elif memory_type == "learning":
        search_paths = [LEARNINGS_DIR]
    elif memory_type == "buffer":
        search_paths = [MEMORY_DIR / "working-buffer.md"]
    else:
        search_paths = [MEMORY_DIR / memory_type]

    results = []
    query_lc = query.casefold()
    for path in search_paths:
        if not path.exists():
            continue
        file_iter = [path] if path.is_file() else sorted(path.rglob("*.md"))
        for file_path in file_iter:
            try:
                for lineno, line in enumerate(file_path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                    if query_lc in line.casefold():
                        results.append({
                            "source_path": str(file_path),
                            "memory_type": memory_type,
                            "chunk_id": f"grep:{file_path}:{lineno}",
                            "snippet": line.strip(),
                            "updated_at": None,
                            "rank": None,
                        })
                        break
            except Exception:
                continue
            if len(results) >= limit:
                return results
    return results
