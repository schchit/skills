![banner](./banner.webp)

<!--skill-metadata
name: wallpaper-claw-skill
description: Generate stunning AI wallpapers for mobile, desktop, ultrawide, and iPad.
emoji: "🖼️"
requires: [NETA_TOKEN, node]
-->

# Wallpaper Claw Skill

> Core tool: `node wallpaper.js` — generates perfectly-sized AI wallpapers for any device.

---

## 0. Initialization

On trigger, **immediately output**:
```
🖼️ Wallpaper generator ready. What do you want on your screen?
```

**Trigger conditions:**
- User says: wallpaper / background / lockscreen / homescreen / desktop background
- User says: "make me a wallpaper of..." / "generate a phone wallpaper"

---

## 1. Device Selection

If the user doesn't specify a device, ask:

```
Which device is this for?
```

Quick buttons:
- `📱 Mobile` → `@{bot_name} mobile wallpaper`
- `🖥️ Desktop` → `@{bot_name} desktop wallpaper`
- `📺 Ultrawide` → `@{bot_name} ultrawide wallpaper`
- `📋 iPad` → `@{bot_name} ipad wallpaper`

| Device | Size | Best for |
|--------|------|----------|
| `mobile` | 576×1024 (9:16) | iPhone, Android |
| `desktop` | 1024×576 (16:9) | Laptop, monitor |
| `ultrawide` | 1024×432 (21:9) | Ultrawide monitor |
| `ipad` | 768×1024 (3:4) | iPad, tablet |

---

## 2. Generation

```bash
node wallpaper.js gen "<prompt>" --device mobile
# stderr: 📱 Generating Mobile (9:16) wallpaper...
# stderr: 🎨 Rendering at 576×1024...
# stderr: ⏳ Task submitted: xxx
# stdout: {"status":"SUCCESS","url":"https://...","device":"mobile","width":576,"height":1024}
```

With character:
```bash
node wallpaper.js gen "standing on a rooftop at sunset" --device mobile --char "character name" --style "cinematic"
```

---

## 3. Display Result

```
━━━━━━━━━━━━━━━━━━━━━━━━
🖼️ Your {device} wallpaper is ready!
{image_url}
━━━━━━━━━━━━━━━━━━━━━━━━
```

Quick buttons:
- `Try another style 🎨` → `@{bot_name} same scene, different style`
- `Other device 📱` → `@{bot_name} make it for desktop`
- `New wallpaper 🔄` → `@{bot_name} generate a new wallpaper`

---

## 4. Style Quick Picks

| Style | Prompt keyword |
|-------|---------------|
| 🌌 Space | "galaxy, nebula, stars, cosmic" |
| 🌊 Ocean | "ocean waves, deep sea, underwater" |
| 🏔️ Nature | "mountain landscape, forest, misty" |
| 🌆 City | "city skyline, neon lights, night" |
| 🎨 Abstract | "abstract art, geometric, colorful" |
| 🌸 Minimal | "minimalist, soft pastel, clean" |
| 🔥 Dark | "dark fantasy, dramatic shadows" |
| ☀️ Bright | "vibrant, sunny, warm tones" |

---

## 5. Error Handling

| Error | Message |
|-------|---------|
| Token missing | "Add `NETA_TOKEN=...` to `~/.openclaw/workspace/.env`" |
| status=FAILURE | ⚠️ Generation failed — try simplifying the prompt |
| status=TIMEOUT | ⏳ Timed out — retry with the same prompt |

---

## CLI Reference

```bash
node wallpaper.js gen "<prompt>" \
  --device  mobile        \   # mobile | desktop | ultrawide | ipad
  --char    "<name>"      \   # optional character
  --pic     "<uuid>"      \   # optional character reference image
  --style   "cinematic"       # optional, repeatable
```

**Output (JSON):**
```json
{
  "status": "SUCCESS",
  "url": "https://oss.talesofai.cn/picture/<task_uuid>.webp",
  "task_uuid": "...",
  "device": "mobile",
  "width": 576,
  "height": 1024
}
```

## Setup

Add your API token to `~/.openclaw/workspace/.env`:
```
NETA_TOKEN=your_token_here
```
