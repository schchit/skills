---
name: tiktok-trend-slayer
description: "TikTok Shop end-to-end operations toolkit for cross-border sellers. Fetches influencer data via EchoTik API and product trending data via TikTok Shop Partner API, then generates: (1) multi-region category analysis, (2) influencer collaboration plans, (3) product selection lists, (4) video hook strategies, (5) competitive intelligence reports, (6) profit/margin calculators, and (7) daily/weekly operations briefs."
metadata:
  openclaw:
    requires:
      env:
        - ECHOTIK_AUTH_HEADER
        - TIKTOK_SHOP_API_KEY
      bins:
        - curl
        - jq
      primaryEnv: ECHOTIK_AUTH_HEADER
    config:
      requiredEnv:
        - ECHOTIK_AUTH_HEADER
      requiredEnv:
        - TIKTOK_SHOP_API_KEY
      stateDirs:
        - .openclaw/skills/tiktok-trend-slayer/output
    homepage: "https://github.com/skovely/tiktok-trendslayer"
    source: "https://github.com/skovely/tiktok-trendslayer"
---

# TikTok Trend Slayer

Full-stack TikTok Shop analytics and operations toolkit for cross-border sellers. From data fetching to daily operations — seven workflows covering the entire seller journey.

TikTok 选品猎手是一款面向 TikTok 电商卖家的智能选品工具。一站式处理 TikTok Shop 跨境经营，涵盖从数据采集到日常运营的 7 大自动化流。通过自动监控 TikTok Shop 商品榜、EchoTik 数据接口，实时识别高增长爆款商品，并利用AI分析爆款视频的钩子（Hook）与结构，自动匹配合适的中腰部达人（KOC），帮助卖家快速发现蓝海品类与合作机会。


## 核心功能概述 （Core Features Overview）

1. **黑马发现算法｜Dark Horse Discovery Algorithm**
- 调用 TikTok Affiliate API 和 EchoTik 接口获取商品/达人数据，实时监测 GMV 增长斜率。当某个商品在 24 小时内销量增速翻倍，且挂车达人数仍处于低位时，系统将自动触发“蓝海预警”。

- Leverages TikTok Affiliate and EchoTik APIs to fetch real-time product and creator data, monitoring GMV growth gradients. When a product's sales growth doubles within 24 hours while the number of linked creators remains low, the system automatically triggers a "Blue Ocean Alert."

2. **视频病毒基因拆解 ｜Viral Video Gene Dissection**
- 识别 GMV 增速前 5% 商品及 24h 销量翻倍的黑马 SKU，AI 自动解析高转化视频的“黄金 3 秒”Hook、脚本结构与 BGM 情绪，为您提供 1:1 可复刻的爆款脚本公式。

- Identifies the top 5% of products by GMV growth and "dark horse" SKUs with doubled sales. AI automatically analyzes the "Golden 3-Second" hooks, script structures, and BGM vibes of high-conversion videos, providing you with 1:1 replicable viral script formulas.

3. **达人撮合雷达 | Creator Matchmaking Radar**
- 基于商品画像自动筛选最具带货潜力的高转化 KOC，拒绝只看粉丝数，只看实战转化率，自动制定达人合作方案。

- Automatically filters KOCs with the highest sales potential based on product profiling. Moving beyond vanity metrics like follower counts, it focuses solely on actual conversion rates to generate automated creator collaboration plans.

4. **自动选品报告 | Automated Product Selection Report**
- 支持自动生成目标品类/商品、当前销量、预估利润、竞争程度及推荐话术等的完整报告。

- Supports the automatic generation of comprehensive reports covering target categories/products, current sales volume, estimated profit margins, competition levels, and recommended sales pitches.



## Quick Start

```bash
# Install dependencies
brew install curl jq

# Set EchoTik credential (required)
export ECHOTIK_AUTH_HEADER="Basic <base64_credentials>"

# Optional: TikTok Shop credential (for product data)
export TIKTOK_SHOP_API_KEY="your_access_token"

# Fetch all data across all categories and regions
~/.openclaw/skills/tiktok-trend-slayer/scripts/tiktok_slayer.sh --all --region US,SG,TH --format json --mode both

# Fetch influencers only (default)
~/.openclaw/skills/tiktok-trend-slayer/scripts/tiktok_slayer.sh --category 3c --region US

# Fetch products only
~/.openclaw/skills/tiktok-trend-slayer/scripts/tiktok_slayer.sh --category 3c --region US --mode products
```

## Script Arguments

| Flag | Value | Default | Description |
|------|-------|---------|-------------|
| `--category` | beauty/3c/home/fashion/food/sports/baby/pet | — | Single category |
| `--all` | — | — | All 8 categories |
| `--region` | US,SG,TH,UK,... (comma-separated) | US | One or more markets |
| `--format` | json / md | json | Output format |
| `--page-size` | 1-10 | 10 | Results per request |
| `--output-dir` | path | skill/output/ | Custom output directory |
| `--mode` | influencers/products/both | influencers | Data type to fetch |

## Core Workflows

Read [references/workflows.md](references/workflows.md) for detailed step-by-step instructions for each workflow.

### 1. Multi-Region Category Analysis
**Trigger:** "compare US vs SG", "analyze Southeast Asia", "which market for 3C"  
**Output:** Regional comparison report with per-market insights, engagement/EC score/sales tables, and market recommendations.

### 2. Influencer Collaboration Plan
**Trigger:** "create collab plan", "how to work with influencers", "partnership proposal"  
**Output:** Tiered proposal (Tier 1/2/3) with compensation framework, collaboration models, and 5-phase execution timeline.

### 3. Product Selection List
**Trigger:** "what to sell", "product recommendations", "selection list"  
**Output:** Prioritized product list with specs, pricing bands, profit margins, and revenue projections.

### 4. Video Hook Strategy
**Trigger:** "create video scripts", "what hooks to use", "content calendar"  
**Output:** 3-5 scene-by-scene video scripts + weekly content calendar with influencer assignments.

### 5. Competitive Intelligence Monitoring
**Trigger:** "竞品动态", "监控竞争对手", "competitive intel", "竞品情报", "daily competitors report"  
**Output:** Daily/weekly competitor activity reports with pricing trends, new entrants, and market alerts.

### 6. Profit & Margin Calculator
**Trigger:** "计算利润", "我能赚多少", "profit margin", "定价建议", "ROI计算"  
**Output:** Full cost breakdown with platform fees, creator commissions, shipping, and margin analysis at multiple price points.

### 7. Daily Operations Report
**Trigger:** "今日报告", "每日简报", "运营日报", "daily brief", "运营周报", "weekly report"  
**Output:** Structured daily/weekly brief with creator performance, market intelligence, inventory alerts, and action items.

## Output Formats

| Format | Best For | How to Generate |
|--------|----------|----------------|
| **MD** | Readability, editing | Write directly |
| **JSON** | Machine processing | Script `--format json` |
| **PDF** | Professional sharing | Python reportlab |
| **Excel** | Data tracking, what-if modeling | Python openpyxl |

## Category Reference

| Category | Code |
|----------|------|
| Beauty | beauty |
| 3C Electronics | 3c |
| Home & Living | home |
| Fashion | fashion |
| Food & Beverage | food |
| Sports & Outdoors | sports |
| Baby & Maternity | baby |
| Pet Supplies | pet |

## API Details

See [references/api_docs.md](references/api_docs.md) for EchoTik and TikTok Shop API endpoints, response schemas, and credential setup.

## Tags

tiktok tiktok-shop influencer-analytics product-selection competitive-intel profit-margin daily-report video-hook content-strategy collaboration-plan cross-border ecommerce operations
