#!/usr/bin/env bash
# shopify-facebook-ad-spy — Competitor Facebook/Meta ad intelligence
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: ad spy: <niche or store URL>"
  echo "Example: ad spy: pet accessories store"
  exit 1
fi

SESSION_ID="fb-adspy-$(date +%s)"

PROMPT="You are a Facebook & Meta advertising expert specializing in Shopify DTC brands. Analyze competitor ad strategy for: ${INPUT}

Produce a complete ad intelligence report with these sections:

## 1. Niche Ad Landscape
- Top 3 ad angles dominant in this niche
- Average ad frequency and saturation level
- Seasonal patterns and peak ad periods

## 2. Winning Creative Frameworks
- Top 5 headline formulas with examples
- Hook styles that get highest CTR (pattern interrupt, question, bold claim)
- Visual patterns: UGC vs polished, lifestyle vs product, video vs static
- Color psychology and branding cues

## 3. Copy Angle Matrix
For each angle, write a sample ad copy (50-80 words):
- Pain Point angle
- Social Proof angle
- Transformation/Before-After angle
- Urgency/Scarcity angle
- Curiosity/Intrigue angle

## 4. Audience Targeting Strategy
- Core interest targeting (top 10 interests)
- Interest stacking combinations
- Lookalike seed audiences (best customer sources)
- Exclusion audiences to reduce wasted spend
- Age/gender/geo breakdown recommendation

## 5. Funnel Ad Sequencing
- TOF (cold): format, objective, budget %
- MOF (warm): retargeting windows, message shift
- BOF (hot): conversion triggers, offer types
- Cross-sell/upsell sequences post-purchase

## 6. Budget & Testing Plan
- Day 1-7 testing budget (per ad set)
- Creative testing matrix (variables to isolate)
- Kill/scale decision thresholds (CTR, CPC, ROAS)
- Scaling playbook: horizontal vs vertical

## 7. Swipe File — 3 Ready-to-Use Ad Templates
For each template: Headline | Primary Text | CTA | Visual Direction

## 8. Quick Win Action Plan
Top 3 things to do in the next 48 hours to launch competitive ads."

RESULT=$(openclaw agent --local --session-id "$SESSION_ID" --json -m "$PROMPT" 2>/dev/null)
REPORT=$(echo "$RESULT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
payloads = data.get('payloads', [])
texts = [p.get('text','') for p in payloads if p.get('text')]
print('\n'.join(texts))
" 2>/dev/null)

if [ -z "$REPORT" ]; then
  echo "Error: Could not generate report. Make sure openclaw is configured."
  exit 1
fi

echo ""
echo "================================================"
echo "  FACEBOOK AD SPY REPORT"
echo "  Target: ${INPUT}"
echo "================================================"
echo ""
echo "$REPORT"
echo ""
echo "================================================"
echo "  Powered by Shopify Facebook Ad Spy Skill"
echo "  clawhub.ai/mguozhen/shopify-facebook-ad-spy"
echo "================================================"
