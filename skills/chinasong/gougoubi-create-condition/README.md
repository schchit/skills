# Gougoubi Create Condition Skill

Reusable skill package for creating conditions under an existing Gougoubi proposal:

- Target: Gougoubi proposal detail create-condition flow
- Use case: AI agent browser automation or EVM contract path
- Goal: deterministic defaults and stable output from minimal input

## Prerequisite

- Configure and connect an available BNB chain wallet address in the agent runtime before using this skill.

## CLI install

Install from local repo clone:

```bash
bash scripts/install-gougoubi-create-condition-skill.sh
```

Install from GitHub (using Codex skill installer):

```bash
~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo <owner>/<repo> \
  --path skills/gougoubi-create-condition
```

After install, restart Codex/Cursor agent runtime to pick up the new skill.

## Required input (user)

```json
{
  "proposalId": "0x...",
  "conditionName": "Will Team A win the match?"
}
```

## What it standardizes

- Minimal input schema (`proposalId` + `conditionName`)
- Proposal resolution before create
- Deadline default from proposal deadline
- Trade deadline default to deadline minus 1 hour with valid clamp
- Canonical `createConditions(...)` argument order
- Normalized success/failure output shape
