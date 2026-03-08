# Metrics Reference (v3)

- **ATM IV (front expiry)**: average of call/put mark IV nearest to 50-delta.
- **RR(25d)**: IV(call 25d) - IV(put 25d). More negative = stronger downside skew.
- **RR(15d)**: IV(call 15d) - IV(put 15d). Faster panic sensitivity.
- **Put/Call OI ratio**: front expiry put OI / call OI.
- **Put buy share proxy**: put option 24h USD volume / total (put+call) USD volume.
- **Deribit funding/basis**: perpetual carry + perp/index dislocation.
- **Cross-exchange spot dispersion (bp)**: max-min spot spread across available venues.
- **Funding regime**: aggregated sign ratio across Deribit/OKX/Bybit funding snapshots.

## Risk Label Heuristic

### Normal mode
- RED: score >= 6
- AMBER: score 3-5
- GREEN: score <= 2

### High-alert mode (event-sensitive)
- RED: score >= 5
- AMBER: score 2-4
- GREEN: score <= 1

## 72h Validation Matrix

Track 5 checks for next 72h:
1. Options skew panic
2. Vol regime hot
3. Flow put dominance
4. Funding bearish confirm
5. Liquidity stress

Action map:
- fired >= 4: DEFENSIVE
- fired 2-3: CAUTIOUS
- fired <= 1: PROBING

## Action Triggers

- `de_risk_triggers`: conditions that suggest reducing risk / hedging
- `re_risk_triggers`: conditions that suggest gradual re-risking

## Audience Modes

- `pro`: terse, trading-oriented output
- `beginner`: plain-language explanation of each key metric and what it means

## Confidence

Confidence score (0-100) is based on:
- Data availability (options + cross-venue sources)
- Signal agreement (how many bearish signals align)

This is a risk-state framework, not trading advice.
