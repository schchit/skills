#!/usr/bin/env bash
# Self-test for Pangolinfo Amazon Niche Data Client
# Requires: PANGOLINFO_API_KEY or PANGOLINFO_EMAIL + PANGOLINFO_PASSWORD
#
# Usage: bash scripts/self_test.sh
#
# Runs all 5 APIs with minimal parameters and validates JSON output.
#
# ⚠ CREDIT COST: A full run consumes up to ~21 credits
#   (Tree 2 + Search 2 + Paths 2 + CategoryFilter 5 + NicheFilter 10).
#   Auth check is free. Only successful calls are charged.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PY="python3 ${SCRIPT_DIR}/pangolinfo.py"

PASS=0
FAIL=0

run_test() {
    local name="$1"
    shift
    echo -n "  [TEST] ${name} ... "
    local output
    if output=$($PY "$@" 2>&1); then
        if echo "$output" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('success') is True" 2>/dev/null; then
            echo "PASS"
            PASS=$((PASS + 1))
            return 0
        else
            echo "FAIL (success!=true)"
            echo "       Output: ${output:0:200}"
            FAIL=$((FAIL + 1))
            return 1
        fi
    else
        echo "FAIL (exit=$?)"
        echo "       Output: ${output:0:200}"
        FAIL=$((FAIL + 1))
        return 1
    fi
}

echo "=== Pangolinfo Amazon Niche Data - Self Test ==="
echo "  NOTE: This test will consume up to ~21 API credits (auth check is free)."
echo ""

# Auth check (free)
run_test "Auth check" --auth-only || true

# 1. Category Tree (2 credits -- may return empty top-level, which is still success)
run_test "Category Tree (top-level)" --api category-tree --size 2 || true

# 2. Category Search (2 credits)
run_test "Category Search (headphones)" --api category-search --keyword headphones --size 2 || true

# 3. Category Paths (2 credits)
run_test "Category Paths (2619526011)" --api category-paths --category-ids "2619526011" || true

# 4. Category Filter (5 credits)
run_test "Category Filter (US/l7d)" --api category-filter --marketplace-id US --time-range l7d --sample-scope all_asin --size 1 || true

# 5. Niche Filter (10 credits)
run_test "Niche Filter (US/yoga mat)" --api niche-filter --marketplace-id US --niche-title "yoga mat" --size 1 || true

echo ""
echo "=== Results: ${PASS} passed, ${FAIL} failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
