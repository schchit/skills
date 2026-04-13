---
name: ntriq-alt-text-generator-mcp
description: "Generate accessible alt text and descriptions for images using local AI vision (Qwen2.5-VL). Returns JSON with alt_text and detailed description."
version: 1.0.0
metadata:
  openclaw:
    primaryTag: data-intelligence
    tags: [accessibility,image,vision]
    author: ntriq
    homepage: https://x402.ntriq.co.kr
---

# Alt Text Generator MCP

Generate accessible alt text and rich descriptions for single images using local Qwen2.5-VL vision AI. Returns JSON with `alt_text` (concise, screen-reader friendly) and `description` (detailed narrative). No external API calls — fully local.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image` | string | ✅ | Image URL or base64-encoded data |
| `context` | string | ❌ | Surrounding page context for relevance tuning |
| `max_length` | integer | ❌ | Max chars for alt_text (default: 125) |

## Example Response

```json
{
  "alt_text": "Engineer reviewing circuit board under magnification lamp",
  "description": "A female engineer in a clean room environment examines a green PCB using a magnification lamp. She wears an ESD wrist strap and blue nitrile gloves. Soldering tools are visible in the background.",
  "tags": ["engineering", "electronics", "pcb", "clean-room"],
  "confidence": 0.97
}
```

## Use Cases

- Automated image accessibility for blog CMS plugins
- Legal document image captioning for court filings
- Medical image labeling for EMR systems (on-premise safe)

## Access

```bash
# Service catalog
curl https://x402.ntriq.co.kr/services
```

Available on [Apify Store](https://apify.com/ntriqpro/alt-text-generator-mcp) · [x402 micropayments](https://x402.ntriq.co.kr)
