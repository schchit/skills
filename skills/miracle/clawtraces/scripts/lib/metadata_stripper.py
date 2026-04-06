# FILE_META
# INPUT:  raw user message text
# OUTPUT: cleaned message text
# POS:    skill lib — called by converter.py
# MISSION: Strip Sender JSON metadata and timestamp prefixes from user messages.

"""Strip metadata prefixes from OpenClaw user messages.

OpenClaw prepends Sender metadata and timestamps to user messages when
received via IM gateways (Telegram, Feishu, etc.).

Example input:
    Sender (untrusted metadata):
    ```json
    {"label":"openclaw-tui","id":"gateway-client"}
    ```

    [Thu 2026-03-12 18:39 GMT+8] actual user message here

Expected output:
    actual user message here
"""

import re

# Pattern: Sender block (from "Sender" to closing ``` + optional blank lines)
# Uses [\s\S]*? to match any JSON content including nested braces
_SENDER_PATTERN = re.compile(
    r"^Sender\s+\(untrusted metadata\):\s*\n"
    r"```json\s*\n"
    r"[\s\S]*?\n"
    r"```\s*\n*",
    re.MULTILINE,
)

# Pattern: Timestamp prefix like [Thu 2026-03-12 18:39 GMT+8]
_TIMESTAMP_PATTERN = re.compile(
    r"^\[(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+"
    r"\d{4}-\d{2}-\d{2}\s+"
    r"\d{2}:\d{2}\s+"
    r"GMT[+-]\d+\]\s*",
    re.MULTILINE,
)

# System startup message detection
_STARTUP_PATTERN = re.compile(
    r"^A new session was started",
    re.IGNORECASE,
)


def strip_metadata_prefix(text: str) -> str:
    """Remove Sender metadata block and timestamp prefix from user message text."""
    # Step 1: Remove Sender block
    text = _SENDER_PATTERN.sub("", text)

    # Step 2: Remove timestamp prefix
    text = _TIMESTAMP_PATTERN.sub("", text)

    # Step 3: Strip leading/trailing whitespace
    return text.strip()


def is_system_startup_message(text: str) -> bool:
    """Check if a user message is a system startup instruction (should be excluded)."""
    cleaned = strip_metadata_prefix(text)
    return bool(_STARTUP_PATTERN.match(cleaned))
