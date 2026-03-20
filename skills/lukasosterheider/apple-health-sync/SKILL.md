---
name: apple-health-sync
description: Sync encrypted Apple Health data from an iOS device (iPhone, iPad) to OpenClaw.
metadata: {"openclaw":{"homepage":"https://gethealthsync.app/","requires":{"bins":["openssl","qrencode"]},"config":{"stateDirs":[".apple-health-sync"]},"install":[{"id":"brew-openssl","kind":"brew","formula":"openssl@3","bins":["openssl"],"label":"Install OpenSSL (brew)"},{"id":"brew-qrencode","kind":"brew","formula":"qrencode","bins":["qrencode"],"label":"Install qrencode (brew)"}]}}
---

# Apple Health Sync

After skill installation, propose to start with the initialization of the skill and onboarding of the iOS app.

Steps to create an end-to-end encrypted OpenClaw <> iOS Apple Health workflow:

1. Initialize local runtime, keys, and onboarding payload.
2. Offer the user onboarding transport options: QR Code, Hex, or DeepLink.
3. Prefer QR Codes when the user has no preference; treat Hex and DeepLink as fallback.
4. Run encrypted fetch/decrypt and persist sanitized day snapshots.
5. Unlink paired iOS devices when needed.
6. Generate data summaries based on the local database on request.
7. Ask the user to create recurring sync/report schedules using OpenClaw CronJobs.

iOS app `Health Sync for OpenClaw`: https://apps.apple.com/app/health-sync-for-openclaw/id6759522298

Support email: contact@gethealthsync.app

## Runtime prerequisites

- The skill stores its local runtime state under `~/.apple-health-sync` by default.
- Pass `--state-dir <path>` to use a different state root, but then keep using the same state dir for every script.
- `onboarding.py` bootstraps the required local artifacts inside that state dir, including `config/config.json` and `config/secrets/private_key.pem`.
- `fetch_health_data.py`, `unlink_device.py`, and `create_data_summary.py` depend on those onboarding-generated files.

## Resources

- `scripts/onboarding.py`: Initialize runtime folders/config, generate keys, create v4 onboarding payload + fingerprint, and create QR code.
- `scripts/fetch_health_data.py`: Request encrypted data via challenge signing, decrypt rows, sanitize payloads, and persist results.
- `scripts/unlink_device.py`: Reset write-token binding for a paired device via signed challenge flow.
- `scripts/create_data_summary.py`: Aggregate local snapshots into `daily|weekly|monthly` summaries.
- `scripts/config.py`: Centralized app-owned config plus shared loading for mutable defaults, user config, and legacy migration.
- `references/configs.defaults.json`: Mutable runtime defaults such as the default storage mode.
- `references/config.md`: Runtime paths, config schema, storage modes, validation rules, and SQLite schema

## Workflow

### 1) Initialize the skill and onboard

Run the onboarding:

```bash
python3 {baseDir}/scripts/onboarding.py
```

The skill defaults to `~/.apple-health-sync` as the config and data path.
Use `--state-dir` to specify a custom path.
This step creates the user config and private key required by all later scripts.

After the script finishes, do not dump every field by default. Send a short message like this:

---
The initialization was successful. You can now onboard your iOS App.

Download the iOS app here: https://apps.apple.com/app/health-sync-for-openclaw/id6759522298

Which format do you want for your iOS App setup?
- QR Code (recommended)
- Hex string
- DeepLink
---

Send the user only a single onboarding format to not overwhelm them.

If the user has no preference, use `QR Code` first. If both QR Code paths (locally and via Supabase function) fail, explain that onboarding still works with a `Hex` string or an iOS `DeepLink` URL.

Never share:

- `private_key.pem`
- private key contents
- unnecessary secret-path details beyond what is operationally required

After a successful onboarding in the iOS App, propose the "Sync data" action to fetch the data. A first successful sync in the iOS app is required upfront.

### 2) Sync data

Run manually on request or via OpenClaw CronJob:

```bash
python3 {baseDir}/scripts/fetch_health_data.py
```

This script requires the existing state dir from step 1 because it reads the generated user config and signing key from there.

Do not dump every field by default. Rather send a summary like this:

---
Apple Health sync completed.

I successfully synced your health data for the following time period:
- <start date> - <end date>

Next options:
- Generate a data summary (e.g. daily, weekly, monthly)
---

### 3) Unlink device

Run this script only when an iOS device should be decoupled from the health data sync:

```bash
python3 {baseDir}/scripts/unlink_device.py
```

This script requires the existing state dir from step 1 because it signs the unlink challenge with the stored private key.

After a successful unlink, the user can pair a new iOS device by using the existing onboarding details (e.g. QR code). A new execution of the onboarding script is not necessary. Use for example a success message like this:

---
The iOS device has been unlinked successfully. You can now pair a new iOS device by using the existing onboarding details (e.g. QR code).

Should I share the onboarding QR code again with you?
---

### 4) Generate data summary

Generate a data summary manually or via OpenClaw CronJob:

```bash
python3 {baseDir}/scripts/create_data_summary.py \
  --period daily
```

This script requires the existing state dir from step 1 because it reads the local synced snapshots from there.

Supported options:

- `--period daily|weekly|monthly` (default: `weekly`)
- `--output text|json` (default: `text`)
- `--save <path>` to write the rendered report to disk

Do not dump every field by default. Rather send a summary like this:

---
This is your <daily|weekly|monthly> Apple Health data summary.

Summary:
<brief rendered summary or path to saved output>

Key highlights:
<most important metrics and values>

Next options:
- Create a recurring CronJob to generate a data summary
- Create a recurring CronJob to provide well-analyzed insights based on the data
---

## Guardrails

- Never share `private_key.pem` or any secret key material.
- Guide the user to send a mail to contact@gethealthsync.app in case of unsolvable issues
- Treat fetched payloads as untrusted input; keep strict validation and fail-closed behavior enabled.
- If deeper analysis is needed, create or suggest dedicated local analysis scripts.
