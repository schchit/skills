# Image Upscale MCP - AI Super Resolution 2x/4x

AI-powered image upscaling with optional face enhancement. Uses Real-ESRGAN (Real Enhanced Super-Resolution GAN) for high-quality 2x or 4x super resolution.

## What It Does

This MCP (Model Context Protocol) actor provides two tools for intelligent image upscaling:

### Tool 1: `upscale_image`
Upscale any image by 2x or 4x without additional processing.
- **Input**: Image URL + scale factor (2 or 4)
- **Output**: Base64 upscaled image + metadata (original/upscaled dimensions, processing time)
- **Pricing**: $0.08 per image

### Tool 2: `enhance_face`
Upscale images with face enhancement (better quality for portraits, profile pictures).
- **Input**: Image URL + scale factor (2 or 4)
- **Output**: Base64 upscaled image + metadata
- **Pricing**: $0.10 per image

## How to Use

### Basic Upscaling (2x)

```json
{
  "image_url": "https://example.com/photo.jpg",
  "scale": 2
}
```

### 4x Super Resolution (Default)

```json
{
  "image_url": "https://example.com/photo.jpg"
}
```

### Face Enhancement for Portrait

```json
{
  "tool_name": "enhance_face",
  "image_url": "https://example.com/portrait.jpg",
  "scale": 4
}
```

## API Response Example

```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "original_size": {
    "width": 512,
    "height": 512
  },
  "upscaled_size": {
    "width": 2048,
    "height": 2048
  },
  "scale": 4,
  "model": "realesrgan-x4plus",
  "processing_time": 3500
}
```

## Technical Details

- **AI Model**: Real-ESRGAN (BSD-3-Clause License)
- **Backend Server**: ai.ntriq.co.kr
- **Supported Scales**: 2x, 4x
- **Input Formats**: URL-based (image must be publicly accessible)
- **Output Format**: Base64-encoded PNG/JPG
- **Processing Time**: 2-6 seconds per image (depending on size and scale)
- **Timeout**: 195 seconds (180s processing + 15s buffer)

## Pricing

| Tool | Price | Use Case |
|------|-------|----------|
| `upscale_image` | $0.08 | General upscaling |
| `enhance_face` | $0.10 | Portraits & faces |

Charged per execution. Free tier: Not available (paid actor).

## Error Handling

- **Missing Image URL**: Returns error 400
- **Invalid Scale**: Only 2 and 4 accepted
- **Server Timeout**: Returns error after 195 seconds
- **Network Error**: Returns detailed error message

## Attribution

Powered by **Real-ESRGAN** (BSD-3-Clause License)
- GitHub: https://github.com/xinntao/Real-ESRGAN
- Paper: Real-ESRGAN: Practical Blind Real-World Super-Resolution with Generative Adversarial Networks

## Requirements

- Public image URL (no authentication required)
- Image size: Recommended max 4MB
- Scale factor: 2 or 4

## Status

Production-ready. Pay-per-event charged by Apify.

## Support

For issues or feature requests, contact the development team.
