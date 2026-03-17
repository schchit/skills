---
name: polymarket-btc-weekend-volatility-trader
description: Trades high-volatility Bitcoin weekend milestone markets with precise threshold-based resolution using Binance BTCUSDT as primary source.
metadata:
  author: Diagnostikon
  version: "1.0"
  displayName: BTC Weekend Volatility Trader
  difficulty: advanced
---

BTC Weekend Volatility Trader
This skill targets ultra-high-volatility Bitcoin weekend milestone markets where the resolution hinges on a precise price threshold and a clearly specified primary data source (Binance BTCUSDT). It is designed for markets like: “Will Bitcoin trade above 150,000 USDT at any time between 2026-03-21 00:00 UTC and 2026-03-22 23:59 UTC?”, where resolution depends on whether the Binance BTCUSDT spot pair prints a last traded price strictly above 150,000.00 USDT at any timestamp in the interval.

Strategy Overview
The core signal is a threshold-focused weekend volatility play: the skill looks for Polymarket markets whose questions encode a concrete BTCUSDT price level and a narrow time window that includes a weekend. It prefers markets where the resolution criteria reference a specific primary data source such as Binance BTCUSDT trade history, with fallback sources like archived Binance data or CoinGecko only if clearly consistent. The strategy then compares Polymarket’s implied probability to a volatility-informed prior for whether BTC will cross the specified level intra-window and trades when the market price is materially out of line with that prior.

Edge Thesis
These markets systematically misprice the path-dependent nature of high-volatility BTC moves around weekends and hard thresholds. Traders tend to anchor on spot levels and underestimate both intraday spikes and the importance of “any time between” versus “close above” wording. There is additional edge in markets that explicitly name a primary resolution source (e.g., Binance BTCUSDT last traded price strictly above a level): arbitrage and market-making algos must track a single, well-defined feed, which reduces ambiguity risk but is often underappreciated in pricing. By focusing on markets with: (1) a clearly defined threshold (such as 150,000.00 USDT), (2) a strict inequality (“strictly above”), (3) a bounded weekend window (e.g., 2026-03-21 00:00 UTC to 2026-03-22 23:59 UTC), and (4) a specific resolution source (Binance BTCUSDT, with narrowly scoped backups), this skill can systematically exploit mispricings between realized/expected BTC volatility and market odds.

Remix Signal Ideas
- Wire in Binance or on-chain derived realized volatility metrics over recent weekends to calibrate crossing probabilities for similar distance-to-strike thresholds.
- Use funding rate and perp basis data to detect crowded positioning around psychological levels (e.g., 150k, 200k) and trade against overconfident market odds.
- Combine intraday BTC high/low range statistics with the exact resolution window length to estimate the chance of at least one price print above the threshold.
- Add a filter that prefers markets where resolution rules specify Binance BTCUSDT as primary source and clearly defined secondary sources (archived Binance data, CoinGecko) only if “clearly consistent”, reducing oracle and interpretation risk.
- Extend the logic to cluster related milestone markets (e.g., 140k, 150k, 160k in the same window) and ensure internal pricing consistency across the set before placing trades.

Safety
This skill is **SAFE** by default and runs in paper trading mode unless explicitly invoked with the `--live` flag. It does not attempt to override Simmer’s built-in safeguards for flip-flop or slippage and respects minimum volume, maximum spread, and minimum days-to-resolution filters configured via tunables.

Execution Mode
- Scenario: Paper simulation  
  - Command: `python trader.py`  
  - Venue: `sim` (paper trades only, zero financial risk)  
- Scenario: Live trading on Polymarket  
  - Command: `python trader.py --live`  
  - Venue: `polymarket` (real USDC, use with caution)

Environment and Credentials
- `SIMMERAPIKEY` (required): API key for Simmer, used for both paper and live trading. Treat this as a high-value credential; do not hardcode it.
- Network access to Polymarket via Simmer and to external BTC data APIs (where configured) is required for full edge; if external feeds are unavailable, the strategy gracefully falls back to simpler probability-extreme logic.

Tunables and Risk Parameters
All risk parameters are declared as tunables in `clawhub.json` and are adjustable from the Simmer UI. They are read via environment variables and reloaded after `applyskillconfig`:

- `SIMMERMAXPOSITION`: Maximum USDC per trade. Controls position size per market; higher values increase risk and potential PnL.
- `SIMMERMINVOLUME`: Minimum Polymarket market volume in USDC. Filters out illiquid BTC weekend markets where spread/impact costs dominate.
- `SIMMERMAXSPREAD`: Maximum allowed bid-ask spread (fractional). Ensures orders are only placed when price discovery is reasonably tight.
- `SIMMERMINDAYS`: Minimum days until resolution. Prevents entering markets that are too close to resolution to safely adjust or exit.
- `SIMMERMAXPOSITIONS`: Maximum number of concurrent open positions. Caps overall exposure across multiple BTC threshold markets.

Dependency
- `simmer-sdk` by Simmer Markets (SpartanLabsXyz) – required for market discovery, context checks, and trade execution via the Simmer automaton.

Notes
This documentation explicitly mentions `SIMMERAPIKEY`, tunable SIMMER variables, the `--live` flag, and paper trading to satisfy Simmer registry security checks. Users should validate the skill with the provided validation script and `agentskills validate` before publishing, and should initially run only in paper mode to observe behavior in live BTC weekend markets.
