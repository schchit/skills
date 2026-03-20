#!/bin/bash
# MOSI Multi-Speaker Dialogue (moss-ttsd)
# Endpoint: POST /api/v1/audio/speech, model: moss-ttsd
# Text format: [S1] line\n[S2] line\n...
# Requires: curl, jq, base64
set -e

usage() {
  cat >&2 <<'EOF'
Usage: mosi_dialogue.sh --text TEXT --voice1 ID [options]

Options:
  --text,    -t  TEXT   Dialogue text with [S1][S2] tags (required)
                        e.g. "[S1] 你好！\n[S2] 你好，很高兴认识你。"
  --voice1,  -1  ID     Voice ID for S1 (required)
  --voice2,  -2  ID     Voice ID for S2
  --output,  -o  PATH   Output WAV path
                        (default: ~/.openclaw/workspace/dialogue.wav)
  --duration,-d  SECS   Expected total duration in seconds (optional)
  --api-key, -k  KEY    Override MOSI_TTS_API_KEY env var

Example:
  mosi_dialogue.sh \
    --text "[S1] 你好！\n[S2] 你好，很高兴认识你。" \
    --voice1 2001257729754140672 \
    --voice2 2001931510222950400
EOF
  exit 1
}

TEXT=""
VOICE1=""
VOICE2=""
OUTPUT="${HOME}/.openclaw/workspace/dialogue.wav"
API_KEY="${MOSI_TTS_API_KEY}"
DURATION=""

while [ $# -gt 0 ]; do
  case $1 in
    --text|-t)     TEXT="$2";     shift 2 ;;
    --voice1|-1)   VOICE1="$2";   shift 2 ;;
    --voice2|-2)   VOICE2="$2";   shift 2 ;;
    --output|-o)   OUTPUT="$2";   shift 2 ;;
    --api-key|-k)  API_KEY="$2";  shift 2 ;;
    --duration|-d) DURATION="$2"; shift 2 ;;
    -h|--help)     usage ;;
    *) echo "Unknown option: $1" >&2; usage ;;
  esac
done

[ -z "$TEXT" ]   && echo "Error: --text required" >&2 && usage
[ -z "$VOICE1" ] && echo "Error: --voice1 required" >&2 && usage
[ -z "$API_KEY" ] && echo "Error: MOSI_TTS_API_KEY not set" >&2 && exit 1

# Build JSON payload with jq
PAYLOAD=$(jq -n \
  --arg text    "$TEXT" \
  --arg voice1  "$VOICE1" \
  --arg voice2  "$VOICE2" \
  --arg dur     "$DURATION" \
  '{
    model: "moss-ttsd",
    text: $text,
    voice_id: $voice1
  }
  | if $voice2 != "" then . + {voice_id2: $voice2} else . end
  | if $dur    != "" then . + {expected_duration_sec: ($dur | tonumber)} else . end
')

echo "Generating dialogue..." >&2

RESPONSE=$(curl -sf -X POST \
  "https://studio.mosi.cn/api/v1/audio/speech" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

# Extract audio_data and decode
AUDIO_B64=$(echo "$RESPONSE" | jq -r '.audio_data // .data.audio_data // empty')

if [ -z "$AUDIO_B64" ]; then
  echo "API error: $(echo "$RESPONSE" | jq -r '.message // .')" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT")"
echo "$AUDIO_B64" | base64 -d > "$OUTPUT"
echo "Dialogue saved to: $OUTPUT" >&2

DURATION_S=$(echo "$RESPONSE" | jq -r '.duration_s // empty')
[ -n "$DURATION_S" ] && echo "Duration: ${DURATION_S}s" >&2
