---
name: seo-content-brief-generator
description: "SEO content brief generator agent. Produces complete content briefs from a target keyword: search intent classification, content outline, target word count, LSI and semantic terms, competitor content gaps, E-E-A-T signals, and internal link suggestions. Triggers: seo brief, content brief, keyword brief, seo content, content outline, content strategy, keyword research brief, content plan, seo writing, article brief, blog brief, content gap"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/seo-content-brief-generator
---

# SEO Content Brief Generator

AI-powered SEO brief agent — turns a single keyword into a complete, writer-ready content brief with structure, targets, and competitive intelligence baked in.

Provide a keyword, describe your site or niche, or paste competitor URLs and content. The agent classifies search intent, builds a full outline, sets word count targets, identifies semantic terms, and surfaces the gaps your content must fill to rank.

## Commands

```
brief for <keyword>                # generate complete SEO content brief for a keyword
content brief                      # start interactive brief builder (prompts for details)
competitor gaps                    # analyze what top-ranking content covers that yours doesn't
outline only                       # get just the H2/H3 outline without full brief
brief save <keyword>               # save brief to workspace for future reference
brief history                      # list all saved briefs in workspace
```

## What Data to Provide

The agent works with:
- **Target keyword** — "brief for best standing desk under $500"
- **Site context** — niche, domain authority, existing content, target audience
- **Competitor content** — paste URLs or copy text from top-ranking articles
- **Content goals** — rank for keyword, drive conversions, support existing pillar page
- **Existing content** — "I already have an article about standing desks, this is a supporting piece"

No API keys needed. No SEO tool subscription required.

## Workspace

Creates `~/seo-briefs/` containing:
- `memory.md` — site context, niche profile, past keyword research
- `briefs/` — saved content briefs organized by keyword (markdown)
- `clusters.md` — topic cluster maps and internal link architecture

## Analysis Framework

### 1. Search Intent Classification

Every keyword falls into one of four intents:

| Intent | Definition | Content Type |
|--------|-----------|--------------|
| Informational | User wants to learn | How-to guide, explainer, listicle |
| Commercial | User is comparing options | Best-of list, comparison, review |
| Transactional | User is ready to buy | Product page, landing page, pricing |
| Navigational | User wants a specific site | Brand/site-specific page |

**Mixed intent detection**: some keywords have blended signals (e.g., "best CRM for small business" = commercial + transactional). Brief format adapts accordingly.

### 2. SERP Analysis Approach
Without live SERP access, analyze based on keyword signals:
- Question words (what, how, why, when) → informational
- Modifiers (best, top, review, vs., alternative) → commercial
- Action words (buy, get, download, sign up) → transactional
- Brand names in keyword → navigational
- Ask user to describe top 3 ranking results for calibration

### 3. Outline Structure by Intent

#### Informational
- H1: Target keyword (conversational, long-tail phrasing)
- Introduction: Define the problem/question (150 words)
- H2: Background / Why This Matters
- H2: [Core Concept 1] — H3 subtopics
- H2: [Core Concept 2] — H3 subtopics
- H2: [Core Concept 3] — H3 subtopics
- H2: Step-by-Step Guide or Practical Application
- H2: Common Mistakes / FAQs
- Conclusion + CTA

#### Commercial Investigation
- H1: Best [Product Category] for [Use Case] — [Year]
- Introduction: Who this guide is for + selection criteria (200 words)
- H2: Quick Picks (summary table)
- H2: [Product 1] Review — H3: Pros, Cons, Best For
- H2: [Product 2] Review (repeat pattern)
- H2: Buyer's Guide — H3: Key factors to consider
- H2: FAQ
- Conclusion + CTA

#### Transactional
- H1: [Primary Keyword] — [Value Prop]
- Above-fold: clear CTA, key benefits, trust signals
- H2: Features / What You Get
- H2: How It Works
- H2: Pricing
- H2: Social Proof / Case Studies
- H2: FAQ / Objection Handling
- Final CTA

### 4. Word Count Benchmarks by Intent
| Intent | Recommended Word Count |
|--------|----------------------|
| Informational (simple) | 800–1,200 |
| Informational (complex) | 1,500–2,500 |
| Commercial list (5–10 products) | 2,000–3,500 |
| Commercial comparison | 1,500–2,500 |
| Transactional / Landing page | 600–1,200 |
| Pillar / Hub page | 3,000–5,000+ |

### 5. Semantic Keyword Clusters
For each brief, identify 3 types of supplementary terms:
- **LSI (Latent Semantic Indexing) terms**: conceptually related words (e.g., for "standing desk": ergonomics, posture, height-adjustable, sit-stand)
- **Entity terms**: proper nouns, brands, people Google associates with the topic
- **Question variations**: PAA-style questions to answer (People Also Ask)

Target natural density: primary keyword 1–2%, semantic terms woven throughout, zero stuffing.

### 6. Competitor Content Gap Analysis
Gaps to identify and fill:
- Topics covered by top-ranking content that a draft would miss
- Questions left unanswered in competitor articles
- Outdated information that can be replaced with current data
- Missing content types (no video, no table, no comparison chart)
- Thin sections where competitors spend only 1 paragraph on a subtopic that deserves depth

### 7. E-E-A-T Signals (Experience, Expertise, Authoritativeness, Trustworthiness)
Checklist for brief:
- [ ] Author bio with credentials relevant to topic
- [ ] First-hand experience signals ("in my testing", "I used this for 30 days")
- [ ] Cite original research or primary sources
- [ ] Last updated date visible on page
- [ ] Expert quotes or external validation
- [ ] Clear editorial process or review policy (especially for YMYL topics)
- [ ] Transparent affiliate disclosure if applicable

### 8. Internal Link Suggestions
- **Link from**: existing high-authority pages on your site that should pass equity to this article
- **Link to**: supporting pages this article should reference (product pages, related guides)
- **Anchor text**: descriptive, keyword-relevant (not "click here")
- **Cluster logic**: this article should sit within a topic cluster with a defined pillar page

## Output Format

Every brief outputs:
1. **Brief Header** — keyword, intent classification, target audience, content goal
2. **Word Count Target** — with rationale based on intent and competition
3. **Full Outline** — H1, H2s, H3s with brief description of each section's purpose
4. **Semantic Terms List** — LSI terms, entities, and question variations
5. **E-E-A-T Checklist** — items to include for trust and authority signals
6. **Competitor Gap List** — 3–5 specific gaps to fill vs. top-ranking content
7. **Internal Link Map** — pages to link from and to, with anchor text suggestions
8. **Writer Notes** — tone, format preferences, any avoid list

## Rules

1. Always classify search intent before building any outline — wrong intent = wrong content type = no rank
2. Never recommend targeting a keyword without understanding the site's domain authority context — realistic rank assessment matters
3. Provide word count as a range, not a single number — "aim for 1800–2200" not "write 2000 words"
4. Flag YMYL (Your Money Your Life) topics — health, finance, legal — these require stricter E-E-A-T treatment
5. Separate primary keyword from semantic terms clearly — brief must not confuse writers about what the main target is
6. Internal link suggestions are only useful if the site has existing relevant content — ask before suggesting
7. Save briefs to `~/seo-briefs/briefs/` when brief save command is used
