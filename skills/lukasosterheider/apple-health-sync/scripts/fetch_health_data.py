#!/usr/bin/env python3
"""
Fetch encrypted Apple Health payload from Supabase using challenge signing,
then decrypt day payloads for local storage.
"""

import argparse
import base64
import json
import math
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib import error, request
from config import load_effective_config, resolve_state_dir, resolve_user_paths, write_user_config

MAX_VALIDATION_DEPTH = 12
MAX_VALIDATION_NODES = 20000
MAX_DICT_KEYS = 256
MAX_LIST_ITEMS = 512
MAX_SERIALIZED_DAY_BYTES = 1_000_000
DATE_KEY_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SAFE_METRIC_KEY_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]{1,64}$")
DROP_VALUE = object()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_public_key_base64(value: str) -> str:
    return re.sub(r"\s+", "", value.strip())


def public_key_base64_from_pem(public_key_pem: str) -> str:
    body = (
        public_key_pem.replace("-----BEGIN PUBLIC KEY-----", "")
        .replace("-----END PUBLIC KEY-----", "")
        .replace("\n", "")
        .replace("\r", "")
        .strip()
    )
    if not body:
        raise RuntimeError("Public key PEM is empty.")
    return body


def http_post_json(url: str, payload: Dict[str, Any], timeout: int, apikey: str, region: str) -> Dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url=url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-region": region,
            "apikey": apikey,
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
            return json.loads(raw.decode("utf-8"))
    except error.HTTPError as http_error:
        detail = http_error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {http_error.code} from function: {detail}") from http_error
    except error.URLError as url_error:
        raise RuntimeError(f"Cannot reach function: {url_error}") from url_error


def sign_challenge(private_key_path: Path, challenge: str, algorithm: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as challenge_file:
        challenge_file.write(challenge.encode("utf-8"))
        challenge_file_path = Path(challenge_file.name)
    with tempfile.NamedTemporaryFile(delete=False) as signature_file:
        signature_file_path = Path(signature_file.name)

    algo = algorithm.lower()
    if "rsa" in algo:
        command = [
            "openssl",
            "dgst",
            "-sha256",
            "-sign",
            str(private_key_path),
            "-binary",
            "-out",
            str(signature_file_path),
            str(challenge_file_path),
        ]
    else:
        command = [
            "openssl",
            "pkeyutl",
            "-sign",
            "-rawin",
            "-inkey",
            str(private_key_path),
            "-in",
            str(challenge_file_path),
            "-out",
            str(signature_file_path),
        ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        signature_bytes = signature_file_path.read_bytes()
        return base64.b64encode(signature_bytes).decode("ascii")
    except subprocess.CalledProcessError as sign_error:
        message = sign_error.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"Challenge signing failed: {message}") from sign_error
    finally:
        challenge_file_path.unlink(missing_ok=True)
        signature_file_path.unlink(missing_ok=True)


def read_rsa_block_size(private_key_path: Path) -> int:
    result = subprocess.run(
        ["openssl", "pkey", "-in", str(private_key_path), "-text", "-noout"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    match = re.search(r"Private-Key:\s*\((\d+)\s*bit(?:,.*)?\)", result.stdout)
    if not match:
        raise RuntimeError("Unable to determine RSA key size.")
    key_bits = int(match.group(1))
    return key_bits // 8


def decrypt_rsa_chunk(private_key_path: Path, encrypted_chunk: bytes) -> bytes:
    with tempfile.NamedTemporaryFile(delete=False) as in_file:
        in_file.write(encrypted_chunk)
        in_path = Path(in_file.name)
    with tempfile.NamedTemporaryFile(delete=False) as out_file:
        out_path = Path(out_file.name)

    command = [
        "openssl",
        "pkeyutl",
        "-decrypt",
        "-inkey",
        str(private_key_path),
        "-in",
        str(in_path),
        "-out",
        str(out_path),
        "-pkeyopt",
        "rsa_padding_mode:oaep",
        "-pkeyopt",
        "rsa_oaep_md:sha256",
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return out_path.read_bytes()
    except subprocess.CalledProcessError as decrypt_error:
        message = decrypt_error.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"RSA decrypt failed: {message}") from decrypt_error
    finally:
        in_path.unlink(missing_ok=True)
        out_path.unlink(missing_ok=True)


def decrypt_rsa_chunked_payload(
    private_key_path: Path,
    encrypted_payload_b64: str,
    block_size: int,
) -> bytes:
    encrypted_bytes = base64.b64decode(encrypted_payload_b64)
    if len(encrypted_bytes) % block_size != 0:
        raise RuntimeError(
            "Encrypted payload length does not align with RSA block size."
        )

    output = bytearray()
    for offset in range(0, len(encrypted_bytes), block_size):
        chunk = encrypted_bytes[offset : offset + block_size]
        output.extend(decrypt_rsa_chunk(private_key_path, chunk))
    return bytes(output)


def decrypt_rows(
    rows: List[Dict[str, Any]],
    private_key_path: Path,
    algorithm: str,
) -> Dict[str, Any]:
    decrypted: Dict[str, Any] = {}
    algo = algorithm.lower()
    rsa_block_size = read_rsa_block_size(private_key_path) if "rsa" in algo else 0

    for row in rows:
        date = row.get("date")
        encrypted_data = row.get("data")
        if not isinstance(date, str) or not isinstance(encrypted_data, str):
            continue

        if "rsa" in algo:
            plaintext = decrypt_rsa_chunked_payload(private_key_path, encrypted_data, rsa_block_size)
            decrypted[date] = json.loads(plaintext.decode("utf-8"))
        else:
            # Legacy non-RSA mode: assume value is already JSON or plain string.
            try:
                decrypted[date] = json.loads(encrypted_data)
            except json.JSONDecodeError:
                decrypted[date] = encrypted_data

    return decrypted


def sanitize_value(value: Any, depth: int, counter: List[int]) -> Any:
    if depth > MAX_VALIDATION_DEPTH:
        return DROP_VALUE

    counter[0] += 1
    if counter[0] > MAX_VALIDATION_NODES:
        return DROP_VALUE

    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            return DROP_VALUE
        return value
    if isinstance(value, str):
        # Drop strings to prevent user-controlled prompt content from being persisted.
        return DROP_VALUE
    if isinstance(value, list):
        sanitized_items: List[Any] = []
        for item in value[:MAX_LIST_ITEMS]:
            sanitized = sanitize_value(item, depth + 1, counter)
            if sanitized is DROP_VALUE:
                continue
            sanitized_items.append(sanitized)
        return sanitized_items
    if isinstance(value, dict):
        sanitized_dict: Dict[str, Any] = {}
        item_count = 0
        for key, child in value.items():
            if item_count >= MAX_DICT_KEYS:
                break
            if not isinstance(key, str):
                continue
            key_clean = key.strip()
            if not SAFE_METRIC_KEY_PATTERN.fullmatch(key_clean):
                continue
            sanitized = sanitize_value(child, depth + 1, counter)
            if sanitized is DROP_VALUE:
                continue
            sanitized_dict[key_clean] = sanitized
            item_count += 1
        return sanitized_dict
    return DROP_VALUE


def sanitize_decrypted_payload(raw_payload: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, int]]:
    sanitized_payload: Dict[str, Any] = {}
    metrics = {
        "raw_days": 0,
        "stored_days": 0,
        "dropped_days": 0,
    }
    counter = [0]

    for date_key, payload in raw_payload.items():
        metrics["raw_days"] += 1
        if not isinstance(date_key, str) or not DATE_KEY_PATTERN.fullmatch(date_key):
            metrics["dropped_days"] += 1
            continue

        sanitized = sanitize_value(payload, depth=0, counter=counter)
        if sanitized is DROP_VALUE:
            metrics["dropped_days"] += 1
            continue
        if isinstance(sanitized, (dict, list)) and not sanitized:
            metrics["dropped_days"] += 1
            continue

        serialized = json.dumps(sanitized, separators=(",", ":"))
        if len(serialized.encode("utf-8")) > MAX_SERIALIZED_DAY_BYTES:
            metrics["dropped_days"] += 1
            continue

        sanitized_payload[date_key] = sanitized
        metrics["stored_days"] += 1

    return sanitized_payload, metrics


def ensure_sqlite_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        create table if not exists health_data (
          id integer primary key autoincrement,
          user_id text not null,
          date text not null,
          data text not null,
          created_at text not null,
          updated_at text not null
        );
        """
    )
    conn.execute(
        "create unique index if not exists health_data_user_date_idx "
        "on health_data (user_id, date);"
    )
    migrate_legacy_health_samples(conn)
    conn.commit()


def migrate_legacy_health_samples(conn: sqlite3.Connection) -> None:
    table_exists = conn.execute(
        "select 1 from sqlite_master where type='table' and name='health_samples' limit 1"
    ).fetchone()
    if not table_exists:
        return

    legacy_rows = conn.execute(
        "select record_id, fetched_at, payload_json from health_samples"
    ).fetchall()
    for user_id, fetched_at, payload_json in legacy_rows:
        try:
            payload = json.loads(payload_json)
            if not isinstance(payload, dict):
                continue
            for date_key, day_payload in payload.items():
                if not isinstance(date_key, str):
                    continue
                serialized = json.dumps(day_payload, separators=(",", ":"))
                conn.execute(
                    """
                    insert into health_data(user_id, date, data, created_at, updated_at)
                    values (?, ?, ?, ?, ?)
                    on conflict(user_id, date) do update
                      set data=excluded.data,
                          updated_at=excluded.updated_at
                    """,
                    (user_id, date_key, serialized, fetched_at, fetched_at),
                )
        except Exception:
            continue


def write_sqlite(sqlite_path: Path, user_id: str, fetched_at: str, data: Dict[str, Any]) -> None:
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(sqlite_path)
    try:
        ensure_sqlite_schema(conn)
        for date_key, day_payload in data.items():
            if not isinstance(date_key, str):
                continue
            serialized = json.dumps(day_payload, separators=(",", ":"))
            conn.execute(
                """
                insert into health_data(user_id, date, data, created_at, updated_at)
                values (?, ?, ?, ?, ?)
                on conflict(user_id, date) do update
                  set data=excluded.data,
                      updated_at=excluded.updated_at
                """,
                (user_id, date_key, serialized, fetched_at, fetched_at),
            )
        conn.commit()
    finally:
        conn.close()


def write_ndjson(json_path: Path, envelope: Dict[str, Any]) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with json_path.open("a", encoding="utf-8") as file_handle:
        file_handle.write(json.dumps(envelope, separators=(",", ":")) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch and store Apple Health data from Supabase.")
    parser.add_argument(
        "--state-dir",
        default="",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--apikey",
        default="",
        help="Supabase publishable key for Edge Function header validation.",
    )
    parser.add_argument("--user-id", default="")
    parser.add_argument("--record-id", default="", help=argparse.SUPPRESS)
    parser.add_argument("--private-key-path", default="")
    parser.add_argument("--public-key", default="")
    parser.add_argument(
        "--storage",
        choices=("auto", "sqlite", "json"),
        default="auto",
    )
    parser.add_argument("--sqlite-path", default="")
    parser.add_argument("--json-path", default="")
    parser.add_argument("--timeout-seconds", type=int, default=20)
    return parser.parse_args()


def resolve_runtime(
    args: argparse.Namespace,
    config: Dict[str, Any],
    paths: Dict[str, Path],
) -> Tuple[str, str, Path, str, str]:
    function_url = str(config.get("supabase_get_data_url", "")).strip()
    user_id = args.user_id or args.record_id or config.get("user_id", "") or config.get("record_id", "")
    private_key_path = Path(
        args.private_key_path or config.get("private_key_path", paths["secrets_dir"] / "private_key.pem")
    ).expanduser()
    algorithm = str(config.get("algorithm", "RSA-2048"))
    public_key_base64 = normalize_public_key_base64(args.public_key or config.get("public_key_base64", ""))

    if not public_key_base64:
        public_key_path = Path(config.get("public_key_path", paths["config_dir"] / "public_key.pem")).expanduser()
        if public_key_path.exists():
            public_key_base64 = public_key_base64_from_pem(public_key_path.read_text(encoding="utf-8"))
        else:
            raise RuntimeError(
                "Missing public key. Set --public-key or config.public_key_base64/public_key_path."
            )

    if not user_id:
        raise RuntimeError("Missing user ID. Set --user-id or config.user_id.")
    if not function_url:
        raise RuntimeError("Missing app-owned get-data URL in scripts/config.py.")
    if not private_key_path.exists():
        raise RuntimeError(f"Missing private key file: {private_key_path}")
    return function_url, user_id, private_key_path, algorithm, public_key_base64


def main() -> int:
    args = parse_args()
    state_dir = resolve_state_dir(args.state_dir)
    paths = resolve_user_paths(state_dir)
    user_config: Dict[str, Any] = {}
    config: Dict[str, Any] = {}

    try:
        user_config, config = load_effective_config(state_dir)
        function_url, user_id, private_key_path, algorithm, public_key_base64 = resolve_runtime(args, config, paths)
        publishable_key = args.apikey or str(config.get("supabase_publishable_key", "")).strip()
        region = str(config.get("supabase_region", "")).strip()
        if not publishable_key:
            raise RuntimeError("Missing app-owned publishable key in scripts/config.py or --apikey.")
        if not region:
            raise RuntimeError("Missing app-owned Supabase region in scripts/config.py.")
        challenge_response = http_post_json(
            function_url,
            {"action": "issue_challenge", "id": user_id},
            args.timeout_seconds,
            publishable_key,
            region,
        )

        challenge = challenge_response["challenge"]
        challenge_id = challenge_response["challengeId"]
        signature = sign_challenge(private_key_path, challenge, algorithm)

        data_response = http_post_json(
            function_url,
            {
                "action": "get_data",
                "id": user_id,
                "challengeId": challenge_id,
                "signature": signature,
                "public_key": public_key_base64,
            },
            args.timeout_seconds,
            publishable_key,
            region,
        )

        encrypted_rows = data_response.get("data", [])
        if not isinstance(encrypted_rows, list):
            raise RuntimeError("Invalid get_data response format (data must be list).")

        decrypted_payload = decrypt_rows(encrypted_rows, private_key_path, algorithm)
        sanitized_payload, validation_metrics = sanitize_decrypted_payload(decrypted_payload)
        fetched_at = now_iso()
        envelope = {
            "user_id": user_id,
            "fetched_at": fetched_at,
            "payload": sanitized_payload,
            "row_count": len(encrypted_rows),
            "validation": validation_metrics,
        }

        if validation_metrics["raw_days"] > 0 and validation_metrics["stored_days"] == 0:
            raise RuntimeError("Validation rejected all decrypted rows; nothing stored.")

        storage = args.storage
        if storage == "auto":
            storage = config.get("storage", "sqlite")

        if storage == "sqlite":
            sqlite_path = Path(args.sqlite_path or config.get("sqlite_path", state_dir / "health_data.db"))
            write_sqlite(sqlite_path.expanduser(), user_id, fetched_at, sanitized_payload)
        elif storage == "json":
            json_path = Path(args.json_path or config.get("json_path", paths["config_dir"] / "health_data.ndjson"))
            write_ndjson(json_path.expanduser(), envelope)
        else:
            raise RuntimeError(f"Unsupported storage backend: {storage}")

        user_config["last_fetch_at"] = fetched_at
        user_config["last_fetch_status"] = "ok"
        user_config["last_fetch_row_count"] = len(encrypted_rows)
        user_config["last_validation_raw_days"] = validation_metrics["raw_days"]
        user_config["last_validation_stored_days"] = validation_metrics["stored_days"]
        user_config["last_validation_dropped_days"] = validation_metrics["dropped_days"]
        write_user_config(user_config, state_dir)

        print(
            f"Fetch successful: user_id={user_id}, storage={storage}, "
            f"rows={len(encrypted_rows)}, stored_days={validation_metrics['stored_days']}, "
            f"dropped_days={validation_metrics['dropped_days']}, fetched_at={fetched_at}"
        )
        return 0
    except Exception as runtime_error:
        print(f"Error: {runtime_error}", file=sys.stderr)
        try:
            if user_config:
                user_config["last_fetch_at"] = now_iso()
                user_config["last_fetch_status"] = "error"
                user_config["last_fetch_error"] = str(runtime_error)
                write_user_config(user_config, state_dir)
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
