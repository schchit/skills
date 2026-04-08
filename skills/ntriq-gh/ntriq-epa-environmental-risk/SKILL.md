---
name: ntriq-epa-environmental-risk
description: "Free EPA environmental compliance API for facility due diligence and risk assessment. Get violation history, enforcement actions, penalties, and toxic chemical releases from EPA ECHO and TRI databa..."
version: 1.0.0
metadata:
  openclaw:
    primaryTag: data-intelligence
    tags: [risk,environment,safety]
    author: ntriq
    homepage: https://x402.ntriq.co.kr
---

# EPA Environmental Risk

Free EPA environmental compliance API for facility due diligence. Query violation history, enforcement actions, penalties, and toxic chemical releases from EPA ECHO and TRI databases. No subscription needed. Essential for real estate, M&A, and lending decisions.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `facility_name` | string | ❌ | Facility or company name to search |
| `registry_id` | string | ❌ | EPA ECHO registry ID for exact match |
| `state` | string | ❌ | US state code (e.g., `TX`, `CA`) |
| `zip_code` | string | ❌ | 5-digit ZIP for location-based search |

## Example Response

```json
{
  "facility": "Bayport Chemical Plant",
  "registry_id": "110000350174",
  "state": "TX",
  "violations_3yr": 7,
  "enforcement_actions": 2,
  "penalties_usd": 125000,
  "tri_releases_lbs": {
    "total": 48200,
    "top_chemical": {"name": "Benzene", "lbs": 12400}
  },
  "compliance_status": "Significant Violation"
}
```

## Use Cases

- Commercial real estate environmental due diligence
- Bank lending collateral environmental risk screening
- Investor ESG portfolio monitoring

## Access

```bash
# Service catalog
curl https://x402.ntriq.co.kr/services
```

Available on [Apify Store](https://apify.com/ntriqpro/epa-environmental-risk) · [x402 micropayments](https://x402.ntriq.co.kr)
