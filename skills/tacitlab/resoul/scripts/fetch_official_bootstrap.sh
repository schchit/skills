#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_DIR="${1:-/root/.openclaw/workspace}"
DEST="$WORKSPACE_DIR/BOOTSTRAP.md"
URL="https://raw.githubusercontent.com/openclaw/openclaw/main/docs/reference/templates/BOOTSTRAP.md"
TMP="$(mktemp "$WORKSPACE_DIR/.bootstrap.tmp.XXXXXX")"

mkdir -p "$WORKSPACE_DIR"

cleanup() {
  rm -f "$TMP"
}
trap cleanup EXIT

if [[ -f "$DEST" ]]; then
  cp "$DEST" "$DEST.bak.$(date +%Y%m%d-%H%M%S)"
fi

if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$URL" -o "$TMP"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$TMP" "$URL"
else
  echo "Neither curl nor wget is available." >&2
  exit 1
fi

mv "$TMP" "$DEST"
echo "Fetched official BOOTSTRAP.md to: $DEST"
