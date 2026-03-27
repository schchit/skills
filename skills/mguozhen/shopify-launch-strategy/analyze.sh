#!/usr/bin/env bash
# shopify-launch-strategy — New product launch playbook for Shopify
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: product launch strategy: <product and niche>"
  exit 1
fi

SESSION_ID="shopify-launch-$(date +%s)"

PROMPT="You are a Shopify product launch expert specializing in pre-launch buzz building, coordinated multi-channel launch campaigns, and post-launch momentum strategies for ecommerce brands. Build a complete product launch playbook for: ${INPUT}

Produce a complete product launch strategy report with these sections:

## 1. Pre-Launch Strategy (30-Day Countdown)
- Week 4 before launch: teaser campaign, waitlist setup, influencer seeding
- Week 3: behind-the-scenes content, origin story release, email list segmentation
- Week 2: product previews, early access offer for existing customers, ad pixel warming
- Week 1: countdown content, press outreach, influencer content embargo lift

## 2. Launch Day Campaign Plan
- Launch time selection: best time of day and day of week for this audience
- Hour 1: email blast #1, social posts go live, ads activate
- Hours 2-6: influencer posts publish, PR pitches sent, community announcement
- End of day: email blast #2 (if goals not met), day-1 results snapshot
- Launch day contingency: what to do if sales are below target

## 3. Email Launch Sequence (8-Email Series)
- Email 1 (day -30): teaser — something exciting is coming
- Email 2 (day -14): product reveal — show it, explain why it exists
- Email 3 (day -7): early access offer — exclusive for subscribers
- Email 4 (day -3): countdown reminder — 3 days left for early access
- Email 5 (launch day AM): it's live — full product reveal with CTA
- Email 6 (launch day PM): social proof and first customer reactions
- Email 7 (day +3): selling scarcity or featuring customer photos
- Email 8 (day +7): last chance / post-launch momentum story

## 4. Social Media Launch Calendar
- Instagram: feed posts, Stories, and Reels schedule for launch month
- TikTok: content series — problem, tease, reveal, launch, testimonials
- Pinterest: launch pin strategy and board creation
- Platform-specific content angles and caption templates

## 5. Paid Advertising Launch Plan
- Pre-launch: awareness campaign to warm up audiences (1-2 weeks before)
- Launch day: conversion campaign with launch-specific creative
- Budget allocation: pre-launch vs launch day vs post-launch
- Retargeting: capturing launch traffic that didn't convert immediately

## 6. Influencer Launch Coordination
- Seeding timeline: product delivery to influencers 3-4 weeks before launch
- Content embargo: coordinating simultaneous publish timing
- Gifting vs paid: strategy for launch partnerships
- Micro-influencer coordination: managing 10-20 smaller creators

## 7. Post-Launch Momentum Plan
- Immediate actions (launch day): monitor, respond, amplify organic posts
- Short-term (week 1): leverage launch reviews and UGC, retargeting campaigns
- Long-term (month 1+): transition from launch to evergreen advertising, restock planning

Include launch success benchmarks: first-day revenue targets, email open rates for launch sequences (typically 40-60%), and how to define a successful product launch for different store sizes."

openclaw agent --local --message "${PROMPT}" --session "${SESSION_ID}"
