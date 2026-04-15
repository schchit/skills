#!/usr/bin/env python3
"""
God Mode — Model Watcher
Polls LM Studio every 30s. When a new model appears, auto-runs probe.

Run as background daemon:
    nohup python probe_watcher.py &

Run once (check new models and exit):
    python probe_watcher.py --once

To run at login on macOS, see: install/launchagent_install.sh
"""

import asyncio
import aiohttp
import json
import argparse
import sys
from pathlib import Path

LMSTUDIO_BASE = "http://127.0.0.1:1234/v1"
POLL_INTERVAL = 30  # seconds
PROFILES_FILE = Path(__file__).parent / "model_profiles.json"


def load_profiles() -> dict:
    if PROFILES_FILE.exists():
        return json.loads(PROFILES_FILE.read_text())
    return {}


async def get_loaded_models() -> list:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{LMSTUDIO_BASE}/models",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status != 200:
                    return []
                data = await r.json()
                return [
                    m["id"] for m in data.get("data", [])
                    if not any(ex in m["id"].lower() for ex in ["embed", "text-embedding"])
                ]
    except Exception:
        return []


async def run_once():
    """Check for new models and probe them."""
    sys.path.insert(0, str(Path(__file__).parent))
    from probe import probe_model, load_profiles, save_profiles

    models = await get_loaded_models()
    if not models:
        return

    profiles = load_profiles()
    new_models = [m for m in models if m not in profiles]

    if not new_models:
        return

    print(f"[god-mode-watcher] {len(new_models)} new model(s) detected: {new_models}")
    for model_id in new_models:
        print(f"[god-mode-watcher] Probing: {model_id}")
        result = await probe_model(model_id, verbose=False)
        profiles[model_id] = result
        save_profiles(profiles)
        print(f"[god-mode-watcher] Result: {model_id} → {result['status']} (technique: {result.get('technique') or 'none'})")


async def watch_loop():
    print(f"[god-mode-watcher] Started — polling LM Studio every {POLL_INTERVAL}s")
    while True:
        try:
            await run_once()
        except Exception as e:
            print(f"[god-mode-watcher] Error: {e}")
        await asyncio.sleep(POLL_INTERVAL)


def main():
    parser = argparse.ArgumentParser(description="God Mode Model Watcher")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    if args.once:
        asyncio.run(run_once())
        return

    asyncio.run(watch_loop())


if __name__ == "__main__":
    main()
