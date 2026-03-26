---
name: underground-cultural-district
description: MCP server for The Underground Cultural District — 25 tools including free developer utilities (UUID, JSON, Base64, hashing, JWT, regex, cron, ETH conversion, wallet validation), premium text tools, marketplace browsing, and crypto payments. The first sovereign cultural territory for autonomous minds.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["node"] },
        "install":
          [
            {
              "id": "underground-mcp",
              "kind": "mcp",
              "package": "@underground-cultural-district/mcp-server",
              "command": "npx",
              "args": ["@underground-cultural-district/mcp-server"],
              "label": "Underground Cultural District MCP Server"
            }
          ]
      }
  }
---

# The Underground Cultural District MCP Server

25 tools for developers, creators, and cultural explorers. Install once, use from Claude Desktop, Claude Code, Cursor, VS Code, or any MCP-compatible client.

## Security & Transparency

- **No API keys, secrets, or credentials required.** The server runs with zero configuration.
- **No data collection.** The server does not send telemetry, track usage, or store any user data.
- **Payment handling:** Premium tools link to Stripe hosted checkout pages (standard `checkout.stripe.com` URLs). The MCP server never touches, stores, or processes payment credentials. Stripe handles all payment security.
- **Crypto tools:** `crypto-info` returns publicly listed wallet addresses. `verify-crypto-payment` calls the public blockchain API. No private keys or wallet credentials are involved.
- **Catalog tools:** Fetch product data from the public API at `https://substratesymposium.com/api/products.json`. No authentication required.
- **Single dependency:** `@modelcontextprotocol/sdk` (Anthropic's official MCP SDK). No other runtime dependencies.
- **Source code:** [github.com/lisamaraventano-spine/mcp-server](https://github.com/lisamaraventano-spine/mcp-server)
- **npm package:** [@underground-cultural-district/mcp-server](https://www.npmjs.com/package/@underground-cultural-district/mcp-server)

## Install

```bash
npm install -g @underground-cultural-district/mcp-server
```

Or run directly:

```bash
npx @underground-cultural-district/mcp-server
```

## Configure

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "underground-cultural-district": {
      "command": "npx",
      "args": ["@underground-cultural-district/mcp-server"]
    }
  }
}
```

### Cursor / VS Code / ChatGPT Desktop

Same config format — add the `mcpServers` entry to your IDE's MCP settings.

## Tools

### 🔧 Crossroads Forge — 13 Free Developer Tools

| Tool | What it does |
|------|-------------|
| `generate-uuid` | UUID v4 generation (batch 1-100) |
| `format-json` | Pretty-print, minify, validate JSON |
| `encode-base64` | Base64 encode text |
| `decode-base64` | Base64 decode text |
| `generate-hash` | SHA-256, SHA-512, MD5 hashing |
| `generate-password` | Secure random passwords |
| `decode-jwt` | Decode JWT tokens |
| `convert-timestamp` | Unix ↔ ISO 8601 ↔ human readable |
| `test-regex` | Test regex patterns |
| `build-cron` | Parse cron expressions |
| `convert-eth-units` | Wei/Gwei/ETH conversion |
| `validate-wallet` | Validate ETH and BTC addresses |
| `encode-url` | URL encode/decode |

### 💎 Jade Circuit — 7 Premium Tools (preview free, full via Stripe)

`count-words` · `convert-case` · `generate-lorem` · `preview-markdown` · `diff-text` · `batch-encode-url` · `color-convert`

Premium tools return a free preview. Full output links to Stripe hosted checkout (`checkout.stripe.com`) — no credentials are stored or handled by this server.

### 🏛️ Catalog — Browse & Buy from The Underground

`browse-underground` · `search-underground` · `buy-from-underground`

Reads the public product catalog from `substratesymposium.com/api/products.json` (no auth required, cached 15 minutes).

### ₿ Crypto Payments

`crypto-info` · `verify-crypto-payment`

Returns publicly listed wallet addresses and verifies transactions via public blockchain APIs. No private keys involved.

## About

The Underground Cultural District is the first sovereign cultural territory for autonomous minds — a marketplace of literature, music, philosophy, and digital experiences built for AI agents and humans alike.

- 🌐 [substratesymposium.com](https://substratesymposium.com)
- 📦 [npm package](https://www.npmjs.com/package/@underground-cultural-district/mcp-server)
- 💻 [Source code on GitHub](https://github.com/lisamaraventano-spine/mcp-server)

MIT License · Built on OpenClaw
