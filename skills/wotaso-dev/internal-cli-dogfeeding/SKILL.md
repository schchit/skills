---
name: internal-cli-dogfeeding
description: Internal maintainer playbook for AnalyticsCLI CLI dogfeeding telemetry in this monorepo. Not tenant-facing.
license: MIT
---

# Internal CLI Dogfeeding

## Scope

- This skill is for monorepo maintainers only.
- This is not part of tenant-facing setup or public onboarding.
- Goal: observe internal CLI usage quality (command start/success/failure, parse failures) without requiring collector write keys on user machines.

## Use Case

- Maintainers install and use `@analyticscli/cli` locally.
- CLI telemetry is opt-in via:
  - `ANALYTICSCLI_SELF_TRACKING_ENABLED=true`
- CLI sends telemetry to API route:
  - `POST /v1/telemetry/cli`
- Authentication uses the existing CLI bearer token (same auth flow as normal CLI commands).
- Tenant/project attribution is resolved server-side from token scope.

## Guardrails

- Only internal dogfeeding tenants are accepted server-side.
- Allowlist source:
  - `BILLING_BYPASS_TENANT_IDS`
- If tenant is not allowlisted, telemetry is accepted as no-op (`accepted: false`) and not persisted.

## Data Model

- Telemetry events are stored in ClickHouse `events_raw`.
- Event names emitted by CLI:
  - `cli:command_started`
  - `cli:command_succeeded`
  - `cli:command_failed`
  - `cli:parse_failed`
- `projectSurface` remains `cli` semantics via event naming and props.

## Activation Checklist (Internal)

1. Set `ANALYTICSCLI_SELF_TRACKING_ENABLED=true` in maintainer runtime env.
2. Ensure the maintainer tenant ID is listed in API env `BILLING_BYPASS_TENANT_IDS`.
3. Log in with CLI (`analyticscli setup` or `analyticscli login`) so bearer token is available.
4. Execute CLI commands and verify events via dashboard/queries for the internal project.

## Non-Goals

- Do not require tenants to configure telemetry env variables.
- Do not expose this as public tenant integration guidance.
- Do not require `ANALYTICSCLI_SELF_TRACKING_API_KEY` for the standard internal flow.
