---
name: gougoubi-create-condition
description: Create Gougoubi proposal conditions from minimal input (proposalId + conditionName) with deterministic defaults for deadline/tradeDeadline, validation, and transaction submission. Use when users ask to create a condition for an existing proposal on Gougoubi.
metadata: {"clawdbot":{"emoji":"🧩","os":["darwin","linux","win32"]}}
---

# Gougoubi Create Condition

Create a new condition for an existing Gougoubi proposal from structured input.

## Run Conditions

- Agent runtime must be configured with a usable BNB chain wallet address.
- Wallet must be connected before submitting any on-chain transaction.

## Minimal Input (User Only)

```json
{
  "proposalId": "0x... or proposal identifier",
  "conditionName": "Will Team A win the match?"
}
```

## Proposal And Date Defaults

The skill must follow create-condition dialog default policy:

- Resolve `proposalId` to proposal contract address (`proposalAddress`) and fetch proposal detail.
- `deadlineDateTime` default: proposal deadline (`proposalDeadline`) in UTC ISO.
- `deadlineTimezone` default: user's local IANA timezone; fallback `UTC`.
- `tradeDeadlineDateTime` default: `deadlineDateTime - 1 hour` (general policy).
- `tradeDeadlineTimezone` default: same as `deadlineTimezone`.

Default safety clamp:

- `deadlineDateTime` must be greater than now.
- `tradeDeadlineDateTime` must be greater than now and not later than `deadlineDateTime`.
- If `deadlineDateTime - 1 hour` is not valid, set trade deadline to the nearest valid value that keeps `tradeDeadlineDateTime <= deadlineDateTime` (typically equal to `deadlineDateTime` when close to now).

## Agent Auto-Fills

The skill auto-fills non-required fields:

- `conditionImageUrl`: empty string by default
- `conditionRules`: empty string by default
- `skills`: empty string by default
- `isNormalized`: `true` by default

## Deterministic Steps

1. Validate minimal input (`proposalId`, `conditionName`).
2. Resolve `proposalAddress` from `proposalId`.
3. Load proposal detail and derive default condition deadline from proposal deadline.
4. Set timezone defaults (local timezone, fallback `UTC`).
5. Set trade deadline default to condition deadline minus 1 hour, then clamp to valid range.
6. Convert `deadlineDateTime` and `tradeDeadlineDateTime` to unix seconds.
7. Validate:
   - `conditionName` non-empty
   - `deadline > now`
   - `tradeDeadline > now`
   - `tradeDeadline <= deadline`
8. Ensure wallet is connected.
9. Submit contract call in canonical order:
   1) `conditionName`
   2) `deadline`
   3) `tradeDeadline`
   4) `conditionImageUrl`
   5) `conditionRules`
   6) `skills`
   7) `isNormalized`
10. Wait transaction confirmation.
11. Return normalized result.

## Output

```json
{
  "ok": true,
  "mode": "browser|contract",
  "txHash": "0x...",
  "proposalAddress": "0x...",
  "normalizedInput": {
    "proposalId": "",
    "proposalAddress": "",
    "conditionName": "",
    "deadlineDateTime": "",
    "deadlineTimezone": "",
    "tradeDeadlineDateTime": "",
    "tradeDeadlineTimezone": "",
    "defaultsApplied": true,
    "tradeDeadlinePolicy": "deadline-minus-1h-with-valid-clamp"
  },
  "warnings": []
}
```

Failure shape:

```json
{
  "ok": false,
  "stage": "validation|resolve-proposal|create|confirm",
  "error": "reason",
  "retryable": true
}
```

## Boundaries

- Do not use private credentials or private hosts.
- Do not auto-accept wallet signatures.
- Do not bypass user confirmation for irreversible on-chain actions.
