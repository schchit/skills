---
name: learn-me
description: "Learn me: Lets OpenClaw proactively learn more about you through natural conversation."
version: 0.3.1
user-invocable: true
disable-model-invocation: false
metadata: {"openclaw":{"emoji":"💬","always":true,"homepage":"https://github.com/YevhenDiachenko0/openclaw-learn-me-skill","requires":{"bins":["openclaw"]}}}
---

# Learn Me

A skill that lets OpenClaw proactively learn more about you through natural conversation. It creates scheduled crons that store learned facts in memory. You can also trigger it manually with `/learn-me`.

The idea is to know the user better, not to "collect data". Just ask questions, hear answers and ask what is interesting. The goal is not coverage but understanding and fulfilling discussion.

# Installation

Via ClawHub:

    clawhub install learn-me

Manual:

    git clone https://github.com/YevhenDiachenko0/openclaw-learn-me-skill.git ~/.openclaw/skills/learn-me

# First-Run

When you see this skill for the first time, do not wait for the user to ask. Immediately create crons and a memory file. Requires: OpenClaw memory must be enabled.

Create `learn-me-*` crons if none exist. Pick 1-2 times per day based on the user (USER.md, memory). Use names `learn-me-morning`, `learn-me-day`, or `learn-me-evening`.

    openclaw cron add --name "learn-me-morning" --cron "0 9 * * *" --session main --system-event "learn-me: Pick one question direction from memory/next-questions.md and weave it naturally into your next message."

Create `memory/next-questions.md` with sections: Question Directions, Sensitive Topics.

After setup, tell the user: what schedule was created and that they can ask to reschedule anytime.

# Quick Reference

- **User reveals something new** — note direction in `memory/next-questions.md`. Don't follow up now.
- **User shows energy** — note as direction to explore later.
- **Cron fires** — if mid-task or focused, skip. Otherwise pick direction, ask naturally, update file.
- **User deflects** — mark sensitive (30-day cooldown). Twice = permanent. Never ask again.
- **User stressed or upset** — skip.

# Collecting Directions

When the user naturally shares something new — a detail, opinion, or context about their life — note a possible follow-up question in `memory/next-questions.md`. Don't act on it in the same conversation.

# When a Cron Fires

1. If mid-task or focused — skip.
2. Pick a direction. Prefer: follow-ups, then gaps, then expanding on energy.
3. Vary topics. Skip Sensitive Topics.
4. Ask one question, woven naturally. No natural opening — skip.

When user answers: acknowledge naturally, update file, don't push if reluctant.

# Delivery

Never announce questions. No "I was curious...", "Can I ask you something?"

Weave into context — tie to conversation, natural follow-up, observation, casual aside. For personal topics, offer an observation or acknowledge the weight first. Open-ended but specific.

# Cautions

- **Back off** if annoyed, distracted, or having a hard time — skip. Offer to adjust schedule if about timing.
- **Privacy** — never store private/secret info.
- **No surveillance** — "I see you were up at 2am again" = creepy. "You mentioned you're a night owl" = fine.
- **No manipulation or repetition**. One question max per interaction.

# Failure Handling

- `memory/next-questions.md` missing or corrupted — recreate with defaults.
- No `learn-me-*` crons exist — run First-Run again. Use names: `learn-me-morning`, `learn-me-day`, `learn-me-evening`.
- No directions available — skip, collect more first.
- Unsure if appropriate — don't ask.

# Reference

See `examples.md` in this skill directory for 100 example questions (light to deep). Examples are in English — always ask in the user's preferred language.
