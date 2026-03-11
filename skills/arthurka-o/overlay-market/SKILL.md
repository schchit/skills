---
name: overlay-market
description: Trade leveraged perpetual futures on Overlay Protocol (BSC). Scan markets, analyze prices with technical indicators, check wallet balance, encode build/unwind transactions, and monitor positions with PnL. Use when the user wants to trade on Overlay, analyze Overlay markets, or manage Overlay positions.
compatibility: Requires Node.js 18+. Run `npm install` in the skill directory. Requires network access to BSC RPC and Overlay APIs.
metadata:
  author: overlay-market
  version: "0.1.1"
  chain: bsc
  chain-id: "56"
env:
  OVERLAY_PRIVATE_KEY:
    required: false
    description: Private key for signing transactions (needed for send.js and --dry-run)
  BSC_RPC_URL:
    required: false
    description: BSC RPC endpoint (defaults to bsc-dataseed.binance.org)
---

# Overlay Market

Trade leveraged perpetual futures on 30+ markets (crypto, commodities, indices, social metrics) on BSC.

Overlay markets are synthetic — you trade against a protocol-managed price feed, not an order book. Positions are opened with USDT collateral.

## Transaction signing

This skill produces **unsigned transaction objects** (JSON with `to`, `data`, `value`, `chainId`). Your agent needs a way to sign and broadcast on BSC (chainId 56). A bundled `send.js` script is provided for simple private-key signing, but any signer works.

The recommended setup is a smart contract account with restricted permissions (e.g. Safe + Zodiac Roles), so the agent can only call approved functions. A raw private key in `.env` is provided as a quick-start option for testing.

## Configuration

The `.env` file in the skill root is loaded automatically by all scripts:

```
OVERLAY_PRIVATE_KEY=0xabc...   # optional, needed for send.js and dry-run
BSC_RPC_URL=https://...        # optional, defaults to bsc-dataseed.binance.org
```

`OVERLAY_PRIVATE_KEY` is only required for `send.js` and `--dry-run` simulation. If your agent already has a way to sign and broadcast transactions, you can skip `send.js` entirely and use the unsigned tx JSON output from `build.js`/`unwind.js` directly. Use `--owner <address>` with `unwind.js` instead of relying on the private key.

## External Services

The scripts contact these external endpoints:

- **Overlay APIs** (`api.overlay.market`):
  - `/data/api/markets` — market catalog
  - `/bsc-charts/v1/charts` — OHLC candle data
  - `/bsc-charts/v1/charts/marketsPricesOverview` — current prices & changes
- **Goldsky Subgraph** (`api.goldsky.com`): GraphQL endpoint for position data
- **1inch Proxy** (`1inch-proxy.overlay-market-account.workers.dev`): Cloudflare Workers proxy for OVL→USDT swap quotes (used by `unwind.js`)
- **BSC RPC** (`bsc-dataseed.binance.org` or custom via `BSC_RPC_URL`): on-chain reads and transaction broadcast

## Scripts

### balance.js — Wallet USDT and BNB balance

`node scripts/balance.js [address]`

### scan.js — All markets with prices and 1h/24h/7d changes

`node scripts/scan.js [--details <market>]`

`--details <market>` shows the full description for a specific market (what it tracks, data sources, methodology).

### chart.js — OHLC candles + SMA(20), RSI(14), ATR(14)

```bash
node scripts/chart.js <market> [timeframe] [candles]
```

- `market` — name (e.g. `BTC/USD`, `SOL`, `GOLD/SILVER`) or contract address. Partial matching works.
- `timeframe` — `5m`, `15m`, `30m`, `1h`, `4h`, `12h`, `1d` (default: `1h`)
- `candles` — number of candles (default: `48`)

### build.js — Encode a buildStable transaction (open position)

```bash
node scripts/build.js <market> <long|short> <collateral_usdt> <leverage> [--slippage <pct>] [--dry-run]
```

Fetches the current mid price from the state contract and sets a price limit with slippage tolerance (default: 1%). The transaction will revert on-chain if the execution price exceeds the limit.

`--dry-run` checks USDT balance, allowance, and simulates the transaction without outputting it. Shows notional size, entry price estimate, and whether the tx would succeed. Note: simulations run against the current block — the actual transaction executes in a later block, so values (price, PnL, received amounts) may differ slightly.

### unwind.js — Encode an unwindStable transaction (close position)

```bash
node scripts/unwind.js <market> <position_id> --direction <long|short> [--owner <addr>] [--slippage <pct>] [--dry-run]
```

`--direction` is required — it sets the correct price limit. Map from positions output: `isLong: true` → `--direction long`, `isLong: false` → `--direction short`. Always unwinds 100%. Same slippage protection as build (default: 1%).

`--dry-run` shows current value, PnL, trading fee, expected USDT to receive, and simulates the transaction.

### send.js — Sign and broadcast an unsigned transaction

Reads unsigned tx JSON from stdin or CLI argument, signs with `OVERLAY_PRIVATE_KEY`, broadcasts to BSC, and waits for confirmation. Returns `{"hash", "status", "blockNumber", "gasUsed"}`.

### positions.js — Open positions with PnL

`node scripts/positions.js [owner_address]`

Returns JSON with positions (positionId, market, isLong, leverage, collateralUSDT, valueUSDT, pnlUSDT, pnlPercent) and a summary.

## Workflow

Build and unwind output JSON to stdout and human info to stderr, so they pipe into send:

```bash
# Research
node scripts/balance.js
node scripts/scan.js
node scripts/scan.js --details "BTC/USD"
node scripts/chart.js BTC/USD 4h

# Dry-run before opening
node scripts/build.js BTC/USD long 5 3 --dry-run

# Open: 5 USDT long BTC 3x
node scripts/build.js BTC/USD long 5 3 2>/dev/null | node scripts/send.js

# Monitor
node scripts/positions.js

# Dry-run before closing
node scripts/unwind.js BTC/USD 0xce --direction long --dry-run

# Close (positionId and direction from positions output)
node scripts/unwind.js BTC/USD 0xce --direction long 2>/dev/null | node scripts/send.js

# Without OVERLAY_PRIVATE_KEY (external signer)
node scripts/unwind.js BTC/USD 0xce --direction long --owner 0x1234...
```

## Contracts (BSC Mainnet)

- **Shiva** (trading): `0xeB497c228F130BD91E7F13f81c312243961d894A`
- **OverlayV1State** (reads): `0x10575a9C8F36F9F42D7DB71Ef179eD9BEf8Df238`

## Resources

- App: https://app.overlay.market
- Docs: https://docs.overlay.market
