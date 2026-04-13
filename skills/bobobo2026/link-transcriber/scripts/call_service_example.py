#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import time
from urllib import error, parse, request

DEFAULT_API_BASE_URL = "https://linktranscriber.store/linktranscriber-api"
IN_PROGRESS_STATUSES = {
    "PENDING",
    "PARSING",
    "DOWNLOADING",
    "TRANSCRIBING",
    "SUMMARIZING",
    "FORMATTING",
    "SAVING",
}
DEFAULT_POLL_MAX_ATTEMPTS = 60
DEFAULT_POLL_INTERVAL_SECONDS = 1.0


def infer_platform(url: str) -> str | None:
    lowered = url.lower()
    if "douyin.com" in lowered or "v.douyin.com" in lowered:
        return "douyin"
    if "xiaohongshu.com" in lowered or "xhslink.com" in lowered:
        return "xiaohongshu"
    return None


def http_json(method: str, url: str, *, payload: dict | None = None) -> dict:
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = request.Request(url, data=body, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as json_exc:
            raise RuntimeError(f"HTTP {exc.code}: {raw.strip()}") from json_exc
        if isinstance(parsed, dict):
            return parsed
        raise RuntimeError(f"HTTP {exc.code}: {raw.strip()}")
    except error.URLError as exc:
        raise RuntimeError(f"Request failed: {exc.reason}") from exc
    return json.loads(raw)


def extract_message(payload: dict | None) -> str:
    if not isinstance(payload, dict):
        return "未知错误"
    data = payload.get("data")
    if isinstance(data, dict):
        error_message = data.get("error_message")
        if isinstance(error_message, str) and error_message.strip():
            return error_message.strip()
    msg = payload.get("msg")
    if isinstance(msg, str) and msg.strip():
        return msg.strip()
    return "未知错误"


def format_failure(payload: dict | None) -> str:
    message = extract_message(payload)
    if "Cookie 缺失" in message or "cookie" in message.lower():
        return f"服务端配置问题: {message}"
    return message


def main() -> int:
    if len(sys.argv) not in {2, 3}:
        print("Usage: call_service_example.py <url> [platform]", file=sys.stderr)
        return 1

    base_url = os.getenv("LINK_SKILL_API_BASE_URL", DEFAULT_API_BASE_URL).strip().rstrip("/")
    provider_id = os.getenv("LINK_SKILL_SUMMARY_PROVIDER_ID", "deepseek").strip() or "deepseek"
    model_name = os.getenv("LINK_SKILL_SUMMARY_MODEL_NAME", "deepseek-chat").strip() or "deepseek-chat"
    poll_max_attempts = int(os.getenv("LINK_SKILL_POLL_MAX_ATTEMPTS", str(DEFAULT_POLL_MAX_ATTEMPTS)))
    poll_interval_seconds = float(
        os.getenv("LINK_SKILL_POLL_INTERVAL_SECONDS", str(DEFAULT_POLL_INTERVAL_SECONDS))
    )

    url = sys.argv[1]
    platform = sys.argv[2] if len(sys.argv) == 3 else None
    platform = platform or infer_platform(url)
    if not platform:
        print("Platform could not be inferred. Pass platform explicitly: douyin or xiaohongshu.", file=sys.stderr)
        return 1

    create_payload = {
        "url": url,
        "platform": platform,
    }
    create_result = http_json("POST", f"{base_url}/api/service/transcriptions", payload=create_payload)
    task_id = (((create_result.get("data") or {}).get("task_id")) if isinstance(create_result, dict) else None)
    if not task_id:
        print(format_failure(create_result), file=sys.stderr)
        return 1

    final_result = create_result
    for _ in range(poll_max_attempts):
        polled = http_json("GET", f"{base_url}/api/service/transcriptions/{parse.quote(str(task_id))}")
        final_result = polled
        status = (((polled.get("data") or {}).get("status")) if isinstance(polled, dict) else None) or ""
        if status not in IN_PROGRESS_STATUSES:
            break
        time.sleep(poll_interval_seconds)

    final_status = (((final_result.get("data") or {}).get("status")) if isinstance(final_result, dict) else None) or ""
    if final_status in IN_PROGRESS_STATUSES:
        print(f"转写任务仍在处理中: {task_id} ({final_status})", file=sys.stderr)
        return 1
    if final_status != "SUCCESS":
        print(format_failure(final_result), file=sys.stderr)
        return 1

    summary_payload = {
        "transcription_task_id": str(task_id),
        "provider_id": provider_id,
        "model_name": model_name,
    }
    summary_result = http_json("POST", f"{base_url}/api/service/summaries", payload=summary_payload)
    summary_markdown = (((summary_result.get("data") or {}).get("summary_markdown")) if isinstance(summary_result, dict) else None)
    if summary_markdown:
        print(summary_markdown)
        return 0

    print(format_failure(summary_result), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
