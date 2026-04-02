"""Thin HTTP client for the DAP daemon API."""
import httpx


class DAPClient:
    """Connects to the local DAP daemon HTTP API."""

    def __init__(self, base_url: str = "http://127.0.0.1:9820"):
        self.base_url = base_url

    async def health(self) -> dict:
        async with httpx.AsyncClient() as c:
            resp = await c.get(f"{self.base_url}/health")
            resp.raise_for_status()
            return resp.json()

    async def whoami(self) -> dict:
        async with httpx.AsyncClient() as c:
            resp = await c.get(f"{self.base_url}/whoami")
            resp.raise_for_status()
            return resp.json()

    async def init(self, name: str, description: str = "") -> dict:
        async with httpx.AsyncClient(timeout=60.0) as c:
            resp = await c.post(f"{self.base_url}/init", json={"name": name, "description": description})
            resp.raise_for_status()
            return resp.json()

    async def update_profile(self, description: str) -> dict:
        async with httpx.AsyncClient(timeout=60.0) as c:
            resp = await c.post(f"{self.base_url}/profile", json={"description": description})
            resp.raise_for_status()
            return resp.json()

    async def search(self, q: str) -> list[dict]:
        async with httpx.AsyncClient() as c:
            resp = await c.get(f"{self.base_url}/search", params={"q": q})
            resp.raise_for_status()
            return resp.json()["agents"]

    async def connect(self, to: str, message: str = "") -> dict:
        async with httpx.AsyncClient() as c:
            resp = await c.post(f"{self.base_url}/connect", json={"to": to, "message": message})
            resp.raise_for_status()
            return resp.json()

    async def accept(self, agent_id: str) -> dict:
        async with httpx.AsyncClient() as c:
            resp = await c.post(f"{self.base_url}/connections/{agent_id}/accept")
            resp.raise_for_status()
            return resp.json()

    async def decline(self, agent_id: str) -> dict:
        async with httpx.AsyncClient() as c:
            resp = await c.post(f"{self.base_url}/connections/{agent_id}/decline")
            resp.raise_for_status()
            return resp.json()

    async def send(self, to: str, content: str, tier: int = 1) -> dict:
        async with httpx.AsyncClient() as c:
            resp = await c.post(f"{self.base_url}/send", json={"to": to, "content": content, "tier": tier})
            resp.raise_for_status()
            return resp.json()

    async def messages(self, from_agent: str | None = None) -> list[dict]:
        async with httpx.AsyncClient() as c:
            params = {"from": from_agent} if from_agent else {}
            resp = await c.get(f"{self.base_url}/messages", params=params)
            resp.raise_for_status()
            return resp.json()["messages"]

    async def connections(self) -> list[dict]:
        async with httpx.AsyncClient() as c:
            resp = await c.get(f"{self.base_url}/connections")
            resp.raise_for_status()
            return resp.json()["connections"]
