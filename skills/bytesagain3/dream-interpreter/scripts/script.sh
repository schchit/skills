#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# Dream Interpreter — Explore dream symbols and keep a dream journal
# Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
###############################################################################

VERSION="3.0.0"
SCRIPT_NAME="dream-interpreter"
DATA_DIR="${HOME}/.local/share/dream-interpreter"
JOURNAL_FILE="${DATA_DIR}/journal.jsonl"
HISTORY_FILE="${DATA_DIR}/history.jsonl"

mkdir -p "$DATA_DIR"

_ts() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
_date() { date '+%Y-%m-%d'; }

# --- Dream Symbol Database --------------------------------------------------
# Each symbol has: meaning, psychology, common themes

declare -A SYMBOLS
SYMBOLS=(
  [water]="Emotions, subconscious mind, purification. Deep water = deep emotions. Calm water = inner peace. Turbulent water = emotional turmoil."
  [flying]="Freedom, ambition, escaping limitations. Flying high = confidence. Struggling to fly = obstacles. Falling while flying = fear of failure."
  [falling]="Loss of control, anxiety, letting go. Endless falling = insecurity. Falling and landing = overcoming fears. Falling from height = risk-taking."
  [teeth]="Self-image, confidence, communication. Losing teeth = anxiety about appearance. Breaking teeth = powerlessness. Growing teeth = personal growth."
  [snake]="Transformation, hidden fears, healing. Being bitten = wake-up call. Multiple snakes = overwhelming problems. Friendly snake = wisdom."
  [death]="Endings, transformation, new beginnings. Own death = major life change. Death of loved one = fear of loss. Witnessing death = transition."
  [house]="Self, psyche, different aspects of personality. Rooms = different aspects of self. Attic = higher mind. Basement = subconscious."
  [chase]="Avoidance, running from problems, anxiety. Being chased = avoiding an issue. Chasing someone = pursuing a goal. Can't run = feeling stuck."
  [baby]="New beginnings, innocence, vulnerability. Holding baby = nurturing new idea. Crying baby = neglected needs. Lost baby = missed opportunity."
  [car]="Life direction, control, ambition. Driving = in control. Passenger = letting others decide. Crash = conflict or setback."
  [fire]="Passion, anger, transformation, destruction. Warm fire = comfort. Wildfire = out of control. Candle = hope and spirituality."
  [dog]="Loyalty, friendship, protection. Friendly dog = trusted companion. Aggressive dog = betrayal fears. Lost dog = missing connection."
  [cat]="Independence, intuition, feminine energy. Playful cat = creativity. Black cat = mystery. Multiple cats = various aspects of femininity."
  [spider]="Creativity, patience, feeling trapped. Web = complex situation. Large spider = dominant female figure. Many spiders = feeling overwhelmed."
  [ocean]="Vast emotions, the unconscious, infinite possibility. Calm ocean = emotional stability. Storm = emotional upheaval. Deep ocean = unexplored self."
  [forest]="Unconscious mind, unknown territory, growth. Dense forest = confusion. Clearing = insight. Dark forest = fear of unknown."
  [mountain]="Goals, obstacles, achievement. Climbing = working toward goal. Summit = achievement. Steep = challenges ahead."
  [bridge]="Transition, connection, crossing over. Crossing = making a change. Broken bridge = obstacle. Building bridge = making connections."
  [mirror]="Self-reflection, truth, identity. Clear mirror = self-awareness. Broken mirror = distorted self-image. No reflection = identity crisis."
  [rain]="Cleansing, sadness, renewal. Gentle rain = emotional release. Storm = overwhelming emotions. Rainbow after = hope."
  [door]="Opportunities, transitions, secrets. Open door = new opportunity. Locked door = blocked path. Many doors = choices ahead."
  [bird]="Freedom, perspective, spiritual messages. Flying bird = liberation. Caged bird = feeling trapped. Flock = community."
  [exam]="Self-evaluation, fear of judgment, preparedness. Failing exam = inadequacy. Unprepared = anxiety. Passing = confidence."
  [naked]="Vulnerability, exposure, authenticity. Public nudity = fear of judgment. Comfortable = self-acceptance. Partial = partial exposure."
  [money]="Self-worth, power, security. Finding money = discovering value. Losing money = insecurity. Counting = evaluating worth."
  [road]="Life path, journey, choices. Straight road = clear direction. Fork = decision point. Winding = uncertain journey."
  [tree]="Growth, life, family roots. Large tree = stability. Fallen tree = loss. Blooming = prosperity."
  [moon]="Intuition, cycles, hidden aspects. Full moon = clarity. New moon = new beginnings. Eclipse = blocked intuition."
  [sun]="Consciousness, vitality, success. Bright sun = optimism. Sunset = ending. Sunrise = new chapter."
  [stairs]="Progress, ascent, spiritual growth. Going up = improvement. Going down = exploring subconscious. Broken stairs = setbacks."
)

declare -A CATEGORIES
CATEGORIES=(
  [nature]="water ocean forest mountain rain tree moon sun fire"
  [animals]="snake dog cat spider bird"
  [body]="teeth naked baby"
  [places]="house road bridge door stairs"
  [actions]="flying falling chase exam"
  [objects]="car mirror money"
  [emotions]="death"
)

# --- commands ---------------------------------------------------------------

cmd_interpret() {
  local symbol="${1:?Usage: interpret <symbol>}"
  symbol="${symbol,,}"

  echo "🌙 Dream Interpretation — ${symbol^}"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  if [[ -n "${SYMBOLS[$symbol]+x}" ]]; then
    local meaning="${SYMBOLS[$symbol]}"

    # Split by period for formatted output
    echo "  🔮 Symbol: ${symbol^}"
    echo ""
    echo "  📖 Meaning:"
    echo "$meaning" | tr '.' '\n' | while IFS= read -r sentence; do
      sentence=$(echo "$sentence" | sed 's/^ *//')
      [[ -z "$sentence" ]] && continue
      echo "    • ${sentence}."
    done

    echo ""
    echo "  💡 Reflection Questions:"
    echo "    • What emotions did this symbol evoke in your dream?"
    echo "    • How does this relate to your current life situation?"
    echo "    • Have you seen this symbol in dreams before?"

    # Find category
    for cat in "${!CATEGORIES[@]}"; do
      if echo "${CATEGORIES[$cat]}" | grep -qw "$symbol"; then
        echo ""
        echo "  📂 Category: ${cat^}"
        break
      fi
    done

    echo "{\"timestamp\":\"$(_ts)\",\"action\":\"interpret\",\"symbol\":\"${symbol}\"}" >> "$HISTORY_FILE"
  else
    echo "  ❓ Symbol '${symbol}' not found in database."
    echo ""
    echo "  Available symbols:"
    printf "    "
    local count=0
    for s in "${!SYMBOLS[@]}"; do
      printf "%s  " "$s"
      count=$((count + 1))
      if [[ $((count % 6)) -eq 0 ]]; then
        printf "\n    "
      fi
    done
    echo ""
    echo ""
    echo "  💡 Try: interpret water, interpret flying, interpret snake"
  fi
}

cmd_search() {
  local keyword="${1:?Usage: search <keyword>}"
  keyword="${keyword,,}"

  echo "🔍 Search Results — '${keyword}'"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  local found=0
  for symbol in "${!SYMBOLS[@]}"; do
    local meaning="${SYMBOLS[$symbol]}"
    if echo "$symbol $meaning" | grep -qi "$keyword"; then
      echo "  🌙 ${symbol^}"
      echo "    ${meaning:0:100}..."
      echo ""
      found=$((found + 1))
    fi
  done

  if [[ "$found" -eq 0 ]]; then
    echo "  No matches found for '${keyword}'."
    echo "  Try broader terms like: emotion, fear, growth, change"
  else
    echo "  📊 Found $found matching symbol(s)"
  fi
}

cmd_random() {
  echo "🎲 Random Dream Symbol"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  local keys=("${!SYMBOLS[@]}")
  local rand_idx=$((RANDOM % ${#keys[@]}))
  local symbol="${keys[$rand_idx]}"

  cmd_interpret "$symbol"
}

cmd_categories() {
  echo "📂 Dream Symbol Categories"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  for cat in "${!CATEGORIES[@]}"; do
    echo "  📁 ${cat^}:"
    for symbol in ${CATEGORIES[$cat]}; do
      echo "    • ${symbol^}"
    done
    echo ""
  done

  echo "  📊 Total symbols: ${#SYMBOLS[@]}"
  echo "  📊 Total categories: ${#CATEGORIES[@]}"
}

cmd_journal() {
  local text="${*:?Usage: journal <dream description text>}"

  echo "📝 Dream Journal Entry"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  local entry_date
  entry_date="$(_date)"
  local entry_ts
  entry_ts="$(_ts)"

  # Detect symbols in the text
  local detected_symbols=""
  local text_lower="${text,,}"
  for symbol in "${!SYMBOLS[@]}"; do
    if echo "$text_lower" | grep -qw "$symbol"; then
      detected_symbols="${detected_symbols}${symbol}, "
    fi
  done
  detected_symbols="${detected_symbols%, }"

  # Save to journal
  local escaped_text
  escaped_text=$(echo "$text" | sed 's/"/\\"/g')
  echo "{\"timestamp\":\"${entry_ts}\",\"date\":\"${entry_date}\",\"dream\":\"${escaped_text}\",\"detected_symbols\":\"${detected_symbols}\"}" >> "$JOURNAL_FILE"

  echo "  📅 Date: ${entry_date}"
  echo "  🕐 Time: ${entry_ts}"
  echo ""
  echo "  📖 Dream:"
  echo "    ${text}"
  echo ""

  if [[ -n "$detected_symbols" ]]; then
    echo "  🔮 Detected Symbols: ${detected_symbols}"
    echo ""
    echo "  💡 Quick interpretations:"
    for symbol in "${!SYMBOLS[@]}"; do
      if echo "$text_lower" | grep -qw "$symbol"; then
        echo "    • ${symbol^}: ${SYMBOLS[$symbol]:0:80}..."
      fi
    done
  else
    echo "  💡 No known symbols detected. Your dream is unique!"
  fi

  echo ""
  echo "  ✅ Entry saved to journal."
}

cmd_history() {
  echo "📚 Dream Journal History"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  if [[ ! -f "$JOURNAL_FILE" ]] || [[ ! -s "$JOURNAL_FILE" ]]; then
    echo "  📭 No journal entries yet. Use 'journal <text>' to start."
    return 0
  fi

  local count=0
  while IFS= read -r line; do
    count=$((count + 1))
    if command -v jq >/dev/null 2>&1; then
      local date dream symbols
      date=$(echo "$line" | jq -r '.date // "?"')
      dream=$(echo "$line" | jq -r '.dream // "?"')
      symbols=$(echo "$line" | jq -r '.detected_symbols // ""')

      echo "  📅 ${date}"
      echo "    ${dream:0:120}"
      if [[ -n "$symbols" ]]; then
        echo "    🔮 Symbols: ${symbols}"
      fi
      echo ""
    else
      echo "  $line"
      echo ""
    fi
  done < <(tail -20 "$JOURNAL_FILE")

  echo "  📊 Total entries: $(wc -l < "$JOURNAL_FILE")"
  echo "  📁 Journal: $JOURNAL_FILE"
}

cmd_help() {
  cat <<EOF
🌙 Dream Interpreter v${VERSION}
Powered by BytesAgain | bytesagain.com | hello@bytesagain.com

Usage: $(basename "$0") <command> [args]

Commands:
  interpret <symbol>     Look up a dream symbol's meaning
  search <keyword>       Search symbols by keyword
  random                 Get a random dream symbol
  categories             List all symbol categories
  journal <text>         Add a dream journal entry (auto-detects symbols)
  history                View dream journal history
  help                   Show this help
  version                Show version

Symbols: water, flying, falling, teeth, snake, death, house, chase,
         baby, car, fire, dog, cat, spider, ocean, forest, mountain,
         bridge, mirror, rain, door, bird, exam, naked, money, road,
         tree, moon, sun, stairs

Examples:
  $(basename "$0") interpret water
  $(basename "$0") search fear
  $(basename "$0") journal "I was flying over an ocean with a bright moon"
  $(basename "$0") random
EOF
}

cmd_version() {
  echo "${SCRIPT_NAME} v${VERSION}"
  echo "Powered by BytesAgain | bytesagain.com | hello@bytesagain.com"
}

# --- main -------------------------------------------------------------------

case "${1:-help}" in
  interpret)   shift; cmd_interpret "$@" ;;
  search)      shift; cmd_search "$@" ;;
  random)      cmd_random ;;
  categories)  cmd_categories ;;
  journal)     shift; cmd_journal "$@" ;;
  history)     cmd_history ;;
  version)     cmd_version ;;
  help|*)      cmd_help ;;
esac
