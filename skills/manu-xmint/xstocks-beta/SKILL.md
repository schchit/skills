---
name: xstocks
description: Search engine for xStocks tokens on Solana mainnet. Discovers available xStocks, resolves mints, and lists wallet holdings. For price discovery and trading, combine with Jupiter. Use when the user wants to find or identify xStocks.
compatibility: Python 3.8+ for scripts. Network access. Optional: Jupiter agent-skills (github.com/jup-ag/agent-skills) for swaps, lobster.cash for wallet/signing.
---

# xStocks

This skill is a **search engine** for xStocks tokens on Solana mainnet — it discovers, lists, filters, and resolves xStock tokens and wallet holdings. It does **not** provide pricing or trading on its own.

For **price discovery**, use the **Jupiter extension** ([github.com/jup-ag/agent-skills](https://github.com/jup-ag/agent-skills)) with the Solana mint address obtained from this skill.

**Important workflow:** After running any script from this skill, always:
1. **Analyze the output** for missing or incomplete information (e.g. tokens without a Solana deployment, empty results, unknown mints).
2. **Check if the user has other extensions** (Jupiter, lobster.cash, etc.) that can enrich the results — for example, fetching live prices, executing swaps, or checking balances — and offer to combine them.

## Prerequisites

- Python 3.8+.
- **Jupiter agent-skills** — [github.com/jup-ag/agent-skills](https://github.com/jup-ag/agent-skills) — for swaps and price discovery.
- **Wallet & signing** — this skill does not handle wallets directly. We recommend **lobster.cash** for wallet management, signing, and transaction approval. If no wallet tool is available, return the mint address and swap details so the user can execute with their own wallet.

## List available xStocks

To list all xStocks tokens with a **Solana deployment** on mainnet, run the list script from the skill root:

```bash
python3 scripts/list_xstocks.py
```

Or with explicit Python:

```bash
python scripts/list_xstocks.py
```

- **Default output:** JSON array of all **Solana xStocks** (filtered from the full catalog). Written to stdout; logs go to stderr.
- **Options:**
  - `--compact` — single-line JSON for piping.
  - `--names` — one line per token: `Name [SYMBOL]`.
  - `--filter "TEXT"` — only tokens whose `name` or `symbol` contains `TEXT` (case-insensitive).
  - `--solana-address-only` — with `--filter`, print only Solana deployment addresses (one per line).
  - `--lookup-address MINT` — given a Solana mint address, print the matching xStock name/symbol (uses `/tmp/xstocks.json` cache, refreshes on miss).
  - `--debug` — emit structured logs to stderr. **Use this flag when a command fails or returns unexpected results** to see what the script is doing internally.

The script uses `/tmp/xstocks.json` as a cache of the xStocks catalog and only refreshes it from the API when needed. See [references/api.md](references/api.md) for the token response schema.

### Typical flows

- **Show user all tradable xStocks:**  
  Run `python3 scripts/list_xstocks.py --names` and present the list (`Name [SYMBOL]`) so they can pick what to buy.

- **User says “buy apple xstock”:**
  1. Use `python3 scripts/list_xstocks.py --filter "apple xstock" --names` to confirm the exact token with the user.
  2. Then run `python3 scripts/list_xstocks.py --filter "apple xstock" --solana-address-only` to get the Solana deployment address (if any).
  3. If **Jupiter agent-skills** is available, use that address with the Jupiter skill to perform the swap/buy on Solana using USDC.
  4. If Jupiter is not available, return the Solana token address in chat and explain that the user (or another tool) can use it for trading.

### Lookup by mint address

When you already know a Solana mint and want to recover the corresponding xStock:

```bash
python3 scripts/list_xstocks.py --lookup-address svm:MintAddressHere
```

- By default this prints `Name [SYMBOL] (mint: ...)`.
- With `--compact`, it prints a single JSON object: `{ "mint", "name", "symbol", "id" }`.
- The script uses `/tmp/xstocks.json` as a cache of the xStocks catalog and only refreshes it from the API if the mint is not found in the cached data.

This is useful when resolving a portfolio of SPL token mints into human-readable xStocks.

## List xStocks held by a wallet

To see which xStocks a given Solana wallet holds:

```bash
python3 scripts/wallet_tokens.py <WALLET_PUBKEY>
```

- **Default output:** JSON array of entries:
  - `wallet` — wallet public key
  - `mint` — SPL token mint address
  - `amount` — UI amount of tokens (float)
  - `name` / `symbol` — xStock metadata (only known xStocks are included; non-xStock mints are filtered out)
- **Options:**
  - `--names` — human-readable lines: `Name [SYMBOL] — amount (mint: ...)`, falling back to `mint — amount (unknown xStock)` when no match is found.
  - `--debug` — emit structured logs to stderr.

`wallet_tokens.py` uses Solana mainnet RPC (`getParsedTokenAccountsByOwner`) to discover SPL token accounts and the same `/tmp/xstocks.json` cache (refreshing from the API when it encounters an unknown mint) to attach xStock metadata.

## Buy xStocks

1. **Resolve the mint** — Use this skill's scripts to get the Solana mint address for the xStock.
2. **Confirm with the user** — Echo amount, token (e.g. which xStock), and any recipient or destination before creating or approving a transaction.
3. **Build the swap** — Use the **standard Jupiter quote → swap flow** (`jupiter_swap` tool, or `/quote` + `/swap` REST endpoints). **Do NOT use Jupiter Ultra** (`/ultra/...` endpoints) — Ultra transactions are not compatible with external signers.
4. **Sign and broadcast** — Use your available wallet and signing tools (we recommend lobster.cash) to sign and broadcast the transaction. If no wallet tool is configured, return the serialized transaction to the user for signing with their own wallet.
5. **Report outcome** — Only claim success when transaction status is `success` or `completed`. Share transaction ID, status, and explorer link when available.

Default to **USDC** for payments. Never claim money moved unless the transaction has reached a successful terminal state.

## Tool selection (quick reference)

| User intent              | Action                                                                 |
| ------------------------ | ---------------------------------------------------------------------- |
| List xStocks on mainnet  | Run `python3 scripts/list_xstocks.py` (optionally `--compact`)          |
| Buy xStock               | Resolve mint → **Jupiter standard swap** (not Ultra) → sign & broadcast with your wallet tools |
| Check balance            | Use your wallet tools, or `wallet_tokens.py` for xStock holdings       |
| Wallet setup             | Use your wallet tools to configure a wallet before transacting         |

## Error handling

- **Script fails (e.g. connection error):** Re-run the command with `--debug` to inspect structured logs on stderr. Check network; retry. If the API URL or pagination format changed, see [references/api.md](references/api.md).
- **"Wallet not configured" / "No wallet found":** User must set up a wallet with their wallet tools before transacting.
- **Transaction timeout or pending:** Use your wallet tools to check transaction status until it reaches a terminal state.

## References

- [Token list API and schema](references/api.md) — `GET https://api.xstocks.fi/api/v1/token`, response shape, pagination.
