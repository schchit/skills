# Advanced Workflow Guides

Detailed step-by-step guides for each workflow. Read the relevant section when executing that task.

---

## Workflow 1: Multi-Region Category Analysis

### Purpose

Run cross-regional comparison of influencer landscapes across categories and markets to identify the best opportunities.

### When to Trigger

User asks for regional analysis, cross-market comparison, or says things like "compare US vs SG", "analyze Southeast Asia", "which market is best for 3C".

### Process

1. **Determine scope** — Ask user for target categories and regions (or suggest defaults: 3c/beauty/home, US/SG/TH).
2. **Fetch data** — Run `tiktok_slayer.sh` with `--mode both` for all region x category combinations.
   ```bash
   tiktok_slayer.sh --category 3c --region US,SG,TH --format json --mode both
   ```
3. **Read all output files** from `output/` directory.
4. **Analyze and compare:**
   - Engagement rate distribution per region
   - EC score ranking per region
   - Sales performance per region
   - Influencer density per category per market
   - Regional trends and patterns

5. **Generate comparison report** with structure:
   - Executive summary (3-5 bullet points)
   - Per-region breakdown (top influencers + insights)
   - Cross-regional comparison tables (engagement, EC score, sales)
   - Best market recommendation per category
   - Priority actions

### Output Format

- **MD**: Default for readability and editing
- **Excel**: One sheet per region, one summary sheet for cross-region comparison
- **PDF**: Professional shareable report with charts

---

## Workflow 2: Influencer Collaboration Plan

### Purpose

Generate a structured influencer collaboration proposal with tiered recommendations, pricing, and execution timeline.

### When to Trigger

User asks for influencer collaboration plan, partnership proposal, or says "how to work with these influencers", "create a collab plan".

### Process

1. **Fetch data** (if not already available):
   ```bash
   tiktok_slayer.sh --category <target> --region <market> --format json --mode influencers
   ```

2. **Score and tier influencers:**

   | Criteria | Weight | Scoring |
   |----------|--------|---------|
   | Engagement Rate | 30% | >15%=100, >10%=90, >5%=70 |
   | EC Score | 25% | >5=100, >4=80, >3=60 |
   | Follower Count | 20% | 1K-5K=90, 5K-20K=80, <1K=70 |
   | Sales Track Record | 15% | Has sales=100, No sales=60 |
   | Content Fit | 10% | Vertical=100, Partial=70 |

   **Tier assignment:**
   - Tier 1 (Priority): Score >= 85 — highest ROI potential
   - Tier 2 (Key): Score 70-84 — solid partners
   - Tier 3 (Supplementary): Score 50-69 — emerging or niche

3. **Generate collaboration plan:**
   - Project overview (product focus, markets, timeline)
   - Influencer selection criteria table
   - Recommended influencers by tier (name, region, followers, engagement, EC score, products, collab type, expected sales, rate)
   - Collaboration models (content collab, direct sales, brand partnership)
   - Compensation framework by tier
   - 5-phase execution timeline (Outreach → Confirmation → Content Creation → Publishing → Review)
   - KPIs and evaluation criteria
   - Risk management (no-show, content quality, platform policy, payment)

### Output Format

- **MD**: Editable and shareable proposal
- **PDF**: Professional proposal for stakeholders
- **Excel**: Track influencer data, rates, and contract status

---

## Workflow 3: Product Selection List

### Purpose

Generate a prioritized, data-informed product selection list for TikTok Shop sellers.

### When to Trigger

User asks for product recommendations, what to sell, selection list, or says "what products to push", "create a product list".

### Process

1. **Fetch market data:**
   ```bash
   tiktok_slayer.sh --category <target> --region <market> --format json --mode both
   ```

2. **Analyze influencer landscape** to understand what sells:
   - Average product prices in the market (from `avg_30d_price`)
   - Sales volumes and GMV patterns (from `sales` field)
   - Category gaps and opportunities

3. **Generate product selection list** based on:
   - Market data (price ranges that convert)
   - Platform trends (seasonal demand)
   - Influencer compatibility (what products match available influencers)

4. **Structure the list:**
   - Executive summary (top 3 product types, optimal price band, expected monthly profit)
   - Product selection by sub-category (product, specs, price range, target market, est. conversion, priority, notes)
   - Pricing strategy (price band, product types, conversion rate, profit margin, recommendation)
   - Revenue forecast table with totals
   - Risk assessment (inventory, quality, competition)

### Output Format

- **MD**: Quick review and editing
- **Excel**: Best for tracking — one sheet per section (Products, Pricing, Revenue)
- **PDF**: Professional report for team sharing

---

## Workflow 4: Video Hook Strategy

### Purpose

Create actionable video content strategies with specific hook types, scripts, and content calendar matched to products and influencers.

### When to Trigger

User asks for video strategy, content plan, hook ideas, or says "create video scripts", "what hooks to use", "content calendar".

### Process

1. **Identify target products** (from Workflow 3 or user-provided).

2. **Match hook types to products:**

   | Hook Type | Conversion Rate | Difficulty | Best For |
   |-----------|----------------|------------|---------|
   | Drop Test | 12-18% | Medium | Cases, screen protectors |
   | Comparison Review | 10-15% | Medium | Power banks, earphones |
   | Quick Unboxing | 9-14% | Low | All products |
   | Scene Application | 8-12% | Medium | Stands, speakers |
   | Price Impact | 11-16% | Low | All products |

3. **Generate video scripts** (3-5 scripts minimum):
   - Meta info (product, hook type, duration, conversion target, assigned influencer)
   - Scene-by-scene storyboard (time, scene, voiceover/subtitle, SFX)
   - Key execution points
   - CTA (link, urgency, next step)

4. **Create content calendar** matching scripts to influencers and dates:
   - Weekly breakdown with theme, product, hook type, influencer, expected conversion

5. **Summarize strategy:**
   - Hook type vs conversion rate analysis
   - Influencer assignment matrix
   - Content volume targets
   - Success metrics

### Output Format

- **MD**: Scripts and calendar (primary format)
- **Excel**: Calendar + tracking sheet
- **PDF**: Professional pitch deck for team/stakeholders

---

## Workflow 5: Competitive Intelligence Monitoring

### Purpose

Monitor competitor activity across categories and regions: what products are rivals promoting, pricing changes, emerging competitors, and new entrants. This keeps sellers informed of market movements in real time.

### When to Trigger

User asks for competitor monitoring, competitive analysis, or says "竞品动态", "监控竞争对手", "竞争对手在做什么", "competitive intel", "competitor watch", "竞品情报", "daily competitors report".

### Process

1. **Fetch latest data** across all relevant categories and regions:
   ```bash
   tiktok_slayer.sh --all --region US,SG,TH --format json --mode influencers
   ```
   Or for a specific competitor's category:
   ```bash
   tiktok_slayer.sh --category 3c --region US,SG,TH --format md --mode both
   ```

2. **Analyze competitive landscape:**
   - Identify creators promoting products in the same category
   - Compare EC scores and sales volumes across creators
   - Detect emerging creators (new entrants with rising engagement)
   - Spot pricing patterns from `avg_30d_price` field
   - Track market concentration (how many active sellers per category per region)

3. **Cross-reference with known competitors** (if user provides competitor usernames, check their latest stats; if not, infer from top creators in the category).

4. **Generate competitive intelligence report:**

   **Standard format (daily/weekly):**
   ```
   # 竞品动态 | YYYY-MM-DD

   ## 📱 [Category] — [Region]
   ### 活跃竞品
   | 竞品/达人 | 粉丝 | 互动率 | EC评分 | 销量 | 动态摘要 |
   | (table)

   ### 新晋竞品 (emerging creators in this category)
   | 新进者 | 粉丝 | 互动率 | EC评分 | 备注 |
   | (table)

   ### 价格监控
   | 产品类型 | 平均价格 | 价格区间 | 趋势 |
   | (table)

   ### 📈 市场洞察
   - [bullet points on competitive patterns]

   ### ⚠️ 预警
   - [any sudden movements, new entrants, pricing wars]
   ```

   **Compact format (for WeChat/messaging):**
   ```
   竞品动态 | YYYY-MM-DD

   [Category] US:
   1. [Competitor]: [dynamic, ≤64 chars]
   2. [Competitor]: [dynamic]

   [Category] SG:
   1. [Competitor]: [dynamic]

   ⚠️ 预警: [if any]
   ```

### Competitive Intelligence Report Types

| Report Type | Frequency | Trigger Phrase |
|-------------|-----------|---------------|
| **Daily Competitor Watch** | Every morning | "竞品日报", "今日竞品动态" |
| **Weekly Competitive Summary** | Every Friday | "竞品周报", "weekly competitive" |
| **Alert: New Entrant** | On-demand | "有新竞品吗", "new competitor alert" |
| **Pricing Intelligence** | On-demand | "竞品价格", "pricing watch" |

### Output Format

- **MD**: Full detailed report for records and analysis
- **Compact text**: For WeChat/chat group sharing (≤200 chars per section)
- **JSON**: For integration with external dashboards

---

## Workflow 6: Profit & Margin Calculator

### Purpose

Calculate precise profit margins and break-even points for TikTok Shop products. TikTok Shop fees, creator commissions, shipping costs, and refund rates can easily erode margins — this workflow gives sellers the full financial picture before they set prices.

### When to Trigger

User asks about pricing, profit, margin, or says "计算利润", "我能赚多少", "定价建议", "profit margin", "这个产品能卖吗", "cost analysis", "ROI计算".

### Process

1. **Gather product info** (from user or from Workflow 3 product data):
   - Product name
   - Cost price (from supplier)
   - Selling price (planned or market reference)
   - Product category
   - Target region(s)

2. **Apply TikTok Shop fee structure:**

   | Fee Type | Rate | Notes |
   |----------|------|-------|
   | Platform Commission | 8% | TikTok Shop cut |
   | Creator Commission | 15-25% | Typically 20% for content creators |
   | Payment Processing | ~0.5% | Payment provider fee |
   | Refund Rate | 3-8% | Industry average, higher for fashion |
   | Shipping Cost | $3-8 | Depends on weight and region |
   | Storage Fee | $0.50-2 | Monthly per unit in warehouse |

3. **Calculate:**
   ```
   Gross Revenue = Selling Price × Units Sold
   Platform Fees = Selling Price × (Commission + Payment Processing) / (1 - Refund Rate)
   Creator Fees = Selling Price × Creator Commission Rate
   Total Costs = Product Cost + Shipping + Storage + Platform Fees + Creator Fees + Refund Reserve
   Net Profit = Selling Price - Total Costs
   Net Margin = Net Profit / Selling Price × 100%
   Break-even = Fixed Costs / Net Profit Per Unit
   ```

4. **Generate margin analysis report:**
   ```
   # 利润分析 | [Product Name]

   ## 基本信息
   - 产品: [name]
   - 品类: [category]
   - 市场: [region(s)]
   - 采购成本: $[cost]
   - 计划售价: $[price]

   ## 成本明细
   | 成本项 | 金额 | 占比 |
   |--------|------|------|
   | 商品成本 | $12.00 | 40% |
   | 平台佣金 (8%) | $2.40 | 8% |
   | 达人佣金 (20%) | $6.00 | 20% |
   | 支付手续费 (0.5%) | $0.15 | 0.5% |
   | 运费 | $3.50 | 11.7% |
   | 仓储费 | $0.80 | 2.7% |
   | 退款预留 (5%) | $1.50 | 5% |
   | **合计成本** | **$26.35** | **88%** |

   ## 利润指标
   | 指标 | 数值 |
   |------|------|
   | 售价 | $30.00 |
   | 总成本 | $26.35 |
   | 净利润 | $3.65 |
   | 净利润率 | **12.2%** |
   | 毛利率 | 58% |
   | 盈亏平衡点 | 55件 / $1,650 |

   ## 定价情景分析
   | 售价 | 净利润 | 利润率 | 盈亏平衡 |
   |------|--------|--------|---------|
   | $25 | $1.65 | 6.6% | 122件 |
   | $30 | $3.65 | 12.2% | 55件 |
   | $35 | $5.65 | 16.1% | 36件 |
   | $40 | $7.65 | 19.1% | 26件 |

   ## 建议
   - **推荐售价**: $35 (利润率 16%+)
   - **最低售价**: $28 (保持正利润)
   - **激进售价**: $40 (高利润，但需配合强转化内容)
   ```

### Scenario Analysis

Also calculate sensitivity to:
- Creator commission rate (15% vs 20% vs 25%)
- Refund rate (3% vs 8%)
- Shipping cost by region
- Bulk order discount scenarios

### Output Format

- **MD**: For review and pricing decision-making
- **Excel**: For what-if scenario modeling (use openpyxl, one sheet per product)
- **Compact table**: For quick messaging (selling price | cost | profit | margin)

---

## Workflow 7: Daily Operations Report

### Purpose

Generate a structured daily or weekly TikTok Shop operations briefing that consolidates creator performance, sales data, inventory alerts, and actionable recommendations — so sellers can start each day with a clear picture and action plan.

### When to Trigger

User asks for a daily brief, operations report, morning briefing, or says "今日报告", "每日简报", "运营日报", "daily brief", "运营周报", "weekly report", "morning briefing".

### Process

1. **Gather data from available sources:**
   - Run latest EchoTik fetch for current data:
     ```bash
     tiktok_slayer.sh --all --region US,SG,TH --format json --mode influencers
     ```
   - Read previous day's report (if exists in `output/` directory)
   - Collect user-provided sales data (orders, GMV, refunds) if available

2. **Analyze across dimensions:**

   **Creator Performance:**
   - Track which creators published content recently
   - Compare engagement rates vs historical average
   - Flag creators who are underperforming (below their average EC score)
   - Identify creators who need follow-up (confirmed collab but no content yet)

   **Market Intelligence:**
   - New entrants in target categories
   - Price movements in competitor products
   - Engagement rate trends across categories

   **Actionable Insights:**
   - Which creators to follow up with today
   - Which products need inventory top-up
   - Which regions are underperforming

3. **Generate daily operations report:**

   ```
   # TikTok Shop 每日运营简报 | YYYY-MM-DD

   ## 📊 今日概览
   | 指标 | 今日 | vs 昨日 | vs 上周 |
   |------|------|---------|---------|
   | 总订单 | X | +X% | +X% |
   | 总销售额 (GMV) | $X | +X% | +X% |
   | 净收入 | $X | +X% | +X% |
   | 平均客单价 | $X | +X% | +X% |
   | 转化率 | X% | +X% | +X% |

   ## 🎯 达人动态
   ### 内容发布
   | 达人 | 地区 | 品类 | 互动率 | 带来订单 | 转化率 | 状态 |
   | (table)

   ### 待跟进达人
   | 达人 | 地区 | 合作状态 | 待办 |
   | (table)

   ## 📈 市场情报
   ### 热门品类 (本区域)
   | 品类 | 活跃达人 | 平均互动 | 平均EC评分 | 市场热度 |
   | (table)

   ### 新晋达人 (可考虑合作)
   | 达人 | 地区 | 粉丝 | 互动率 | EC评分 | 建议 |
   | (table)

   ## ⚠️ 预警与提醒
   - [库存不足预警]
   - [高退款率提醒]
   - [平台政策变动]
   - [达人超时未发布]

   ## 💡 今日行动建议
   1. [Action 1 — high priority]
   2. [Action 2 — medium priority]
   3. [Action 3 — if time permits]

   ## 📅 本周进度
   | 目标 | 当前 | 进度 |
   |------|------|------|
   | 视频发布 X 条 | X 条 | XX% |
   | 新达人合作 X 人 | X 人 | XX% |
   | GMV $X | $X | XX% |
   ```

### Report Frequency Variants

| Frequency | Trigger Phrase | Focus |
|-----------|---------------|-------|
| **Daily Brief** | "今日简报", "daily brief" | Today's actions, yesterday's results |
| **Weekly Report** | "周报", "weekly report" | 7-day trends, week-over-week comparison |
| **Monthly Review** | "月报", "monthly review" | Full month analysis, goal tracking |

### Weekly Report Additions

Beyond the daily structure, add:
- Week-over-week comparison table
- Creator ranking this week (best → worst by ROI)
- Top performing content (highest engagement)
- Budget spent vs planned (creator fees, ad spend)
- Goal completion rate

### Output Format

- **MD**: Primary format for review and records
- **Compact text**: For WeChat/messaging (structured, scannable)
- **PDF**: For stakeholder sharing (e.g., send to boss/investor)

---

## Output Format Reference

### When to Use Each Format

| Format | Best For | How to Generate |
|--------|----------|----------------|
| **MD** | Readability, editing, git versioning | Write directly |
| **JSON** | Machine processing, API integration | Script `--format json` |
| **PDF** | Professional reports, sharing with stakeholders | Python reportlab (English content to avoid font issues) |
| **Excel** | Data management, tracking, what-if modeling | Python openpyxl (use Calibri font, English content) |

### PDF Generation (Python with reportlab)

```python
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet
# Use English content to avoid CJK font issues
# Register CJK font if Chinese output is needed:
# from reportlab.pdfbase import pdfmetrics
# pdfmetrics.registerFont(TTFont('PingFang', '/System/Library/Fonts/PingFang.ttc'))
```

### Excel Generation (Python with openpyxl)

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
# Use Calibri font for cross-platform compatibility
# Use English for cell content to avoid encoding issues
```

### File Naming Convention

```
<report_type>_<category>[_<region>]_<YYYYMMDD>.<format>

Examples:
  competitor_watch_3c_US_20260325.md
  margin_calculator_65w_charger_20260325.xlsx
  daily_ops_20260325.pdf
  weekly_report_US_SG_TH_20260325.md
```
