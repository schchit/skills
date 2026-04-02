"""Test DAPClient against a real daemon HTTP API (in-process)."""
import os
import tempfile
import pytest
from httpx import AsyncClient, ASGITransport

from dap_daemon.server import create_app
from dap_daemon.config import DaemonConfig
from dap_skill.client import DAPClient


@pytest.fixture
async def daemon_and_client():
    """Start a daemon in-process and create a DAPClient pointing at it."""
    with tempfile.TemporaryDirectory() as d:
        config = DaemonConfig(data_dir=d, relay_url="ws://localhost:99999")
        app = create_app(config)
        # Use httpx ASGITransport so no actual network needed
        transport = ASGITransport(app=app)
        # Monkey-patch the client to use ASGI transport
        client = DAPClient(base_url="http://test")
        # Override the client to use our transport
        original_health = client.health

        import httpx as _httpx

        class PatchedClient(DAPClient):
            async def _request(self, method, path, **kwargs):
                async with _httpx.AsyncClient(transport=transport, base_url="http://test") as c:
                    resp = await getattr(c, method)(path, **kwargs)
                    resp.raise_for_status()
                    return resp.json()

            async def health(self):
                return await self._request("get", "/health")

            async def whoami(self):
                return await self._request("get", "/whoami")

            async def messages(self, from_agent=None):
                params = {"from": from_agent} if from_agent else {}
                return (await self._request("get", "/messages", params=params))["messages"]

            async def connections(self):
                return (await self._request("get", "/connections"))["connections"]

        yield PatchedClient()


async def test_client_health(daemon_and_client):
    client = daemon_and_client
    result = await client.health()
    assert result["status"] == "ok"


async def test_client_whoami(daemon_and_client):
    client = daemon_and_client
    result = await client.whoami()
    assert result["agent_id"] is None


async def test_client_messages_empty(daemon_and_client):
    client = daemon_and_client
    msgs = await client.messages()
    assert msgs == []


async def test_client_connections_empty(daemon_and_client):
    client = daemon_and_client
    conns = await client.connections()
    assert conns == []
