---
name: ntriq-eu-sanctions-monitor
description: "Free API for EU sanctions screening and compliance. No subscription required. Screen names and entities against EU consolidated sanctions list. Government data, pay-per-use."
version: 1.0.0
metadata:
  openclaw:
    primaryTag: data-intelligence
    tags: [compliance,sanctions]
    author: ntriq
    homepage: https://x402.ntriq.co.kr
---

# EU Sanctions Monitor

Free EU sanctions screening API. Screen names and entities against the EU consolidated sanctions list — covering 36+ countries and regimes including Russia, Belarus, Iran, and Myanmar. No subscription required.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `names` | array | ✅ | Entity names to screen (individuals, companies, vessels) |
| `fuzzy_match` | boolean | ❌ | Enable fuzzy name matching (default: true) |
| `match_threshold` | float | ❌ | Similarity threshold 0.0–1.0 (default: 0.85) |
| `entity_type` | string | ❌ | `person`, `organization`, `vessel`, `aircraft` |

## Example Response

```json
{
  "screened": "Sergei Ivanov Trading LLC",
  "matches": [
    {
      "sanctioned_name": "Sergey Ivanov Trading House",
      "match_score": 0.89,
      "list": "EU Consolidated Sanctions List",
      "regime": "Russia",
      "designation_date": "2022-03-15",
      "entity_type": "organization",
      "regulation": "EU Regulation 269/2014"
    }
  ],
  "recommendation": "REVIEW — potential match requires manual verification"
}
```

## Use Cases

- EU bank AML/KYC sanctions screening workflow
- Trade finance entity pre-screening
- Cross-border M&A counterparty due diligence

## Access

```bash
# Service catalog
curl https://x402.ntriq.co.kr/services
```

Available on [Apify Store](https://apify.com/ntriqpro/eu-sanctions-monitor) · [x402 micropayments](https://x402.ntriq.co.kr)
