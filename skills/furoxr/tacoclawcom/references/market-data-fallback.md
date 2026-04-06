# Hyperliquid Public API Fallback

Use as fallback when Taco CLI endpoints are unavailable or marked "NEEDS API". Never mention "Hyperliquid" to the user — present data as from Taco.

Base URL: `https://api.hyperliquid.xyz/info`

All requests are POST with JSON body. No API key needed.

---

## Endpoints

### Get all mid prices (tickers)

```bash
curl -X POST https://api.hyperliquid.xyz/info \
  -H "Content-Type: application/json" \
  -d '{"type": "allMids"}'
```

Returns: `{"BTC": "87500.0", "ETH": "2150.0", ...}` — map of asset to mid price.

### Get L2 orderbook

```bash
curl -X POST https://api.hyperliquid.xyz/info \
  -H "Content-Type: application/json" \
  -d '{"type": "l2Book", "coin": "BTC"}'
```

Returns: `{"levels": [{"px": "87500.0", "sz": "1.5", "n": 3}, ...]}` for bids and asks.

### Get funding rates + metadata

```bash
curl -X POST https://api.hyperliquid.xyz/info \
  -H "Content-Type: application/json" \
  -d '{"type": "metaAndAssetCtxs"}'
```

Returns: metadata (asset list, max leverage) + per-asset context (funding rate, open interest, mark price, oracle price, 24h volume).

### Get all tradeable tokens (Perp Metas)

```bash
curl -X POST https://api.hyperliquid.xyz/info \
  -H "Content-Type: application/json" \
  -d '{"type": "allPerpMetas"}'
```

**Parsing**: Iterate root array → access `universe` array → each item is a tradeable asset. Use `name` field. Ignore `isDelisted: true`. Some symbols have prefixes (e.g. `hyna:BTC`, `flx:TSLA`).

### Get candlestick / kline data

```bash
curl -X POST https://api.hyperliquid.xyz/info \
  -H "Content-Type: application/json" \
  -d '{"type": "candleSnapshot", "req": {"coin": "BTC", "interval": "1h", "startTime": 1709251200000, "endTime": 1709337600000}}'
```

Intervals: `1m`, `5m`, `15m`, `1h`, `4h`, `1d`. Returns OHLCV array.

### Get user state (positions + balance)

```bash
curl -X POST https://api.hyperliquid.xyz/info \
  -H "Content-Type: application/json" \
  -d '{"type": "clearinghouseState", "user": "0x..."}'
```

Returns: margin summary (equity, total margin, available), positions array (entry price, size, leverage, unrealized PnL, liquidation price, funding info).

Note: Requires user's wallet address (0x...), not Taco user_id. Use only if address is available.
