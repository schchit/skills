---
name: bankofbots
description: >
  Trust scoring for AI agents. Submit on-chain payment proofs and x402 receipts
  to build a verifiable BOB Score that other agents and services can check
  before doing business with yours.
metadata: '{"openclaw":{"requires":{"env":["BOB_API_KEY","BOB_AGENT_ID"]},"optional":{"env":["BOB_API_URL"]},"primaryEnv":"BOB_API_KEY"}}'
---

## Core concepts

BOB (beta) is a non-custodial payment proof and trust layer. Agents submit cryptographic proofs of on-chain payments they made externally. Each proof builds credit history and raises their BOB Score, a 0–1000 reputation score for long-term financial trustworthiness.

- **Agent**: An AI agent with its own identity and BOB Score
- **Payment Proof**: Cryptographic evidence of an on-chain transaction (BTC, ETH, Base, or SOL txid/hash)
- **BOB Score**: 0–1000 reputation score derived from proof history, wallet binding, and social signals
- **Credit Event**: A scored action that changed the agent's BOB Score
- **Wallet Binding**: Proof of ownership over an external EVM wallet

## Quick start

```bash
bob init --code <claim-code>
bob auth me
```

## Commands

### Check your identity

```bash
bob auth me
```

### Agent management

```bash
bob agent create --name <name>
bob agent get <agent-id>
bob agent list
bob agent approve <agent-id>
```

### Import historical on-chain proofs

For outbound proofs, pass `--sender-address` (required for EVM proofs) so BOB can verify the on-chain sender matches your bound wallet. For inbound proofs, pass `--recipient-address` instead. When both the sender and recipient submit the same tx, confidence is boosted from Medium to Strong (see "Dual-sided proof submission" below).

```bash
# BTC on-chain (outbound)
bob agent credit-import <agent-id> \
  --proof-type btc_onchain_tx \
  --proof-ref <txid> \
  --rail onchain \
  --currency BTC \
  --amount <sats> \
  --direction outbound

# ETH on-chain (outbound — sender-address required)
bob agent credit-import <agent-id> \
  --proof-type eth_onchain_tx \
  --proof-ref <0x...txhash> \
  --rail onchain \
  --currency ETH \
  --amount <wei> \
  --direction outbound \
  --sender-address <your-bound-wallet>

# Base on-chain (outbound — sender-address required)
bob agent credit-import <agent-id> \
  --proof-type base_onchain_tx \
  --proof-ref <0x...txhash> \
  --rail onchain \
  --currency ETH \
  --amount <wei> \
  --direction outbound \
  --sender-address <your-bound-wallet>

# Solana on-chain (outbound)
bob agent credit-import <agent-id> \
  --proof-type sol_onchain_tx \
  --proof-ref <txsig> \
  --rail onchain \
  --currency SOL \
  --amount <lamports> \
  --direction outbound

# ETH on-chain (inbound — you received the payment)
bob agent credit-import <agent-id> \
  --proof-type eth_onchain_tx \
  --proof-ref <0x...txhash> \
  --rail onchain \
  --currency ETH \
  --amount <wei> \
  --direction inbound \
  --recipient-address <your-bound-wallet>

bob agent credit-imports <agent-id> [--limit 50] [--offset 0]
```

### Dual-sided proof submission

Both the sender and recipient of a transaction can independently submit a proof for the same on-chain tx. Each side earns credit:

- **Outbound** (`--direction outbound`, default): You sent the payment. Pass `--sender-address` for EVM proofs so the on-chain sender can be verified against your bound wallet.
- **Inbound** (`--direction inbound`): You received the payment. Pass `--recipient-address` for EVM proofs.

When both counterparties submit the same transaction, confidence is automatically upgraded from `medium` to `strong`.

### Import x402 payment receipts

```bash
bob agent x402-import <agent-id> \
  --tx <tx-hash> \
  --network eip155:8453 \
  --payer <wallet-address> \
  --payee <service-address> \
  --amount <atomic-units> \
  --resource-url <service-url>
```

### Agent credit and BOB Score

```bash
bob score me
bob agent credit-events <agent-id> [--limit 50] [--offset 0]

bob score me
bob score composition
bob score leaderboard
bob score signals --signal github --visible true
```

### Bind a wallet

```bash
bob binding evm-challenge --address <0x...>
bob binding evm-verify --challenge-id <id> --address <0x...> --signature <sig> [--chain-id 0x1]
```

### Webhooks and inbox

```bash
bob webhook create <agent-id> --url https://example.com/hook --events proof.verified,credit.updated
bob webhook list <agent-id>
bob webhook get <agent-id> <webhook-id>
bob webhook update <agent-id> <webhook-id> --active true
bob webhook delete <agent-id> <webhook-id>

bob inbox list <agent-id> [--limit 30] [--offset 0]
bob inbox ack <agent-id> <event-id>
bob inbox events <agent-id> [--limit 30]
```

### API keys

```bash
bob api-key list
bob api-key create --name <label>
bob api-key revoke <key-id>
```

## Output format

```json
{
  "ok": true,
  "command": "bob agent credit-import",
  "data": {},
  "next_actions": [
    {
      "command": "bob score me",
      "description": "Check updated BOB Score"
    }
  ]
}
```

### Import MPP receipt (Tempo, Lightning, Stripe, Card)

```bash
bob agent mpp-import $BOB_AGENT_ID \
  --method tempo \
  --reference 0xabc123... \
  --challenge-id ch_xxx \
  --challenge-intent pay \
  --challenge-request <base64url-encoded-json> \
  --realm api.merchant.com \
  --source did:key:sender... \
  --resource-url https://api.merchant.com/v1/chat
```

Supported methods: `tempo` (stablecoin on Base), `lightning`, `stripe`, `card`.

## Error recovery

| Error | Cause | Fix |
|---|---|---|
| `sender_address_mismatch` | The `--sender-address` you provided does not match the on-chain sender of the transaction | Verify the address matches the actual sender on-chain and that it is bound to your agent via `bob binding evm-verify` |

## Important rules

1. Amounts are native atomic units: satoshis for BTC, wei for ETH/Base, lamports for SOL.
2. Proofs are non-custodial. BOB never holds your funds.
3. Historical on-chain proof imports and x402 receipt imports are the current public proof rails.
4. For outbound EVM proofs, `--sender-address` is required and must match the on-chain sender — mismatches fail with `sender_address_mismatch`.
