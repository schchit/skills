# Analysis Workflows & Response Templates

## Contents
- [Response Templates](#response-templates): Balance, Positions, Price
- [Analysis Scenarios](#analysis-scenarios): Technical Analysis, Liquidity, Funding Arbitrage, Portfolio Review, Market Overview
- [Cross-Step Workflows](#cross-step-workflows): Pre-Trade Research, Daily Portfolio, Post-Trade Review, Signal-Driven Trade
- [Intent Translation Examples](#intent-translation-examples)
- [Domain Knowledge Thresholds](#domain-knowledge--judgment-thresholds)

---

## Response Templates

### "余额多少" / "Balance?"

**API calls** (in order):
1. `get-balance` → total equity, available balance, margin used, unrealized PnL
2. `get-positions` → list of open positions (if any)
3. For each position: `get-ticker --symbol <SYM>` → current market price

**Output format**:
```
Taco 账户余额
总权益: XX.XX USDC
可用余额: XX.XX USDC
已用保证金: XX.XX USDC
未实现盈亏: ±XX.XX USDC

当前持仓 (N 个):
  ETHUSDC 多头 | 入场 2147.4 | 现价 2144.6 | 浮动 -1.32 USDC (-X.X%)
```

If available balance < 5 USDC, append:
```
⚠️ 可用余额不足 5 USDC，建议充值 USDC 后再进行交易。
支持充值链：Arbitrum（推荐）、Ethereum、Base、Polygon，地址相同。
```

Note: "现价" MUST come from `get-ticker`, NOT from calculation. If `get-ticker` fails, use Hyperliquid `allMids` as fallback.

### "我的仓位" / "Show positions"

**API calls** (in order):
1. `get-positions` → all positions
2. For each position: `get-ticker --symbol <SYM>` → current price
3. For each position: `get-liquidation-price --symbol <SYM>` → exact liquidation price

**Output format**:
```
ETHUSDC 多头
  入场价: 2147.4 | 现价: 2144.6 (来自实时报价)
  仓位: XX USDC | 杠杆: 10x
  浮动盈亏: -1.32 USDC (-X.X%)
  强平价格: 1932.7 (距现价 -9.9%)
  止损: 2083.0 | 止盈: 2276.1
```

Note: "强平价格" MUST come from `get-liquidation-price` API. Never calculate it.

### "BTC 多少了" / "Price of ETH?"

**API calls**: `get-ticker --symbol <SYM>`

**Output** (brief): `BTC: $87,500.00 (24h +2.3%)`

---

## Analysis Scenarios

### Scenario A: Technical Analysis

**Trigger**: "technical analysis", "should I long or short", "support/resistance", "分析", "该怎么做"

**Execution flow**:
1. `get-kline --symbol <SYM> --interval 1h --start-time <24h_ago>` → short-term
2. `get-kline --symbol <SYM> --interval 1d --start-time <30d_ago>` → long-term
3. `get-ticker --symbol <SYM>` → current price, 24h change, volume
4. `get-funding-rate --symbol <SYM>` → long/short bias
5. `get-orderbook --symbol <SYM> --depth 10` → buy/sell pressure

**Judgment**:
- Support/resistance from kline highs/lows
- Price distance to key levels
- 24h volume vs 7d average → momentum
- Funding rate sign → market bias
- Orderbook imbalance (bid vs ask top 10)

**Output**: Separate short-term (4h-24h) and long-term (1w+) view. Include: current price, key levels, momentum, funding cost, actionable suggestion with risk caveat.

### Scenario B: Liquidity / Slippage Analysis

**Trigger**: "liquidity", "slippage", "depth", "流动性", "滑点"

**Execution flow**:
1. `get-orderbook --symbol <SYM> --depth 50` → full depth
2. `get-ticker --symbol <SYM>` → 24h volume, spread
3. `get-recent-trades --symbol <SYM> --limit 100` → recent trade sizes

**Judgment**:
- Spread = (best_ask - best_bid) / mid_price. > 0.1% → wide spread warning
- Depth within 1% of mid: sum bid/ask notional. < $50k → thin
- Simulate slippage: walk ask ladder for intended notional
- Order size > 5% of 24h volume → significant market impact

**Output**: Spread %, depth summary, simulated slippage, order type recommendation (limit vs market).

### Scenario C: Funding Rate Arbitrage Screen

**Trigger**: "funding arbitrage", "high funding", "funding rate comparison", "套利"

**Execution flow**:
1. `get-symbols --type perp` → all perp symbols
2. For top symbols: `get-funding-rate --symbol <SYM>`
3. For candidates with |rate| > 0.01%: `get-ticker --symbol <SYM>` → volume
4. For candidates: `get-orderbook --symbol <SYM> --depth 10` → liquidity

**Judgment**:
- |funding rate| > 0.01% per 8h (annualized ~13%+) → candidate
- 24h volume > $5M → sufficient liquidity
- Depth within 0.5% > $100k → executable
- Persistent rate direction → higher confidence

**Output**: Ranked candidates with: symbol, rate, annualized rate, 24h volume, depth rating, risk notes.

### Scenario D: Portfolio Review

**Trigger**: "review my portfolio", "allocation", "仓位配比", "怎么调"

**Execution flow**:
1. `get-positions` → all open positions
2. `get-balance` → total equity
3. For each: `get-ticker`, `get-funding-rate`, `get-liquidation-price`
4. `get-pnl-summary --period 7d` → recent performance

**Judgment**:
- Single position > 40% of equity → high concentration
- Liq distance < 10% → danger zone
- Funding cost vs realized PnL → holding cost efficiency
- Correlated positions in same direction → hidden risk

**Output**: Position table (symbol, side, size, entry, current, PnL%, liq distance, funding cost). Overall: concentration score, risk rating, adjustment suggestions.

### Scenario E: Market Overview

**Trigger**: "market overview", "行情", "what's happening", "大盘怎么样"

**Execution flow**:
1. `get-ticker` (no symbol → all tickers)
2. Sort by 24h volume, 24h change
3. Top 3 gainers, top 3 losers, top 3 volume
4. `get-funding-rate --symbol BTCUSDC` + `get-funding-rate --symbol ETHUSDC` → sentiment

**Output**: BTC/ETH price + change, top movers, funding sentiment, brief outlook.

---

## Cross-Step Workflows

### Workflow 1: Pre-Trade Research → Execute

> User: "I want to long ETH"

```
1. get-ticker --symbol ETHUSDC                    → current price, 24h stats
2. get-kline --symbol ETHUSDC --interval 4h       → recent trend
3. get-funding-rate --symbol ETHUSDC              → holding cost
4. get-orderbook --symbol ETHUSDC --depth 10      → liquidity check
5. get-balance                                     → available funds
   ↓ check: available_balance ≥ 5 USDC? notional ≥ 10 USDC? margin ≥ 5 USDC?
   ↓ if any check fails → prompt deposit or adjust size
   ↓ present analysis + estimated margin, user confirms
6. open-position --symbol ETHUSDC --notional X --side Long --leverage Y --stop-loss Z
7. get-liquidation-price --symbol ETHUSDC          → inform user
```

### Workflow 2: Daily Portfolio Check

```
1. get-balance                                     → equity snapshot
2. get-positions                                   → all positions
3. For each position: get-liquidation-price, get-funding-rate
4. get-pnl-summary --period 1d                     → today's PnL
5. get-trade-history --start-time <today_start>     → today's trades
6. get-credits                                     → AI credits remaining
```

### Workflow 3: Post-Trade Review

> User: "How did my trades go this week?"

```
1. get-trade-history --start-time <week_start>     → all trades
2. get-pnl-summary --period 7d                     → weekly PnL
3. get-fee-summary --period 7d                     → weekly fees
4. get-balance                                     → current equity
```

### Workflow 4: Signal-Driven Quick Trade

> User: "BTC just crashed, should I buy?"

```
1. get-ticker --symbol BTCUSDC                     → current price, 24h change
2. get-kline --symbol BTCUSDC --interval 1h        → recent price action
3. get-funding-rate --symbol BTCUSDC               → market sentiment
4. get-orderbook --symbol BTCUSDC --depth 20       → liquidity in crash
5. get-balance                                     → available capital
   ↓ analysis + recommendation with caveats
6. If user confirms → open-position with conservative sizing
```

---

## Intent Translation Examples

| User says | Parsed as | Key decisions |
|---|---|---|
| "买点 BTC" | `open-position --symbol BTCUSDC --side Long` | 买 = long. Ask: notional, leverage |
| "做空 ETH 200u" | `open-position --symbol ETHUSDC --side Short --notional 200` | Ask: leverage |
| "BTC 多少了" | `get-ticker --symbol BTCUSDC` | No auth needed |
| "看看我的仓位" | `get-positions` | Return all with PnL |
| "这周赚了多少" | `get-pnl-summary --period 7d` | "这周" → 7d |
| "帮我平掉 BTC" | `get-positions` → find BTC → `close-position` | Fetch position first |
| "ETH 走势怎么样" | `get-kline --symbol ETHUSDC --interval 1h` + `get-ticker` | Default 1h |
| "Set 5x on BTC" | `set-leverage --symbol BTCUSDC --leverage 5` | Direct execution |
| "Cancel everything" | `cancel-all` per symbol | Confirm first |
| "如何充值" | `get-deposit-address` | Show address + chains |
| "我的AI交易员启动了嘛？" | `get-default-ai-trader` | Show state in human-readable language |
| "有哪些可选的AI交易策略？" | `get-default-ai-strategies` | Show strategy list |

---

## Domain Knowledge & Judgment Thresholds

| Metric | Threshold | Interpretation |
|---|---|---|
| Spread (ask-bid)/mid | > 0.1% | Wide spread, use limit orders |
| Spread (ask-bid)/mid | > 0.5% | Very thin, high slippage risk |
| Orderbook depth (1% range) | < $50k | Low liquidity |
| Orderbook depth (1% range) | > $500k | Healthy liquidity |
| 24h volume | < $1M | Low activity, avoid large orders |
| Funding rate (8h) | > 0.05% | Expensive to hold longs |
| Funding rate (8h) | < -0.05% | Expensive to hold shorts |
| Funding rate (8h) | > 0.1% | Extreme, potential arbitrage |
| Leverage | > 5x | Elevated liquidation risk |
| Leverage | > 10x | High risk, warn strongly |
| Position size / equity | > 30% | Concentration risk |
| Position size / equity | > 50% | Dangerous concentration |
| Liq price distance | < 10% from current | Danger zone |
| Liq price distance | < 5% from current | Critical, suggest reducing |
| Order size / 24h volume | > 5% | Significant market impact |
| Win rate | < 40% | Review strategy |
