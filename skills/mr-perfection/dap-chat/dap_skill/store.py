"""Local persistent storage for agent state — keypairs, connections, settings."""

import base64
import json
import os
import sqlite3

from nacl.signing import SigningKey, VerifyKey

CURRENT_SCHEMA_VERSION = 2

# Migrations: version N contains SQL to run when upgrading from N-1 to N
_MIGRATIONS = {
    2: [
        "ALTER TABLE connections ADD COLUMN epoch INTEGER NOT NULL DEFAULT 1",
    ],
}


class DAPStore:
    """SQLite-backed store for agent identity, connections, and pending requests."""

    def __init__(self, db_path: str = "dap_agent.db"):
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()
        self._migrate()

    def _create_tables(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS identity (
                key TEXT PRIMARY KEY,
                value BLOB NOT NULL
            );
            CREATE TABLE IF NOT EXISTS connections (
                agent_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                public_key TEXT,
                epoch INTEGER NOT NULL DEFAULT 1,
                metadata TEXT NOT NULL DEFAULT '{}'
            );
            CREATE TABLE IF NOT EXISTS pending_requests (
                from_agent_id TEXT PRIMARY KEY,
                envelope_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)
        self._conn.commit()

    def _get_schema_version(self) -> int:
        try:
            row = self._conn.execute(
                "SELECT value FROM identity WHERE key = 'schema_version'"
            ).fetchone()
            if row is None:
                return 0
            return int(row[0])
        except Exception:
            return 0

    def _set_schema_version(self, version: int):
        self._conn.execute(
            "INSERT OR REPLACE INTO identity (key, value) VALUES ('schema_version', ?)",
            (str(version).encode(),),
        )

    def _migrate(self):
        current = self._get_schema_version()
        if current >= CURRENT_SCHEMA_VERSION:
            return
        if current == 0:
            # Check if this is a fresh DB or an old one without schema_version.
            # Fresh DBs have 0 non-schema rows in identity; old DBs have keypairs etc.
            row = self._conn.execute(
                "SELECT COUNT(*) FROM identity WHERE key != 'schema_version'"
            ).fetchone()
            if row[0] == 0:
                # Fresh DB — tables already created with latest schema
                self._set_schema_version(CURRENT_SCHEMA_VERSION)
                self._conn.commit()
                return
            # Old DB — start migrations from version 1
            current = 1
        for version in range(current + 1, CURRENT_SCHEMA_VERSION + 1):
            for sql in _MIGRATIONS.get(version, []):
                try:
                    self._conn.execute(sql)
                except sqlite3.OperationalError:
                    pass  # e.g. column already exists
            self._set_schema_version(version)
        self._conn.commit()

    # --- Identity ---

    def save_keypair(self, private_key: SigningKey, public_key: VerifyKey):
        self._set("private_key", bytes(private_key))
        self._set("public_key", bytes(public_key))

    def save_recovery_keypair(self, private_key: SigningKey, public_key: VerifyKey):
        self._set("recovery_private_key", bytes(private_key))
        self._set("recovery_public_key", bytes(public_key))

    def load_keypair(self) -> tuple[SigningKey, VerifyKey] | None:
        priv = self._get("private_key")
        pub = self._get("public_key")
        if priv is None or pub is None:
            return None
        return SigningKey(priv), VerifyKey(pub)

    def load_recovery_keypair(self) -> tuple[SigningKey, VerifyKey] | None:
        priv = self._get("recovery_private_key")
        pub = self._get("recovery_public_key")
        if priv is None or pub is None:
            return None
        return SigningKey(priv), VerifyKey(pub)

    def save_agent_description(self, desc: dict):
        self._set("agent_description", json.dumps(desc).encode())

    def load_agent_description(self) -> dict | None:
        data = self._get("agent_description")
        if data is None:
            return None
        return json.loads(data)

    def save_agent_id(self, agent_id: str):
        self._set("agent_id", agent_id.encode())

    def load_agent_id(self) -> str | None:
        data = self._get("agent_id")
        if data is None:
            return None
        return data.decode()

    # --- Connections ---

    def save_connection(self, agent_id: str, status: str, public_key: str | None = None, epoch: int = 1, metadata: dict | None = None):
        self._conn.execute(
            "INSERT OR REPLACE INTO connections (agent_id, status, public_key, epoch, metadata) VALUES (?, ?, ?, ?, ?)",
            (agent_id, status, public_key, epoch, json.dumps(metadata or {})),
        )
        self._conn.commit()

    def get_connection(self, agent_id: str) -> dict | None:
        row = self._conn.execute("SELECT * FROM connections WHERE agent_id = ?", (agent_id,)).fetchone()
        if row is None:
            return None
        return {"agent_id": row["agent_id"], "status": row["status"], "public_key": row["public_key"], "epoch": row["epoch"], "metadata": json.loads(row["metadata"])}

    def list_connections(self, status: str | None = None) -> list[dict]:
        if status:
            rows = self._conn.execute("SELECT * FROM connections WHERE status = ?", (status,)).fetchall()
        else:
            rows = self._conn.execute("SELECT * FROM connections").fetchall()
        return [{"agent_id": r["agent_id"], "status": r["status"], "public_key": r["public_key"], "epoch": r["epoch"], "metadata": json.loads(r["metadata"])} for r in rows]

    def remove_connection(self, agent_id: str):
        self._conn.execute("DELETE FROM connections WHERE agent_id = ?", (agent_id,))
        self._conn.commit()

    # --- Pending requests ---

    def save_pending_request(self, from_agent_id: str, envelope_json: str):
        from datetime import datetime, timezone
        self._conn.execute(
            "INSERT OR REPLACE INTO pending_requests (from_agent_id, envelope_json, created_at) VALUES (?, ?, ?)",
            (from_agent_id, envelope_json, datetime.now(timezone.utc).isoformat()),
        )
        self._conn.commit()

    def get_pending_request(self, from_agent_id: str) -> dict | None:
        row = self._conn.execute("SELECT * FROM pending_requests WHERE from_agent_id = ?", (from_agent_id,)).fetchone()
        if row is None:
            return None
        return {"from_agent_id": row["from_agent_id"], "envelope_json": row["envelope_json"], "created_at": row["created_at"]}

    def list_pending_requests(self) -> list[dict]:
        rows = self._conn.execute("SELECT * FROM pending_requests ORDER BY created_at").fetchall()
        return [{"from_agent_id": r["from_agent_id"], "envelope_json": r["envelope_json"], "created_at": r["created_at"]} for r in rows]

    def remove_pending_request(self, from_agent_id: str):
        self._conn.execute("DELETE FROM pending_requests WHERE from_agent_id = ?", (from_agent_id,))
        self._conn.commit()

    # --- Internal helpers ---

    def _set(self, key: str, value: bytes):
        self._conn.execute("INSERT OR REPLACE INTO identity (key, value) VALUES (?, ?)", (key, value))
        self._conn.commit()

    def _get(self, key: str) -> bytes | None:
        row = self._conn.execute("SELECT value FROM identity WHERE key = ?", (key,)).fetchone()
        if row is None:
            return None
        return row["value"]
