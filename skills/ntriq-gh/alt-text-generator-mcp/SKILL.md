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

# Alt Text Generator

Generate accessible alt text and descriptions for images using local AI vision (Qwen2.5-VL). Returns JSON with alt_text and detailed description.

## Usage

### x402 Payment (AI agents)
```bash
curl -X POST https://x402.ntriq.co.kr/alt-text \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/doc.png"}'
# Returns 402 → auto-pay USDC → get result
```

### Service Catalog
```bash
curl https://x402.ntriq.co.kr/services
```

## Features
- 100% local AI inference (zero external API calls)
- x402 micropayments (USDC on Base)
- Sub-10 second processing
- JSON structured output

## Powered by
- [ntriq Data Intelligence](https://x402.ntriq.co.kr)
- Qwen2.5-VL (vision) + Qwen2.5 (text) local inference
