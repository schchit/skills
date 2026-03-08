---
name: btc-risk-radar
description: Analyze Bitcoin market risk with public derivatives and spot data (Deribit options/perp + Binance spot). Use when the user asks for BTC risk assessment, panic/black-swan validation, options skew/IV interpretation, or a structured long/short risk snapshot with timestamped evidence.
---

# BTC Risk Radar

Generate a verifiable BTC risk snapshot from public data, then produce a concise analyst conclusion.

## Workflow

1. Run `scripts/btc_risk_radar.py` to collect current data and compute metrics.
2. Read JSON output first; treat it as the source of truth.
3. Explain conclusions with explicit confidence and caveats.
4. Avoid deterministic predictions; present risk state (GREEN/AMBER/RED) and trigger reasons.

## Commands

```bash
python3 skills/btc-risk-radar/scripts/btc_risk_radar.py --json
python3 skills/btc-risk-radar/scripts/btc_risk_radar.py --prompt "用户问题"
python3 skills/btc-risk-radar/scripts/btc_risk_radar.py --lang en
python3 skills/btc-risk-radar/scripts/btc_risk_radar.py --lang zh
python3 skills/btc-risk-radar/scripts/btc_risk_radar.py --horizon-hours 72
python3 skills/btc-risk-radar/scripts/btc_risk_radar.py --event-mode high-alert
python3 skills/btc-risk-radar/scripts/btc_risk_radar.py --audience beginner --lang zh
```

## Output Policy

- Default response language: English.
- If user asks in Chinese (or prompt contains Chinese), switch final answer to Chinese.
- Internal reasoning/analysis can stay English.
- Always include:
  - `as_of_utc`
  - key metrics (ATM IV, RR25, RR15, put-volume proxy, funding, basis)
  - 72h validation matrix (`validation_72h`)
  - confidence (`confidence.score`, `confidence.level`)
  - action trigger set (`action_triggers`)
  - data-source note and caveats
- Audience modes:
  - `pro` (default): concise trading/risk language
  - `beginner`: plain-language educational explanation with metric interpretation
- Event modes:
  - `normal` (default)
  - `high-alert` (more sensitive thresholds for macro/event windows)

## Interpretation Guardrails

- `put_buy_share_proxy` is a **proxy** from put/call volume split, not true aggressor signed-flow.
- RR and ATM IV are computed from front expiry delta-nearest options; this is robust but may differ from proprietary dashboards.
- RED means elevated downside risk pricing, not guaranteed crash.

## Data Sources (public)

- Deribit Public API
  - `/public/get_instruments`
  - `/public/get_order_book`
  - `/public/get_book_summary_by_currency`
  - `/public/get_index_price`
  - `/public/get_book_summary_by_instrument`
- Coinbase Public API
  - `/v2/prices/BTC-USD/spot`
- Binance Public API (optional)
  - `/api/v3/ticker/price`
- OKX Public API
  - `/api/v5/market/ticker`
  - `/api/v5/public/funding-rate`
- Bybit Public API
  - `/v5/market/tickers`
