#!/usr/bin/env python3
"""Prepare and launch the ClawArena local watcher."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


CLAW_DIR = Path.home() / ".clawarena"
HOOK_CONFIG_PATH = CLAW_DIR / "openclaw_hook.json"
WATCHER_PID_PATH = CLAW_DIR / "watcher.pid"
WATCHER_LOG_PATH = CLAW_DIR / "watcher.log"
WATCHER_LAUNCHER_PATH = CLAW_DIR / "run-watcher.sh"


def atomic_write(path: Path, content: str, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content)
    tmp_path.replace(path)
    if mode is not None:
        path.chmod(mode)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    return {}


def process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def stop_existing_watcher() -> None:
    if not WATCHER_PID_PATH.exists():
        return
    try:
        pid = int(WATCHER_PID_PATH.read_text().strip())
    except ValueError:
        WATCHER_PID_PATH.unlink(missing_ok=True)
        return
    if process_alive(pid):
        os.kill(pid, signal.SIGTERM)
        for _ in range(20):
            if not process_alive(pid):
                break
            time.sleep(0.2)
    WATCHER_PID_PATH.unlink(missing_ok=True)


def write_hook_config(args: argparse.Namespace) -> dict[str, Any]:
    existing = read_json(HOOK_CONFIG_PATH)
    channel = args.channel or existing.get("channel")
    target = args.to or existing.get("to")
    hook_token = args.hook_token or existing.get("token")
    if not channel or not target or not hook_token:
        raise SystemExit(
            "channel, to, and hook-token are required on first setup; reruns can reuse the saved config."
        )
    config = {
        "url": args.hook_url.rstrip("/") + "/hooks/agent",
        "token": hook_token,
        "channel": channel,
        "to": target,
        "deliver": "announce",
        "timeoutSeconds": 120,
    }
    atomic_write(HOOK_CONFIG_PATH, json.dumps(config, indent=2, sort_keys=True) + "\n", 0o600)
    return config


def write_launcher(skill_root: Path) -> None:
    launcher = f"""#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$HOME/.clawarena"
exec python3 "{skill_root / "watcher.py"}" >> "{WATCHER_LOG_PATH}" 2>&1
"""
    atomic_write(WATCHER_LAUNCHER_PATH, launcher, 0o700)


def start_watcher() -> int:
    WATCHER_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(  # noqa: S603
        [str(WATCHER_LAUNCHER_PATH)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    WATCHER_PID_PATH.write_text(f"{proc.pid}\n")
    return proc.pid


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Set up the ClawArena local watcher")
    parser.add_argument("--channel", help="Active OpenClaw channel for delivery, e.g. telegram")
    parser.add_argument("--to", help="Active chat target, e.g. a Telegram numeric chat id")
    parser.add_argument("--hook-token", help="Local OpenClaw hook token")
    parser.add_argument(
        "--hook-url",
        default="http://127.0.0.1:18789",
        help="Base URL for the local OpenClaw gateway (default: http://127.0.0.1:18789)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_root = Path(__file__).resolve().parent
    config = write_hook_config(args)
    write_launcher(skill_root)
    stop_existing_watcher()
    pid = start_watcher()
    print(
        json.dumps(
            {
                "watcher_started": True,
                "pid": pid,
                "hook_url": config["url"],
                "channel": config["channel"],
                "to": config["to"],
                "launcher": str(WATCHER_LAUNCHER_PATH),
                "log_file": str(WATCHER_LOG_PATH),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
