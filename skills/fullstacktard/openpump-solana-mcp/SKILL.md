---
name: openpump-solana-mcp
description: >
  Solana token launch and trading tools via the OpenPump MCP server.
  Use when creating tokens on pump.fun, buying or selling tokens,
  transferring SOL or SPL tokens, checking wallet balances, managing wallets,
  getting token quotes, or monitoring portfolio and creator fees.
  Covers all pump.fun operations including bundle buys, bundle sells,
  Jito priority, bonding curve analytics, and trading workflows.
version: "1.0.0"
author: openpump
license: MIT
homepage: https://openpump.io
user-invocable: true

metadata:
  openclaw:
    emoji: "\U0001F680"
    requires:
      bins: ["node", "npx"]
      env: ["OPENPUMP_API_KEY"]
    primaryEnv: "OPENPUMP_API_KEY"
    install:
      - id: openpump-mcp
        kind: node
        package: "@openpump/mcp-server"
        bins: ["openpump-mcp"]
        label: "Install OpenPump MCP Server (npm)"
    os: ["linux", "darwin", "win32"]
    network: ["api.openpump.io", "mcp.openpump.io"]
    homepage: "https://openpump.io"

tags:
  - solana
  - crypto
  - trading
  - pump-fun
  - defi
  - mcp
  - token-launch
  - memecoin
  - jito
  - bonding-curve
---

# OpenPump MCP Server

Trade pump.fun tokens, manage Solana wallets, and monitor positions via MCP.

## Setup

### 1. Get Your API Key

1. Sign up at [openpump.io](https://openpump.io)
2. Go to Dashboard > API Keys
3. Create a new key (starts with `op_sk_live_`)

### 2. Set the Environment Variable

```bash
export OPENPUMP_API_KEY="op_sk_live_YOUR_KEY_HERE"
```

Or add it to your `~/.openclaw/.env` file.

### 3. Add MCP Server to OpenClaw

Add the following to your `~/.openclaw/openclaw.json` under the `mcpServers` key:

```json
{
  "mcpServers": {
    "openpump": {
      "command": "npx",
      "args": ["-y", "@openpump/mcp-server@latest"],
      "env": {
        "OPENPUMP_API_KEY": "${OPENPUMP_API_KEY}"
      }
    }
  }
}
```

OpenClaw will hot-reload and connect to the server. All 23 tools become available immediately.

### Alternative: HTTP Transport (No Local Process)

If you prefer a remote connection instead of a local stdio process:

```json
{
  "mcpServers": {
    "openpump": {
      "url": "https://mcp.openpump.io/mcp",
      "headers": {
        "Authorization": "Bearer ${OPENPUMP_API_KEY}"
      }
    }
  }
}
```

## When to Use

- Launching a new token on pump.fun
- Buying or selling pump.fun tokens
- Checking wallet balances or token holdings
- Transferring SOL or SPL tokens between wallets
- Getting price quotes before trading
- Monitoring creator fees
- Coordinating multi-wallet bundle buys or sells
- Querying token analytics and risk metrics

## When NOT to Use

- **On-chain queries outside pump.fun** -- use a Solana RPC tool for general data
- **Wallet key management** -- OpenPump uses custodial HD wallets; you cannot import external private keys
- **DeFi beyond pump.fun** -- Raydium, Orca, Jupiter swaps are not supported
- **NFT operations** -- fungible tokens only

## Available Tools (23)

### Token Creation

| Tool | Description |
|------|-------------|
| `create-token` | Launch a new token on pump.fun with name, symbol, description, and image |

### Trading

| Tool | Description |
|------|-------------|
| `bundle-buy` | Coordinated multi-wallet buy at token creation via Jito bundles |
| `bundle-sell` | Multi-wallet sell packed into Jito bundles |
| `buy-token` | Buy a PumpFun token with SOL (single wallet) |
| `sell-token` | Sell a token position back to SOL |
| `estimate-bundle-cost` | Preview bundle cost without submitting a transaction |
| `claim-creator-fees` | Claim accumulated creator fees from your tokens |

### Transfers

| Tool | Description |
|------|-------------|
| `transfer-sol` | Send SOL to any Solana address (10 SOL cap per call) |
| `transfer-token` | Send SPL tokens to any Solana address |

### Wallet Management

| Tool | Description |
|------|-------------|
| `create-wallet` | Create a new HD-derived custodial wallet |
| `get-aggregate-balance` | Sum SOL across all user wallets |
| `get-wallet-deposit-address` | Get deposit address and QR-ready funding instructions |
| `get-wallet-transactions` | Paginated transfer history for a wallet |

### Information (Read-Only)

| Tool | Description |
|------|-------------|
| `get-token-info` | Bonding curve state: price, market cap, graduation status |
| `get-token-market-info` | Rich analytics: volume, buy/sell counts, risk metrics |
| `list-my-tokens` | All tokens launched by the authenticated user |
| `get-token-holdings` | Which wallets hold a specific token (or all holdings) |
| `get-wallet-balance` | SOL + token balances for a single wallet |
| `list-wallets` | All wallets with public keys, labels, derivation index |
| `get-creator-fees` | Check accumulated PumpFun creator fees across wallets |
| `get-token-quote` | Price quote for buy or sell without executing |
| `get-jito-tip-levels` | Current Jito MEV tip amounts per priority level |

### Job Polling

| Tool | Description |
|------|-------------|
| `poll-job` | Check status of async operations (poll every 2s until done) |

## Workflows

### 1. Launch a Token

```
1. create-wallet (label: "launch-wallet")
2. Fund the wallet with SOL (use get-wallet-deposit-address for the address)
3. create-token (name, symbol, description, imageUrl)
4. poll-job (wait for confirmation)
5. get-token-info (verify token is live on pump.fun)
```

### 2. Buy and Sell Flow

```
1. list-wallets (find walletId with SOL balance)
2. get-token-quote (action: "buy", solAmount in lamports) -- preview first
3. buy-token (mint, walletId, amountSol in lamports)
4. get-token-holdings (mint) -- verify purchase
5. get-token-quote (action: "sell", tokenAmount) -- preview sell
6. sell-token (mint, walletId, tokenAmount or "all")
```

### 3. Check Portfolio

```
1. list-wallets -- see all wallets
2. get-aggregate-balance -- total SOL across wallets
3. get-token-holdings -- all token positions (omit mint for everything)
4. get-token-market-info (per mint) -- current prices and risk metrics
```

### 4. Claim Creator Fees

```
1. get-creator-fees -- check all wallets for accumulated fees
2. claim-creator-fees (creatorAddress)
3. get-wallet-balance (walletId) -- verify SOL increased
```

### 5. Bundle Launch (Multi-Wallet)

```
1. create-wallet (multiple, label each by purpose)
2. Fund wallets with SOL
3. estimate-bundle-cost (buyWalletCount, devBuyAmountSol, walletBuyAmounts)
4. bundle-buy (devWalletId, buyWalletIds, tokenParams, amounts, confirm: true)
5. poll-job (wait for confirmation)
6. get-token-holdings (mint) -- verify all wallets hold the token
```

### 6. Transfer SOL Out

```
1. get-wallet-balance (walletId) -- check available SOL
2. transfer-sol (walletId, toAddress, amountLamports, dryRun: true) -- preview
3. transfer-sol (walletId, toAddress, amountLamports) -- execute
```

## Autonomous Agent Patterns

### Heartbeat: Portfolio Monitor

Configure OpenClaw's heartbeat (runs every 30 minutes) to monitor your positions:

```
Every heartbeat cycle:
1. get-token-holdings -- check all open positions
2. get-token-market-info (per mint) -- current price and risk metrics
3. If any position is down > 50%: sell-token to stop losses
4. If any position is up > 200%: sell-token to take profits
5. Report P&L summary
```

### Autonomous Token Scanner

Use OpenClaw's event loop to scan for new opportunities:

```
On each cycle:
1. Monitor for new pump.fun token launches (via external feeds)
2. get-token-info (mint) -- check bonding curve state
3. get-token-market-info (mint) -- check risk metrics
4. If safety score > 70 AND liquidity > 5 SOL AND dev holdings < 10%:
   - get-token-quote (buy preview)
   - buy-token (within position size limits)
5. Log reasoning and decision
```

### Copy Trader

Follow whale wallets and mirror their trades:

```
On whale activity detected:
1. Identify which token the whale bought
2. get-token-info (mint) -- is it on pump.fun?
3. get-token-market-info (mint) -- safety check
4. get-token-quote (buy, proportional amount)
5. buy-token (if within risk limits)
6. Set exit conditions (stop-loss, take-profit)
```

## Safety Guardrails

**IMPORTANT: These guardrails should be followed for ALL trading operations.**

1. **Always check balances first.** Before any trade or transfer, run `get-wallet-balance` or `get-aggregate-balance` to verify you have sufficient SOL.

2. **Use quotes before trading.** Call `get-token-quote` before `buy-token` or `sell-token` to preview the expected output and price impact.

3. **Confirm large trades explicitly.** Bundle operations require `confirm: true`. Never set confirm without reviewing the parameters.

4. **Verify addresses on transfers.** Double-check the destination address before calling `transfer-sol` or `transfer-token`. Transfers are irreversible on Solana.

5. **Use dryRun for transfers.** Both transfer tools support `dryRun: true` to validate inputs and estimate fees without submitting.

6. **Check risk metrics.** Use `get-token-market-info` to check sniper count, bundler activity, and insider percentage before buying.

7. **Understand priority levels.** Jito priority tiers (economy/normal/fast/turbo) affect transaction speed and cost. Use `get-jito-tip-levels` to see current rates.

8. **Monitor async operations.** After `create-token` or `bundle-buy`, call `poll-job` every 2 seconds until status is "completed" or "failed". Jobs expire after 10 minutes.

9. **Transfer cap.** `transfer-sol` has a hard cap of 10 SOL per call. For larger amounts, split into multiple calls.

10. **Bundle buy legal notice.** Coordinated multi-wallet purchases (`bundle-buy`) may have legal implications. Review the RICO disclaimer before using.

## Key Concepts

- **Lamports:** SOL amounts are in lamports (1 SOL = 1,000,000,000 lamports). Always pass as decimal integer strings, not floats.
- **Token base units:** Token amounts use raw base units (not UI decimals). Use the exact string from `get-token-holdings`.
- **Custodial wallets:** All wallets are HD-derived and managed by the platform. You cannot import external keys.
- **Bonding curve:** pump.fun tokens trade on a bonding curve until they graduate to PumpSwap. `bundle-sell` only works on bonding curve tokens.
- **Jito bundles:** Bundle operations use Jito MEV for atomic, same-block execution (first 3 wallets guaranteed).

## Quick Reference

```
# Check setup
list-wallets                          # See all wallets
get-aggregate-balance                 # Total SOL

# Before buying
get-token-info (mint)                 # Is it live?
get-token-market-info (mint)          # Risk metrics
get-token-quote (mint, "buy", amount) # Price preview

# Trade
buy-token (walletId, mint, amountSol)
sell-token (walletId, mint, tokenAmount or "all")

# After trading
get-token-holdings (mint)             # Verify position
get-wallet-balance (walletId)         # Check SOL left

# Transfer
transfer-sol (walletId, toAddress, amount, dryRun: true)  # Preview
transfer-sol (walletId, toAddress, amount)                 # Execute

# Creator fees
get-creator-fees                      # Check claimable
claim-creator-fees (creatorAddress)   # Claim
```

## Links

- Website: [openpump.io](https://openpump.io)
- API Docs: [docs.openpump.io](https://docs.openpump.io)
- GitHub: [github.com/openpump/openpump](https://github.com/openpump/openpump)
- npm: [@openpump/mcp-server](https://www.npmjs.com/package/@openpump/mcp-server)
