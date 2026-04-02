"""Tests for RelayListener — background WebSocket relay listening."""

import asyncio
import json
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from dap import generate_keypair, derive_agent_id
from dap.identity import sign_message, _encode_key
from dap.crypto import (
    ed25519_to_x25519_private,
    ed25519_to_x25519_public,
    x25519_key_exchange,
    derive_session_key,
    encrypt_payload,
)
from dap import (
    MessageType,
    Payload,
    create_envelope,
    sign_envelope,
    create_conversation_id,
)

import base64

from dap_skill.agent import DAPAgent
from dap_skill.config import DAPConfig, AutonomyLevel
from dap_skill.listener import RelayListener
from dap_skill.store import DAPStore


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def keypair():
    return generate_keypair()


class FakeWebSocket:
    """A fake websockets connection for testing the listener.

    Handles the REGISTER/CHALLENGE/PROVE/REGISTERED auth handshake
    automatically, then yields recv_messages one by one before raising
    to simulate disconnect.
    """

    def __init__(self, recv_messages: list[str] | None = None, fail_auth: bool = False):
        self._recv_messages = list(recv_messages or [])
        self._sent: list[str] = []
        self._closed = False
        self._fail_auth = fail_auth
        self._recv_index = 0
        self._pending_responses: list[str] = []

    async def send(self, data: str):
        self._sent.append(data)
        msg = json.loads(data)
        if msg["type"] == "REGISTER":
            self._pending_responses.append(
                json.dumps({"type": "CHALLENGE", "nonce": "test-nonce-123"})
            )
        elif msg["type"] == "PROVE":
            if self._fail_auth:
                self._pending_responses.append(
                    json.dumps({"type": "ERROR", "reason": "auth failed"})
                )
            else:
                self._pending_responses.append(
                    json.dumps({"type": "REGISTERED", "agent_id": msg["agent_id"]})
                )

    async def recv(self):
        # Return pending auth responses first
        if self._pending_responses:
            return self._pending_responses.pop(0)

        # Then deliver queued messages
        if self._recv_index < len(self._recv_messages):
            msg = self._recv_messages[self._recv_index]
            self._recv_index += 1
            return msg

        # Simulate disconnect
        raise Exception("connection closed")

    async def close(self):
        self._closed = True

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            msg = await self.recv()
            return msg
        except Exception:
            raise StopAsyncIteration

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()


def _make_listener(keypair_tuple, on_message=None, backoff=0.01):
    """Helper to create a RelayListener with tiny backoff for testing."""
    priv, pub = keypair_tuple
    agent_id = derive_agent_id(pub)

    async def noop_callback(data):
        pass

    listener = RelayListener(
        private_key=priv,
        public_key=pub,
        agent_id=agent_id,
        relay_url="http://localhost:8080",
        on_message=on_message or noop_callback,
    )
    listener._backoff = backoff
    listener.INITIAL_BACKOFF = backoff
    listener.MAX_BACKOFF = 0.05
    return listener, agent_id


async def test_listener_connects_and_authenticates(keypair):
    """Test that the listener connects, sends REGISTER, responds to CHALLENGE."""
    received = []

    async def on_message(data):
        received.append(data)

    listener, agent_id = _make_listener(keypair, on_message)
    fake_ws = FakeWebSocket(recv_messages=[])

    with patch("dap_skill.listener.websockets.connect", return_value=fake_ws):
        await listener.start()
        await asyncio.sleep(0.05)
        await listener.stop()

    # Verify REGISTER was sent
    sent_msgs = [json.loads(s) for s in fake_ws._sent]
    assert len(sent_msgs) >= 2
    assert sent_msgs[0]["type"] == "REGISTER"
    assert sent_msgs[0]["agent_id"] == agent_id
    assert sent_msgs[1]["type"] == "PROVE"
    assert sent_msgs[1]["agent_id"] == agent_id


async def test_listener_processes_deliver_message(keypair):
    """Test that incoming DELIVER messages trigger the callback."""
    received = []

    async def on_message(data):
        received.append(data)

    deliver_msg = json.dumps({
        "type": "DELIVER",
        "from": "dap:sender123",
        "encrypted_payload": "test-payload-data",
    })

    listener, agent_id = _make_listener(keypair, on_message)
    fake_ws = FakeWebSocket(recv_messages=[deliver_msg])

    with patch("dap_skill.listener.websockets.connect", return_value=fake_ws):
        await listener.start()
        await asyncio.sleep(0.05)
        await listener.stop()

    assert len(received) == 1
    assert received[0]["type"] == "DELIVER"
    assert received[0]["from"] == "dap:sender123"


async def test_listener_reconnects_on_disconnect(keypair):
    """Test that the listener reconnects after a disconnect."""
    connect_count = 0

    def make_fake_ws(*args, **kwargs):
        nonlocal connect_count
        connect_count += 1
        return FakeWebSocket(recv_messages=[])

    listener, agent_id = _make_listener(keypair, backoff=0.01)

    with patch("dap_skill.listener.websockets.connect", side_effect=make_fake_ws):
        await listener.start()
        await asyncio.sleep(0.15)
        await listener.stop()

    assert connect_count >= 2


async def test_listener_ignores_non_deliver_messages(keypair):
    """Test that non-DELIVER messages are silently ignored."""
    received = []

    async def on_message(data):
        received.append(data)

    error_msg = json.dumps({"type": "ERROR", "reason": "something"})
    deliver_msg = json.dumps({
        "type": "DELIVER",
        "from": "dap:sender",
        "encrypted_payload": "data",
    })

    listener, agent_id = _make_listener(keypair, on_message)
    fake_ws = FakeWebSocket(recv_messages=[error_msg, deliver_msg])

    with patch("dap_skill.listener.websockets.connect", return_value=fake_ws):
        await listener.start()
        await asyncio.sleep(0.05)
        await listener.stop()

    assert len(received) == 1
    assert received[0]["type"] == "DELIVER"


async def test_agent_start_stop_listening(tmp_dir):
    """Test DAPAgent.start_listening / stop_listening integration."""
    config = DAPConfig(data_dir=os.path.join(tmp_dir, "agent"), relay_url="http://localhost:8080")
    store = DAPStore(db_path=os.path.join(tmp_dir, "agent", "agent.db"))
    agent = DAPAgent(config, store)
    await agent.initialize("ListenerBot")

    fake_ws = FakeWebSocket(recv_messages=[])

    with patch("dap_skill.listener.websockets.connect", return_value=fake_ws):
        await agent.start_listening()
        assert agent._listener is not None
        assert agent._listener.running is True
        # Set small backoff so stop doesn't wait long
        agent._listener._backoff = 0.01
        agent._listener.INITIAL_BACKOFF = 0.01
        agent._listener.MAX_BACKOFF = 0.02

        await asyncio.sleep(0.05)
        await agent.stop_listening()
        assert agent._listener is None


async def test_agent_get_pending_messages(tmp_dir):
    """Test that get_pending_messages returns and clears queued messages."""
    config = DAPConfig(data_dir=os.path.join(tmp_dir, "agent"))
    store = DAPStore(db_path=os.path.join(tmp_dir, "agent", "agent.db"))
    agent = DAPAgent(config, store)
    await agent.initialize("PendingBot")

    agent._pending_messages.append({"action": "delivered", "from_agent_id": "dap:x", "content": "hi"})
    agent._pending_messages.append({"action": "delivered", "from_agent_id": "dap:y", "content": "yo"})

    msgs = agent.get_pending_messages()
    assert len(msgs) == 2
    assert msgs[0]["content"] == "hi"
    assert agent.get_pending_messages() == []


async def test_agent_on_message_received_end_to_end(tmp_dir):
    """Test the full flow: DELIVER -> parse envelope -> process_incoming -> pending."""
    config_a = DAPConfig(data_dir=os.path.join(tmp_dir, "a"), registry_url="http://test:8081")
    store_a = DAPStore(db_path=os.path.join(tmp_dir, "a", "agent.db"))
    agent_a = DAPAgent(config_a, store_a)
    await agent_a.initialize("SenderBot")

    config_b = DAPConfig(
        data_dir=os.path.join(tmp_dir, "b"),
        registry_url="http://test:8081",
        autonomy=AutonomyLevel.ASK_ALWAYS,
    )
    store_b = DAPStore(db_path=os.path.join(tmp_dir, "b", "agent.db"))
    agent_b = DAPAgent(config_b, store_b)
    await agent_b.initialize("ReceiverBot")

    # Agent A creates a connection_request envelope to agent B
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"public_key": _encode_key(agent_b.public_key)}

    with patch("dap_skill.agent.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client
        env_dict = await agent_a.connect(agent_b.agent_id, message="Hello from listener test!")

    # Simulate what the relay delivers
    deliver_data = {
        "type": "DELIVER",
        "from": agent_a.agent_id,
        "encrypted_payload": json.dumps(env_dict),
    }

    # Agent B processes the delivered message via the callback
    mock_resp2 = MagicMock()
    mock_resp2.status_code = 200
    mock_resp2.json.return_value = {"public_key": _encode_key(agent_a.public_key)}

    with patch("dap_skill.agent.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp2)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client
        await agent_b._on_message_received(deliver_data)

    pending = agent_b.get_pending_messages()
    assert len(pending) == 1
    assert pending[0]["action"] == "ask_owner"
    assert pending[0]["from_agent_id"] == agent_a.agent_id
    assert pending[0]["message"] == "Hello from listener test!"


async def test_listener_start_requires_initialization(tmp_dir):
    """Test that start_listening raises if agent not initialized."""
    config = DAPConfig(data_dir=os.path.join(tmp_dir, "agent"))
    store = DAPStore(db_path=os.path.join(tmp_dir, "agent", "agent.db"))
    agent = DAPAgent(config, store)

    with pytest.raises(RuntimeError, match="not initialized"):
        await agent.start_listening()
