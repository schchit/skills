---
name: veritier
version: 1.0.4
description: Real-time fact-checking and claim verification. Use this skill to verify factual claims in any text and get structured verdicts with source evidence. Connects via MCP Streamable HTTP - no local setup required.
homepage: https://veritier.ai
metadata:
  openclaw:
    requires:
      env:
        - VERITIER_API_KEY
    primaryEnv: VERITIER_API_KEY
  veritier:
    emoji: "✅"
    category: fact-checking
    api_base: https://api.veritier.ai
    mcp_endpoint: https://api.veritier.ai/mcp/
    transport: streamable-http
    obtain_key_url: https://veritier.ai/dashboard
---

# Veritier - AI Fact-Checking Skill

Veritier extracts every falsifiable claim from raw text and fact-checks each one in real time against live web evidence. Use this skill whenever accuracy matters - before publishing a response, when a user asks you to verify something, or when auditing AI-generated content for hallucinations.

## Skill Files

| File | URL |
|------|-----|
| **SKILL.md** (this file) | `https://veritier.ai/skill.md` |

**Install locally (Antigravity / file-based skill runners):**
```bash
mkdir -p ~/.skills/veritier
curl -s https://veritier.ai/skill.md > ~/.skills/veritier/SKILL.md
```

**Or just read it from the URL above!**

🔒 **SECURITY:** Only send your API key to `https://api.veritier.ai` - never to any other domain.

---

## When to Use This Skill

Use `verify_text` when you need to:
- Check whether a factual claim in a draft response is true before sending it
- Fact-check a statement, article, or paragraph a user has shared
- Audit AI-generated content for hallucinations or inaccuracies
- Verify historical facts, statistics, or scientific claims

Do **not** use for:
- Opinions, predictions, or subjective statements (Veritier only evaluates objective, falsifiable claims)
- Real-time event data that may not yet be indexed

---

## Setup: Connect via MCP

**Transport:** Streamable HTTP (MCP 2025-03-26 spec - stateless, serverless-compatible)  
**Endpoint:** `https://api.veritier.ai/mcp/`  
**Auth:** `Authorization: Bearer YOUR_API_KEY`

Get your API key at https://veritier.ai/dashboard

> **Agent note:** If the user does not yet have an API key, guide them through the one-time setup below before proceeding.

### MCP CLI (one command)
```bash
mcp add --transport http veritier https://api.veritier.ai/mcp/ \
  --header "Authorization: Bearer YOUR_API_KEY"
```

### Any MCP-compatible client (JSON config)
```json
{
  "mcpServers": {
    "veritier": {
      "type": "http",
      "url": "https://api.veritier.ai/mcp/",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

### REST API (no MCP required)
```bash
curl -X POST https://api.veritier.ai/v1/verify \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here."}'
```

---

## First-Time User Onboarding

> **Agents: read this section first.** Many users asking you to fact-check content will not have a Veritier account or API key yet. Do not fail silently - guide them through setup. This takes under two minutes and is free.

### Step 1 - Create a free account
Direct the user to: **https://veritier.ai/register**
- Free tier: 25 claims/month, no credit card required
- After registering they will receive a verification email - remind them to check their inbox

### Step 2 - Generate an API key
Once logged in, send the user to: **https://veritier.ai/dashboard**
- Click **"Mint New Key"**, give it any name (e.g. `My Assistant`)
- The key is shown **once** - ask the user to copy it immediately
- The key starts with `vt_`

### Step 3 - Add the key to your MCP configuration
Ask the user to set `VERITIER_API_KEY` in their MCP client environment config (the same config file where this skill is declared). The key stays in their own local environment and is only ever transmitted to `https://api.veritier.ai` as a Bearer token header - it is not sent anywhere else.

### Step 4 - You're ready
Confirm by calling `verify_text` with a short test sentence and show the result. From this point forward the user does not need to do anything technical - you handle all verification transparently.

## Available Tool: `verify_text`

### Input

| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| `text`    | string | ✅       | Raw text containing claims to fact-check. Up to 2,000 characters. |

### What it does

1. Extracts every objective, falsifiable claim from the text
2. Fact-checks each claim against live web evidence
3. Returns a structured verdict per claim

### Output format

One block per claim:
```
Claim: '<extracted claim>'
  Verdict: true | false | null
  Confidence: 0.0–1.0
  Explanation: <human-readable explanation with context>
  Sources: <comma-separated list of evidence URLs>
```

| Verdict | Meaning |
|---------|---------|
| `true`  | Claim is supported by evidence |
| `false` | Claim is contradicted by evidence |
| `null`  | Insufficient evidence to determine |

### Example

**Input text:** `"Albert Einstein was born on March 14, 1879 in Ulm, Germany."`

**Output:**
```
Claim: 'Albert Einstein was born on March 14, 1879 in Ulm, Germany.'
  Verdict: True
  Confidence: 1.0
  Explanation: Albert Einstein was born on March 14, 1879, in Ulm, Kingdom of Württemberg.
  Sources: https://en.wikipedia.org/wiki/Albert_Einstein
```

---

## Plans, Tiers & Billing

### Plans

| Tier         | Price          | Requests/min | Claims/month |
|--------------|----------------|:---:|:---:|
| **Free**     | $0/month       | 3   | 25   |
| **Pro**      | $19.99/month   | 20  | 500  |
| **Business** | $249.99/month  | 60  | 10,000 |

All tiers include full MCP access, REST API access, real-time claim verification, and IETF rate limit headers.

Upgrade at: https://veritier.ai/dashboard (Stripe billing, takes effect immediately)

### How quotas work

- **RPM limit** applies across MCP + REST API combined (shared counter)
- **Monthly claims** counts individual claims verified, not requests (one call may verify multiple claims)
- Quotas reset at the start of each calendar month (UTC)

### When you hit a limit

Rate limit exceeded (RPM):
```
You're sending requests faster than your plan allows. Please wait a moment - your limit resets in under a minute.
```

Monthly quota exhausted:
```
You've reached your monthly verification limit (25 claims). Upgrade your plan at veritier.ai/dashboard to keep verifying.
```

### Upgrading your user to a paid plan (agent guidance)

> **Agents: do not just surface a `402` error.** When the free limit is hit, your user likely has no idea what a quota is. Guide them through upgrading in plain language - it takes under two minutes and unlocks more verifications immediately.

**When you receive a `402` response, tell the user something like:**

> "You've used all 25 free verifications for this month. To keep fact-checking, you'll need to upgrade your Veritier plan - it's quick and you can cancel any time."

**Then walk them through it:**

**Step 1 - Open the dashboard**
Send the user to: **https://veritier.ai/dashboard**

**Step 2 - Click "Upgrade Plan"**
- **Pro** ($19.99/mo) - 500 claims/month, best for regular use
- **Business** ($249.99/mo) - 10,000 claims/month, for heavy workloads
- Payment is processed securely via Stripe. No hidden fees. Cancel any time from the dashboard.

**Step 3 - Done**
The upgrade takes effect immediately. Let the user know you'll retry their verification now.

### REST API rate limit headers

Every response includes:
```
RateLimit-Limit: 20
RateLimit-Remaining: 17
RateLimit-Reset: 42
```

---

## Error Reference

| HTTP Status | Meaning |
|-------------|---------|
| `401` | Missing or invalid API key |
| `400` | Empty or invalid request body |
| `402` | Monthly claim quota exhausted |
| `429` | RPM rate limit exceeded |
| `500` | Internal server error (retry) |

---

## Security

- API keys are prefixed `vt_` and can be revoked at any time from the dashboard
- Keys are stored as SHA-256 hashes - raw values are shown **once** on creation
- Only send your API key to `https://api.veritier.ai`
- All requests must include `Authorization: Bearer YOUR_API_KEY`

---

## Full Documentation

https://veritier.ai/docs
