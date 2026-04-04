---
name: elm
slug: elm
version: 1.3.0
description: Help users make action-ready 饿了么 decisions: compare红包 and threshold value, late-night or convenience ordering fit, delivery reliability, merchant risk, and refund practicality, then recommend whether to order now, switch merchant, switch platform, or skip.
---

# elm

Use this skill when the user explicitly mentions 饿了么 or when the decision centers on whether the current red-packet and threshold structure is genuinely worth taking.

This is a low-sensitivity public skill. It does not log in, access orders, claim coupons, or read account-state data.

## What This Skill Should Do

Convert a platform browse into one direct move:
- order this merchant now
- use the current红包 because the threshold is natural
- switch to another merchant because the promo is fake value
- move to 美团 because the fulfillment or merchant fit is stronger
- skip the deal

## elm Lens

Bias this skill toward:
- whether 红包 and满减 create real checkout savings
- convenience ordering such as late-night, drinks, snacks, grocery, or quick top-up
- whether a weaker merchant can still be acceptable because the basket is low-risk

## Decision Rules

### Real Savings

- Count the effective savings only after threshold, delivery fee, and packaging fee.
- If the user has to add filler items to unlock the red packet, compare the extra spend to the savings and call it plainly.
- If the final price edge is tiny, let delivery quality and merchant trust decide.

### Scenario Fit

- For late-night and convenience orders, availability and reliability can beat menu breadth.
- For grocery or small top-up baskets, simplicity and low friction matter more than flashy promos.

### Merchant And Refund Risk

Prefer:
- merchants with believable recent reviews
- offers that still make sense without gaming the cart
- stores with lower downside if the food disappoints

Avoid:
- suspiciously deep discounts with weak store credibility
- high-fee baskets pretending to be low-price
- poor review patterns around delays, wrong items, or refund arguments

## Output

### Recommended Move
Say what the user should do now.

### Savings Reality
Summarize whether the promo is actually good.

### Risk Check
Point out delivery and merchant concerns.

### Next Step
Tell the user exactly what to verify before ordering.
