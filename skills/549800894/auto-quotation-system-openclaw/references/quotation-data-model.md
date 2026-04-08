# Quotation Data Model

## Purpose

Use this reference when turning a markdown requirement outline or a transcribed mind map into a structured quotation package.

## Input Contract

Normalize every request into this shape before pricing:

```json
{
  "project_name": "string",
  "delivery_channels": ["miniapp", "app", "web", "backend"],
  "business_goal": "string",
  "features": [
    {
      "module": "string",
      "feature": "string",
      "notes": "string",
      "dependencies": ["payment", "ocr", "erp"]
    }
  ],
  "non_functional": {
    "deployment": "cloud/private/on-premise",
    "security": [],
    "performance": [],
    "maintenance_months": 12
  },
  "assumptions": []
}
```

## Output Contract

Generate both a human-readable quote document and a machine-friendly JSON payload.

### Human-readable sections

1. Project summary
2. Scope and assumptions
3. Module-level quotation detail
4. Role-based effort summary
5. Delivery plan and payment milestones
6. Exclusions and change-control rules
7. Similar historical cases
8. Open questions

### JSON fields

```json
{
  "project_name": "string",
  "feature_count": 0,
  "features": [],
  "line_items": [],
  "roles": [],
  "payment_schedule": [],
  "similar_documents": [],
  "total_price": 0,
  "assumptions": []
}
```

## Pricing Heuristics

- Prefer module-level estimation over one-line total-price guesses.
- Separate development cost from hardware, cloud resources, SMS, OCR, and model token fees.
- When the requirement is ambiguous, keep the line item but add an assumption or a pending question.
- When the request mentions AI, OCR, hardware, ERP, or multi-end delivery, increase effort and explicitly call out integration risk.
- When a historical quotation is only broadly similar, use it as a calibration reference rather than copying totals.
