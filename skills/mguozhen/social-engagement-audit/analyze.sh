#!/usr/bin/env bash
set -euo pipefail
INPUT="${*:-}"
[ -z "$INPUT" ] && echo "Usage: engagement audit: <platform, niche, followers, current engagement rate>" && exit 1
SESSION_ID="audit-$(date +%s)"
PROMPT="You are a social media analytics expert specializing in engagement optimization. Run a full engagement audit for: ${INPUT}

## Engagement Rate Benchmark
Industry benchmarks for this platform + niche:
| Metric | Below Average | Average | Good | Excellent |
|--------|-------------|---------|------|-----------|
| Engagement Rate | <X% | X-X% | X-X% | >X% |
| Reach Rate | | | | |
| Save Rate | | | | |
| Share Rate | | | | |
| Comment Rate | | | | |

Current status based on input: [Rating + comparison to benchmark]

## Top 5 Engagement Killers
Diagnose the most likely causes based on the account description:

**Killer #1: [Issue Name]**
- What it looks like: [specific symptom]
- Why it happens: [root cause]
- How to fix it: [specific action]

**Killer #2: [Issue Name]**
[Same format]

**Killer #3: [Issue Name]**
[Same format]

**Killer #4: [Issue Name]**
[Same format]

**Killer #5: [Issue Name]**
[Same format]

## Content Autopsy
Most common reasons posts fail in this niche:
- Hook failure: [what bad hooks look like + fix]
- Caption failure: [common mistake + fix]
- Format mismatch: [format vs what algorithm rewards right now]
- Posting time failure: [when not to post + best times]
- CTA failure: [weak vs strong CTAs for this platform]

## Algorithm Alignment Check
What this platform's algorithm rewards right now:
| Signal | What Algorithm Wants | Are You Doing This? | Fix |
|--------|---------------------|---------------------|-----|
| Watch time / dwell time | | | |
| Saves | | | |
| Shares / Sends | | | |
| Comments | | | |
| Profile visits | | | |
| Follower ratio | | | |

## 30-Day Engagement Fix Plan
**Week 1 — Foundation:**
- Day 1-2: [specific action]
- Day 3-4: [specific action]
- Day 5-7: [specific action]

**Week 2 — Content Overhaul:**
- [Specific changes to make]

**Week 3 — Engagement Farming:**
- [Specific tactics]

**Week 4 — Analyze & Double Down:**
- [What to measure and what to scale]

## 3 Quick Wins (Do Today)
1. [Action you can do in 10 minutes that will improve engagement]
2. [Action you can do in 30 minutes]
3. [Action you can do this week]

## Engagement Rate Calculator
If you implement all recommendations:
- Current rate: X%
- Expected rate in 30 days: X%
- Expected rate in 90 days: X%
- Key metric to watch as leading indicator: [metric]"

RESULT=$(openclaw agent --local --session-id "$SESSION_ID" --json -m "$PROMPT" 2>/dev/null)
REPORT=$(echo "$RESULT" | python3 -c "
import json,sys
data=json.load(sys.stdin)
texts=[p.get('text','') for p in data.get('payloads',[]) if p.get('text')]
print('\n'.join(texts))
" 2>/dev/null)
[ -z "$REPORT" ] && echo "Error: Could not generate audit." && exit 1
echo ""
echo "=== ENGAGEMENT AUDIT === ${INPUT} ==="
echo ""
echo "$REPORT"
