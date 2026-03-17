#!/bin/bash
# =============================================================================
# SocialConductor — OpenClaw Skill Setup Script (All Platforms)
# Run this once on your Mac to install OpenClaw and publish your skill
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

divider() { echo -e "${BLUE}──────────────────────────────────────────────────────────${NC}"; }
header()  { echo ""; divider; echo -e "${BOLD}${CYAN}  $1${NC}"; divider; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warn()    { echo -e "${YELLOW}⚠️  $1${NC}"; }
info()    { echo -e "${BLUE}ℹ️  $1${NC}"; }
error()   { echo -e "${RED}❌ $1${NC}"; exit 1; }
step()    { echo -e "\n${BOLD}▶ $1${NC}"; }

# =============================================================================
# BANNER
# =============================================================================
clear
echo ""
echo -e "${CYAN}${BOLD}"
echo "  ╔═══════════════════════════════════════════════════════════╗"
echo "  ║   SocialConductor — OpenClaw Skill Setup 📺🎵👥🦞         ║"
echo "  ╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "  Publishes a unified OpenClaw skill covering:"
echo -e "  ${GREEN}📺${NC} YouTube   — studio.socialconductor.ai  ${GREEN}(live)${NC}"
echo -e "  ${YELLOW}🎵${NC} TikTok    — violin.socialconductor.ai  ${YELLOW}(coming soon)${NC}"
echo -e "  ${YELLOW}👥${NC} Facebook  — podium.socialconductor.ai  ${YELLOW}(coming soon)${NC}"
echo ""
echo -e "  This script will:"
echo -e "  ${GREEN}1.${NC} Check / install Node.js"
echo -e "  ${GREEN}2.${NC} Install the OpenClaw CLI"
echo -e "  ${GREEN}3.${NC} Install the ClawHub CLI"
echo -e "  ${GREEN}4.${NC} Create your unified SKILL.md"
echo -e "  ${GREEN}5.${NC} Log you into ClawHub"
echo -e "  ${GREEN}6.${NC} Publish your skill"
echo ""
echo -e "  ${YELLOW}Estimated time: ~5 minutes${NC}"
echo ""

read -p "  Press Enter to begin, or Ctrl+C to cancel..."

# =============================================================================
# STEP 1 — CHECK NODE.JS
# =============================================================================
header "STEP 1 of 6 — Checking Node.js"

if command -v node &>/dev/null; then
    NODE_VER=$(node --version)
    NODE_MAJOR=$(echo "$NODE_VER" | sed 's/v//' | cut -d. -f1)
    if [ "$NODE_MAJOR" -ge 18 ]; then
        success "Node.js $NODE_VER is installed (18+ required)"
    else
        warn "Node.js $NODE_VER is too old. Need 18+. Installing via Homebrew..."
        if ! command -v brew &>/dev/null; then
            error "Homebrew not found. Install it first: https://brew.sh then re-run this script."
        fi
        brew install node
        success "Node.js installed via Homebrew"
    fi
else
    warn "Node.js not found. Installing via Homebrew..."
    if ! command -v brew &>/dev/null; then
        echo -e "  ${YELLOW}Homebrew not found. Installing Homebrew first...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install node
    success "Node.js installed"
fi

# =============================================================================
# STEP 2 — INSTALL OPENCLAW CLI
# =============================================================================
header "STEP 2 of 6 — Installing OpenClaw CLI"

if command -v openclaw &>/dev/null; then
    OC_VER=$(openclaw --version 2>/dev/null || echo "unknown")
    success "OpenClaw already installed ($OC_VER)"
    info "Updating to latest version..."
    npm update -g openclaw@latest 2>/dev/null || true
else
    step "Installing OpenClaw globally..."
    npm install -g openclaw@latest
    success "OpenClaw CLI installed"
fi

# =============================================================================
# STEP 3 — INSTALL CLAWHUB CLI
# =============================================================================
header "STEP 3 of 6 — Installing ClawHub CLI"

if command -v clawhub &>/dev/null; then
    CH_VER=$(clawhub --version 2>/dev/null || echo "unknown")
    success "ClawHub already installed ($CH_VER)"
    info "Updating to latest version..."
    npm update -g clawhub@latest 2>/dev/null || true
else
    step "Installing ClawHub globally..."
    npm install -g clawhub@latest
    success "ClawHub CLI installed"
fi

# =============================================================================
# STEP 4 — CREATE SKILL FOLDER AND SKILL.MD
# =============================================================================
header "STEP 4 of 6 — Creating unified SKILL.md"

SKILL_DIR="$HOME/socialconductor-skill"

if [ -d "$SKILL_DIR" ]; then
    warn "Skill folder already exists at $SKILL_DIR"
    read -p "  Overwrite SKILL.md with latest version? (y/N): " OVERWRITE
    if [[ ! "$OVERWRITE" =~ ^[Yy]$ ]]; then
        info "Keeping existing SKILL.md"
        WRITE_SKILL=false
    else
        WRITE_SKILL=true
    fi
else
    mkdir -p "$SKILL_DIR"
    WRITE_SKILL=true
fi

if [ "$WRITE_SKILL" = true ]; then
    step "Writing SKILL.md to $SKILL_DIR..."

cat > "$SKILL_DIR/SKILL.md" << 'SKILLEOF'
---
name: socialconductor
description: Control all your SocialConductor AI bots from WhatsApp, Slack, or Telegram. Manage your YouTube, TikTok, and Facebook/Instagram comment automation — check status, pause replies, view logs, post manual replies, and manage video polling — all from chat.
version: 1.1.0
metadata:
  openclaw:
    requires:
      env:
        - SC_YT_API_KEY
    emoji: "🤖"
    homepage: https://studio.socialconductor.ai
    primaryEnv: SC_YT_API_KEY
---

# SocialConductor — All Platforms

Control all your SocialConductor AI comment bots from any chat app.

## Platforms

| Platform | Status | App URL |
|----------|--------|---------|
| 📺 YouTube | ✅ Live | studio.socialconductor.ai |
| 🎵 TikTok | 🔜 Coming Soon | violin.socialconductor.ai |
| 👥 Facebook / Instagram | 🔜 Coming Soon | podium.socialconductor.ai |

---

## YouTube — Setup (first time only)

Say this to OpenClaw:

> connect my youtube channel

OpenClaw will register you, then send a one-time browser link. Open it, sign
in with Google (30 seconds), close the tab. All commands are now active.

## YouTube — Commands

| Say this | What happens |
|----------|-------------|
| check my youtube bot status | Mode, plan, daily usage, last 3 comments |
| pause my youtube bot | Hold mode ON — replies stop immediately |
| resume my youtube bot | Hold mode OFF — replies resume |
| show recent youtube comments | Last 5 log entries |
| show posted youtube comments | Only live-posted replies |
| show youtube gate skipped comments | Comments the bot skipped |
| show youtube leads | Lead-trigger comments only |
| reply to youtube comment abc123 with Great question! | Posts manual reply |
| turn on fast youtube response mode | Sets delay mode to fast |
| turn on aggressive youtube response mode | Sets delay mode to aggressive |
| turn on youtube simulation mode | Replies generated but not posted |
| go youtube live | Disables simulation — bot posts for real |
| enable my youtube bot | Turns on auto-reply |
| disable my youtube bot | Turns off auto-reply |
| show my youtube videos | Video polling status |
| show stale youtube videos | Videos with no recent activity |
| reactivate youtube video abc123 | Resumes polling that video |

## YouTube — Webhook Base URL
https://studio.socialconductor.ai/api/openclaw/

---

## TikTok — Coming Soon 🔜

TikTok bot control via chat is in development.
Visit violin.socialconductor.ai to manage your TikTok bot in the meantime.

Planned commands:
- check my tiktok bot status
- pause my tiktok bot / resume my tiktok bot
- show recent tiktok comments
- show tiktok leads
- reply to tiktok comment abc123 with Great video!

---

## Facebook / Instagram — Coming Soon 🔜

Facebook and Instagram bot control via chat is in development.
Visit podium.socialconductor.ai to manage your Facebook bot in the meantime.

Planned commands:
- check my facebook bot status
- pause my facebook bot / resume my facebook bot
- show recent facebook comments
- show facebook leads
- reply to facebook comment abc123 with Thanks!

---

## Auth
Bearer token — stored automatically by OpenClaw after setup.
Each platform will use its own API key registered at setup time.

## Registration Flow
On first use OpenClaw calls POST /api/openclaw/register with your openclaw_user_id.
Your API key is stored locally and sent as a Bearer token on every subsequent call.
To link your YouTube channel, OpenClaw calls POST /api/openclaw/link_token and sends
you a browser link. After OAuth your channel is permanently connected.
SKILLEOF

    success "SKILL.md written to $SKILL_DIR/SKILL.md"
fi

# Preview
echo ""
echo -e "  ${BOLD}Preview:${NC}"
head -14 "$SKILL_DIR/SKILL.md" | sed 's/^/    /'

# =============================================================================
# STEP 5 — CLAWHUB LOGIN
# =============================================================================
header "STEP 5 of 6 — Logging into ClawHub"

echo ""
info "ClawHub uses GitHub for authentication."
info "A browser window will open — sign in with GitHub."
echo ""
warn "Your GitHub account must be at least 1 week old to publish."
echo ""
read -p "  Press Enter to open ClawHub login..."

clawhub login

echo ""
success "ClawHub login complete"

# =============================================================================
# STEP 6 — PUBLISH
# =============================================================================
header "STEP 6 of 6 — Publishing to ClawHub"

echo ""
info "Publishing from: $SKILL_DIR"
echo ""

cd "$SKILL_DIR"
clawhub publish .

echo ""
success "Skill published to ClawHub!"

# =============================================================================
# DONE
# =============================================================================
echo ""
divider
echo -e "${GREEN}${BOLD}"
echo "  🎉  ALL DONE!"
echo -e "${NC}"
echo -e "  Your unified skill is live on ClawHub."
echo ""
echo -e "  ${BOLD}Your customers install it with:${NC}"
echo -e "  ${CYAN}  clawhub install <your-github-username>/socialconductor${NC}"
echo ""
echo -e "  ${BOLD}Then in WhatsApp / Slack / Telegram they say:${NC}"
echo -e "  ${CYAN}  \"connect my youtube channel\"   → works now${NC}"
echo -e "  ${CYAN}  \"pause my tiktok bot\"          → shows coming soon message${NC}"
echo -e "  ${CYAN}  \"check my facebook status\"     → shows coming soon message${NC}"
echo ""
echo -e "  ${BOLD}When TikTok/Facebook routes are ready, bump the skill:${NC}"
echo -e "  ${CYAN}  cd $SKILL_DIR${NC}"
echo -e "  ${CYAN}  # Edit SKILL.md — bump version: 1.1.0 → 1.2.0${NC}"
echo -e "  ${CYAN}  # Change 🔜 Coming Soon to ✅ Live for each platform${NC}"
echo -e "  ${CYAN}  # Add the new commands to the command tables${NC}"
echo -e "  ${CYAN}  clawhub publish .${NC}"
echo ""
echo -e "  ${BOLD}Skill folder:${NC}"
echo -e "  ${CYAN}  $SKILL_DIR${NC}"
echo ""
divider
echo ""

read -p "  Open skill folder in Finder? (y/N): " OPEN_FINDER
if [[ "$OPEN_FINDER" =~ ^[Yy]$ ]]; then
    open "$SKILL_DIR"
fi

echo ""
