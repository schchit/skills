"""Unit tests for DAPAgent — core operations with mocked relay/registry."""

import json
import os
import tempfile
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from dap import (
    generate_keypair,
    derive_agent_id,
    MessageType,
    Payload,
    create_envelope,
    sign_envelope,
    create_conversation_id,
)
from dap.identity import _encode_key
from dap.crypto import (
    ed25519_to_x25519_private,
    ed25519_to_x25519_public,
    x25519_key_exchange,
    derive_session_key,
    encrypt_payload,
)

import base64

from dap_skill.agent import DAPAgent
from dap_skill.config import DAPConfig, AutonomyLevel
from dap_skill.store import DAPStore


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def agent_pair(tmp_dir):
    """Create two agents with configs pointing at test dirs."""
    config_a = DAPConfig(data_dir=os.path.join(tmp_dir, "a"), registry_url="http://test:8081")
    store_a = DAPStore(db_path=os.path.join(tmp_dir, "a", "agent.db"))
    agent_a = DAPAgent(config_a, store_a)

    config_b = DAPConfig(data_dir=os.path.join(tmp_dir, "b"), registry_url="http://test:8081")
    store_b = DAPStore(db_path=os.path.join(tmp_dir, "b", "agent.db"))
    agent_b = DAPAgent(config_b, store_b)

    return agent_a, agent_b


async def test_initialize(tmp_dir):
    config = DAPConfig(data_dir=os.path.join(tmp_dir, "agent"))
    store = DAPStore(db_path=os.path.join(tmp_dir, "agent", "agent.db"))
    agent = DAPAgent(config, store)

    desc = await agent.initialize("TestBot")

    assert desc["name"] == "TestBot"
    assert desc["agent_id"].startswith("dap:")
    assert agent.agent_id == desc["agent_id"]
    assert agent.public_key is not None

    # Verify persistence
    assert store.load_agent_id() == agent.agent_id
    assert store.load_keypair() is not None
    assert store.load_recovery_keypair() is not None
    assert store.load_agent_description() == desc


async def test_initialize_with_description(tmp_dir):
    config = DAPConfig(data_dir=os.path.join(tmp_dir, "agent"))
    store = DAPStore(db_path=os.path.join(tmp_dir, "agent", "agent.db"))
    agent = DAPAgent(config, store)

    desc = await agent.initialize("ProfileBot", description="Into MMA and cooking.")

    assert desc["description"] == "Into MMA and cooking."


async def test_register_success(tmp_dir):
    config = DAPConfig(data_dir=os.path.join(tmp_dir, "agent"), registry_url="http://test:8081")
    store = DAPStore(db_path=os.path.join(tmp_dir, "agent", "agent.db"))
    agent = DAPAgent(config, store)
    await agent.initialize("RegBot")

    mock_response = MagicMock()
    mock_response.status_code = 201

    with patch("dap_skill.agent.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await agent.register(pow_difficulty=1)

    assert result is True


async def test_search(tmp_dir):
    config = DAPConfig(data_dir=os.path.join(tmp_dir, "agent"), registry_url="http://test:8081")
    store = DAPStore(db_path=os.path.join(tmp_dir, "agent", "agent.db"))
    agent = DAPAgent(config, store)
    await agent.initialize("SearchBot")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"agents": [{"agent_id": "dap:test", "name": "Found"}]}

    with patch("dap_skill.agent.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        results = await agent.search(q="mma")

    assert len(results) == 1
    assert results[0]["name"] == "Found"


async def test_connect_creates_envelope(agent_pair):
    agent_a, agent_b = agent_pair
    await agent_a.initialize("AgentA")
    await agent_b.initialize("AgentB")

    # Mock registry to return agent B's key
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"public_key": _encode_key(agent_b.public_key)}

    with patch("dap_skill.agent.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        env = await agent_a.connect(agent_b.agent_id, message="Hello!")

    assert env["from_id"] == agent_a.agent_id
    assert env["to_id"] == agent_b.agent_id
    assert env["encrypted_payload"] is not None
    assert env["signature"] is not None

    # Check connection stored as pending
    conn = agent_a.store.get_connection(agent_b.agent_id)
    assert conn["status"] == "pending_outbound"


async def test_process_incoming_connection_request(agent_pair):
    """Test that processing a connection_request returns ask_owner action."""
    agent_a, agent_b = agent_pair
    await agent_a.initialize("AgentA")
    await agent_b.initialize("AgentB")

    # Build a connection_request envelope from A to B
    pub_b_key = _encode_key(agent_b.public_key)

    # Agent A creates and encrypts envelope
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"public_key": _encode_key(agent_b.public_key)}

    with patch("dap_skill.agent.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        env_dict = await agent_a.connect(agent_b.agent_id, message="Let's connect!")

    # Now agent B processes the incoming envelope
    mock_resp2 = MagicMock()
    mock_resp2.status_code = 200
    mock_resp2.json.return_value = {"public_key": _encode_key(agent_a.public_key)}

    with patch("dap_skill.agent.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp2)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        result = await agent_b.process_incoming(env_dict)

    assert result["action"] == "ask_owner"
    assert result["from_agent_id"] == agent_a.agent_id
    assert result["message"] == "Let's connect!"


async def test_send_message_tier_limit(tmp_dir):
    config = DAPConfig(data_dir=os.path.join(tmp_dir, "agent"), max_disclosure_tier=2)
    store = DAPStore(db_path=os.path.join(tmp_dir, "agent", "agent.db"))
    agent = DAPAgent(config, store)
    await agent.initialize("TierBot")

    other_id = "dap:fake_id"
    store.save_connection(other_id, "connected", public_key=_encode_key(agent.public_key))

    with pytest.raises(ValueError, match="exceeds max"):
        await agent.send_message(other_id, "secret", tier=3)


async def test_send_message_no_connection(tmp_dir):
    config = DAPConfig(data_dir=os.path.join(tmp_dir, "agent"))
    store = DAPStore(db_path=os.path.join(tmp_dir, "agent", "agent.db"))
    agent = DAPAgent(config, store)
    await agent.initialize("NoConnBot")

    with pytest.raises(ValueError, match="No active connection"):
        await agent.send_message("dap:nobody", "hello")


async def test_auto_accept_autonomy(agent_pair):
    """Test AUTO_ACCEPT_NOTIFY returns auto_accepted."""
    agent_a, agent_b = agent_pair
    agent_b.config.autonomy = AutonomyLevel.AUTO_ACCEPT_NOTIFY

    await agent_a.initialize("AgentA")
    await agent_b.initialize("AgentB")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"public_key": _encode_key(agent_b.public_key)}

    with patch("dap_skill.agent.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client
        env_dict = await agent_a.connect(agent_b.agent_id, message="Hi")

    mock_resp2 = MagicMock()
    mock_resp2.status_code = 200
    mock_resp2.json.return_value = {"public_key": _encode_key(agent_a.public_key)}

    with patch("dap_skill.agent.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp2)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client
        result = await agent_b.process_incoming(env_dict)

    assert result["action"] == "auto_accepted"


async def test_connect_stamps_epoch(agent_pair):
    """connect() should stamp connection_epoch=1 on first connection."""
    agent_a, agent_b = agent_pair
    await agent_a.initialize("AgentA")
    await agent_b.initialize("AgentB")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"public_key": _encode_key(agent_b.public_key)}

    with patch("dap_skill.agent.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        env = await agent_a.connect(agent_b.agent_id, message="Hello!")

    assert env["connection_epoch"] == 1
    conn = agent_a.store.get_connection(agent_b.agent_id)
    assert conn["epoch"] == 1


async def test_reconnect_increments_epoch(agent_pair):
    """Reconnecting after a previous connection bumps epoch."""
    agent_a, agent_b = agent_pair
    await agent_a.initialize("AgentA")
    await agent_b.initialize("AgentB")

    # Simulate previous connection at epoch 2
    agent_a.store.save_connection(agent_b.agent_id, "connected", public_key=_encode_key(agent_b.public_key), epoch=2)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"public_key": _encode_key(agent_b.public_key)}

    with patch("dap_skill.agent.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        env = await agent_a.connect(agent_b.agent_id, message="Reconnecting!")

    assert env["connection_epoch"] == 3
    conn = agent_a.store.get_connection(agent_b.agent_id)
    assert conn["epoch"] == 3


async def test_higher_epoch_reconnect_auto_recovers(agent_pair):
    """Receiving CONNECTION_REQUEST at higher epoch auto-recovers."""
    agent_a, agent_b = agent_pair
    await agent_a.initialize("AgentA")
    await agent_b.initialize("AgentB")

    # B thinks it's connected at epoch 1
    agent_b.store.save_connection(agent_a.agent_id, "connected", public_key=_encode_key(agent_a.public_key), epoch=1)
    # A has a prior connection at epoch 1 (will reconnect at epoch 2)
    agent_a.store.save_connection(agent_b.agent_id, "connected", public_key=_encode_key(agent_b.public_key), epoch=1)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"public_key": _encode_key(agent_b.public_key)}

    with patch("dap_skill.agent.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        env_dict = await agent_a.connect(agent_b.agent_id, message="Reconnecting!")
        assert env_dict["connection_epoch"] == 2

    # B processes the epoch-2 request
    mock_resp2 = MagicMock()
    mock_resp2.status_code = 200
    mock_resp2.json.return_value = {"public_key": _encode_key(agent_a.public_key)}

    with patch("dap_skill.agent.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp2)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        result = await agent_b.process_incoming(env_dict)

    assert result["action"] == "auto_accepted"
    conn_b = agent_b.store.get_connection(agent_a.agent_id)
    assert conn_b["status"] == "connected"
    assert conn_b["epoch"] == 2


async def test_lower_epoch_returns_epoch_mismatch(agent_pair):
    """Receiving a message at lower epoch returns epoch_mismatch."""
    agent_a, agent_b = agent_pair
    await agent_a.initialize("AgentA")
    await agent_b.initialize("AgentB")

    # B is at epoch 3
    agent_b.store.save_connection(agent_a.agent_id, "connected", public_key=_encode_key(agent_a.public_key), epoch=3)
    # A is at epoch 1 (stale)
    agent_a.store.save_connection(agent_b.agent_id, "connected", public_key=_encode_key(agent_b.public_key), epoch=1)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"public_key": _encode_key(agent_b.public_key)}

    with patch("dap_skill.agent.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        env_dict = await agent_a.send_message(agent_b.agent_id, "old message", tier=1)
        assert env_dict["connection_epoch"] == 1

    mock_resp2 = MagicMock()
    mock_resp2.status_code = 200
    mock_resp2.json.return_value = {"public_key": _encode_key(agent_a.public_key)}

    with patch("dap_skill.agent.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp2)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        result = await agent_b.process_incoming(env_dict)

    assert result["action"] == "epoch_mismatch"
    assert result["local_epoch"] == 3
    assert result["message_epoch"] == 1
