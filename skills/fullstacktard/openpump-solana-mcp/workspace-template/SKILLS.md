# SKILLS -- Skill References

This workspace uses the following ClawHub skills for its MCP tool capabilities.

## openpump-solana-mcp

**Source:** `clawhub://openpump-solana-mcp`

Solana token launch and trading tools via the OpenPump MCP server. Provides 23 tools covering:

- Token creation on pump.fun
- Buying and selling tokens (single wallet and multi-wallet bundles)
- SOL and SPL token transfers
- Wallet creation and management
- Token analytics and risk metrics (snipers, bundlers, insiders)
- Price quotes and bonding curve state
- Creator fee management
- Jito MEV bundle operations and tip level monitoring
- Async job polling for long-running operations

### Requirements

| Requirement | Details |
|-------------|---------|
| Runtime | Node.js (via `npx`) |
| Environment | `OPENPUMP_API_KEY` must be set |
| Network | Outbound access to `api.openpump.io` and `mcp.openpump.io` |
| Package | `@openpump/mcp-server` (auto-installed via npx) |

### API Key

Obtain your API key from [openpump.io](https://openpump.io):

1. Sign up or log in
2. Navigate to Dashboard > API Keys
3. Create a new key (starts with `op_sk_live_`)

Set it as an environment variable:

```bash
export OPENPUMP_API_KEY="op_sk_live_YOUR_KEY_HERE"
```

Or add it to your `~/.openclaw/.env` file so it persists across sessions.

### Tool Categories

| Category | Tools | Description |
|----------|-------|-------------|
| Token Creation | 1 | `create-token` |
| Trading | 6 | `buy-token`, `sell-token`, `bundle-buy`, `bundle-sell`, `estimate-bundle-cost`, `claim-creator-fees` |
| Transfers | 2 | `transfer-sol`, `transfer-token` |
| Wallet Management | 4 | `create-wallet`, `get-aggregate-balance`, `get-wallet-deposit-address`, `get-wallet-transactions` |
| Information | 9 | `get-token-info`, `get-token-market-info`, `list-my-tokens`, `get-token-holdings`, `get-wallet-balance`, `list-wallets`, `get-creator-fees`, `get-token-quote`, `get-jito-tip-levels` |
| Job Polling | 1 | `poll-job` |

See `TOOLS.md` for detailed parameter documentation for each tool.
