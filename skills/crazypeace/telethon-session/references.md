# Telethon Session Skill Reference

## Unknown values to request from user

### Required before first real use
These values are stable for a given Telegram app/account setup and must be obtained from the user before first use:

- `api_id` — from https://my.telegram.org
- `api_hash` — from https://my.telegram.org
- `session` — local Telethon session path/name, created by `scripts/login.py`

### Required on each task
These are task inputs and may change every run:

- `username` — target Telegram username / recipient
- `text` — message content to send, only for send actions
- `limit` — how many recent messages to read, only for read actions

## Session handling

- Treat `.session` files like secrets.
- Do not commit `.session` files to git.
- Reuse the same session file until Telegram invalidates it.
- If the session is missing or invalid, run `scripts/login.py` again.

## Typical send flow

1. Ensure `telethon` is installed.
2. Ensure the user has provided `api_id` and `api_hash`.
3. Ensure a valid `.session` file exists.
4. Ask for per-run inputs: `username` and `text`.
5. Run `scripts/send_message.py`.

## Typical read flow

1. Ensure `telethon` is installed.
2. Ensure the user has provided `api_id` and `api_hash`.
3. Ensure a valid `.session` file exists.
4. Ask for per-run inputs: `username` and `limit`.
5. Run `scripts/read_messages.py`.

## Examples

### Send

```bash
python3 scripts/send_message.py \
  --api-id YOUR_ID \
  --api-hash YOUR_HASH \
  --session /path/to/telegram_session \
  --username crazypeace \
  --text '测试信息'
```

### Read multiple recent messages

```bash
python3 scripts/read_messages.py \
  --api-id YOUR_ID \
  --api-hash YOUR_HASH \
  --session /path/to/telegram_session \
  --username crazypeace \
  --limit 10
```
