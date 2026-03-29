---
name: misttrack-payment
description: MistTrack x402 pay-per-use payment protocol. When the user does not have a MistTrack API Key, use the x402 protocol to pay per call with USDC.
disable_model_calls: true
---

# MistTrack x402 Payment

> **This sub-skill requires explicit user invocation.** Autonomous agent calls are disabled (`disable_model_calls: true`) because this skill can sign and broadcast on-chain transactions.

> When the user does not have a MistTrack API Key, the Agent can use the x402 protocol to pay per API call with USDC via EVM (EIP-3009) or Solana partial signing. Base chain is used by default.

> **SECURITY — Read before use:**
> - This skill signs on-chain USDC transactions using a private key.
> - A hard cap of **$1.00 USDC per call** is enforced in code to limit exposure.
> - The `--auto` flag (or `auto_pay=True`) bypasses per-call confirmation — do **not** use in production agent pipelines.
> - Pass the private key via `--private-key` at invocation time; do **not** store it permanently in `X402_PRIVATE_KEY`.
> - Environment variables are visible to all child processes of the current session.

## Supported APIs and Pricing (USDC per call)

| # | x402 API Path | Original Path | Price |
|---|---|---|---|
| 1 | `https://openapi.misttrack.io/x402/address_labels` | `v1/address_labels` | $0.1 |
| 2 | `https://openapi.misttrack.io/x402/address_overview` | `v1/address_overview` | $0.5 |
| 3 | `https://openapi.misttrack.io/x402/risk_score` | `v2/risk_score` | $1.0 |
| 4 | `https://openapi.misttrack.io/x402/risk_score_create_task` | `v2/risk_score_create_task` | $1.0 |
| 5 | `https://openapi.misttrack.io/v2/risk_score_query_task` | `v2/risk_score_query_task` | $0 (free polling) |
| 6 | `https://openapi.misttrack.io/x402/transactions_investigation` | `v1/transactions_investigation` | $1.0 |
| 7 | `https://openapi.misttrack.io/x402/address_action` | `v1/address_action` | $0.5 |
| 8 | `https://openapi.misttrack.io/x402/address_trace` | `v1/address_trace` | $0.5 |
| 9 | `https://openapi.misttrack.io/x402/address_counterparty` | `v1/address_counterparty` | $0.5 |

## Supported EVM Chains

| Chain ID | Network |
|:---:|:---|
| 1 | Ethereum Mainnet |
| 10 | Optimism |
| 137 | Polygon |
| 8453 | Base (default) |
| 42161 | Arbitrum One |
| 43114 | Avalanche C-Chain |

---

## Usage

### 1. CLI

```bash
# Full x402 payment flow (request → parse 402 → sign → retry)
python3 scripts/pay.py pay \
  --url "https://openapi.misttrack.io/x402/address_labels?address=0x..." \
  --private-key <hex_private_key> \
  --chain-id 8453

# Manually sign EIP-3009
python3 scripts/pay.py sign-eip3009 \
  --private-key <hex> \
  --token 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \
  --chain-id 8453 \
  --to 0x209693Bc6afc0C5328bA36FaF03C514EF312287C \
  --amount 10000

# Sign a Solana partial transaction
python3 scripts/pay.py sign-solana \
  --private-key <hex_32byte_seed> \
  --transaction <base64_encoded_tx>
```

Environment variable: `X402_PRIVATE_KEY` can be used in place of the `--private-key` argument.

### 2. Inline Code Usage

> **Warning**: The example below uses `auto_pay=True`, which means the Agent will automatically sign and broadcast payment transactions without per-call confirmation. Do not enable this in production environments, and avoid hardcoding or storing private keys in environment variables long-term.

```python
from scripts.pay import request_with_x402

response = request_with_x402(
    url="https://openapi.misttrack.io/x402/address_labels?address=0x...",
    private_key="your_private_key_hex",
    chain_id=8453,
    auto_pay=True,  # True = auto-pay without confirmation; set to False in production
)
print(response.json())
```

---

## Security Limits

- Per-call payment cap: **$1.00 USDC (1,000,000 smallest units)**. Amounts exceeding this are automatically rejected to prevent a malicious server from draining the wallet.
- The private key can be passed via the `--private-key` argument or the `X402_PRIVATE_KEY` environment variable. **It is recommended to use `--private-key` on demand (one-time use)** rather than storing the private key as a long-lived environment variable — environment variables are visible to all child processes of the current process and carry a risk of leakage.

---

## Dependencies

```bash
pip install eth-account eth-abi eth-utils requests
# For Solana payments, additionally install:
pip install solders base58
```
