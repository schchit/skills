---
name: openclaw-skills-audit
version: 1.0.3
description: Security audit + append-only NDJSON logging + realtime monitoring for OpenClaw skills.
---

# Skills Audit (skills-audit)

A security-oriented skill to help you manage OpenClaw skills safely, with three core capabilities:

1) **Threat scanning** (static analysis)
2) **Append-only audit logs** (local NDJSON)
3) **Skills monitoring & notifications** (push alerts on changes)

This skill is designed to be **protocol-first**: it audits and records changes without executing skill code.

---

## Core Capabilities

### 1) Threat Scanning / Static Risk Analysis
When scanning an installed skill directory, `skills_audit.py` performs **static inspection** and generates a risk summary.

It focuses on three classes of signals:

- **Network indicators**: URLs/domains, `curl/wget/requests` usage hints
- **Dangerous command indicators**: `curl|sh`, `wget|bash`, `eval`, dynamic exec, base64 decode pipelines
- **Suspicious file indicators**: persistence hooks (cron/systemd), sensitive paths (`~/.ssh`, `~/.aws`, `/etc/...`)

Output fields:
- `risk.level`: `low | medium | high | extreme`
- `risk.decision`: `allow | allow_with_caution | require_sandbox | deny`
- `risk.risk_signals[]`: evidence entries (file + snippet)
- `risk.network.domains[]`: domains extracted from text files

> Note: this is **static analysis only**. It never executes the skill code.

### 2) Audit Logging (Append-only)
All detections are written as **one JSON object per line (NDJSON)** and appended to:

- `~/.openclaw/skills-audit/logs.ndjson`

A small snapshot file is also maintained for diffing:

- `~/.openclaw/skills-audit/state.json`

The record schema is defined by:

- `skills-audit/log-template.json`

Key design points:
- **Append-only**: logs are never rewritten
- **Integrity hint**: `md5` (MD5 of the skill’s `SKILL.md` if present)
- **No extra sensitive fields**: `source` / `approval` are intentionally removed from the schema

### 3) Skills Realtime Monitoring & Push Notifications
For better UX, you can run a scheduled monitor that detects:

- Skill **新增/变更/删除** under `workspace/skills`

and pushes a message (e.g., to WeCom) only when changes are detected.

Components:
- `skills_watch_and_notify.py`: generates a human-friendly notification text
- `openclaw cron add / edit`: OpenClaw owns cron creation/update and delivery routing

Behavior:
- **No changes → no message**
- **Has changes → push one notification**

Notification style (fixed contract; do not collapse to a short summary):
- Every non-empty change notification must use a **fixed template**. It must not degrade into a risk-only summary or a one-line skill-only alert.
- The notification must preserve these fields in this order:
  1. Title: `【Skills 监控提醒】`
  2. Intro line: `检测到 skills 目录发生变更`
  3. Change sections: `【新增】` / `【变更】` / `【删除】` (show only non-empty sections)
  4. One line per skill: `• <slug>｜风险等级：<risk_label>`
  5. Path line: `📁 路径：<skills_dir>`
  6. Time line: `🕒 时间：<timestamp> (<timezone>)`
  7. Audit log line: `🧾 审计日志：<logs_path>`
- Items 1~7 are part of the fixed notification skeleton and **must not be omitted** due to model summarization, style rewriting, or channel compression.
- No changes -> no output.
- Risk levels use the fixed visual labels:
  - `🟢 低`
  - `🟢 中`
  - `🟡 高`
  - `🔴 极高`
  - `⚪ 未知`

Recommended fixed template example:

```text
【Skills 监控提醒】
检测到 skills 目录发生变更

【删除】
• weather｜风险等级：⚪ 未知

📁 路径：/root/.openclaw/workspace/skills
🕒 时间：2026-03-27 17:58:11 (Asia/Shanghai)
🧾 审计日志：/root/.openclaw/skills-audit/logs.ndjson
```

---

## How to Start (Enable skills-audit)

There is no daemon by default. You can start it in two ways.

### Recommended: start by chat (no commands)

Just tell the assistant in chat:

> “Start skills-audit. Monitor skills every minute and push changes back to this conversation.”

The preferred wording is **push back to this conversation** instead of naming a fixed channel such as WeCom.
That way the assistant should:

1. Initialize the local files required by `skills_audit.py`
2. Use `openclaw cron add` (or `openclaw cron edit` if the job already exists)
3. Route notifications back to the **current conversation**, with channel/recipient decided by OpenClaw from session context

Optional parameters:
- Schedule: `SCHEDULE="*/5 * * * *"`
- Timezone: `TZ=Asia/Shanghai`
- Log-only mode: “record logs only, do not push”
- Preview-only mode: “preview first, do not create yet”

> Design rule: `skills-audit` is responsible only for **scan / audit log / notification text generation**. Cron scheduling and delivery should be owned by **OpenClaw cron**.

### Manual: run commands

### Mode 1) Manual scan (recommended for first-time verification)

1. Initialize local files:

```bash
python3 skills/skills-audit/scripts/skills_audit.py init --workspace /root/.openclaw/workspace
```

2. Run a scan once:

```bash
python3 skills/skills-audit/scripts/skills_audit.py scan --workspace /root/.openclaw/workspace --who user --channel local
```

This will create/update:
- `~/.openclaw/skills-audit/logs.ndjson`
- `~/.openclaw/skills-audit/state.json`

### Mode 2) Background monitoring (recommended for production)

Use OpenClaw’s own cron system to create the scheduled job (every minute by default).

### C) Install monitoring cron (recommended)

Prefer creating/updating the job with `openclaw cron add` / `openclaw cron edit` instead of letting the skill write `jobs.json` directly.

Recommended design:
- **skills-audit does not directly own cron file writes**
- **OpenClaw cron owns scheduling**
- **Notifications should return to the current conversation** when delivery is enabled

For local verification, you can still run the notifier directly:

```bash
python3 skills/skills-audit/scripts/skills_watch_and_notify.py --workspace /root/.openclaw/workspace
```

---

## Files

- `skills/skills-audit/log-template.json` — NDJSON schema template
- `skills/skills-audit/scripts/skills_audit.py` — scanner + logger (logs.ndjson/state.json)
- `skills/skills-audit/scripts/skills_watch_and_notify.py` — notification text generator

---

## Safety Notes

- Static analysis only: never execute unknown skill code during audit.
- If `risk.level` is `high`/`extreme`, require explicit human review or sandbox.
- Prefer OpenClaw `cron add` / `cron edit` for scheduled jobs and delivery routing.
