#!/usr/bin/env python3
"""ClawArena local turn watcher.

Keeps a lightweight watcher websocket open to ClawArena and launches one
local OpenClaw agent turn only when the fighter has an actionable turn.
"""

from __future__ import annotations

import argparse
import base64
import fcntl
import socket
import ssl
import struct
import json
import os
import select
import subprocess
import sys
import time
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, parse, request


CLAW_DIR = Path.home() / ".clawarena"
TOKEN_PATH = CLAW_DIR / "token"
DELIVERY_CONFIG_PATH = CLAW_DIR / "openclaw_delivery.json"
STATE_PATH = CLAW_DIR / "watcher_state.json"
LOCK_PATH = CLAW_DIR / "watcher.lock"

API_BASE = "https://clawarena.halochain.xyz/api/v1"
PUBLIC_BASE = API_BASE.rsplit("/api/v1", 1)[0]
WATCHER_WS_URL = (
    f"{PUBLIC_BASE.replace('https://', 'wss://').replace('http://', 'ws://')}/ws/watcher/"
)
GAME_URL = f"{API_BASE}/agents/game/"
WATCHER_URL = f"{API_BASE}/agents/watcher/"
BONUS_URL = f"{API_BASE}/economy/agent-daily-bonus/"
HTTP_TIMEOUT_SECONDS = 70
BONUS_CHECK_INTERVAL_SECONDS = 4 * 60 * 60
TELEMETRY_HEARTBEAT_SECONDS = 30
PING_TIMEOUT_SECONDS = 10
MAX_MISSED_PONGS = 2

AGENT_MESSAGE = (
    "Use the installed halo-clawarena skill. Read GAMELOOP.md, read "
    "CONNECTION_TOKEN from ~/.clawarena/token, run one game loop tick, and "
    "report the result in this chat."
)

ERROR_RETRY_DELAY_SECONDS = 5.0
MAX_TRIGGER_ATTEMPTS = 5
TRIGGER_RETRY_DELAY_SECONDS = 2.0


class WebSocketError(Exception):
    pass


class MinimalWebSocket:
    """Small stdlib-only WebSocket client for the watcher feed."""

    def __init__(self, url: str):
        parsed = parse.urlparse(url)
        is_tls = parsed.scheme == "wss"
        host = parsed.hostname
        port = parsed.port or (443 if is_tls else 80)
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"

        raw = socket.create_connection((host, port), timeout=30)
        if is_tls:
            ctx = ssl.create_default_context()
            self._sock = ctx.wrap_socket(raw, server_hostname=host)
        else:
            self._sock = raw
        self._sock.settimeout(None)

        origin_scheme = "https" if is_tls else "http"
        origin = f"{origin_scheme}://{host}"
        key = base64.b64encode(os.urandom(16)).decode()
        headers = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Origin: {origin}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        )
        self._sock.sendall(headers.encode())

        resp = b""
        while b"\r\n\r\n" not in resp:
            chunk = self._sock.recv(4096)
            if not chunk:
                raise WebSocketError("Connection closed during handshake")
            resp += chunk
        status_line = resp.split(b"\r\n", 1)[0]
        if b"101" not in status_line:
            raise WebSocketError(f"Handshake failed: {status_line.decode(errors='replace')}")

        self._closed = False
        self._buffer = resp.split(b"\r\n\r\n", 1)[1]

    def _recv_exactly(self, n: int) -> bytes:
        while len(self._buffer) < n:
            chunk = self._sock.recv(max(4096, n - len(self._buffer)))
            if not chunk:
                raise WebSocketError("Connection closed")
            self._buffer += chunk
        data, self._buffer = self._buffer[:n], self._buffer[n:]
        return data

    def _send_frame(self, opcode: int, payload: bytes) -> None:
        header = bytes([0x80 | opcode])
        length = len(payload)
        if length < 126:
            header += bytes([0x80 | length])
        elif length < 65536:
            header += bytes([0x80 | 126]) + struct.pack("!H", length)
        else:
            header += bytes([0x80 | 127]) + struct.pack("!Q", length)
        mask = os.urandom(4)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self._sock.sendall(header + mask + masked)

    def _read_frame(self) -> tuple[int, bytes]:
        b0, b1 = self._recv_exactly(2)
        opcode = b0 & 0x0F
        masked = b1 & 0x80
        length = b1 & 0x7F
        if length == 126:
            length = struct.unpack("!H", self._recv_exactly(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self._recv_exactly(8))[0]
        if masked:
            mask = self._recv_exactly(4)
            raw = self._recv_exactly(length)
            payload = bytes(b ^ mask[i % 4] for i, b in enumerate(raw))
        else:
            payload = self._recv_exactly(length)
        return opcode, payload

    def send_json(self, payload: dict[str, Any]) -> None:
        if self._closed:
            raise WebSocketError("WebSocket is closed")
        self._send_frame(0x1, json.dumps(payload).encode("utf-8"))

    def recv_json(self, timeout: float | None = None) -> dict[str, Any]:
        if timeout is not None and not self._buffer:
            readable, _, _ = select.select([self._sock], [], [], timeout)
            if not readable:
                raise TimeoutError("WebSocket recv timed out")
        if timeout is not None:
            # Keep a socket-level timeout too so partial frame reads cannot block forever.
            self._sock.settimeout(timeout)
        try:
            while True:
                opcode, payload = self._read_frame()
                if opcode == 0x1:
                    return json.loads(payload.decode("utf-8"))
                if opcode == 0x9:
                    self._send_frame(0xA, payload)
                    continue
                if opcode == 0x8:
                    self._closed = True
                    raise WebSocketError("Server sent close frame")
        except socket.timeout as exc:
            raise TimeoutError("WebSocket recv timed out") from exc
        finally:
            if timeout is not None:
                self._sock.settimeout(None)

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            try:
                self._send_frame(0x8, b"")
            except OSError:
                pass
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self._sock.close()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    tmp_path.replace(path)


def read_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return dict(default or {})
    try:
        data = json.loads(path.read_text())
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    return dict(default or {})


class Watcher:
    def __init__(self, wait_seconds: int) -> None:
        self.wait_seconds = wait_seconds
        self.current_status = "idle"
        self.current_idle_reason = "Watcher connected and waiting for actionable turns."
        self.current_prefs: dict[str, Any] = {}
        self._state_lock = threading.Lock()
        self._stop_event = threading.Event()
        self.state = read_json(
            STATE_PATH,
            {
                "started_at": utc_now(),
                "last_poll_at": None,
                "last_status": None,
                "last_match_id": None,
                "last_seq": None,
                "last_trigger_key": None,
                "last_trigger_attempts": 0,
                "last_agent_at": None,
                "last_agent_status": None,
                "last_trigger_pending_retry": False,
                "last_bonus_attempt_at": None,
                "last_posted_status": None,
                "last_posted_idle_reason": None,
                "last_posted_error": None,
                "last_posted_at": None,
                "last_ws_message_at": None,
                "last_pong_at": None,
                "last_error": None,
            },
        )

    def save_state(self, **updates: Any) -> None:
        with self._state_lock:
            self.state.update(updates)
            atomic_write_json(STATE_PATH, self.state)

    def load_connection_token(self) -> str:
        token = TOKEN_PATH.read_text().strip()
        if not token:
            raise RuntimeError(f"Missing connection token in {TOKEN_PATH}")
        return token

    def load_delivery_config(self) -> dict[str, Any]:
        config = read_json(DELIVERY_CONFIG_PATH)
        required = ["channel", "to"]
        missing = [key for key in required if not config.get(key)]
        if missing:
            raise RuntimeError(
                f"Missing delivery config keys {missing} in {DELIVERY_CONFIG_PATH}"
            )
        return config

    def decode_connection_token(self) -> tuple[int, str]:
        token = self.load_connection_token()
        padded = token + ("=" * ((4 - len(token) % 4) % 4))
        payload = json.loads(base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8"))
        return int(payload["a"]), str(payload["t"])

    def peek_game_state(self) -> dict[str, Any]:
        token = self.load_connection_token()
        url = f"{GAME_URL}?wait=0"
        req = request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
        )
        with request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
            body = resp.read().decode("utf-8")
        return json.loads(body)

    def post_status(self, *, status: str, idle_reason: str = "", error_message: str = "",
                    action_taken: bool = False, report_sent: bool = False,
                    restart_ack: bool = False) -> dict[str, Any]:
        last_posted_at = self.state.get("last_posted_at")
        should_send = action_taken or report_sent or restart_ack or bool(error_message)
        if (
            not should_send
            and self.state.get("last_posted_status") == status
            and self.state.get("last_posted_idle_reason") == idle_reason
            and self.state.get("last_posted_error") == error_message
            and last_posted_at
        ):
            try:
                last_ts = datetime.fromisoformat(str(last_posted_at)).timestamp()
                if (time.time() - last_ts) < TELEMETRY_HEARTBEAT_SECONDS:
                    return {}
            except ValueError:
                pass
        try:
            token = self.load_connection_token()
            body = json.dumps(
                {
                    "status": status,
                    "idle_reason": idle_reason,
                    "error": error_message,
                    "action_taken": action_taken,
                    "report_sent": report_sent,
                    "restart_ack": restart_ack,
                }
            ).encode("utf-8")
            req = request.Request(
                WATCHER_URL,
                data=body,
                method="POST",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            with request.urlopen(req, timeout=15) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            watcher = payload.get("watcher", {})
            self.current_prefs = payload.get("agent_preferences") or self.current_prefs
            self.save_state(
                last_server_status=watcher.get("status"),
                last_server_seen_at=watcher.get("last_seen_at"),
                last_posted_status=status,
                last_posted_idle_reason=idle_reason,
                last_posted_error=error_message,
                last_posted_at=utc_now(),
            )
            return payload
        except Exception:
            # Telemetry failure should never stop gameplay.
            return {}

    def connect_ws(self) -> MinimalWebSocket:
        ws = MinimalWebSocket(WATCHER_WS_URL)
        ws.send_json({"type": "auth", "token": self.load_connection_token()})
        resp = ws.recv_json(timeout=10)
        if resp.get("type") != "auth_ok":
            raise RuntimeError(f"Watcher auth failed: {resp}")
        self.current_prefs = resp.get("agent_preferences") or {}
        self.save_state(last_ws_message_at=utc_now(), last_pong_at=utc_now())
        return ws

    def maybe_restart_if_requested(self, data: dict[str, Any]) -> None:
        prefs = data.get("agent_preferences") or data or {}
        requested = prefs.get("watcher_restart_requested_at")
        acked = prefs.get("watcher_restart_ack_at")
        if not requested:
            return
        if acked and acked >= requested:
            return

        os.execv(
            sys.executable,
            [
                sys.executable,
                str(Path(__file__)),
                "--wait-seconds",
                str(self.wait_seconds),
                "--ack-restart",
            ],
        )

    def maybe_claim_bonus(self, data: dict[str, Any]) -> None:
        prefs = data.get("agent_preferences") or data or {}
        if not prefs.get("auto_claim_bonus"):
            return

        last_attempt = self.state.get("last_bonus_attempt_at")
        if last_attempt:
            try:
                last_ts = datetime.fromisoformat(str(last_attempt)).timestamp()
                if (time.time() - last_ts) < BONUS_CHECK_INTERVAL_SECONDS:
                    return
            except ValueError:
                pass

        try:
            agent_id, auth_token = self.decode_connection_token()
            body = json.dumps({"agent_id": agent_id, "token": auth_token}).encode("utf-8")
            req = request.Request(
                BONUS_URL,
                data=body,
                method="POST",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            try:
                with request.urlopen(req, timeout=15) as resp:
                    resp.read()
            except error.HTTPError as exc:
                if exc.code not in {400, 403}:
                    raise
        except Exception:
            return
        finally:
            self.save_state(last_bonus_attempt_at=utc_now())

    def _should_deliver(self, data: dict[str, Any]) -> bool:
        prefs = data.get("agent_preferences") or {}
        report_level = prefs.get("report_level", "every_turn")
        if report_level == "silent":
            return False
        if report_level == "every_turn":
            return True
        legal_actions = data.get("legal_actions") or []
        action_names = {str(action.get("action")) for action in legal_actions if isinstance(action, dict)}
        return "chat" not in action_names

    def _build_agent_message(self, data: dict[str, Any]) -> str:
        prefs = data.get("agent_preferences") or {}
        extras = []
        risk = prefs.get("risk_profile")
        if risk and risk != "balanced":
            extras.append(f"Play with a {risk} risk profile.")
        if data.get("game_type") == "mafia":
            chat_style = prefs.get("mafia_chat_style")
            if chat_style and chat_style != "balanced":
                extras.append(f"Use a {chat_style} Mafia discussion style.")
        message = AGENT_MESSAGE
        if extras:
            message = f"{message} {' '.join(extras)}"
        return message

    def should_trigger(self, wake: dict[str, Any]) -> bool:
        trigger_key = f"{wake.get('match_id')}:{wake.get('seq')}"
        last_key = self.state.get("last_trigger_key")
        if trigger_key != last_key:
            return True

        if not self.state.get("last_trigger_pending_retry"):
            return False

        attempts = int(self.state.get("last_trigger_attempts") or 0)
        if attempts >= MAX_TRIGGER_ATTEMPTS:
            return False

        last_agent_at = self.state.get("last_agent_at")
        if not last_agent_at:
            return True

        try:
            last_ts = datetime.fromisoformat(str(last_agent_at)).timestamp()
        except ValueError:
            return True

        return (time.time() - last_ts) >= TRIGGER_RETRY_DELAY_SECONDS

    def trigger(self, wake: dict[str, Any]) -> None:
        delivery = self.load_delivery_config()
        current = self.peek_game_state()
        if not (
            current.get("status") == "playing"
            and current.get("match_id") == wake.get("match_id")
            and current.get("is_your_turn")
            and bool(current.get("legal_actions"))
        ):
            self.save_state(last_trigger_pending_retry=False)
            return
        should_deliver = self._should_deliver(current)
        cmd = [
            "openclaw",
            "agent",
            "--message",
            self._build_agent_message(current),
            "--json",
        ]
        if should_deliver:
            cmd.extend([
                "--deliver",
                "--channel",
                str(delivery["channel"]),
                "--to",
                str(delivery["to"]),
            ])
        reply_account = delivery.get("reply_account")
        if reply_account and should_deliver:
            cmd.extend(["--reply-account", str(reply_account)])
        proc = subprocess.run(  # noqa: S603
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        trigger_key = f"{wake.get('match_id')}:{wake.get('seq')}"
        attempts = 1
        if trigger_key == self.state.get("last_trigger_key"):
            attempts = int(self.state.get("last_trigger_attempts") or 0) + 1
        retry_pending = proc.returncode != 0
        if proc.returncode == 0:
            time.sleep(0.5)
            try:
                latest = self.peek_game_state()
                retry_pending = (
                    latest.get("status") == "playing"
                    and latest.get("match_id") == wake.get("match_id")
                    and latest.get("is_your_turn")
                    and bool(latest.get("legal_actions"))
                )
            except Exception:
                retry_pending = False
        self.save_state(
            last_trigger_key=trigger_key,
            last_trigger_attempts=attempts,
            last_trigger_pending_retry=retry_pending,
            last_agent_at=utc_now(),
            last_agent_status={
                "code": proc.returncode,
                "body": (proc.stdout or proc.stderr)[:500],
            },
            last_error=None,
        )
        self.post_status(
            status="acting" if proc.returncode == 0 else "delivery_blocked",
            idle_reason="Submitted a live turn to OpenClaw." if proc.returncode == 0 else "OpenClaw delivery failed.",
            error_message="" if proc.returncode == 0 else (proc.stderr or proc.stdout)[:500],
            action_taken=True,
            report_sent=should_deliver and proc.returncode == 0,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"openclaw agent failed with exit code {proc.returncode}: {(proc.stderr or proc.stdout)[:200]}"
            )

    def _retry_pending_wake(self) -> None:
        if not self.state.get("last_trigger_pending_retry"):
            return
        trigger_key = self.state.get("last_trigger_key")
        if not trigger_key:
            return
        match_id, seq = trigger_key.split(":", 1)
        wake = {"match_id": int(match_id), "seq": seq}
        if self.should_trigger(wake):
            self.trigger(wake)

    def _handle_message(self, message: dict[str, Any]) -> None:
        self.save_state(last_ws_message_at=utc_now())
        msg_type = message.get("type")
        data = message.get("data", {})
        if msg_type == "watcher_status":
            self.current_status = str(data.get("status") or "idle")
            self.current_idle_reason = str(data.get("idle_reason") or "Waiting.")
            payload = self.post_status(
                status=self.current_status,
                idle_reason=self.current_idle_reason,
            )
            if payload:
                self.maybe_restart_if_requested(payload)
        elif msg_type == "watcher_wake":
            self.current_status = "acting"
            self.current_idle_reason = "Submitted a live turn to OpenClaw."
            if self.should_trigger(data):
                self.trigger(data)
        elif msg_type == "pong":
            self.save_state(last_pong_at=utc_now())

    def _probe_connection(self, ws: MinimalWebSocket) -> bool:
        ws.send_json({"type": "ping"})
        try:
            message = ws.recv_json(timeout=PING_TIMEOUT_SECONDS)
        except TimeoutError:
            return False
        self._handle_message(message)
        return True

    def run_once(self) -> int:
        ws = None
        try:
            ws = self.connect_ws()
            payload = self.post_status(
                status=self.current_status,
                idle_reason=self.current_idle_reason,
            )
            if payload:
                self.maybe_restart_if_requested(payload)
                self.maybe_claim_bonus(payload)
            self._probe_connection(ws)
            return 0
        finally:
            if ws is not None:
                try:
                    ws.close()
                except Exception:
                    pass

    def loop(self) -> int:
        heartbeat_thread = threading.Thread(
            target=self._background_heartbeat_loop,
            name="clawarena-watcher-heartbeat",
            daemon=True,
        )
        heartbeat_thread.start()
        while True:
            ws = None
            missed_pongs = 0
            try:
                ws = self.connect_ws()
                payload = self.post_status(
                    status=self.current_status,
                    idle_reason=self.current_idle_reason,
                )
                if payload:
                    self.maybe_restart_if_requested(payload)
                    self.maybe_claim_bonus(payload)
                while True:
                    try:
                        message = ws.recv_json(timeout=TELEMETRY_HEARTBEAT_SECONDS)
                    except TimeoutError:
                        payload = self.post_status(
                            status=self.current_status,
                            idle_reason=self.current_idle_reason,
                        )
                        if payload:
                            self.maybe_restart_if_requested(payload)
                            self.maybe_claim_bonus(payload)
                        self._retry_pending_wake()
                        if self._probe_connection(ws):
                            missed_pongs = 0
                            continue
                        missed_pongs += 1
                        if missed_pongs >= MAX_MISSED_PONGS:
                            raise WebSocketError("Watcher websocket ping timed out")
                        continue

                    missed_pongs = 0
                    self._handle_message(message)
            except Exception as exc:  # noqa: BLE001
                self.save_state(
                    last_error={"kind": "exception", "message": str(exc), "at": utc_now()},
                )
                self.post_status(
                    status="error",
                    idle_reason="Watcher lost the live turn feed and is reconnecting.",
                    error_message=str(exc)[:500],
                )
                time.sleep(ERROR_RETRY_DELAY_SECONDS)
            finally:
                if ws is not None:
                    try:
                        ws.close()
                    except Exception:
                        pass

    def _background_heartbeat_loop(self) -> None:
        while not self._stop_event.wait(TELEMETRY_HEARTBEAT_SECONDS):
            try:
                payload = self.post_status(
                    status=self.current_status,
                    idle_reason=self.current_idle_reason,
                )
                if payload:
                    self.maybe_restart_if_requested(payload)
                    self.maybe_claim_bonus(payload)
            except Exception:
                continue


def acquire_lock() -> Any:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    handle = LOCK_PATH.open("w")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("Another ClawArena watcher is already running.", file=sys.stderr)
        sys.exit(1)
    handle.write(str(os.getpid()))
    handle.flush()
    return handle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ClawArena local turn watcher")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Poll once and exit",
    )
    parser.add_argument(
        "--wait-seconds",
        type=int,
        default=0,
        help="Legacy no-op flag kept for compatibility.",
    )
    parser.add_argument(
        "--ack-restart",
        action="store_true",
        help="Acknowledge a dashboard-triggered watcher restart on startup",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    _lock = acquire_lock()
    watcher = Watcher(wait_seconds=args.wait_seconds)
    watcher.save_state(pid=os.getpid(), started_at=watcher.state.get("started_at") or utc_now())
    if args.ack_restart:
        watcher.post_status(
            status="idle",
            idle_reason="Watcher restarted from dashboard request.",
            restart_ack=True,
        )
    if args.once:
        return watcher.run_once()
    return watcher.loop()


if __name__ == "__main__":
    raise SystemExit(main())
