# FILE_META
# INPUT:  .jsonl session file (OpenClaw DAG format)
# OUTPUT: ordered list of message nodes (final conversation chain)
# POS:    skill lib — called by scan_and_convert.py
# MISSION: Parse DAG structure and extract final conversation chain via parent-id traceback.

"""DAG traversal for OpenClaw .jsonl session logs.

OpenClaw logs are append-only JSONL where nodes form a DAG via id + parentId.
To extract the final conversation, trace back from the last message node to root.
"""

import json
import sys
from typing import Optional

from .metadata_stripper import is_system_startup_message


def parse_jsonl(file_path: str) -> list[dict]:
    """Parse a .jsonl file into a list of JSON objects.

    Skips lines with invalid JSON or encoding errors.
    """
    nodes = []
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                nodes.append(json.loads(line))
            except (json.JSONDecodeError, UnicodeDecodeError):
                print(f"Warning: skipped invalid JSON at {file_path}:{line_num}", file=sys.stderr)
    return nodes


def extract_conversation_chain(nodes: list[dict]) -> list[dict]:
    """Extract the final conversation chain by tracing back from the last message node.

    Handles compaction events: if the chain crosses a compaction boundary,
    the compaction summary is preserved and messages after the boundary are returned.

    Returns a chronologically ordered list of nodes. If a compaction was encountered,
    the compaction node (with its summary) is included at the beginning of the list,
    followed by message nodes from the boundary onward.
    """
    # Build id -> node index
    index: dict[str, dict] = {}
    for node in nodes:
        node_id = node.get("id")
        if node_id:
            index[node_id] = node

    # Find the last message node
    last_message: Optional[dict] = None
    for node in reversed(nodes):
        if node.get("type") == "message":
            last_message = node
            break

    if last_message is None:
        return []

    # Trace back to root
    chain = []
    current = last_message
    visited = set()
    compaction_node = None
    compaction_boundary = None  # id of the first kept entry after compaction

    while current is not None:
        node_id = current.get("id")
        if node_id in visited:
            break  # cycle protection
        visited.add(node_id)
        chain.append(current)

        # Detect compaction events in the chain
        if current.get("type") == "compaction":
            compaction_node = current
            first_kept = current.get("firstKeptEntryId")
            if first_kept:
                compaction_boundary = first_kept
            break  # stop tracing beyond compaction

        parent_id = current.get("parentId")
        if parent_id is None:
            break
        current = index.get(parent_id)

    # Reverse to chronological order
    chain.reverse()

    # If we hit a compaction boundary, keep compaction node + messages from boundary onward
    if compaction_boundary:
        filtered = []
        past_boundary = False
        for node in chain:
            if node.get("id") == compaction_boundary:
                past_boundary = True
            if past_boundary:
                filtered.append(node)
        chain = filtered if filtered else chain

    # Filter to message nodes + compaction node (if present)
    result = []
    if compaction_node and compaction_node.get("summary"):
        result.append(compaction_node)
    result.extend(node for node in chain if node.get("type") == "message")

    return result


def count_turns(messages: list[dict]) -> int:
    """Count conversation turns. One turn = one assistant reply (including tool calls).

    Each assistant message represents one model inference, so tool-call rounds
    are counted as turns rather than being ignored.

    Skips compaction nodes (type="compaction") that may be in the list.
    """
    count = 0
    for msg in messages:
        if msg.get("type") == "compaction":
            continue
        role = msg.get("message", {}).get("role")
        if role == "assistant":
            count += 1
    return count


def get_model_from_nodes(nodes: list[dict]) -> Optional[str]:
    """Extract model ID from the first few nodes (model_change event).

    Only returns values that pass is_allowed_model() to avoid picking up
    gateway-internal names like 'delivery-mirror'.
    """
    from lib.session_index import is_allowed_model

    for node in nodes[:10]:
        if node.get("type") == "model_change":
            mid = node.get("modelId")
            if mid and is_allowed_model(mid):
                return mid
        # Also check assistant messages for model info
        if node.get("type") == "message":
            model = node.get("message", {}).get("model")
            if model and is_allowed_model(model):
                return model
    return None
