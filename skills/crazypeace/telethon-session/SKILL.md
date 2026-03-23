---
name: telethon-session
description: Generate Telethon .session files for user-account login to Telegram. Use when: (1) user wants to test a Telegram bot as a real user, (2) user needs to interact with Telegram via user identity, (3) creating a Telegram session for Telethon-based automation, (4) mentions telethon, telegram session, or user-account login. NOT for: bot-token-based bots (no session needed).
---

# Telethon Session Generator

Generate a `.session` file to authenticate a Telegram **user account** via Telethon.

## Prerequisites

- `telethon` (install in a venv)
- API credentials from <https://my.telegram.org> (`api_id` + `api_hash`)

## Recommended: set as system environment variables

Set these once, then you won't need to re-type them:

- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_PHONE`
- (optional) `TELETHON_SESSION` (default: `telegram_session`)

### One-command interactive setup (writes a local .env)

Run:

```bash
bash scripts/setup_env.sh
```

This script will:
- Prompt you interactively for the 3 values (api_id/api_hash/phone)
- Write them to `.env` (gitignored)
- Tell you the exact `source` command to load them into your current shell

### Option A: put them in a local `.env` file (recommended)

In this skill directory, create `.env` (it is ignored by git):

```bash
TELEGRAM_API_ID=__SET_ME__
TELEGRAM_API_HASH=__SET_ME__
TELEGRAM_PHONE=__SET_ME__
TELETHON_SESSION=telegram_session
```

Lock down file permissions:

```bash
chmod 600 .env
```

Template: `.env.example`

### Option B: export them in your shell

```bash
export TELEGRAM_API_ID=__SET_ME__
export TELEGRAM_API_HASH="..."
export TELEGRAM_PHONE="+8613..."
export TELETHON_SESSION=telegram_session
```

## Quick Start (generate session)

### Interactive (safe: avoids putting secrets in command history)

```bash
python3 scripts/login.py --session telegram_session
```

The script will prompt for:
- `api_id`
- `api_hash` (hidden)
- `phone`
- Telegram login code (+ optional 2FA password)

On success, `<session_name>.session` is created in the working directory.

## Common actions

### Send a message

```bash
python3 scripts/send_message.py --api-id YOUR_ID --to @username --message "hi" --session telegram_session
```

(or omit `--api-hash` to be prompted with hidden input)

### Read last messages from a dialog

```bash
python3 scripts/read_dialog.py --api-id YOUR_ID --with @username --limit 3 --session telegram_session
```

## Key Notes

- **Session file is reusable** — no need to re-login unless Telegram invalidates it
- **Do NOT commit `.session` files** to version control (treat as secrets)
- **Bot token ≠ session** — bots use `bot_token=` in Telethon, no session file needed
- If `pip install telethon` fails on externally-managed Python, use a venv:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install telethon
  ```

## Using the Session File (code)

```python
from telethon import TelegramClient

client = TelegramClient('telegram_session', api_id, api_hash)
await client.start()  # auto-loads session, no prompt needed
```
