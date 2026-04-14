# Decision Guide

Start from the gameplay requirement, then map it to RNGNeeds.

## If the user wants one weighted random result

Use `ProbabilityList<T>` with `PickValue()`.

Examples: one loot drop, one enemy archetype, one dialogue bark.

## If the user wants multiple weighted results at once

Use `ProbabilityList<T>` with `PickValues(...)` and configure pick counts.

- fixed amount: `PickValues(count)`
- variable amount: `LinkPickCounts = false`, set `PickCountMin`, `PickCountMax`, optionally `PickCountCurve`

## If the user wants limited stock or true exhaustion

Use a **depletable list**.

Choose this for:

- card decks
- unique rewards
- finite loot pool
- limited enemy reinforcements

Do **not** use repeat prevention for this.

## If the user wants “do not repeat twice in a row” but not finite stock

Use **repeat prevention**.

- best feel-first choice: `Repick`
- best distribution preservation: `Shuffle`
- fastest but more biased: `Spread`

## If the user wants probabilities to react to game state

Use **influence providers**.

Choose this for:

- health-based drops
- distance-based spawns
- reputation-based dialogue
- time-of-day enemy tables

Use `IProbabilityInfluenceProvider`, `InfluenceSpread`, and possibly `InvertInfluence`.

## If the user wants deterministic or replayable results

Use seeding.

- same list, same results: `KeepSeed = true`
- known sequence: assign `Seed`
- global custom rule: `RNGNeedsCore.SetSeedProvider(...)`

## If the user wants designer-friendly rarity knobs instead of raw percentages

Use weights.

Look at `Weight`, `BaseWeight`, `WeightsPriority`, and related weight conversion helpers.

## If the user wants grouped tables or multi-stage loot

Use nested lists or `PLCollection<T>`.

Choose this for:

- chest chooses category, then item
- biome chooses subtable, then encounter
- deck builder chooses a collection, then cards from it

## If the user wants exact top-of-deck or bottom-of-deck behavior

Do **not** use random picks.

Walk the items manually by index and decrement units yourself, as shown in the card deck sample.

## If the user is debugging “wrong probabilities”

Check these first:

1. influenced list normalization
2. disabled or depleted items
3. repeat prevention bias
4. `MaintainPickCountIfDisabled`
5. shared `PickValues()` result reuse
