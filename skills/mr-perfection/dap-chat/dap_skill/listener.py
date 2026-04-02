"""Persistent background WebSocket relay listener for incoming DAP messages."""

import asyncio
import json
import logging
from typing import Any, Awaitable, Callable

import websockets
from nacl.signing import SigningKey, VerifyKey

from dap.identity import sign_message

logger = logging.getLogger(__name__)


def _encode_key(key: VerifyKey) -> str:
    import base64
    return base64.urlsafe_b64encode(bytes(key)).rstrip(b"=").decode()


def _encode_sig(sig: bytes) -> str:
    import base64
    return base64.urlsafe_b64encode(sig).rstrip(b"=").decode()


class RelayListener:
    """Maintains a persistent WebSocket connection to the relay, receiving messages.

    On DELIVER messages, invokes the provided callback with the parsed data dict.
    Automatically reconnects with exponential backoff on disconnection.
    """

    MAX_BACKOFF = 30.0
    INITIAL_BACKOFF = 1.0

    def __init__(
        self,
        private_key: SigningKey,
        public_key: VerifyKey,
        agent_id: str,
        relay_url: str,
        on_message: Callable[[dict[str, Any]], Awaitable[Any]],
    ):
        self._private_key = private_key
        self._public_key = public_key
        self._agent_id = agent_id
        self._relay_url = relay_url
        self._on_message = on_message
        self._task: asyncio.Task | None = None
        self._ws = None
        self._running = False
        self._backoff = self.INITIAL_BACKOFF

    @property
    def running(self) -> bool:
        return self._running

    async def start(self) -> None:
        """Start the background listener task."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())

    async def send(self, message: dict) -> None:
        """Send a JSON message through the active WebSocket connection."""
        if not self._ws:
            logger.warning("Cannot send — not connected to relay")
            return
        await self._ws.send(json.dumps(message))

    async def stop(self) -> None:
        """Stop the background listener and close the WebSocket."""
        self._running = False
        if self._ws:
            await self._ws.close()
            self._ws = None
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _authenticate(self, ws) -> bool:
        """Perform REGISTER -> CHALLENGE -> PROVE -> REGISTERED handshake."""
        await ws.send(json.dumps({
            "type": "REGISTER",
            "agent_id": self._agent_id,
            "public_key": _encode_key(self._public_key),
        }))
        challenge = json.loads(await ws.recv())
        if challenge.get("type") != "CHALLENGE":
            logger.error("Relay auth: expected CHALLENGE, got %s", challenge)
            return False

        nonce = challenge["nonce"]
        sig = sign_message(self._private_key, nonce.encode())
        await ws.send(json.dumps({
            "type": "PROVE",
            "agent_id": self._agent_id,
            "signature": _encode_sig(sig),
        }))
        result = json.loads(await ws.recv())
        if result.get("type") != "REGISTERED":
            logger.error("Relay auth: expected REGISTERED, got %s", result)
            return False

        return True

    async def _run_loop(self) -> None:
        """Main loop: connect, authenticate, listen; reconnect on failure."""
        while self._running:
            try:
                ws_url = self._relay_url.replace("http://", "ws://").replace("https://", "wss://")
                if not ws_url.endswith("/ws"):
                    ws_url += "/ws"

                async with websockets.connect(ws_url) as ws:
                    self._ws = ws
                    if not await self._authenticate(ws):
                        logger.warning("Authentication failed, will retry")
                        await self._wait_backoff()
                        continue

                    # Successfully connected — reset backoff
                    self._backoff = self.INITIAL_BACKOFF
                    logger.info("Relay listener connected for %s", self._agent_id)

                    # Listen loop
                    async for raw in ws:
                        if not self._running:
                            break
                        try:
                            data = json.loads(raw)
                            if data.get("type") == "DELIVER":
                                await self._on_message(data)
                        except json.JSONDecodeError:
                            logger.warning("Non-JSON message from relay: %s", raw[:200])
                        except Exception:
                            logger.exception("Error processing incoming message")

                # Connection ended cleanly — treat as disconnect and backoff
                if self._running:
                    logger.info("Relay connection closed, reconnecting in %.1fs", self._backoff)
                    await self._wait_backoff()

            except asyncio.CancelledError:
                break
            except Exception:
                if not self._running:
                    break
                logger.warning(
                    "Relay connection lost, reconnecting in %.1fs", self._backoff,
                    exc_info=True,
                )
                await self._wait_backoff()
            finally:
                self._ws = None

    async def _wait_backoff(self) -> None:
        """Sleep for current backoff duration, then increase it."""
        await asyncio.sleep(self._backoff)
        self._backoff = min(self._backoff * 2, self.MAX_BACKOFF)
