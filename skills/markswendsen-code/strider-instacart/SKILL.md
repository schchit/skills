---
name: strider-instacart
description: Give AI agents the ability to search products, manage cart, and place grocery orders on Instacart via the Strider Labs MCP connector.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "commerce"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Instacart Connector

MCP server that gives AI agents the ability to search products, manage cart, and place grocery orders on Instacart.

Built by [Strider Labs](https://striderlabs.ai) — building the action layer for AI agents.

## Features

- 🔍 **Search Products** — Find products across Instacart with prices and availability
- 🛒 **Cart Management** — Add items, view cart, clear cart
- 📦 **Place Orders** — Preview and place orders with delivery time selection
- 🔐 **Session Persistence** — Cookies saved locally for seamless re-authentication
- 🛡️ **Order Safety** — Requires explicit confirmation before placing orders

## Installation

```bash
npm install @striderlabs/mcp-instacart
```

### Prerequisites

This package requires Playwright browsers:

```bash
npx playwright install chromium
```

## MCP Configuration

Add to your Claude Desktop or MCP client config:

```json
{
  "mcpServers": {
    "instacart": {
      "command": "npx",
      "args": ["@striderlabs/mcp-instacart"]
    }
  }
}
```

## Available Tools

### Authentication

| Tool | Description |
|------|-------------|
| `instacart_status` | Check login status and session info |
| `instacart_login` | Initiate login flow (returns URL for manual login) |
| `instacart_logout` | Clear saved session and cookies |

### Shopping

| Tool | Description |
|------|-------------|
| `instacart_search` | Search for products by name |
| `instacart_stores` | List available stores for delivery location |
| `instacart_set_address` | Set delivery address or zip code |

### Cart

| Tool | Description |
|------|-------------|
| `instacart_add_to_cart` | Add a product to cart |
| `instacart_view_cart` | View cart contents and totals |
| `instacart_clear_cart` | Remove all items from cart |

### Orders

| Tool | Description |
|------|-------------|
| `instacart_preview_order` | Preview order before placing |
| `instacart_place_order` | Place order (requires `confirm=true`) |

## Usage Examples

### Search for Products

```
User: Find organic bananas on Instacart
Agent: [calls instacart_search with query="organic bananas"]
→ Returns list of products with prices and availability
```

### Build a Shopping List

```
User: Add milk, eggs, and bread to my Instacart cart
Agent: 
  [calls instacart_add_to_cart with product="milk"]
  [calls instacart_add_to_cart with product="eggs"]
  [calls instacart_add_to_cart with product="bread"]
→ Items added to cart with confirmation
```

### View Cart and Place Order

```
User: What's in my cart and how much is it?
Agent: [calls instacart_view_cart]
→ Returns items, quantities, subtotal, fees, total

User: Place the order
Agent: [calls instacart_place_order with confirm=false]
→ Returns preview for confirmation
User: Yes, confirm it
Agent: [calls instacart_place_order with confirm=true]
→ Order placed successfully
```

## Authentication Flow

Instacart requires browser-based login:

1. Call `instacart_login` — returns a login URL
2. User opens URL and logs in manually
3. Cookies are automatically saved to `~/.strider/instacart/`
4. Future sessions use saved cookies until they expire

## Order Safety

The `instacart_place_order` tool has a built-in safety mechanism:

- Without `confirm=true`: Returns a preview, does not place order
- With `confirm=true`: Actually places the order

Agents should ALWAYS show the preview and get explicit user confirmation before calling with `confirm=true`.

## Error Handling

| Error | Solution |
|-------|----------|
| "Not logged in" | Run `instacart_login` and complete login |
| Timeout errors | Retry after a moment |
| CAPTCHA challenges | Complete CAPTCHA in browser, then retry |
| "Could not find element" | UI may have changed, file issue |

## Links

- **npm:** https://npmjs.com/package/@striderlabs/mcp-instacart
- **GitHub:** https://github.com/markswendsen-code/mcp-instacart
- **Strider Labs:** https://striderlabs.ai
- **MCP Protocol:** https://modelcontextprotocol.io
