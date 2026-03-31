#!/usr/bin/env python3
"""Shared helpers for Bitrix24 skill scripts."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from pathlib import Path

WEBHOOK_RE = re.compile(r"^https://(?P<host>[^/]+)/rest/(?P<user_id>\d+)/(?P<secret>[^/]+)/?$")
DEFAULT_CONFIG_PATH = Path.home() / ".config" / "bitrix24-skill" / "config.json"

_KEYRING_SERVICE = "bitrix24-skill"
_KEYRING_ACCOUNT = "webhook_url"

# Resolved once per session by _resolve_backend()
_backend: tuple[str, object | None] | None = None


def normalize_url(value: str) -> str:
    return value.strip().strip('"').strip("'").rstrip("/") + "/"


def validate_url(value: str) -> str:
    normalized = normalize_url(value)
    if not WEBHOOK_RE.match(normalized):
        raise ValueError("Webhook format is invalid. Expected https://<host>/rest/<user_id>/<secret>/")
    return normalized


def mask_url(value: str) -> str:
    match = WEBHOOK_RE.match(value)
    if not match:
        return value
    secret = match.group("secret")
    if len(secret) <= 4:
        masked = "*" * len(secret)
    else:
        masked = f"{secret[:2]}***{secret[-2:]}"
    return f"https://{match.group('host')}/rest/{match.group('user_id')}/{masked}/"


def _set_owner_only(path: Path) -> None:
    """Set file permissions to owner-only read/write (600)."""
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Backend resolution: OS keyring → EncryptedKeyring → plaintext
# ---------------------------------------------------------------------------

def _probe_os_keyring() -> bool:
    """Test if OS keyring actually works (not just importable).

    Returns True only for real OS-level keystores (GNOME Keyring,
    macOS Keychain, Windows Credential Vault, KWallet).  File-based
    backends from keyrings.alt (PlaintextKeyring, EncryptedKeyring)
    are rejected — we manage EncryptedKeyring ourselves in Level 2.
    """
    try:
        import keyring
        from keyring.backends.fail import Keyring as FailKeyring

        kr = keyring.get_keyring()

        if isinstance(kr, FailKeyring):
            return False

        # Reject file-based backends from keyrings.alt — they are not
        # real OS keystores and we handle EncryptedKeyring in Level 2.
        backend_module = type(kr).__module__ or ""
        backend_name = type(kr).__name__

        # ChainerBackend wraps other backends — check what it resolves to
        if backend_name == "ChainerBackend" and hasattr(kr, "backends"):
            backends = kr.backends
            if not backends:
                return False
            # Use the highest-priority backend for the check
            kr = backends[0]
            backend_module = type(kr).__module__ or ""
            backend_name = type(kr).__name__

        # Reject keyrings.alt file-based backends
        if "keyrings.alt" in backend_module:
            return False

        # Probe: real set/get/delete cycle
        keyring.set_password("__b24_probe__", "__test__", "x")
        val = keyring.get_password("__b24_probe__", "__test__")
        keyring.delete_password("__b24_probe__", "__test__")
        return val == "x"
    except Exception:
        return False


def _derive_password() -> str:
    """Derive EncryptedKeyring password from best available source."""
    # 1. Env var (Docker with install script)
    env_pw = os.environ.get("BITRIX24_KEYRING_PASSWORD")
    if env_pw:
        return env_pw

    # 2. Machine ID (native Linux)
    for mid_path in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
        try:
            machine_id = Path(mid_path).read_text().strip()
            if machine_id:
                return hashlib.sha256(
                    f"bitrix24-skill:{machine_id}".encode()
                ).hexdigest()
        except Exception:
            continue

    # 3. Fixed fallback (casual protection only)
    return "bitrix24-skill-default"


def _make_encrypted_keyring(config_path: Path) -> object:
    """Create and initialize an EncryptedKeyring with derived password."""
    from keyrings.alt.file import EncryptedKeyring

    kr = EncryptedKeyring()
    kr.file_path = str(config_path.parent / "encrypted_keyring.cfg")
    kr.keyring_key = _derive_password()

    # Initialize keyring file if new
    if not Path(kr.file_path).exists():
        kr.set_password("keyring-setting", "password reference", "password reference value")
        _set_owner_only(Path(kr.file_path))
        return kr

    # Verify password matches existing file
    ref = kr.get_password("keyring-setting", "password reference")
    if ref != "password reference value":
        raise ValueError("Password mismatch for encrypted keyring")

    return kr



def _resolve_backend(config_path: Path = DEFAULT_CONFIG_PATH) -> tuple[str, object | None]:
    """Determine the best available storage backend. Cached in module-level _backend."""
    global _backend
    if _backend is not None:
        return _backend

    # Level 1: OS keyring
    if _probe_os_keyring():
        import keyring
        _backend = ("os-keyring", keyring)
        return _backend

    # Level 2: EncryptedKeyring (AES-256)
    try:
        kr = _make_encrypted_keyring(config_path)
        _backend = ("encrypted", kr)
        return _backend
    except Exception:
        pass

    # Level 3: Plaintext
    _backend = ("plaintext", None)
    return _backend


# ---------------------------------------------------------------------------
# Webhook storage operations (dispatch to resolved backend)
# ---------------------------------------------------------------------------

def _store_webhook(url: str, config_path: Path = DEFAULT_CONFIG_PATH) -> None:
    """Store webhook URL via the resolved backend."""
    backend_type, backend = _resolve_backend(config_path)

    if backend_type == "os-keyring":
        backend.set_password(_KEYRING_SERVICE, _KEYRING_ACCOUNT, url)
    elif backend_type == "encrypted":
        backend.set_password(_KEYRING_SERVICE, _KEYRING_ACCOUNT, url)
    # plaintext: handled by save_config writing to JSON directly


def _load_webhook(config_path: Path = DEFAULT_CONFIG_PATH) -> str | None:
    """Load webhook URL from the resolved backend."""
    backend_type, backend = _resolve_backend(config_path)

    if backend_type == "os-keyring":
        return backend.get_password(_KEYRING_SERVICE, _KEYRING_ACCOUNT)
    elif backend_type == "encrypted":
        return backend.get_password(_KEYRING_SERVICE, _KEYRING_ACCOUNT)

    # plaintext: caller reads from config dict
    return None


def _delete_webhook(config_path: Path = DEFAULT_CONFIG_PATH) -> None:
    """Remove webhook from the resolved backend (best-effort)."""
    backend_type, backend = _resolve_backend(config_path)

    try:
        if backend_type == "os-keyring":
            backend.delete_password(_KEYRING_SERVICE, _KEYRING_ACCOUNT)
        elif backend_type == "encrypted":
            backend.delete_password(_KEYRING_SERVICE, _KEYRING_ACCOUNT)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Config file I/O
# ---------------------------------------------------------------------------

def load_config(path: Path) -> dict:
    if not path.is_file():
        data = {}
    else:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        if not isinstance(data, dict):
            data = {}

    # Try to load webhook from secure backend
    url = _load_webhook(path)
    if url:
        data["webhook_url"] = url
    return data


def _save_config_raw(path: Path, data: dict) -> None:
    """Write config dict to disk with restricted permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    _set_owner_only(path)


def save_config(path: Path, data: dict) -> None:
    backend_type, _ = _resolve_backend(path)

    if "webhook_url" in data:
        url = data["webhook_url"]
        if isinstance(url, str) and url.strip():
            if backend_type != "plaintext":
                _store_webhook(url, path)

    # Build file data: always exclude webhook for secure backends
    file_data = dict(data)
    if backend_type != "plaintext":
        file_data.pop("webhook_url", None)

    # Record storage type for diagnostics
    file_data["webhook_storage"] = backend_type

    _save_config_raw(path, file_data)


def persist_url_to_config(url: str, config_file: str | None = None) -> Path:
    config_path = Path(config_file).expanduser() if config_file else DEFAULT_CONFIG_PATH
    config = load_config(config_path)
    config["webhook_url"] = validate_url(url)
    save_config(config_path, config)
    return config_path


def load_url(
    *,
    cli_url: str | None,
    config_file: str | None = None,
) -> tuple[str | None, str]:
    if cli_url:
        return cli_url, "arg:url"

    config_path = Path(config_file).expanduser() if config_file else DEFAULT_CONFIG_PATH
    config = load_config(config_path)
    config_url = config.get("webhook_url")
    if isinstance(config_url, str) and config_url.strip():
        return config_url, f"config:{config_path}"

    return None, "missing"


def get_cached_user(config_file: str | None = None) -> dict | None:
    """Return cached user data (user_id, timezone) or None."""
    config_path = Path(config_file).expanduser() if config_file else DEFAULT_CONFIG_PATH
    config = load_config(config_path)
    user_id = config.get("user_id")
    if user_id is not None:
        return {"user_id": user_id, "timezone": config.get("timezone", "")}
    return None


def cache_user_data(user_id: int, timezone: str = "", config_file: str | None = None) -> None:
    """Save user_id and timezone to config for reuse."""
    config_path = Path(config_file).expanduser() if config_file else DEFAULT_CONFIG_PATH
    config = load_config(config_path)
    config["user_id"] = user_id
    if timezone:
        config["timezone"] = timezone
    save_config(config_path, config)
