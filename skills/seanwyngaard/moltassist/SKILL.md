---
name: moltassist
description: "Unified event-driven notification backbone for OpenClaw. Handles routing, formatting, quiet hours, rate limiting, and optional LLM enrichment across Telegram, WhatsApp, and Discord. Use when: (1) a skill needs to fire a notification to the user, (2) checking notification status or logs, (3) configuring notification routing/categories. NOT for: direct channel messaging without the notification pipeline."
homepage: https://github.com/seanwyngaard/moltassist
metadata: { "openclaw": { "emoji": "🔔", "requires": { "python": ">=3.10", "openclaw": ">=2026.1.8" } } }
---

# MoltAssist — Skill Interface

MoltAssist is OpenClaw's shared notification layer. Skills call `notify()` to send alerts — MoltAssist handles routing, formatting, dedup, quiet hours, rate limiting, and optional LLM enrichment.

**MoltAssist is event-driven. It reacts to triggers from other skills — it never initiates on its own.**

## Security and Transparency

- **No credentials stored.** Delivery uses `openclaw message send` — MoltAssist delegates entirely to OpenClaw's existing channel credentials. It never reads, stores, or handles API tokens or bot tokens.
- **Local web server is opt-in, localhost-only.** The `/moltassist config` command starts a plain HTTP server on `127.0.0.1:7430` on demand. It is not accessible outside your machine. It auto-closes after 30 minutes. It only reads and writes `moltassist/config.json`.
- **File writes are scoped to OPENCLAW_WORKSPACE.** All files written by MoltAssist are under `~/.openclaw/workspace/moltassist/` (config, logs, queue, custom pollers) or `~/.openclaw/workspace/memory/` (scheduler state, poll log). Nothing is written outside the OpenClaw workspace.
- **No network calls except through OpenClaw.** The only outbound calls MoltAssist makes are: (1) CoinGecko public API for crypto prices (no key required), (2) `openclaw message send` for delivery, (3) `openclaw agent --local` for LLM enrichment (optional, uses your existing model). No data is sent to any MoltAssist server — there is no MoltAssist server.

---

## Slash Commands

### /moltassist onboard

Start the interactive onboarding flow. Runs entirely in-chat in ~5 steps.

**What it does:**
1. Detects your current channel (Telegram / WhatsApp / Discord)
2. Asks your role (free text if LLM available, buttons if not)
3. Asks which categories matter to you (multi-select)
4. Maps your role to a profile, detects installed skills, recommends missing ones
5. Generates `moltassist/config.json`

**Example output:**
```
Welcome to MoltAssist! Let's get you set up.

Which channel should I use for notifications?
[Telegram] [WhatsApp] [Discord]
```

After completion:
```
Config saved! You're set up with:
  - Telegram (all urgency levels)
  - Email, Calendar, Crypto, Weather enabled
  - Quiet hours: 23:00–08:00

Run /moltassist config to fine-tune anytime.
```

**Edge cases:**
- If already onboarded: warns that re-running will overwrite existing config, asks for confirmation.
- If no channel is configured in OpenClaw: tells the user to set up a channel first.

---

### /moltassist config

Open the localhost configuration dashboard in your browser.

**What it does:**
- Launches a local HTTP server on `127.0.0.1:7430` (localhost only — not accessible externally)
- Opens `http://localhost:7430` in your default browser
- Dashboard shows: category toggles, delivery routing, quiet hours, rate limits, recent activity
- Saves directly to `moltassist/config.json` — no restart needed
- Server auto-closes after 30 minutes of inactivity

**Example output:**
```
Dashboard running at http://localhost:7430
Opening in your browser...

(Server will auto-close after 30 min of inactivity)
```

**Edge cases:**
- If not yet onboarded: responds with "Run /moltassist onboard first to generate your config."
- If port 7430 is in use: reports the conflict and suggests killing the existing process.

---

### /moltassist status

Show current configuration summary at a glance.

**Example output:**
```
MoltAssist v0.1.0 — Status

Enabled categories:
  📧 Email        (medium+, LLM enriched)
  🗓 Calendar     (medium+, LLM enriched)
  ₿  Crypto       (medium+, plain)
  🌤️ Weather      (low+, plain)
  🔧 System       (high+, plain)
  🔔 Custom       (medium+, plain)

Delivery:
  Default channel: Telegram
  Critical → Telegram
  Quiet hours: 23:00–08:00

LLM mode: none
Installed skills: gog, weather
```

---

### /moltassist log

Show alerts fired in the last 24 hours, grouped by category.

**Example output:**
```
Last 24h — 7 alerts fired, 2 queued overnight

📧 Email (3): Mark re: contract [high], Newsletter [low x2]
₿  Crypto (2): BTC -6% [high], ETH +8% [medium]
🗓 Calendar (1): Standup in 15min [medium]
🔧 System (1): price_alert.py error [high]
```

**Filter by category:** `/moltassist log crypto`
**Filter by urgency:** `/moltassist log high`

---

### /moltassist snooze [category] [duration]

Temporarily disable notifications for a category.

**Usage:** `/moltassist snooze crypto 2h`

**Duration format:** `30m`, `1h`, `2h`, `4h`, `8h`, `12h`, `24h`

**Example output:**
```
Crypto notifications snoozed for 2h (until 16:30).
Critical alerts will still fire.

To cancel: /moltassist snooze crypto off
```

---

### /moltassist test

Send a test notification through the full pipeline to verify delivery is working.

**Example output:**
```
Test notification sent!

Pipeline: config ✅ → dedup ✅ → format ✅ → deliver ✅
Channel: Telegram
```

---

### /moltassist scheduler install

Install the background system job that runs pollers automatically.

- **macOS:** writes a launchd plist to `~/Library/LaunchAgents/ai.moltassist.poll.plist`
- **Linux:** adds a crontab entry
- Runs `python3 -m moltassist.poll --workspace <path>` every 1 minute

---

### /moltassist scheduler uninstall

Remove the background system job. Polling stops immediately.

---

### /moltassist scheduler status

Show whether the scheduler is installed and the last run time per category.

---

### /moltassist poll now [category]

Run a specific poller immediately, bypassing the interval check. Useful for testing.

**Usage:** `/moltassist poll now crypto`

---

### /moltassist reload

Hot-reload configuration from disk without restarting the process.

---

## Python Interface — notify()

The `notify()` function is the single entry point for all skill integrations.

### Import Pattern (with graceful fallback)

```python
try:
    from moltassist import notify
    MOLTASSIST = True
except ImportError:
    MOLTASSIST = False

if MOLTASSIST:
    notify(message="...", urgency="medium", category="email")
```

Skills must always work without MoltAssist installed.

### Function Signature

```python
def notify(
    message: str,
    urgency: str = "medium",        # "low" | "medium" | "high" | "critical"
    category: str = "custom",
    source: str = "unknown",
    action_hint: str | None = None,
    llm_hint: bool = False,
    event_id: str | None = None,
    dry_run: bool = False,
) -> dict
```

### Return Value

```python
{
    "sent": bool,
    "channel": str | None,
    "queued": bool,
    "dry_run": bool,
    "error": str | None,
}
```

### Pipeline (every notify() call)

1. Config check — category enabled, urgency threshold met
2. Lockfile — single instance guard
3. Quiet hours — queue if inside window (unless critical)
4. Rate limit — per-category-per-hour cap
5. Dedup — same event_id never sent twice
6. LLM enrichment — optional, 10s timeout, fallback to raw message
7. Channel router — pick channel by urgency routing config
8. Formatter — Telegram MarkdownV2, WhatsApp plain text
9. Deliver — via `openclaw message send`, return code verified
10. Failure handling — log error, clear queue on permanent failure
11. Log — write to `moltassist/memory/moltassist-log.json`

---

## Example Integrations

### Email alert

```python
try:
    from moltassist import notify
    MOLTASSIST = True
except ImportError:
    MOLTASSIST = False

def on_important_email(sender, subject, last_contact_days):
    msg = f"{sender} emailed: {subject}"
    if last_contact_days and last_contact_days > 30:
        msg += f" — last contact {last_contact_days} days ago"
    if MOLTASSIST:
        notify(
            message=msg,
            urgency="high",
            category="email",
            source="gog",
            action_hint="Reply now",
            llm_hint=True,
            event_id=f"email_{sender}_{subject[:20]}",
        )
```

### Crypto price alert

```python
try:
    from moltassist import notify
    MOLTASSIST = True
except ImportError:
    MOLTASSIST = False

def on_price_move(coin, pct_change, current_price):
    urgency = "critical" if abs(pct_change) > 10 else "high" if abs(pct_change) > 5 else "medium"
    direction = "dropped" if pct_change < 0 else "rose"
    if MOLTASSIST:
        notify(
            message=f"{coin} {direction} {abs(pct_change):.1f}% — now ${current_price:,.0f}",
            urgency=urgency,
            category="crypto",
            source="price_alert",
            action_hint="Check exchange",
            event_id=f"{coin.lower()}_{int(time.time() // 3600)}",
        )
```

---

## Categories

| Category | Emoji | Required Skill | Built-in |
|----------|-------|---------------|----------|
| email | 📧 | gog | no |
| calendar | 🗓 | gog | no |
| crypto | ₿ | — | yes |
| health | 💪 | health | no |
| weather | 🌤️ | weather | no |
| dev | 👨‍💻 | github | no |
| finance | 💰 | — | partial |
| compliance | 📋 | — | yes |
| travel | ✈️ | — | no |
| staff | 👥 | — | yes |
| social | 📱 | — | yes |
| system | 🔧 | — | yes |
| custom | 🔔 | — | yes |

## Urgency Levels

| Level | Meaning | Quiet Hours | Rate Limited |
|-------|---------|-------------|-------------|
| low | FYI — weather, minor updates | Queued | Yes |
| medium | Default — most alerts | Queued | Yes |
| high | Important — needs attention | Queued | Yes |
| critical | Emergency — always fires | Bypasses | Yes |
