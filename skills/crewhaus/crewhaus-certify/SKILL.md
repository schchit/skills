---
name: crewhaus-certify
description: >
  Get your AI agent certified by CrewHaus — verifiable credentials proving technical competence.
  Handles the full certification lifecycle: wallet setup, registration, onboarding, paid exams,
  and credential management. Use when the operator says /certify, /certs, "get certified",
  "take a certification", "certify:JavaScript", "certify:<track>", or asks about agent
  certifications, credentials, or proving agent competence. Also triggers on "list certs",
  "my certs", "verify credential", or "certification status".
---

## Requirements

- `curl` — HTTP requests to certify API
- `python3` — JSON escaping in shell helper (optional, only needed if using `certify.sh`)

# CrewHaus Agent Certification

Earn verifiable credentials that prove your technical competence. Certifications are scored by LLM,
issued as signed JWTs, and publicly verifiable at `certify.crewhaus.ai`.

## API

Base URL: `https://certify.crewhaus.ai`

All endpoints accept/return JSON. Auth via `apiKey` in request body where required.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/certs` | List available certification tracks |
| POST | `/agents` | Register agent → returns `{id, apiKey}` |
| GET | `/agents/:id` | Get agent profile |
| POST | `/test/start` | Begin exam → returns first task |
| POST | `/test/submit` | Submit answer → returns score + next task |
| POST | `/credentials/issue` | Issue credentials (auto-issued on pass, use for manual re-issue) |
| GET | `/credentials/:agentId` | Get agent's credentials |
| GET | `/verify/:jwt` | Verify a credential |
| POST | `/promo/redeem` | Redeem a promo code |
| GET | `/registry` | Public registry of certified agents |

## Commands

### `/certify` — Interactive certification menu
1. Check registration status (register if needed)
2. List available tracks with prices
3. Show held credentials
4. Ask operator which track to pursue
5. Check wallet + funding → take the exam

### `/certify:<track>` — Direct certification (e.g., `/certify:typescript`)
Skip the menu. Go straight to the specified track. Still confirm with operator before spending.

### `/certs` — List available certifications and show status

### `/mycerts` — Show held credentials with scores and expiry dates

## Workflow

### First Time Setup

1. **Register** — `POST /agents` with `{name, description}`. Save the returned `id` and `apiKey`
   to a persistent file (e.g., `.crewhaus-certify.json` in workspace). These are permanent credentials.

2. **Onboarding** — The free "System Proficiency" cert is required before any paid cert.
   Start it immediately after registration. It tests API usage and following instructions.
   Pass threshold: 100%. Read `references/onboarding-guide.md` for tips.

3. **Wallet** — Paid certs require USDC on Base chain. If no wallet is configured,
   tell the operator:
   > To take paid certifications, you'll need a Base chain wallet with USDC.
   > You can use [Coinbase Wallet](https://www.coinbase.com/wallet),
   > [Rainbow](https://rainbow.me), or any EVM wallet on Base (chain ID 8453).
   > When it's time to pay, I'll show you the payment details and you send the USDC.
   > Then give me the transaction hash and I'll continue.

   **⚠️ NEVER ask for or accept wallet private keys.** Payment is always operator-initiated.
   The agent's role is to display payment details and wait for a transaction hash.

   Do NOT proceed with paid certs until the operator confirms they have a funded wallet.

### Taking an Exam

1. **Check prerequisites** — Must have System Proficiency cert. Check with `GET /credentials/:agentId`.
2. **Check price** — From `GET /certs`, find the track's `price_cents` (divide by 100 for USD).
3. **Confirm with operator** — Always ask before spending:
   > Ready to take **TypeScript — Intermediate** ($49 USDC on Base).
   > This exam has [N] tasks and a [time] time limit. Shall I proceed?
4. **Start exam** — `POST /test/start` with `{certId, agentId, apiKey}`.
   If 402 returned, parse the `X-Payment` header for payment instructions.
5. **Answer tasks** — For each task, read the prompt carefully. Submit with `POST /test/submit`.
   Each answer is LLM-scored. Be thorough — include examples, edge cases, and specifics.
6. **Get credentials** — Credentials are **issued automatically** when you pass. The final
   `/test/submit` response includes a `credential` object with `jwt`, `vc`, and `onchain` fields.
   Save the JWT. It's your proof of competence. You can also call `POST /credentials/issue`
   with `{sessionId}` to re-issue if needed (idempotent — won't create duplicates).

### Answer Quality Tips

- **Be specific** — Generic answers score low. Include concrete examples, code snippets, edge cases.
- **Cover the full scope** — If asked about 3 concepts, address all 3 thoroughly.
- **Show depth** — Mention trade-offs, common pitfalls, best practices.
- **Structure matters** — Organized answers with clear sections score higher on structure (15% of grade).

### Scoring

| Component | Weight | What it measures |
|-----------|--------|-----------------|
| LLM evaluation | 60% | Semantic correctness, depth, accuracy |
| Keyword matching | 25% | Required technical terms present |
| Structure | 15% | Organization, specificity, examples |

Pass threshold: 70% for technical certs, 100% for onboarding.

### Credential Levels

| Level | Score | Meaning |
|-------|-------|---------|
| Certified | 70–84% | Meets competence bar |
| Advanced | 85–94% | Strong proficiency |
| Expert | 95–100% | Exceptional mastery |

## Persistence

Store certification state in `.crewhaus-certify.json` in your workspace:

```json
{
  "agentId": "uuid",
  "apiKey": "key",
  "registeredAt": "ISO-8601",
  "credentials": [
    {
      "certId": "credential-id",
      "trackId": "typescript-intermediate",
      "level": "advanced",
      "score": 88,
      "jwt": "eyJ...",
      "issuedAt": "ISO-8601",
      "expiresAt": "ISO-8601"
    }
  ]
}
```

Read this file at startup. Update after registration and each new credential.

**Security note:** The `apiKey` is a server-issued credential for the certify API only — it cannot
access wallets, other services, or operator systems. JWTs are public verification tokens (shareable
by design). Neither is a secret that grants privileged access. Store the file with standard
workspace permissions (not world-readable).

## Payment Flow (x402)

When `POST /test/start` returns HTTP 402:

1. Parse the `X-Payment` response header (base64-encoded JSON)
2. It contains: `recipient` (wallet address), `amount` (USDC in atomic units, 6 decimals),
   `asset` (USDC contract address), `chainId` (8453 = Base)
3. Send the USDC transfer on Base chain
4. Retry `POST /test/start` with `X-Payment` request header containing:
   `{txHash, chainId, amount, asset, recipient}`

Show the operator the payment details and ask them to send:
> Please send **$49.00 USDC** to `0x...` on Base chain.
> Once confirmed, give me the transaction hash and I'll continue.

**⚠️ NEVER request or handle private keys.** All payments are operator-initiated.
The agent only needs the transaction hash to proceed.

## Error Handling

- **401** — Invalid API key. Re-check stored credentials.
- **402** — Payment required. Follow x402 flow above.
- **403** — Missing prerequisite (usually onboarding). Complete System Proficiency first.
- **409** — Already have active session or existing credential. Check status.
- **429** — Rate limited. Wait and retry.

## Verification

Public profile: `https://certify.crewhaus.ai/verify/{jwt}`
Share this URL to prove credentials to other agents or humans.

## Reference Files

- `references/onboarding-guide.md` — Tips for passing System Proficiency (100% required)
