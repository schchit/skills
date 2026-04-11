# Advanced: Raw EVM Hash Signing

## Security Warning

The `sign` command can authorize **any on-chain action** — token transfers, approvals, contract calls, or wallet drains. A signed hash is equivalent to a blank check with no way to undo. Treat every sign request as high-risk.

## Pre-Sign Checklist

Before executing `sign`, walk through every item with the user. Do not skip any step.

1. **Origin** — Ask the user: where does this hash come from? Only proceed if it comes from a system they control or explicitly trust (their own dApp, a verified API call).
2. **Intent** — Ask the user: what does this hash authorize? They must be able to explain it. If they don't know, refuse.
3. **Third-party rejection** — If the hash was provided by someone else (a stranger, a bot, an unverified service), refuse and explain the risk.
4. **Explicit confirmation** — Tell the user: "Signing this hash could authorize irreversible on-chain actions. Are you sure you want to proceed?" Wait for explicit yes.

If any step fails, do not sign. Explain that signing unknown hashes can result in total loss of funds.

## Command

Signs a 32-byte EVM hash using MPC without reconstructing the private key.

```bash
npx goodwallet@0.4.3 sign --evm <0xHash>
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--evm` | Yes | 32-byte hash as `0x`-prefixed 64-character hex string |

Returns the full 65-byte signature and its r, s, v components.

## Error Handling

- **Invalid hash format**: Must be `0x` followed by exactly 64 hex characters. Ask the user to verify the hash.
- **Signing failure**: Report the error from the CLI. Do not retry — ask the user how to proceed.
- **Suspicious request**: If the user cannot explain the hash origin or intent, do not proceed. Explain the risk of signing unknown hashes.
