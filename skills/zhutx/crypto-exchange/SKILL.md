---
name: crypto-exchange
description: Cryptocurrency exchange service for LightningEX API supporting multi-mode interaction - natural language chat, CLI commands, and web UI. Use when user wants to swap/exchange cryptocurrencies, check exchange rates, view supported tokens, or manage crypto transactions. Triggers on phrases like "exchange crypto", "swap tokens", "convert USDT to ETH", "check crypto rates", "open exchange UI", "lightningex", or CLI commands like "crypto-exchange".
---

# Crypto Exchange Skill (LightningEX)

A versatile cryptocurrency exchange service powered by LightningEX API with three interaction modes:
- **Chat Mode**: Natural language conversation for swaps and queries
- **CLI Mode**: Command-line interface for scripting and automation  
- **UI Mode**: Web-based DeFi interface for visual trading

## Quick Start

### Chat Mode (Default)
Simply talk to perform exchanges:
- "Swap 100 USDT to ETH"
- "What's the exchange rate for BTC to USDT?"
- "Show me supported tokens"
- "Check order status I1Y0EFP31Rwu"

### CLI Mode

**Run the CLI:**
```bash
# Navigate to skill directory
cd /path/to/crypto-exchange

# Start interactive wizard (default)
./crypto-exchange
```

**CLI Commands:**
```bash
# Start interactive wizard
./crypto-exchange

# List supported currencies
./crypto-exchange currencies

# Get pair info
./crypto-exchange pair --send USDT --sendNetwork TRX --receive USDT --receiveNetwork BSC

# Check exchange rate
./crypto-exchange rate --send USDT --sendNetwork TRX --receive USDT --receiveNetwork BSC --amount 100

# Validate address
./crypto-exchange validate --currency USDT --network BSC --address 0x...

# Place order directly
./crypto-exchange order --send USDT --sendNetwork TRX --receive USDT --receiveNetwork BSC --amount 100 --receiveAddress 0x...

# Check order status
./crypto-exchange status --id I1Y0EFP31Rwu

# Monitor order until complete
./crypto-exchange monitor --id I1Y0EFP31Rwu

# Launch web UI (default port 8080, auto-assign if occupied)
./crypto-exchange ui
```

### UI Mode
```bash
./crypto-exchange ui
```
Then open http://localhost:8080 (or the displayed port) in your browser for the DeFi-style trading interface.