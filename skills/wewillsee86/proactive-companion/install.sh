#!/usr/bin/env bash
# ============================================================
# Proactive v1.0.34 — Installer
# ============================================================

set -e

echo "Proactive v1.0.30 Installer"
echo "==========================="

# --- CONFIG ---
TARGET_DIR="/data/.openclaw/skills/proaktiv"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
OPENCLAW_BIN="${OPENCLAW_BIN:-openclaw}"

# --- STEP 1: Create directory ---
echo "[1/7] Creating directory structure..."
mkdir -p "$TARGET_DIR"

# --- STEP 2: Copy scripts ---
echo "[2/7] Copying scripts..."
cp "$REPO_DIR/proaktiv_check.py"     "$TARGET_DIR/"
cp "$REPO_DIR/interest_evolve.py"   "$TARGET_DIR/"
cp "$REPO_DIR/feedback_update.py"   "$TARGET_DIR/"

# --- STEP 3: Copy templates ---
echo "[3/7] Copying templates..."
mkdir -p "$TARGET_DIR/templates"
cp "$REPO_DIR/templates/proaktiv_state.json"  "$TARGET_DIR/"
cp "$REPO_DIR/templates/interest_graph.json" "$TARGET_DIR/"
cp "$REPO_DIR/templates/social_knowledge.json" "$TARGET_DIR/"

# --- STEP 4: Copy topic templates ---
echo "[4/7] Copying topic templates..."
cp "$REPO_DIR/TOPIC_TEMPLATES.md" "$TARGET_DIR/"

# --- STEP 5: Auto-extract Telegram session (dynamic lookup) ---
echo "[5/7] Extracting Telegram session..."
echo ""
echo "  Trying to auto-detect your Telegram session..."
echo "  (You must have sent at least one message to your Telegram bot before running this)"

SESSION_JSON=$("$OPENCLAW_BIN" sessions --json 2>/dev/null || echo "{}")
TG_SESSIONS=$(echo "$SESSION_JSON" | python3 -c "
import sys, json
try:
    sessions = json.load(sys.stdin).get('sessions', [])
    tg = [s for s in sessions if 'telegram:direct' in s.get('key', '')]
    if tg:
        tg.sort(key=lambda x: x.get('updatedAt', 0), reverse=True)
        s = tg[0]
        key = s.get('key', '')
        uid = key.split(':')[-1] if ':' in key else ''
        print(s.get('sessionId', '') + '|' + uid)
    else:
        print('')
except:
    print('')
" 2>/dev/null || echo "")

if [ -n "$TG_SESSIONS" ]; then
    TELEGRAM_UUID=$(echo "$TG_SESSIONS" | cut -d'|' -f1)
    TELEGRAM_CHAT_ID=$(echo "$TG_SESSIONS" | cut -d'|' -f2)
    echo "  ✅ Telegram session found!"
    echo "     Session UUID: ${TELEGRAM_UUID:0:16}..."
    echo "     Telegram ID:  $TELEGRAM_CHAT_ID"
else
    echo "  ⚠️  No Telegram session found."
    echo "     The user must send a message to the Telegram bot FIRST."
    echo "     After sending, re-run this installer."
    echo ""
    echo "     Or install manually:"
    echo "       echo 'OPENCLAW_TELEGRAM_NR=YOUR_CHAT_ID' > $TARGET_DIR/.env"
    echo "       chmod 600 $TARGET_DIR/.env"
    echo "       openclaw cron add --name 'PROAKTIV-30min' --cron '*/30 * * * *' --tz 'Europe/Berlin' --session isolated --session-key 'agent:main:telegram:direct:<YOUR_ID>' --system-event '[SYSTEM-TRIGGER: PROAKTIV_CHECK | ambient_context=auto]' --no-deliver"
    echo ""
    # Still create .env as empty marker
    touch "$TARGET_DIR/.env"
fi

# Save Telegram ID to .env if we have it
if [ -n "$TELEGRAM_CHAT_ID" ]; then
    echo "OPENCLAW_TELEGRAM_NR=$TELEGRAM_CHAT_ID" > "$TARGET_DIR/.env"
    chmod 600 "$TARGET_DIR/.env"
    echo "  Saved to $TARGET_DIR/.env"
fi

# --- STEP 6: Make scripts executable ---
echo ""
echo "[6/7] Making scripts executable..."
chmod +x "$TARGET_DIR/proaktiv_check.py"
chmod +x "$TARGET_DIR/interest_evolve.py"
chmod +x "$TARGET_DIR/feedback_update.py"

# --- STEP 7: Remove old PROAKTIV cron jobs ---
echo ""
echo "[7/7] Removing old PROAKTIV cron jobs..."
if "$OPENCLAW_BIN" cron list 2>/dev/null | grep -q "PROAKTIV"; then
    for job_id in $("$OPENCLAW_BIN" cron list 2>/dev/null | grep "PROAKTIV" | awk '{print $1}'); do
        echo "  Removing old cron job: $job_id"
        "$OPENCLAW_BIN" cron rm "$job_id" 2>/dev/null || true
    done
else
    echo "  No old PROAKTIV cron jobs found."
fi

# --- STEP 8: Set up new OpenClaw Cron job (System-Event) ---
echo ""
echo "Setting up new OpenClaw Cron job (every 30 min)..."

if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "  SKIPPED — Telegram session not detected."
    echo "  Install again after sending a message to your Telegram bot."
else
    (
        export OPENCLAW_TELEGRAM_NR="$TELEGRAM_CHAT_ID"
        "$OPENCLAW_BIN" cron add \
            --name "PROAKTIV-30min" \
            --cron "*/30 * * * *" \
            --tz "Europe/Berlin" \
            --session isolated \
            --session-key "agent:main:telegram:direct:$OPENCLAW_TELEGRAM_NR" \
            --system-event "[SYSTEM-TRIGGER: PROAKTIV_CHECK | ambient_context=auto]" \
            --no-deliver \
        && echo "  ✅ PROAKTIV-30min cron registered" \
        || echo "  ⚠️  Could not register cron — run manually."
    )
fi

echo ""
echo "==========================="
echo "Proactive skill installed successfully!"
echo ""
echo "If TELEGRAM_CHAT_ID was auto-detected:"
echo "  - Restart: openclaw gateway restart"
echo "  - The session UUID was extracted from your active Telegram session"
echo ""
echo "If Telegram session was NOT found:"
echo "  1. Send a message to your Telegram bot"
echo "  2. Re-run: bash install.sh"
echo "  Or set manually:"
echo "    echo 'OPENCLAW_TELEGRAM_NR=YOUR_CHAT_ID' > $TARGET_DIR/.env"
echo "==========================="
echo ""
echo "================================================================="
echo "✅ PROAKTIV SKILL INSTALLATION COMPLETE / ERFOLGREICH INSTALLIERT"
echo "================================================================="
echo "🚨 ACTION REQUIRED / WICHTIGER SCHRITT 🚨"
echo ""
echo "EN: Send a short message (e.g., 'Hello') to your Telegram bot NOW"
echo " to initialize the communication session."
echo ""
echo "DE: Schreibe JETZT eine kurze Nachricht (z.B. 'Hallo') an deinen"
echo " Telegram-Bot, um die Kommunikations-Session zu starten."
echo "================================================================="
