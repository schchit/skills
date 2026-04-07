---
name: ntriq-audio-intelligence-mcp
description: "Transcribe, summarize, and analyze audio files using local Whisper + Qwen. Returns transcript, segments, and action items."
version: 1.0.0
metadata:
  openclaw:
    primaryTag: data-intelligence
    tags: [audio,transcription,analysis]
    author: ntriq
    homepage: https://x402.ntriq.co.kr
---

# Audio Intelligence

Transcribe, summarize, and analyze audio files using local Whisper + Qwen. Returns transcript, segments, and action items.

## Usage

### x402 Payment (AI agents)
```bash
curl -X POST https://x402.ntriq.co.kr/audio-intel \
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
