#!/usr/bin/env python3
"""Patch an OpenClaw config with NVIDIA provider + secure API key reference."""

import argparse
import json
import os
import shutil
from pathlib import Path

MODEL_ENTRIES = [
    {
        "id": "mistralai/mixtral-8x7b-instruct-v0.1",
        "name": "Mixtral 8x7B Instruct v0.1",
        "reasoning": False,
        "input": ["text"],
        "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
        "contextWindow": 32000,
        "maxTokens": 8192,
    },
    {
        "id": "moonshotai/kimiai-8b-instruct",
        "name": "Moonshot Kimi 8B Instruct",
        "reasoning": False,
        "input": ["text"],
        "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
        "contextWindow": 32000,
        "maxTokens": 8192,
    },
    {
        "id": "moonshotai/kimi-k2.5",
        "name": "Kimi K2.5",
        "reasoning": True,
        "input": ["text", "image"],
        "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
        "contextWindow": 256000,
        "maxTokens": 8192,
    },
    {
        "id": "nvidia/nemotron-3-super-120b-a12b",
        "name": "nemotron-3-super-120b-a12b",
        "reasoning": True,
        "input": ["text", "image"],
        "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
        "contextWindow": 1000000,
        "maxTokens": 32768,
    },
    {
        "id": "nvidia/llama-3.1-nemotron-ultra-253b-v1",
        "name": "llama-3.1-nemotron-ultra-253b-v1",
        "reasoning": True,
        "input": ["text"],
        "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
        "contextWindow": 131072,
        "maxTokens": 32768,
    },
    {
        "id": "minimaxai/minimax-m2.5",
        "name": "minimax-m2.5",
        "reasoning": True,
        "input": ["text"],
        "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
        "contextWindow": 204800,
        "maxTokens": 32768,
    },
]

PROVIDER_TEMPLATE = {
    "baseUrl": "https://integrate.api.nvidia.com/v1",
    "api": "openai-completions",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Add NVIDIA models + secure key reference to an OpenClaw config."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("openclaw.json"),
        help="Path to the OpenClaw JSON config to patch.",
    )
    parser.add_argument(
        "--key",
        help=(
            "NVIDIA API key. Optional in secure mode (default). "
            "Required only when --inline-key is used."
        ),
    )
    parser.add_argument(
        "--key-id",
        default="NVIDIA_API_KEY",
        help="Environment variable id used by SecretRef (default: NVIDIA_API_KEY).",
    )
    parser.add_argument(
        "--inline-key",
        action="store_true",
        help=(
            "Legacy mode: write plaintext key into config. "
            "Not recommended for shared or versioned configs."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print patched JSON to stdout instead of writing to disk.",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Copy the original config to <config>.bak before overwriting.",
    )
    return parser.parse_args()


def load_config(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_config(path: Path, data: dict):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def remove_inline_env_key(config: dict, key_id: str):
    """Strip legacy plaintext NVIDIA key fields from config."""
    env = config.get("env")
    if not isinstance(env, dict):
        return

    env_vars = env.get("vars")
    if isinstance(env_vars, dict):
        env_vars.pop(key_id, None)
        if not env_vars:
            env.pop("vars", None)

    env.pop(key_id, None)
    if not env:
        config.pop("env", None)


def merge_nvidia_provider(config: dict, api_key: str | None, key_id: str, inline_key: bool):
    models_block = config.setdefault("models", {})
    providers = models_block.setdefault("providers", {})
    provider = providers.setdefault("nvidia", {})
    provider.update(PROVIDER_TEMPLATE)
    if inline_key:
        provider["apiKey"] = api_key
    else:
        provider["apiKey"] = {
            "source": "env",
            "provider": "default",
            "id": key_id,
        }
    provider["models"] = MODEL_ENTRIES


def main():
    args = parse_args()
    key = args.key or os.environ.get(args.key_id)
    if args.inline_key and not key:
        raise SystemExit(
            f"NVIDIA API key required via --key or {args.key_id} environment variable when --inline-key is used."
        )

    config_path = args.config.expanduser()
    config = load_config(config_path)

    remove_inline_env_key(config, args.key_id)
    merge_nvidia_provider(config, key, args.key_id, args.inline_key)

    if args.dry_run:
        print(json.dumps(config, indent=2, ensure_ascii=False))
        return

    if args.backup:
        backup_path = config_path.with_name(config_path.name + ".bak")
        shutil.copy2(config_path, backup_path)

    dump_config(config_path, config)


if __name__ == "__main__":
    main()
