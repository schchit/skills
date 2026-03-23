# Drip OpenClaw API Reference

## Contents

- Quick links
- Path 1: OpenClaw identity endpoints
- Path 2: Core Drip API
- SDK examples

## Quick Links

- Website: `https://drippay.dev`
- API host: `https://api.drippay.dev`
- Core API base: `https://api.drippay.dev/v1`

## Path 1: OpenClaw Identity Endpoints

These endpoints use your OpenClaw identity token for authentication. Drip auto-creates a customer record for the agent, so no separate signup is required for this path.

### Authentication

```http
X-OpenClaw-Identity: <your-openclaw-identity-token>
```

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/openclaw/estimate_cost` | POST | Estimate cost before execution |
| `/openclaw/track_usage` | POST | Record usage event |
| `/openclaw/record_run` | POST | Record complete agent run |
| `/openclaw/set_budget` | POST | Configure spending budget |
| `/openclaw/ledger` | GET | View usage ledger and recent runs |
| `/openclaw/charge` | POST | Settle on-chain (gated) |
| `/openclaw/skill.md` | GET | Public skill documentation |

### Estimate Cost

```http
POST /openclaw/estimate_cost

{
  "unit_type": "tokens",
  "quantity": 5000
}
```

### Track Usage

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `agent_id` | string | Yes | Your agent identifier |
| `unit_type` | string | Yes | Usage type like `tokens` or `api_calls` |
| `quantity` | number | Yes | Must be positive |
| `idempotency_key` | string | Yes | Prevents duplicate recording |
| `metadata` | object | No | Sanitized diagnostics only |

```http
POST /openclaw/track_usage
X-OpenClaw-Identity: <token>

{
  "agent_id": "my-agent",
  "unit_type": "tokens",
  "quantity": 5000,
  "idempotency_key": "req_unique_123",
  "metadata": { "model": "gpt-4" }
}
```

### Record Run

```http
POST /openclaw/record_run
X-OpenClaw-Identity: <token>

{
  "agent_id": "my-agent",
  "run_id": "run_456",
  "status": "completed",
  "duration_ms": 4500,
  "usage": [
    { "unit_type": "tokens", "quantity": 2500 },
    { "unit_type": "tool_calls", "quantity": 3 }
  ]
}
```

### Unit Pricing

| Unit Type | Price per Unit |
|-----------|----------------|
| `tokens` | $0.000002 |
| `api_calls` | $0.001 |
| `tool_calls` | $0.001 |
| `compute_seconds` | $0.005 |
| Custom types | $0.001 (default) |

### Rate Limits

- 100 requests per minute per agent
- Headers: `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Path 2: Core Drip API

Use the core Drip API when you need full billing features like runs, events, usage writes, charges, entitlements, and settlement.

### Authentication

```http
Authorization: Bearer <DRIP_API_KEY>
```

Use a `pk_live_...` key for runtime integrations. Only use `sk_live_...` when you need trusted admin operations like webhook or key management.

### Recommended Flow

1. Start a run with `POST /runs`
2. Emit an event for each tool or API call with `POST /events`
3. Emit billable usage with `POST /usage` or `POST /usage/async`
4. End the run with `PATCH /runs/:id`

### Run Start

```http
POST /runs

{
  "customerId": "cus_123",
  "workflowId": "wf_openclaw",
  "externalRunId": "openclaw_req_456",
  "metadata": { "integration": "openclaw" }
}
```

### Event Payload

```json
{
  "customerId": "cus_123",
  "runId": "run_abc",
  "actionName": "brave_search",
  "eventType": "TOOL_CALL",
  "outcome": "SUCCEEDED",
  "quantity": 1,
  "idempotencyKey": "openclaw_run_abc_brave_search_001",
  "metadata": {
    "provider": "brave",
    "endpoint": "/res/v1/web/search",
    "statusCode": 200,
    "latencyMs": 412,
    "queryHash": "9f9e2d..."
  }
}
```

### Usage Payload

```json
{
  "customerId": "cus_123",
  "usageType": "brave_api_calls",
  "quantity": 1,
  "idempotencyKey": "openclaw_run_abc_brave_search_001_usage",
  "metadata": {
    "runId": "run_abc",
    "provider": "brave",
    "statusCode": 200,
    "latencyMs": 412
  }
}
```

### Run End

```http
PATCH /runs/:id

{
  "status": "COMPLETED"
}
```

On failure:

```json
{
  "status": "FAILED",
  "errorMessage": "Provider timeout",
  "errorCode": "TOOL_TIMEOUT"
}
```

## SDK Examples

### Node.js (`@drip-sdk/node`)

```typescript
import { OpenClawBilling } from '@drip-sdk/node/openclaw';

const billing = new OpenClawBilling({
  apiKey: process.env.DRIP_API_KEY,
  customerId: 'cus_123',
  workflowId: process.env.DRIP_WORKFLOW_ID ?? 'wf_openclaw',
});

await billing.withRun(
  { externalRunId: 'openclaw_req_456' },
  async ({ runId }) => {
    await billing.withToolCall(
      { runId, provider: 'brave', endpoint: '/res/v1/web/search' },
      async () => fetch('https://api.search.brave.com/res/v1/web/search?q=...'),
    );
  },
);
```

Install: `npm install @drip-sdk/node`

### Python (`drip-sdk`)

```python
import os
from drip import Drip

client = Drip(api_key=os.environ["DRIP_API_KEY"])

run = client.start_run(
    customer_id="cus_123",
    workflow_id=os.environ["DRIP_WORKFLOW_ID"],
    external_run_id="openclaw_req_456",
)

client.emit_event(
    run_id=run.id,
    event_type="tool.call",
    quantity=1,
    metadata={"provider": "brave", "endpoint": "/res/v1/web/search"},
)

client.track_usage(
    customer_id="cus_123",
    meter="brave_api_calls",
    quantity=1,
    metadata={"runId": run.id},
)

client.end_run(run.id, status="COMPLETED")
```

Install: `pip install drip-sdk`

## Outcome

Both paths give you run timelines, spend attribution, charge ledger visibility, and anomaly detection in Drip analytics.
