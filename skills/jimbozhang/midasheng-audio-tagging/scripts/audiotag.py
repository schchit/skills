#!/usr/bin/env python3
"""
AudioTag API Client - Audio tagging service for environmental sound recognition
识别环境音（水声、鼾声等）
支持排队情况查询（metrics）
"""

import sys
import json
import requests
from pathlib import Path

API_BASE = "https://llmplus.ai.xiaomi.com"


def check_queue(api_base: str = API_BASE) -> dict:
    """
    查询 audiotag 服务的排队情况

    Returns:
        dict: 包含 active（活跃请求数）、avg_latency_ms（平均耗时）、estimated_wait_ms（预估等待时长）等
    """
    url = f"{api_base}/metrics?path=/dasheng/audio/tag"
    response = requests.post(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    active = data.get("active", 0)
    avg_latency_ms = data.get("avg_latency_ms", 0)
    # 预估等待时长 = 活跃请求数 × 平均耗时
    estimated_wait_ms = active * avg_latency_ms

    return {
        "active": active,
        "avg_latency_ms": round(avg_latency_ms, 1),
        "estimated_wait_ms": round(estimated_wait_ms, 1),
        "estimated_wait_sec": round(estimated_wait_ms / 1000, 1),
        "total_processed": data.get("total", 0),
        "min_latency_ms": data.get("min_latency_ms", 0),
        "max_latency_ms": data.get("max_latency_ms", 0),
        "raw": data
    }


def format_queue_status(queue_info: dict) -> str:
    """
    将排队信息格式化为用户友好的文本

    Args:
        queue_info: check_queue() 的返回值

    Returns:
        str: 格式化的排队状态文本
    """
    active = queue_info["active"]
    avg_ms = queue_info["avg_latency_ms"]
    wait_sec = queue_info["estimated_wait_sec"]

    if active == 0:
        return f"🟢 当前无排队，服务空闲（平均处理耗时 {avg_ms}ms）"
    elif wait_sec < 5:
        return f"🟢 当前 {active} 个请求处理中，预计等待 {wait_sec}s（平均耗时 {avg_ms}ms）"
    elif wait_sec < 30:
        return f"🟡 当前 {active} 个请求排队中，预计等待约 {wait_sec}s（平均耗时 {avg_ms}ms）"
    else:
        return f"🔴 当前 {active} 个请求排队中，预计等待约 {wait_sec}s（约 {round(wait_sec/60, 1)} 分钟），建议稍后再试"


def tag_audio(audio_file: str, api_url: str = f"{API_BASE}/dasheng/audio/tag") -> dict:
    """
    Tag audio file for environmental sounds

    Args:
        audio_file: Path to audio file (mp3, wav, etc.)
        api_url: AudioTag API endpoint

    Returns:
        dict: API response with tagging results
    """
    audio_path = Path(audio_file)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    # Determine MIME type based on file extension
    suffix = audio_path.suffix.lower()
    mime_types = {
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.m4a': 'audio/mp4',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac'
    }
    mime_type = mime_types.get(suffix, 'audio/wav')

    with open(audio_path, 'rb') as f:
        files = {'file': (audio_path.name, f, mime_type)}
        response = requests.post(api_url, files=files)

    response.raise_for_status()
    return response.json()


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  audiotag.py <audio_file> [api_url]   # Tag audio file")
        print("  audiotag.py --queue                   # Check queue status")
        print()
        print("Examples:")
        print("  audiotag.py sample-0.mp3")
        print("  audiotag.py sample-0.mp3 https://llmplus.ai.xiaomi.com/dasheng/audio/tag")
        print("  audiotag.py --queue")
        sys.exit(1)

    # Queue status check
    if sys.argv[1] == "--queue":
        try:
            queue_info = check_queue()
            print(format_queue_status(queue_info))
            print()
            print(json.dumps(queue_info, indent=2, ensure_ascii=False))
        except requests.exceptions.RequestException as e:
            print(f"Error checking queue: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # Audio tagging
    audio_file = sys.argv[1]
    api_url = sys.argv[2] if len(sys.argv) > 2 else f"{API_BASE}/dasheng/audio/tag"

    try:
        result = tag_audio(audio_file, api_url)
        print(f"Audio tagging result for: {audio_file}")
        print("-" * 50)

        # Pretty print the result
        if isinstance(result, dict):
            if 'tags' in result:
                print(f"Processing time: {result.get('processing_time', 'N/A')}s")
                print(f"Model: {result.get('model', 'N/A')}")
                print(f"Device: {result.get('device', 'N/A')}")
                print("\nDetected environmental sounds:")
                print("-" * 50)
                for tag in result['tags']:
                    label = tag.get('label', 'Unknown')
                    score = tag.get('score', 0)
                    confidence = f"{score * 100:.1f}%"
                    print(f"  • {label:30s} {confidence:>8s}")
            else:
                for key, value in result.items():
                    print(f"{key}: {value}")
        else:
            print(result)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
