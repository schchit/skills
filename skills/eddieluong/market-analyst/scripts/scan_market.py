#!/usr/bin/env python3
"""
VN Market Scanner — finds oversold stocks with good fundamentals
Usage: python3 scan_market.py [--rsi 40] [--exchange HOSE] [--limit 20]
"""
import urllib.request, json, sys, argparse

def scan(rsi_threshold=40, exchange="HOSE", limit=20):
    payload = {
        "filter": [
            {"left": "RSI", "operation": "less", "right": rsi_threshold},
            {"left": "exchange", "operation": "equal", "right": exchange},
            {"left": "volume", "operation": "greater", "right": 500000}  # min 500K volume
        ],
        "columns": ["name", "close", "change", "volume", "RSI", "EMA20", "EMA50", "EMA200",
                   "MACD.macd", "MACD.signal", "BB.lower", "price_52_week_high", "price_52_week_low"],
        "sort": {"sortBy": "RSI", "sortOrder": "asc"},
        "range": [0, limit]
    }

    req = urllib.request.Request(
        "https://scanner.tradingview.com/vietnam/scan",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read())

    results = []
    for item in data.get("data", []):
        sym = item["s"].split(":")[1]
        d = item["d"]
        name, close, chg, vol, rsi, ema20, ema50, ema200, macd, macd_sig, bb_low, h52, l52 = d

        # Score system (higher = better buy opportunity)
        score = 0
        signals = []

        if rsi and rsi < 30:
            score += 3
            signals.append("RSI cực oversold")
        elif rsi and rsi < 40:
            score += 2
            signals.append(f"RSI oversold ({rsi:.1f})")

        if close and ema200 and close > ema200:
            score += 2
            signals.append("Trên EMA200 ✓")
        if close and ema50 and close < ema50:
            score += 1
            signals.append("Dưới EMA50 (điều chỉnh)")
        if macd and macd_sig and macd > macd_sig:
            score += 1
            signals.append("MACD bullish")
        if close and bb_low and close <= bb_low * 1.02:
            score += 2
            signals.append("Gần BB Lower")

        pos52 = ((close - l52) / (h52 - l52) * 100) if (h52 and l52 and h52 != l52) else None

        results.append({
            "symbol": sym, "close": close, "change": chg, "volume": vol,
            "rsi": rsi, "ema200": ema200, "score": score,
            "signals": signals, "pos52": pos52
        })

    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)

    print(f"\n🔍 VN Market Scanner — {exchange} | RSI < {rsi_threshold}")
    print(f"{'Mã':<8} {'Giá':>10} {'%':>7} {'RSI':>6} {'Score':>6} {'Vol(M)':>8}  Tín hiệu")
    print("-" * 90)

    for r in results:
        vol_m = f"{r['volume']/1e6:.1f}" if r['volume'] else "N/A"
        pos = f"[52W:{r['pos52']:.0f}%]" if r['pos52'] else ""
        signals_str = ", ".join(r['signals'][:2])
        print(f"{r['symbol']:<8} {r['close']:>10,.0f} {r['change']:>+6.2f}% {r['rsi']:>6.1f} {r['score']:>6}  {vol_m:>6}M  {signals_str} {pos}")

    print(f"\nTổng: {len(results)} cổ phiếu")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VN Market Scanner — tìm cổ phiếu oversold")
    parser.add_argument("--rsi", type=float, default=40, help="RSI threshold (default: 40)")
    parser.add_argument("--exchange", default="HOSE", help="Exchange: HOSE, HNX, UPCOM (default: HOSE)")
    parser.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")
    args = parser.parse_args()
    scan(args.rsi, args.exchange, args.limit)
