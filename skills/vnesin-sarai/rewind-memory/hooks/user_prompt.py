#!/usr/bin/env python3
"""UserPromptSubmit hook — search Rewind memory for relevant context.

When a user submits a prompt, search memory for related content and
inject it as a system message so Claude has historical context.
"""
import json
import os
import sys

PLUGIN_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
if PLUGIN_ROOT and PLUGIN_ROOT not in sys.path:
    sys.path.insert(0, os.path.join(PLUGIN_ROOT, "hooks"))

try:
    from rewind_bridge import rewind_search
except ImportError:
    print(json.dumps({}))
    sys.exit(0)


def main():
    try:
        input_data = json.load(sys.stdin)
        prompt = input_data.get("prompt", "")

        if not prompt or len(prompt) < 10:
            print(json.dumps({}))
            sys.exit(0)

        # Search memory for relevant context
        results = rewind_search(prompt, top_k=3)

        if not results:
            print(json.dumps({}))
            sys.exit(0)

        # Build context from search results
        context_parts = []
        for r in results:
            text = r.get("text", "")[:500]
            source = r.get("source", "unknown")
            score = r.get("score", 0)
            if text and score > 0.3:
                context_parts.append(f"[{source}] {text}")

        if context_parts:
            context = "\n---\n".join(context_parts)
            output = {
                "systemMessage": f"📚 Rewind Memory — relevant context from previous sessions:\n{context}"
            }
        else:
            output = {}

        print(json.dumps(output))

    except Exception as e:
        print(json.dumps({"systemMessage": f"Rewind: {e}"}))

    sys.exit(0)


if __name__ == "__main__":
    main()
