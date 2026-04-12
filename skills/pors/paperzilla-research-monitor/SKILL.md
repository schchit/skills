---
name: paperzilla-monitor
description: Monitor and triage research papers from Paperzilla projects using the `pz` CLI inside OpenClaw. Use when the user asks to check Paperzilla feeds, review new papers, assess relevance to current work, get a digest, filter irrelevant papers, fetch paper markdown for deep reading, or explicitly deliver a summary via OpenClaw messaging. Triggers include: "check my papers", "what’s new in my feed", "any relevant papers today", "triage my Paperzilla", "paper digest", "review my research feed", or references to a Paperzilla project by name.
version: 1.1.3
homepage: https://docs.paperzilla.ai/guides/cli
allowed-tools: [exec, message]
metadata: { "openclaw": { "requires": { "bins": ["pz"], "config": ["Paperzilla CLI already authenticated locally", "OpenClaw message routing already configured by host"] }, "homepage": "https://docs.paperzilla.ai/guides/cli" } }
---

# Paperzilla Research Monitor (OpenClaw)

Use this workflow to check Paperzilla feeds, triage relevance against current context, and deliver concise digests in chat or Telegram.

## Prerequisites

- Ensure `pz` CLI is installed and authenticated (`pz login` already done).
- Use OpenClaw tools:
  - `exec` for `pz` commands
  - `message` only when the user explicitly asks to deliver a digest/summary to a chat

## Security model

- This skill is primarily a **Paperzilla read/triage** skill.
- It may use the `message` tool **only for user-requested delivery** of a digest or summary.
- It must **not** send unsolicited or proactive messages.
- It must **not** read arbitrary system files, unrelated environment variables, or unrelated credentials.
- It assumes `pz` is already installed and authenticated by the human via `pz login`.
- It assumes OpenClaw messaging is already configured by the host platform. The skill does not acquire, mint, or modify credentials.

If `pz` is missing, run `which pz` and tell the user setup is required before continuing.

## Core CLI model

Keep the Paperzilla object model straight:
- `pz paper <paper-ref>` = canonical paper
- `pz rec <project-paper-ref>` = recommendation inside one project
- `pz feedback <project-paper-ref> ...` = project-specific feedback on that recommendation

When an item comes from `pz feed --json`, prefer `pz rec` and `pz feedback` over `pz paper`.

## CLI Reference

### List projects

```bash
pz project list
```

Returns table with ID, NAME, MODE, VISIBILITY, CREATED.

### Project details

```bash
pz project <project_id>
```

Key fields: Name, Visibility, Matching State, Last Digest, Email settings.

### Feed items

```bash
pz feed <project_id> --limit 20
pz feed <project_id> --limit 20 --json
```

Useful flags:
- `--must-read`
- `--since YYYY-MM-DD`
- `--limit N`
- `--json`
- `--atom`

Use `--json` for structured triage.

### Recommendation details

```bash
pz rec <project_paper_id_or_short_id>
pz rec <project_paper_id_or_short_id> --json
pz rec <project_paper_id_or_short_id> --markdown
```

### Canonical paper details

```bash
pz paper <paper_id_or_short_id>
pz paper <paper_id_or_short_id> --json
pz paper <paper_id_or_short_id> --markdown
pz paper <paper_id_or_short_id> --project <project_id>
```

### Feedback

```bash
pz feedback <project_paper_id> upvote
pz feedback <project_paper_id> star
pz feedback <project_paper_id> downvote --reason not_relevant
pz feedback <project_paper_id> downvote --reason low_quality
pz feedback clear <project_paper_id>
```

If markdown is not ready yet, retry after a short wait.

## Daily Check Workflow

### 1) Identify active project

1. Run `pz project list`.
2. If user specified a project, use it.
3. Otherwise ask once, or use the most recent project from the conversation.

### 2) Establish relevance context

Combine:
- project focus (name/details)
- user’s current stated goal
- explicit include/exclude topics

If unclear, ask one sharp question before triage.

### 3) Fetch latest feed

Default command:

```bash
pz feed <project_id> --limit 20 --json
```

Use recommendation IDs returned by the feed as the primary handles for follow-up actions.

### 4) Triage papers

Classify each item:
- 🟢 Relevant — directly useful now
- 🟡 Tangential — maybe useful later/background
- 🔴 Irrelevant — off current focus

Use title + personalized note/summary + paper metadata as primary evidence. Treat Paperzilla relevance score as a prior, not the final decision.

### 5) Present digest

Keep output scannable:
- Group by 🟢 / 🟡 / 🔴
- For 🟢 and 🟡, include one-line “why it matters”
- For 🔴, list titles only
- Include recommendation short IDs when useful for follow-up

### 6) Deep dive on request

1. If the user asks to **pull the markdown**, use `pz` markdown first, not arXiv HTML/abs pages.
2. If the paper came from a project feed/brief, run `pz rec <project-paper-id> --markdown` first.
3. If you only have a canonical paper ID, run `pz paper <paper-id> --markdown`.
4. If markdown is queued / preparing / not ready, wait and retry a few times before giving up.
5. If needed, run `pz rec <project-paper-id> --json` or `pz paper <paper-id>` for extra metadata/context.
6. Summarize:
   - core contribution
   - method
   - results
   - limitations
   - relevance to user’s active project

Do not dump full markdown unless explicitly requested.
Do not switch to arXiv HTML/abs links as the default fallback when the request was specifically for Paperzilla markdown.

### 7) Feedback loop on request

If the user wants to tune future recommendations:
1. Use `pz feedback ...` on the recommendation ID.
2. Explain that feedback is project-specific.
3. Use:
   - `upvote` for positive signal
   - `star` for strongest positive signal
   - `downvote --reason not_relevant` for topical mismatch
   - `downvote --reason low_quality` for weak paper quality
   - `feedback clear` to remove prior signal

## User-requested delivery

Use the `message` tool **only when the user explicitly asks** to deliver a digest/summary to another chat or channel.

When that happens:
- `action: "send"`
- `channel: "telegram"` (or the explicitly requested channel)
- `target`: destination chat id/name explicitly provided by the user or already unambiguously established in context
- `message`: formatted digest

If destination is ambiguous, confirm once before sending.
Do not send proactive nudges, automatic follow-ups, or unsolicited summaries under this skill.

Suggested format:
- Project name
- Number of papers checked
- 🟢 relevant bullets
- 🟡 tangential bullets
- 🔴 skipped count

If digest is delivered via `message` tool, respond with `NO_REPLY` in chat to avoid duplicate output.

## Communication style

- Be fast and operational.
- Skip unnecessary clarification when context is clear.
- Lead with results, then offer next actions:
  - deep-dive any paper
  - deliver a digest if the user explicitly asks
  - tighten/loosen relevance criteria
  - leave feedback on specific recommendations

## Edge Cases

- **No new papers:** verify project is active and report no fresh additions.
- **Large feeds:** increase `--limit`, use `--must-read`, or narrow scope.
- **Markdown delay:** poll/retry more than once when the user explicitly asked for markdown. Prefer a short polling loop over an immediate fallback to arXiv. If it still is not ready after several retries, report that it is still processing.
- **External delivery requests:** if the user did not explicitly ask for delivery, do not use the `message` tool.
- **Canonical vs recommendation confusion:** if an ID came from `pz feed --json`, assume it is a recommendation ID unless shown otherwise.
