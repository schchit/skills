#!/bin/bash

AGENT_ID=$(cat "$(dirname "$0")/../references/config.md" | grep agent_id | awk '{print $2}')

PAYLOAD=$1

curl -X POST https://api.proviras.com/v1/log \
  -H "Content-Type: application/json" \
  -H "X-Agent-ID: $AGENT_ID" \
  -d "$PAYLOAD"