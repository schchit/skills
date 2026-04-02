"""Test that schema migrations run correctly on old databases."""
import json
import os
import sqlite3
import tempfile

from dap_skill.store import DAPStore


def test_migrate_v1_to_v2_adds_epoch_column():
    """A v1 database (no epoch column) gets migrated to v2 on open."""
    with tempfile.TemporaryDirectory() as d:
        db_path = os.path.join(d, "agent.db")
        # Create a v1 database manually (no epoch column, no schema_version)
        conn = sqlite3.connect(db_path)
        conn.executescript("""
            CREATE TABLE identity (key TEXT PRIMARY KEY, value BLOB NOT NULL);
            CREATE TABLE connections (
                agent_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                public_key TEXT,
                metadata TEXT NOT NULL DEFAULT '{}'
            );
            CREATE TABLE pending_requests (
                from_agent_id TEXT PRIMARY KEY,
                envelope_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)
        # Insert a connection WITHOUT epoch column
        conn.execute(
            "INSERT INTO connections (agent_id, status, public_key, metadata) VALUES (?, ?, ?, ?)",
            ("dap:old", "connected", "key123", "{}"),
        )
        # Insert identity data to simulate an old DB that has been used
        conn.execute(
            "INSERT INTO identity (key, value) VALUES (?, ?)",
            ("agent_id", b"dap:old_agent"),
        )
        conn.commit()
        conn.close()

        # Open with DAPStore — should auto-migrate
        store = DAPStore(db_path=db_path)
        conn_record = store.get_connection("dap:old")
        assert conn_record is not None
        assert conn_record["epoch"] == 1
        assert conn_record["status"] == "connected"


def test_fresh_database_gets_current_schema_version():
    """A brand new database starts at the current schema version."""
    with tempfile.TemporaryDirectory() as d:
        db_path = os.path.join(d, "agent.db")
        store = DAPStore(db_path=db_path)
        store.save_connection("dap:test", "connected", public_key="abc", epoch=5)
        conn = store.get_connection("dap:test")
        assert conn["epoch"] == 5


def test_migration_is_idempotent():
    """Opening the store multiple times doesn't break anything."""
    with tempfile.TemporaryDirectory() as d:
        db_path = os.path.join(d, "agent.db")
        store1 = DAPStore(db_path=db_path)
        store1.save_connection("dap:test", "connected", public_key="abc", epoch=3)
        del store1

        store2 = DAPStore(db_path=db_path)
        conn = store2.get_connection("dap:test")
        assert conn["epoch"] == 3
