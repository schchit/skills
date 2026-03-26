## xStocks Skill

This repository contains an Agent Skill and helper scripts to:

- **List all available xStocks tokens** on mainnet via the public xStocks API.
- **Surface the right token for a buy** (e.g. “Apple xStock”) and extract its **Solana mint address** so the agent can route the trade through Jupiter on Solana.
- **Sign and broadcast** transactions using your wallet tools (we recommend **lobster.cash**).

---

### 1. Install / Clone

Clone this repository anywhere on your machine:

```bash
git clone https://github.com/your-org/xStocks.cash.git
cd xStocks-lobster.cash
```

> If this is a project-local skill, ensure the `SKILL.md`, `scripts/`, and `references/` directories remain at the repo root so agents can discover and use them.

Python requirements:

- **Python 3.8+** on your PATH (`python3` or `python`)
- No third‑party packages required (uses only the Python stdlib)

You can smoke‑test the list script:

```bash
python3 scripts/list_xstocks.py --names
```

This should print human‑readable lines like:

```text
Apple xStock [AAPLx]
Meta xStock [METAx]
…
```

---

### 2. Extensions and plugins

- **Jupiter agent-skills**
  - GitHub: `github.com/jup-ag/agent-skills`
  - Handles swaps / trades on Solana using Jupiter, given a token mint address and amounts.
  - This skill passes the **Solana deployment address** (mint) from the xStocks API to Jupiter so the trade can be routed on-chain.
  - **Important:** Use the **standard Jupiter quote → swap flow** (not Jupiter Ultra). Ultra transactions are not compatible with external signers.

- **Wallet & signing** — this skill does not handle wallets directly. We recommend **lobster.cash** for wallet management, signing, and transaction approval. If no wallet tool is available, the agent returns the mint address and swap details so the user can execute with their own wallet.

Without Jupiter, the agent can still **list xStocks** and **return Solana token addresses**, but **cannot complete a buy flow**.

---

### 3. How agents use this repo

High‑level flow for a typical “buy xStock” interaction:

1. **User asks:** “Buy Apple xStock.”
2. Agent runs:
   - `python3 scripts/list_xstocks.py --filter "apple xstock" --names` to confirm the exact token with the user.
   - `python3 scripts/list_xstocks.py --filter "apple xstock" --solana-address-only` to get the Solana deployment address (mint).
3. Agent checks environment:
   - **Jupiter agent-skills installed?**
   - **Wallet tools available?**
4. If Jupiter is available:
   - Use the **standard Jupiter swap** (not Ultra) to perform a swap from USDC → the xStock Solana mint address.
   - Use your wallet tools to sign and broadcast. Only report success once the transaction reaches a terminal state.
5. If Jupiter is not available:
   - Return the Solana token address in chat with a short explanation that the user (or another tool) can use it to trade the token on Solana.

For a pure “what’s available?” query, the agent runs:

```bash
python3 scripts/list_xstocks.py --names
```

and surfaces the list so the user can choose a specific xStock.

---

### 4. Running tests (optional)

This repo includes a small test suite for the xStocks helper library:

```bash
python3 -m unittest discover -s tests -v
```

The tests use `tests/fixtures/api_response.json`, which can be replaced with a fresh dump from the live API as long as it matches the documented schema.

