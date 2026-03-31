---
name: discount-optimizer
description: Calculate optimal discount levels based on unit cost, conversion targets, and inventory velocity so promos move product without destroying margin.
---

# Discount Optimizer

Promotional discounts are one of the fastest ways to drive volume on TikTok Shop — but cutting price without a margin model turns short-term spikes into long-term losses. This skill calculates mathematically grounded discount levels by working from your unit economics upward, ensuring every promotion moves product while protecting profit.

## Use when

- You are planning a TikTok Shop flash sale or platform-wide campaign and need to set a discount percentage that hits a GMV target without pushing gross margin below a minimum acceptable threshold.
- You are evaluating whether a stacked promotion — platform voucher, affiliate commission, or creator coupon code — is still profitable after layering all cost components together.
- You have aging inventory above a target days-on-hand threshold and want to find the minimum effective discount depth to accelerate sell-through before a reorder cycle.
- You are comparing multiple discount mechanics such as percentage off, bundle pricing, or buy-one-get-one to determine which structure maximizes contribution margin at a given sell-through volume target.

## What this skill does

Discount Optimizer takes your unit cost, current list price, minimum acceptable margin percentage, target conversion rate uplift, and inventory velocity data as inputs. It then runs a margin-preserved discount calculation that identifies the maximum allowable discount ceiling, models expected volume uplift using your conversion rate assumptions, and outputs a ranked set of discount scenarios with projected margin impact, break-even sell-through volumes, and a recommended promo price. Each scenario clearly shows the discounted price, resulting margin percentage, estimated units sold at projected conversion uplift, total contribution margin generated, and a break-even comparison against running no promotion. When stacked promotions including platform vouchers, creator commissions, and ad spend cost per order are included as inputs, the skill incorporates all of those cost layers before producing its final recommendation, ensuring nothing is hidden in the math.

## Inputs required

- **unit_cost** (required): Total landed cost per unit including cost of goods, inbound shipping, and standard platform fees. Example: $8.50 per unit.
- **list_price** (required): Current selling price before any discount is applied. Example: $24.99.
- **min_margin_pct** (required): Minimum acceptable gross margin percentage you are willing to accept during the promotional period. Example: 20%.
- **inventory_units** (optional): Current stock on hand in units. Used to model sell-through scenarios and flag whether discount depth is justified by inventory pressure or not.
- **conversion_rate_baseline** (optional): Current baseline conversion rate on the listing before discounting. Used to estimate volume uplift at different discount levels. Example: 2.4%.
- **stacked_costs** (optional): Any additional per-unit cost layers such as affiliate commission rate, platform coupon subsidy cost, or blended ad cost per order. Example: 10% affiliate commission plus $1.20 ad cost per order.

## Output format

The skill outputs a structured discount scenario table modeling three to five price points from a conservative five-percent discount up to the margin floor. For each scenario the output includes the discounted price, resulting gross margin percentage, estimated units sold at projected conversion uplift, total contribution margin generated, and a break-even comparison against running no promotion. A recommended scenario is highlighted with a plain-English rationale explaining why that discount level best serves the stated goal, whether that goal is margin protection, inventory clearance, or GMV volume maximization. Scenarios where stacked costs push the effective margin below the minimum acceptable threshold are flagged as unprofitable and excluded from the final recommendation so you never accidentally run a money-losing promo.

## Scope

- Designed for: TikTok Shop sellers, ecommerce brand operators, and performance marketing managers who run regular promotional events.
- Platform: TikTok Shop, Shopify, Lazada, Shopee, and any ecommerce channel where promotional pricing is configurable.
- Language: English

## Limitations

- Does not have access to real-time platform conversion data — conversion rate uplift assumptions must be provided or estimated by the operator based on historical data.
- Does not automatically account for halo effects or post-promotion brand lift that may generate additional revenue beyond the promotional window.
- Margin calculations assume fixed unit costs at current volumes; economies of scale or variable fulfillment costs at significantly higher volumes are not modeled unless explicitly provided as inputs.
