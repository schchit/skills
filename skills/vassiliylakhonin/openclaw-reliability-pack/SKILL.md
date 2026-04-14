---
name: openclaw-reliability-pack
description: Unified reliability triage for OpenClaw incidents from first symptom to ship/rollback decision. Use for channel failures, gateway/runtime instability, cron/session issues, and post-change regression risk with command-first routing and explicit go/no-go outcomes.
user-invocable: true
metadata: {"openclaw":{"emoji":"🛡️","os":["linux","darwin","win32"]}}
---

# OpenClaw Reliability Pack

Single entrypoint for OpenClaw reliability triage.

## Best for

- No-reply/channel routing incidents
- Gateway/runtime instability and tool hangs
- Pre-release or post-change regression decisions

## Not for

- Feature implementation unrelated to reliability
- Broad refactors before baseline diagnosis
- Silent fixes without evidence and verification gate

## 60-second preflight

Before routing, capture:
- primary symptom,
- blast radius (who/what affected),
- when issue started,
- last change before failure,
- current severity (`low/medium/high`).

## Router

Pick one path first, then execute it fully.

### Path A: Channel issues

Use for:
- no replies
- listener/startup errors
- reply/quote/mention rendering breaks
- thread/topic misrouting
- duplicate sends

Run: `openclaw-channel-doctor`

### Path B: Core runtime issues

Use for:
- `openclaw status` unreachable
- missing `scope/operator.read`
- gateway closed 1000
- hanging tool calls
- cron misbehavior
- session wedges

Run: `openclaw-troubleshooter-pro`

### Path C: Change-risk validation

Use for:
- “safe to release?”
- “did this update regress quality?”
- “ship or rollback?”

Run: `agent-regression-guard`

## Standard reliability flow

1. Classify symptom (A/B/C).
2. Run read-only baseline checks first.
3. Apply smallest safe fix.
4. Verify with explicit gate.
5. Return one status:
   - `resolved`
   - `mitigated`
   - `blocked`
   - `rollback_recommended`

## Output contract

Always return:
- chosen path (A/B/C),
- commands run,
- key evidence,
- current risk level (low/medium/high),
- next action.

## Escalation rule

Escalate when any remain true:
- repeated failure after restart,
- critical path still broken,
- uncertain root cause after baseline checks.

Escalation payload must include:
- symptom,
- exact commands run,
- key logs/errors (redacted),
- top 2 suspected causes,
- next highest-signal test.

## Author

Vassiliy Lakhonin
