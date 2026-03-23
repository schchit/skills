---
name: drip-billing
description: Usage-based billing for OpenClaw and ClawHub agents with Drip run, event, and usage telemetry. Use when you need request-level traceability, OpenClaw identity endpoints, or public SDK examples for Node.js and Python.
license: MIT
compatibility: Requires either OpenClaw identity auth or DRIP API credentials. SDK support is available for Node.js 18+ (`@drip-sdk/node`) and Python 3.9+ (`drip-sdk`).
credentials:
  primary: X-OpenClaw-Identity
  alternate: DRIP_API_KEY
requiredEnvVars:
  - name: OPENCLAW_IDENTITY_TOKEN
    description: Required when using `/openclaw/*` identity endpoints.
    required: false
  - name: DRIP_API_KEY
    description: Required when using `/v1/*` core Drip API endpoints.
    required: false
  - name: DRIP_BASE_URL
    description: Optional trusted Drip API host for telemetry emission.
    required: false
  - name: DRIP_WORKFLOW_ID
    description: Workflow ID used for run lifecycle telemetry on the core API path.
    required: false
  - name: OPENCLAW_DEFAULT_CUSTOMER_ID
    description: Fallback customer or tenant identifier when a request omits customerId.
    required: false
  - name: OPENCLAW_TELEMETRY_FAIL_OPEN
    description: Continue execution when Drip telemetry writes fail.
    required: false
  - name: OPENCLAW_BILL_SKILL_CALLS
    description: Emit `/v1/usage` for skill calls in addition to `/v1/events`.
    required: false
metadata:
  author: drip
  version: "1.0.9"
---

# Drip OpenClaw Billing

Use this skill when OpenClaw or ClawHub handles a request and you need usage tracking, run timelines, or billable usage attribution in Drip.

Get API keys, dashboard access, and product details at `https://drippay.dev`.

## Choose an integration path

1. Use `X-OpenClaw-Identity` with `/openclaw/*` for lightweight, auto-provisioned metering.
2. Use `DRIP_API_KEY` with `/v1/*` for full billing, runs, events, and usage writes.

## Safety contract

- Use `pk_` keys by default for runtime integrations. Reserve `sk_` keys for trusted admin flows.
- Send sanitized operational metadata only.
- Never send raw prompts, raw outputs, request or response bodies, credentials, or PII.
- Prefer hashed identifiers like `queryHash` over raw user content.
- Emit stable idempotency keys for retries.

## SDKs

### Node.js

Install: `npm install @drip-sdk/node`

For the OpenClaw wrapper flow, use `OpenClawBilling` from `@drip-sdk/node/openclaw` or `OpenClawDripMiddleware` from `@drip/openclaw/middleware` when you are inside the package integration.

```typescript
import { OpenClawBilling } from '@drip-sdk/node/openclaw';

const billing = new OpenClawBilling({
  apiKey: process.env.DRIP_API_KEY,
  customerId: 'cus_123',
  workflowId: process.env.DRIP_WORKFLOW_ID ?? 'wf_openclaw',
});
```

### Python

Install: `pip install drip-sdk`

Use the public Python SDK when you need the same run, event, and usage lifecycle from Python.

```python
import os
from drip import Drip

client = Drip(api_key=os.environ["DRIP_API_KEY"])

run = client.start_run(
    customer_id="cus_123",
    workflow_id=os.environ["DRIP_WORKFLOW_ID"],
    external_run_id="openclaw_req_456",
)
```

## Reference loading

Read [references/API.md](references/API.md) when you need:

- OpenClaw identity endpoint auth and payload shapes
- Core Drip API run, event, and usage flow
- Node.js and Python examples
- Pricing, rate limits, and outcome semantics
