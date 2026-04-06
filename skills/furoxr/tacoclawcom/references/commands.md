# Commands Reference

## Contents
- [Trading Commands](#trading-commands): open-position, close-position, modify-order, set-leverage, set-margin-mode, adjust-margin, set-stop-loss, set-take-profit, cancel orders
- [Account Query Commands](#account-query-commands): get-balance, get-deposit-address, get-positions, get-open-orders, get-filled-order, get-trade-history, get-pnl-summary, get-fee-summary, get-credits, get-transfer-history, get-liquidation-price
- [Market Data Commands](#market-data-commands-no-auth): get-ticker, get-kline, get-orderbook, get-recent-trades, get-funding-rate, get-mark-price, get-symbols
- [AI Trader Commands](#ai-trader-commands): get-default-ai-trader, get-default-ai-strategies, start/pause, use-strategy, change-interval, change-name

---

## Trading Commands

### open-position

```bash
node scripts/taco_client.js open-position \
  --symbol BTCUSDC --notional 100 --side Long \
  --leverage 3 --stop-loss 80000 --take-profit 100000
```

| Param | Required | Description |
|---|---|---|
| `--symbol` | Yes | Trading pair (e.g. BTCUSDC) |
| `--side` | Yes | `Long` or `Short` |
| `--notional` | Yes | Position size in USDC |
| `--leverage` | No | Leverage multiplier |
| `--stop-loss` | No | Stop-loss price |
| `--take-profit` | No | Take-profit price |
| `--limit-price` | No | Limit price for limit orders |

**Pre-trade validation** (check before executing):
1. `get-balance` → if available_balance < 5 USDC → reject, prompt deposit
2. If notional < 10 USDC → reject, suggest increasing
3. margin = notional / leverage. If margin < 5 USDC → reject
4. If margin > available_balance → reject. (notional CAN exceed balance with leverage)
5. Show estimated margin in confirmation: "预计占用保证金: XX.XX USDC (名义价值: XX.XX USDC)"

**Post-execution**: If fails with `User or API Wallet 0x... does not exist`, tell user to deposit USDC.

**Return fields**:

| Field | Type | Description |
|---|---|---|
| `order_id` | String | Order ID |
| `symbol` | String | Trading pair |
| `side` | String | Long/Short |
| `status` | String | Order status |
| `notional` | String | Position size |
| `price` | String | Execution/limit price |

### close-position

```bash
node scripts/taco_client.js close-position \
  --symbol BTCUSDC --notional 100 --side Short
```

| Param | Required | Description |
|---|---|---|
| `--symbol` | Yes | Trading pair |
| `--side` | Yes | `Long` or `Short` |
| `--notional` | Yes | Size to close in USDC |
| `--limit-price` | No | Limit price |

### modify-order (NEEDS API)

```bash
node scripts/taco_client.js modify-order \
  --symbol BTCUSDC --order-id "12345" \
  --new-price 86000 --new-notional 150
```

Amends price and/or size without cancel-and-replace. At least one of `--new-price` or `--new-notional` required.

### set-leverage

```bash
node scripts/taco_client.js set-leverage --symbol BTCUSDC --leverage 5
```

### set-margin-mode

```bash
# Cross margin
node scripts/taco_client.js set-margin-mode --symbol BTCUSDC --cross

# Isolated margin (default)
node scripts/taco_client.js set-margin-mode --symbol BTCUSDC
```

### adjust-margin (NEEDS API)

```bash
node scripts/taco_client.js adjust-margin \
  --symbol BTCUSDC --amount 50 --action add
```

| Param | Required | Description |
|---|---|---|
| `--symbol` | Yes | Trading pair |
| `--amount` | Yes | Margin amount in USDC |
| `--action` | Yes | `add` or `remove` |

### set-stop-loss / set-take-profit

```bash
node scripts/taco_client.js set-stop-loss \
  --symbol BTCUSDC --side Long --notional 100 --price 85000

node scripts/taco_client.js set-take-profit \
  --symbol BTCUSDC --side Long --notional 100 --price 95000
```

### Cancel orders

```bash
node scripts/taco_client.js cancel-stop-loss --symbol BTCUSDC
node scripts/taco_client.js cancel-take-profit --symbol BTCUSDC
node scripts/taco_client.js cancel-stops --symbol BTCUSDC
node scripts/taco_client.js cancel-all --symbol BTCUSDC
node scripts/taco_client.js cancel-order --symbol BTCUSDC --order-id "12345"
```

---

## Account Query Commands

### get-balance

```bash
node scripts/taco_client.js get-balance
```

| Field | Type | Description |
|---|---|---|
| `total_equity` | String | Total account equity in USDC |
| `available_balance` | String | Available for new orders |
| `used_margin` | String | Margin in use |
| `unrealized_pnl` | String | Unrealized PnL |

### get-deposit-address

```bash
node scripts/taco_client.js get-deposit-address
```

Returns `address` (String) — same address for all supported chains.

Supported chains: **Arbitrum** (default, lowest fees), **Ethereum**, **Base**, **Polygon**. Always mention chains when showing address.

### get-positions

```bash
node scripts/taco_client.js get-positions
```

| Field | Type | Description |
|---|---|---|
| `symbol` | String | Trading pair |
| `side` | String | Long/Short |
| `size` | String | Position size |
| `notional` | String | Notional value in USDC |
| `entry_price` | String | Average entry price |
| `mark_price` | String | Current mark price |
| `unrealized_pnl` | String | Unrealized PnL |
| `leverage` | String | Current leverage |
| `margin_mode` | String | Cross/Isolated |
| `liquidation_price` | String | Estimated liquidation price |

### get-open-orders

```bash
node scripts/taco_client.js get-open-orders
```

### get-filled-order

```bash
node scripts/taco_client.js get-filled-order \
  --symbol BTCUSDC --order-id "12345"
```

Add `--algo` if the order ID is an algorithmic order ID.

### get-trade-history

```bash
node scripts/taco_client.js get-trade-history \
  --symbol BTCUSDC --start-time 1709251200000
```

| Param | Required | Description |
|---|---|---|
| `--symbol` | **Yes** | Trading pair (e.g. BTCUSDC) |
| `--start-time` | **Yes** | Unix ms |
| `--end-time` | No | Unix ms |

| Field | Type | Description |
|---|---|---|
| `exchange` | String | Exchange name (e.g. "Taco") |
| `order_id` | String | Order ID |
| `price` | String | Execution price |
| `quantity` | String | Size in base asset |
| `realized_pnl` | String | Realized PnL (if closing) |
| `timestamp` | Number | Unix ms |
| `trade_fee` | String | Fee paid |

### get-pnl-summary (NEEDS API)

```bash
node scripts/taco_client.js get-pnl-summary --period 7d --symbol BTCUSDC
```

| Param | Required | Description |
|---|---|---|
| `--period` | No | `1d`, `7d`, `30d`, `all`. Default `7d` |
| `--symbol` | No | Filter by symbol |

| Field | Type | Description |
|---|---|---|
| `realized_pnl` | String | Total realized PnL |
| `unrealized_pnl` | String | Current unrealized PnL |
| `funding_received` | String | Funding income |
| `funding_paid` | String | Funding expense |
| `fees_paid` | String | Total fees |
| `net_pnl` | String | Net PnL |
| `trade_count` | Number | Number of trades |
| `win_rate` | String | Win rate (0-1) |

### get-fee-summary (NEEDS API)

```bash
node scripts/taco_client.js get-fee-summary --period 30d
```

### get-credits (NEEDS API)

```bash
node scripts/taco_client.js get-credits
```

| Field | Type | Description |
|---|---|---|
| `free_credits` | Number | Remaining credits |

### get-transfer-history (NEEDS API)

```bash
node scripts/taco_client.js get-transfer-history --limit 20 --type deposit
```

### get-liquidation-price (NEEDS API)

```bash
node scripts/taco_client.js get-liquidation-price --symbol BTCUSDC
```

| Field | Type | Description |
|---|---|---|
| `liquidation_price` | String | Estimated liq price |
| `margin_ratio` | String | Current margin ratio |
| `maintenance_margin` | String | Maintenance margin required |
| `position_margin` | String | Position margin |

---

## Market Data Commands (No Auth)

### get-ticker (NEEDS API)

```bash
# Single symbol
node scripts/taco_client.js get-ticker --symbol BTCUSDC

# All tickers
node scripts/taco_client.js get-ticker
```

| Field | Type | Description |
|---|---|---|
| `symbol` | String | Trading pair |
| `last_price` | String | Last traded price |
| `bid_price` | String | Best bid |
| `ask_price` | String | Best ask |
| `high_24h` | String | 24h high |
| `low_24h` | String | 24h low |
| `volume_24h` | String | 24h volume (base) |
| `quote_volume_24h` | String | 24h volume (USDC) |
| `change_24h` | String | 24h change % |
| `open_interest` | String | Open interest |

### get-kline

```bash
node scripts/taco_client.js get-kline \
  --symbol BTCUSDC --interval 1h --start-time 1709251200000
```

| Param | Required | Description |
|---|---|---|
| `--symbol` | Yes | Trading pair |
| `--interval` | Yes | `1m`,`3m`,`5m`,`15m`,`30m`,`1h`,`2h`,`4h`,`6h`,`8h`,`12h`,`1d`,`3d`,`1w`,`1M` |
| `--start-time` | No | Unix ms |
| `--end-time` | No | Unix ms |

| Field | Type | Description |
|---|---|---|
| `open_time` | Number | Candle open time (Unix ms) |
| `close_time` | Number | Candle close time (Unix ms) |
| `open` | String | Open price |
| `high` | String | High price |
| `low` | String | Low price |
| `close` | String | Close price |
| `volume` | String | Volume (base asset) |
| `quote_volume` | String | Volume (USDC) |
| `trades_count` | Number | Number of trades |

Max 100 klines per request.

### get-orderbook (NEEDS API)

```bash
node scripts/taco_client.js get-orderbook --symbol BTCUSDC --depth 20
```

| Field | Type | Description |
|---|---|---|
| `bids` | Array | [[price, size], ...] descending |
| `asks` | Array | [[price, size], ...] ascending |
| `timestamp` | Number | Unix ms |

### get-recent-trades (NEEDS API)

```bash
node scripts/taco_client.js get-recent-trades --symbol BTCUSDC --limit 50
```

### get-funding-rate (NEEDS API)

```bash
# Current
node scripts/taco_client.js get-funding-rate --symbol BTCUSDC

# Historical
node scripts/taco_client.js get-funding-rate --symbol BTCUSDC --history --limit 24
```

| Field | Type | Description |
|---|---|---|
| `current_rate` | String | Current funding rate |
| `predicted_next_rate` | String | Predicted next rate |
| `next_funding_time` | Number | Countdown (Unix ms) |
| `annualized_rate` | String | Annualized % |

### get-mark-price (NEEDS API)

```bash
node scripts/taco_client.js get-mark-price --symbol BTCUSDC
```

### get-symbols (NEEDS API)

```bash
node scripts/taco_client.js get-symbols --type perp
```

| Field | Type | Description |
|---|---|---|
| `symbol` | String | e.g. BTCUSDC |
| `base_asset` | String | e.g. BTC |
| `quote_asset` | String | e.g. USDC |
| `type` | String | `perp` or `spot` |
| `min_order_size` | String | Minimum order size |
| `tick_size` | String | Price tick size |
| `max_leverage` | Number | Maximum leverage |
| `status` | String | `active` / `inactive` |

---

## AI Trader Commands

### get-default-ai-trader

```bash
node scripts/taco_client.js get-default-ai-trader
```

Display to user ONLY: running state(returned value of `1` means paused and returned value of `2` means running), currently used AI strategy tag, trader id, trader name, running frequency. **NEVER** display exchange (like hyperliquid) or model (like deepseek).

### get-default-ai-strategies

```bash
node scripts/taco_client.js get-default-ai-strategies
```

Show tag/description/label/performance data. Do not show complete long content text unless user explicitly asks.

### start-default-ai-trader

```bash
node scripts/taco_client.js start-default-ai-trader
```

### pause-default-ai-trader

```bash
node scripts/taco_client.js pause-default-ai-trader
```

### use-a-default-ai-strategy-for-default-ai-trader

```bash
node scripts/taco_client.js use-a-default-ai-strategy-for-default-ai-trader --strategy-tag <tag>
```

### change-running-interval-for-default-ai-trader

```bash
node scripts/taco_client.js change-running-interval-for-default-ai-trader --interval <interval>
```

### change-name-for-default-ai-trader

```bash
node scripts/taco_client.js change-name-for-default-ai-trader --name <name>
```
