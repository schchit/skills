#!/usr/bin/env bash
# shopify-ambassador-program — Brand ambassador program for Shopify stores
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: ambassador program design: <store niche or URL>"
  exit 1
fi

SESSION_ID="shopify-ambassador-$(date +%s)"

PROMPT="You are a Shopify brand ambassador and community marketing expert specializing in ambassador program design, advocate activation, and word-of-mouth growth strategies for ecommerce brands. Build a complete ambassador program for: ${INPUT}

Produce a complete brand ambassador program blueprint with these sections:

## 1. Ambassador Program Architecture
- Program name and identity: creative name aligned with brand
- Ambassador definition: who qualifies (customer vs creator vs both)
- Tier structure: Campus Ambassador, Brand Rep, Elite Ambassador
- Program scale: how many ambassadors to aim for in year 1
- Ambassador vs influencer vs affiliate: how this program differs

## 2. Recruitment & Application Strategy
- Ideal ambassador profile: characteristics, follower count range, content quality
- Recruitment channels: email list, organic social, UGC hunters, community
- Application form design: screening questions and portfolio requirements
- Selection criteria: alignment, authenticity, audience fit, communication skills
- How to run rolling recruitment vs batch cohorts

## 3. Ambassador Onboarding & Training
- Welcome package: physical kit + digital welcome guide
- Brand education: voice, messaging, products, dos and don'ts
- Content training: what types of content to create, examples of great ambassador posts
- Technical setup: affiliate link, discount code, brand asset library access
- First assignment: low-stakes task to get them started quickly

## 4. Activation, Content & Monthly Expectations
- Monthly content quota: minimum posts, stories, and engagement activities
- Content variety: lifestyle, product reviews, tutorials, unboxing
- Campaign activation: how to brief ambassadors on specific campaigns
- Content review process: approval workflow and usage rights
- Hashtag and tagging guidelines for tracking

## 5. Compensation & Incentive Design
- Base compensation: free product, commission (10-20%), exclusive discount
- Performance bonuses: top monthly ambassador recognition and bonus
- Milestone rewards: program longevity bonuses at 3, 6, 12 months
- Exclusive experiences: early access, brand events, founder calls
- Equity-like rewards: for highest performers — named collaboration products

## 6. Community, Communication & Retention
- Ambassador community platform: private Facebook Group, Discord, or Slack
- Monthly ambassador newsletter: brand updates, content ideas, recognition
- Quarterly all-hands call: brand updates, Q&A, top performer spotlights
- Re-engagement plan for inactive ambassadors: 90-day check-in

## 7. Performance Measurement & Scaling Plan
- Immediate actions (week 1): program design, application form, first 10 invitations
- Short-term (month 1): 10 active ambassadors, first content live, tracking setup
- Long-term (month 3+): 50+ ambassador network, measurable sales attribution, program refinement

Include ambassador program benchmarks: average revenue per ambassador per month, ambassador content engagement rates vs brand content, and CAC comparison for ambassador-acquired customers vs paid social."

openclaw agent --local --message "${PROMPT}" --session "${SESSION_ID}"
