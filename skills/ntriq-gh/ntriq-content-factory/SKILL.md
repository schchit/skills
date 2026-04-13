---
name: ntriq-content-factory
description: "Transform any text into 8 content types: Q&A, reports, quizzes, flashcards, mind maps, data tables, slide decks, and podcast scripts. Plus TTS audio generation. All powered by local AI — zero exter..."
version: 1.0.0
metadata:
  openclaw:
    primaryTag: data-intelligence
    tags: [media,content]
    author: ntriq
    homepage: https://x402.ntriq.co.kr
---

# Content Factory

Transform any text into 8 content formats plus TTS audio. Upload articles, reports, or meeting transcripts; receive Q&A sets, quizzes, flashcards, mind maps, data tables, slide decks, podcast scripts, and MP3 audio — all powered by local AI with zero external dependencies.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source_text` | string | ✅ | Input content (max 50,000 chars) |
| `output_types` | array | ✅ | Formats: `qa`, `quiz`, `flashcards`, `mindmap`, `table`, `slides`, `podcast`, `audio` |
| `voice` | string | ❌ | TTS voice for audio: `neutral`, `male`, `female` |
| `topic_focus` | string | ❌ | Specific topic to emphasize |

## Example Response

```json
{
  "quiz": {
    "questions": [
      {"question": "Which regulation mandates breach notification within 72 hours?", "options": ["GDPR","CCPA","HIPAA","SOX"], "answer": "GDPR", "explanation": "GDPR Article 33 requires notification within 72 hours of breach awareness."}
    ]
  },
  "audio_url": "/output/content_factory_audio_20240408.mp3",
  "podcast_script": "Welcome to today's deep dive on GDPR compliance. Let's start with the basics..."
}
```

## Use Cases

- Corporate compliance training content production
- Product documentation to customer FAQ conversion
- Research paper to podcast episode pipeline

## Access

```bash
# Service catalog
curl https://x402.ntriq.co.kr/services
```

Available on [Apify Store](https://apify.com/ntriqpro/content-factory) · [x402 micropayments](https://x402.ntriq.co.kr)
