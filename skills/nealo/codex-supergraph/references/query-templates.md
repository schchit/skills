# Codex Supergraph Query Templates

## 1) Simple query

```bash
curl -sS https://graph.codex.io/graphql \
  -H 'Content-Type: application/json' \
  -H "Authorization: $CODEX_API_KEY" \
  --data-binary @- <<'JSON'
{
  "query": "query GetNetworks { getNetworks { id name } }"
}
JSON
```

## 2) Query with variables

```bash
curl -sS https://graph.codex.io/graphql \
  -H 'Content-Type: application/json' \
  -H "Authorization: $CODEX_API_KEY" \
  --data-binary @- <<'JSON'
{
  "query": "query GetTokenPrices($inputs: [GetPriceInput!]!) { getTokenPrices(inputs: $inputs) { address networkId priceUsd timestamp } }",
  "variables": {
    "inputs": [
      { "address": "So11111111111111111111111111111111111111112", "networkId": 1399811149 }
    ]
  }
}
JSON
```

## 3) Token discovery (`filterTokens`)

```graphql
query FilterTokens(
  $filters: TokenFilters
  $statsType: TokenPairStatisticsType
  $rankings: [TokenRanking]
  $limit: Int
  $offset: Int
) {
  filterTokens(
    filters: $filters
    statsType: $statsType
    rankings: $rankings
    limit: $limit
    offset: $offset
  ) {
    count
    page
    results {
      priceUSD
      marketCap
      buyVolume24
      sellVolume24
      volume24
      circulatingMarketCap
      liquidity
      txnCount24
      holders
      token {
        info {
          address
          name
          symbol
          networkId
        }
      }
    }
  }
}
```

Example variables — top tokens on Solana by volume:

```json
{
  "filters": {
    "network": [1399811149],
    "liquidity": { "gte": 10000 }
  },
  "rankings": [{ "attribute": "volume24", "direction": "DESC" }],
  "limit": 25,
  "offset": 0
}
```

Example variables — trending tokens:

```json
{
  "filters": {
    "volume24": { "lte": 100000000000 },
    "liquidity": { "lte": 1000000000 },
    "marketCap": { "gte": 500000, "lte": 1000000000000 },
    "trendingIgnored": false,
    "creatorAddress": null,
    "potentialScam": false
  },
  "statsType": "FILTERED",
  "rankings": [{ "attribute": "trendingScore24", "direction": "DESC" }],
  "limit": 50,
  "offset": 0
}
```

Note: `trendingScore24` is a valid ranking attribute but is not a selectable field on the result type. Sort by it, but don't request it in the selection set.

## 4) Pair metadata (`pairMetadata`)

```graphql
query PairMetadata($pairId: String!) {
  pairMetadata(pairId: $pairId) {
    id
    pairAddress
    networkId
    liquidity
    price
    priceChange24
    volume24
    token0 {
      address
      symbol
      name
    }
    token1 {
      address
      symbol
      name
    }
  }
}
```

## 5) Pair bars (`getBars`)

```graphql
query GetBars(
  $symbol: String!
  $from: Int!
  $to: Int!
  $resolution: String!
  $countback: Int
  $removeEmptyBars: Boolean
) {
  getBars(
    symbol: $symbol
    from: $from
    to: $to
    resolution: $resolution
    countback: $countback
    removeEmptyBars: $removeEmptyBars
  ) {
    t
    o
    h
    l
    c
    volume
  }
}
```

## 6) Single-token realtime (`onPriceUpdated`)

```graphql
subscription OnPriceUpdated($address: String!, $networkId: Int!) {
  onPriceUpdated(address: $address, networkId: $networkId) {
    address
    networkId
    priceUsd
    timestamp
    blockNumber
  }
}
```

## 7) Multi-token realtime (`onPricesUpdated`)

```graphql
subscription OnPricesUpdated($input: [OnPricesUpdatedInput!]!) {
  onPricesUpdated(input: $input) {
    address
    networkId
    priceUsd
    timestamp
    blockNumber
  }
}
```

Example variables:

```json
{
  "input": [
    { "address": "So11111111111111111111111111111111111111112", "networkId": 1399811149 },
    { "address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "networkId": 1 }
  ]
}
```

## 8) Token bars (`getTokenBars`)

Aggregates OHLCV across top liquidity pairs for a token. Uses same `resolution` values as `getBars`.

```graphql
query GetTokenBars(
  $symbol: String!
  $from: Int!
  $to: Int!
  $resolution: String!
  $countback: Int
  $removeEmptyBars: Boolean
) {
  getTokenBars(
    symbol: $symbol
    from: $from
    to: $to
    resolution: $resolution
    countback: $countback
    removeEmptyBars: $removeEmptyBars
  ) {
    t
    o
    h
    l
    c
    volume
  }
}
```

## 9) List pairs for a token (`listPairsWithMetadataForToken`)

```graphql
query ListPairs($tokenAddress: String!, $networkId: Int!) {
  listPairsWithMetadataForToken(tokenAddress: $tokenAddress, networkId: $networkId) {
    results {
      pair {
        address
        networkId
        token0
        token1
      }
      volume
      liquidity
    }
  }
}
```

## 10) Token events (`getTokenEvents`)

```graphql
query GetTokenEvents(
  $query: EventsQueryInput!
  $cursor: String
  $limit: Int
) {
  getTokenEvents(
    query: $query
    cursor: $cursor
    limit: $limit
  ) {
    cursor
    items {
      timestamp
      eventType
      token0SwapValueUsd
      token1SwapValueUsd
      token0ValueBase
      token1ValueBase
      maker
      transactionHash
    }
  }
}
```

Example variables:

```json
{
  "query": {
    "address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "networkId": 1
  },
  "limit": 25
}
```

## 11) Maker events (`getTokenEventsForMaker`)

```graphql
query GetTokenEventsForMaker(
  $query: MakerEventsQueryInput!
  $cursor: String
  $limit: Int
) {
  getTokenEventsForMaker(
    query: $query
    cursor: $cursor
    limit: $limit
  ) {
    cursor
    items {
      timestamp
      eventType
      token0SwapValueUsd
      token1SwapValueUsd
      token0ValueBase
      token1ValueBase
      transactionHash
    }
  }
}
```

Example variables:

```json
{
  "query": {
    "maker": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    "networkId": 1,
    "tokenAddress": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
  },
  "limit": 25
}
```

## 12) Holders (`holders`)

```graphql
query Holders($input: HoldersInput!) {
  holders(input: $input) {
    cursor
    count
    top10HoldersPercent
    items {
      address
      balance
      shiftedBalance
      balanceUsd
    }
  }
}
```

## 13) Top-10 holder concentration (`top10HoldersPercent`)

The `tokenId` is a composite ID in `address:networkId` format.

```graphql
query Top10HoldersPercent($tokenId: String!) {
  top10HoldersPercent(tokenId: $tokenId)
}
```

Example variables:

```json
{
  "tokenId": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2:1"
}
```

## 14) Wallet leaders (`filterTokenWallets`)

```graphql
query FilterTokenWallets($input: FilterTokenWalletsInput!) {
  filterTokenWallets(input: $input) {
    results {
      address
      tokenAddress
      networkId
      amountBoughtUsd1d
      amountSoldUsd1d
      realizedProfitUsd1d
      realizedProfitPercentage1d
      buys1d
      sells1d
      labels
    }
  }
}
```

Example variables:

```json
{
  "input": {
    "tokenIds": ["0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2:1"],
    "limit": 25
  }
}
```

## 15) Wallet chart (`walletChart`)

```graphql
query WalletChart($input: WalletChartInput!) {
  walletChart(input: $input) {
    walletAddress
    networkId
    resolution
    data {
      timestamp
      volumeUsd
      realizedProfitUsd
      swaps
    }
  }
}
```

Example variables:

```json
{
  "input": {
    "walletAddress": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    "networkId": 1,
    "range": { "start": 1710000000, "end": 1710600000 },
    "resolution": "1D"
  }
}
```

## 16) WebSocket client (`graphql-ws`)

```typescript
import { createClient } from "graphql-ws";

const client = createClient({
  url: "wss://graph.codex.io/graphql",
  connectionParams: {
    Authorization: process.env.CODEX_API_KEY!,
  },
});

const unsubscribe = client.subscribe(
  {
    query: `
      subscription OnPriceUpdated($address: String!, $networkId: Int!) {
        onPriceUpdated(address: $address, networkId: $networkId) {
          address
          networkId
          priceUsd
          timestamp
          blockNumber
        }
      }
    `,
    variables: {
      address: "So11111111111111111111111111111111111111112",
      networkId: 1399811149,
    },
  },
  {
    next: (msg) => console.log(msg),
    error: (err) => console.error(err),
    complete: () => console.log("done"),
  }
);
```
