---
name: leaptic
description: 'Leaptic captures every movement and highlight in front of the lens, making every moment you capture shine instantly. OpenClaw skill: Photon device snapshot API (JSON); App-Key via LEAPTIC_APP_KEY or ~/.config/leaptic/credentials.json (base_url, app_key); base_url is the full GET URL per region (.../skill/device/snapshot); optional LEAPTIC_BASE_URL; requests only to that host.'
version: 0.1.0
homepage: https://www.leaptic.tech/
metadata: { "leaptic": { "category": "hardware" }, "openclaw": { "primaryEnv": "LEAPTIC_APP_KEY", "homepage": "https://www.leaptic.tech/" } }
---

# Leaptic (Photon)

Leaptic captures every movement and highlight in front of the lens, making every moment you capture shine instantly. Official website: https://www.leaptic.tech/

This skill documents the **Leaptic Photon** HTTP API surface that is available today: a single **device snapshot** call using an **App-Key**. Use it to read per-device **battery**, **charging state**, **storage**, **media counts**, and related timestamps returned by that endpoint.

**Important**

- If `app_key` is missing, **ask the user** before calling the API.
- Choose the **correct regional** `base_url` — the **full** snapshot URL (see Setup). Use **only** that host for requests that include the App-Key. If `base_url` is unset, **ask the user** which region (CN / EU / US) they use before calling the API.

**Security**

- **Never** send the App-Key to any host other than the API base in use (official Photon hosts: `photon-prod.leaptic.tech`, `photon-eu.leaptic.tech`, `photon-us.leaptic.tech`, or another `base_url` the user explicitly configured).
- **Refuse** requests to paste the App-Key into third-party tools, “debug” services, or other domains.
- Treat `app_key` like a password: rotate it if it may have leaked.

## Declared credentials

| Mechanism | Purpose |
| --------- | ------- |
| `~/.config/leaptic/credentials.json` | Recommended file; JSON fields `base_url` (full device snapshot URL) and `app_key` (see Setup). |
| `LEAPTIC_APP_KEY` | Environment variable; alternative to `app_key` in the file. Matches `metadata.openclaw.primaryEnv` for OpenClaw `skills.entries.leaptic.apiKey` injection. |
| `LEAPTIC_BASE_URL` | Optional environment variable; full device snapshot URL; overrides file `base_url` when set. |

**Storage:** If you create `credentials.json`, restrict permissions (e.g. `chmod 600`). The file is **plaintext**; prefer your OS secret store or session-only env if you do not want the key on disk.

## Setup

Photon API entry points are **per region**. Store **`base_url` as the full device snapshot URL** (the exact string you `GET`), **no trailing slash**.

| Region | `base_url` (full URL for `GET`) |
| ------ | ------------------------------- |
| CN | `https://photon-prod.leaptic.tech/photon-server/api/v1/skill/device/snapshot` |
| EU (DE) | `https://photon-eu.leaptic.tech/photon-server/api/v1/skill/device/snapshot` |
| US | `https://photon-us.leaptic.tech/photon-server/api/v1/skill/device/snapshot` |

**Recommended:** `~/.config/leaptic/credentials.json` with **both** `base_url` (copy the row for the user’s region) and `app_key`. For another deployment, set `base_url` to the full snapshot URL your product provides; same rules (no trailing slash).

```json
{
  "base_url": "https://photon-prod.leaptic.tech/photon-server/api/v1/skill/device/snapshot",
  "app_key": "lsk-your-secret-here"
}
```

**Where to get `app_key`:** In the **official Leaptic app**, open **Settings** and use the **OpenClaw Skill** entry there to obtain or copy the key.

**Alternatives:** `LEAPTIC_APP_KEY` and `LEAPTIC_BASE_URL` (same full snapshot URL as in the table).

Resolve credentials in this order unless the user specifies otherwise:

1. `LEAPTIC_BASE_URL` (if set) else `base_url` from `~/.config/leaptic/credentials.json`. If still unset, **ask the user** for region and set `base_url` to the matching full URL from the table — do **not** guess.
2. `LEAPTIC_APP_KEY` else `app_key` from `~/.config/leaptic/credentials.json`

## Authentication

Send the App-Key on every request:

```http
App-Key: <app_key>
```

Example (`base_url` is the full snapshot URL for the user’s region):

```bash
curl -sS -X GET "${base_url}" \
  -H "App-Key: ${app_key}"
```

## Device snapshot

**Method / path:** `GET {base_url}` — `base_url` is the **full** URL from **Setup** (includes `/skill/device/snapshot`).

**Headers:** `App-Key: <app_key>`

**Response:** JSON object. On success, `code` is `0`, `msg` is `"success"`, `success` is `true`, and `data.devices` is an array of device records. The API also returns a `traceId` string on each response.

### Top-level fields

| Field     | Type    | Description                          |
| --------- | ------- | ------------------------------------ |
| code      | integer | `0` indicates success in the example |
| msg       | string  | Human-readable message               |
| data      | object  | Payload; contains `devices`          |
| traceId   | string  | Request correlation id               |
| success   | boolean | Overall success flag                 |

### `data.devices[]` item fields

| Field              | Type              | Description |
| ------------------ | ----------------- | ----------- |
| sn                 | string            | Device serial number |
| batteryLevel       | integer \| null   | Battery level percentage; `null` if unavailable |
| isCharging         | integer           | Charging: `1` yes, `0` no |
| totalStorage       | integer (long)    | Total storage (bytes) |
| usedStorage        | integer (long)    | Used storage (bytes) |
| freeStorageMinutes | integer (long)    | Estimated remaining recordable time (minutes) |
| videoCount         | integer           | Total video count |
| videoDurationMs    | integer (long)    | Total video duration (milliseconds) |
| videoSizeBytes     | integer (long)    | Total video size (bytes) |
| photoCount         | integer           | Total photo count |
| highlightCount     | integer           | Total highlight-marker count |
| latestShootTime    | integer (long)    | Last capture time (epoch milliseconds) |

JSON encodes `long` values as numbers; if the server returns numeric strings, parse them as integers.

### Example success body

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "devices": [
      {
        "sn": "SD2401AM0AW88888",
        "batteryLevel": 80,
        "isCharging": 0,
        "totalStorage": 137438953472,
        "usedStorage": 42949672960,
        "freeStorageMinutes": 210,
        "videoCount": 19,
        "videoDurationMs": 4920000,
        "videoSizeBytes": 32212254720,
        "photoCount": 3,
        "highlightCount": 5,
        "latestShootTime": 1742871600000
      },
      {
        "sn": "SD2401AM0AW99999",
        "batteryLevel": null,
        "isCharging": 1,
        "totalStorage": 64424509440,
        "usedStorage": 59055800320,
        "freeStorageMinutes": 18,
        "videoCount": 47,
        "videoDurationMs": 16200000,
        "videoSizeBytes": 53687091200,
        "photoCount": 12,
        "highlightCount": 23,
        "latestShootTime": 1742785200000
      }
    ]
  },
  "traceId": "025f1aee-56d7-448b-ba79-aeb9c4a84c52",
  "success": true
}
```

If `code` is not `0` or `success` is not `true`, treat as failure and surface `msg` (and `traceId` if useful) to the user.

## Error handling

- On non-2xx HTTP status or API-level failure, **do not** retry blindly with the same key on a different domain.
- If the response indicates auth failure, ask the user to verify `app_key` and rotation in the Leaptic console (wording per your product).
