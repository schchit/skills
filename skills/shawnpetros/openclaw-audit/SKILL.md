---
name: openclaw-audit
description: "Audit an OpenClaw installation against 12 production primitives using local configuration and workspace files. Use for read-only OpenClaw config reviews, hardening checks, cost-control reviews, heartbeat/runbook audits, and migration readiness checks. Default to an offline audit from local files only."
metadata:
  openclaw:
    requires:
      bins: ["openclaw"]
---

# OpenClaw Config Audit

Audit an OpenClaw installation against 12 production primitives.

## Safety

This skill is read-only. It:
- does not modify files or configuration
- does not install or remove anything
- does not reveal secrets in output
- defaults to local file inspection only

Treat `~/.openclaw/openclaw.json`, secrets providers, and any CLI output as sensitive.
Redact tokens, API keys, passwords, auth headers, cookies, webhook secrets, gateway tokens, and long opaque identifiers as `[REDACTED]`.
Do not quote raw secret values, even partially.

## Runtime assumptions

- Primary path: inspect local files only, no network required.
- Do not run `openclaw` CLI commands during the default audit flow.
- If the user explicitly asks for live runtime verification, state that the `openclaw` CLI is required and that some status or probe commands may contact the local gateway or configured services.
- If you perform any optional live checks, label them separately as `Live runtime checks`, describe the exact command used, and note that results may differ from the offline config audit.

## When to use
- after initial setup or onboarding
- after major config changes
- before machine migration
- when costs or behavior feel off but you cannot pinpoint why
- periodic health check (monthly recommended)

## Default process

1. Read the user's `~/.openclaw/openclaw.json` and redact sensitive values in your output.
2. Read `~/.openclaw/workspace/AGENTS.md` if it exists.
3. Read `~/.openclaw/workspace/HEARTBEAT.md` if it exists.
4. Optionally inspect local workspace structure relevant to operations, for example `skills/`, `memory/`, or hook directories.
5. Assess against each of the 12 primitives below using local evidence only.
6. Return findings ranked by severity (critical > warning > info).
7. Include specific fix recommendations with config snippets for each finding.

## Optional live runtime checks

Only perform these if the user explicitly asks for runtime validation in addition to the offline audit.
Before running them, say that they require the `openclaw` CLI and may contact the local gateway or configured services.

Examples:
- `openclaw gateway status`
- `openclaw status`
- `openclaw channels status --probe`

## The 12 Production Primitives

### Tier 1: Day One Non-Negotiables

#### 1. Secrets Hygiene
- Are API keys, tokens, and passwords stored via secrets provider (file/env), NOT inline?
- Is `logging.redactSensitive` set to `"tools"` or `"all"`?
- Are file permissions locked down (config 600, directory 700)?

#### 2. Permission System (Tiered Trust)
- Are DM policies set to `pairing` or `allowlist` (never `open` without good reason)?
- Are group policies gated with `requireMention`?
- Are destructive operations gated?

#### 3. Session Persistence & Isolation
- Is `session.dmScope` set to `per-channel-peer` or stricter?
- Is compaction configured with appropriate mode?
- Is context pruning configured with reasonable TTL?

#### 4. Model Fallback Chain
- Are fallback models configured?
- Is the primary model appropriate (not burning Opus on routine work)?
- Are heartbeats using a cheap model?
- Are model aliases defined for usability?

#### 5. Token Budget & Cost Control
- Is there a `maxConcurrent` limit on agents?
- Is there a `subagents.maxConcurrent` limit?
- Are heartbeats gated on budget in HEARTBEAT.md?
- Is compaction threshold configured (`softThresholdTokens`)?

#### 6. Memory Durability
- Is `memoryFlush` enabled in compaction settings?
- Is there a memory search provider configured?
- Are significant events captured before context is lost?

#### 7. Gateway Hardening
- Is gateway bound to `loopback` (not `0.0.0.0`)?
- Is auth token set via secrets provider?
- Is Tailscale configured appropriately if remote access is needed?

#### 8. Streaming & Responsiveness
- Is streaming configured for channels that support it?
- Are partial responses enabled where appropriate?

### Tier 2: Operational Maturity

#### 9. Agent Type System
- Are different agent roles defined (main, monitor, researcher, etc.)?
- Do agents have role-appropriate models and permissions?
- Are sub-agents properly scoped?

#### 10. Transcript Compaction
- Is compaction mode configured (`safeguard` or `default`)?
- Is the threshold appropriate for the use case?
- Is a cheap model used for compaction?

#### 11. Hook & Plugin Hygiene
- Are hooks enabled for session memory, boot, and command logging?
- Are plugins explicitly allowlisted (not open)?
- Are channel-specific plugins only enabled where needed?

#### 12. Operational Runbook
- Does AGENTS.md exist with clear operating instructions?
- Does HEARTBEAT.md exist with structured checks?
- Is there a workspace structure (memory/, skills/, etc.)?

## Output Format

Return findings as a structured list:

```
## Audit Results for [hostname/identifier]

### Critical
- [finding]: [explanation]. Fix: [specific config snippet]

### Warning  
- [finding]: [explanation]. Fix: [specific config snippet]

### Info
- [finding]: [explanation]. Suggestion: [improvement]

### Score: X/12 primitives satisfied
### Overall: [PRODUCTION-READY | NEEDS-WORK | CRITICAL-GAPS]
```

## Attribution
Built by PennywiseOps (pennywiseops.com)
Free config audits available — reach out at penny@pennywiseops.com
