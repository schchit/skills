---
name: proactive
description: 🦊 Proactive — An autonomous, self-improving companion for OpenClaw. Learns your interests, adapts its behavior, and reaches out at the right moment — without being annoying.
homepage: https://github.com/Wewillsee86/proaktiv-skill
metadata:
  openclaw:
    emoji: 🦊
    requires:
      bins: [python3, openclaw]
      env: [OPENCLAW_TELEGRAM_NR]
    primaryEnv: OPENCLAW_TELEGRAM_NR
---

# 🦊 Proactive — The Living Companion

## ⚠️ Installation — Telegram Only / Nur über Telegram

### 🇩🇪 Deutsch
Dieser Skill muss **zwingend über Telegram installiert werden** — nicht über das Web-UI!

1. Öffne deinen Telegram-Bot
2. Schreibe dem Bot den Install-Befehl
3. Beantworte alle Fragen direkt in Telegram
4. Der Skill richtet sich automatisch für deinen Account ein

> ⚠️ **Installation über das Web-UI führt zu Routing-Fehlern** — Nachrichten landen dann nicht in Telegram!

### 🇬🇧 English
This skill **must be installed via Telegram** — not through the Web-UI!

1. Open your Telegram bot
2. Send the install command to your bot
3. Answer all questions directly in Telegram
4. The skill will automatically configure itself for your account

> ⚠️ **Installing via Web-UI will cause routing errors** — messages will not be delivered to Telegram!

---

## What Is This?

Proactive transforms OpenClaw into a smart companion that actively looks out for you. Instead of waiting for commands, it monitors what matters and sends you timely pings — updates on your favorite sports, breaking news in your field, reminders at the right moment. And it gets better over time by learning from every interaction.

## How It Works

Every 30 minutes, Proactive runs a decision cycle:

```
Should I ping my user right now?
  ├── Is it quiet hours? → Nightshift: run memory cleanup, then sleep
  ├── Morning (7:00–9:00)? → Morning briefing
  ├── Ping pressure high enough? → Send targeted topic ping
  └── Otherwise? → Wait silently
```

## Core Features

### 1. Breathing Interest Graph
Proactive tracks your topics across three states:
- **Hot** — actively discussed recently → gets pings
- **Emerging** — mentioned a few times → promoted toward Hot
- **Dormant** — not mentioned for days → cooled down, stops getting pings

Topics with more engagement get pinged more often. Topics you ignore fade away automatically.

### 2. Morning Briefing (7:00–9:00)
Every morning (once per day, configurable), you get a structured briefing:
- Today's calendar events
- Important unread emails
- Weather at your location
- Breaking news in your interests

### 3. Topic-Based Pings (30-min Cycle)
Throughout the day, Proactive decides whether to ping based on:
- **Budget**: max 6-8 pings per day (resets at midnight)
- **Pressure**: chance increases the longer you've been silent
- **Recent history**: won't ping the same topic twice in a row

Example topics:
- `f1`: Race week — Thursday build-up, Friday first practice results, Saturday quali, Sunday is quiet
- `ki_news`: Monday–Friday mornings — latest AI/LLM developments relevant to your setup
- `n8n`: When something breaks or a new workflow pattern is relevant
- `turkish`: Cultural/entertainment — weekend vibes, memes, casual check-ins

### 4. Quiet Hours & Nightshift (21:00–07:30)
During quiet hours, Proactive stops sending pings. But it still works in the background:

When quiet hours start, the **Nightshift Module** kicks in:
1. Reads the day's `proaktiv_state.json` (conversation highlights captured during the day)
2. Extracts key decisions, corrections, and preferences
3. Updates `proaktiv_state.json` with compacted daily memory
4. Clears the buffer
5. Goes to sleep — silently, no chat message

### 5. Feedback Loop
After every ping you react to (reply, emoji, anything), Proactive scores that interaction:
- **Positive reaction** → topic gets a boost, pressure resets
- **No reaction** → topic cools down, pressure increases
- **Negative reaction** ("stop", "not this again") → topic goes on a temporary no-go list
- **Apology protocol** → if a ping annoyed you, Proactive acknowledges it and adjusts

### 6. WAL Protocol (Write-Ahead Log)
Proactive maintains a live working state. During conversation, it scans for:
- **Corrections**: "No, it's X not Y" / "Actually..."
- **Decisions**: "Let's go with option B" / "Use X instead"
- **Preferences**: "I prefer dark mode" / "I like X more than Y"
- **Key facts**: new names, URLs, numbers, deadlines

These get written to `proaktiv_state.json` immediately — before answering. This survives context clears and compaction.

### 7. 60% Context Buffer
When the conversation gets long (~60% context used), Proactive starts mirroring the conversation essence to `proaktiv_state.json`. This file bridges context loss and nightly compaction. After a context clear, Proactive reads the buffer first and recovers the thread.

## Architecture

```
proaktiv_check.py     ← Main loop. Runs every 30 min via OpenClaw Cron
                     ← Decides: ping / nightshift / sleep
                     ← Contains interest_evolve logic (daily evolution)
feedback_update.py    ← Called after every user reaction. Updates scores
```

Supporting files (created on install — no personal data in templates):
```
proaktiv_state.json     ← Daily budget, quiet hours config, last ping dates
interest_graph.json     ← Topic scores, temperatures, cooldown state
social_knowledge.json  ← Tracked goals, commitments, no-go list
```

## Installation

```bash
git clone https://github.com/Wewillsee86/proaktiv-skill.git
cd proaktiv-skill
bash install.sh
```

The installer will:
1. Copy all scripts to `/data/.openclaw/skills/proaktiv/`
2. Copy template JSON files (empty state — no personal data)
3. **Auto-detect your Telegram session** (dynamic UUID lookup)
4. Set up the OpenClaw Cron job (every 30 minutes, Europe/Berlin)
5. Fire the onboarding interview via Telegram

### Finding Your Telegram Chat ID
Message [@userinfobot](https://t.me/userinfobot) on Telegram. It will reply with your numeric user ID. Enter that during install.

### Manual Setup (skip chat ID prompt)
```bash
echo "OPENCLAW_TELEGRAM_NR=YOUR_CHAT_ID" > /data/.openclaw/skills/proaktiv/.env
chmod 600 /data/.openclaw/skills/proaktiv/.env
```

## Configuration

### Quiet Hours
Default: 22:00–07:30 (Europe/Berlin). Override during onboarding:
```
[SETUP-QUIET: 21-08]
```

### Daily Ping Budget
Default: 8 pings/day (weekdays) / 10 pings/day (weekends). Resets at midnight. Hard cap — Proactive won't exceed it.

### No-Go Topics
Tell Proactive topics to never ping about:
```
[SETUP-NOGO: politics]
[SETUP-NOGO: crypto]
```

### Topic Time Windows
Each topic has a preferred time window. Examples:
- `f1`: Any time during race week; quiet on Sundays
- `ki_news`: Weekdays only, mornings
- `morning_briefing`: Only 7:00–9:00

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENCLAW_TELEGRAM_NR` | Yes | Your Telegram chat ID. Written to `.env` during install. |

## Cron Job

Proactive registers a single cron job on install:
```
PROAKTIV-30min  */30 * * * *  (Europe/Berlin)
```

Runs via `--session-key agent:main:telegram:direct:<ID>` — routes directly to your Telegram session.

## Permissions

- **Cron**: every 30 min, autonomous
- **File system**: read/write `/data/.openclaw/skills/proaktiv/`
- **Telegram**: send direct messages to configured chat ID
- **Chat context**: reads recent chat history for morning briefing personalization (via OpenClaw CLI)
- **Working buffer**: writes conversation highlights to `proaktiv_state.json` during long sessions
  — this survives context loss and feeds the nightly memory compaction

## Example Pings

**Morning Briefing:**
> "Good morning! You've got a dentist appointment at 10am. One urgent email from Stripe. Weather: 8°C and rainy. F1: Hamilton contract extension announced. Want details?"

**F1 Race Week (Thursday):**
> "Japanese GP is this Sunday! Schedule: FP1 Fri 04:00, FP2 Fri 08:00, Quali Sat 08:00, Race Sun 07:00 CET. Want me to pull up the championship standings?"

**KI News (Monday morning):**
> "Weekend AI roundup: OpenAI dropped a new model, plus rumors about an Anthropic investment round. Want the details?"

**Nightshift complete (silent — no chat sent):**
> *(nothing — Proactive updates proaktiv_state.json and goes to sleep)*

## Extending Proactive

### Adding a New Topic
1. Add to `interest_graph.json` under `interests`:
```json
"my_topic": {
  "temperature": 0.5,
  "weight": 1.0,
  "status": "candidate"
}
```
2. Add time window in `proaktiv_check.py` (look for `TW` definitions):
```python
TW = {
    ...
    "my_topic": {"from": 9, "to": 22, "weekend": True},
}
```

### Adjusting Ping Frequency
- Lower budget: edit `DAILY_BUDGET` in `proaktiv_check.py`
- Higher pressure cap: edit `PRESSURE_MAX`
- More topics active: increase `MAX_PROMOTIONS_PER_DAY` in `interest_evolve.py`

## Open for Contribution

Open source — PRs, forks, and ideas are welcome. The codebase is readable and heavily commented. Fork it and build your own version.

## Changelog

- **v1.0.31**: Fix — `last_run_date` in `proaktiv_state.json` wird jetzt nach jedem Lauf korrekt aktualisiert.
- **v1.0.30**: Fix — Install-Reihenfolge verifiziert (Auto-UUID-Lookup aus aktiver Telegram-Session). ClawHub: Telegram-Only-Warning DE/EN hinzugefügt.
- **v1.0.29**: Production Release — Dynamic UUID lookup via `openclaw sessions --json`, `--session-key agent:main:telegram:direct:`, `--system-event` Cron, explizite Fehlermeldung, dual-language Install-UX.
- **v1.0.28**: RC — Dynamic UUID lookup, explicit routing, blocking 120s `subprocess.run()`, dual-language install UX.
- **v1.0.23**: Bugfix — Split-Brain-Amnesie behoben (Session-ID fest verdrahtet auf `agent:main:telegram:direct:{tg_nr}`).
- **v1.0.21**: Bugfix — Telegram-Routing-Flags (`--reply-channel`, `--reply-to`) für async delivery wiederhergestellt.
- **v1.0.19**: Strict Silence Policy — Fallback-Telegram-Code komplett entfernt. Bei `inject_trigger()`-Fehler: nur Log, kein Direkt-Fallback.
- **v1.0.18**: Fix routing — `inject_trigger()` sends to MAIN session instead of Telegram. SOUL.md processes trigger, generates researched content, sends proper message.
- **v1.0.9**: Topic Templates Module — all topic rules in `TOPIC_TEMPLATES.md`. Generic fallback for custom interests.
- **v1.0.8**: Fix .env loading.
- **v1.0.7**: Remove deceptive onboarding text. Permission transparency.
- **v1.0.6**: Full English rebrand.
- **v1.0.5**: Privacy fix.
- **v1.0.4**: Nightshift Module.
- **v1.0.3**: Interactive install.
- **v1.0.1**: Initial ClawHub release.

## License

MIT — see LICENSE file
