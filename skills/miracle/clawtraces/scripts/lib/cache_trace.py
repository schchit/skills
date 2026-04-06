# FILE_META
# INPUT:  cache-trace.jsonl log file
# OUTPUT: dict mapping session_id → system prompt
# POS:    skill lib — primary system prompt source, called by scan_and_convert.py
# MISSION: Extract real system prompts from OpenClaw's cache-trace log.

"""Parse cache-trace.jsonl to extract real system prompts by session ID."""

import json
import os
from typing import Optional


def _normalize_system_prompt(system) -> Optional[str]:
    """Normalize system prompt to a string.

    Handles both string format and Anthropic content-blocks format
    (list of dicts with type/text).
    """
    if isinstance(system, str):
        return system
    if isinstance(system, list):
        # Content blocks format: [{"type": "text", "text": "..."}]
        parts = []
        for block in system:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        if parts:
            return "\n".join(parts)
    return None


def get_cache_trace_path() -> str:
    """Get cache-trace.jsonl path from OpenClaw state directory."""
    state_dir = os.environ.get("OPENCLAW_STATE_DIR", os.path.expanduser("~/.openclaw"))

    # Check if openclaw.json specifies a custom path
    config_path = os.path.join(state_dir, "openclaw.json")
    if os.path.isfile(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            custom_path = (
                config.get("diagnostics", {})
                .get("cacheTrace", {})
                .get("filePath", "")
            )
            if custom_path:
                return os.path.expanduser(custom_path)
        except (json.JSONDecodeError, OSError):
            pass

    return os.path.join(state_dir, "logs", "cache-trace.jsonl")


def build_session_system_prompt_index(cache_trace_path: str) -> dict[str, str]:
    """Build a mapping of sessionId → system prompt from cache-trace.jsonl.

    For each session, takes the last occurrence of a system prompt
    (from stages that include the system field), which is the most complete.

    Returns:
        Dict mapping sessionId to system prompt string.
    """
    index: dict[str, str] = {}

    if not os.path.isfile(cache_trace_path):
        return index

    try:
        with open(cache_trace_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue

                session_id = obj.get("sessionId")
                system = obj.get("system")

                if session_id and system:
                    normalized = _normalize_system_prompt(system)
                    if normalized:
                        # Keep updating — last entry wins (most complete)
                        index[session_id] = normalized
    except OSError:
        pass

    return index


def get_system_prompt_for_session(
    cache_trace_path: str,
    session_id: str,
) -> Optional[str]:
    """Get the system prompt for a specific session from cache-trace.jsonl.

    Returns the last system prompt recorded for this session, or None.
    """
    result: Optional[str] = None

    if not os.path.isfile(cache_trace_path):
        return None

    try:
        with open(cache_trace_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue

                if obj.get("sessionId") == session_id:
                    system = obj.get("system")
                    if system:
                        normalized = _normalize_system_prompt(system)
                        if normalized:
                            result = normalized
    except OSError:
        pass

    return result
