# AI Airbnb and Short Term Rental Growth Engine: Scrape Markets, Optimize Pricing and Outperform Every Host in Your Area

**Display Name:** AI Airbnb and Short Term Rental Growth Engine  
**Version:** 1.0.0
**Author:** @g4dr

## Overview

Short-term rentals are a $100B+ market and most hosts leave money on the table because they price by gut feeling and ignore their competition. This skill scrapes Airbnb, Vrbo and Booking.com listings in any city, analyzes pricing patterns, occupancy signals, review sentiment and amenity gaps, then generates a data-driven strategy to maximize your revenue per night and produce marketing content that makes your listing stand out.

Works for: Airbnb hosts, property managers, short-term rental investors, vacation rental agencies, co-hosting businesses, real estate investors evaluating STR markets.

Powered by: [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI

---

## What This Skill Does

- Scrape all Airbnb, Vrbo and Booking.com listings in any city or neighborhood with pricing, ratings, amenities and availability
- Analyze competitor pricing by property type, bedroom count, location and season
- Detect pricing gaps where you can charge more based on amenity advantages
- Mine guest reviews to find what travelers love and hate in your area
- Calculate revenue potential for any market before you invest
- Score your listing competitiveness vs every nearby property
- Generate optimized listing titles, descriptions and photo captions using top-performer language
- Create a dynamic pricing strategy with day-of-week and seasonal adjustments
- Produce property showcase and marketing videos for social media and direct booking sites
- Build a monthly market report showing trends, new supply and demand shifts

---

## Step 1: Set Up Your Research Engine

This skill uses [Apify](https://www.apify.com?fpr=dx06p) to scrape rental platform data.

1. Create your free account at [Apify](https://www.apify.com?fpr=dx06p)
2. Go to **Settings > Integrations** and copy your Personal API Token
3. Store it securely:
   ```bash
   export APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxx
   ```

---

## Step 2: Set Up Your Video Engine

This skill uses [InVideo AI](https://invideo.sjv.io/TBB) to produce property marketing videos.

1. Create your account at [InVideo AI](https://invideo.sjv.io/TBB)
2. Choose a plan with API access
3. Copy your API key:
   ```bash
   export INVIDEO_API_KEY=iv_api_xxxxxxxxxxxxxxxx
   ```

---

## Step 3: Install Dependencies

```bash
npm install apify-client axios
```

---

## Apify Actors Used

| Actor | What It Scrapes | Data Extracted |
|---|---|---|
| [Apify Airbnb Scraper](https://www.apify.com?fpr=dx06p) | Airbnb listings by location | Price, rating, reviews, amenities, capacity, superhost status, availability |
| [Apify Booking.com Scraper](https://www.apify.com?fpr=dx06p) | Booking.com properties | Price, rating, review count, facilities, location score |
| [Apify Google Maps Scraper](https://www.apify.com?fpr=dx06p) | Local attractions and restaurants | Distance to points of interest, walkability data |
| [Apify Google Maps Reviews Scraper](https://www.apify.com?fpr=dx06p) | Area reviews and sentiment | What tourists love about the neighborhood |
| [Apify Instagram Scraper](https://www.apify.com?fpr=dx06p) | Local travel content | Trending spots, photo-worthy locations, influencer activity |
| [Apify Reddit Scraper](https://www.apify.com?fpr=dx06p) | Travel subreddits for the city | Real traveler opinions, hidden tips, complaints |
| [Apify Google Trends Scraper](https://www.apify.com?fpr=dx06p) | Search interest for the destination | Seasonal demand patterns, rising interest |
| [Apify TikTok Scraper](https://www.apify.com?fpr=dx06p) | Travel TikTok for the area | Viral location content, trending travel formats |

---

## Examples

### Scrape All Competitor Listings in Your Market

```javascript
import ApifyClient from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });

async function scrapeMarket(city, propertyType = 'entire_home', maxListings = 100) {
  const run = await client.actor("apify/airbnb-scraper").call({
    locationQuery: city,
    maxListings: maxListings,
    propertyType: propertyType,
    currency: "USD",
    checkIn: new Date(Date.now() + 14 * 86400000).toISOString().split('T')[0],
    checkOut: new Date(Date.now() + 16 * 86400000).toISOString().split('T')[0]
  });

  const { items } = await run.dataset().getData();

  return items.map(listing => ({
    name: listing.name,
    price: listing.pricing?.rate?.amount || listing.price,
    currency: listing.pricing?.rate?.currency || 'USD',
    rating: listing.rating,
    reviewCount: listing.reviewCount || listing.numberOfReviews,
    bedrooms: listing.bedrooms,
    bathrooms: listing.bathrooms,
    capacity: listing.personCapacity || listing.guests,
    isSuperhost: listing.isSuperhost || false,
    amenities: listing.amenities || [],
    neighborhood: listing.neighborhood || listing.location,
    instantBook: listing.instantBook || false,
    url: listing.url,
    photos: listing.photos?.length || 0
  }));
}

const market = await scrapeMarket("Austin, TX", "entire_home", 100);
console.log(`Found ${market.length} listings in Austin`);
```

---

### Market Pricing Analysis

```javascript
function analyzeMarketPricing(listings) {
  const prices = listings.filter(l => l.price > 0).map(l => l.price);
  prices.sort((a, b) => a - b);

  const avg = Math.round(prices.reduce((s, p) => s + p, 0) / prices.length);
  const median = prices[Math.floor(prices.length / 2)];
  const p25 = prices[Math.floor(prices.length * 0.25)];
  const p75 = prices[Math.floor(prices.length * 0.75)];

  // Price by bedroom count
  const byBedroom = {};
  listings.forEach(l => {
    const br = l.bedrooms || 'Studio';
    if (!byBedroom[br]) byBedroom[br] = [];
    if (l.price > 0) byBedroom[br].push(l.price);
  });

  const bedroomPricing = {};
  Object.entries(byBedroom).forEach(([br, prices]) => {
    bedroomPricing[br] = {
      avg: Math.round(prices.reduce((s, p) => s + p, 0) / prices.length),
      min: Math.min(...prices),
      max: Math.max(...prices),
      count: prices.length
    };
  });

  // Superhost premium
  const superhosts = listings.filter(l => l.isSuperhost && l.price > 0);
  const regular = listings.filter(l => !l.isSuperhost && l.price > 0);
  const superhostAvg = superhosts.length > 0
    ? Math.round(superhosts.reduce((s, l) => s + l.price, 0) / superhosts.length)
    : 0;
  const regularAvg = regular.length > 0
    ? Math.round(regular.reduce((s, l) => s + l.price, 0) / regular.length)
    : 0;

  return {
    totalListings: listings.length,
    priceStats: { avg, median, p25, p75, min: prices[0], max: prices[prices.length - 1] },
    bedroomPricing,
    superhostPremium: superhostAvg > 0 && regularAvg > 0
      ? Math.round((superhostAvg - regularAvg) / regularAvg * 100)
      : 0,
    superhostAvg,
    regularAvg,
    avgRating: Math.round(
      listings.filter(l => l.rating).reduce((s, l) => s + l.rating, 0) /
      listings.filter(l => l.rating).length * 100
    ) / 100,
    avgPhotos: Math.round(listings.reduce((s, l) => s + l.photos, 0) / listings.length)
  };
}

const pricing = analyzeMarketPricing(market);
console.log(`Market avg: $${pricing.priceStats.avg}/night`);
console.log(`Superhost premium: +${pricing.superhostPremium}%`);
console.log("Pricing by bedroom:", pricing.bedroomPricing);
```

---

### Competitive Listing Score (Your Listing vs Market)

```javascript
function scoreYourListing(yourListing, marketData, pricingData) {
  let score = 50;

  // Price positioning
  const pricePercentile = marketData.filter(l => l.price < yourListing.price).length / marketData.length * 100;
  if (pricePercentile >= 30 && pricePercentile <= 70) score += 10; // sweet spot
  if (pricePercentile < 20) score += 5; // too cheap, leaving money
  if (pricePercentile > 85) score -= 10; // overpriced risk

  // Rating advantage
  if (yourListing.rating >= 4.9) score += 15;
  else if (yourListing.rating >= 4.7) score += 10;
  else if (yourListing.rating >= 4.5) score += 5;
  else if (yourListing.rating < 4.0) score -= 15;

  // Review count (social proof)
  if (yourListing.reviewCount >= 100) score += 10;
  else if (yourListing.reviewCount >= 50) score += 7;
  else if (yourListing.reviewCount >= 20) score += 3;
  else score -= 5;

  // Superhost status
  if (yourListing.isSuperhost) score += 8;

  // Photo count
  if (yourListing.photos >= 30) score += 5;
  else if (yourListing.photos < 10) score -= 10;

  // Instant book
  if (yourListing.instantBook) score += 3;

  // Amenity advantages
  const topAmenities = ['pool', 'hot tub', 'wifi', 'kitchen', 'washer', 'parking', 'gym', 'ev charger'];
  const yourAmenities = (yourListing.amenities || []).map(a => a.toLowerCase());
  const amenityScore = topAmenities.filter(a => yourAmenities.some(ya => ya.includes(a))).length;
  score += amenityScore * 2;

  return {
    score: Math.min(100, Math.max(0, score)),
    pricePercentile: Math.round(pricePercentile),
    amenityAdvantages: amenityScore,
    improvements: [
      yourListing.photos < 20 ? 'Add more photos (aim for 30+)' : null,
      !yourListing.isSuperhost ? 'Work toward Superhost status' : null,
      !yourListing.instantBook ? 'Enable Instant Book for more visibility' : null,
      yourListing.reviewCount < 20 ? 'Focus on getting more reviews (offer early check-in for review)' : null,
      pricePercentile > 80 ? `Consider dropping price to $${pricingData.priceStats.median} (market median)` : null,
      pricePercentile < 25 ? `You may be underpriced. Market avg is $${pricingData.priceStats.avg}. Test $${Math.round(pricingData.priceStats.avg * 0.9)}` : null
    ].filter(Boolean)
  };
}
```

---

### Review Sentiment Mining (What Guests Want)

```javascript
async function mineGuestSentiment(city) {
  // Scrape Reddit travel discussions
  const rdRun = await client.actor("apify/reddit-search-scraper").call({
    queries: [`airbnb ${city}`, `where to stay ${city}`, `best neighborhood ${city}`],
    maxItems: 50
  });

  // Scrape Google Maps reviews for the area
  const mapsRun = await client.actor("compass~crawler-google-places").call({
    searchStringsArray: [`tourist attractions in ${city}`],
    maxCrawledPlacesPerSearch: 20,
    language: "en"
  });

  const [reddit, maps] = await Promise.all([
    rdRun.dataset().getData(),
    mapsRun.dataset().getData()
  ]);

  // Extract what travelers care about
  const travelKeywords = {
    location: ['walkable', 'close to', 'near', 'downtown', 'safe', 'quiet', 'parking'],
    amenities: ['wifi', 'kitchen', 'washer', 'pool', 'hot tub', 'coffee', 'workspace'],
    experience: ['clean', 'cozy', 'modern', 'spacious', 'view', 'decor', 'comfortable'],
    issues: ['noisy', 'dirty', 'bug', 'smell', 'broken', 'uncomfortable', 'misleading']
  };

  const mentions = {};
  Object.entries(travelKeywords).forEach(([category, keywords]) => {
    mentions[category] = {};
    keywords.forEach(kw => {
      const count = reddit.items.filter(p =>
        ((p.title || '') + (p.selftext || '')).toLowerCase().includes(kw)
      ).length;
      if (count > 0) mentions[category][kw] = count;
    });
  });

  // Top neighborhoods mentioned
  const neighborhoods = reddit.items
    .filter(p => (p.title || '').toLowerCase().includes('neighborhood') || (p.title || '').toLowerCase().includes('area'))
    .map(p => ({ title: p.title, score: p.score }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 5);

  return {
    guestPriorities: mentions,
    topNeighborhoods: neighborhoods,
    nearbyAttractions: maps.items.slice(0, 10).map(p => ({
      name: p.title,
      rating: p.totalScore,
      reviews: p.reviewsCount,
      category: p.categoryName
    }))
  };
}

const sentiment = await mineGuestSentiment("Austin, TX");
console.log("Guest priorities:", sentiment.guestPriorities);
```

---

### Generate AI Listing Optimization

```javascript
import axios from 'axios';

async function optimizeListing(yourListing, marketData, pricingData, sentiment) {
  const topListings = marketData
    .filter(l => l.rating >= 4.9 && l.reviewCount >= 50)
    .sort((a, b) => b.reviewCount - a.reviewCount)
    .slice(0, 5);

  const prompt = `You are an Airbnb listing optimization expert. Rewrite this listing to maximize bookings.

CURRENT LISTING:
- Title: ${yourListing.name}
- Price: $${yourListing.price}/night
- Bedrooms: ${yourListing.bedrooms}
- Rating: ${yourListing.rating}/5 (${yourListing.reviewCount} reviews)
- Amenities: ${(yourListing.amenities || []).join(', ')}

MARKET DATA:
- Average price: $${pricingData.priceStats.avg}/night
- Median price: $${pricingData.priceStats.median}/night
- Your price percentile: top ${100 - Math.round(marketData.filter(l => l.price < yourListing.price).length / marketData.length * 100)}%

TOP COMPETITOR TITLES:
${topListings.map(l => `"${l.name}" (${l.rating}/5, ${l.reviewCount} reviews)`).join('\n')}

WHAT GUESTS SEARCH FOR:
${JSON.stringify(sentiment.guestPriorities, null, 2)}

GENERATE:
1. Optimized Title (max 50 characters, include top search terms)
2. Optimized Description (250 words, mention amenities guests care about first)
3. 5 Photo Caption suggestions (for the 5 most important photos)
4. Pricing Recommendation with day-of-week adjustments
5. 3 Quick Wins to improve ranking immediately

Write like a top-performing host, not a marketer. Warm, specific, confident.`;

  const { data } = await axios.post('https://api.anthropic.com/v1/messages', {
    model: "claude-sonnet-4-20250514",
    max_tokens: 1500,
    messages: [{ role: "user", content: prompt }]
  }, {
    headers: {
      'x-api-key': process.env.CLAUDE_API_KEY,
      'anthropic-version': '2023-06-01'
    }
  });

  return data.content[0].text;
}
```

---

### Produce Property Marketing Video

```javascript
const invideo = axios.create({
  baseURL: 'https://api.invideo.io/v1',
  headers: {
    'Authorization': `Bearer ${process.env.INVIDEO_API_KEY}`,
    'Content-Type': 'application/json'
  }
});

async function producePropertyVideo(listing, highlights) {
  const script = `Welcome to ${listing.name}. Located in the heart of ${listing.neighborhood || 'the city'}, this ${listing.bedrooms}-bedroom retreat is rated ${listing.rating} out of 5 by ${listing.reviewCount} guests. ${highlights.join('. ')}. Whether you are here for business or exploring the city, this is your home base. Book now and see why guests keep coming back.`;

  const response = await invideo.post('/videos/generate', {
    script,
    format: "9:16",
    duration: "short",
    style: "cinematic",
    voiceover: {
      enabled: true,
      voice: "en-US-female-1",
      speed: 1.0
    },
    captions: {
      enabled: true,
      style: "bold-bottom",
      highlight: true
    },
    music: {
      enabled: true,
      mood: "chill",
      volume: 0.3
    }
  });

  const videoId = response.data.videoId;

  let exportUrl = null;
  while (!exportUrl) {
    await new Promise(r => setTimeout(r, 5000));
    const status = await invideo.get(`/videos/${videoId}/status`);
    if (status.data.state === "completed") exportUrl = status.data.exportUrl;
    if (status.data.state === "failed") throw new Error("Video generation failed");
  }

  return { videoId, exportUrl };
}
```

---

### Revenue Potential Calculator (For New Markets)

```javascript
function calculateRevenuePotential(pricingData, occupancyEstimate = 0.65) {
  const avgNightlyRate = pricingData.priceStats.avg;
  const medianRate = pricingData.priceStats.median;

  const monthly = {
    conservative: Math.round(medianRate * 30 * 0.50), // 50% occupancy
    moderate: Math.round(avgNightlyRate * 30 * occupancyEstimate), // 65% occupancy
    optimistic: Math.round(pricingData.priceStats.p75 * 30 * 0.80) // 80% occupancy at top quartile
  };

  const annual = {
    conservative: monthly.conservative * 12,
    moderate: monthly.moderate * 12,
    optimistic: monthly.optimistic * 12
  };

  return {
    avgNightlyRate,
    medianRate,
    topQuartileRate: pricingData.priceStats.p75,
    estimatedOccupancy: `${occupancyEstimate * 100}%`,
    monthlyRevenue: monthly,
    annualRevenue: annual,
    breakEvenNights: (nights) => Math.ceil(nights / avgNightlyRate),
    marketSize: `${pricingData.totalListings} active listings`
  };
}

const revenue = calculateRevenuePotential(pricing);
console.log(`Monthly revenue potential: $${revenue.monthlyRevenue.conservative} - $${revenue.monthlyRevenue.optimistic}`);
console.log(`Annual: $${revenue.annualRevenue.conservative} - $${revenue.annualRevenue.optimistic}`);
```

---

### Full Pipeline: Market Research, Optimize, Produce

```javascript
import { writeFileSync } from 'fs';

async function fullSTRPipeline(city, yourListingUrl = null) {
  console.log(`Starting STR Growth Pipeline for ${city}...`);

  // 1. Scrape market
  const market = await scrapeMarket(city, 'entire_home', 100);
  console.log(`Step 1: ${market.length} listings scraped`);

  // 2. Analyze pricing
  const pricing = analyzeMarketPricing(market);
  console.log(`Step 2: Market avg $${pricing.priceStats.avg}/night`);

  // 3. Mine guest sentiment
  const sentiment = await mineGuestSentiment(city);
  console.log(`Step 3: Guest priorities analyzed`);

  // 4. Revenue potential
  const revenue = calculateRevenuePotential(pricing);
  console.log(`Step 4: Annual potential $${revenue.annualRevenue.conservative} - $${revenue.annualRevenue.optimistic}`);

  // 5. Generate optimization (if listing provided)
  let optimization = null;
  if (yourListingUrl) {
    const yourListing = market.find(l => l.url === yourListingUrl) || market[0];
    optimization = await optimizeListing(yourListing, market, pricing, sentiment);
    console.log(`Step 5: Listing optimized`);
  }

  // 6. Export
  const report = {
    city,
    generatedAt: new Date().toISOString(),
    marketOverview: pricing,
    revenuePotential: revenue,
    guestSentiment: sentiment,
    topListings: market.sort((a, b) => b.reviewCount - a.reviewCount).slice(0, 20),
    optimization
  };

  const filename = `str-market-${city.replace(/[\s,]+/g, '-')}-${Date.now()}.json`;
  writeFileSync(filename, JSON.stringify(report, null, 2));
  console.log(`Full report exported to ${filename}`);

  return report;
}

await fullSTRPipeline("Austin, TX");
```

---

## What Makes This Different

| Feature | Manual Research | This Skill |
|---|---|---|
| Competitor analysis | Browse listings one by one | Scrape 100+ listings with full data |
| Pricing strategy | Copy nearby listings | Statistical analysis with percentiles and bedroom breakdown |
| Guest insights | Read your own reviews | Mine Reddit + Google for area-wide sentiment |
| Listing optimization | Generic Airbnb tips | AI-rewritten title, description, captions from real data |
| Revenue projections | Spreadsheet guesses | 3-tier model based on market data |
| Marketing | None | AI-produced property showcase videos |

---

## Pro Tips

1. Run the market scrape before and after peak season to see how supply changes
2. Listings with 30+ photos get 2x more bookings. Invest in photography
3. Check what amenities top-rated listings have that you do not. Adding "workspace" or "EV charger" can justify $20-40 more per night
4. Use the Reddit sentiment data in your listing description. If travelers mention "walkable to downtown" as a priority, make that your first sentence
5. Price 5 to 10% below market for your first 10 bookings to build reviews fast, then raise to market rate
6. Cross-post your property video on TikTok with location hashtags. Direct booking inquiries from social media have zero platform fees

---

## Cost Estimate

| Action | Tool | Cost |
|---|---|---|
| Scrape 100 Airbnb listings | [Apify](https://www.apify.com?fpr=dx06p) | ~$0.15 |
| Scrape Booking.com comparison | [Apify](https://www.apify.com?fpr=dx06p) | ~$0.10 |
| Guest sentiment (Reddit + Maps) | [Apify](https://www.apify.com?fpr=dx06p) | ~$0.12 |
| Listing optimization | Claude AI | ~$0.05 |
| Property video | [InVideo AI](https://invideo.sjv.io/TBB) | Plan dependent |
| Full pipeline | Total | Under $1 for complete market analysis |

---

## Error Handling

```javascript
try {
  const run = await client.actor("apify/airbnb-scraper").call(input);
  const dataset = await run.dataset().getData();
  return dataset.items;
} catch (error) {
  if (error.statusCode === 401) throw new Error("Invalid Apify token. Get yours at https://www.apify.com?fpr=dx06p");
  if (error.statusCode === 429) throw new Error("Rate limit. Reduce batch size.");
  throw error;
}
```

---

## Requirements

- An [Apify](https://www.apify.com?fpr=dx06p) account with API token
- An [InVideo AI](https://invideo.sjv.io/TBB) account for video production
- Claude API key for listing optimization
- Node.js 18+ with `apify-client` and `axios`
