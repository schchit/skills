# xStocks API reference

## List tokens

**Endpoint:** `GET https://api.xstocks.fi/api/v1/token`

Returns xStocks tokens (mainnet). No query parameters. No authentication required.

### Response schema

```json
{
  "nodes": [
    {
      "id": "string",
      "name": "string",
      "symbol": "string",
      "isin": "string",
      "underlyingSymbol": "string",
      "underlyingIsin": "string",
      "description": "string",
      "logo": "string",
      "isTradingHalted": true,
      "deployments": [
        {
          "address": "string",
          "network": "string",
          "wrapperAddress": "string"
        }
      ]
    }
  ],
  "page": {
    "currentPage": 0,
    "hasNextPage": true
  }
}
```

- **nodes** — Array of token objects.
- **page** — Optional pagination metadata (currentPage, hasNextPage); the API returns all tokens in a single response.

### Token fields

| Field             | Description |
| ----------------- | ----------- |
| id                | Unique token ID |
| name              | Display name |
| symbol            | Ticker symbol |
| isin              | ISIN identifier |
| underlyingSymbol  | Underlying asset symbol |
| underlyingIsin    | Underlying asset ISIN |
| description       | Token description |
| logo              | Logo URL |
| isTradingHalted   | Whether trading is halted |
| deployments       | Per-network deployment (address, network, wrapperAddress) |

Use `deployments` with `network: "mainnet"` (or the appropriate network value) to get on-chain addresses for swaps or transfers.

### Usage from the skill

Run the bundled script to fetch all pages and output a single JSON array:

```bash
python3 scripts/list_tokens.py
python3 scripts/list_tokens.py --compact
```
