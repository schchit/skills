#!/usr/bin/env bash
# extract-book-digests.sh — Extract first 12 pages of each PDF as text
# Usage: bash extract-book-digests.sh <books-dir> <output-dir> [--help]
set -euo pipefail

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  echo "Usage: bash extract-book-digests.sh <books-dir> <output-dir>"
  echo "Extract first 12 pages of each PDF as text via pdftotext."
  exit 0
fi

for arg in "$@"; do
  case "$arg" in --help|-h) ;; --*) echo "Error: unknown option '$arg'" >&2; exit 2 ;; esac
done

command -v pdftotext >/dev/null 2>&1 || { echo "Error: pdftotext is required (install poppler-utils (Linux) or brew install poppler (macOS))" >&2; exit 1; }

BOOKS="${1:?Usage: extract-book-digests.sh <books-dir> <output-dir>}"
OUT="${2:?Usage: extract-book-digests.sh <books-dir> <output-dir>}"
mkdir -p "$OUT"

_err=$(mktemp)
trap 'rm -f "$_err" 2>/dev/null' EXIT

for pdf in "$BOOKS"/*.pdf; do
  [ -f "$pdf" ] || continue
  name=$(basename "$pdf" .pdf)
  dest="$OUT/$name.txt"
  echo -n "Extracting $name ... "
  if pdftotext -f 1 -l 12 "$pdf" "$dest" 2>"$_err"; then
    sz=$(wc -c < "$dest" | tr -d ' ')
    echo "OK (${sz} bytes)"
  else
    echo "FAIL: $(cat "$_err")"
    rm -f "$dest"
  fi
  : > "$_err"
done

echo ""
echo "Digests: $(find "$OUT" -maxdepth 1 -type f -name '*.txt' 2>/dev/null | wc -l | tr -d ' ') files in $OUT"
