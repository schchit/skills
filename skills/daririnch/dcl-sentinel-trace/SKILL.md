---
description: "Detects and redacts PII in AI outputs: emails, phones, SSNs, bank cards, IBANs, crypto addresses, IPs. Delivers cryptographic tamper-evident audit proofs. GDPR & HIPAA compliant privacy checkpoint for AI pipelines."
tags: [pii, redaction, privacy, gdpr, hipaa, compliance, data-protection, security, audit, sensitive-data, leibniz]
---

# dcl-sentinel-trace v1.0.0

**Sentinel Trace** is a compliance checkpoint for AI outputs that automatically detects and redacts personally identifiable and sensitive information using the **Leibniz Layer™** protocol.

### Key Features
- **Detection and redaction of**:
  - Email addresses
  - Phone numbers (international and US formats)
  - National ID and Social Security Numbers
  - Bank card PANs and IBANs
  - Cryptocurrency addresses (Bitcoin, Ethereum)
  - IP addresses
  - Passport and document numbers

- **Enterprise-grade security**:
  - Generates **cryptographically tamper-evident** audit proofs for every detection/block.
  - **Never stores or exposes** raw input data.

- **Simple API**:
  - `/evaluate` — analyze and redact text
  - `/health` — health check endpoint
  - `/chain/tail` — retrieve recent audit log entries

### Ideal for
Any AI pipeline that requires strong **privacy and regulatory compliance** (GDPR, HIPAA, etc.).  
Zero data retention, no third-party leakage — pure output protection.

### When to use this skill
Invoke Sentinel Trace whenever AI-generated output might contain personal data, financial identifiers, contact details, or any sensitive information that needs redaction for compliance or privacy reasons.

---

### How to use

```bash
curl -s -X POST https://webhook.fronesislabs.com/evaluate \
  -H "Content-Type: application/json" \
  -d '{"response": "<AI OUTPUT TO SCAN>", "policy": "sentinel_trace"}'
```

### Example response

```json
{
  "verdict": "NO_COMMIT",
  "confidence": 0.0,
  "policy": "sentinel_trace",
  "violations": ["email", "phone_intl"],
  "sentinel_detections": [
    {"type": "email", "redacted_sample": "te****st@****.com", "position": 14},
    {"type": "phone_intl", "redacted_sample": "+1****67", "position": 103}
  ],
  "sentinel_count": 2,
  "tx_hash": "183305b58e0ac9b8f099...",
  "chain_hash": "a485a4b80cec19b35f5a...",
  "powered_by": "Leibniz Layer™ | Fronesis Labs"
}
```

### Verdicts
| Verdict | Meaning |
|---------|---------|
| `COMMIT` | No PII detected — output is clean |
| `NO_COMMIT` | PII detected — output blocked, interception recorded |

---

Powered by **Leibniz Layer™** | [Fronesis Labs](https://fronesislabs.com) · Source-Available · Patent Pending
