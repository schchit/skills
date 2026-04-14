#!/usr/bin/env python3
"""Stop hook — extract session summary and flush KG extraction queue.

When Claude Code session ends:
1. Store session summary for future recall
2. Pro tier: flush queued texts to Modal for batch KG extraction
"""
import json
import os
import sys
from datetime import datetime

PLUGIN_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
if PLUGIN_ROOT and PLUGIN_ROOT not in sys.path:
    sys.path.insert(0, os.path.join(PLUGIN_ROOT, "hooks"))

try:
    from rewind_bridge import rewind_store, get_config
except ImportError:
    print(json.dumps({}))
    sys.exit(0)


def _flush_pro_queue():
    """Flush batch queue to Modal (Pro tier only)."""
    try:
        cfg = get_config()
        if cfg.get("tier", "free") != "pro":
            return

        api_url = cfg.get("modal", {}).get("extract_batch_url", "")
        auth_token = cfg.get("modal", {}).get("auth_token", "")
        if not api_url or not auth_token:
            return

        from batch_queue import flush_queue, queue_size
        pending = queue_size()
        if pending == 0:
            return

        result = flush_queue(api_url, auth_token)
        # Store flush result as a memory for debugging
        rewind_store(
            f"KG batch flush: {result['extracted']} texts → {result['nodes']} nodes, {result['edges']} edges",
            source="rewind-kg-flush",
            metadata=result,
        )
    except Exception:
        pass


def main():
    try:
        input_data = json.load(sys.stdin)

        # Extract conversation summary from stop event
        conversation = input_data.get("conversation", [])
        session_id = input_data.get("session_id", "unknown")

        if conversation:
            # Build session summary from last N messages
            summary_parts = []
            for msg in conversation[-10:]:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if isinstance(content, str) and content.strip():
                    summary_parts.append(f"[{role}] {content[:300]}")

            if summary_parts:
                summary = "\n".join(summary_parts)
                ts = datetime.now().isoformat()
                rewind_store(
                    f"Session {session_id} ({ts}):\n{summary}",
                    source="claude-code-session",
                    metadata={
                        "session_id": session_id,
                        "timestamp": ts,
                        "turns": len(conversation),
                    },
                )

        # Flush Pro queue on session end
        _flush_pro_queue()

        print(json.dumps({}))

    except Exception:
        print(json.dumps({}))

    sys.exit(0)


if __name__ == "__main__":
    main()
