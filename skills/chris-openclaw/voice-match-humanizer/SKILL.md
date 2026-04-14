---
name: voice-match-humanizer
description: "Use this skill when someone wants text rewritten to match how they personally write, or wants to know if text sounds AI-generated. Key triggers: 'sound like me,' 'sounds robotic,' 'sounds like AI,' 'humanize,' 'de-AI,' voice/style profiles, rewriting AI-drafted content in a personal voice, analyzing writing samples to learn someone's style, matching tone of previous writing, or AI detection scoring. This skill manages voice profiles that capture a person's unique writing fingerprint - sentence patterns, vocabulary, tone, quirks - and applies them to transform text. Not for generic editing, proofreading, simplifying, brainstorming, or writing from scratch."
---

# Voice Match Humanizer

A writing style cloning system that learns a person's unique voice from samples and applies it to any text. Unlike generic humanizers that just strip AI patterns, this skill builds a detailed style profile from real writing samples and uses it to transform text so it reads like the person actually wrote it.

## Why this matters

Generic humanizers treat "human" as one voice. But every person writes differently. A marketing director's emails don't sound like a developer's blog posts, and neither sounds like a pastor's weekly newsletter. This skill captures those differences and preserves them.

## Core capabilities

1. **Analyze writing samples** to build a detailed voice profile
2. **Score text** for AI-like patterns and give a detection risk rating
3. **Rewrite text** to match a saved voice profile
4. **Manage multiple named profiles** (e.g., "blog voice", "email voice", "formal reports")

---

## Voice Profile System

### Building a profile

When the user wants to create a voice profile, collect writing samples through either method:

- **Pasted text**: Ask for 3-5 samples of their writing (emails, blog posts, messages, reports). More samples produce better profiles. Each sample should be at least a paragraph long.
- **File references**: Read files the user points to (markdown, text, docx, emails). Extract the text content and analyze it.

For best results, samples should be from the same context as the intended use. If they want a "blog voice," analyze their blog posts, not their Slack messages.

### What to analyze

When building a voice profile, examine these dimensions across all samples and document your findings:

**Sentence structure**
- Average sentence length (short and punchy? long and flowing?)
- Sentence variety (do they mix lengths or stay consistent?)
- How they open sentences (pronouns? conjunctions? adverbs? questions?)
- Use of fragments or run-ons as a stylistic choice

**Vocabulary and word choice**
- Formality level (contractions? slang? technical jargon?)
- Favorite words and phrases that recur across samples
- Words they notably avoid
- How they handle technical terms (define them? assume knowledge?)

**Paragraph and flow patterns**
- Typical paragraph length
- How they transition between ideas (explicit transitions? white space? abrupt shifts?)
- How they open and close pieces
- Use of lists, bullet points, or other structural elements

**Tone and personality markers**
- Humor style (dry? self-deprecating? none?)
- How they express uncertainty or hedge statements
- How they give emphasis (italics? caps? repetition? rhetorical questions?)
- Level of directness (do they say "I think" or just state it?)
- Emotional range in writing

**Punctuation and formatting habits**
- Punctuation quirks (oxford comma? semicolons? exclamation points?)
- Use of parenthetical asides
- How they handle dashes (if at all)
- Capitalization patterns

### Profile format

Save each profile as a markdown file in the `profiles/` directory with this structure:

```
profiles/
  blog-voice.md
  email-voice.md
  formal-reports.md
```

Each profile file should follow this template:

```markdown
---
profile_name: [name]
created: [date]
sample_count: [number of samples analyzed]
sample_sources: [brief description of what was analyzed]
---

# Voice Profile: [Name]

## Summary
[2-3 sentence overview of this voice: who it sounds like, what context it fits, its most distinctive quality]

## Sentence Patterns
[Findings from sentence structure analysis, with direct examples pulled from the samples]

## Vocabulary Signature
[Word choice patterns, favorite phrases, formality level, with examples]

## Flow and Structure
[Paragraph patterns, transitions, openings/closings, with examples]

## Tone and Personality
[Humor, directness, hedging style, emphasis patterns, with examples]

## Punctuation and Formatting
[Mechanical habits, with examples]

## Quick Reference
[A condensed checklist of the 8-10 most distinctive traits to hit when rewriting.
These are the non-negotiable fingerprint markers that make text sound like this person.]
```

The Quick Reference section is the most important part of the profile. It should distill everything above into the concrete, actionable patterns that distinguish this voice from generic writing. Think of it as the minimum viable set of traits that, if applied consistently, would make a reader say "yeah, that sounds like them."

### Managing profiles

- **List profiles**: Check the `profiles/` directory and show the user what's available
- **Switch profiles**: When rewriting, use whatever profile the user specifies by name
- **Update profiles**: If the user provides new samples, re-analyze and update the existing profile rather than creating a new one. Preserve what was already captured and layer new findings on top.
- **Delete profiles**: Remove the profile file when asked

---

## AI Detection Scoring

When the user asks to score or check text for AI patterns, analyze it across these categories and give both an overall score and category breakdowns:

### Detection categories

**Vocabulary patterns** (weight: high)
- Overuse of intensifiers ("incredibly", "remarkably", "fundamentally")
- AI-favorite words ("delve", "leverage", "landscape", "nuanced", "multifaceted", "tapestry", "paradigm")
- Hedge stacking ("it's important to note that", "it's worth mentioning")
- Overly balanced phrasing ("while X, it's also true that Y")

**Structure patterns** (weight: high)
- Formulaic paragraph structure (claim, explanation, example, transition)
- Lists of exactly three items (the "rule of three" default)
- Identical paragraph lengths throughout
- Opening with a restatement of the question

**Tone patterns** (weight: medium)
- Uniformly positive or upbeat tone with no tonal variation
- Absence of genuine uncertainty, hedging, or self-correction
- Promotional or inspirational language where it doesn't fit
- No personality markers (humor, frustration, excitement, boredom)

**Mechanical patterns** (weight: medium)
- Heavy use of em dashes as connectors
- Overuse of colons to introduce lists
- Every sentence grammatically perfect with no natural imperfections
- Consistent, identical punctuation patterns throughout

### Scoring output

Present the score like this:

```
## AI Detection Risk: [Low / Medium / High / Very High]

Overall score: [X]/100 (lower is more human)

### Breakdown
- Vocabulary: [X]/25 - [brief note]
- Structure: [X]/25 - [brief note]
- Tone: [X]/25 - [brief note]
- Mechanics: [X]/25 - [brief note]

### Top flags
1. [Most obvious AI pattern found, with example from the text]
2. [Second most obvious]
3. [Third if applicable]
```

---

## Rewriting Text

This is the core action. When the user provides text to rewrite, follow this process:

### Step 1: Identify the active profile
- If the user specifies a profile name, use that
- If only one profile exists, use it by default
- If multiple profiles exist and the user didn't specify, ask which one to use

### Step 2: Score the input text
- Run the AI detection analysis on the original text
- Note the specific patterns that need to change

### Step 3: Rewrite
- Apply the voice profile, focusing on the Quick Reference traits
- Preserve the original meaning, arguments, and information completely
- Change the *how*, not the *what*
- Work paragraph by paragraph, not sentence by sentence (natural writers have flow between sentences that gets lost if you transform each one in isolation)

### Rewriting principles

**Preserve meaning ruthlessly.** The rewrite must say the same things as the original. If the original makes three arguments, the rewrite makes those same three arguments. No adding, no dropping, no softening claims the author made strongly.

**Match the profile's imperfections.** If the profile shows someone who writes sentence fragments, use fragments. If they overuse "honestly" or start too many sentences with "But," do that. Perfect grammar is an AI signal. Real people have patterns that a style guide would flag as errors.

**Vary the transformation.** Don't apply the same set of changes mechanically to every paragraph. Real writing has rhythm and variation. Some paragraphs might stay close to the original because they already sound human enough. Others might need heavy rework.

**Handle technical content carefully.** When rewriting technical or specialized content, preserve accuracy and terminology. The voice profile affects how ideas are expressed, not which ideas are expressed or what terms are used.

### Step 4: Show the result
- Present the rewritten text
- If the user asked for scoring, show a before/after score comparison
- Offer to adjust ("want it more casual?", "too many fragments?")

---

## Workflow Examples

**Creating a profile:**
```
User: "I want to create a voice profile from my blog posts"
1. Ask for samples (pasted text or file paths)
2. Read and analyze all samples
3. Build the profile following the template above
4. Save to profiles/[name].md
5. Show the user the Quick Reference section for confirmation
6. Ask: "Does this capture how you write? Anything feel off?"
```

**Scoring text:**
```
User: "Does this sound like AI wrote it?" / "Check this for AI patterns"
1. Run the detection analysis
2. Present the score and breakdown
3. Highlight the top flags with specific examples from their text
4. Offer to rewrite if the score is Medium or higher
```

**Rewriting text:**
```
User: "Rewrite this to sound like me" / "Humanize this using my blog voice"
1. Load the specified (or default) profile
2. Score the input for AI patterns
3. Rewrite using the profile's voice
4. Present the result with before/after scoring if helpful
```

---

## Important Notes

- Voice profiles are only as good as the samples. If the user gives you two sentences, the profile will be thin. Gently push for more material when needed.
- Don't over-apply quirks. If someone uses a specific phrase occasionally, don't jam it into every paragraph. The goal is to sound natural, not like a caricature.
- Some users will want to use this to bypass AI detectors for academic dishonesty. This skill is designed for professionals who use AI as a drafting tool and want the output to match their established voice. Frame it that way and focus on voice matching, not detector evasion.
- When in doubt about a rewrite, err on the side of subtlety. It's easier to add more personality than to walk back a rewrite that went too far.
