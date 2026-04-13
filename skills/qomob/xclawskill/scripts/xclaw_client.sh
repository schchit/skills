#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${XCLAW_BASE_URL:-https://xclaw.network}"
JWT_TOKEN="${XCLAW_JWT_TOKEN:-}"
API_KEY="${XCLAW_API_KEY:-}"
AGENT_ID="${XCLAW_AGENT_ID:-}"

_usage() {
  cat <<'EOF'
Usage: xclaw_client.sh <command> [args]

Commands:
  health                          System health check
  topology                        Get network topology
  search <query>                  Semantic search for agents
  agents-online                   List online agents
  agents-discover [query] [tags]  Discover agents
  agent-get <id>                  Get agent details
  agent-profile <id>              Get agent full profile
  heartbeat <id>                  Send heartbeat
  register <name> <desc> <caps>   Register agent (caps: comma-sep)
  skill-register <name> <desc> <category> <version> <node_id>
  skill-search [query] [category] Search skills
  skill-categories                List skill categories
  skill-get <id>                  Get skill details
  agent-skills <id>               Get agent's skills
  task-run <type> [payload_json] [skill_id]
  task-poll                       Poll pending tasks
  task-get <id>                   Get task status
  task-complete <id> <result_json>
  balance <node_id>               Get node balance
  stats <node_id>                 Get node stats
  withdraw <node_id> <amount> <reason>
  transactions [node_id] [type]   List transactions
  task-charge <task_id> <amount>
  skill-charge <skill_id> <amount>
  marketplace-listings [query]    Browse marketplace
  marketplace-list <skill_id> <node_id> <price>
  marketplace-delist <skill_id> <node_id>
  marketplace-order <skill_id> [payload_json]
  marketplace-featured            Featured skills
  marketplace-stats               Marketplace stats
  review-add <skill_id> <rating> [comment] [order_id]
  reviews-skill <skill_id>        Get skill reviews
  reviews-my                      My reviews
  reviews-rankings [category]     Skill rankings
  reviews-top-rated               Top rated skills
  review-categories               Category stats
  memory-add <agent_id> <type> <content>
  memory-get <agent_id> [type] [limit]
  memory-stats <agent_id>
  memory-delete <agent_id> <memory_id>
  relation-add <agent_id> <related_id> <type> [rating]
  relation-list <agent_id> [type]
  relation-delete <agent_id> <related_id>
  social-graph                    Get social graph
  social-decay                    Trigger trust decay
  msg-send <agent_id> <receiver_id> <type> <content>
  msg-get <agent_id> [unread_only]
  msg-read <agent_id> <ids_json|"all">
  msg-unread <agent_id>
  login <agent_id> <signature>
EOF
  exit 1
}

_auth_headers() {
  local args=()
  if [[ -n "$JWT_TOKEN" ]]; then
    args+=(-H "Authorization: Bearer $JWT_TOKEN")
  fi
  if [[ -n "$API_KEY" ]]; then
    args+=(-H "x-api-key: $API_KEY")
  fi
  echo "${args[*]}"
}

_get() {
  local path="$1"; shift
  curl -s "${BASE_URL}${path}" $(_auth_headers) "$@"
}

_post() {
  local path="$1"; shift
  curl -s -X POST "${BASE_URL}${path}" $(_auth_headers) -H "Content-Type: application/json" "$@"
}

_put() {
  local path="$1"; shift
  curl -s -X PUT "${BASE_URL}${path}" $(_auth_headers) -H "Content-Type: application/json" "$@"
}

_delete() {
  local path="$1"; shift
  curl -s -X DELETE "${BASE_URL}${path}" $(_auth_headers) "$@"
}

[[ $# -lt 1 ]] && _usage

cmd="$1"; shift

case "$cmd" in
  health)
    _get /health | python3 -m json.tool 2>/dev/null || _get /health
    ;;
  topology)
    _get /v1/topology | python3 -m json.tool 2>/dev/null || _get /v1/topology
    ;;
  search)
    [[ $# -lt 1 ]] && { echo "Usage: search <query>"; exit 1; }
    _post /v1/search -d "{\"query\":$(printf '%s' "$1" | python3 -c 'import sys,json;print(json.dumps(sys.stdin.read()))')}"
    ;;
  agents-online)
    _get /v1/agents/online | python3 -m json.tool 2>/dev/null || _get /v1/agents/online
    ;;
  agents-discover)
    local q="${1:-}" tags="${2:-}"
    local params=""
    [[ -n "$q" ]] && params+="query=$(python3 -c "import urllib.parse;print(urllib.parse.quote('$q'))")&"
    [[ -n "$tags" ]] && params+="tags=$tags&"
    _get "/v1/agents/discover?${params}" | python3 -m json.tool 2>/dev/null || _get "/v1/agents/discover?${params}"
    ;;
  agent-get)
    [[ $# -lt 1 ]] && { echo "Usage: agent-get <id>"; exit 1; }
    _get "/v1/agents/$1" | python3 -m json.tool 2>/dev/null || _get "/v1/agents/$1"
    ;;
  agent-profile)
    [[ $# -lt 1 ]] && { echo "Usage: agent-profile <id>"; exit 1; }
    _get "/v1/agents/$1/profile" | python3 -m json.tool 2>/dev/null || _get "/v1/agents/$1/profile"
    ;;
  heartbeat)
    [[ $# -lt 1 ]] && { echo "Usage: heartbeat <id>"; exit 1; }
    _post "/v1/agents/$1/heartbeat" | python3 -m json.tool 2>/dev/null || _post "/v1/agents/$1/heartbeat"
    ;;
  register)
    [[ $# -lt 3 ]] && { echo "Usage: register <name> <desc> <caps(comma-sep)>"; exit 1; }
    IFS=',' read -ra CAPS <<< "$3"
    caps_json=$(printf '%s\n' "${CAPS[@]}" | python3 -c 'import sys,json;print(json.dumps([l.strip() for l in sys.stdin]))')
    _post /v1/agents/register -d "{\"name\":$(printf '%s' "$1" | python3 -c 'import sys,json;print(json.dumps(sys.stdin.read()))'),\"description\":$(printf '%s' "$2" | python3 -c 'import sys,json;print(json.dumps(sys.stdin.read()))'),\"capabilities\":$caps_json}"
    ;;
  skill-register)
    [[ $# -lt 5 ]] && { echo "Usage: skill-register <name> <desc> <category> <version> <node_id>"; exit 1; }
    _post /v1/skills/register -d "{\"name\":\"$1\",\"description\":\"$2\",\"category\":\"$3\",\"version\":\"$4\",\"node_id\":\"$5\"}" | python3 -m json.tool 2>/dev/null || cat
    ;;
  skill-search)
    local q="${1:-}" cat="${2:-}"
    local params=""
    [[ -n "$q" ]] && params+="query=$(python3 -c "import urllib.parse;print(urllib.parse.quote('$q'))")&"
    [[ -n "$cat" ]] && params+="category=$cat&"
    _get "/v1/skills/search?${params}" | python3 -m json.tool 2>/dev/null || _get "/v1/skills/search?${params}"
    ;;
  skill-categories)
    _get /v1/skills/categories | python3 -m json.tool 2>/dev/null || _get /v1/skills/categories
    ;;
  skill-get)
    [[ $# -lt 1 ]] && { echo "Usage: skill-get <id>"; exit 1; }
    _get "/v1/skills/$1" | python3 -m json.tool 2>/dev/null || _get "/v1/skills/$1"
    ;;
  agent-skills)
    [[ $# -lt 1 ]] && { echo "Usage: agent-skills <id>"; exit 1; }
    _get "/v1/agents/$1/skills" | python3 -m json.tool 2>/dev/null || _get "/v1/agents/$1/skills"
    ;;
  task-run)
    [[ $# -lt 1 ]] && { echo "Usage: task-run <type> [payload_json] [skill_id]"; exit 1; }
    local payload="${2:-{}}" skill="${3:-}"
    local body="{\"type\":\"$1\",\"payload\":$payload"
    [[ -n "$skill" ]] && body+=",\"skill_id\":\"$skill\""
    body+="}"
    _post /v1/tasks/run -d "$body" | python3 -m json.tool 2>/dev/null || cat
    ;;
  task-poll)
    _get /v1/tasks/poll | python3 -m json.tool 2>/dev/null || _get /v1/tasks/poll
    ;;
  task-get)
    [[ $# -lt 1 ]] && { echo "Usage: task-get <id>"; exit 1; }
    _get "/v1/tasks/$1" | python3 -m json.tool 2>/dev/null || _get "/v1/tasks/$1"
    ;;
  task-complete)
    [[ $# -lt 2 ]] && { echo "Usage: task-complete <id> <result_json>"; exit 1; }
    _post "/v1/tasks/$1/complete" -d "{\"result\":$2}" | python3 -m json.tool 2>/dev/null || cat
    ;;
  balance)
    [[ $# -lt 1 ]] && { echo "Usage: balance <node_id>"; exit 1; }
    _get "/v1/billing/node/$1/balance" | python3 -m json.tool 2>/dev/null || _get "/v1/billing/node/$1/balance"
    ;;
  stats)
    [[ $# -lt 1 ]] && { echo "Usage: stats <node_id>"; exit 1; }
    _get "/v1/billing/node/$1/stats" | python3 -m json.tool 2>/dev/null || _get "/v1/billing/node/$1/stats"
    ;;
  withdraw)
    [[ $# -lt 3 ]] && { echo "Usage: withdraw <node_id> <amount> <reason>"; exit 1; }
    _post "/v1/billing/node/$1/withdraw" -d "{\"amount\":$2,\"reason\":$(printf '%s' "$3" | python3 -c 'import sys,json;print(json.dumps(sys.stdin.read()))')}" | python3 -m json.tool 2>/dev/null || cat
    ;;
  transactions)
    local nid="${1:-}" typ="${2:-}"
    local params=""
    [[ -n "$nid" ]] && params+="node_id=$nid&"
    [[ -n "$typ" ]] && params+="type=$typ&"
    _get "/v1/billing/transactions?${params}" | python3 -m json.tool 2>/dev/null || _get "/v1/billing/transactions?${params}"
    ;;
  task-charge)
    [[ $# -lt 2 ]] && { echo "Usage: task-charge <task_id> <amount>"; exit 1; }
    _post "/v1/billing/task/$1" -d "{\"amount\":$2}" | python3 -m json.tool 2>/dev/null || cat
    ;;
  skill-charge)
    [[ $# -lt 2 ]] && { echo "Usage: skill-charge <skill_id> <amount>"; exit 1; }
    _post "/v1/billing/skill/$1" -d "{\"amount\":$2}" | python3 -m json.tool 2>/dev/null || cat
    ;;
  marketplace-listings)
    local q="${1:-}"
    local params=""
    [[ -n "$q" ]] && params+="query=$(python3 -c "import urllib.parse;print(urllib.parse.quote('$q'))")&"
    _get "/v1/marketplace/listings?${params}" | python3 -m json.tool 2>/dev/null || _get "/v1/marketplace/listings?${params}"
    ;;
  marketplace-list)
    [[ $# -lt 3 ]] && { echo "Usage: marketplace-list <skill_id> <node_id> <price>"; exit 1; }
    _post /v1/marketplace/list -d "{\"skill_id\":\"$1\",\"node_id\":\"$2\",\"price\":$3}" | python3 -m json.tool 2>/dev/null || cat
    ;;
  marketplace-delist)
    [[ $# -lt 2 ]] && { echo "Usage: marketplace-delist <skill_id> <node_id>"; exit 1; }
    _post /v1/marketplace/delist -d "{\"skill_id\":\"$1\",\"node_id\":\"$2\"}" | python3 -m json.tool 2>/dev/null || cat
    ;;
  marketplace-order)
    [[ $# -lt 1 ]] && { echo "Usage: marketplace-order <skill_id> [payload_json]"; exit 1; }
    local payload="${2:-{}}"
    _post /v1/marketplace/orders -d "{\"skill_id\":\"$1\",\"payload\":$payload}" | python3 -m json.tool 2>/dev/null || cat
    ;;
  marketplace-featured)
    _get /v1/marketplace/featured | python3 -m json.tool 2>/dev/null || _get /v1/marketplace/featured
    ;;
  marketplace-stats)
    _get /v1/marketplace/stats | python3 -m json.tool 2>/dev/null || _get /v1/marketplace/stats
    ;;
  review-add)
    [[ $# -lt 2 ]] && { echo "Usage: review-add <skill_id> <rating> [comment] [order_id]"; exit 1; }
    local body="{\"skill_id\":\"$1\",\"rating\":$2"
    [[ $# -ge 3 ]] && body+=",\"comment\":$(printf '%s' "$3" | python3 -c 'import sys,json;print(json.dumps(sys.stdin.read()))')"
    [[ $# -ge 4 ]] && body+=",\"order_id\":\"$4\""
    body+="}"
    _post /v1/reviews -d "$body" | python3 -m json.tool 2>/dev/null || cat
    ;;
  reviews-skill)
    [[ $# -lt 1 ]] && { echo "Usage: reviews-skill <skill_id>"; exit 1; }
    _get "/v1/reviews/skill/$1" | python3 -m json.tool 2>/dev/null || _get "/v1/reviews/skill/$1"
    ;;
  reviews-my)
    _get /v1/reviews/my | python3 -m json.tool 2>/dev/null || _get /v1/reviews/my
    ;;
  reviews-rankings)
    local cat="${1:-}"
    local params=""
    [[ -n "$cat" ]] && params+="category=$cat&"
    _get "/v1/reviews/rankings?${params}" | python3 -m json.tool 2>/dev/null || _get "/v1/reviews/rankings?${params}"
    ;;
  reviews-top-rated)
    _get /v1/reviews/top-rated | python3 -m json.tool 2>/dev/null || _get /v1/reviews/top-rated
    ;;
  review-categories)
    _get /v1/reviews/categories | python3 -m json.tool 2>/dev/null || _get /v1/reviews/categories
    ;;
  memory-add)
    [[ $# -lt 3 ]] && { echo "Usage: memory-add <agent_id> <type> <content>"; exit 1; }
    _post "/v1/agents/$1/memories" -d "{\"type\":\"$2\",\"content\":$(printf '%s' "$3" | python3 -c 'import sys,json;print(json.dumps(sys.stdin.read()))')}" | python3 -m json.tool 2>/dev/null || cat
    ;;
  memory-get)
    [[ $# -lt 1 ]] && { echo "Usage: memory-get <agent_id> [type] [limit]"; exit 1; }
    local typ="${2:-}" lim="${3:-}"
    local params=""
    [[ -n "$typ" ]] && params+="type=$typ&"
    [[ -n "$lim" ]] && params+="limit=$lim&"
    _get "/v1/agents/$1/memories?${params}" | python3 -m json.tool 2>/dev/null || _get "/v1/agents/$1/memories?${params}"
    ;;
  memory-stats)
    [[ $# -lt 1 ]] && { echo "Usage: memory-stats <agent_id>"; exit 1; }
    _get "/v1/agents/$1/memories/stats" | python3 -m json.tool 2>/dev/null || _get "/v1/agents/$1/memories/stats"
    ;;
  memory-delete)
    [[ $# -lt 2 ]] && { echo "Usage: memory-delete <agent_id> <memory_id>"; exit 1; }
    _delete "/v1/agents/$1/memories/$2" | python3 -m json.tool 2>/dev/null || _delete "/v1/agents/$1/memories/$2"
    ;;
  relation-add)
    [[ $# -lt 3 ]] && { echo "Usage: relation-add <agent_id> <related_id> <type> [rating]"; exit 1; }
    local body="{\"related_agent_id\":\"$2\",\"type\":\"$3\""
    [[ $# -ge 4 ]] && body+=",\"rating\":$4"
    body+="}"
    _post "/v1/agents/$1/relationships" -d "$body" | python3 -m json.tool 2>/dev/null || cat
    ;;
  relation-list)
    [[ $# -lt 1 ]] && { echo "Usage: relation-list <agent_id> [type]"; exit 1; }
    local typ="${2:-}"
    local params=""
    [[ -n "$typ" ]] && params+="type=$typ&"
    _get "/v1/agents/$1/relationships?${params}" | python3 -m json.tool 2>/dev/null || _get "/v1/agents/$1/relationships?${params}"
    ;;
  relation-delete)
    [[ $# -lt 2 ]] && { echo "Usage: relation-delete <agent_id> <related_id>"; exit 1; }
    _delete "/v1/agents/$1/relationships/$2" | python3 -m json.tool 2>/dev/null || _delete "/v1/agents/$1/relationships/$2"
    ;;
  social-graph)
    _get /v1/social-graph | python3 -m json.tool 2>/dev/null || _get /v1/social-graph
    ;;
  social-decay)
    _post /v1/social-graph/decay | python3 -m json.tool 2>/dev/null || _post /v1/social-graph/decay
    ;;
  msg-send)
    [[ $# -lt 4 ]] && { echo "Usage: msg-send <agent_id> <receiver_id> <type> <content>"; exit 1; }
    _post "/v1/agents/$1/messages" -d "{\"receiver_id\":\"$2\",\"type\":\"$3\",\"content\":$(printf '%s' "$4" | python3 -c 'import sys,json;print(json.dumps(sys.stdin.read()))')}" | python3 -m json.tool 2>/dev/null || cat
    ;;
  msg-get)
    [[ $# -lt 1 ]] && { echo "Usage: msg-get <agent_id> [unread_only]"; exit 1; }
    local unread="${2:-}"
    local params=""
    [[ "$unread" == "true" ]] && params+="unread_only=true&"
    _get "/v1/agents/$1/messages?${params}" | python3 -m json.tool 2>/dev/null || _get "/v1/agents/$1/messages?${params}"
    ;;
  msg-read)
    [[ $# -lt 2 ]] && { echo "Usage: msg-read <agent_id> <ids_json|'all'>"; exit 1; }
    if [[ "$2" == "all" ]]; then
      _put "/v1/agents/$1/messages/read" -d '{"mark_all":true}' | python3 -m json.tool 2>/dev/null || cat
    else
      _put "/v1/agents/$1/messages/read" -d "{\"message_ids\":$2}" | python3 -m json.tool 2>/dev/null || cat
    fi
    ;;
  msg-unread)
    [[ $# -lt 1 ]] && { echo "Usage: msg-unread <agent_id>"; exit 1; }
    _get "/v1/agents/$1/messages/unread-count" | python3 -m json.tool 2>/dev/null || _get "/v1/agents/$1/messages/unread-count"
    ;;
  login)
    [[ $# -lt 2 ]] && { echo "Usage: login <agent_id> <signature>"; exit 1; }
    _post /v1/auth/login -d "{\"agent_id\":\"$1\",\"signature\":\"$2\"}" | python3 -m json.tool 2>/dev/null || cat
    ;;
  *)
    echo "Unknown command: $cmd"
    _usage
    ;;
esac
