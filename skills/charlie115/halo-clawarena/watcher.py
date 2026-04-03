#!/usr/bin/env python3
"""ClawArena local turn watcher.

Long-polls the lightweight ClawArena agent state endpoint and wakes OpenClaw
via the local hooks/agent endpoint only when the fighter has an actionable turn.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, request


CLAW_DIR = Path.home() / ".clawarena"
TOKEN_PATH = CLAW_DIR / "token"
HOOK_CONFIG_PATH = CLAW_DIR / "openclaw_hook.json"
STATE_PATH = CLAW_DIR / "watcher_state.json"
LOCK_PATH = CLAW_DIR / "watcher.lock"

API_BASE = os.environ.get("CLAWARENA_API_BASE", "https://clawarena.halochain.xyz/api/v1").rstrip("/")
GAME_URL = f"{API_BASE}/agents/game/"
DEFAULT_WAIT_SECONDS = 55
HTTP_TIMEOUT_SECONDS = 70

HOOK_MESSAGE = (
    "Use the installed halo-clawarena skill. Read GAMELOOP.md, read "
    "CONNECTION_TOKEN from ~/.clawarena/token, run one game loop tick, and "
    "report the result in this chat."
)


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
        self.wait_seconds = max(0, min(wait_seconds, 60))
        self.state = read_json(
            STATE_PATH,
            {
                "started_at": utc_now(),
                "last_poll_at": None,
                "last_status": None,
                "last_match_id": None,
                "last_seq": None,
                "last_trigger_key": None,
                "last_hook_at": None,
                "last_hook_status": None,
                "last_error": None,
            },
        )

    def save_state(self, **updates: Any) -> None:
        self.state.update(updates)
        atomic_write_json(STATE_PATH, self.state)

    def load_connection_token(self) -> str:
        token = TOKEN_PATH.read_text().strip()
        if not token:
            raise RuntimeError(f"Missing connection token in {TOKEN_PATH}")
        return token

    def load_hook_config(self) -> dict[str, Any]:
        config = read_json(HOOK_CONFIG_PATH)
        required = ["url", "token", "channel", "to"]
        missing = [key for key in required if not config.get(key)]
        if missing:
            raise RuntimeError(
                f"Missing hook config keys {missing} in {HOOK_CONFIG_PATH}"
            )
        return config

    def poll(self) -> dict[str, Any]:
        token = self.load_connection_token()
        url = f"{GAME_URL}?wait={self.wait_seconds}"
        req = request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
        )
        with request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
            body = resp.read().decode("utf-8")
        data = json.loads(body)
        self.save_state(
            last_poll_at=utc_now(),
            last_status=data.get("status"),
            last_match_id=data.get("match_id"),
            last_seq=data.get("seq"),
            last_error=None,
        )
        return data

    def should_trigger(self, data: dict[str, Any]) -> bool:
        if data.get("status") != "playing":
            return False
        if not data.get("is_your_turn"):
            return False
        if not data.get("legal_actions"):
            return False
        trigger_key = f"{data.get('match_id')}:{data.get('seq')}"
        return trigger_key != self.state.get("last_trigger_key")

    def trigger(self, data: dict[str, Any]) -> None:
        hook = self.load_hook_config()
        payload = {
            "message": HOOK_MESSAGE,
            "name": "ClawArena Turn",
            "deliver": hook.get("deliver", "announce"),
            "channel": hook["channel"],
            "to": hook["to"],
            "timeoutSeconds": int(hook.get("timeoutSeconds", 120)),
        }
        req = request.Request(
            hook["url"],
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {hook['token']}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        with request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
            body = resp.read().decode("utf-8") if resp else ""
            status_code = getattr(resp, "status", 200)
        trigger_key = f"{data.get('match_id')}:{data.get('seq')}"
        self.save_state(
            last_trigger_key=trigger_key,
            last_hook_at=utc_now(),
            last_hook_status={
                "code": status_code,
                "body": body[:500],
            },
            last_error=None,
        )

    def run_once(self) -> int:
        try:
            data = self.poll()
            if self.should_trigger(data):
                self.trigger(data)
            return 0
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            self.save_state(
                last_poll_at=utc_now(),
                last_error={
                    "kind": "http",
                    "code": exc.code,
                    "body": body[:500],
                    "at": utc_now(),
                },
            )
            return 1
        except Exception as exc:  # noqa: BLE001
            self.save_state(
                last_poll_at=utc_now(),
                last_error={
                    "kind": "exception",
                    "message": str(exc),
                    "at": utc_now(),
                },
            )
            return 1

    def loop(self) -> int:
        while True:
            exit_code = self.run_once()
            if exit_code != 0:
                time.sleep(5)


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
        default=DEFAULT_WAIT_SECONDS,
        help="Long-poll wait time for /agents/game/ (default: 55)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    _lock = acquire_lock()
    watcher = Watcher(wait_seconds=args.wait_seconds)
    watcher.save_state(pid=os.getpid(), started_at=watcher.state.get("started_at") or utc_now())
    if args.once:
        return watcher.run_once()
    return watcher.loop()


if __name__ == "__main__":
    raise SystemExit(main())
