---
name: ntriq-drug-safety-intelligence
description: "Free drug safety API combining FDA adverse events, recalls, clinical trials, and PubMed research trends. No subscription or API key required. Get complete medication safety profiles for pharmacovig..."
version: 1.0.0
metadata:
  openclaw:
    primaryTag: data-intelligence
    tags: [healthcare,fda]
    author: ntriq
    homepage: https://x402.ntriq.co.kr
---

# Drug Safety Intelligence

Complete medication safety profiles from FDA adverse events (FAERS), drug recalls, clinical trials, and PubMed research trends — all in one API call. No subscription or API key required. Free government data.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `drug_name` | string | ✅ | Generic or brand name (e.g., `metformin`, `Ozempic`) |
| `sources` | array | ❌ | `faers`, `recalls`, `trials`, `pubmed` (default: all) |
| `date_range_years` | integer | ❌ | Historical window (default: 5) |
| `serious_only` | boolean | ❌ | Filter to serious adverse events (default: false) |

## Example Response

```json
{
  "drug": "semaglutide",
  "brand_names": ["Ozempic", "Wegovy", "Rybelsus"],
  "faers_reports_5yr": 48234,
  "top_adverse_events": [
    {"event": "nausea", "count": 12841, "seriousness": "non-serious"},
    {"event": "pancreatitis", "count": 423, "seriousness": "serious"}
  ],
  "active_recalls": 0,
  "active_trials": 47,
  "pubmed_publications_1yr": 1842
}
```

## Use Cases

- Pharmacovigilance signal detection for drug manufacturers
- Clinical trial competitive landscape analysis
- Hospital formulary safety review automation

## Access

```bash
# Service catalog
curl https://x402.ntriq.co.kr/services
```

Available on [Apify Store](https://apify.com/ntriqpro/drug-safety-intelligence) · [x402 micropayments](https://x402.ntriq.co.kr)
