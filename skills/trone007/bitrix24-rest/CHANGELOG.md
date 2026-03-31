# Changelog

## 1.1.6 — 2026-03-31

### Security
- Removed silent runtime `pip install` from code — package installation now only via visible shell commands in agent instructions
- Declared `BITRIX24_KEYRING_PASSWORD` env var in skill metadata (`requires.env_vars`) with fallback behavior description

## 1.1.5 — 2026-03-31

### Security
- Three-level encrypted storage for webhook:
  1. OS keychain (macOS Keychain, Windows Credential Vault, Linux SecretService) — webhook never on disk
  2. AES-256 encrypted file via `keyrings.alt` EncryptedKeyring — for containers and headless servers
  3. Plaintext config with permissions 600 — fallback when encryption packages unavailable
- Agent auto-installs `keyring`, `keyrings.alt`, `pycryptodome` when falling back to plaintext
- OS keyring probe correctly rejects file-based backends (PlaintextKeyring) in containers
- Encryption password derived from env var `BITRIX24_KEYRING_PASSWORD`, `/etc/machine-id`, or built-in default

### Changed
- `bitrix24_config.py`: removed hard dependency on `keyring` — all crypto packages are now optional
- Updated Security Model in SKILL.md with three-level storage description
- Added auto-install instructions for agent in Setup section
- Updated credential metadata: `storage: "auto"` instead of `"os-keychain"`

## 1.1.2 — 2026-03-30

### Fixed
- Added rule: do not use im.*/imbot.* methods for replying to users — the channel plugin handles delivery
- Clarified references/chat.md and references/files.md to separate "reply to user" vs "manage other chats" scenarios

## 1.1.1 — 2026-03-27

### Fixed
- Declared webhook credential in skill metadata (credentials.webhook_url with storage path)
- Softened Rule 2: transparent about connecting to Bitrix24, hides only implementation details
- Rule 1: clarified that user authorized access by providing webhook

## 1.1.0 — 2026-03-27

### Changed
- Switched from Vibe Platform to direct webhook integration
- New scripts: bitrix24_call.py, bitrix24_batch.py, bitrix24_config.py, check_webhook.py, save_webhook.py
- Updated all reference files for webhook-based API
- Landing page updated for webhook setup flow

### Removed
- Vibe Platform scripts (vibe.py, vibe_config.py, check_connection.py)
- Reference files: bots, telephony, workflows, ecommerce, duplicates, timeline-logs

## 1.0.0 — 2026-03-26

Initial release — Bitrix24 REST API skill for OpenClaw.
