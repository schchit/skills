---
name: pangolinfo-amazon-scraper
description: >
  Amazon scraper for product data and reviews (ASIN-based, 13 regions).
metadata:
  openclaw:
    requires:
      env:
        - PANGOLIN_API_KEY
        - PANGOLIN_EMAIL
        - PANGOLIN_PASSWORD
      notes: "Auth: set PANGOLIN_API_KEY (recommended) OR PANGOLIN_EMAIL + PANGOLIN_PASSWORD."
---

# Pangolinfo Amazon Scraper

Scrape Amazon product data via Pangolin's APIs. Returns parsed JSON with product details, search results, rankings, reviews, and more across 13 Amazon regions.

## When to Use This Skill

| Intent (EN) | Intent (CN) | Action |
|---|---|---|
| Look up an Amazon product / ASIN | 查一下亚马逊上的这个商品 | Product detail |
| Search Amazon for a keyword | 在亚马逊搜索关键词 | Keyword search |
| Show bestsellers in a category | 看看某个类目的畅销榜 | Bestsellers |
| Show new releases | 看看最新上架的商品 | New releases |
| Browse a category on Amazon | 浏览亚马逊某个分类 | Category products |
| Find products from a seller | 查看某个卖家的商品 | Seller products |
| Get reviews for a product | 看看这个产品的评论 | Reviews |
| Compare prices across regions | 对比不同国家亚马逊的价格 | Multi-region |
| Check seller/variant options | 查看其他卖家选项 / 变体 | Follow seller / Variant |

Do **not** use for Google search, SERP, or non-Amazon data -- those require a different skill.

## Prerequisites

- **Python 3.8+** (stdlib only, no pip install needed)
- **Pangolin account** at [pangolinfo.com](https://pangolinfo.com/?referrer=clawhub_amz)
- **Environment variables**: `PANGOLIN_API_KEY` (recommended) OR `PANGOLIN_EMAIL` + `PANGOLIN_PASSWORD`

macOS SSL error? Run: `/Applications/Python\ 3.x/Install\ Certificates.command`

## Script Execution

```bash
python3 scripts/pangolin.py --content B0DYTF8L2W --mode amazon --site amz_us
```

## Intent-to-Command Mapping

### 1. Product Detail by ASIN

```bash
python3 scripts/pangolin.py --asin B0DYTF8L2W --site amz_us
```

`--asin` auto-uppercases and selects `amzProductDetail`.

### 2. Keyword Search

```bash
python3 scripts/pangolin.py --q "wireless mouse" --site amz_us
```

Non-ASIN text auto-selects `amzKeyword`.

### 3. Bestsellers

```bash
python3 scripts/pangolin.py --content "electronics" --parser amzBestSellers --site amz_us
```

### 4. New Releases

```bash
python3 scripts/pangolin.py --content "toys" --parser amzNewReleases --site amz_us
```

### 5. Category Products

```bash
python3 scripts/pangolin.py --content "172282" --parser amzProductOfCategory --site amz_us
```

### 6. Seller Products

```bash
python3 scripts/pangolin.py --content "A1B2C3D4E5" --parser amzProductOfSeller --site amz_us
```

### 7. Follow Seller (Other Seller Options)

```bash
python3 scripts/pangolin.py --asin B0G4QPYK4Z --parser amzFollowSeller --site amz_us
```

### 8. Variant ASIN (Product Variants)

```bash
python3 scripts/pangolin.py --asin B0G4QPYK4Z --parser amzVariantAsin --site amz_us
```

### 9. Product Reviews

```bash
python3 scripts/pangolin.py --content B00163U4LK --mode review --site amz_us --filter-star critical
```

**Star filter mapping:**

| User says | `--filter-star` |
|---|---|
| all reviews / 所有评论 | `all_stars` |
| 5-star / 五星 | `five_star` |
| 4-star / 四星 | `four_star` |
| 3-star / 三星 | `three_star` |
| 2-star / 两星 | `two_star` |
| 1-star / 一星 | `one_star` |
| positive / 好评 | `positive` |
| critical / 差评 | `critical` |

**Sort:** `--sort-by recent` (default) or `--sort-by helpful`

**Multiple pages:** `--pages N` (each page costs 5 credits)

### 10. Product by URL (Legacy)

```bash
python3 scripts/pangolin.py --url "https://www.amazon.com/dp/B0DYTF8L2W" --mode amazon
```

Site code auto-inferred from URL domain.

## Smart Defaults

1. **ASIN detection** -- 10-char codes starting with `B0` auto-select `amzProductDetail`
2. **Keyword detection** -- non-ASIN text auto-selects `amzKeyword`
3. **Defaults to `amz_us`** if no `--site` provided
4. **Auto-switches to review mode** if `--filter-star` is set or `--parser amzReviewV2`
5. **Site inferred from URL** when using `--url`
6. **Parser auto-inference only runs when `--parser` is not specified** -- explicit `--parser` is never overridden

## All CLI Options

| Flag | Description | Default |
|---|---|---|
| `--q` | Search query or keyword | -- |
| `--url` | Target Amazon URL (legacy) | -- |
| `--content` | Content ID: ASIN, keyword, category Node ID, seller ID | -- |
| `--asin` | ASIN shortcut (auto-uppercases) | -- |
| `--site` / `--region` | Amazon site/region code | `amz_us` |
| `--mode` | `amazon` or `review` | `amazon` |
| `--parser` | Parser name (auto-inferred if omitted) | auto |
| `--zipcode` | US zipcode for localized pricing | `10041` |
| `--format` | `json`, `rawHtml`, `markdown` | `json` |
| `--filter-star` | Star filter for reviews | `all_stars` |
| `--sort-by` | Review sort: `recent` or `helpful` | `recent` |
| `--pages` | Review pages (5 credits/page) | `1` |
| `--auth-only` | Auth check only (no credits) | -- |
| `--raw` | Output raw API response | -- |
| `--timeout` | Timeout in seconds | `120` |
| `--cache-key` | Persist API key to `~/.pangolin_api_key` | off |

## Amazon Parsers

| Parser | Use Case | Content Value | Endpoint |
|---|---|---|---|
| `amzProductDetail` | Single product page | ASIN | `/api/v1/scrape` |
| `amzKeyword` | Keyword search results | Keyword | `/api/v1/scrape` |
| `amzProductOfCategory` | Category listing | Node ID | `/api/v1/scrape` |
| `amzProductOfSeller` | Seller's products | Seller ID | `/api/v1/scrape` |
| `amzBestSellers` | Best sellers ranking | Category keyword | `/api/v1/scrape` |
| `amzNewReleases` | New releases ranking | Category keyword | `/api/v1/scrape` |
| `amzFollowSeller` | Other sellers | ASIN | `/api/v1/scrape/follow-seller` |
| `amzVariantAsin` | Product variants | ASIN | `/api/v1/scrape/variant-asin` |
| `amzReviewV2` | Product reviews | ASIN (via `--mode review`) | `/api/v1/scrape` |

## Amazon Sites

| Code | Region | Domain |
|---|---|---|
| `amz_us` | United States | amazon.com |
| `amz_uk` | United Kingdom | amazon.co.uk |
| `amz_ca` | Canada | amazon.ca |
| `amz_de` | Germany | amazon.de |
| `amz_fr` | France | amazon.fr |
| `amz_jp` | Japan | amazon.co.jp |
| `amz_it` | Italy | amazon.it |
| `amz_es` | Spain | amazon.es |
| `amz_au` | Australia | amazon.com.au |
| `amz_mx` | Mexico | amazon.com.mx |
| `amz_sa` | Saudi Arabia | amazon.sa |
| `amz_ae` | UAE | amazon.ae |
| `amz_br` | Brazil | amazon.com.br |

## Cost

| Operation | Credits |
|---|---|
| Amazon scrape (`json`) | 1 |
| Amazon scrape (`rawHtml` / `markdown`) | 0.75 |
| Follow Seller | 1 |
| Variant ASIN | 1 |
| Review page | 5 per page |

Credits consumed on success only (API code 0). Auth checks are free.

## Output Format

JSON to **stdout** on success, error JSON to **stderr** on failure.

### Success

```json
{
  "success": true,
  "task_id": "02b3e90810f0450ca6d41244d6009d0f",
  "url": "https://www.amazon.com/dp/B0DYTF8L2W",
  "metadata": {
    "executionTime": 1791,
    "parserType": "amzProductDetail",
    "parsedAt": "2026-01-13T06:42:01.861Z"
  },
  "results": [ ... ],
  "results_count": 1
}
```

### Error (stderr)

```json
{
  "success": false,
  "error": {
    "code": "API_ERROR",
    "api_code": 2001,
    "message": "Insufficient credits",
    "hint": "Top up at https://pangolinfo.com/?referrer=clawhub_amz"
  }
}
```

## Response Presentation

Match the user's language. Never dump raw JSON.

- **Product Detail**: structured card with title, price, rating, features, rank
- **Keyword Search**: numbered list with title, price, rating
- **Bestsellers/New Releases**: ranked list emphasizing position
- **Follow Seller / Variant**: option comparison table
- **Reviews**: summary + top 3-5 reviews + pattern analysis
- **Empty results**: suggest checking ASIN spelling, trying another region, broadening search

## Exit Codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | API error |
| 2 | Usage error (bad arguments) |
| 3 | Network error |
| 4 | Authentication error |

## Error Reference

### Script Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| `MISSING_ENV` | No credentials | Set env vars |
| `AUTH_FAILED` | Wrong credentials | Verify email/password |
| `RATE_LIMIT` | Too many requests | Wait and retry |
| `NETWORK` | Connection issue | Check internet |
| `SSL_CERT` | Certificate error | See macOS SSL fix |
| `API_ERROR` | Pangolin API error | Check `api_code` and `hint` |
| `PARSE_ERROR` | Invalid API response | Retry |
| `USAGE_ERROR` | Bad arguments | Fix CLI args |

### Pangolin API Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| 1004 | Invalid token | Auto-retried by script |
| 1009 | Invalid parser name | Check `--parser` value |
| 2001 | Insufficient credits | Top up at [pangolinfo.com](https://pangolinfo.com/?referrer=clawhub_amz) |
| 2005 | No active plan | Subscribe at [pangolinfo.com](https://pangolinfo.com/?referrer=clawhub_amz) |
| 2007 | Account expired | Renew at [pangolinfo.com](https://pangolinfo.com/?referrer=clawhub_amz) |
| 2009 | Usage limit reached | Wait for next billing cycle |
| 4029 | Rate limited | Reduce request frequency |
| 10000/10001 | Task failed | Retry |

## First-Time Setup

See [references/setup-guide.md](references/setup-guide.md) for interactive setup instructions.

Quick start:
```bash
export PANGOLIN_API_KEY="your-api-key"
python3 scripts/pangolin.py --auth-only
```

## Important Notes for AI Agents

1. **Never dump raw JSON.** Parse and present per the Response Presentation guidelines.
2. **Match the user's language.**
3. **Be proactive.** Highlight best matches, summarize review patterns, flag out-of-stock.
4. **Handle multi-step requests.** E.g., "compare US vs JP price" = two queries + comparison table.
5. **Credit awareness.** Warn before multi-page reviews (5 credits/page).
6. **ASIN detection.** 10-char codes starting with B0 are almost always ASINs -- auto-detect.
7. **Default to `amz_us`** unless context implies another region.
8. **Security.** Never expose API keys or passwords.
9. **Use `--parser` explicitly** for category, seller, bestsellers, new releases, follow-seller, variant-asin. Auto-inference only works for ASIN vs keyword.
10. **Combine results.** "Find a good mouse under $30 with good reviews" = keyword search + review fetch for top candidates.

## Output Schema

See [references/output-schema.md](references/output-schema.md) for per-parser field documentation.
