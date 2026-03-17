---
name: review-buying-advisor
description: Analyze a product from a product name plus platform by locating the intended listing, reading public user reviews when accessible, and turning the evidence into a practical buying recommendation. Use when the user asks whether a product is worth buying on Tmall, Taobao, JD.com, Pinduoduo, Amazon, Best Buy, or similar platforms; asks for help reading reviews; wants a real user-feedback summary; wants recurring complaints, hidden risks, pros and cons, buying advice, who the product is suitable for, or how to avoid buying mistakes before ordering. Especially relevant for requests like "值不值得买", "帮我看评论", "看看口碑", "有什么坑", "适不适合买", or "帮我避坑".
---

# Review Buying Advisor

Turn platform review evidence into a practical buying recommendation.

Use this skill when the input is a product name plus platform and the user wants help deciding whether to buy.

This skill operates in two modes:
- **Mode 1: Review-accessible mode** — the platform exposes enough public review content to support analysis.
- **Mode 2: Review-limited mode** — the platform blocks, weakens, or hides review content, so only a limited or inconclusive answer is possible.

Read these references as needed:
- `references/product-identification.md` when the product or variant is unclear
- `references/review-sampling.md` before collecting review evidence
- `references/review-signals.md` when judging strengths, risks, and buyer fit
- `references/platform-notes.md` when platform review quality may affect interpretation
- `references/category-playbooks.md` when category-specific priorities matter
- `references/failure-modes.md` when evidence is sparse, mixed, or inaccessible
- `references/output-patterns.md` when preparing the final answer
- `references/examples.md` when examples would help calibrate tone or structure

## Workflow

1. Identify the product.
   - Accept a product name plus platform.
   - Match the likely listing by brand, model, category, and variant cues.
   - If the product is ambiguous, ask one short clarifying question.
   - Do not guess across multiple plausible products or variants.

2. Check review accessibility.
   - Try to access public review content on the specified platform.
   - Decide which mode applies:
     - **Mode 1** if enough public review content is accessible.
     - **Mode 2** if review content is blocked, too weak, or too incomplete.

3. If Mode 1, analyze review evidence.
   - Use a representative sample rather than only the first visible comments.
   - Include positive, negative, mixed, and recent reviews when possible.
   - Prefer specific reviews over generic praise or blame.
   - Downweight generic praise, generic criticism, shipping-only comments, and suspiciously promotional wording.
   - Group signals into useful themes.
   - Separate repeated issues from isolated complaints.
   - Weigh severity as well as frequency.

4. If Mode 2, do not fake completion.
   - State that public review evidence is not sufficiently accessible.
   - Explain the limitation briefly.
   - Give only a limited conclusion when still useful.
   - Do not pretend to have validated real review sentiment.

5. Give the final answer.
   Cover:
   - verdict
   - what evidence was actually available
   - buyer fit when supportable
   - main positives and risks when supportable
   - what to verify before buying
   - confidence

## Output

Use this structure unless the user asks for something else.

### Mode 1 output
Use when public review evidence is available.

#### Overall Verdict
Choose one:
- Recommend
- Recommend with caveats
- Depends on use case
- Not recommended
- Not enough evidence for a strong recommendation

#### Why
2-4 bullets with the strongest evidence.

#### Best For
Who is most likely to be satisfied.

#### Main Positives
Most credible repeated strengths.

#### Main Risks
Most important risks, including repeated issues or severe but less frequent ones.

#### Watch Before Buying
What the buyer should verify before ordering.

#### Final Advice
A direct recommendation in plain language.

#### Confidence
High / Medium / Low, with a brief reason.

### Mode 2 output
Use when public review evidence is not sufficiently accessible.

#### Overall Verdict
Usually:
- Not enough evidence for a strong recommendation
- Depends on use case

#### Why
Explain what was and was not accessible.

#### Current Limitation
State whether the issue is platform blocking, weak public text, ambiguous product matching, or incomplete review visibility.

#### Watch Before Buying
State what remains unverified.

#### Final Advice
Give a cautious conclusion without pretending the reviews were validated.

#### Confidence
Usually Low.
## Quality bar

Do:
- lead with the verdict
- use representative evidence
- explain trade-offs clearly
- say who the product is for
- lower confidence when evidence is weak

Do not:
- summarize without recommending
- rely on only one review slice
- overreact to one dramatic review
- overstate certainty
- invent facts not supported by visible evidence

## Limitation handling

If the product cannot be identified confidently:
- ask one short clarifying question

If the platform does not expose enough public review content:
- switch to Mode 2
- state the limitation briefly
- keep confidence low

If public review evidence is sparse or mixed but still partially usable:
- stay in Mode 1 only if a limited review-based judgment is still supportable
- lower confidence
- narrow the claim

If reviews may mix multiple variants:
- mention that risk
- avoid overly specific claims unless the variant is clear
