# TOOLS -- OpenPump MCP Server Tool Reference

This workspace connects to the OpenPump MCP server, which provides 23 tools for Solana token operations on pump.fun. All tools communicate with the OpenPump REST API using your `OPENPUMP_API_KEY`.

## MCP Server Connection

The server is configured in `openclaw.json` and connects automatically when OpenClaw starts. All tools below are available as MCP tool calls.

**Important conventions:**
- SOL amounts are always in **lamports** as decimal integer strings (1 SOL = `"1000000000"`)
- Token amounts use raw **base units** as decimal strings (use the exact string from `get-token-holdings`)
- Never pass floats or JavaScript numbers for on-chain amounts -- always use strings
- Wallet IDs are UUIDs returned by `list-wallets`, not public key addresses

---

## Token Creation Tools

### `create-token`

Launch a new token on pump.fun with a bonding curve.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| walletId | string | Yes | ID of the creator/dev wallet |
| name | string | Yes | Token name (max 32 chars) |
| symbol | string | Yes | Token ticker symbol (max 10 chars) |
| description | string | Yes | Token description (max 500 chars) |
| imageUrl | string | Yes | Publicly accessible image URL (fetched and uploaded to IPFS) |
| initialBuyAmountSol | number | No | SOL amount for dev initial buy at creation |
| twitter | string | No | Twitter handle |
| telegram | string | No | Telegram link |
| website | string | No | Website URL |

**When to use:** Only when explicitly instructed to create a token. Not part of the standard trading workflow.

**Returns:** Mint address and transaction signature. Typical confirmation: 2-5 seconds.

---

## Trading Tools

### `buy-token`

Buy a pump.fun token with SOL from a single wallet.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| walletId | string | Yes | ID of the wallet to buy with |
| mint | string | Yes | Token mint address (base58) |
| amountSol | string | Yes | SOL to spend in lamports (e.g., `"100000000"` = 0.1 SOL) |
| slippageBps | number | No | Slippage tolerance in basis points (default: 500 = 5%) |
| priorityLevel | string | No | `"economy"`, `"normal"` (default), `"fast"`, or `"turbo"` |

**When to use:** Primary buy tool. Always call `get-token-quote` first to preview.

**Returns:** Transaction result with updated wallet balance.

### `sell-token`

Sell a token position back to SOL.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| walletId | string | Yes | ID of the wallet holding the token |
| mint | string | Yes | Token mint address (base58) |
| tokenAmount | string | Yes | Raw base units as string, or `"all"` to sell entire balance |
| slippageBps | number | No | Slippage tolerance in basis points (default: 500 = 5%) |
| priorityLevel | string | No | `"economy"`, `"normal"` (default), `"fast"`, or `"turbo"` |

**When to use:** For all exits -- stop-loss, take-profit, time decay, manual sell. Use `tokenAmount: "all"` for full exits.

**Returns:** Transaction result with updated wallet balance.

### `bundle-buy`

Coordinated multi-wallet buy at token creation via Jito MEV bundles. Requires `confirm: true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| devWalletId | string | Yes | ID of the dev/creator wallet |
| buyWalletIds | string[] | Yes | IDs of wallets for bundle buy (max 20) |
| tokenParams | object | Yes | `{ name, symbol, description, imageUrl }` |
| devBuyAmountSol | string | Yes | Dev buy amount in lamports |
| walletBuyAmounts | string[] | Yes | Per-wallet SOL amounts in lamports |
| priorityLevel | string | No | Priority tier (default: `"normal"`) |
| confirm | boolean | Yes | Must be `true` to execute |

**When to use:** Advanced token launch with coordinated multi-wallet buying. Always run `estimate-bundle-cost` first.

**Returns:** Job ID for async tracking via `poll-job`.

### `bundle-sell`

Multi-wallet sell packed into Jito MEV bundles. Requires `confirm: true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| mint | string | Yes | Token mint address (base58) |
| walletSells | object[] | Yes | Array of `{ walletId, tokenAmount }` (1-20 wallets) |
| tipWalletId | string | No | Wallet ID that pays the Jito tip |
| slippageBps | number | No | Slippage tolerance (default: 500 = 5%) |
| priorityLevel | string | No | Priority tier (default: `"normal"`) |
| confirm | boolean | Yes | Must be `true` to execute |

**When to use:** Selling from multiple wallets simultaneously. Only works on bonding curve tokens (not yet graduated).

### `estimate-bundle-cost`

Preview the total SOL required for a bundle launch without submitting.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| buyWalletCount | number | Yes | Number of buy wallets (max 20) |
| devBuyAmountSol | string | Yes | Dev buy amount in lamports |
| walletBuyAmounts | string[] | Yes | Per-wallet amounts in lamports |
| tipLamports | number | No | Custom Jito tip in lamports |
| priorityLevel | string | No | Priority tier (default: `"normal"`) |

**When to use:** Always call before `bundle-buy` to verify sufficient balances.

### `claim-creator-fees`

Claim all accumulated creator fees for a wallet address.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| creatorAddress | string | Yes | Creator wallet address (base58) |

**When to use:** After `get-creator-fees` shows a claimable balance. Call periodically to collect fees.

---

## Transfer Tools

### `transfer-sol`

Send SOL to any Solana address. Hard cap: 10 SOL per call. Requires `confirm: true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| fromWalletId | string | Yes | Source wallet ID |
| toAddress | string | Yes | Destination Solana address (base58) |
| amountSol | string | Yes | Amount in lamports (max `"10000000000"` = 10 SOL) |
| memo | string | No | On-chain memo (max 256 chars) |
| priorityFeeMicroLamports | number | No | Priority fee in micro-lamports |
| dryRun | boolean | No | Validate without submitting (default: false) |
| confirm | boolean | Yes | Must be `true` to execute |

**When to use:** Moving SOL between wallets or to external addresses. Always use `dryRun: true` first to preview.

### `transfer-token`

Send SPL tokens to any Solana address. Requires `confirm: true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| fromWalletId | string | Yes | Source wallet ID |
| toAddress | string | Yes | Destination Solana address (base58) |
| mint | string | Yes | SPL token mint address (base58) |
| tokenAmount | string | Yes | Raw base units as string, or `"all"` |
| memo | string | No | On-chain memo (max 256 chars) |
| priorityFeeMicroLamports | number | No | Priority fee in micro-lamports |
| dryRun | boolean | No | Validate without submitting (default: false) |
| confirm | boolean | Yes | Must be `true` to execute |

**When to use:** Moving tokens between wallets or to external addresses. Always use `dryRun: true` first.

---

## Wallet Management Tools

### `create-wallet`

Create a new HD-derived custodial wallet.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| label | string | No | Human-readable label (e.g., `"trading-main"`) |

**When to use:** Setting up a new trading wallet. Use labels to organize by purpose.

### `get-aggregate-balance`

Sum SOL across all user wallets. No parameters.

**When to use:** Quick check of total available capital before large operations.

### `get-wallet-deposit-address`

Get deposit address and funding instructions for a wallet.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| walletId | string | Yes | Wallet ID to get deposit address for |

**When to use:** When a wallet needs to be funded from an external source.

### `get-wallet-transactions`

Paginated transfer history for a wallet.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| walletId | string | Yes | Wallet ID |
| type | string | No | Filter: `"buy"`, `"sell"`, or `"transfer"` |
| limit | number | No | Results per page (default: 50, max: 100) |
| offset | number | No | Pagination offset (default: 0) |

**When to use:** Reviewing trade history, calculating P&L, auditing transactions.

---

## Information & Analytics Tools

### `get-token-info`

Bonding curve state for a pump.fun token: price, market cap, graduation status.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| mint | string | Yes | Token mint address (base58) |

**When to use:** First check when evaluating a token. Confirms the token exists and is active.

### `get-token-market-info`

Rich analytics: volume, buy/sell counts, price changes, risk metrics (snipers, bundlers, insiders). Mainnet only.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| mint | string | Yes | Token mint address (base58) |

**When to use:** Second check in the safety checklist. Critical for risk assessment. Always check before buying.

### `list-my-tokens`

All tokens launched by the authenticated user. No parameters.

**When to use:** Reviewing tokens you have created (for creator fee claims).

### `get-token-holdings`

Check which wallets hold a specific token, or get all token holdings across all wallets.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| mint | string | No | Token mint address. Omit for ALL holdings across all wallets |

**When to use:** Before selling (to get exact token amounts), during heartbeat checks (to scan all positions), after buying (to verify purchase).

### `get-wallet-balance`

SOL and token balances for a single wallet. Real-time on-chain data.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| walletId | string | Yes | Wallet ID |

**When to use:** Before buying (to confirm sufficient SOL), after trades (to verify balance changes).

### `list-wallets`

All wallets with public keys, labels, and derivation index. No parameters.

**When to use:** At startup to identify available wallets. After creating a new wallet.

### `get-creator-fees`

Check accumulated PumpFun creator fees across wallets.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| address | string | No | Specific creator address. Omit to check all wallets |

**When to use:** Periodically to check if creator fees are claimable.

### `get-token-quote`

Price quote for buy or sell without executing a transaction.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| mint | string | Yes | Token mint address |
| action | string | Yes | `"buy"` or `"sell"` |
| solAmount | string | Conditional | SOL in lamports (required for buy) |
| tokenAmount | string | Conditional | Raw base units (required for sell) |

**When to use:** Always before `buy-token` or `sell-token` to preview expected output and price impact.

### `get-jito-tip-levels`

Current Jito MEV tip amounts per priority level. No parameters.

**When to use:** Before trades to understand current MEV costs. Useful for selecting appropriate priority level.

---

## Job Polling

### `poll-job`

Check status of async operations.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| jobId | string | Yes | Job ID from a previous async tool call |

**When to use:** After `bundle-buy` or any operation that returns a `jobId`. Poll every 2 seconds until status is `"completed"` or `"failed"`. Jobs expire after 10 minutes.

---

## Priority Level Reference

| Level | Jito Tip Range | Use Case |
|-------|---------------|----------|
| `economy` | ~1,000 - 10,000 lamports | Low-urgency trades, saving fees |
| `normal` | ~2,000 - 100,000 lamports | Standard trading (default) |
| `fast` | ~10,000 - 500,000 lamports | Stop-loss exits, time-sensitive entries |
| `turbo` | ~100,000 - 1,000,000 lamports | Emergency exits, rug detection response |
