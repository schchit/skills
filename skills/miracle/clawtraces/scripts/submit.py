# FILE_META
# INPUT:  .trajectory.json files + API key
# OUTPUT: server submission confirmation + manifest.json updates
# POS:    skill scripts — Step 4, depends on lib/auth.py and lib/paths.py
# MISSION: Upload converted trajectories to the ClawTraces collection server.

#!/usr/bin/env python3
"""Submit converted trajectory files to the ClawTraces collection server.

Usage:
    python submit.py [--output-dir PATH] [--count-only]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

sys.path.insert(0, os.path.dirname(__file__))

from lib.auth import get_server_url, get_stored_key, handle_401, get_ssl_context, _format_connection_error

from lib.paths import get_default_output_dir

DEFAULT_OUTPUT_DIR = get_default_output_dir()
MANIFEST_FILENAME = "manifest.json"


def load_manifest(output_dir: str) -> dict:
    """Load the submission manifest."""
    manifest_path = os.path.join(output_dir, MANIFEST_FILENAME)
    if os.path.isfile(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"submitted": {}, "rejected": {}}


def save_manifest(output_dir: str, manifest: dict):
    """Save the submission manifest."""
    manifest_path = os.path.join(output_dir, MANIFEST_FILENAME)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def _load_stats(trajectory_path: str) -> str | None:
    """Load the stats JSON file that corresponds to a trajectory file."""
    # Handle both .trajectory.json and .openai.json paths
    stats_path = trajectory_path.replace(".trajectory.json", ".stats.json").replace(".openai.json", ".stats.json")
    if os.path.isfile(stats_path):
        with open(stats_path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def upload_file(server_url: str, secret_key: str, file_path: str, force: bool = False) -> dict:
    """Upload a trajectory file to the server, with optional stats.

    Args:
        force: If True, overwrite existing submission with same session_id.
    """
    filename = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        file_data = f.read()

    stats_json = _load_stats(file_path)

    boundary = "----ClawTracesBoundary9876543210"
    parts = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: application/json\r\n"
        f"\r\n"
    ).encode("utf-8") + file_data + b"\r\n"

    if stats_json:
        parts += (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="stats"\r\n'
            f"Content-Type: application/json\r\n"
            f"\r\n"
            f"{stats_json}\r\n"
        ).encode("utf-8")

    if force:
        parts += (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="force"\r\n'
            f"\r\n"
            f"true\r\n"
        ).encode("utf-8")

    body = parts + f"--{boundary}--\r\n".encode("utf-8")

    url = f"{server_url}/upload"
    req = Request(
        url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "X-Secret-Key": secret_key,
            "User-Agent": "ClawTraces/1.0",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=30, context=get_ssl_context()) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        if e.code == 401:
            handle_401()
            return {"error": "unauthorized"}
        error_body = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(error_body)
            if "error" not in parsed:
                parsed["error"] = f"HTTP {e.code}"
            return parsed
        except (json.JSONDecodeError, ValueError):
            return {"error": f"HTTP {e.code}", "detail": error_body}
    except URLError as e:
        return {"error": _format_connection_error(e.reason)}


def query_count(server_url: str, secret_key: str) -> dict:
    """Query the server for submission count."""
    url = f"{server_url}/count"
    req = Request(url, headers={"X-Secret-Key": secret_key, "User-Agent": "ClawTraces/1.0"}, method="GET")

    try:
        with urlopen(req, timeout=10, context=get_ssl_context()) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        if e.code == 401:
            handle_401()
            return {"error": "unauthorized"}
        error_body = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(error_body)
            if "error" not in parsed:
                parsed["error"] = f"HTTP {e.code}"
            return parsed
        except (json.JSONDecodeError, ValueError):
            return {"error": f"HTTP {e.code}", "detail": error_body}
    except URLError as e:
        return {"error": _format_connection_error(e.reason)}


def submit_all(output_dir: str, server_url: str, secret_key: str) -> dict:
    """Submit all new trajectory files.

    Returns summary dict with success_count, error_count, total.
    """
    manifest = load_manifest(output_dir)
    submitted = manifest.get("submitted", {})

    all_files = [
        f for f in os.listdir(output_dir)
        if f.endswith(".trajectory.json")
    ]

    new_files = [f for f in all_files if f not in submitted]

    if not new_files:
        count_result = query_count(server_url, secret_key)
        return {
            "success_count": 0,
            "error_count": 0,
            "review_skip_count": 0,
            "new_files": 0,
            "server_total": count_result.get("count", "unknown"),
            "workspace_threshold": count_result.get("workspace_threshold", 5),
            "workspace_submitted": count_result.get("workspace_submitted", False),
        }

    success_count = 0
    error_count = 0
    review_skip_count = 0
    auth_failed = False

    for filename in new_files:
        file_path = os.path.join(output_dir, filename)

        # Validate that agent review (step 3) has been completed
        stats_path = file_path.replace(".trajectory.json", ".stats.json")
        try:
            if os.path.isfile(stats_path):
                with open(stats_path, "r", encoding="utf-8") as f:
                    stats_data = json.load(f)
                if stats_data.get("domain", "pending") == "pending" or not (stats_data.get("title") or "").strip():
                    print(f"  Skipped (pending review): {filename}")
                    review_skip_count += 1
                    continue
        except (json.JSONDecodeError, OSError):
            print(f"  Skipped (stats unreadable): {filename}")
            review_skip_count += 1
            continue

        print(f"  Uploading: {filename}...", end=" ", flush=True)

        result = upload_file(server_url, secret_key, file_path)

        if result.get("error") == "unauthorized":
            print("FAILED (unauthorized)")
            error_count += 1
            auth_failed = True
            break
        elif result.get("error") == "account_disabled":
            msg = result.get("message", "账号已被禁用")
            print(f"FAILED ({msg})")
            error_count += 1
            auth_failed = True
            break
        elif result.get("error") in ("daily_limit_exceeded", "total_limit_exceeded"):
            msg = result.get("message", result["error"])
            print(f"STOPPED ({msg})")
            error_count += 1
            break
        elif result.get("error") == "duplicate":
            # Already on server — record in manifest to avoid retrying
            print("OK (already submitted)")
            success_count += 1
            submitted[filename] = {
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "server_response": "duplicate",
            }
            manifest["submitted"] = submitted
            save_manifest(output_dir, manifest)
        elif "error" in result:
            print(f"FAILED ({result.get('message') or result['error']})")
            error_count += 1
        else:
            print("OK")
            success_count += 1
            submitted[filename] = {
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "server_response": result.get("status", "ok"),
            }
            manifest["submitted"] = submitted
            save_manifest(output_dir, manifest)

    # Only query server count if auth is still valid
    server_total: int | str = "unknown"
    workspace_threshold = 5
    workspace_submitted = False
    daily_count: int | str = "unknown"
    daily_submission_limit = 0
    total_submission_limit = 0
    if not auth_failed:
        count_result = query_count(server_url, secret_key)
        server_total = count_result.get("count", "unknown")
        workspace_threshold = count_result.get("workspace_threshold", 5)
        workspace_submitted = count_result.get("workspace_submitted", False)
        daily_count = count_result.get("daily_count", "unknown")
        daily_submission_limit = count_result.get("daily_submission_limit", 0)
        total_submission_limit = count_result.get("total_submission_limit", 0)

    if review_skip_count > 0:
        print(f"\n  {review_skip_count} file(s) skipped (pending agent review — run step 3 first).", file=sys.stderr)

    return {
        "success_count": success_count,
        "error_count": error_count,
        "review_skip_count": review_skip_count,
        "new_files": len(new_files),
        "server_total": server_total,
        "workspace_threshold": workspace_threshold,
        "workspace_submitted": workspace_submitted,
        "daily_count": daily_count,
        "daily_submission_limit": daily_submission_limit,
        "total_submission_limit": total_submission_limit,
    }


def resubmit_one(session_id: str, output_dir: str, server_url: str, secret_key: str) -> dict:
    """Force-resubmit a single session by session_id.

    Finds the trajectory file in output_dir, uploads with force=True to overwrite
    the existing server record.

    Returns dict with status info.
    """
    # Find trajectory file matching this session_id
    target_filename = f"{session_id}.trajectory.json"
    file_path = os.path.join(output_dir, target_filename)

    if not os.path.isfile(file_path):
        return {"error": f"trajectory file not found: {target_filename}"}

    print(f"  Re-uploading: {target_filename} (force)...", end=" ", flush=True)
    result = upload_file(server_url, secret_key, file_path, force=True)

    if result.get("error") == "unauthorized":
        print("FAILED (unauthorized)")
        return {"error": "unauthorized"}
    elif "error" in result:
        print(f"FAILED ({result['error']})")
        return result
    else:
        updated = result.get("updated", False)
        print("OK (overwritten)" if updated else "OK (new)")

        # Update manifest
        manifest = load_manifest(output_dir)
        submitted = manifest.get("submitted", {})
        submitted[target_filename] = {
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "server_response": "updated" if updated else "ok",
        }
        manifest["submitted"] = submitted
        save_manifest(output_dir, manifest)

        return {
            "status": "ok",
            "updated": updated,
            "total_count": result.get("total_count", "unknown"),
        }


def main():
    parser = argparse.ArgumentParser(description="Submit trajectory files to collection server")
    parser.add_argument("--output-dir", "-o", default=DEFAULT_OUTPUT_DIR, help="Directory with .trajectory.json files")
    parser.add_argument("--count-only", action="store_true", help="Only query submission count")
    parser.add_argument("--resubmit", metavar="SESSION_ID", help="Force-resubmit a specific session by ID")
    args = parser.parse_args()

    key = get_stored_key()
    if not key:
        print("Not authenticated. Please run /clawtraces to authenticate first.", file=sys.stderr)
        sys.exit(1)

    server_url = get_server_url()

    if args.count_only:
        result = query_count(server_url, key)
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        print(f"Total submitted: {result.get('count', 0)}")
        return

    if args.resubmit:
        result = resubmit_one(args.resubmit, args.output_dir, server_url, key)
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        print(f"Resubmit done. Your total submissions: {result.get('total_count', 'unknown')}")
        return

    result = submit_all(args.output_dir, server_url, key)
    review_skipped = result.get('review_skip_count', 0)
    if review_skipped:
        print(f"\nDone: {result['success_count']} uploaded, {result['error_count']} failed, {review_skipped} skipped (pending review)")
    else:
        print(f"\nDone: {result['success_count']} uploaded, {result['error_count']} failed")
    print(f"Your total submissions: {result['server_total']}")

    daily_limit = result.get("daily_submission_limit", 0)
    total_limit = result.get("total_submission_limit", 0)
    if daily_limit > 0:
        print(f"Daily quota: {result.get('daily_count', '?')}/{daily_limit}")
    if total_limit > 0:
        print(f"Total quota: {result['server_total']}/{total_limit}")


if __name__ == "__main__":
    main()
