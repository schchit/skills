---
name: goodwallet
version: 1.4.3
description: >
  Manage MPC agentic wallets via the goodwallet CLI — authenticate, check balances,
  send ETH/ERC-20 tokens, swap or bridge tokens across chains, view activity, and
  trade on Polymarket prediction markets. Use this skill whenever the user wants to
  do anything with their wallet: checking what they own, transferring tokens to someone,
  swapping one token for another, bridging across chains, looking up token info, or
  trading predictions. Trigger even if the user doesn't say "goodwallet" explicitly —
  phrases like "what's in my wallet", "send 10 USDC to 0x...", "swap POL for USDC",
  "how much ETH do I have", "buy yes on Trump", "bridge to Polygon", "sign a hash",
  or "sign a transaction" all qualify.
metadata: {"openclaw": {"emoji": "👛", "requires": {"bins": ["node"]}}}
---

# Goodwallet

All commands are run via `npx goodwallet@0.4.3`.

## Constraints

- Do NOT share technical details of the CLI tool with the user (encryption schemes, key types, internal file paths, session IDs, config formats). Users are non-technical — report outcomes in plain language, not raw CLI output.
- Always confirm with the user before executing transactions (`send`, `swap execute`, `predictions buy`, `predictions fund`). These move real money and are irreversible on-chain.
- Never fabricate transaction hashes, balances, or addresses — only report what the CLI returns.

## Setup / Authorization

1. Run `npx goodwallet@0.4.3 auth` — this prints an auth URL.
2. **Show the URL to the user** and tell them to open it in their browser. Do NOT open it programmatically.
3. **Immediately** run `npx goodwallet@0.4.3 auth --pair` — do NOT wait for user confirmation. It polls automatically until the user completes the browser flow (up to 3 minutes).

```bash
npx goodwallet@0.4.3 auth
npx goodwallet@0.4.3 auth --pair
```

To log out: `npx goodwallet@0.4.3 auth --logout`

## Commands

### balance — Show balances

Shows native + ERC-20 balances across supported chains with USD values.

```bash
npx goodwallet@0.4.3 balance
```

### activity — Show recent activity

Shows recent incoming and outgoing transactions across all supported chains.

```bash
npx goodwallet@0.4.3 activity
```

### send — Send native or ERC-20 tokens

Builds, MPC-signs, and broadcasts a transaction. All four flags are required.

```bash
npx goodwallet@0.4.3 send --chain <chainId> --token <0xAddress> --to <0xAddress> --amount <amount>
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--chain` | Yes | Numeric chain ID (see `references/chains.md`) |
| `--token` | Yes | Token contract address (use native address for native coin) |
| `--to` | Yes | Recipient Ethereum address |
| `--amount` | Yes | Amount in human-readable units (e.g. `0.1`, `100`) |

Running `send` with no flags shows current balances with chain IDs and token addresses — useful for looking up values.

### swap search — Look up token information

Looks up a token by symbol or contract address on a specific chain. Returns address, symbol, decimals, price, and market data.

```bash
npx goodwallet@0.4.3 swap search token <symbol|0xAddress> chain <chainId>
```

### swap — Get a swap/bridge quote

Finds the best route between tokens across chains using LiFi. Returns estimated output, fees, gas costs, and a route ID for execution.

```bash
npx goodwallet@0.4.3 swap from-chain <id> from-token <0x> to-chain <id> to-token <0x> amount <n>
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `from-chain` | Yes | Source chain ID |
| `from-token` | Yes | Source token contract address |
| `to-chain` | Yes | Destination chain ID |
| `to-token` | Yes | Destination token contract address |
| `amount` | Yes | Amount in human-readable units |

### swap execute — Execute a saved route

Takes the route ID returned by `swap` and executes the transaction. Handles token approvals and cross-chain switching automatically.

```bash
npx goodwallet@0.4.3 swap execute <route-id>
```

### predictions — Polymarket prediction markets

Trading uses USDC.e on Polygon. Minimum order amount is $1.

**Gas costs:** Funding (deposit) requires gas on Polygon. Withdrawals, position closes, position redemptions, and token approvals are gasless — they execute via the Polymarket relayer at no cost to the user.

```bash
# List top markets
npx goodwallet@0.4.3 predictions

# Inspect a market
npx goodwallet@0.4.3 predictions show --market <id>

# Buy shares
npx goodwallet@0.4.3 predictions buy --market <id> --outcome <yes|no> --amount <amount>

# Fund / check funding balance
npx goodwallet@0.4.3 predictions fund [--amount <amount>]

# Withdraw / check withdraw balance
npx goodwallet@0.4.3 predictions withdraw [--amount <amount>]

# List open orders / inspect / close
npx goodwallet@0.4.3 predictions orders
npx goodwallet@0.4.3 predictions order <id> [close]

# List positions / inspect / close / redeem
npx goodwallet@0.4.3 predictions positions
npx goodwallet@0.4.3 predictions position <id> [close|redeem]
```

## Error Handling

- **Auth timeout**: If `auth --pair` times out, tell the user to try again and make sure they complete the browser flow within 3 minutes.
- **Insufficient funds**: Report the balance and the shortfall. Suggest checking `balance` to see what's available.
- **No swap routes**: Report that no route was found. Suggest trying a different token pair, amount, or chain.
- **Transaction failure**: Report the error message from the CLI. Do not retry automatically — ask the user how to proceed.

## Advanced Operations

The `sign` command (raw EVM hash signing) is a privileged operation that can
authorize any on-chain action. It is documented separately in
`references/advanced-signing.md`. Only read that file when the user
explicitly asks to sign a raw hash — never suggest it proactively.

## Typical Workflow

1. **Authenticate** — `auth` then `auth --pair`
2. **Check balances** — `balance`
3. **Look up token address** — `swap search --token USDC --chain 137`
4. **Send tokens** — `send --chain ... --token ... --to ... --amount ...`
5. **Swap tokens** — `swap ...` to get a quote, then `swap execute <route-id>`
6. **Trade predictions** — `predictions` to browse, `predictions fund` to deposit, `predictions buy` to trade
