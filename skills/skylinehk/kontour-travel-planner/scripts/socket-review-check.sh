#!/usr/bin/env bash
# Read-only trust review pack focused on Socket-style static concerns.
# Prints a single PASS/FAIL verdict with compact evidence.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
cd "$SKILL_DIR"

RUNTIME_FILES=(
  "scripts/plan.sh"
  "scripts/export-gmaps.sh"
  "scripts/gen-airports.py"
)

# 1) Runtime suspicious execution/network clients (should be empty)
if rg -n "\\bcurl\\b|\\bwget\\b|urllib\\.request|requests\\.|httpx\\.|subprocess\\.(run|Popen)|os\\.system|eval\\(|exec\\(" "${RUNTIME_FILES[@]}" >/tmp/socket-review-runtime.txt; then
  echo "SOCKET_REVIEW: FAIL"
  echo "reason=runtime_suspicious_pattern_detected"
  cat /tmp/socket-review-runtime.txt
  exit 1
fi

# 2) Credential leak smoke scan (should be empty)
if rg -n "AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]+|ghp_[A-Za-z0-9]{36}|-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----" SKILL.md README.md scripts references >/tmp/socket-review-secrets.txt; then
  echo "SOCKET_REVIEW: FAIL"
  echo "reason=security_concerns_credential_like_pattern_detected"
  cat /tmp/socket-review-secrets.txt
  exit 1
fi

# 3) Obfuscation smoke scan for runtime scripts (should be empty)
if rg -n "[A-Za-z0-9+/]{180,}={0,2}" scripts/plan.sh scripts/export-gmaps.sh scripts/gen-airports.py >/tmp/socket-review-obfuscation.txt; then
  echo "SOCKET_REVIEW: FAIL"
  echo "reason=code_obfuscation_long_encoded_blob_detected"
  cat /tmp/socket-review-obfuscation.txt
  exit 1
fi

# 4) Frontmatter invariants
if ! rg -n "^license:\s*MIT-0\s*$" SKILL.md >/dev/null; then
  echo "SOCKET_REVIEW: FAIL"
  echo "reason=security_concerns_license_not_mit_0"
  exit 1
fi

if ! rg -n "^\s*env:\s*\[\]\s*$" SKILL.md >/dev/null; then
  echo "SOCKET_REVIEW: FAIL"
  echo "reason=security_concerns_requires_env_not_empty"
  exit 1
fi

echo "SOCKET_REVIEW: PASS"
echo "checks=runtime_suspicious_pattern,credential_leak_smoke,obfuscation_smoke,frontmatter_invariants"
echo "socket_categories=malicious_behavior:pass,security_concerns:pass,code_obfuscation:pass,suspicious_patterns:pass"
