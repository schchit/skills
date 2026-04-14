---
name: album-reviewer
description: Search and aggregate album reviews from multiple sources (Pitchfork, AllMusic, RateYourMusic, Metacritic, Douban, Rolling Stone, NME, Bandcamp Daily, Sputnikmusic, etc.) to produce a comprehensive, bias-minimized review. Use when the user asks to review an album, look up album ratings, compare album reception, or analyze critical consensus on any music release.
---

# Album Reviewer

A multi-source album review aggregator with systematic bias minimization.

## Workflow Overview

```
Step 0: Language selection
Step 1: Identify the album
Step 2: Fast batch search
Step 3: Verify minimum source threshold
Step 4: Bias analysis (internal, not output)
Step 5: Generate output
Step 6: Save review file
```

## Step 0: Language Selection

Before starting, ask the user which language to use for the review output. Offer: Chinese (中文), English, or custom input. All subsequent prose must be in the chosen language. Source quotes should be in their original language with a translation.

## Step 1: Identify the Album

Extract from user input:
- **Artist name** (including aliases / romanizations)
- **Album title** (including localized variants)
- **Release year** (if ambiguous, confirm with user)

Default to the original release unless user specifies otherwise.

## Step 2: Fast Batch Search

Speed is critical. The goal is to gather enough material to write well, not to exhaustively check every source.

### Search Strategy: Two-Pass Approach

**Pass 1 — Wikipedia + Aggregator Sweep (1–2 searches)**

Start here. A single Wikipedia article and/or aggregator page often contains most of what you need: scores from AllMusic, Pitchfork, Rolling Stone, Christgau, plus sales data, chart positions, and accolades.

```
WebSearch: "{album title}" "{artist name}" wikipedia album
WebSearch: "{album title}" "{artist name}" albumoftheyear.org OR metacritic
```

WebFetch the Wikipedia article's "Critical reception" section. This typically lists multiple review scores in one place, saving dozens of individual searches.

**Pass 2 — Targeted Deep Dives (only as needed)**

After Pass 1, identify which **high-value sources** you still lack quotes from. Only search sources where you need actual review prose for the essay. Prioritize:

1. The 2–3 most prominent critics who reviewed this album (varies by genre)
2. One non-English-language community source (e.g. Douban for Asian music)
3. Any source with a notably different opinion (for counterargument material)

```
WebSearch: "{album title}" "{artist name}" {specific source} review
```

### Source Reference

See [sources-reference.md](sources-reference.md) for detailed bias profiles of each source. Key sources by tier:

- **Professional Critics**: Pitchfork, AllMusic, NME, Rolling Stone, The Guardian, Consequence of Sound, Stereogum, The Quietus, Bandcamp Daily, Paste Magazine, Clash Magazine
- **Aggregators**: Metacritic, Album of the Year (AotY)
- **User Communities**: RateYourMusic, Douban Music (豆瓣音乐), Sputnikmusic

### Handling Search Failures

- **Never fabricate scores or quotes.** Only report data actually retrieved via WebSearch/WebFetch.
- **Training data fallback is PROHIBITED** for scores and quotes.
- If a source is unreachable, move on. Do not retry endlessly.

## Step 3: Verify Minimum Source Threshold

Count the number of sources where a score or substantive review was successfully retrieved.

- **≥ 3 sources retrieved**: Proceed.
- **< 3 sources retrieved**: Stop and inform the user. Offer options: retry with broader terms, or proceed with limited data (user must explicitly opt in).

## Step 4: Bias Analysis (Internal)

This step is analytical work that informs the writing — it does NOT produce a separate output section.

For each source collected, internally note:
- **Editorial stance**: e.g. Pitchfork leans indie/art-rock; Rolling Stone leans classic rock canon
- **Temporal context**: contemporary review vs. retrospective vs. re-rating
- **Cultural lens**: Western-centric vs. non-Western
- **Outliers**: scores that deviate ≥15 points from the mean — hypothesize why

These bias notes should be woven **inline** into the comprehensive review prose (e.g. "Pitchfork, which favors art-rock aesthetics, praised..."), not presented as a standalone section.

## Step 5: Generate Output

Follow the template in [output-template.md](output-template.md). The structure is:

1. **Epigraph** — the single best quote about this album, placed at the very top
2. **Header** — album title, artist, year, genre, label
3. **Comprehensive Review** — the main body, a long-form essay (1500–3000 words)
4. **Track Highlights** — 3–5 standout tracks woven into narrative context

### Writing Guidelines for the Comprehensive Review

This is the heart of the output. It should read like a great music essay, not a data report.

- **Open with a scene or context**, not a score. Set the historical/cultural moment the album emerged from.
- **Follow the album's emotional arc.** Walk the reader through the listening experience — discuss specific tracks, production choices, lyrical moments, and mood shifts as they unfold across the tracklist. Let the prose breathe and expand. The reader should feel like they're listening alongside you.
- **Weave in critical perspectives naturally.** When citing a source's opinion, note its perspective inline (e.g. "AllMusic, which takes an encyclopedic approach, called it..."). Don't dump all sources in one paragraph.
- **Separate facts from opinions.** Sales, charts, awards = facts. "Masterpiece", "overrated" = opinions that need attribution.
- **Address the strongest counterargument.** If consensus is positive, steelman the best negative critique. This is mandatory.
- **Discuss temporal trajectory.** How has the album's reputation shifted over time? Dedicate substantial space to this.
- **End with significance.** Close by situating the album in the artist's catalog and broader genre/music history. This replaces the old standalone "Summary" section — the conclusion of the essay IS the summary.
- **Track highlights should be integrated into the essay flow**, not separated into a standalone section. However, after the essay, include a brief "Track Highlights" section listing 3–5 key tracks with 1–2 sentence descriptions for quick reference.

## Step 6: Save Review File

Save the review as a Markdown file:
- Filename: `review.md`
- Location: user's working directory or designated output folder

## Hard Rules

1. **No fabricated data.** Every score, quote, and factual claim must come from a fetched source.
2. **Minimum 3 verified sources** before generating a review (unless user explicitly overrides).
3. **Bias annotations are inline**, not in separate tables or sections.
4. **Counterarguments are mandatory.** Every review must address at least one dissenting perspective.
5. **Source quotes in original language** with translation in the user's chosen output language.
6. **No score tables, no multi-source summary tables, no gap analysis sections.** All analytical insights must be woven into the essay prose.
