---
name: sticker-cog
description: "Create sticker packs and custom emoji sets. Character-consistent expressions, transparent backgrounds, batch generation. WhatsApp, Telegram, Discord, Slack formats. Use for messaging stickers or workspace emoji. Outputs: PNG, WebP, SVG. Powered by CellCog."
metadata:
  openclaw:
    emoji: "✨"
    os: [darwin, linux, windows]
    requires:
      bins: [python3]
      env: [CELLCOG_API_KEY]
author: CellCog
homepage: https://cellcog.ai
dependencies: [cellcog]
---

# Sticker Cog - Custom Sticker Packs With Character Consistency

CellCog creates entire sticker packs where every expression looks like the same character. Transparent backgrounds, batch generation, platform-ready packaging.

---

## Prerequisites

This skill requires the `cellcog` skill for SDK setup and API calls.

```bash
clawhub install cellcog
```

**Read the cellcog skill first** for SDK setup. This skill shows you what's possible.

**OpenClaw agents (fire-and-forget — recommended for long tasks):**
```python
result = client.create_chat(
    prompt="[your task prompt]",
    notify_session_key="agent:main:main",  # OpenClaw only
    task_label="my-task",
    chat_mode="agent",  # See cellcog skill for all modes
)
```

**All other agents (blocks until done):**
```python
result = client.create_chat(
    prompt="[your task prompt]",
    task_label="my-task",
    chat_mode="agent",
)
```

See the **cellcog** mothership skill for complete SDK API reference — delivery modes, timeouts, file handling, and more.

---

## What CellCog Has Internally

CellCog handles sticker creation using its internal models and tools:

1. **Transparent Image Generation Model** — Generates individual stickers with transparent backgrounds. Maintains character reference across batch generations for consistency.
2. **Vector Image Generation Models** — Produces SVG stickers and icons for scalable, resolution-independent output.
3. **Image Generation Models** — For raster stickers with rich detail, various art styles (kawaii, flat, cartoon, pixel art, anime, watercolor, etc.).
4. **Python Processing** — Handles batch conversion, resizing, and format packaging (PNG → WebP, dimension standardization) for platform-specific requirements.

The agent orchestrates: **define character → generate each expression with consistent reference → package for target platform**.

---

## What You Can Create

- Character sticker packs (10-30 consistent expressions from one character description)
- Brand/team emoji sets (mascot or themed reactions for Slack, Discord)
- WhatsApp sticker packs (formatted and ready to import)
- Telegram sticker sets (static PNG/WebP)
- Kawaii/cute sticker collections
- Professional reaction stickers (approved, needs revision, shipped, etc.)
- Stickers from reference photos (pet portraits, self-portraits → cartoon sticker pack)

---

## Platform Specifications

| Platform | Format | Size | Per Pack |
|----------|--------|------|----------|
| WhatsApp | WebP, transparent | 512×512, <100KB each | 3-30 |
| Telegram | PNG or WebP, transparent | 512×512 | Up to 120 |
| Discord | PNG or GIF | 128×128 or 320×320 | Per slot |
| Slack | PNG, GIF, or JPG | 128×128 | Per slot |
| iMessage | PNG, transparent | 300×300 recommended | 10-40 |
| General | PNG, transparent | Any | Any |

---

## Sticker Styles Available

Kawaii, flat design, cartoon, pixel art, watercolor, line art, chibi/anime, 3D render — all supported through the underlying image generation models.

---

## Chat Mode

| Scenario | Recommended Mode |
|----------|------------------|
| Single sticker pack (10-20 stickers), emoji sets | `"agent"` |
| Multiple coordinated packs, brand sticker system | `"agent team"` |
