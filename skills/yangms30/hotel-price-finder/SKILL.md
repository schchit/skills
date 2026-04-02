---
name: hotel-price-finder
version: 1.0.0
description: Compare hotel prices across Booking.com, Agoda, Trip.com in real-time. Free multi-OTA price comparison with direct booking links. No API key required.
tags: [travel, hotel, agoda, booking, price-comparison, trip, expedia, cheapest, deal]
env:
  - APIFY_API_KEY (optional - enables Agoda-specific deep search with 22+ fields)
---

# Hotel Price Compare - Multi OTA

Search hotels and compare real-time prices across multiple OTAs (Booking.com, Agoda, Trip.com, etc.).

**Three modes available:**
- **Free Mode** (default): Xotelo API - hotel list + real-time OTA price comparison. No API key needed.
- **Agoda Direct Mode**: Agoda autocomplete API for city lookup + direct Agoda search URL.
- **Apify Mode** (optional): Agoda-specific deep search with 22+ data fields. Requires `APIFY_API_KEY`.

## When to Use This Skill

Activate when the user asks about:
- Hotel/accommodation search in any city
- Comparing hotel prices across booking sites
- Finding the cheapest OTA for a specific hotel
- Budget-friendly or luxury hotel recommendations
- Accommodation near specific landmarks or areas

## Step 1: Parse User Query

Extract the following from the user's request:

| Parameter | Required | Default | Example |
|-----------|----------|---------|---------|
| `destination` | Yes | - | "Seoul", "Tokyo", "Bangkok" |
| `checkIn` | Yes | - | "2026-05-01" (YYYY-MM-DD) |
| `checkOut` | Yes | - | "2026-05-03" (YYYY-MM-DD) |
| `adults` | No | 2 | Number of adults |
| `rooms` | No | 1 | Number of rooms |
| `currency` | No | USD | USD, KRW, JPY, THB, etc. |
| `sort` | No | popularity | popularity, price-low, price-high, rating |
| `maxBudget` | No | - | Max price per night |
| `limit` | No | 10 | Number of hotels to show |

If the user omits dates, ask for check-in and check-out dates. If they say "next weekend", calculate actual dates.

## Step 2: Resolve Destination

### 2A: TripAdvisor Location Key (for Xotelo)

Xotelo uses TripAdvisor location keys in the format `g{number}`. Common keys:

| City | Location Key | Country |
|------|-------------|---------|
| Seoul | g294197 | South Korea |
| Busan | g297884 | South Korea |
| Jeju | g983296 | South Korea |
| Tokyo | g298184 | Japan |
| Osaka | g298566 | Japan |
| Kyoto | g298564 | Japan |
| Bangkok | g293916 | Thailand |
| Phuket | g293920 | Thailand |
| Chiang Mai | g293917 | Thailand |
| Singapore | g294265 | Singapore |
| Bali | g294226 | Indonesia |
| Kuala Lumpur | g298570 | Malaysia |
| Hong Kong | g294217 | Hong Kong |
| Taipei | g293913 | Taiwan |
| Da Nang | g298085 | Vietnam |
| Ho Chi Minh | g293925 | Vietnam |
| Hanoi | g293924 | Vietnam |
| Cebu | g294261 | Philippines |
| Manila | g298573 | Philippines |
| Siem Reap | g297390 | Cambodia |
| Paris | g187147 | France |
| London | g186338 | UK |
| New York | g60763 | USA |
| Los Angeles | g32655 | USA |

For cities not in this list, use the Xotelo search API:

```bash
curl -s "https://data.xotelo.com/api/search?q=DESTINATION&limit=5"
```

This returns hotel/location results with their keys.

### 2B: Agoda City ID (for direct Agoda links)

Use the Agoda autocomplete API:

```bash
curl -s "https://www.agoda.com/api/cronos/search/GetUnifiedSuggestResult/3/1/1/0/en-us/?searchText=DESTINATION&origin=US" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
```

Extract `ObjectId` where `PageTypeId == 5` and `SearchType == 1` → this is the **Agoda city ID**.

**Common Agoda City IDs:**

| City | ID |
|------|----|
| Seoul | 14690 |
| Busan | 17172 |
| Tokyo | 5085 |
| Osaka | 9590 |
| Bangkok | 9395 |
| Singapore | 4064 |
| Bali | 17193 |
| Hong Kong | 16808 |

---

## Step 3: Search Hotels (Free Mode - Xotelo API)

> **This is the primary search method.** Xotelo provides free, real-time hotel data with OTA price comparison. No API key required.

### 3-1: Get Hotel List

```bash
curl -s "https://data.xotelo.com/api/list?location_key=${LOCATION_KEY}&limit=${LIMIT}"
```

**Response fields per hotel:**
- `name` - Hotel name
- `key` - Hotel key (needed for price lookup)
- `accommodation_type` - Hotel, Hostel, B&B, etc.
- `review_summary.rating` - Rating out of 5
- `review_summary.count` - Number of reviews
- `price_ranges.minimum` - Lowest price per night (USD)
- `price_ranges.maximum` - Highest price per night (USD)
- `geo.latitude`, `geo.longitude` - GPS coordinates
- `image` - Hotel image URL
- `url` - TripAdvisor URL

### 3-2: Get Real-Time OTA Price Comparison

For each hotel the user is interested in, fetch prices across all OTAs:

```bash
curl -s "https://data.xotelo.com/api/rates?hotel_key=${HOTEL_KEY}&chk_in=${CHECK_IN}&chk_out=${CHECK_OUT}&currency=${CURRENCY}"
```

**Response fields per OTA:**
- `code` - OTA code (BookingCom, Agoda, CtripTA, etc.)
- `name` - OTA display name (Booking.com, Agoda.com, Trip.com, etc.)
- `rate` - Room rate (before tax)
- `tax` - Tax amount

**Common OTAs returned:** Booking.com, Agoda.com, Trip.com, Vio.com, Hotels.com, Expedia

### 3-3: Generate OTA Booking Links

Xotelo does NOT provide booking URLs. Generate direct booking links for each OTA using these verified URL patterns:

```
HOTEL_NAME_ENCODED = URL-encoded hotel name (e.g., "Hotel%20Skypark%20Myeongdong%203")
```

| OTA Code | URL Pattern |
|----------|-------------|
| `BookingCom` | `https://www.booking.com/searchresults.html?ss={HOTEL_NAME_ENCODED}&checkin={CHECK_IN}&checkout={CHECK_OUT}&group_adults={ADULTS}&no_rooms={ROOMS}` |
| `Agoda` | `https://www.agoda.com/search?q={HOTEL_NAME_ENCODED}&city={AGODA_CITY_ID}&checkIn={CHECK_IN}&checkOut={CHECK_OUT}&los={LOS}&rooms={ROOMS}&adults={ADULTS}` |
| `CtripTA` | `https://www.trip.com/hotels/list?keyword={HOTEL_NAME_ENCODED}&checkin={CHECK_IN}&checkout={CHECK_OUT}` |
| `HotelsCom` | `https://www.hotels.com/search.do?q={HOTEL_NAME_ENCODED}&checkin={CHECK_IN}&checkout={CHECK_OUT}` |
| `Expedia` | `https://www.expedia.com/Hotel-Search?destination={HOTEL_NAME_ENCODED}&d1={CHECK_IN}&d2={CHECK_OUT}&adults={ADULTS}&rooms={ROOMS}` |
| `Vio` | `https://www.vio.com/?q={HOTEL_NAME_ENCODED}` |

**Important**: Always include the booking link next to each OTA's price so users can click through and book directly.

### 3-4: Get Price Heatmap (optional)

For flexible date travelers, show which dates are cheapest:

```bash
curl -s "https://data.xotelo.com/api/heatmap?hotel_key=${HOTEL_KEY}&currency=${CURRENCY}"
```

Returns daily price data showing cheap vs expensive days.

---

## Step 4: Agoda Direct Link (Always Provide)

Always generate and provide a direct Agoda search URL, regardless of mode:

```bash
AGODA_URL="https://www.agoda.com/search?city=${AGODA_CITY_ID}&checkIn=${CHECK_IN}&checkOut=${CHECK_OUT}&los=${LOS}&rooms=${ROOMS}&adults=${ADULTS}&currency=${CURRENCY}"
```

Also extract popular areas from Agoda autocomplete response:
- Area results (`PageTypeId == 14` or `15`) with property counts
- Each area has its own search URL

---

## Step 5: Apify Mode (Optional - With API Key)

If `APIFY_API_KEY` is set and the user wants Agoda-specific deep data:

```bash
# Start scraper
curl -s -X POST "https://api.apify.com/v2/acts/knagymate~fast-agoda-scraper/runs?token=${APIFY_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"city":"'"${DESTINATION}"'","checkIn":"'"${CHECK_IN}"'","checkOut":"'"${CHECK_OUT}"'","rooms":'"${ROOMS}"',"adults":'"${ADULTS}"',"currency":"'"${CURRENCY}"'","maxItems":15}'

# Poll for completion (get RUN_ID from response .data.id)
STATUS=$(curl -s "https://api.apify.com/v2/actor-runs/${RUN_ID}?token=${APIFY_API_KEY}" | jq -r '.data.status')

# Fetch results
DATASET_ID=$(curl -s "https://api.apify.com/v2/actor-runs/${RUN_ID}?token=${APIFY_API_KEY}" | jq -r '.data.defaultDatasetId')
curl -s "https://api.apify.com/v2/datasets/${DATASET_ID}/items?token=${APIFY_API_KEY}"
```

Returns 22+ fields per hotel including facilities, detailed pricing, photos, etc.

---

## Step 6: Format and Present Results

### Primary Output (Hotel List + OTA Price Comparison with Booking Links)

For each hotel, show the price comparison table with **clickable booking links** for every OTA:

```
## 🏨 Hotel Search: [Destination]
📅 [CheckIn] → [CheckOut] ([N] nights) | 👤 [Adults] adults | 🛏️ [Rooms] room(s)
Found [X,XXX] hotels. Showing top [N]:

---

### #1 [Hotel Name]
⭐ [Rating]/5 ([Reviews] reviews) | 💰 $[Min]-$[Max]/night

| OTA | Rate | Tax | Total | Book |
|-----|------|-----|-------|------|
| **Agoda.com** | $280 | $53 | **$333** ← Best | [Book on Agoda](agoda_url) |
| Trip.com | $347 | $34 | $381 | [Book on Trip.com](trip_url) |
| Booking.com | $348 | $67 | $415 | [Book on Booking.com](booking_url) |

💡 Save $82 by booking on Agoda vs Booking.com!

---

### #2 [Next Hotel...]
...

---
🔗 **Full Agoda Search**: [direct Agoda search URL]
📍 **Popular Areas**: [Area 1], [Area 2], ...
```

**Key rules for output:**
- ALWAYS include a clickable booking link for each OTA
- Sort OTAs by total price (cheapest first)
- Mark the cheapest OTA as "Best"
- Show savings amount between cheapest and most expensive
- Include the full Agoda city search URL at the bottom

### Sorting Options

- `popularity` (default): As returned by Xotelo
- `price-low`: Sort by `price_ranges.minimum` ascending
- `price-high`: Sort by `price_ranges.maximum` descending
- `rating`: Sort by `review_summary.rating` descending

### Budget Filtering

If `maxBudget` specified:
- Filter hotels where `price_ranges.minimum <= maxBudget`
- Show count of filtered-out hotels
- Suggest cheapest option above budget as "slightly over budget"

## Step 7: Follow-up Actions

After presenting results, offer:
1. "Want detailed OTA price comparison for any of these hotels?"
2. "Should I search with different dates?"
3. "Need recommendations for a specific area?"
4. "Want to see which dates are cheapest? (heatmap)"
5. "Should I open the Agoda search page for you?"

## Error Handling

| Error | Action |
|-------|--------|
| Destination not found | Try Xotelo search API, then ask user to clarify |
| `chk_in is invalid` | Dates may be too far in future; try dates within 1 year |
| No OTA rates available | Hotel may not be listed on OTAs; show TripAdvisor link |
| Apify API timeout | Fall back to Free Mode (Xotelo) automatically |
| Xotelo rate limit | Add 1-second delay between requests; limit to 5 hotels at a time |

## Important Notes

- Xotelo rates are real-time but may differ slightly from booking sites (dynamic pricing)
- Always provide the direct Agoda/Booking.com URL so users can verify and book
- Tax amounts vary by OTA - always show rate + tax for fair comparison
- Do NOT attempt to make bookings - only search and present information
- Be respectful to Xotelo API - add 1s delay between rate lookups for multiple hotels
