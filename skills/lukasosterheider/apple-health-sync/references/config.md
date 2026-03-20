# Config reference

This skill now uses a centralized app config module plus two data layers:

- `scripts/config.py`: centralized app-owned configuration and shared config loading
- `references/configs.defaults.json`: mutable user defaults shipped with the skill
- `~/.apple-health-sync/config/config.json`: generated and mutable per-user user config

Required local state:

- The default state root is `~/.apple-health-sync`.
- Passing `--state-dir <path>` moves all required local artifacts under that custom root instead.
- `config/config.json` and `config/secrets/private_key.pem` are created by `scripts/onboarding.py` and are required by later sync and unlink operations.

Legacy note:

- `~/.apple-health-sync/config/runtime.json` is still read as a fallback for older installs, but new writes go to `config.json`.

Effective config order:

1. app-owned values from `scripts/config.py`
2. `references/configs.defaults.json`
3. `config.json` (or legacy `runtime.json`)

App-owned values are centralized in `scripts/config.py`, including:

- `onboarding_version`
- `ios_app_link`
- `supabase_region`
- `supabase_get_data_url`
- `supabase_qr_code_generator_url`
- `supabase_unlink_device_url`
- `supabase_publishable_key`

## Skill-shipped config

`references/configs.defaults.json` contains mutable user defaults:

```json
{
  "storage": "sqlite"
}
```

## User Config

User config defaults to `~/.apple-health-sync`, or the `--state-dir` path when provided:

- SQLite DB: `~/.apple-health-sync/health_data.db`
- User config: `~/.apple-health-sync/config/config.json`
- Private key: `~/.apple-health-sync/config/secrets/private_key.pem`

Typical user config fields:

```json
{
  "user_id": "ahs_...",
  "algorithm": "RSA-2048",
  "state_dir": "/Users/<user>/.apple-health-sync",
  "config_dir": "/Users/<user>/.apple-health-sync/config",
  "secrets_dir": "/Users/<user>/.apple-health-sync/config/secrets",
  "private_key_path": "/Users/<user>/.apple-health-sync/config/secrets/private_key.pem",
  "public_key_path": "/Users/<user>/.apple-health-sync/config/public_key.pem",
  "public_key_base64": "<base64-spki-public-key>",
  "onboarding_fingerprint": "<sha256-hex>",
  "onboarding_payload_json": "<compact-json>",
  "onboarding_payload_hex": "<hex-encoded-json>",
  "onboarding_deeplink": "healthsync://onboarding?payload=<base64url>",
  "storage": "sqlite",
  "sqlite_path": "/Users/<user>/.apple-health-sync/health_data.db",
  "json_path": "/Users/<user>/.apple-health-sync/config/health_data.ndjson",
  "qr_payload_path": "/Users/<user>/.apple-health-sync/config/registration-qr.json",
  "qr_png_path": "/Users/<user>/.apple-health-sync/config/registration-qr.png",
  "qr_render_method": "local",
  "last_validation_raw_days": 7,
  "last_validation_stored_days": 7,
  "last_validation_dropped_days": 0
}
```

Onboarding writes user-owned fields only. App-owned keys such as `onboarding_version`, `ios_app_link`, and the Supabase settings are centralized in `scripts/config.py` and are not persisted back into `config.json`.

## Storage behavior

- `storage=sqlite`: upsert decrypted day payloads into `health_data`
- `storage=json`: append decrypted envelopes to NDJSON

`storage` remains a mutable user field. Existing installs with the removed legacy value `custom` are migrated to `sqlite` when the config is loaded.

## Relay behavior

- `fetch_health_data.py` reads `supabase_region`, `supabase_get_data_url`, and `supabase_publishable_key` from `scripts/config.py`
- `onboarding.py` reads `supabase_region`, `supabase_qr_code_generator_url`, and `supabase_publishable_key` from `scripts/config.py` for remote QR fallback
- `unlink_device.py` reads `supabase_region`, `supabase_unlink_device_url`, and `supabase_publishable_key` from `scripts/config.py`

## Validation behavior in `fetch_health_data.py`

- Accept only date keys in `YYYY-MM-DD`
- Accept only safe metric keys matching `^[A-Za-z0-9_.:-]{1,64}$`
- Accept only JSON values `null`, `bool`, finite numbers, lists, and objects
- Drop all string values to prevent persisted prompt-style instructions
- Enforce depth, node, list, dict, and payload-size limits
- Fail closed when all decrypted day payloads are rejected

## SQLite schema

```sql
create table health_data (
  id integer primary key autoincrement,
  user_id text not null,
  date text not null,
  data text not null,
  created_at text not null,
  updated_at text not null
);
```

CronJobs are created and managed in OpenClaw, not by scripts in this skill.
