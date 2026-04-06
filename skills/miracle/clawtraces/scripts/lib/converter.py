# FILE_META
# INPUT:  message nodes + system prompt + session metadata
# OUTPUT: Anthropic trajectory dict (system/tools/messages)
# POS:    skill lib — called by scan_and_convert.py, depends on tool_registry.py
# MISSION: Convert OpenClaw message nodes to Anthropic trajectory format.

"""Convert OpenClaw .jsonl message nodes to Anthropic trajectory format."""

from __future__ import annotations

from .session_index import is_allowed_model
from .tool_registry import get_tool_schemas


def _extract_user_text(content: list) -> str:
    """Extract text from user message content blocks."""
    parts = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
        elif isinstance(block, str):
            parts.append(block)
    return "\n".join(parts)


def _convert_assistant_content(content: list) -> list[dict]:
    """Convert assistant content blocks from OpenClaw to Anthropic format."""
    result = []
    for block in content:
        if not isinstance(block, dict):
            continue

        block_type = block.get("type")

        if block_type == "thinking":
            result.append({
                "type": "thinking",
                "thinking": block.get("thinking", ""),
                "signature": "",
            })
        elif block_type == "text":
            text = block.get("text", "")
            if text.strip():
                result.append({
                    "type": "text",
                    "text": text,
                })
        elif block_type == "toolCall":
            arguments = block.get("arguments", {})
            # arguments may be a JSON string instead of dict in some OpenClaw versions
            if isinstance(arguments, str):
                try:
                    import json
                    arguments = json.loads(arguments)
                except (json.JSONDecodeError, ValueError):
                    arguments = {}
            if not isinstance(arguments, dict):
                arguments = {}
            result.append({
                "type": "tool_use",
                "id": block.get("id", ""),
                "name": block.get("name", ""),
                "input": arguments,
            })

    return result


def _convert_tool_result(message: dict) -> dict:
    """Convert a toolResult message to Anthropic tool_result content block."""
    content_blocks = message.get("content", [])
    text_parts = []
    for block in content_blocks:
        if isinstance(block, dict) and block.get("type") == "text":
            text_parts.append(block.get("text", ""))
        elif isinstance(block, str):
            text_parts.append(block)

    result = {
        "type": "tool_result",
        "tool_use_id": message.get("toolCallId", ""),
        "content": "\n".join(text_parts),
    }

    if message.get("isError"):
        result["is_error"] = True

    return result


def _collect_tool_calls(messages: list[dict], validate_model: bool = True) -> list[dict]:
    """Collect toolCall blocks from assistant messages of allowed models."""
    tool_calls = []
    for node in messages:
        if node.get("type") == "compaction":
            continue
        msg = node.get("message", {})
        if msg.get("role") != "assistant":
            continue
        if msg.get("stopReason") == "error":
            continue
        if validate_model:
            msg_model = msg.get("model", "")
            if msg_model and not is_allowed_model(msg_model):
                continue
        for block in msg.get("content", []):
            if isinstance(block, dict) and block.get("type") == "toolCall":
                tool_calls.append(block)
    return tool_calls


def _is_aborted_by_tool_error(message_nodes: list[dict]) -> bool:
    """Detect if the session was aborted due to a tool error.

    A session is considered aborted when the last message(s) are toolResult
    with isError=True and there is no subsequent assistant recovery.
    """
    # Walk backwards to find the last non-empty message
    for node in reversed(message_nodes):
        if node.get("type") == "compaction":
            continue
        msg = node.get("message", {})
        role = msg.get("role")

        if role == "assistant":
            # Session ends with an assistant message — not aborted by tool error
            # (but could be a model error, handled separately)
            return False

        if role == "toolResult":
            if msg.get("isError"):
                return True
            # Non-error tool result at the end without assistant follow-up
            # is unusual but not a tool-error abort
            return False

        if role == "user":
            # Session ends with a user message (no assistant response) — not tool-error
            return False

    return False


def convert_to_trajectory(
    message_nodes: list[dict],
    validate_model: bool = True,
    session_meta: dict | None = None,
    real_system_prompt: str | None = None,
) -> dict:
    """Convert a list of OpenClaw message nodes to Anthropic trajectory format.

    Args:
        message_nodes: Chronologically ordered list of message nodes
                      (output of dag.extract_conversation_chain)
        validate_model: If True, skip assistant messages from non-allowed models
                       (handles mid-session model switches)
        session_meta: Optional session metadata dict (from extract_session_metadata)
                     with keys: cwd, model, thinking_level, timestamp, tool_names.
        real_system_prompt: System prompt — either from cache-trace.jsonl (preferred)
                          or reconstructed from session metadata (fallback).

    Returns:
        Anthropic trajectory dict with system, tools, messages keys
    """
    meta = session_meta or {}

    if not real_system_prompt:
        return {
            "system": "",
            "tools": [],
            "messages": [],
            "_discarded": "no_system_prompt",
        }

    # Check if session was aborted by a tool error — discard entire trajectory
    if _is_aborted_by_tool_error(message_nodes):
        return {
            "system": "",
            "tools": [],
            "messages": [],
            "_discarded": "tool_error_abort",
        }

    # Collect tool calls only from allowed-model messages for schema extraction
    tool_calls = _collect_tool_calls(message_nodes, validate_model=validate_model)
    tool_schemas = get_tool_schemas(tool_calls)

    # Track which tool_call IDs came from allowed-model assistant messages
    # so we can also skip their corresponding toolResult messages
    skipped_tool_call_ids: set[str] = set()

    # Convert messages
    converted_messages = []

    for node in message_nodes:
        # Handle compaction nodes — inject summary as context (Q11)
        if node.get("type") == "compaction":
            summary = node.get("summary", "")
            if summary:
                converted_messages.append({
                    "role": "user",
                    "content": f"[Context from prior conversation (compacted)]:\n\n{summary}",
                })
                converted_messages.append({
                    "role": "assistant",
                    "content": [{"type": "text", "text": "Understood. I have the context from our prior conversation. How can I help you next?"}],
                })
            continue

        msg = node.get("message", {})
        role = msg.get("role")
        content = msg.get("content", [])

        if role == "user":
            # Extract user text — preserve metadata prefixes as-is (Q09)
            raw_text = _extract_user_text(content)

            if not raw_text.strip():
                continue

            converted_messages.append({
                "role": "user",
                "content": raw_text,
            })

        elif role == "assistant":
            # Skip error messages
            if msg.get("stopReason") == "error":
                continue

            # Skip messages from non-allowed models (mid-session model switch)
            if validate_model:
                msg_model = msg.get("model", "")
                if msg_model and not is_allowed_model(msg_model):
                    # Track tool_call IDs from this skipped message
                    # so we also skip their toolResult responses
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "toolCall":
                            skipped_tool_call_ids.add(block.get("id", ""))
                    continue

            anthropic_content = _convert_assistant_content(content)
            if not anthropic_content:
                continue

            converted_messages.append({
                "role": "assistant",
                "content": anthropic_content,
            })

        elif role == "toolResult":
            # Skip toolResults for tool calls from non-allowed models
            if msg.get("toolCallId", "") in skipped_tool_call_ids:
                continue

            tool_result_block = _convert_tool_result(msg)
            converted_messages.append({
                "role": "user",
                "content": [tool_result_block],
            })

    # Merge consecutive same-role messages
    merged = _merge_consecutive_messages(converted_messages)

    # Anthropic format requires messages to start with role="user"
    # Strip leading non-user messages
    while merged and merged[0]["role"] != "user":
        merged.pop(0)

    # Anthropic format requires messages to end with role="assistant"
    # Strip trailing non-assistant messages
    while merged and merged[-1]["role"] != "assistant":
        merged.pop()

    # Validate minimum viable trajectory: at least one user + one assistant
    if len(merged) < 2:
        return {
            "system": real_system_prompt,
            "tools": [],
            "messages": [],
        }

    return {
        "system": real_system_prompt,
        "tools": tool_schemas,
        "messages": merged,
    }


def _normalize_content_to_blocks(content) -> list[dict]:
    """Normalize message content to a list of content blocks.

    Handles string content (plain user text) and list content (blocks).
    """
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if isinstance(content, list):
        return content
    return []


def _merge_consecutive_messages(messages: list[dict]) -> list[dict]:
    """Merge consecutive messages with the same role.

    This handles parallel tool calls producing multiple consecutive toolResult
    messages (all role="user" with tool_result blocks).
    """
    if not messages:
        return []

    merged = [messages[0]]

    for msg in messages[1:]:
        prev = merged[-1]

        if msg["role"] == prev["role"]:
            prev_blocks = _normalize_content_to_blocks(prev["content"])
            curr_blocks = _normalize_content_to_blocks(msg["content"])
            prev["content"] = prev_blocks + curr_blocks
        else:
            merged.append(msg)

    return merged
