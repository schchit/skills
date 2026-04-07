# Audio Intelligence MCP Server

Transcribe, summarize, and analyze audio files using local AI models. No external API calls — 100% privacy.

## Features

| Tool | Description | Price |
|------|-------------|-------|
| `transcribe_audio` | Speech-to-text transcription with timestamps | $0.05/use |
| `summarize_audio` | Transcribe + AI summary (brief, detailed, or action items) | $0.10/use |
| `analyze_audio` | Transcribe + comprehensive analysis (speakers, sentiment, topics) | $0.15/use |

## Connect via Claude Desktop

Add to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "audio-intelligence": {
      "url": "https://ntriqpro--audio-intelligence-mcp.apify.actor/mcp?token=YOUR_APIFY_TOKEN"
    }
  }
}
```

## Supported Audio Formats

MP3, WAV, M4A, OGG, FLAC, WebM, and other common audio formats.

## Input

Each tool accepts:
- `audioUrl` (required): URL of the audio file to process
- `summaryType` (summarize only): "brief", "detailed", or "action_items"
- `language` (optional): Response language code (default: "en")

## Output Examples

### transcribe_audio
```json
{
  "status": "success",
  "text": "Hello, welcome to today's meeting...",
  "segments": [
    { "start": 0.0, "end": 3.5, "text": "Hello, welcome to today's meeting." },
    { "start": 3.5, "end": 7.2, "text": "Let's start with the agenda." }
  ],
  "language": "en",
  "model": "whisper-large-v3-turbo"
}
```

### summarize_audio (action_items)
```json
{
  "status": "success",
  "transcript": "...",
  "summary": {
    "action_items": ["Review Q1 report by Friday", "Schedule follow-up meeting"],
    "decisions": ["Approved new budget allocation"],
    "follow_ups": ["Check with legal team on contract"]
  }
}
```

### analyze_audio
```json
{
  "status": "success",
  "transcript": "...",
  "analysis": {
    "speakers_estimated": 2,
    "topics": ["quarterly review", "budget planning"],
    "sentiment": "positive",
    "key_phrases": ["revenue growth", "new market expansion"],
    "summary": "A productive meeting discussing Q1 results and Q2 plans."
  }
}
```

## Technology

- **Speech Recognition**: OpenAI Whisper (MIT License)
- **Text Analysis**: Qwen 3.5 (Apache 2.0 License)
- **Processing**: Local AI inference, zero external API calls
- **Privacy**: Audio files are processed in real-time and not stored

## Open Source Licenses

This service uses the following open source models:
- [OpenAI Whisper](https://github.com/openai/whisper) — MIT License
- [Qwen 3.5](https://huggingface.co/Qwen/Qwen3.5-4B) — Apache 2.0 License

## Legal Disclaimer

**Audio Data Privacy Notice**: Users are solely responsible for ensuring they have obtained all necessary consents and authorizations before submitting audio recordings for processing through this service. This includes compliance with applicable laws regarding recording consent (including but not limited to two-party consent laws). Audio data is processed in real-time and is not stored, retained, or used for model training. This service is provided as a tool for audio analysis and does not constitute legal advice regarding recording or privacy compliance.

Platform usage is free. You only pay per event (see pricing above).
