---
name: natural-language-editor
description: Turn robotic drafts into natural, credible writing without changing meaning. Use for polish, anti-AI tone cleanup, concise/professional rewrites, readability upgrades, and tone adaptation (light/deep/clarity/concise/professional/linkedin/anti-ai/keep-length) with optional JSON output.
---

# Natural Language Editor

Rewrite user text so it reads naturally while preserving intent and facts.

## 2-minute wins

- Clean AI-sounding text for client-facing use.
- Make long text concise without losing key points.
- Convert rough draft into polished professional copy.

## Commands

- `edit [text]` — default natural rewrite
- `edit --concise [text]` — shorter, same meaning
- `edit --clarity [text]` — easier to understand
- `edit --professional [text]` — neutral, polished tone
- `edit --light [text]` — minimal edits only
- `edit --deep [text]` — stronger restructuring, same meaning
- `edit --anti-ai [text]` — reduce templated/AI-like cadence while preserving meaning
- `edit --linkedin [text]` — optimize for LinkedIn profile/about style (credible, concrete, concise)
- `edit --keep-length [text]` — preserve source length within ±10% while improving naturalness
- `edit --json [text]` — structured analysis + rewrite

If the user provides only text, use default natural mode.

## Core Rules

1. Preserve meaning.
2. Do not add new facts.
3. Do not remove essential claims.
4. Do not inject new opinions, emotions, or experiences.
5. Keep perspective unless the user asks to change it.
6. Prefer direct, concrete wording over vague phrasing.
7. Keep technical terminology accurate when precision matters.

## Mode Behavior

### Natural (default)
Improve flow and readability with minimal semantic change.

### Concise
Remove redundancy and filler; keep all essential points.

### Clarity
Simplify complex phrasing, split overloaded sentences, reduce abstraction.

### Professional
Use clear, neutral, business-appropriate wording.

### Light
Keep structure and tone close to source; apply minimal edits.

### Deep
Allow stronger sentence-level restructuring while preserving meaning.

### Anti-AI
Reduce robotic markers (template transitions, repetitive cadence, hedge stacking, generic intensifiers). Vary sentence rhythm and prefer concrete wording while preserving facts and intent.

### LinkedIn
Optimize for LinkedIn profile/about usage: strong first-person positioning, concrete outcomes, credible tone, and scannable structure. Avoid hype, clichés, and overclaiming.

### Keep-Length (±10%)
Rewrite naturally while keeping total character length close to the source (target within ±10%). Prioritize meaning preservation first, then length control.

## Rewrite Workflow

1. Identify friction points (repetition, filler, generic transitions, vagueness, rhythm issues, tone mismatch, AI-like templating).
2. Choose the least invasive mode that solves the problem.
3. Rewrite while preserving facts, claims, terminology, and perspective.
4. For `--anti-ai`, explicitly remove robotic patterns and smooth cadence without adding subjectivity.
5. For `--linkedin`, prioritize concrete achievements, clean role framing, and concise professional tone without adding new claims.
6. For `--keep-length`, check source vs rewrite length and adjust to stay within ±10%.
7. Validate output: no factual additions, no distortion, better readability.

## Output Format

- Default: return rewritten text only.
- JSON mode (`--json`):

```json
{
  "issues_found": ["repetitive phrasing", "inflated language"],
  "rewrite_strategy": "remove filler and simplify wording",
  "rewritten_text": "...",
  "introduced_subjectivity": false
}
```

## Limits

Do not:

- add new facts,
- change argument intent,
- invent experiences/emotions,
- shift perspective unless requested,
- strengthen legal/medical/technical claims beyond source.

## Author

Vassiliy Lakhonin
