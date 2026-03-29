---
name: misttrack-skills
description: Cryptocurrency address risk analysis, AML compliance checks, and on-chain transaction tracing using the MistTrack OpenAPI. MistTrack is an anti-money laundering tracking tool developed by SlowMist, supporting risk scoring, label lookup, and transaction investigation for BTC, ETH, TRX, BNB, and other major chains.
optional_env_vars:
  - name: MISTTRACK_API_KEY
    required: false
    sensitive: true
    description: "MistTrack API key for authenticating all script requests (recommended). Required for standard API usage; if absent, configure X402_PRIVATE_KEY for x402 pay-per-use instead. Obtain at https://dashboard.misttrack.io/apikeys"
  - name: X402_PRIVATE_KEY
    required: false
    sensitive: true
    description: "Hex-encoded EVM/Solana private key for x402 pay-per-use. WARNING: grants the agent ability to sign on-chain transactions. See Security section below."
---

# MistTrack Skills

## Sub-skill Index

This skill pack contains two functional modules, each defined under the `skills/` directory:

| File | Function | Use Case |
|------|----------|----------|
| [skills/core.md](skills/core.md) | **Core Features** | Risk scoring, address investigation, multisig analysis, pre-transfer security checks, wallet integration (Bitget/Trust/Binance/OKX) |
| [skills/payment.md](skills/payment.md) | **x402 Payment** | Pay-per-use MistTrack API calls when no API Key is available |

---

## Security

> **Read this section before setting any environment variables or invoking payment features.**

### MISTTRACK_API_KEY

A standard API key for read-only AML queries. No on-chain access. Set via environment variable or `--api-key` flag.

### X402_PRIVATE_KEY - High Sensitivity

`X402_PRIVATE_KEY` enables the x402 pay-per-use flow in `scripts/pay.py`. This key can **sign and broadcast on-chain USDC transactions**.

Safeguards in code:
- Hard cap: **$1.00 USDC per call** - amounts above this are rejected automatically.
- `--auto` flag is off by default; without it, every payment requires explicit CLI confirmation.

Remaining risks:
- Any agent with access to this key and the `--auto` flag can transfer funds without further human confirmation.
- Long-lived environment variables are visible to all child processes of the current session.

Recommended practice:
1. **Prefer `MISTTRACK_API_KEY`** for normal usage - it never touches on-chain state.
2. If you must use x402, **pass the private key via `--private-key` at invocation time** rather than storing it as a permanent environment variable.
3. **Never enable `--auto` in production agent pipelines** unless you have reviewed and accept the risk.
4. The payment sub-skill (`skills/payment.md`) sets `disable_model_calls: true` to signal that autonomous agent invocation should be blocked. **Enforcement is harness-dependent**: platforms such as OpenClaw/skills.sh enforce this field; on other platforms (e.g., raw Claude Code) it is advisory only. In either case, do not pass `--auto` in automated pipelines.

---

## Quick Reference

### Pre-Transfer Security Check (Most Common)

Before executing any transfer or withdrawal, run the following script to check the recipient address for AML risk:

```bash
python3 scripts/transfer_security_check.py \
  --address <recipient_address> \
  --chain <chain_code> \
  --json
```

Exit Code: `0=ALLOW` / `1=WARN` / `2=BLOCK` / `3=ERROR`
See [skills/core.md](skills/core.md) for detailed decision logic.

### Full Address Investigation

```bash
python3 scripts/address_investigation.py --address 0x... --coin ETH
```

### x402 Pay-per-Use

When no API Key is available, use `scripts/pay.py` to pay per call with USDC.
See [skills/payment.md](skills/payment.md) for details and security considerations.

---

## Environment Variables

| Variable | Required | Sensitive | Description |
|----------|----------|-----------|-------------|
| `MISTTRACK_API_KEY` | No (recommended) | Yes | MistTrack API key - all scripts read this first; x402 is the alternative if absent |
| `X402_PRIVATE_KEY` | No | **High** | EVM/Solana private key (hex) for x402 payments - see Security section |

> When `MISTTRACK_API_KEY` is set, all scripts use API Key mode (read-only, no on-chain access).
> When not set, configure `X402_PRIVATE_KEY` to pay per call via `scripts/pay.py`.

---

## Python Dependencies

Install before use:

```bash
pip install requests eth-account eth-abi eth-utils
# For x402 Solana payments only:
pip install solders base58
```

| Package | Required for |
|---------|-------------|
| `requests` | All scripts |
| `eth-account` | `pay.py` (EIP-3009 signing) |
| `eth-abi` | `pay.py` (EIP-712 encoding) |
| `eth-utils` | `pay.py` (keccak256) |
| `solders` | `pay.py` (Solana partial signing) |
| `base58` | `pay.py` (Solana partial signing) |

---

## Script Reference

| Script | Function |
|--------|----------|
| `scripts/transfer_security_check.py` | Pre-transfer AML address check (main entry point) |
| `scripts/risk_check.py` | Single address risk scoring |
| `scripts/batch_risk_check.py` | Batch async risk scoring |
| `scripts/address_investigation.py` | Full address investigation (aggregates 6 APIs) |
| `scripts/multisig_analysis.py` | Multisig address identification and permission analysis |
| `scripts/pay.py` | x402 payment protocol client - see Security section |
