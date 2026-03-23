"""Generate a Telethon .session file for user-login to Telegram.

This script is intentionally designed to support *interactive* entry of secrets so you
DON'T have to put sensitive values (api_hash, phone) on the command line.

Usage examples:
    # Fully interactive (recommended)
    python scripts/login.py

    # Specify only session name (still prompts for credentials)
    python scripts/login.py --session telegram_session

    # Non-interactive flags (works, but leaks secrets into shell history)
    python scripts/login.py --api-id 24714103 --api-hash "..." --phone "+8613..."

Interactive prompts:
  - api_id
  - api_hash
  - phone
  - Telegram login code (and 2FA password if enabled)

Output:
  - <session_name>.session (default: telegram_session)
"""

import argparse
import asyncio
import getpass
from pathlib import Path

from telethon import TelegramClient


def _prompt_int(label: str) -> int:
    while True:
        raw = input(label).strip()
        try:
            return int(raw)
        except ValueError:
            print("Please enter a valid integer.")


def _prompt_str(label: str, secret: bool = False) -> str:
    while True:
        raw = (getpass.getpass(label) if secret else input(label)).strip()
        if raw:
            return raw
        print("Value cannot be empty.")


def _normalize_phone(phone: str) -> str:
    # Remove spaces; keep leading '+' if present
    return phone.replace(" ", "")


async def main(args):
    api_id = args.api_id if args.api_id is not None else _prompt_int("App api_id: ")
    api_hash = args.api_hash if args.api_hash else _prompt_str("App api_hash: ", secret=True)
    phone = _normalize_phone(args.phone if args.phone else _prompt_str("Phone number (e.g. +8613...): "))

    client = TelegramClient(args.session, api_id, api_hash)

    # This will prompt for login code + (optional) 2FA password.
    await client.start(phone=phone)

    me = await client.get_me()
    session_path = f"{Path(args.session).resolve()}.session"

    print("\nLogin successful")
    print(f"Name:     {me.first_name} {me.last_name or ''}")
    print(f"Username: @{me.username or 'N/A'}")
    # Avoid printing phone unless user asked for verbose info.
    if args.show_phone:
        print(f"Phone:    {me.phone}")
    print(f"Session:  {session_path}")

    await client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Telethon session file")
    parser.add_argument("--api-id", type=int, default=None, help="Telegram API ID (from my.telegram.org)")
    parser.add_argument("--api-hash", default=None, help="Telegram API hash")
    parser.add_argument("--phone", default=None, help="Phone number with country code, e.g. +86...")
    parser.add_argument("--session", default="telegram_session", help="Session file name (default: telegram_session)")
    parser.add_argument(
        "--show-phone",
        action="store_true",
        help="Print the phone number on success (off by default).",
    )

    asyncio.run(main(parser.parse_args()))
