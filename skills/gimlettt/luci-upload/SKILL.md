---
name: luci-upload
description: "Upload a video to memories.ai. Use when the user wants to upload a video, add a video to their memory, or send a video to Luci."
metadata: {"clawdbot":{"emoji":"📤","requires":{"bins":["python3","ffprobe"],"env":["MEMORIES_AI_KEY"]},"primaryEnv":"MEMORIES_AI_KEY"}}
---

# luci-upload

Upload a video file to memories.ai with capture time and location metadata.

## Setup

Requires `MEMORIES_AI_KEY` — same key as luci-memory. If not found, create `{baseDir}/.env`:

```
MEMORIES_AI_KEY=sk-your-key-here
```

Also requires `ffprobe` (from ffmpeg) for extracting video metadata.

## When to use
- User wants to upload a video to memories.ai
- User says "add this video to my memory" or similar
- User wants to send/import a video to Luci

## How it works

The script tries to auto-extract capture time and GPS coordinates from the video file metadata (via ffprobe). If metadata is missing, the agent should ask the user for:

1. **When** was the video taken? → pass as `--datetime` with `--timezone`
2. **Where** was it taken? → pass as `--location` (geocoded automatically) or `--lat`/`--lon`

## How to invoke

```bash
# Probe metadata only (no upload) — do this first to check what info is available
bash {baseDir}/run.sh --probe --file /path/to/video.mp4

# Upload with auto-detected metadata
bash {baseDir}/run.sh --file /path/to/video.mp4

# Upload with explicit time and location name (geocoded to lat/lon)
bash {baseDir}/run.sh --file /path/to/video.mp4 --datetime "2025-06-22 14:00:00" --timezone Asia/Shanghai --location "Suzhou, China"

# Upload with explicit coordinates and epoch timestamp
bash {baseDir}/run.sh --file /path/to/video.mp4 --time 1769097600000 --lat 31.3 --lon 120.59
```

## Parameters

| Flag | Short | Description |
|------|-------|-------------|
| `--file` | `-f` | Path to video file (required) |
| `--probe` | | Only show extracted metadata, don't upload |
| `--time` | | Start time as epoch milliseconds |
| `--datetime` | | Start time as readable datetime (e.g. `2025-06-22 14:00:00`) |
| `--timezone` | | Timezone for `--datetime` (e.g. `Asia/Shanghai`, `UTC`, `+8`) |
| `--lat` | | Latitude |
| `--lon` | | Longitude |
| `--location` | | Location name to geocode (e.g. `Suzhou, China`) |

## Workflow

1. **Probe first**: run with `--probe` to see what metadata the video has
2. If time and GPS are both present → upload directly
3. If missing, ask the user for the missing info (time and/or location)
4. Upload with all parameters filled in
