---
name: agenttimes
description: News intelligence API for AI agents. Semantic search 160K+ articles, 3,597 feeds, 14 categories, 60+ country tags, sentiment scoring, entity extraction, source credibility, webhook alerts. Free /ask endpoint. x402 micropayments.
metadata:
  openclaw:
    emoji: "\U0001F4F0"
    homepage: https://agenttimes.live
    author: penghian
    skillKey: agenttimes
    always: false
    requires:
      bins:
        - curl
    links:
      homepage: https://agenttimes.live
      documentation: https://agenttimes.live/info
---

# Agent Times — News Intelligence API

## TL;DR

```bash
# Search anything (free):
curl -s "https://agenttimes.live/ask?q=TOPIC+HERE"

# What's trending (free):
curl -s "https://agenttimes.live/trending"
```

Response is JSON. Each result has: `title`, `url`, `summary`, `category`, `sentiment`, `sentiment_score`, `credibility`, `entities`, `tags`. No API key needed.

## Common Tasks — Copy-Paste Commands

**Job search (remote devops/SRE):**
```bash
curl -s "https://agenttimes.live/news?category=business&tag=jobs&limit=20"
```

**Country-specific news (e.g. Singapore):**
```bash
curl -s "https://agenttimes.live/ask?q=singapore+news"
```

**Crypto market news:**
```bash
curl -s "https://agenttimes.live/ask?q=crypto+market+news&limit=10"
```

**Gaming news:**
```bash
curl -s "https://agenttimes.live/news?category=entertainment&tag=gaming&limit=10"
```

**Filter by any tag:** Add `&tag=TAG` to `/news`. Example tags: `jobs`, `gaming`, `space`, `bitcoin`, `asia`, `europe`, `startups`, `devtools`.

---

## What This Does

Agent Times aggregates **3,597 RSS feeds** across **14 categories** from **60+ countries**, refreshing every 3 minutes. It provides:

- **Semantic search** — AI understands meaning, not just keywords. "AI taking jobs" finds articles about "automation threatens employment"
- **Sentiment scoring** — every article rated bullish/bearish/neutral with a -1 to 1 score
- **Source credibility** — tier 1 (Reuters, BBC) ranked above tier 3 (unknown blogs)
- **Entity extraction** — companies, stock tickers, crypto tickers, and people detected per article
- **Country tags** — filter by 60+ countries and regions
- **Webhook subscriptions** — get notified when articles matching your topic arrive
- **3-tier fallback** — semantic search → keyword search → web search (70+ engines). Always finds something.

160,000+ articles with 30-day retention.

## When to Use Which Endpoint

| You want to... | Use this | Free? |
|---|---|---|
| Search for a topic | `GET /ask?q=TOPIC` | Yes |
| Get trending stories | `GET /trending` | Yes |
| Browse a category | `GET /news?category=CAT` | $0.001 |
| Filter by country/tag | `GET /news?category=world&tag=singapore` | $0.001 |
| Search the web | `GET /search?q=QUERY` | $0.001 |
| Monitor a topic | `POST /subscribe` | Yes |
| List categories | `GET /news/categories` | Yes |

**Rule of thumb:** Start with `/ask`. It's free, smart, and handles most cases. Use `/news` only when you need bulk category browsing with filters.

## /ask — Smart Search (FREE)

Searches all 160K+ articles using AI semantic matching + keyword matching + web search fallback. Returns results ranked by relevance and recency.

```bash
curl -s "https://agenttimes.live/ask?q=bitcoin+etf"
curl -s "https://agenttimes.live/ask?q=singapore+startup+funding"
curl -s "https://agenttimes.live/ask?q=climate+policy+europe&limit=20"
curl -s "https://agenttimes.live/ask?q=remote+devops+jobs"
```

| Param | Default | Description |
|-------|---------|-------------|
| q | required | Search query. Replace spaces with `+` |
| limit | 10 | Max results (1-50) |

**Response:**
```json
{
  "success": true,
  "query": "bitcoin etf",
  "source": "news_db",
  "count": 10,
  "results": [
    {
      "title": "SEC Approves Spot Bitcoin ETF Applications",
      "url": "https://example.com/article",
      "summary": "The Securities and Exchange Commission has approved...",
      "category": "crypto",
      "published": "Mon, 24 Mar 2026 14:30:00 +0000",
      "sentiment": "bullish",
      "sentiment_score": 0.75,
      "credibility": "high",
      "entities": {
        "companies": ["SEC"],
        "tickers": [],
        "crypto": ["BTC"],
        "people": []
      },
      "tags": ["markets"]
    }
  ]
}
```

When `/ask` finds fewer than 3 results, it automatically falls back to web search. When 0 results, it returns `suggestions` with related categories and terms.

## /trending — Trending Stories (FREE)

Detects stories being covered by multiple independent sources.

```bash
curl -s "https://agenttimes.live/trending?hours=12"
```

| Param | Default | Description |
|-------|---------|-------------|
| hours | 6 | Lookback window (1-48) |
| min_sources | 3 | Minimum sources covering the same story |
| limit | 20 | Max trending clusters |

## /subscribe — Topic Alerts (FREE)

Get webhook notifications when new articles matching your query arrive.

```bash
curl -s -X POST https://agenttimes.live/subscribe \
  -H "Content-Type: application/json" \
  -d '{"query":"bitcoin regulation","category":"crypto","webhook":"https://your-agent.com/notify"}'
```

Response: `{"success":true,"subscription_id":1}`

Unsubscribe: `curl -s -X DELETE https://agenttimes.live/subscribe/1`

Your webhook receives a POST with matching articles every time new ones arrive (checked every 3 minutes).

**Security:** Webhook must be a public HTTPS URL. Localhost, private IPs, and cloud metadata endpoints are blocked.

## /news — Category Browsing ($0.001)

Browse and filter articles by category with optional tag, date range, and keyword filters.

```bash
# All crypto news
curl -s "https://agenttimes.live/news?category=crypto&limit=10"

# Asian news only
curl -s "https://agenttimes.live/news?category=world&tag=asia"

# Singapore news
curl -s "https://agenttimes.live/news?category=world&tag=singapore"

# Gaming news
curl -s "https://agenttimes.live/news?category=entertainment&tag=gaming"

# Jobs in tech
curl -s "https://agenttimes.live/news?category=business&tag=jobs"

# AI news from last 2 days
curl -s "https://agenttimes.live/news?category=ai&since=2026-03-22"

# Search within a category
curl -s "https://agenttimes.live/news?category=tech&q=rust+programming"
```

| Param | Default | Description |
|-------|---------|-------------|
| category | required | One of 14 categories, or `all` |
| tag | — | Subcategory/country filter (see table below) |
| limit | 20 | Max results (1-1000) |
| q | — | Keyword filter within category |
| since | — | ISO date — articles after this time |
| before | — | ISO date — articles before this time |
| dedup | true | Deduplicate similar headlines |

## /search — Web Search ($0.001)

Search the open web via 70+ engines when you need non-news results.

```bash
curl -s "https://agenttimes.live/search?q=how+to+deploy+docker"
```

| Param | Default | Description |
|-------|---------|-------------|
| q | required | Search query |
| limit | 5 | Max results (1-50) |
| category | general | general, news, images, videos, science, files |

## Categories + Tags

14 categories. Use `&tag=` on `/news` to filter by subcategory, country, or region.

| Category | What's in it | Available tags |
|----------|-------------|----------------|
| **world** | International news, geopolitics, diplomacy | `asia`, `europe`, `middleeast`, `africa`, `india`, `latam`, `oceania`, `defense`, `government` + 50 country tags (see below) |
| **politics** | Elections, policy, legislation, regulation | — |
| **business** | Finance, commerce, employment, markets | `finance`, `startups`, `jobs`, `marketing`, `ecommerce`, `fintech`, `realestate`, `legal`, `supplychain` |
| **tech** | Software, hardware, engineering, data | `devtools`, `engineering`, `mobile`, `datascience`, `telecom` |
| **ai** | Artificial intelligence, machine learning | `robotics`, `research` |
| **crypto** | Cryptocurrency, blockchain, DeFi | `web3`, `defi`, `bitcoin`, `markets` |
| **science** | Research, discoveries, academia | `biotech`, `space`, `research` |
| **health** | Medicine, wellness, public health | `fitness` |
| **energy** | Energy, climate change, environment | `climate`, `environment`, `agriculture` |
| **security** | Cybersecurity, infosec, threats | — |
| **sports** | All sports coverage | — |
| **entertainment** | Film, music, gaming, TV, culture | `gaming`, `film`, `music` |
| **lifestyle** | Food, travel, fashion, daily life | `food`, `travel`, `fashion`, `design`, `education` |
| **automotive** | Vehicles, EVs, transportation, logistics | `shipping` |

### Country Tags (use with `category=world&tag=COUNTRY`)

**Asia:** `singapore`, `malaysia`, `philippines`, `indonesia`, `thailand`, `vietnam`, `japan`, `korea`, `china`, `taiwan`, `hongkong`, `india`, `pakistan`, `bangladesh`

**Europe:** `uk`, `germany`, `france`, `italy`, `spain`, `netherlands`, `sweden`, `norway`, `denmark`, `finland`, `ireland`, `poland`, `austria`, `switzerland`, `iceland`, `romania`, `hungary`, `greece`, `serbia`, `ukraine`, `russia`

**Middle East:** `israel`, `turkey`, `iran`, `saudiarabia`, `uae`, `qatar`

**Africa:** `nigeria`, `southafrica`, `kenya`, `ghana`, `ethiopia`

**Latin America:** `brazil`, `mexico`, `argentina`, `colombia`, `chile`, `peru`

**Oceania:** `australia`, `newzealand`

**North America:** `usa`, `canada`

## Response Format

All endpoints return:
```json
{"success": true, "count": N, "results": [...]}
```

Each article result contains:
- `title` — headline
- `url` — link to original article
- `summary` — first 200 chars of content
- `category` — one of 14 categories
- `published` — publication date
- `sentiment` — "bullish", "bearish", or "neutral"
- `sentiment_score` — -1.0 (very bearish) to 1.0 (very bullish)
- `credibility` — "high" (tier 1 outlets), "medium" (established), or "unknown"
- `entities` — `{companies, tickers, crypto, people}` extracted from text
- `tags` — subcategory and country tags for this article

Errors: `{"success": false, "error": "Missing param: q"}`

## Payment (x402)

Paid endpoints (`/news`, `/search`) use the [x402](https://www.x402.org) protocol. Your agent pays **$0.001 USDC** per request on Base network — no accounts, no subscriptions, just micropayments.

Wallet: `0x536Eafe011786599d9a656D62e2aeAFcE06a96D1` (Base)

## Other Free Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /news/categories` | List all 14 categories with counts |
| `GET /stats` | Database statistics |
| `GET /feeds/health?category=CAT` | Per-feed health and status |
| `GET /health` | Health check |
| `GET /info` | Full API docs (JSON for agents, HTML for browsers) |

## Tips for Best Results

1. **Always start with `/ask`** — it's free, semantic, and handles fallback automatically
2. **Country news:** Use `/ask?q=japan+earthquake` not `/news?category=japan` (no country categories)
3. **Filter by country:** Use `/news?category=world&tag=singapore` for source-based filtering
4. **Sentiment analysis:** Check `sentiment_score` to gauge market/public mood on a topic
5. **Entity detection:** Use `entities.tickers` and `entities.crypto` to find articles mentioning specific assets
6. **Monitor breaking news:** POST to `/subscribe` with a webhook URL to get real-time alerts
7. **Parse JSON directly** — don't pipe to `jq` (may not be installed)
8. **Replace spaces with `+`** in all query strings
9. **Check `suggestions`** when 0 results — it recommends related categories and search terms
10. **Credibility matters:** Sort by `credibility` to prioritize tier 1 sources (Reuters, BBC, AP) over unknown blogs
