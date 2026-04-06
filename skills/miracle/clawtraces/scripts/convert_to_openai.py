# FILE_META
# INPUT:  .trajectory.json + .stats.json (Anthropic format)
# OUTPUT: .openai.json (OpenAI format)
# POS:    skill scripts — utility, standalone
# MISSION: Convert Anthropic trajectory format to OpenAI format with model_config.

#!/usr/bin/env python3
"""Convert Anthropic trajectory files to OpenAI format with model_config.

Reads .trajectory.json (Anthropic format) + .stats.json, outputs .openai.json.

Usage:
    python convert_to_openai.py [--input-dir PATH] [--output-dir PATH]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import glob

sys.path.insert(0, os.path.dirname(__file__))
from lib.paths import get_default_output_dir


# Default max_tokens by model (maxTokens / 3, from OpenClaw model catalog)
MODEL_MAX_TOKENS: dict[str, int] = {
    "claude-opus-4-6": 42666,
    "claude-opus-4-5": 21333,
    "claude-opus-4-5-thinking": 21333,
    "claude-sonnet-4-6": 42666,
    "claude-sonnet-4-5": 21845,
    "claude-haiku-4-5": 21845,
    "gpt-5.4": 42666,
}


def _normalize_provider(model: str) -> str:
    """Map model name to standard provider name."""
    model_lower = model.lower()
    if "claude" in model_lower:
        return "anthropic"
    if "gpt" in model_lower or "o1" in model_lower or "o3" in model_lower:
        return "openai"
    if "gemini" in model_lower:
        return "google"
    if "qwen" in model_lower:
        return "alibaba"
    if "deepseek" in model_lower:
        return "deepseek"
    return "anthropic"


def _resolve_max_tokens(model: str, stats: dict) -> int | None:
    """Resolve max_tokens for a model.

    Checks stats first, then falls back to MODEL_MAX_TOKENS catalog.
    """
    # Check if stats has it
    mt = stats.get("max_tokens")
    if isinstance(mt, int) and mt > 0:
        return mt

    # Lookup from catalog
    model_lower = model.lower()
    for key, val in MODEL_MAX_TOKENS.items():
        if key in model_lower:
            return val

    return None


def build_model_config(stats: dict, model: str) -> dict:
    """Build model_config object from stats and model info."""
    provider = stats.get("provider")
    if not provider or provider == "unknown":
        provider = _normalize_provider(model)
    thinking = stats.get("thinking", stats.get("thinking_level", "off"))
    max_tokens = _resolve_max_tokens(model, stats)

    # temperature: when thinking is enabled, OpenClaw doesn't send it,
    # API uses its default (1.0 for Anthropic, 1.0 for OpenAI)
    temperature = 1.0

    config: dict = {
        "model": model,
        "provider": provider,
        "temperature": temperature,
        "thinking": thinking,
    }
    if max_tokens:
        config["max_tokens"] = max_tokens

    return config


def convert_tools(anthropic_tools: list[dict]) -> list[dict]:
    """Convert Anthropic tool schemas to OpenAI function format.

    Anthropic: {"name": "...", "description": "...", "input_schema": {...}}
    OpenAI:    {"type": "function", "function": {"name": "...", "description": "...", "parameters": {...}}}
    """
    openai_tools = []
    for tool in anthropic_tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool.get("name", ""),
                "description": tool.get("description", ""),
                "parameters": tool.get("input_schema", {}),
            },
        })
    return openai_tools


def convert_messages(system_prompt: str, anthropic_messages: list[dict]) -> list[dict]:
    """Convert Anthropic messages to OpenAI messages format.

    Key mappings:
    - system prompt → {"role": "system", "content": "..."}
    - content[type=thinking] → reasoning_content field
    - content[type=text] → content string
    - content[type=tool_use] → tool_calls array
    - user message with tool_result blocks → separate role="tool" messages
    """
    openai_messages: list[dict] = []

    # System message
    if system_prompt:
        openai_messages.append({
            "role": "system",
            "content": system_prompt,
        })

    for msg in anthropic_messages:
        role = msg.get("role")
        content = msg.get("content")

        if role == "user":
            # User message: could be plain text or contain tool_result blocks
            if isinstance(content, str):
                openai_messages.append({
                    "role": "user",
                    "content": content,
                })
            elif isinstance(content, list):
                # Separate tool_result blocks from text content
                tool_results = [b for b in content if isinstance(b, dict) and b.get("type") == "tool_result"]
                text_blocks = [b for b in content if isinstance(b, dict) and b.get("type") == "text"]
                other_text = [b for b in content if isinstance(b, str)]

                # Collect text parts
                text_parts = []
                for b in text_blocks:
                    t = b.get("text", "")
                    if t.strip():
                        text_parts.append(t)
                for b in other_text:
                    if b.strip():
                        text_parts.append(b)

                if tool_results:
                    # Emit tool results as role="tool" messages
                    for tr in tool_results:
                        result_content = tr.get("content", "")
                        openai_messages.append({
                            "role": "tool",
                            "tool_call_id": tr.get("tool_use_id", ""),
                            "content": result_content if isinstance(result_content, str) else json.dumps(result_content, ensure_ascii=False),
                        })
                    # If there's also text alongside tool results, emit as user message after
                    if text_parts:
                        openai_messages.append({
                            "role": "user",
                            "content": "\n".join(text_parts),
                        })
                elif text_parts:
                    # Pure text user message
                    openai_messages.append({
                        "role": "user",
                        "content": "\n".join(text_parts),
                    })

        elif role == "assistant":
            if isinstance(content, list):
                # Extract thinking, text, and tool_use blocks
                reasoning_parts: list[str] = []
                text_parts: list[str] = []
                tool_calls: list[dict] = []

                for block in content:
                    if not isinstance(block, dict):
                        continue
                    block_type = block.get("type")

                    if block_type == "thinking":
                        thinking_text = block.get("thinking", "")
                        if thinking_text:
                            reasoning_parts.append(thinking_text)

                    elif block_type == "text":
                        text = block.get("text", "")
                        if text.strip():
                            text_parts.append(text)

                    elif block_type == "tool_use":
                        tool_input = block.get("input", {})
                        tool_calls.append({
                            "id": block.get("id", ""),
                            "type": "function",
                            "function": {
                                "name": block.get("name", ""),
                                "arguments": json.dumps(tool_input, ensure_ascii=False),
                            },
                        })

                openai_msg: dict = {"role": "assistant"}

                # Reasoning content
                if reasoning_parts:
                    openai_msg["reasoning_content"] = "\n".join(reasoning_parts)

                # Text content or tool calls
                if tool_calls:
                    openai_msg["content"] = "\n".join(text_parts) if text_parts else None
                    openai_msg["tool_calls"] = tool_calls
                else:
                    openai_msg["content"] = "\n".join(text_parts) if text_parts else ""

                openai_messages.append(openai_msg)

            elif isinstance(content, str):
                openai_messages.append({
                    "role": "assistant",
                    "content": content,
                })

    return openai_messages


def convert_trajectory(anthropic_traj: dict, stats: dict) -> dict:
    """Convert a full Anthropic trajectory to OpenAI format with model_config.

    Input (Anthropic):
        {"system": "...", "tools": [...], "messages": [...]}

    Output (OpenAI + model_config):
        {"model_config": {...}, "tools": [...], "messages": [...]}
    """
    system_prompt = anthropic_traj.get("system", "")
    anthropic_tools = anthropic_traj.get("tools", [])
    anthropic_messages = anthropic_traj.get("messages", [])

    model = stats.get("model", "unknown")

    return {
        "model_config": build_model_config(stats, model),
        "tools": convert_tools(anthropic_tools),
        "messages": convert_messages(system_prompt, anthropic_messages),
    }


def main():
    parser = argparse.ArgumentParser(description="Convert Anthropic trajectories to OpenAI format")
    parser.add_argument("--input-dir", "-i", help="Directory with .trajectory.json files")
    parser.add_argument("--output-dir", "-o", help="Output directory (default: same as input)")
    args = parser.parse_args()

    input_dir = args.input_dir or get_default_output_dir()
    input_dir = os.path.expanduser(input_dir)
    output_dir = args.output_dir or input_dir
    output_dir = os.path.expanduser(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    traj_files = sorted(glob.glob(os.path.join(input_dir, "*.trajectory.json")))
    if not traj_files:
        print("No .trajectory.json files found.", file=sys.stderr)
        sys.exit(1)

    print(f"Converting {len(traj_files)} trajectory(ies)...", file=sys.stderr)

    converted = 0
    for traj_path in traj_files:
        sid = os.path.basename(traj_path).replace(".trajectory.json", "")
        stats_path = os.path.join(input_dir, f"{sid}.stats.json")

        # Load Anthropic trajectory
        with open(traj_path, "r", encoding="utf-8") as f:
            anthropic_traj = json.load(f)

        # Load stats (optional)
        stats: dict = {}
        if os.path.isfile(stats_path):
            with open(stats_path, "r", encoding="utf-8") as f:
                stats = json.load(f)

        # Convert
        openai_traj = convert_trajectory(anthropic_traj, stats)

        # Write
        output_path = os.path.join(output_dir, f"{sid}.openai.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(openai_traj, f, ensure_ascii=False, indent=2)

        model_config = openai_traj["model_config"]
        msg_count = len(openai_traj["messages"])
        tool_count = len(openai_traj["tools"])
        print(f"  {sid[:14]}... model={model_config['model']} msgs={msg_count} tools={tool_count}")
        converted += 1

    print(f"\nConverted {converted} file(s) to {output_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
