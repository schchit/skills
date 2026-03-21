---
name: dasheng-audio-tag
description: Audio tagging service for environmental sound recognition. Use when user needs to identify environmental sounds in audio files (water sounds, snoring, etc.) or analyze audio content for sound classification.
---

# dasheng-audio-tag

Audio tagging service that identifies environmental sounds in audio files.

## Quick Start

Tag an audio file:
```bash
python3 scripts/audiotag.py <audio_file>
# 服务地址: https://llmplus.ai.xiaomi.com/dasheng/audio/tag
```

Check queue status:
```bash
python3 scripts/audiotag.py --queue
```

## API Details

**Tagging Endpoint:** `POST https://llmplus.ai.xiaomi.com/dasheng/audio/tag`
- Method: POST, multipart form-data with file upload

**Queue Metrics Endpoint:** `POST https://llmplus.ai.xiaomi.com/metrics?path=/dasheng/audio/tag`
- Returns: `active`（当前活跃请求数）、`avg_latency_ms`（平均耗时）
- 预估等待时长 = active × avg_latency_ms

## Usage Patterns

### Basic tagging
```bash
python3 scripts/audiotag.py audio.mp3
```

### Check queue / waiting status
```bash
python3 scripts/audiotag.py --queue
```

### Programmatic usage
```python
from scripts.audiotag import tag_audio, check_queue, format_queue_status

# Tag audio
result = tag_audio("sample-0.mp3")

# Check queue
queue_info = check_queue()
print(format_queue_status(queue_info))
```

## Queue Status（排队情况）

### 何时调用

1. **IM 即将超时但 tag 服务还未返回结果时**：调用 `--queue` 查排队情况，告知用户当前排队状态并请用户稍后来问任务是否完成。
2. **用户稍后询问任务进度但 tag 服务仍未返回时**：调用 `--queue` 返回最新排队情况给用户。

### 返回字段说明

| 字段 | 说明 |
|------|------|
| `active` | 当前活跃请求数（排队中） |
| `avg_latency_ms` | 平均处理耗时（毫秒） |
| `estimated_wait_sec` | 预估等待时长（秒）= active × avg_latency_ms |
| `total_processed` | 累计已处理请求数 |

### 状态分级

- 🟢 active=0 或预估等待 <5s → 服务空闲/很快完成
- 🟡 预估等待 5-30s → 轻微排队
- 🔴 预估等待 >30s → 排队较长，建议稍后重试

## Supported Audio Formats

Common audio formats: mp3, wav, m4a, ogg, flac

## Troubleshooting

- **File not found**: Check the audio file path
- **API request failed**: Verify network connectivity and API endpoint availability
- **Unsupported format**: Try converting to mp3 or wav format
- **Long wait**: Use `--queue` to check current queue status
