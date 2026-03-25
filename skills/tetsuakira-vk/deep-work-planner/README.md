# Deep Work Planner

**Turn your chaotic task list into a focused, time-blocked day — in seconds.**

Stop starting your morning staring at a wall of undifferentiated tasks. Deep Work Planner takes your raw brain dump, scores every item by impact and urgency, and hands you back a structured daily schedule built around protected 90-minute deep work sessions. No friction. No fluff. Just a plan you can actually follow.

---

## What it does

- **Sorts your tasks by impact and urgency** — using a weighted priority score that stops you from spending all day on urgent-but-unimportant busywork
- **Generates a time-blocked daily schedule** — structured around 90-minute deep work sessions scheduled at your peak energy hours
- **Labels every task** as Deep Work 🔵, Shallow Work 🟡, or Admin 🔘 — so you know exactly what mode you should be in and when
- **Flags energy-draining low-value tasks** — with a specific recommendation to eliminate, delegate, batch, or automate each one
- **Outputs a clean, copy-pasteable schedule block** — ready to drop into Notion, your calendar, or a plain text file without any cleanup

---

## Who it's for

**Knowledge workers** who spend their days in meetings and email and can never seem to carve out time for the work that actually matters.

**Freelancers and consultants** juggling multiple clients and projects who need a daily structure that keeps revenue-generating work front and centre.

**Founders and solopreneurs** pulled in ten directions at once who need a ruthless prioritisation system that protects strategic thinking time.

**Writers, researchers, and creators** who know deep focus is their core asset but keep letting reactive tasks eat into it.

**Anyone who ends the day having been "busy" but not productive** — and wants that to stop.

---

## Installation

```bash
npx clawhub install tetsuakira-vk/deep-work-planner
```

Once installed, the skill is available immediately inside Claude Code. No API keys, no configuration, no additional setup required.

---

## Usage

### Example 1 — Quick brain dump

**Input:**
```
Write newsletter issue #12, reply to 3 client emails, update project tracker, 
research competitors for Q3 deck, fix bug on checkout page, schedule podcast 
guest, pay contractor invoice, review team PRs, prep for Friday board call
```

**Output (excerpt):**
```
───────────────────────────────────────
🗓️  DEEP WORK SCHEDULE — Today
───────────────────────────────────────

⏰ 09:00 – 10:30  │ 🔵 DEEP WORK BLOCK 1
                  │ → Write newsletter issue #12

☕ 10:30 – 10:45  │ BREAK — step away from screens

⏰ 10:45 – 12:15  │ 🔵 DEEP WORK BLOCK 2
                  │ → Research competitors for Q3 deck
                  │ → Fix bug on checkout page

🍽️  12:15 – 13:15  │ LUNCH — protect this time

⏰ 13:15 – 14:45  │ 🟡 SHALLOW WORK BLOCK
                  │ → Reply to 3 client emails
                  │ → Review team PRs
                  │ → Schedule podcast guest

⏰ 15:00 – 16:00  │ 🔘 ADMIN BLOCK
                  │ → Pay contractor invoice
                  │ → Update project tracker

⏰ 16:00 – 16:30  │ 🔲 BUFFER / WRAP-UP
                  │ → Prep notes for Friday board call
───────────────────────────────────────
```

---

### Example 2 — Constrained day with a deadline

**Input
