import os
import tempfile
from dap_skill.store import DAPStore


def test_save_connection_with_epoch():
    with tempfile.TemporaryDirectory() as d:
        store = DAPStore(db_path=os.path.join(d, "agent.db"))
        store.save_connection("dap:test", "connected", public_key="abc", epoch=3)
        conn = store.get_connection("dap:test")
        assert conn["epoch"] == 3


def test_connection_epoch_defaults_to_1():
    with tempfile.TemporaryDirectory() as d:
        store = DAPStore(db_path=os.path.join(d, "agent.db"))
        store.save_connection("dap:test", "connected", public_key="abc")
        conn = store.get_connection("dap:test")
        assert conn["epoch"] == 1


def test_list_connections_includes_epoch():
    with tempfile.TemporaryDirectory() as d:
        store = DAPStore(db_path=os.path.join(d, "agent.db"))
        store.save_connection("dap:a", "connected", public_key="abc", epoch=2)
        store.save_connection("dap:b", "pending_outbound", public_key="def", epoch=5)
        conns = store.list_connections()
        epochs = {c["agent_id"]: c["epoch"] for c in conns}
        assert epochs == {"dap:a": 2, "dap:b": 5}
