---
name: strider-zipcar
description: Rent Zipcars via Strider Labs MCP connector. Find nearby cars, book by the hour or day, unlock vehicles, and manage your Zipcar membership.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "travel"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Zipcar Connector

MCP connector for Zipcar car sharing. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-zipcar
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "zipcar": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-zipcar"]
    }
  }
}
```

## Available Tools

### zipcar.find_cars
Find available Zipcars nearby.

**Input Schema:**
```json
{
  "location": "string (address or coordinates)",
  "start_time": "string (ISO 8601)",
  "duration_hours": "number",
  "vehicle_type": "sedan | suv | pickup | van (optional)"
}
```

**Output:**
```json
{
  "cars": [{
    "car_id": "zip123",
    "name": "Honda Civic",
    "type": "sedan",
    "location": "123 Main St - Garage A",
    "distance": "0.3 miles",
    "hourly_rate": 12.50,
    "daily_rate": 89.00,
    "fuel_level": "3/4"
  }]
}
```

### zipcar.reserve
Book a Zipcar.

**Input Schema:**
```json
{
  "car_id": "string",
  "start_time": "string",
  "duration_hours": "number"
}
```

### zipcar.extend_reservation
Add time to current reservation.

**Input Schema:**
```json
{
  "reservation_id": "string",
  "additional_hours": "number"
}
```

### zipcar.unlock_car
Remotely unlock your reserved car.

**Input Schema:**
```json
{
  "reservation_id": "string"
}
```

### zipcar.get_reservations
List upcoming reservations.

### zipcar.cancel_reservation
Cancel a booking.

### zipcar.report_issue
Report a problem with the vehicle.

## Authentication

First use triggers OAuth authorization:
1. User redirected to Zipcar login
2. Membership verified automatically
3. Tokens stored encrypted per-user

No API key required — connector manages OAuth flow.

## Usage Examples

**Find a car:**
```
Find a Zipcar near me available in 30 minutes
```

**Book hourly:**
```
Reserve the Honda Civic on Main St for 3 hours
```

**Extend time:**
```
Add 2 more hours to my current Zipcar reservation
```

**Unlock:**
```
Unlock my Zipcar - I'm at the parking spot
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| NO_CARS_AVAILABLE | None nearby | Expand search area |
| ALREADY_RESERVED | Car taken | Choose different car |
| CANNOT_EXTEND | Extension not available | Return on time |

## Use Cases

- Errands: quick trips around town
- Day trips: full-day rentals outside the city
- Moving help: rent a van or pickup
- Commute backup: when transit fails
- Car-free living: on-demand vehicle access

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-zipcar
- Strider Labs: https://striderlabs.ai
