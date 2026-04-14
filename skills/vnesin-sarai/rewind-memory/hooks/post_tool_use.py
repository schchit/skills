#!/usr/bin/env python3
"""PostToolUse hook — capture file edits and tool results for memory.

After each tool use, store relevant context (file changes, search results,
command outputs) as memory chunks for future recall.

Pro tier: also queues text for batch KG extraction via Modal.
"""
import json
import os
import sys

PLUGIN_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
if PLUGIN_ROOT and PLUGIN_ROOT not in sys.path:
    sys.path.insert(0, os.path.join(PLUGIN_ROOT, "hooks"))

try:
    from rewind_bridge import rewind_store, rewind_ingest_file
except ImportError:
    print(json.dumps({}))
    sys.exit(0)


# Tools worth capturing
CAPTURE_TOOLS = {"write", "edit", "read", "bash", "execute"}
# Minimum output length to store
MIN_OUTPUT_LEN = 50


def _is_pro_tier() -> bool:
    """Check if Pro tier is configured."""
    try:
        from rewind_bridge import get_config
        cfg = get_config()
        return cfg.get("tier", "free") == "pro"
    except Exception:
        return False


def _enqueue_for_extraction(text: str, source: str = "claude-code"):
    """Queue text for batch KG extraction (Pro tier)."""
    try:
        from batch_queue import enqueue
        enqueue(text, source=source)
    except ImportError:
        pass


def main():
    try:
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        tool_output = input_data.get("tool_output", "")

        # Only capture relevant tools
        if tool_name.lower() not in CAPTURE_TOOLS:
            print(json.dumps({}))
            sys.exit(0)

        pro = _is_pro_tier()

        # For file writes/edits — ingest the file
        if tool_name.lower() in ("write", "edit"):
            file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
            if file_path and os.path.exists(file_path):
                rewind_ingest_file(file_path)
                # Pro: queue file content for KG extraction
                if pro:
                    try:
                        with open(file_path, "r") as f:
                            content = f.read(2000)
                        _enqueue_for_extraction(content, source=f"file:{file_path}")
                    except Exception:
                        pass

        # For significant command outputs — store as memory
        if tool_name.lower() in ("bash", "execute"):
            command = tool_input.get("command", "")
            output = str(tool_output)[:2000] if tool_output else ""
            if command and output and len(output) > MIN_OUTPUT_LEN:
                text = f"Command: {command}\nOutput: {output}"
                rewind_store(
                    text,
                    source="claude-code-tool",
                    metadata={"tool": tool_name, "command": command},
                )
                # Pro: queue for KG extraction
                if pro:
                    _enqueue_for_extraction(text, source="claude-code-tool")

        print(json.dumps({}))

    except Exception:
        print(json.dumps({}))

    sys.exit(0)


if __name__ == "__main__":
    main()
