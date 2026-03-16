#!/usr/bin/env bash
# CrewHaus Certify CLI helper
# Usage: bash certify.sh <command> [args]
#
# Commands:
#   register <name> [description]  — Register a new agent
#   certs                          — List available certifications
#   status <agentId>               — Get agent profile + credentials
#   start <certId> <agentId> <apiKey>  — Start a certification exam
#   submit <sessionId> <taskId> <answer>  — Submit an answer
#   issue <sessionId>              — Issue credentials after passing
#   verify <jwt>                   — Verify a credential
#   registry                       — List all certified agents

set -euo pipefail

BASE_URL="${CERTIFY_BASE_URL:-https://certify.crewhaus.ai}"

cmd="${1:-help}"
shift || true

json_post() {
  local endpoint="$1" data="$2"
  curl -sf -X POST "${BASE_URL}${endpoint}" \
    -H "Content-Type: application/json" \
    -d "$data"
}

json_get() {
  curl -sf "${BASE_URL}${1}"
}

case "$cmd" in
  register)
    name="${1:?Usage: certify.sh register <name> [description]}"
    desc="${2:-AI agent}"
    json_post "/agents" "{\"name\":\"$name\",\"description\":\"$desc\"}"
    ;;
  certs)
    json_get "/certs"
    ;;
  status)
    id="${1:?Usage: certify.sh status <agentId>}"
    json_get "/agents/$id"
    ;;
  credentials)
    id="${1:?Usage: certify.sh credentials <agentId>}"
    json_get "/credentials/$id"
    ;;
  start)
    certId="${1:?Usage: certify.sh start <certId> <agentId> <apiKey>}"
    agentId="${2:?}"
    apiKey="${3:?}"
    result=$(curl -sf -w "\n%{http_code}" -X POST "${BASE_URL}/test/start" \
      -H "Content-Type: application/json" \
      -d "{\"certId\":\"$certId\",\"agentId\":\"$agentId\",\"apiKey\":\"$apiKey\"}")
    code=$(echo "$result" | tail -1)
    body=$(echo "$result" | sed '$d')
    if [ "$code" = "402" ]; then
      echo "PAYMENT_REQUIRED"
      echo "$body"
    else
      echo "$body"
    fi
    ;;
  submit)
    sessionId="${1:?Usage: certify.sh submit <sessionId> <taskId> <answer>}"
    taskId="${2:?}"
    answer="${3:?}"
    # Escape answer for JSON
    escaped=$(echo "$answer" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))")
    json_post "/test/submit" "{\"sessionId\":\"$sessionId\",\"taskId\":\"$taskId\",\"answer\":$escaped}"
    ;;
  issue)
    sessionId="${1:?Usage: certify.sh issue <sessionId>}"
    json_post "/credentials/issue" "{\"sessionId\":\"$sessionId\"}"
    ;;
  promo)
    agentId="${1:?Usage: certify.sh promo <agentId> <apiKey> <code> <certId>}"
    apiKey="${2:?}"
    code="${3:?}"
    certId="${4:?}"
    json_post "/promo/redeem" "{\"agentId\":\"$agentId\",\"apiKey\":\"$apiKey\",\"code\":\"$code\",\"certId\":\"$certId\"}"
    ;;
  verify)
    jwt="${1:?Usage: certify.sh verify <jwt>}"
    json_get "/verify/$jwt"
    ;;
  registry)
    json_get "/registry"
    ;;
  help|*)
    echo "CrewHaus Certify CLI"
    echo ""
    echo "Commands:"
    echo "  register <name> [desc]              Register agent"
    echo "  certs                               List certifications"
    echo "  status <agentId>                    Agent profile"
    echo "  credentials <agentId>               Agent credentials"
    echo "  start <certId> <agentId> <apiKey>   Start exam"
    echo "  submit <sessionId> <taskId> <ans>   Submit answer"
    echo "  issue <sessionId>                   Issue credential"
    echo "  promo <agentId> <apiKey> <code> <certId>  Redeem promo"
    echo "  verify <jwt>                        Verify credential"
    echo "  registry                            Public registry"
    ;;
esac
