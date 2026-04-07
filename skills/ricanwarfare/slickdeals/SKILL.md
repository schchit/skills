---
name: slickdeals
description: Search Slickdeals.net for deals, coupons, and promo codes. Use when the user asks for deals, discounts, price comparisons, or to find cheap games, electronics, or other products.
license: Apache-2.0
---

# Slickdeals Skill

Search Slickdeals.net for the best deals, coupons, promo codes, and discounts across electronics, games, home goods, and more.

## Capabilities

- Search for deals by product name, category, or keyword
- Get frontpage deals (top trending deals)
- Filter by store, category, or price range
- Check deal expiration status
- Find coupon codes and promo codes

## Usage

### Search for Deals

```
Use the skill to search Slickdeals for specific products or categories.
```

**Examples:**
- "Find deals on PS5 games"
- "Search for Nintendo Switch deals"
- "Any deals on air fryers?"
- "Find GTA Trilogy deals under $30"
- "Show me frontpage deals"
- "Find laptop deals on Slickdeals"

### Search URL Format

The search URL pattern is:
```
https://slickdeals.net/newsearch.php?q={QUERY}&searcharea=deals&searchin=first
```

For category browsing:
```
https://slickdeals.net/computer-deals/
https://slickdeals.net/electronics-deals/
https://slickdeals.net/video-game-deals/
https://slickdeals.net/home-deals/
```

## Implementation

### Step 1: Search Slickdeals

Use `ollama_web_fetch` to retrieve search results:

```
https://slickdeals.net/newsearch.php?q=URL_ENCODED_QUERY&searcharea=deals&searchin=first
```

### Step 2: Parse Results

Extract from the HTML:
- Deal title
- Current price vs original price
- Discount percentage
- Store name
- Deal score (thumbs up/down)
- Comments count
- Expiration status (if marked "expired")

### Step 3: Format Output

Present deals in a clean table format:

| Deal | Price | Discount | Store | Score |
|------|-------|----------|-------|-------|
| Title | $XX ($YY) | 50% off | Amazon | +15 |

## Categories

- `video-game-deals` - Video games, consoles, accessories
- `computer-deals` - Laptops, desktops, components
- `electronics-deals` - TVs, phones, audio
- `home-deals` - Appliances, furniture
- `clothing-deals` - Fashion, apparel
- `travel-deals` - Hotels, flights, vacation packages

## Tips

1. **Check expiration**: Deals marked "expired" are no longer valid
2. **Deal score**: Higher thumbs up = better verified deal
3. **Comments**: Read comments for coupon codes or price match tips
4. **Store filter**: Results often include Amazon, Best Buy, Walmart, Newegg, etc.

## Limitations

- Slickdeals is a community-driven site; deals may expire quickly
- Some deals require store-specific coupons or subscriptions (Amazon Prime, etc.)
- Regional availability may vary

## Example Queries

| User Request | Search Query |
|--------------|--------------|
| "Find PS5 deals" | `PS5` |
| "Cheap GTA Trilogy" | `GTA Trilogy` |
| "Nintendo Switch games under $30" | `Nintendo Switch games` |
| "Laptop deals" | `laptop` |
| "Air fryer deals" | `air fryer` |
| "Frontpage deals" | Browse `https://slickdeals.net/` |

## Notes

- Always check if the deal is still active (not marked "expired")
- Include the store name and any coupon codes required
- Mention if the deal requires membership (Prime, etc.)