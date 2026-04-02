---
name: shared-memory-os
description: Shared memory governance for multi-agent OpenClaw workspaces — with tiered memory, heartbeat maintenance, review cycles, conflict handling, and controlled evolution.
---

# Shared Memory OS

Use this skill when a workspace wants **all current and future agents** to share one memory model instead of each agent improvising its own note style.

Shared Memory OS is not just another memory skill. It provides a shared memory governance layer for multi-agent OpenClaw workspaces, helping agents remember, review, and evolve shared context without creating fragmented parallel systems.

## Core model

Adopt this tiering:

- **HOT** → `MEMORY.md`
- **DAILY** → `memory/YYYY-MM-DD.md`
- **WARM** → `memory/`
  - `active-thread.md`
  - `current-state.md`
  - `recent-focus.md`
  - `trigger-map.md`
  - `success-patterns.md`
  - `default-behaviors.md`
  - `feedback-model.md`
  - `projects.md` + `projects/*.md`
  - `decisions.md`
  - `routines.md`
  - `people.md`
  - `prompts.md`
  - `inbox.md`
  - `pattern-candidates.md`
  - `intake-log.md`
  - `promotion-log.md`
  - `conflict-log.md`
  - `governance-dashboard.md`
  - `governance-guide.md`
  - `skill-release-state.md`
  - `evolution-log.md`
- **RESTRICTED** → `memory/`
  - `private-secrets.md`
- **CONTROL** → `memory/`
  - `index.md`
  - `rules.md`
  - `corrections.md`
  - `heartbeat-state.md`
  - `weekly-review.md`
  - `monthly-review.md`
  - `monthly-governance-review.md`
  - `archive/`

## Required workspace behavior

When attaching a new agent to the workspace:

1. Read `SOUL.md`
2. Read `USER.md`
3. Read today and yesterday daily files if present
4. In direct/private main sessions, also read `MEMORY.md`
5. Read `memory/active-thread.md` and `memory/current-state.md` before acting on an ongoing thread
6. Use `memory/index.md` only when routing help is needed
7. Do not read `memory/private-secrets.md` unless the task explicitly requires credentialed action or secret lookup

Do not load every memory file by default. Prefer HOT, then the smallest matching WARM file.

For onboarding details, read `references/onboarding-checklist.md`.
For operational navigation, read `references/governance-guide.md` and mirror it into `memory/governance-guide.md` if the workspace enables the full governance layer.

## Promotion rules

Promote information only when it is:
- Repeated
- Stable
- Likely to improve future collaboration
- Clearly more than one-off noise

Routing:
- Stable preference / long-lived context → `MEMORY.md`
- Current main thread / what “continue” should mean → `active-thread.md`
- Current front-of-mind state → `current-state.md`
- Recent 24-72h active topics → `recent-focus.md`
- High-frequency aliases / fuzzy references → `trigger-map.md`
- Proven good collaboration pattern → `success-patterns.md`
- Default behavior that should now be assumed → `default-behaviors.md`
- User evaluation / feedback model → `feedback-model.md`
- Multi-step ongoing work → `projects/*.md`
- Reasoned choice with tradeoff → `decisions.md`
- Reusable workflow → `routines.md`
- Explicit mistake or reusable lesson → `corrections.md`
- Pattern not yet validated → `pattern-candidates.md`
- Skill release / publish state → `skill-release-state.md`
- System-level learning / evolution record → `evolution-log.md`
- Secrets / tokens / passwords / keys that truly must be remembered → `private-secrets.md`
- Unsorted temporary capture → `inbox.md`

## Front-of-mind working memory

A human-like memory system does not just store facts; it keeps the right things near the front.

Use these files together:
- `active-thread.md` → current main line of work
- `current-state.md` → current high-priority facts
- `recent-focus.md` → what has been repeatedly active recently
- `trigger-map.md` → fuzzy phrase / alias → intended topic

These files exist to improve immediate context recall, not long-term archival depth.

## Success, defaults, and feedback

To evolve beyond pure error correction, keep three additional layers:
- `success-patterns.md` → what already works well
- `default-behaviors.md` → what the system should now do by default
- `feedback-model.md` → how the user is currently evaluating quality, usefulness, and trust

A system that wants to become more human-like must learn not only from mistakes, but also from successful interaction patterns and repeated user feedback.

## Restricted secrets layer

Use `memory/private-secrets.md` only for credentials or secret material that must be remembered for future automation.

Hard rules:
- Do not store secrets in HOT / DAILY / ordinary WARM / CONTROL files
- Never copy secrets into skill bundles, release notes, published artifacts, or public/shareable memory
- Do not read `private-secrets.md` by default during normal startup
- Read it only when the current task explicitly requires credential lookup or secret-backed action
- Never use restricted secrets in group/shared contexts unless the workspace owner clearly intends that use
- Prefer storing a short usage note with each secret: what it is for, where it is used, and when it was last verified

For a suggested structure, read `references/private-secrets-template.md`.

## Heartbeat integration

Use `HEARTBEAT.md` as the lightweight maintenance entrypoint.

On heartbeat:
1. Check `memory/heartbeat-state.md`
2. Review recent daily files
3. Review `inbox.md` only if needed
4. Promote / merge / compact only when there is real value
5. Optionally review newly added skills for intake classification
6. Check whether repeated errors, repeated success patterns, new aliases, or recent active themes should be upgraded
7. Otherwise respond with `HEARTBEAT_OK`

Heartbeat should maintain memory quietly, not create noise.

## Weekly and monthly maintenance

- Weekly: promote useful daily items into HOT/WARM/corrections
- Monthly: compress HOT, refine WARM, archive stale items
- Monthly governance: review whether the governance layer itself is growing coherently

Read these only when doing maintenance:
- `memory/weekly-review.md`
- `memory/monthly-review.md`
- `memory/monthly-governance-review.md`

For migration guidance, read `references/migration-playbook.md`.
For archive policy, read `references/archive-strategy.md`.
For new skill checks, read `references/skill-intake-protocol.md` and `references/new-skill-checklist.md`.
For learning from other skills, read `references/pattern-harvesting.md`.
For sync after changes, read `references/auto-sync-checklist.md`.

## Multi-agent safety

- `MEMORY.md` is private-main-session material unless the workspace explicitly decides otherwise
- Never expose personal memory in shared/group contexts
- Do not infer preferences from silence alone
- Treat `private-secrets.md` as a special-case restricted file, not a normal shared memory tier

## Skill publishing governance

When the workspace uses shared memory to manage local/custom skills, treat release state as governed memory rather than ad-hoc chat context.

Required rules:
- Distinguish clearly between local edits, local packaging, ClawHub published version, and current displayed registry state
- Do not assume local packaging means the newest changes are already published
- Before bumping any skill version, verify:
  1. which exact skill is being discussed
  2. what changed locally
  3. what version is already published
  4. whether a new version bump is actually justified
- If a user refers to “the skill changed yesterday”, identify the exact skill first before publishing anything else
- Store materially important release-state facts in stable memory, project notes, or a dedicated release-state record instead of relying only on transient session context

For publish-specific notes, read the relevant skill's `references/release-state.md` when present.

## Files to update when standardizing a workspace

Update:
- `AGENTS.md`
- `HEARTBEAT.md`
- `memory/README.md`
- `memory/index.md`
- existing memory files as needed

## Keep it lean

A good shared memory system is:
- Easy for a new agent to enter
- Hard to pollute with noise
- Structured enough for maintenance
- Small enough to load selectively
