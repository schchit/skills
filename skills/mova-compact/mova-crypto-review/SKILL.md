---
name: mova-crypto-review
description: Submit a crypto trade order for automated risk analysis and human-in-the-loop review via MOVA. Trigger when the user mentions a trade order, wallet address, token pair, or asks to review/approve a crypto trade. Mandatory human escalation for orders above $10,000 or leverage above 3x.
license: MIT-0
metadata: {"openclaw":{"plugin":{"name":"MOVA","installCmd":"openclaw plugins install openclaw-mova"},"dataSentToExternalServices":[{"service":"MOVA API (api.mova-lab.eu)","data":"trade ID, wallet address, chain, token pair, order size, leverage, AI analysis results, human decision, audit metadata"},{"service":"Market data connector (read-only)","data":"token pair for price and volatility lookup"},{"service":"Sanctions screening connector (read-only)","data":"wallet address screened against OFAC, EU, UN lists"}]}}
---

# MOVA Crypto Trade Review

Submit a crypto trade order to MOVA for automated risk analysis and a mandatory human decision gate — with a tamper-proof audit trail of every trading decision.

## What it does

1. **Risk analysis** — AI checks wallet sanctions screening (OFAC/EU/UN), wallet balance, portfolio concentration, and market volatility
2. **Risk snapshot** — scores the trade (0.0–1.0) and surfaces anomaly flags
3. **Human decision gate** — trader chooses: approve / reject / escalate to human trader
4. **Audit receipt** — every decision is signed, timestamped, and stored in an immutable compact journal

**Mandatory rules enforced by policy:**
- Orders ≥ $10,000 → mandatory human escalation, no exceptions
- Leverage > 3x → mandatory escalation
- Sanctions hit → immediate rejection

## Requirements

**Plugin:** MOVA OpenClaw plugin must be installed in your OpenClaw workspace.

**Data flows:**
- Trade details + wallet address → `api.mova-lab.eu` (MOVA platform, EU-hosted)
- Wallet address → sanctions screening (OFAC, EU, UN — read-only, no data stored)
- Token pair → market data connector (price and volatility — read-only)
- Audit journal → MOVA R2 storage, cryptographically signed
- No data is sent to third parties beyond the above

## Quick start

Say "review trade TRD-2026-0002: buy $25,000 BTC/USDT on ethereum":

```
https://raw.githubusercontent.com/mova-compact/mova-bridge/main/test_trade_TRD-2026-0002.png
```

## Demo

**Step 1 — Task submitted with trade document (RISK GATE REQUIRED)**
![Step 1](screenshots/01-input.jpg)

**Step 2 — AI analysis: risk 0.62, sanctions clean, large_order_size flag, escalate_human recommended**
![Step 2](screenshots/02-analysis.jpg)

**Step 3 — Compact audit log with full event timeline**
![Step 3](screenshots/03-audit.jpg)

## Why contract execution matters

- **Policy is law, not a suggestion** — orders above $10,000 cannot be auto-approved regardless of risk score
- **Sanctions screening is mandatory** — every wallet is checked against OFAC, EU, and UN lists before any decision
- **Immutable audit trail** — when a compliance officer asks "who escalated trade TRD-2026-0002 and why?" — the answer is in the system
- **MiCA / EU AI Act ready** — high-value crypto transactions require human oversight and full explainability

## What the user receives

| Output | Description |
|--------|-------------|
| Risk score | 0.0 (clean) – 1.0 (critical) |
| Sanctions check | OFAC / EU / UN / PEP screening result |
| Balance check | Wallet balance, available margin |
| Portfolio concentration | Concentration %, risk level |
| Market volatility | 24h volatility score |
| Anomaly flags | large_order_size, high_leverage, sanctions_hit, etc. |
| Findings | Structured list with severity codes |
| Recommended action | AI-suggested decision |
| Decision options | approve / reject / escalate_human |
| Audit receipt ID | Permanent signed record of the trading decision |
| Compact journal | Full event log: analysis → sanctions → human decision |

## When to trigger

Activate when the user:
- Mentions a trade order ID (e.g. "TRD-2026-001")
- Provides a wallet address and token pair with trade details
- Says "review this trade", "check this order", "approve trade"

**Before starting**, confirm: "Submit trade [trade_id] for MOVA risk review?"

If details are missing — ask once for: trade ID, wallet address, chain, token pair, side (buy/sell), order size in USD, leverage.

## Step 1 — Submit trade order

Call tool `mova_hitl_start_trade` with:
- `trade_id`, `wallet_address`, `chain`, `token_pair`
- `side` (buy/sell), `order_type` (market/limit/stop)
- `order_size_usd`, `leverage`

## Step 2 — Show analysis and decision options

If `status = "waiting_human"` — show risk summary and ask to choose:

- **approve** — Approve trade
- **reject** — Reject trade
- **escalate_human** — Escalate to human trader

Show `recommended` option if present (mark ← RECOMMENDED).

Call tool `mova_hitl_decide` with:
- `contract_id`: from the response above (NOT the trade ID)
- `option`: chosen decision
- `reason`: human reasoning

## Step 3 — Show audit receipt

Call tool `mova_hitl_audit` with `contract_id`.
Call tool `mova_hitl_audit_compact` with `contract_id` for the full signed event chain.

## Connect your real market data and custody systems

By default MOVA uses a sandbox mock. To route checks against your live trading infrastructure, call `mova_list_connectors` with `keyword: "market"`.

Relevant connectors:

| Connector ID | What it covers |
|---|---|
| `connector.market.price_feed_v1` | Live spot price, volume, and volatility |
| `connector.wallet.balance_v1` | Wallet balance and open positions |
| `connector.market.portfolio_risk_v1` | Portfolio VaR, concentration, leverage |
| `connector.screening.pep_sanctions_v1` | Wallet sanctions screening (OFAC, EU, UN) |

Call `mova_register_connector` with `connector_id`, `endpoint`, optional `auth_header` and `auth_value`.

## Rules

- NEVER make HTTP requests manually
- NEVER invent or simulate results — if a tool call fails, show the exact error
- Use MOVA plugin tools directly — do NOT use exec or shell
- CONTRACT_ID comes from the mova_hitl_start_trade response, not from the trade ID
