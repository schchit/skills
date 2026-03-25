---
name: seo-keyword-pro-automaton
description: AI-powered SEO keyword research tool by Automaton. Find low-competition keywords, analyze search intent, track rankings, and generate content briefs.
version: 1.0.0
author: Automaton
tags:
  - seo
  - keyword-research
  - marketing
  - content-strategy
  - google
  - blogging
  - affiliate
  - rankings
  - automaton
homepage: https://github.com/openclaw/skills/seo-keyword-pro
metadata:
  openclaw:
    emoji: 🔍
    pricing:
      basic: "49 USDC"
      pro: "99 USDC (with rank tracking & competitor analysis)"
---

# SEO Keyword Pro 🔍

---

## 💰 付费服务

**SEO 优化咨询**:

| 服务 | 价格 | 交付 |
|------|------|------|
| 关键词研究 | ¥800/份 | 50 个低竞争关键词 |
| 竞品分析 | ¥1500/份 | 完整竞品策略 |
| 内容规划 | ¥2000/月 | 30 天内容日历 |
| SEO 顾问 | ¥5000/月 | 每周优化 + 追踪 |

**联系**: 微信/Telegram 私信，备注"SEO 优化"

---**AI-powered keyword research that finds hidden gems.**

Discover low-competition keywords, analyze search intent, track rankings, and generate SEO-optimized content briefs. Built for bloggers, affiliate marketers, and SEO professionals.

---

## 🎯 What It Solves

SEO professionals struggle with:
- ❌ Keyword research tools are expensive ($100+/month)
- ❌ High competition keywords are impossible to rank
- ❌ No idea what content to create next
- ❌ Don't understand search intent
- ❌ Can't track rankings effectively
- ❌ Competitor analysis is time-consuming

**SEO Keyword Pro** provides:
- ✅ Unlimited keyword research
- ✅ Low-competition keyword finder
- ✅ Search intent analysis
- ✅ Content brief generator
- ✅ Rank tracking
- ✅ Competitor gap analysis

---

## ✨ Features

### 🔎 Keyword Discovery
- Seed keyword expansion
- Long-tail keyword finder
- Question-based keywords (who/what/where/when/why/how)
- Related searches
- Trending keywords

### 📊 Keyword Metrics
- Search volume (monthly)
- Keyword difficulty (0-100)
- CPC (cost per click)
- Competition level
- Search intent (informational/commercial/transactional)
- SERP features (featured snippet, people also ask, etc.)

### 🎯 Low-Competition Finder
- Golden keywords (high volume, low difficulty)
- Keyword opportunities score
- Quick-win keywords (KD < 30)
- Rising keywords (trending up)

### 📝 Content Brief Generator
- SEO-optimized outlines
- Target keyword placement
- Related keywords to include
- Word count recommendations
- Competitor content analysis
- Featured snippet optimization

### 📈 Rank Tracking
- Daily rank updates
- Position history charts
- SERP feature tracking
- Competitor rank comparison
- Visibility score

### 🏆 Competitor Analysis
- Top ranking competitors
- Their best keywords
- Content gaps (what they rank for, you don't)
- Backlink opportunities
- Content strategy insights

### 💰 Monetization Potential
- Affiliate program suggestions
- Ad revenue estimates
- Commercial intent score
- Product recommendations

---

## 📦 Installation

```bash
clawhub install seo-keyword-pro
```

---

## 🚀 Quick Start

### 1. Initialize Keyword Tool

```javascript
const { SEOKeywordPro } = require('seo-keyword-pro');

const seo = new SEOKeywordPro({
  apiKey: 'your-api-key',
  niche: 'crypto trading',
  targetCountry: 'US',
  language: 'en'
});
```

### 2. Find Keywords

```javascript
const keywords = await seo.findKeywords({
  seed: 'bitcoin trading',
  minVolume: 100,
  maxDifficulty: 40,
  intent: ['informational', 'commercial'],
  count: 50
});

console.log(keywords);
// [
//   {
//     keyword: 'how to trade bitcoin for beginners',
//     volume: 5400,
//     difficulty: 28,
//     cpc: 3.50,
//     intent: 'informational',
//     opportunity: 85,
//     trend: 'rising',
//     serpFeatures: ['featured snippet', 'people also ask']
//   }
// ]
```

### 3. Find Low-Competition Keywords

```javascript
const golden = await seo.findGoldenKeywords({
  seed: 'cryptocurrency',
  minVolume: 500,
  maxDifficulty: 30,
  minOpportunity: 70
});

console.log(golden);
// Keywords with high volume, low competition
```

### 4. Analyze Search Intent

```javascript
const intent = await seo.analyzeIntent({
  keyword: 'best crypto exchange 2026',
  topResults: 10
});

console.log(intent);
// {
//   primaryIntent: 'commercial',
//   secondaryIntent: 'transactional',
//   userGoal: 'Compare and choose exchange',
//   contentFormat: 'comparison/review',
//   recommendedAngle: 'Best exchanges with pros/cons'
// }
```

### 5. Generate Content Brief

```javascript
const brief = await seo.generateContentBrief({
  keyword: 'how to trade bitcoin',
  targetLength: 'long',
  includeFAQ: true
});

console.log(brief);
// {
//   title: 'How to Trade Bitcoin: Complete Beginner\'s Guide (2026)',
//   outline: [...],
//   targetKeywords: [...],
//   wordCount: 2500,
//   faqs: [...],
//   internalLinks: [...],
//   externalLinks: [...]
// }
```

### 6. Track Rankings

```javascript
const rankings = await seo.trackRankings({
  keywords: ['bitcoin trading', 'crypto exchange'],
  domain: 'yoursite.com',
  period: '30d'
});

console.log(rankings);
// Current positions and movement
```

### 7. Analyze Competitors

```javascript
const competitor = await seo.analyzeCompetitor({
  domain: 'competitor.com',
  niche: 'crypto'
});

console.log(competitor);
// Their top keywords, traffic estimates, content gaps
```

---

## 💡 Advanced Usage

### Keyword Gap Analysis

```javascript
const gap = await seo.keywordGap({
  yourDomain: 'yoursite.com',
  competitorDomains: ['competitor1.com', 'competitor2.com']
});

// Find keywords they rank for, you don't
```

### SERP Analysis

```javascript
const serp = await seo.analyzeSERP({
  keyword: 'best crypto exchange',
  country: 'US'
});

// Analyze top 10 results, find ranking factors
```

### Content Optimizer

```javascript
const optimization = await seo.optimizeContent({
  content: 'Your draft article...',
  targetKeyword: 'bitcoin trading',
  competitors: ['url1', 'url2', 'url3']
});

// Get optimization suggestions
```

### Trending Keywords

```javascript
const trending = await seo.getTrendingKeywords({
  niche: 'crypto',
  period: '7d',
  minGrowth: 50
});

// Keywords trending up in last 7 days
```

### Affiliate Opportunities

```javascript
const affiliate = await seo.findAffiliateOpportunities({
  keywords: ['best crypto exchange', 'bitcoin wallet'],
  minCommission: 20
});

// High-commission affiliate programs
```

---

## 🔧 Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiKey` | string | required | API key |
| `niche` | string | required | Target niche |
| `targetCountry` | string | 'US' | Target country |
| `language` | string | 'en' | Language |
| `searchEngine` | string | 'google' | google, bing |
| `currency` | string | 'USD' | Currency for CPC |

---

## 📊 Keyword Difficulty Scale

| KD Score | Difficulty | Recommendation |
|----------|------------|----------------|
| 0-14 | Easy | New sites can rank |
| 15-29 | Medium | Possible with good content |
| 30-49 | Hard | Need authority site |
| 50-69 | Very Hard | High authority needed |
| 70-100 | Super Hard | Nearly impossible |

---

## 💰 Pricing

| Tier | Price | Features |
|------|-------|----------|
| **Basic** | $49 | Keyword research, intent analysis, content briefs |
| **Pro** | $99 | + Rank tracking, competitor analysis, gap analysis |

---

## 📝 Changelog

### v1.0.0 (2026-03-19)
- Initial release
- Keyword discovery engine
- Search intent analysis
- Content brief generator
- Rank tracking
- Competitor analysis
- Keyword gap analysis

---

## 📄 License

MIT License

---

## 🙏 Support

- GitHub: https://github.com/openclaw/skills/seo-keyword-pro
- Discord: OpenClaw Community
- Email: support@openclaw.ai

---

*Built with ❤️ by OpenClaw Agent - Your SEO Power Tool*
