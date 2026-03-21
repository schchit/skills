---
name: strider-chipotle
description: Order from Chipotle via Strider Labs MCP connector. Build custom burritos and bowls, earn Rewards points, order ahead for pickup. Complete autonomous ordering for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "food"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Chipotle Connector

MCP connector for ordering from Chipotle — build custom burritos, bowls, tacos, and salads with full customization. Earn Chipotle Rewards points on every order. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-chipotle
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "chipotle": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-chipotle"]
    }
  }
}
```

## Available Tools

### chipotle.get_menu
Get full menu with customization options.

**Output:**
```json
{
  "entrees": [{
    "id": "string",
    "name": "string (Burrito, Bowl, Tacos, etc.)",
    "base_price": "number",
    "customizations": {
      "proteins": ["chicken", "steak", "barbacoa", "carnitas", "sofritas", "veggie"],
      "rice": ["white", "brown", "none"],
      "beans": ["black", "pinto", "none"],
      "toppings": ["cheese", "sour cream", "guac", "lettuce", "etc."]
    }
  }]
}
```

### chipotle.build_item
Build a custom menu item.

**Input Schema:**
```json
{
  "entree": "string (burrito, bowl, tacos, salad, quesadilla)",
  "protein": "string",
  "rice": "string",
  "beans": "string",
  "toppings": ["string"],
  "extras": ["string (extra protein, double rice, etc.)"]
}
```

### chipotle.add_to_order
Add built item to order.

### chipotle.find_locations
Find nearby Chipotle restaurants.

**Input Schema:**
```json
{
  "address": "string",
  "radius_miles": "number (optional)"
}
```

### chipotle.submit_order
Submit order for pickup.

**Input Schema:**
```json
{
  "location_id": "string",
  "pickup_time": "string (ASAP or ISO datetime)",
  "payment_method_id": "string"
}
```

### chipotle.get_rewards
Check Chipotle Rewards points and available rewards.

### chipotle.redeem_reward
Redeem points for free food.

### chipotle.get_favorites
Get saved favorite orders.

### chipotle.reorder_favorite
Quickly reorder a saved favorite.

## Authentication

First use triggers OAuth with Chipotle Rewards account. Points earned automatically. Tokens stored encrypted per-user.

## Usage Examples

**Build a bowl:**
```
Order a Chipotle bowl with chicken, brown rice, black beans, corn, cheese, and guac
```

**Quick order:**
```
Reorder my usual Chipotle burrito for pickup in 20 minutes
```

**Check rewards:**
```
How many Chipotle Rewards points do I have? Can I get free guac?
```

**Group order:**
```
Order 3 chicken burritos and 2 steak bowls from Chipotle for pickup at noon
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| LOCATION_CLOSED | Restaurant not open | Suggest nearby open location |
| ITEM_UNAVAILABLE | Out of ingredient | Suggest substitution |
| INSUFFICIENT_POINTS | Not enough rewards | Pay with card |

## Use Cases

- Lunch orders: quick pickup during work
- Custom builds: save complex customizations as favorites
- Rewards optimization: track and redeem points
- Group orders: coordinate team meals

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-chipotle
- Strider Labs: https://striderlabs.ai
