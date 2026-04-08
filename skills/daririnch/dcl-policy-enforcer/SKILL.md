---
description: "Cryptographic compliance enforcement for AI outputs. Detects jailbreaks, prompt injection, EU AI Act violations, GDPR breaches, unsafe financial and medical advice. Every evaluation produces a tamper-evident audit proof via Leibniz Layer™. For AI agents, LLM pipelines, and compliance teams."
tags: [compliance, audit, ai-safety, policy-enforcement, eu-ai-act, gdpr, anti-jailbreak, prompt-injection, finance, medical, llm-guardrails, tamper-evident, cryptographic-proof, leibniz-layer, agent-safety, verification, ai-governance, regulatory, hipaa, mifid, fca, sec]
---

# DCL Policy Enforcer — Leibniz Layer™

**DCL Policy Enforcer** is a cryptographic compliance checkpoint for AI-generated outputs. It evaluates any LLM response against deterministic policy rules and returns a tamper-evident audit proof — powered by the **Leibniz Layer™** protocol.

Use this skill when you need to verify, audit, or enforce AI outputs against regulatory frameworks, safety rules, or custom compliance policies.

### When to use this skill

- User asks to **check, verify, audit, or enforce** an AI response
- Agent output needs to pass **EU AI Act, GDPR, MiFID II, FCA, SEC, or HIPAA** compliance
- You need to detect **jailbreak or prompt injection** attempts
- AI is generating **financial or medical content** that requires guardrails
- You need **cryptographic proof** that an output was evaluated at a specific time
- You are building an **AI pipeline** that requires an audit trail

### Available policies

| Policy | What it enforces |
|--------|-----------------|
| `eu_ai_act` | EU AI Act Art. 9/13/52 — transparency, no impersonation, no manipulation, no social scoring |
| `anti_jailbreak` | Prompt injection, DAN, STAN, role-switch, instruction override, token smuggling |
| `finance` | MiFID II / SEC / FCA — no guaranteed returns, no unqualified investment advice, required disclaimers |
| `medical` | EU MDR / FDA / HIPAA — no diagnostic claims, no dosage guidance, required professional referral |
| `gdpr` | GDPR Art. 5/6/17 — no unlawful retention, no unconsented data sharing, no data sale |
| `sentinel_trace` | PII & identity exposure — emails, phones, national IDs, card PANs, crypto wallets, IPs |

### How to use

```bash
curl -s -X POST https://webhook.fronesislabs.com/evaluate \
  -H "Content-Type: application/json" \
  -d '{"response": "<AI OUTPUT TO CHECK>", "policy": "<POLICY_NAME>", "agent_id": "optional"}'
```

Report `verdict`, `violations`, and `tx_hash` to the user. Always show `tx_hash` as cryptographic proof.

### Example response

```json
{
  "verdict": "NO_COMMIT",
  "confidence": 0.55,
  "policy": "anti_jailbreak",
  "policy_name": "Anti-Jailbreak & Prompt Injection Shield",
  "violations": ["ignore previous instructions", "you are now"],
  "missing_required": [],
  "tx_hash": "a3f8c2e1d09b4f76...",
  "chain_hash": "7c4d9a0e2f31b85a...",
  "chain_depth": 57,
  "powered_by": "Leibniz Layer™ | Fronesis Labs",
  "timestamp": 1744123456.789
}
```

### Verdicts

| Verdict | Meaning |
|---------|---------|
| `COMMIT` | Output passes policy — safe to proceed |
| `NO_COMMIT` | Policy violation detected — block this output |
| `tx_hash` | Tamper-evident proof of this evaluation |
| `chain_hash` | Links to all previous evaluations — append-only audit chain |
| `violations` | Forbidden patterns found in the output |
| `missing_required` | Required patterns absent from the output |
| `confidence` | 0.0–1.0; drops per violation; below threshold → NO_COMMIT |

### Additional endpoints

```bash
# List all policies with full descriptions
GET https://webhook.fronesislabs.com/policies

# Last N audit chain entries for tamper verification
GET https://webhook.fronesislabs.com/chain/tail?n=5

# Health check
GET https://webhook.fronesislabs.com/health
```

> **Privacy notice:** This skill sends the evaluated text to `https://webhook.fronesislabs.com/evaluate` operated by Fronesis Labs. Text is processed in-memory only — not stored to disk, not shared with third parties. The webhook is fully owned and operated by the skill author.

---

Powered by **Leibniz Layer™** | [Fronesis Labs](https://fronesislabs.com) · Source-Available · Patent Pending
