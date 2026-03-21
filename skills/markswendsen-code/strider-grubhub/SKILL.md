---
name: strider-grubhub
description: Order food delivery via Grubhub using Strider Labs MCP connector. Search restaurants, browse menus, customize orders, track delivery. Complete autonomous food ordering for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "food"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Grubhub Connector

MCP connector for ordering food delivery through Grubhub — search restaurants, browse menus, customize orders, and track delivery. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-grubhub
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "grubhub": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-grubhub"]
    }
  }
}
```

## Available Tools

### grubhub.search_restaurants
Search for restaurants by cuisine, location, or keyword.

**Input Schema:**
```json
{
  "query": "string (optional: search terms)",
  "cuisine": "string (optional: pizza, chinese, mexican, etc.)",
  "address": "string (delivery address)",
  "sort": "string (optional: rating, delivery_time, distance, price)"
}
```

**Output:**
```json
{
  "restaurants": [{
    "id": "string",
    "name": "string",
    "cuisine": ["string"],
    "rating": "number",
    "delivery_time_min": "number",
    "delivery_fee": "number",
    "minimum_order": "number"
  }]
}
```

### grubhub.get_menu
Get full menu for a restaurant with prices and options.

### grubhub.add_to_cart
Add items to cart with customizations.

**Input Schema:**
```json
{
  "restaurant_id": "string",
  "item_id": "string",
  "quantity": "number",
  "customizations": {
    "size": "string",
    "toppings": ["string"],
    "special_instructions": "string"
  }
}
```

### grubhub.checkout
Complete order with delivery address and payment.

**Input Schema:**
```json
{
  "delivery_address": {
    "street": "string",
    "apt": "string (optional)",
    "city": "string",
    "state": "string",
    "zip": "string"
  },
  "tip_percent": "number",
  "payment_method_id": "string"
}
```

### grubhub.track_order
Get real-time order and driver status.

### grubhub.get_past_orders
Retrieve order history for easy reordering.

### grubhub.reorder
Quickly reorder a previous order.

## Authentication

First use triggers OAuth authorization flow. Payment methods and addresses saved to account. Tokens stored encrypted per-user.

## Usage Examples

**Quick dinner:**
```
Order Thai food from the highest-rated restaurant near me on Grubhub
```

**Specific order:**
```
Order a large pepperoni pizza and garlic knots from the nearest pizza place on Grubhub
```

**Reorder:**
```
Reorder my last Grubhub order from Panda Express
```

**Browse options:**
```
What Mexican restaurants on Grubhub deliver to my address in under 30 minutes?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| RESTAURANT_CLOSED | Not accepting orders | Suggest alternatives |
| BELOW_MINIMUM | Order below minimum | Add more items |
| DELIVERY_UNAVAILABLE | Can't deliver to address | Try different restaurant |

## Use Cases

- Dinner delivery: find restaurants open now
- Group orders: coordinate large orders with customizations
- Dietary needs: filter by cuisine and dietary restrictions
- Reordering: quickly repeat frequent orders

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-grubhub
- Strider Labs: https://striderlabs.ai
