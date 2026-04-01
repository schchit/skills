---
name: jail-search
description: Search papers, books, code, legal cases, forums, Wikipedia, and more from one API.
metadata: {"openclaw":{"requires":{"bins":["curl"]},"optionalEnv":["JAIL_API_KEY"],"emoji":"🔍","homepage":"https://jail.li"}}
---

# JAIL Search

Results include titles, authors, URLs, and short descriptions. This is for discovering sources and links, not retrieving full content. After finding relevant results, use their URLs with fetch or browsing tools to read the actual documents.

## When to use

- User asks to research a topic, find papers, books, or articles
- User wants to look up facts, people, places, or concepts
- User asks about community discussions or forum threads
- User wants to find legal cases or legislation
- User asks "search for...", "find...", or "look up..."

## Search

```bash
curl -Gs "https://api.jail.li/v1/search" --data-urlencode "q=QUERY" -d "type=TYPE&limit=10"
```

With API key: add `-H "Authorization: Bearer $JAIL_API_KEY"`

Replace `QUERY` and `TYPE` (required, see below).

Paginate: add `&cursor=CURSOR` using `next_cursor` from previous response.

## Detail

```bash
curl -s "https://api.jail.li/v1/detail/DOC_ID"
```

## Types

Start with: `academic`, `wiki`, `books`, `legal`, `forums`. The rest just exist if you need.

```bash
curl -s "https://api.jail.li/v1/types"
```

| Type | Content |
|------|---------|
| `academic` | OpenAlex, arXiv, Semantic Scholar, DBLP |
| `wiki` | Wikipedia (en/zh/de/fr/es/ru/ja/ko/it/pl/ar/cs/da/el/hi/hu/ro/az) |
| `books` | Books, digital libraries, and classical literature |
| `legal` | Harvard Case Law, CourtListener, EUR-Lex, UK Legislation |
| `forums` | Hacker News, StackExchange, Lobsters, LessWrong, and 60+ more |
| `economics` | World Bank, IMF, FRED, ECB, BLS, Tax Foundation |
| `packages` | npm, PyPI, Crates.io, Libraries.io |
| `knowledge` | Wikidata, structured knowledge, and facts |
| `news` | News articles and journalism |
| `music` | Discogs, MusicBrainz |
| `video` | IMDb, YouTube |
| `health` | Clinical trials and food safety data |
| `geo` | World place names and geographic data |
| `fandom` | Fan wiki articles and community knowledge bases |
| `tech` | Dev.to, product community forums |
| `audio` | Podcasts and audio content |
| `social` | Mastodon, Lemmy, fediverse |
| `crypto` | DeFi protocols, token data, and on-chain analytics |
| `predictions` | Prediction markets and forecasting |

## Strategy

1. Pick the right type first
2. 2-4 keywords work best
3. Try different types for cross-referencing
4. Use `next_cursor` to paginate
5. Use detail endpoint for full metadata
