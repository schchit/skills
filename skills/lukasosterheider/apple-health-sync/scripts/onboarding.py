#!/usr/bin/env python3
"""
Bootstrap secure identity material for Apple Health sync. Not required to just onboard a new iOS device.
"""

import argparse
import base64
import hashlib
import json
import os
import secrets
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib import error, request
from urllib.parse import quote
from config import (
    APP_CONFIG,
    load_defaults_config,
    load_existing_user_config,
    resolve_state_dir,
    resolve_user_paths,
    write_user_config,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_checked(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def secure_json_write(path: Path, value: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.chmod(tmp_path, 0o600)
    tmp_path.replace(path)


def secure_binary_write(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_bytes(value)
    os.chmod(tmp_path, 0o600)
    tmp_path.replace(path)


def resolve_mutable_string_setting(existing_config: Dict[str, Any], defaults: Dict[str, Any], key: str) -> str:
    existing_value = str(existing_config.get(key, "")).strip()
    if existing_value:
        return existing_value
    return str(defaults.get(key, ""))


def generate_user_id() -> str:
    return "ahs_" + secrets.token_urlsafe(16).rstrip("=")


def ensure_binary(binary_name: str) -> None:
    if shutil.which(binary_name) is None:
        raise RuntimeError(f"Missing required binary: {binary_name}")


def generate_keys(
    private_key_path: Path,
    public_key_path: Path,
    rotate: bool,
) -> str:
    private_exists = private_key_path.exists()
    public_exists = public_key_path.exists()
    if private_exists or public_exists:
        if private_exists and public_exists and not rotate:
            return "existing"
        if not rotate:
            raise RuntimeError("Only one key file exists. Fix manually or run with --rotate.")
        private_key_path.unlink(missing_ok=True)
        public_key_path.unlink(missing_ok=True)

    run_checked(
        [
            "openssl",
            "genpkey",
            "-algorithm",
            "RSA",
            "-pkeyopt",
            "rsa_keygen_bits:2048",
            "-out",
            str(private_key_path),
        ]
    )

    run_checked(["openssl", "pkey", "-in", str(private_key_path), "-pubout", "-out", str(public_key_path)])
    os.chmod(private_key_path, 0o600)
    os.chmod(public_key_path, 0o644)
    return "generated"


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


def http_post_binary(url: str, payload: Dict[str, Any], timeout: int, apikey: str, region: str) -> Tuple[bytes, str]:
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
            content_type = response.headers.get("Content-Type", "")
            return raw, content_type
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


def public_key_base64_from_pem(public_key_pem: str) -> str:
    body = (
        public_key_pem.replace("-----BEGIN PUBLIC KEY-----", "")
        .replace("-----END PUBLIC KEY-----", "")
        .replace("\n", "")
        .replace("\r", "")
        .strip()
    )
    if not body:
        raise RuntimeError("Generated public key PEM is empty.")
    return body


def canonical_json_bytes(value: Dict) -> bytes:
    return json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")


def sha256_hex(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def to_base64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def build_onboarding_payload(
    user_id: str,
    onboarding_version: int,
    algorithm: str,
    public_key_base64: str,
) -> Dict:
    base_payload = {
        "v": onboarding_version,
        "id": user_id,
        "alg": algorithm,
        "publicKeyBase64": public_key_base64,
    }
    fingerprint = sha256_hex(canonical_json_bytes(base_payload))
    payload = dict(base_payload)
    payload["fingerprint"] = fingerprint
    return payload


def ensure_sqlite_schema(sqlite_path: Path) -> None:
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(sqlite_path)
    try:
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
        conn.commit()
    finally:
        conn.close()


def render_qr(payload: str, config_dir: Path) -> Optional[Path]:
    qr_png_path = config_dir / "registration-qr.png"

    if shutil.which("qrencode"):
        subprocess.run(["qrencode", "-t", "ANSIUTF8", payload], check=True)
        subprocess.run(["qrencode", "-o", str(qr_png_path), payload], check=True)
        return qr_png_path

    try:
        import qrcode
    except ImportError:
        print("QR rendering skipped: install 'qrencode' or Python package 'qrcode'.")
        return None

    qr = qrcode.QRCode(border=1)
    qr.add_data(payload)
    qr.make(fit=True)
    qr.print_ascii(invert=True)

    try:
        image = qr.make_image(fill_color="black", back_color="white")
        image.save(qr_png_path)
        return qr_png_path
    except Exception:
        print("QR PNG generation skipped: qrcode backend has no image support.")
        return None


def render_qr_via_supabase(
    payload: str,
    config_dir: Path,
    function_url: str,
    apikey: str,
    region: str,
    user_id: str,
    private_key_path: Path,
    algorithm: str,
    public_key_base64: str,
) -> Path:
    challenge_response = http_post_json(
        function_url,
        {
            "action": "issue_challenge",
            "id": user_id,
        },
        10,
        apikey,
        region,
    )
    challenge = str(challenge_response["challenge"])
    challenge_id = str(challenge_response["challengeId"])
    signature = sign_challenge(private_key_path, challenge, algorithm)

    raw_png, content_type = http_post_binary(
        function_url,
        {
            "action": "render_onboarding_qr",
            "id": user_id,
            "payload": payload,
            "challengeId": challenge_id,
            "signature": signature,
            "public_key": public_key_base64,
        },
        10,
        apikey,
        region,
    )
    if "image/png" not in content_type.lower():
        raise RuntimeError(f"Function response has unexpected content type: {content_type or 'unknown'}")
    if not raw_png.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError("Function response is not a valid PNG payload.")

    qr_png_path = config_dir / "registration-qr.png"
    secure_binary_write(qr_png_path, raw_png)
    return qr_png_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize keypair and config for HealthSync.")
    parser.add_argument(
        "--state-dir",
        default="",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--storage",
        choices=("auto", "sqlite", "json"),
        default="auto",
        help="Default local storage backend for fetch script.",
    )
    parser.add_argument(
        "--rotate",
        action="store_true",
        help="Rotate keys if key files already exist.",
    )
    return parser.parse_args()


def main() -> int:
    os.umask(0o077)
    args = parse_args()
    state_dir = resolve_state_dir(args.state_dir)
    paths = resolve_user_paths(state_dir)
    config_dir = paths["config_dir"]
    secrets_dir = paths["secrets_dir"]
    state_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)
    secrets_dir.mkdir(parents=True, exist_ok=True)

    try:
        ensure_binary("openssl")
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    private_key_path = secrets_dir / "private_key.pem"
    public_key_path = config_dir / "public_key.pem"
    qr_payload_path = config_dir / "registration-qr.json"

    try:
        config_defaults = load_defaults_config()
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    existing_config = load_existing_user_config(state_dir)

    user_id = existing_config.get("user_id") or generate_user_id()
    resolved_ios_app_link = str(APP_CONFIG["ios_app_link"])
    resolved_storage = (
        args.storage
        if args.storage != "auto"
        else resolve_mutable_string_setting(existing_config, config_defaults, "storage")
    )
    resolved_onboarding_version = int(APP_CONFIG["onboarding_version"])
    resolved_supabase_region = str(APP_CONFIG.get("supabase_region", "")).strip()
    resolved_qr_function_url = str(APP_CONFIG.get("supabase_qr_code_generator_url", "")).strip()
    resolved_publishable_key = str(APP_CONFIG.get("supabase_publishable_key", "")).strip()

    try:
        generate_keys(private_key_path, public_key_path, rotate=args.rotate)
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as error:
        print(error.stderr.decode("utf-8", errors="replace"), file=sys.stderr)
        return 1

    public_key_pem = public_key_path.read_text(encoding="utf-8")
    public_key_base64 = public_key_base64_from_pem(public_key_pem)
    algorithm = "RSA-2048"
    onboarding_payload = build_onboarding_payload(
        user_id,
        resolved_onboarding_version,
        algorithm,
        public_key_base64,
    )
    onboarding_payload_compact = json.dumps(onboarding_payload, separators=(",", ":"), sort_keys=True)
    onboarding_payload_hex = onboarding_payload_compact.encode("utf-8").hex()
    onboarding_payload_b64url = to_base64url(onboarding_payload_compact.encode("utf-8"))
    onboarding_deeplink = f"healthsync://onboarding?payload={quote(onboarding_payload_b64url, safe='')}"
    secure_json_write(qr_payload_path, onboarding_payload)

    qr_png_path = None
    qr_render_method = "none"
    try:
        qr_png_path = render_qr(onboarding_payload_compact, config_dir)
    except subprocess.CalledProcessError as error:
        message = error.stderr.decode("utf-8", errors="replace") if error.stderr else str(error)
        print(f"QR rendering failed: {message}")
    if qr_png_path:
        qr_render_method = "local"
    elif resolved_qr_function_url and resolved_publishable_key and resolved_supabase_region:
        try:
            qr_png_path = render_qr_via_supabase(
                onboarding_payload_compact,
                config_dir,
                resolved_qr_function_url,
                resolved_publishable_key,
                resolved_supabase_region,
                user_id,
                private_key_path,
                algorithm,
                public_key_base64,
            )
            qr_render_method = "supabase"
            print("QR fallback succeeded via Supabase.")
        except RuntimeError as error:
            print(f"QR fallback failed: {error}")

    sqlite_path = state_dir / "health_data.db"
    ensure_sqlite_schema(sqlite_path)

    user_config = dict(existing_config)
    user_config.pop("qr_svg_path", None)
    user_config.update(
        {
        "user_id": user_id,
        "algorithm": algorithm,
        "state_dir": str(state_dir),
        "config_dir": str(config_dir),
        "secrets_dir": str(secrets_dir),
        "private_key_path": str(private_key_path),
        "public_key_path": str(public_key_path),
        "public_key_base64": public_key_base64,
        "onboarding_fingerprint": onboarding_payload["fingerprint"],
        "onboarding_payload_json": onboarding_payload_compact,
        "onboarding_payload_hex": onboarding_payload_hex,
        "onboarding_deeplink": onboarding_deeplink,
        "storage": resolved_storage,
        "sqlite_path": str(sqlite_path),
        "json_path": str(config_dir / "health_data.ndjson"),
        "qr_payload_path": str(qr_payload_path),
        "qr_png_path": str(qr_png_path) if qr_png_path else "",
        "qr_render_method": qr_render_method,
        "updated_at": now_iso(),
        }
    )
    write_user_config(user_config, state_dir)

    print("\nInitialization complete.")
    print(f"State dir: {state_dir}")
    print(f"Config dir: {config_dir}")
    print(f"User ID: {user_id}")
    print(f"Public key: {public_key_path}")
    if qr_png_path:
        print(f"QR PNG: {qr_png_path}")
    if not qr_png_path:
        print("QR unavailable: use the DeepLink or Hex onboarding payload.")
    print(f"iOS app link: {resolved_ios_app_link}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
