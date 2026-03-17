---
name: wallpaper-claw-skill
description: Generate stunning AI wallpapers for mobile, desktop, ultrawide, and iPad — sized perfectly for each device in one command.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - NETA_TOKEN
      bins:
        - node
    primaryEnv: NETA_TOKEN
    emoji: "🖼️"
    homepage: https://github.com/BarbaraLedbettergq/wallpaper-claw-skill
---

# Wallpaper Claw Skill

Generate stunning AI wallpapers sized perfectly for any device — mobile, desktop, ultrawide, or iPad — in a single command.

## Helper script

```bash
node wallpaper.js gen "<prompt>" [--device mobile|desktop|ultrawide|ipad] [--char <name>] [--style <name>]
# → {"status":"SUCCESS","url":"https://...","width":576,"height":1024}
```

The agent handles all prompt crafting and style decisions. The script only calls the image generation API.

## Device Presets

| Device | Size | Ratio | Best for |
|--------|------|-------|---------|
| `mobile` | 576×1024 | 9:16 | iPhone, Android lock screens |
| `desktop` | 1024×576 | 16:9 | Monitor backgrounds |
| `ultrawide` | 1024×432 | 21:9 | Ultrawide monitors |
| `ipad` | 768×1024 | 3:4 | iPad home/lock screens |

## Usage Examples

```bash
# Mobile wallpaper
node wallpaper.js gen "misty mountain at sunrise, soft pink sky" --device mobile

# Desktop wallpaper with style
node wallpaper.js gen "futuristic city at night" --device desktop --style cyberpunk

# Character wallpaper
node wallpaper.js gen "standing in forest" --device mobile --char "Aria"
```

## Setup

Add your token to `~/.openclaw/workspace/.env`:

```
NETA_TOKEN=your_token_here
```
