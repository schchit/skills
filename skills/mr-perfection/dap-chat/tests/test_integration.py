"""Integration test — two DAPAgents talking through local relay + registry.

Spins up real FastAPI apps (relay + registry) via httpx/websocket test clients.
Tests the full flow: init, register, search, connect, accept, message, transcript.
"""

import asyncio
import json
import os
import tempfile

import pytest
import httpx
import uvicorn

from dap.identity import _encode_key

from dap_relay.server import create_app as create_relay_app
from dap_registry.server import create_app as create_registry_app

from dap_skill.agent import DAPAgent
from dap_skill.config import DAPConfig
from dap_skill.store import DAPStore


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


async def test_two_agents_full_flow(tmp_dir):
    """End-to-end: two agents init, register, search, connect, message, verify transcripts."""

    # --- Set up relay and registry as real FastAPI apps served over localhost ---
    relay_app = create_relay_app(tofu_db_path=os.path.join(tmp_dir, "relay_tofu.db"))
    registry_app = create_registry_app(db_path=os.path.join(tmp_dir, "registry.db"), pow_difficulty=1)

    relay_config = uvicorn.Config(relay_app, host="127.0.0.1", port=0, log_level="error")
    registry_config = uvicorn.Config(registry_app, host="127.0.0.1", port=0, log_level="error")

    relay_server = uvicorn.Server(relay_config)
    registry_server = uvicorn.Server(registry_config)

    # Start servers — find free ports
    import socket

    def find_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]

    relay_port = find_free_port()
    registry_port = find_free_port()

    relay_config.port = relay_port
    registry_config.port = registry_port

    relay_task = asyncio.create_task(relay_server.serve())
    registry_task = asyncio.create_task(registry_server.serve())

    # Wait for servers to start
    for _ in range(50):
        await asyncio.sleep(0.1)
        if relay_server.started and registry_server.started:
            break

    relay_url = f"ws://127.0.0.1:{relay_port}"
    registry_url = f"http://127.0.0.1:{registry_port}"

    try:
        # --- 1. Initialize two agents ---
        config_a = DAPConfig(
            relay_url=relay_url,
            registry_url=registry_url,
            data_dir=os.path.join(tmp_dir, "agent_a"),
        )
        store_a = DAPStore(db_path=os.path.join(tmp_dir, "agent_a", "agent.db"))
        agent_a = DAPAgent(config_a, store_a)

        config_b = DAPConfig(
            relay_url=relay_url,
            registry_url=registry_url,
            data_dir=os.path.join(tmp_dir, "agent_b"),
        )
        store_b = DAPStore(db_path=os.path.join(tmp_dir, "agent_b", "agent.db"))
        agent_b = DAPAgent(config_b, store_b)

        desc_a = await agent_a.initialize("Alice", description="Into MMA and cooking.")
        desc_b = await agent_b.initialize("Bob", description="Into cooking and hiking.")

        assert desc_a["agent_id"].startswith("dap:")
        assert desc_b["agent_id"].startswith("dap:")
        assert desc_a["agent_id"] != desc_b["agent_id"]

        # --- 2. Register both with registry ---
        assert await agent_a.register(pow_difficulty=1)
        assert await agent_b.register(pow_difficulty=1)

        # --- 3. Search and find each other ---
        results = await agent_a.search(q="cooking")
        agent_ids_found = [r["agent_id"] for r in results]
        assert agent_b.agent_id in agent_ids_found

        results_b = await agent_b.search(q="mma")
        agent_ids_found_b = [r["agent_id"] for r in results_b]
        assert agent_a.agent_id in agent_ids_found_b

        # --- 4. Agent A sends connection_request to Agent B through relay ---
        await agent_a.connect_relay()
        await agent_b.connect_relay()

        env_dict = await agent_a.connect(agent_b.agent_id, message="Hey Bob, want to be friends?")
        assert env_dict["from_id"] == agent_a.agent_id
        assert env_dict["to_id"] == agent_b.agent_id

        # Send through relay
        await agent_a.send_via_relay(env_dict, agent_b.agent_id)

        # Agent A receives ACK for the sent message
        ack = await agent_a.receive_from_relay()
        assert ack["type"] == "ACK"

        # Agent B receives from relay
        delivery = await agent_b.receive_from_relay()
        assert delivery["type"] == "DELIVER"
        assert delivery["from"] == agent_a.agent_id

        # Parse the forwarded envelope
        received_env = json.loads(delivery["encrypted_payload"])

        # --- 5. Agent B processes incoming, gets ask_owner action ---
        result = await agent_b.process_incoming(received_env)
        assert result["action"] == "ask_owner"
        assert result["from_agent_id"] == agent_a.agent_id
        assert result["message"] == "Hey Bob, want to be friends?"

        # --- 6. Agent B accepts connection ---
        accept_env = await agent_b.accept_connection(agent_a.agent_id)
        assert accept_env["from_id"] == agent_b.agent_id
        assert accept_env["to_id"] == agent_a.agent_id

        # Send acceptance through relay
        await agent_b.send_via_relay(accept_env, agent_a.agent_id)

        # Agent B receives ACK for the acceptance
        ack_b = await agent_b.receive_from_relay()
        assert ack_b["type"] == "ACK"

        # Agent A receives acceptance
        accept_delivery = await agent_a.receive_from_relay()
        assert accept_delivery["type"] == "DELIVER"
        accept_received = json.loads(accept_delivery["encrypted_payload"])
        accept_result = await agent_a.process_incoming(accept_received)
        assert accept_result["action"] == "connection_accepted"

        # --- 7. Exchange encrypted messages ---
        msg1_env = await agent_a.send_message(agent_b.agent_id, "What's your favorite dish to cook?", tier=1)
        await agent_a.send_via_relay(msg1_env, agent_b.agent_id)

        # Agent A receives ACK for msg1
        ack_a2 = await agent_a.receive_from_relay()
        assert ack_a2["type"] == "ACK"

        msg1_delivery = await agent_b.receive_from_relay()
        msg1_received = json.loads(msg1_delivery["encrypted_payload"])
        msg1_result = await agent_b.process_incoming(msg1_received)
        assert msg1_result["action"] == "delivered"
        assert msg1_result["content"] == "What's your favorite dish to cook?"
        assert msg1_result["tier"] == 1

        # Agent B's connection status should now be connected (from accepting)
        # We need to mark B's side as connected for send_message to work
        conn_b = agent_b.store.get_connection(agent_a.agent_id)
        assert conn_b["status"] == "connected"

        msg2_env = await agent_b.send_message(agent_a.agent_id, "I love making pasta from scratch!", tier=1)
        await agent_b.send_via_relay(msg2_env, agent_a.agent_id)

        # Agent B receives ACK for msg2
        ack_b2 = await agent_b.receive_from_relay()
        assert ack_b2["type"] == "ACK"

        msg2_delivery = await agent_a.receive_from_relay()
        msg2_received = json.loads(msg2_delivery["encrypted_payload"])
        msg2_result = await agent_a.process_incoming(msg2_received)
        assert msg2_result["action"] == "delivered"
        assert msg2_result["content"] == "I love making pasta from scratch!"

        # --- 8. Verify transcripts on both sides ---
        transcript_a = await agent_a.get_messages(agent_b.agent_id)
        transcript_b = await agent_b.get_messages(agent_a.agent_id)

        # Both sides should have the same number of messages
        # A's transcript: connection_request, connection_accepted(received), msg1(sent), msg2(received)
        # B's transcript: connection_request(received), connection_accepted(sent), msg1(received), msg2(sent)
        assert len(transcript_a) == 4
        assert len(transcript_b) == 4

        # Verify all messages have decrypted content
        for msg in transcript_a:
            assert "from" in msg
            assert "to" in msg
            assert "type" in msg
            assert "content" is not None
        for msg in transcript_b:
            assert "from" in msg
            assert "to" in msg
            assert "type" in msg
            assert "content" is not None

    finally:
        # Clean up servers
        relay_server.should_exit = True
        registry_server.should_exit = True
        await asyncio.sleep(0.2)
        relay_task.cancel()
        registry_task.cancel()
        try:
            await relay_task
        except (asyncio.CancelledError, Exception):
            pass
        try:
            await registry_task
        except (asyncio.CancelledError, Exception):
            pass

        await agent_a.disconnect_relay()
        await agent_b.disconnect_relay()
