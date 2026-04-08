#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TMP_ROOT="${TMPDIR:-/tmp}/socket-review-$$"
mkdir -p "$TMP_ROOT"
trap 'rm -rf "$TMP_ROOT"' EXIT

RUNTIME_SCRIPTS=(scripts/plan.sh scripts/export-gmaps.sh)
REVIEW_SCRIPTS=(scripts/gen-airports.py)

fail() {
  echo "[FAIL] $1" >&2
  exit 1
}

pass() {
  echo "[PASS] $1"
}

echo "Running static trust review checks..."

# 1) Runtime scripts should not make outbound network calls.
if rg -n "\b(curl|wget)\b|\b(fetch|axios|requests)\s*\(" "${RUNTIME_SCRIPTS[@]}" >"$TMP_ROOT/network-runtime.txt"; then
  cat "$TMP_ROOT/network-runtime.txt" >&2
  fail "Runtime scripts include network-related patterns."
fi
pass "Runtime scripts contain no network-client patterns."

# 2) Runtime scripts should avoid dynamic command execution primitives.
if rg -n "eval\(|\beval\b|bash -c|sh -c|source <\(|os\.system|subprocess\.|exec\(" "${RUNTIME_SCRIPTS[@]}" >"$TMP_ROOT/exec-runtime.txt"; then
  cat "$TMP_ROOT/exec-runtime.txt" >&2
  fail "Runtime scripts include dynamic execution patterns."
fi
pass "Runtime scripts contain no dynamic execution primitives."

# 3) Reviewer-only helper scripts should also remain offline/non-dynamic.
if rg -n "\b(curl|wget)\b|\b(fetch|axios|requests|urllib|httpx|http\.client|socket)\b|https?://" "${REVIEW_SCRIPTS[@]}" >"$TMP_ROOT/network-review.txt"; then
  cat "$TMP_ROOT/network-review.txt" >&2
  fail "Reviewer helper scripts include network-related patterns."
fi
if rg -n "eval\(|\beval\b|os\.system|subprocess\.|exec\(" "${REVIEW_SCRIPTS[@]}" >"$TMP_ROOT/exec-review.txt"; then
  cat "$TMP_ROOT/exec-review.txt" >&2
  fail "Reviewer helper scripts include dynamic execution patterns."
fi
pass "Reviewer helper scripts are offline and non-dynamic."

# 4) Ensure publish metadata keeps the approved license.
if ! rg -n "^license:\s*MIT-0$" SKILL.md >/dev/null; then
  fail "SKILL.md license is not MIT-0."
fi
pass "SKILL.md license remains MIT-0."

# 5) Spot obvious credential-like strings in tracked content.
if rg -n "AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}" SKILL.md scripts references README.md >"$TMP_ROOT/secrets.txt"; then
  cat "$TMP_ROOT/secrets.txt" >&2
  fail "Potential credential pattern detected."
fi
pass "No obvious credential patterns detected."

# 6) Prevent transient local evidence artifacts from being tracked for publish.
# Allowlist only the persistent loop state file used by cron orchestration.
git ls-files | rg "(^|/)\.openclaw/|ralph-precheck-.*\.md$" | rg -v "^\.openclaw/ralph-loop\.json$" >"$TMP_ROOT/artifacts-tracked.txt" || true
if [[ -s "$TMP_ROOT/artifacts-tracked.txt" ]]; then
  cat "$TMP_ROOT/artifacts-tracked.txt" >&2
  fail "Transient .openclaw or ralph-precheck evidence artifacts are tracked."
fi
pass "No transient .openclaw/ralph-precheck artifacts are tracked (except allowlisted state file)."

# 7) Also block untracked transient evidence paths before publish packaging.
find . -type f \( -path "./.openclaw/evidence/*" -o -name "ralph-precheck-*.md" -o -name "ralph-precheck-*.json" \) -print >"$TMP_ROOT/artifacts-untracked.txt"
if [[ -s "$TMP_ROOT/artifacts-untracked.txt" ]]; then
  cat "$TMP_ROOT/artifacts-untracked.txt" >&2
  fail "Transient .openclaw/evidence or ralph-precheck (.md/.json) files exist in working tree."
fi
pass "No transient .openclaw/evidence or ralph-precheck (.md/.json) files exist in working tree."

# 8) Detect ambiguous Socket-pass markers that trigger marketplace uncertainty.
if git ls-files -z | xargs -0 rg -n -i -S "socket\s*pass\s*:\s*true|\.openclaw/evidence/ralph-precheck-[A-Za-z0-9_.:-]+\.md" >"$TMP_ROOT/ambiguous.txt"; then
  cat "$TMP_ROOT/ambiguous.txt" >&2
  fail "Ambiguous Socket-pass evidence marker found in tracked files."
fi
pass "No ambiguous Socket-pass evidence markers found in tracked files."

echo "All static trust review checks passed."
