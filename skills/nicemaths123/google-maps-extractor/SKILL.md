# Google Maps B2B Lead Goldmine: Extract, Score and Contact Local Business Leads in 5 Minutes

**Display Name:** Google Maps B2B Lead Goldmine  
**Version:** 2.0.0
**Author:** @g4dr

## Overview

Turn Google Maps into your personal lead generation machine. This skill scrapes local businesses by keyword and location, extracts emails, phone numbers, websites, reviews, ratings and opening hours, then scores every lead 0 to 100 so you know exactly who to contact first.

Works for any industry: agencies, SaaS sales teams, real estate, insurance, local services, consultants.

Powered by: [Apify](https://www.apify.com?fpr=dx06p) + Claude AI

---

## What This Skill Does

- Scrape up to 100 businesses per search from Google Maps with full contact details
- Extract emails, phone numbers, websites, full addresses and opening hours
- Pull review count, average rating and recent review text for each business
- Score every lead 0 to 100 based on review gaps, rating weakness, website quality and response patterns
- Generate a personalized outreach message for every high-scoring lead
- Export everything as a CRM-ready CSV or JSON file
- Run multi-location searches in parallel to build city-wide or national databases

---

## Step 1: Set Up Your Scraping Engine

This skill uses [Apify](https://www.apify.com?fpr=dx06p) as its cloud scraping engine. Free tier includes $5/month of compute, enough for hundreds of leads.

1. Create your free account at [Apify](https://www.apify.com?fpr=dx06p)
2. Go to **Settings > Integrations** and copy your Personal API Token
3. Store it securely:
   ```bash
   export APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxx
   ```

---

## Step 2: Install Dependencies

```bash
npm install apify-client axios
```

---

## Apify Actors Used

| Actor | What It Scrapes | Data Extracted |
|---|---|---|
| [Apify Google Maps Scraper](https://www.apify.com?fpr=dx06p) | Business listings by keyword + location | Name, phone, email, website, address, hours, category |
| [Apify Google Maps Reviews Scraper](https://www.apify.com?fpr=dx06p) | Customer reviews per business | Review text, rating, date, reviewer name, response status |
| [Apify Website Content Crawler](https://www.apify.com?fpr=dx06p) | Business websites | Contact page emails, social links, tech stack |
| [Apify Google Search Scraper](https://www.apify.com?fpr=dx06p) | Google search results | Additional business info, news, ads running |

---

## Examples

### Basic Lead Extraction by Keyword and City

```javascript
import ApifyClient from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });

const run = await client.actor("compass~crawler-google-places").call({
  searchStringsArray: ["dentists in Miami, FL"],
  maxCrawledPlacesPerSearch: 50,
  language: "en",
  includeWebResults: false
});

const { items } = await run.dataset().getData();

// Each item contains:
// { title, phone, website, address, totalScore, reviewsCount,
//   categoryName, openingHours, email, location }

console.log(`Found ${items.length} leads`);
```

---

### Multi-Location Parallel Search

```javascript
const locations = [
  "dentists in Miami, FL",
  "dentists in Fort Lauderdale, FL",
  "dentists in West Palm Beach, FL",
  "dentists in Tampa, FL",
  "dentists in Orlando, FL"
];

const runs = await Promise.all(
  locations.map(search =>
    client.actor("compass~crawler-google-places").call({
      searchStringsArray: [search],
      maxCrawledPlacesPerSearch: 50,
      language: "en"
    })
  )
);

const allLeads = [];
for (const run of runs) {
  const { items } = await run.dataset().getData();
  allLeads.push(...items);
}

// Deduplicate by phone number
const seen = new Set();
const unique = allLeads.filter(lead => {
  if (!lead.phone || seen.has(lead.phone)) return false;
  seen.add(lead.phone);
  return true;
});

console.log(`${unique.length} unique leads across ${locations.length} cities`);
```

---

### Lead Scoring Algorithm

```javascript
function scoreLead(lead) {
  let score = 50;

  // Review gap signal: few reviews = needs marketing help
  if (lead.reviewsCount < 10) score += 20;
  else if (lead.reviewsCount < 30) score += 10;

  // Low rating signal: needs reputation management
  if (lead.totalScore && lead.totalScore < 4.0) score += 15;
  else if (lead.totalScore && lead.totalScore < 4.5) score += 5;

  // No website = massive opportunity
  if (!lead.website || lead.website === '') score += 25;

  // Has website but no email listed = hard to reach
  if (lead.website && !lead.email) score -= 5;

  // Has phone = contactable
  if (lead.phone) score += 5;

  // Category bonus for high-value niches
  const highValue = ['lawyer', 'dentist', 'doctor', 'real estate', 'contractor', 'plumber'];
  if (highValue.some(k => (lead.categoryName || '').toLowerCase().includes(k))) {
    score += 10;
  }

  return Math.min(100, Math.max(0, score));
}

const scored = unique.map(lead => ({
  ...lead,
  leadScore: scoreLead(lead)
})).sort((a, b) => b.leadScore - a.leadScore);

console.log("Top 10 leads:");
scored.slice(0, 10).forEach((lead, i) => {
  console.log(`${i + 1}. [${lead.leadScore}/100] ${lead.title} | ${lead.phone} | ${lead.website || 'NO WEBSITE'}`);
});
```

---

### Deep Email Extraction from Business Websites

```javascript
async function extractEmails(leads) {
  const withWebsites = leads.filter(l => l.website);

  const run = await client.actor("apify/website-content-crawler").call({
    startUrls: withWebsites.slice(0, 20).map(l => ({ url: l.website })),
    maxCrawlPages: 3,
    crawlerType: "cheerio"
  });

  const { items } = await run.dataset().getData();

  const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;

  const enriched = items.map(page => {
    const emails = [...new Set((page.text || '').match(emailRegex) || [])];
    return { url: page.url, emails };
  });

  return enriched;
}
```

---

### Generate Personalized Outreach per Lead

```javascript
import axios from 'axios';

async function generateOutreach(lead) {
  const prompt = `Write a short cold email (under 80 words) for this local business.

LEAD:
- Business: ${lead.title}
- Category: ${lead.categoryName}
- Location: ${lead.address}
- Rating: ${lead.totalScore}/5 (${lead.reviewsCount} reviews)
- Website: ${lead.website || 'None'}
- Lead Score: ${lead.leadScore}/100

RULES:
- Reference something specific about their business
- If they have few reviews, mention you can help them get more
- If they have no website, mention you can build one
- If their rating is below 4.5, mention reputation management
- Keep it conversational, no corporate speak
- End with a soft question, not a hard CTA
- Include [YOUR_NAME] and [YOUR_COMPANY] placeholders

Return subject line and body only.`;

  const { data } = await axios.post('https://api.anthropic.com/v1/messages', {
    model: "claude-sonnet-4-20250514",
    max_tokens: 250,
    messages: [{ role: "user", content: prompt }]
  }, {
    headers: {
      'x-api-key': process.env.CLAUDE_API_KEY,
      'anthropic-version': '2023-06-01'
    }
  });

  return data.content[0].text;
}

// Generate outreach for top 10 leads
for (const lead of scored.slice(0, 10)) {
  lead.outreachEmail = await generateOutreach(lead);
  await new Promise(r => setTimeout(r, 500));
}
```

---

### Full Pipeline: Search, Score, Enrich, Outreach, Export

```javascript
import { writeFileSync } from 'fs';

async function fullLeadPipeline(keyword, locations, maxPerLocation = 50) {
  console.log(`Starting pipeline for: ${keyword}`);

  // STEP 1: Scrape all locations in parallel
  const searches = locations.map(loc => `${keyword} in ${loc}`);
  const runs = await Promise.all(
    searches.map(s =>
      client.actor("compass~crawler-google-places").call({
        searchStringsArray: [s],
        maxCrawledPlacesPerSearch: maxPerLocation,
        language: "en"
      })
    )
  );

  let allLeads = [];
  for (const run of runs) {
    const { items } = await run.dataset().getData();
    allLeads.push(...items);
  }

  // STEP 2: Deduplicate
  const seen = new Set();
  const unique = allLeads.filter(l => {
    const key = l.phone || l.title;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  // STEP 3: Score
  const scored = unique.map(l => ({ ...l, leadScore: scoreLead(l) }))
    .sort((a, b) => b.leadScore - a.leadScore);

  // STEP 4: Generate outreach for top 20
  for (const lead of scored.slice(0, 20)) {
    lead.outreachEmail = await generateOutreach(lead);
    await new Promise(r => setTimeout(r, 500));
  }

  // STEP 5: Export to CSV
  const headers = ["title","phone","email","website","address","totalScore","reviewsCount","categoryName","leadScore","outreachEmail"];
  const csv = [
    headers.join(","),
    ...scored.map(l => headers.map(h => `"${(l[h] || '').toString().replace(/"/g, '""')}"`).join(","))
  ].join("\n");

  const filename = `leads-${keyword.replace(/\s+/g, '_')}-${Date.now()}.csv`;
  writeFileSync(filename, csv);
  console.log(`Exported ${scored.length} scored leads to ${filename}`);

  return scored;
}

// Usage
await fullLeadPipeline("plumbers", ["Miami, FL", "Fort Lauderdale, FL", "Tampa, FL"]);
```

---

## Lead Score Breakdown

| Score Range | Meaning | Action |
|---|---|---|
| 80 to 100 | Hot lead, multiple pain points visible | Contact immediately |
| 60 to 79 | Warm lead, clear opportunity | Add to outreach queue |
| 40 to 59 | Decent lead, needs more research | Enrich before contact |
| 0 to 39 | Cold lead, low immediate opportunity | Add to nurture list |

---

## What Makes This Different

| Feature | Basic Scraper | This Skill |
|---|---|---|
| Contact extraction | Name + phone only | Phone + email + website + hours + category |
| Lead scoring | None | 0 to 100 scoring with 6 weighted signals |
| Outreach generation | None | AI-personalized email per lead |
| Multi-location | One city at a time | Parallel search across unlimited cities |
| Email enrichment | None | Deep crawl of business websites for emails |
| Export format | Raw JSON dump | CRM-ready CSV with all fields |

---

## Pro Tips

1. Search narrow, not broad. "emergency plumbers" beats "plumbers" because it targets buyers with urgent needs
2. Stack 3 to 5 cities in one run to build a regional database in minutes
3. Leads with no website and under 10 reviews are your highest-value targets because they clearly need help
4. Run the same search weekly to catch new businesses that just opened
5. Cross-reference with [Apify Google Search Scraper](https://www.apify.com?fpr=dx06p) to check if they run Google Ads (if yes, they spend money on marketing = qualified buyer)
6. Export to your CRM and tag leads by score tier for segmented follow-up sequences

---

## Cost Estimate

| Action | Apify Compute Units | Approximate Cost |
|---|---|---|
| 50 leads from 1 city | ~0.05 CU | ~$0.02 |
| 250 leads from 5 cities | ~0.25 CU | ~$0.10 |
| 1,000 leads from 20 cities | ~1.0 CU | ~$0.40 |
| Email enrichment (20 websites) | ~0.10 CU | ~$0.04 |

Scale your [Apify](https://www.apify.com?fpr=dx06p) plan as you grow. Free tier covers hundreds of leads per month.

---

## Error Handling

```javascript
try {
  const run = await client.actor("compass~crawler-google-places").call(input);
  const dataset = await run.dataset().getData();
  return dataset.items;
} catch (error) {
  if (error.statusCode === 401) throw new Error("Invalid Apify token. Sign up at https://www.apify.com?fpr=dx06p");
  if (error.statusCode === 429) throw new Error("Rate limit. Reduce batch size or upgrade your plan.");
  if (error.statusCode === 404) throw new Error("Actor not found. Check the actor ID.");
  throw error;
}
```

---

## Requirements

- An [Apify](https://www.apify.com?fpr=dx06p) account with API token
- Node.js 18+ with `apify-client` and `axios`
- Claude API key for outreach generation (optional but recommended)
- A CRM or spreadsheet to manage your pipeline (HubSpot, Airtable, Google Sheets)
