---
name: mova-churn-prediction
description: Analyze customer behavior signals to predict churn probability and route retention campaign decisions through a human approval gate via MOVA HITL. Trigger when the user asks to predict customer churn, requests a retention analysis, or wants to identify at-risk customers. Human sign-off is required before any targeted retention action is launched.
license: MIT-0
metadata: {"openclaw":{"plugin":{"name":"MOVA","installCmd":"openclaw plugins install openclaw-mova"},"dataSentToExternalServices":[{"service":"MOVA API (api.mova-lab.eu)","data":"segment ID, analysis period, customer behavior features, churn probability scores, model version, human decision, audit metadata"},{"service":"Customer events connector (read-only)","data":"customer activity signals (logins, transactions, support tickets, feature usage) for the specified segment and period"},{"service":"Churn model connector (read-only)","data":"customer feature vectors evaluated by churn prediction model"},{"service":"CRM connector (read-only)","data":"customer profile and segment metadata lookup"}]}}
---

> **Contract Skill** — A ready-to-use MOVA HITL workflow. Requires the `openclaw-mova` plugin.

# MOVA Churn Prediction

Run an AI churn risk assessment on your customer segment — get a ranked at-risk list with contributing factor breakdown, then route the retention campaign decision through a mandatory human approval gate with a full audit trail.

## What it does

1. **Behavior ingestion** — customer activity signals (logins, transactions, support tickets, feature usage) for the specified segment and period
2. **Churn model** — probability score per customer (0.0–1.0) with contributing factor breakdown
3. **High-risk list** — ranked list of at-risk customers above threshold with recommended retention actions
4. **Human gate** — customer success manager reviews the list and chooses: launch campaign / launch selective / defer / escalate
5. **Audit receipt** — input features, model version, prediction scores, and human approval are all logged

**Escalation rules enforced by policy:**
- GDPR check required before any customer is targeted — consent and legitimate interest must be confirmed
- Model version drift (> 90 days) → recommend review before launch
- Campaigns above budget threshold → escalate to VP required

## Requirements

**Plugin:** MOVA OpenClaw plugin must be installed in your OpenClaw workspace.

**Data flows:**
- Segment ID + period + threshold → `api.mova-lab.eu` (MOVA platform, EU-hosted)
- Customer activity data → events connector (read-only, no raw data stored by MOVA)
- Feature vectors → churn model connector (inference only, read-only)
- Customer profiles → CRM connector (read-only)
- Audit journal → MOVA R2 storage, signed
- No data sent to third parties beyond the above

## Demo

**Step 1 — Segment submitted: SEG-ENTERPRISE, 30 days, threshold 0.70**
![Step 1](screenshots/01-input.jpg)

**Step 2 — AI analysis: 300 at-risk customers, avg score 0.75, top signals and findings**
![Step 2](screenshots/02-analysis.jpg)

**Step 3 — Decision recorded: launch_selective top 10 by churn score + audit receipt**
![Step 3](screenshots/03-audit.jpg)

## Quick start

Say "run churn analysis for segment SEG-ENTERPRISE over the last 30 days":

```
segment_id: SEG-ENTERPRISE
period_days: 30
threshold: 0.70
requestor_id: EMP-0441
```

The agent fetches behavior signals, scores churn probability per customer, shows the ranked at-risk list with top contributing factors, then asks for your retention decision.

## Why contract execution matters

- **GDPR compliance built in** — policy enforces consent check before any customer is targeted, not left to the agent's discretion
- **Model version tracking** — the exact model version used for scoring is locked in the audit trail, enabling reproducibility audits
- **Immutable decision record** — when a customer asks "why did I receive this offer?" or an auditor asks "who approved this campaign?" — the answer is in the system
- **EU AI Act / GDPR Article 22 ready** — automated profiling for targeted campaigns requires documented human oversight

## What the user receives

| Output | Description |
|--------|-------------|
| Customers analyzed | Total in segment |
| At-risk count | Above threshold |
| Avg churn score | Average probability for at-risk group |
| Per-customer score | 0.0–1.0 churn probability |
| Top contributing factors | Feature breakdown (e.g. login drop, support volume) |
| Model version | Scoring model identifier and date |
| Recommended retention actions | Per-customer suggested action |
| Recommended decision | AI-suggested campaign choice |
| Decision options | launch_campaign / launch_selective / defer / escalate |
| Audit receipt ID | Permanent signed record of the campaign decision |
| Compact journal | Full event log: feature pull → scoring → human decision |

## When to trigger

Activate when the user:
- Asks to predict churn, run retention analysis, or identify at-risk customers
- Provides a segment ID or cohort with a date range
- Sets up a scheduled churn review (weekly / monthly)

**Before starting**, confirm: "Run churn analysis for segment [SEG-ID] — last [N] days?"

If segment ID or period is missing — ask once.

## Step 1 — Submit customer segment for analysis

Call tool `mova_hitl_start_churn` with:
- `segment_id`: customer segment or cohort identifier
- `period_days`: lookback period in days (e.g. 30)
- `threshold`: minimum churn probability to include in at-risk list (e.g. 0.70)
- `requestor_id`: employee ID of the requestor

## Step 2 — Show at-risk list and decision options

If `status = "waiting_human"` — show the churn summary and ask to choose:

```
Segment:           SEG-ID
Period:            N days
Customers at risk: COUNT  (above THRESHOLD)
Avg churn score:   AVG

Top at-risk customers:
[ID | Name | Score | Top factor]
Recommended action: ACTION ← RECOMMENDED
```

| Option | Description |
|---|---|
| `launch_campaign` | Launch retention campaign for all high-risk customers |
| `launch_selective` | Launch for top-N only (specify N in reason) |
| `defer` | Defer to next review cycle |
| `escalate` | Escalate to VP of Customer Success |

Call tool `mova_hitl_decide` with:
- `contract_id`: from the response above — this is `ctr-chn-xxxxxxxx`, NOT the segment ID
- `option`: chosen decision
- `reason`: manager reasoning

## Step 3 — Show audit receipt

Call tool `mova_hitl_audit` with `contract_id`.
Call tool `mova_hitl_audit_compact` with `contract_id` for the full signed scoring chain.

## Connect your real data systems

By default MOVA uses a sandbox mock. To route analysis against your live infrastructure, call `mova_list_connectors` with `keyword: "churn"`.

Relevant connectors:

| Connector ID | What it covers |
|---|---|
| `connector.analytics.customer_events_v1` | Customer activity event stream |
| `connector.ml.churn_model_v1` | Churn prediction model (inference endpoint) |
| `connector.crm.customer_lookup_v1` | Customer profile and segment metadata |

Call `mova_register_connector` with `connector_id`, `endpoint`, optional `auth_header` and `auth_value`.

## Rules

- NEVER make HTTP requests manually
- NEVER invent or simulate churn scores — if a tool call fails, show the exact error
- Use MOVA plugin tools directly — do NOT use exec or shell
- CONTRACT_ID is `ctr-chn-xxxxxxxx` from the mova_hitl_start_churn response — NOT the segment ID
