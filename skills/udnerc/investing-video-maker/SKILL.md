---
name: investing-video-maker
version: 1.0.5
displayName: "Investing Video Maker — Create Stock Market and Investment Education Videos"
description: >
    Investing Video Maker — Create Stock Market and Investment Education Videos. Works by connecting to the NemoVideo AI backend. Supports MP4, MOV, AVI, WebM, and MKV output formats. Automatic credential setup on first use — no manual configuration needed.
metadata: {"openclaw": {"emoji": "📈", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
---

# Investing Video Maker — Stock Market and Investment Education Videos

The brokerage account has been open for three months, the portfolio contains one share of a company the investor heard about on TikTok, and the daily ritual of checking whether it went up or down has replaced any meaningful investment strategy. Investing content on YouTube exists on a spectrum between "buy my course to learn the secret" and "here's a 45-minute lecture on the efficient market hypothesis" — neither of which helps the person who just wants to know whether they should put their $500 into an index fund or individual stocks and what happens after they click the buy button. The channels that build trust are the ones that show real portfolio screenshots, explain concepts with actual dollar amounts instead of abstract percentages, and admit when they don't know something — a radical act in a category dominated by people who predicted every crash after it happened. This tool transforms investment concepts, market analysis, and portfolio strategies into polished education videos — animated stock-chart breakdowns with labeled support and resistance levels, portfolio-allocation pie charts that rebalance in real time, compound-growth projections with specific dollar inputs, dividend-reinvestment visualizations showing the snowball effect, risk-comparison matrices with volatility ranges, and the step-by-step brokerage walkthroughs that demystify the distance between "I should invest" and "I just did." Built for finance educators building course content, financial advisors creating client education, fintech platforms producing onboarding tutorials, investment clubs documenting strategies, and anyone who wants to explain why a 22-year-old putting $200/month into an S&P 500 index fund will likely retire with more money than most day traders.

## Example Prompts

### 1. Beginner Guide — Index Fund Investing from Zero
"Create a 10-minute video teaching complete beginners how to start investing in index funds. Real numbers, real steps, real brokerage screen recording. Opening (0-20 sec): 'You've heard you should invest. You've been told "start early." Nobody showed you where to click. Today I'm showing you where to click.' What's an index fund (20-90 sec): animated explanation. 'An index fund owns a piece of every company in an index — the S&P 500 has 500 companies. You buy one fund, you own 500 companies. Apple, Microsoft, Amazon, the boring industrial company you've never heard of — all of them.' Show the diversification visually: one dollar bill splitting into 500 tiny pieces, each landing on a company logo. 'If one company crashes, the other 499 absorb the blow.' Why index funds beat stock picking (90-150 sec): the data. Animated bar chart: '92% of actively managed funds underperformed the S&P 500 over 15 years.' Let that stat sit on screen. 'Professional fund managers with Bloomberg terminals and Ivy League degrees can't beat the index consistently. You with a phone app can match it.' How much to start (150-220 sec): 'As little as $1. Seriously. Most brokerages have no minimum now.' Show the growth scenarios animated: $100/month at 10% average for 30 years = $226,000. $300/month = $678,000. $500/month = $1,130,000. 'The amount matters less than the starting. Start with what you have.' The walkthrough (220-420 sec): screen recording of opening a brokerage account — step by step. 'I'm using [generic brokerage], but Fidelity, Schwab, and Vanguard all work the same way.' Show: create account (2 minutes), link bank account, search for the fund (type the ticker), click buy, enter the dollar amount ($200), confirm. 'That's it. You're now an investor. That took less time than ordering food delivery.' What happens next (420-500 sec): 'You'll open the app tomorrow and the number will be different. It might be down. That's normal.' Show a 1-year chart with ups and downs, then zoom out to 30 years — the upward trend is undeniable. 'Zoom in and it's chaos. Zoom out and it's a staircase.' Dollar-cost averaging explained: animated monthly buys at different prices — sometimes buying high, sometimes low, the average smoothing out. Closing (500-600 sec): 'You don't need to pick stocks. You don't need to time the market. You need to buy an index fund regularly and not touch it for decades. The math does the rest.'"

### 2. Portfolio Analysis — Annual Review Walkthrough
"Build a 7-minute portfolio review video showing how to evaluate and rebalance a real portfolio. Opening: portfolio screenshot on screen — total value $47,200. Holdings: S&P 500 index 60%, international index 20%, bond index 15%, REIT 5%. 'This is my actual portfolio. Once a year I check if it still matches my plan. Here's the 20-minute review that determines whether I change anything.' Performance check (0-120 sec): YTD returns per holding — animated bar chart. S&P 500: +22%, International: +8%, Bonds: +3%, REIT: +11%. Overall: +16.4%. 'My target was "don't lose money and beat inflation." 16.4% beat both. But the returns aren't what I'm really checking.' Allocation drift (120-240 sec): the original target was 60/20/15/5. After a year of differential returns, the actual allocation is 65/17/13/5. Show the pie chart morphing from target to actual. 'The S&P grew faster than everything else, so it's now 65% of my portfolio instead of 60%. That means I'm taking more risk than my plan says I should.' Rebalancing (240-360 sec): two methods animated. Method 1 — sell the winners, buy the underperformers: sell $2,400 of S&P 500, buy $1,400 international, buy $1,000 bonds. 'This feels wrong. You're selling what worked and buying what didn't. That's the point. You're selling high and buying low systematically.' Method 2 — redirect new contributions: don't sell anything, just put new money into the underweight categories. 'This avoids tax events but takes longer to rebalance. If your portfolio is in a tax-advantaged account, Method 1 is fine.' Risk check (360-420 sec): 'Am I still comfortable with this allocation?' Show the worst-case scenario: 2008 crash simulation on this portfolio — a 60/20/15/5 portfolio dropped roughly 35%. 'If $47,200 became $30,700, would I panic sell? If yes, increase bonds. If no, the allocation is right.' Closing: updated allocation pie chart — back to 60/20/15/5. 'Twenty minutes once a year. That's all active management this portfolio needs.'"

### 3. Concept Explainer — Compound Interest Visualized
"Produce a 4-minute compound interest explainer that makes the concept click. No jargon, no formulas, just a visual story. Opening: two jars — one labeled 'Simple Interest' and one labeled 'Compound Interest.' Both start with $10,000. 'Same starting amount. Same 10% annual return. Thirty years. One jar makes you comfortable. The other makes you wealthy. The difference is one word: reinvestment.' Year 1 (0-60 sec): both jars earn $1,000 (10% of $10,000). Simple jar: the $1,000 sits next to the jar (it's earned but not reinvested). Compound jar: the $1,000 goes INTO the jar. Both show $11,000 at year end. 'So far, identical.' Year 2: simple jar earns another $1,000 (still 10% of original $10,000). Compound jar earns $1,100 (10% of $11,000 — the interest earned interest). The $100 difference is small. 'It's $100. You wouldn't bother bending down to pick it up. But wait.' Year 5: simple = $15,000. Compound = $16,105. Difference: $1,105. Year 10: simple = $20,000. Compound = $25,937. 'Now the compound jar is pulling ahead — and it's accelerating.' Year 20: simple = $30,000. Compound = $67,275. The gap is now enormous. Animate both jars growing — the compound jar's growth curve visibly steepening. Year 30: simple = $40,000. Compound = $174,494. 'Same starting amount. Same percentage. The compound jar has four times more money. The only difference: the interest earned interest, which earned interest, which earned interest.' The rule of 72 (180-210 sec): 'Quick shortcut — divide 72 by your return rate. That's how many years it takes to double. 10% return? Your money doubles every 7.2 years.' Show: $10K → $20K at year 7 → $40K at year 14 → $80K at year 22 → $160K at year 29. 'Four doubles in 30 years.' The real application (210-240 sec): 'This is why starting at 22 instead of 32 matters more than the amount.' Two people: Person A invests $200/month from age 22-32, then stops (total invested: $24,000). Person B invests $200/month from 32-62 (total invested: $72,000). At 62: Person A has more money. 'Person A invested one-third the money and ended up with more. That's not a math trick. That's compound interest and ten extra years.'"

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the investment topic, real numbers, strategies, and target audience level |
| `duration` | string | | Target video length (e.g. "4 min", "7 min", "10 min") |
| `style` | string | | Video style: "beginner-guide", "portfolio-review", "concept-explainer", "market-analysis", "strategy-comparison" |
| `music` | string | | Background audio: "ambient-focus", "motivational-build", "corporate-light", "none" |
| `format` | string | | Output ratio: "16:9", "9:16", "1:1" |
| `data_animations` | boolean | | Animate charts, growth curves, and allocation graphics (default: true) |
| `disclaimer` | boolean | | Include "not financial advice" disclaimer overlay (default: true) |

## Workflow

1. **Describe** — Outline the investment topic, real numbers, scenarios, and audience knowledge level
2. **Upload (optional)** — Add portfolio screenshots, brokerage recordings, or chart images
3. **Generate** — AI produces the video with growth animations, allocation charts, and scenarios
4. **Review** — Verify all financial calculations, check disclaimer placement, adjust pacing
5. **Export** — Download in your chosen format and resolution

## API Example

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "investing-video-maker",
    "prompt": "Create a 10-minute index fund beginner guide: diversification animation of 1 dollar into 500 companies, 92% active funds underperform stat, growth scenarios at $100 $300 $500 per month for 30 years, brokerage account walkthrough screen recording, 1-year vs 30-year chart zoom showing volatility vs trend, dollar-cost averaging animation",
    "duration": "10 min",
    "style": "beginner-guide",
    "data_animations": true,
    "disclaimer": true,
    "music": "ambient-focus",
    "format": "16:9"
  }'
```

## Tips for Best Results

1. **Use specific dollar amounts, not just percentages** — "$200/month becomes $226,000 in 30 years" motivates action; "10% annual return" is abstract. The AI renders dollar-specific growth projections when you provide monthly contribution amounts and timeframes.
2. **Show the chart at two zoom levels** — A 1-year chart looks scary; a 30-year chart looks inevitable. The AI generates zoom-out transitions from short-term volatility to long-term growth curves when you describe both timeframes.
3. **Include a brokerage walkthrough** — "Where do I click?" is the real barrier for beginners. The AI sequences your screen recording with step-number overlays and highlighted click targets for each action in the account-opening flow.
4. **Animate allocation pie charts for rebalancing** — A pie chart morphing from target to actual allocation shows drift intuitively. The AI generates animated pie-chart transitions when you describe target vs actual portfolio percentages.
5. **Always include the disclaimer** — Investment content requires it. The AI places a "not financial advice" overlay at the opening and closing when disclaimer is enabled, keeping you compliant without interrupting the content.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube investing tutorial / course content |
| MP4 9:16 | 1080p | TikTok / Instagram Reels finance tip |
| MP4 1:1 | 1080p | LinkedIn finance post / Instagram carousel |
| GIF | 720p | Growth animation loop / Reddit investing post |

## Related Skills

- [personal-finance-video](/skills/personal-finance-video) — Money management and personal finance videos
- [crypto-video-maker](/skills/crypto-video-maker) — Cryptocurrency and blockchain education videos
- [budgeting-video-maker](/skills/budgeting-video-maker) — Budget planning and expense tracking videos
