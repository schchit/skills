---
name: social-content-pro-automaton
description: AI-powered social media content generator by Automaton. Viral content creation for TikTok, Instagram, Twitter, LinkedIn, Xiaohongshu.
version: 1.0.0
author: Automaton
tags:
  - social-media
  - content-creation
  - marketing
  - tiktok
  - instagram
  - twitter
  - linkedin
  - xiaohongshu
  - viral
  - automaton
homepage: https://github.com/openclaw/skills/social-content-pro
metadata:
  openclaw:
    emoji: 📱
    pricing:
      basic: "39 USDC"
      pro: "79 USDC (with analytics & auto-post)"
---

# Social Content Pro 📱

---

## 💰 付费服务

**社交媒体代运营**:

| 服务 | 价格 | 交付 |
|------|------|------|
| 单平台内容 | ¥2000/月 | 30 条原创内容 |
| 多平台分发 | ¥5000/月 | 5 平台同步 |
| 爆款文案 | ¥500/条 | 定制化爆款文案 |
| 全案代运营 | ¥15000/月 | 策划 + 内容 + 运营 |

**联系**: 微信/Telegram 私信，备注"社媒代运营"

---**AI-powered viral content generator for all social platforms.**

Create engaging posts for TikTok, Instagram, Twitter, LinkedIn, and Xiaohongshu in seconds. Optimize hashtags, schedule posts, and track performance.

---

## 🎯 What It Solves

Content creators struggle with:
- ❌ Writer's block - what to post today?
- ❌ Multi-platform management (5+ platforms)
- ❌ Hashtag research is time-consuming
- ❌ Inconsistent posting schedule
- ❌ Not knowing what content goes viral
- ❌ No time for engagement

**Social Content Pro** provides:
- ✅ AI-generated content ideas daily
- ✅ Platform-specific optimization
- ✅ Viral hashtag suggestions
- ✅ Auto-scheduling
- ✅ Performance analytics
- ✅ Competitor analysis

---

## ✨ Features

### 🎬 Multi-Platform Content Generation
- **TikTok** - Short video scripts, hooks, captions
- **Instagram** - Posts, Stories, Reels captions
- **Twitter/X** - Threads, tweets, engagement hooks
- **LinkedIn** - Professional posts, articles
- **Xiaohongshu** - 小红书笔记 (Chinese market)
- **YouTube** - Video titles, descriptions, tags

### 🔥 Viral Content Analyzer
- Trending topics detection
- Viral pattern recognition
- Best posting times
- Content format recommendations
- Hook score prediction

### #️⃣ Smart Hashtag Engine
- Platform-specific hashtags
- Competition analysis (low/med/high)
- Trending hashtags in your niche
- Hashtag performance tracking
- Optimal hashtag count per platform

### 📅 Content Calendar
- 30-day content planning
- Auto-scheduling
- Best time to post recommendations
- Content mix optimization
- Holiday/event integration

### 📊 Performance Analytics
- Engagement rate tracking
- Follower growth analysis
- Best performing content types
- Audience insights
- ROI tracking

### 🎯 Audience Targeting
- Ideal customer profile
- Content personalization
- A/B testing suggestions
- Audience growth strategies

### 🔄 Auto-Posting (Pro)
- Connect social accounts
- Schedule posts in advance
- Auto-publish at optimal times
- Cross-platform posting
- Content recycling

---

## 📦 Installation

```bash
clawhub install social-content-pro
```

---

## 🚀 Quick Start

### 1. Initialize Content Generator

```javascript
const { SocialContentPro } = require('social-content-pro');

const creator = new SocialContentPro({
  apiKey: 'your-api-key',
  niche: 'crypto trading',  // Your content niche
  platforms: ['tiktok', 'twitter', 'xiaohongshu'],
  tone: 'professional'  // casual, professional, funny, inspirational
});
```

### 2. Generate Content Ideas

```javascript
const ideas = await creator.generateIdeas({
  count: 10,
  format: 'all',  // video, text, image, carousel
  trending: true  // Include trending topics
});

console.log(ideas);
// [
//   {
//     id: 'idea_001',
//     title: '5 Trading Mistakes Beginners Make',
//     format: 'video',
//     platform: 'tiktok',
//     hook: 'Stop making these 5 trading mistakes!',
//     script: 'Mistake #1: No stop loss...',
//     caption: 'Don\'t let these mistakes kill your portfolio! 💸',
//     hashtags: ['#trading', '#crypto', '#investing', '#money'],
//     viralScore: 87,
//     estimatedViews: '50k-200k'
//   }
// ]
```

### 3. Create Platform-Specific Content

```javascript
const post = await creator.createPost({
  topic: 'Bitcoin halving explained',
  platform: 'twitter',
  format: 'thread',
  length: 'long'  // short, medium, long
});

console.log(post);
// {
//   platform: 'twitter',
//   format: 'thread',
//   tweets: [
//     '1/ Bitcoin halving is one of the most important events in crypto... 🧵',
//     '2/ Every 4 years, the reward for mining Bitcoin gets cut in half...',
//     '3/ Historically, halvings have led to bull markets because...'
//   ],
//   hashtags: ['#Bitcoin', '#Crypto', '#BTC', '#Halving'],
//   bestTimeToPost: '2026-03-19T14:00:00Z',
//   engagementPrediction: 'high'
// }
```

### 4. Get Viral Hashtags

```javascript
const hashtags = await creator.getHashtags({
  niche: 'crypto',
  platform: 'instagram',
  count: 30
});

console.log(hashtags);
// {
//   platform: 'instagram',
//   niche: 'crypto',
//   hashtags: [
//     { tag: '#crypto', posts: '50M', competition: 'high' },
//     { tag: '#cryptotrading', posts: '5M', competition: 'medium' },
//     { tag: '#bitcoinnews', posts: '500k', competition: 'low' }
//   ],
//   recommended: ['#cryptotrading', '#bitcoinnews', '#defi'],
//   optimalCount: 15
// }
```

### 5. Plan Content Calendar

```javascript
const calendar = await creator.planCalendar({
  days: 30,
  postsPerDay: 3,
  platforms: ['tiktok', 'twitter', 'instagram'],
  themes: ['education', 'entertainment', 'promotion']
});

console.log(calendar);
// Returns 30-day content plan with specific post ideas
```

### 6. Analyze Performance

```javascript
const analytics = await creator.getAnalytics({
  platform: 'twitter',
  period: '30d',
  metrics: ['engagement', 'followers', 'impressions']
});

console.log(analytics);
// {
//   period: '30d',
//   totalPosts: 45,
//   totalImpressions: 125000,
//   engagementRate: 4.2,
//   followerGrowth: 850,
//   bestPost: { ... },
//   recommendations: [...]
// }
```

---

## 💡 Advanced Usage

### Competitor Analysis

```javascript
const competitor = await creator.analyzeCompetitor({
  username: '@competitor',
  platform: 'twitter',
  period: '30d'
});

// Returns competitor's top posts, engagement patterns, posting schedule
```

### Viral Pattern Detection

```javascript
const patterns = await creator.detectViralPatterns({
  niche: 'crypto',
  platform: 'tiktok',
  limit: 20
});

// Analyzes what makes content go viral in your niche
```

### A/B Testing

```javascript
const abTest = await creator.createABTest({
  baseContent: 'Bitcoin is breaking out!',
  variations: 5,
  platform: 'twitter'
});

// Creates 5 variations for testing
```

### Content Repurposing

```javascript
const repurposed = await creator.repurposeContent({
  originalUrl: 'https://youtube.com/watch?v=xxx',
  targetPlatforms: ['twitter', 'tiktok', 'linkedin']
});

// Converts long-form content to multiple platforms
```

### Auto-Schedule

```javascript
await creator.schedulePost({
  content: '...',
  platform: 'twitter',
  scheduledTime: '2026-03-20T10:00:00Z',
  autoOptimize: true  // Adjust time based on engagement
});
```

---

## 🔧 Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiKey` | string | required | API key |
| `niche` | string | required | Content niche |
| `platforms` | array | ['twitter'] | Target platforms |
| `tone` | string | 'casual' | Content tone |
| `language` | string | 'en' | Content language |
| `autoHashtags` | boolean | true | Auto-add hashtags |
| `scheduling` | object | null | Auto-schedule config |

---

## 📊 Platform Best Practices

| Platform | Optimal Length | Hashtags | Best Time | Frequency |
|----------|---------------|----------|-----------|-----------|
| TikTok | 15-60s video | 3-5 | 6-9 PM | 1-3/day |
| Instagram | 100-200 chars | 10-15 | 11 AM-1 PM | 1-2/day |
| Twitter | 100-280 chars | 2-3 | 12-3 PM | 3-5/day |
| LinkedIn | 150-300 chars | 3-5 | 8-10 AM | 1/day |
| Xiaohongshu | 500-1000 chars | 10-20 | 7-9 PM | 1-2/day |

---

## 💰 Pricing

| Tier | Price | Features |
|------|-------|----------|
| **Basic** | $39 | Content generation, hashtag engine, calendar planning |
| **Pro** | $79 | + Analytics, auto-posting, competitor analysis, A/B testing |

---

## 📝 Changelog

### v1.0.0 (2026-03-19)
- Initial release
- Multi-platform content generation
- Viral hashtag engine
- Content calendar
- Performance analytics
- Competitor analysis
- Auto-scheduling

---

## 📄 License

MIT License

---

## 🙏 Support

- GitHub: https://github.com/openclaw/skills/social-content-pro
- Discord: OpenClaw Community
- Email: support@openclaw.ai

---

*Built with ❤️ by OpenClaw Agent - Your Viral Content Creator*
