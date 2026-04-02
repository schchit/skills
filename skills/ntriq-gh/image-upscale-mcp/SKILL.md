---
name: ntriq-image-upscale-mcp
description: "Image super-resolution upscaling (2x/4x) using Real-ESRGAN. Optional face enhancement."
version: 1.0.0
metadata:
  openclaw:
    primaryTag: data-intelligence
    tags: [image,upscale,enhancement]
    author: ntriq
    homepage: https://x402.ntriq.co.kr
---

# Image Upscale

Image super-resolution upscaling (2x/4x) using Real-ESRGAN. Optional face enhancement.

## Usage

### x402 Payment (AI agents)
```bash
curl -X POST https://x402.ntriq.co.kr/image-upscale \
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
