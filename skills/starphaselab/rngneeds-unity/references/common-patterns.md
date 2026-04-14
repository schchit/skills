# Common Patterns

## Weighted loot drop

Use one `ProbabilityList<Item>`.

- one pick for a single drop
- multiple picks for bundles
- use weights if designers think in rarity tiers

Add repeat prevention only if back-to-back duplicates feel bad.

## Chest with categories

Use one higher-level table to choose category, then one table per category.

Good fits:

- `ProbabilityList<ItemCollection>` where each collection owns its own `ProbabilityList<Item>`
- `PLCollection<T>` when many named tables must be organized together

This keeps authoring modular and makes balancing easier.

## Gacha or summon banner

Use a `ProbabilityList<Character>` or `ProbabilityList<Reward>`.

Common additions:

- fixed multi-pulls with `PickValues(10)`
- seeded pulls for reproducible tests
- pick history if later systems need to inspect outcomes

If the design requires pity or guarantee logic, treat RNGNeeds as one part of the system and add explicit game logic around it.

## Dynamic spawn selection

Use `ProbabilityList<SpawnLocation>` or `ProbabilityList<EnemyType>` plus influence providers.

Example signals:

- distance to player
- current threat level
- time of day
- room occupancy

Use `InvertInfluence` when one signal should boost one option while suppressing another.

## AI decision weighting

Use `ProbabilityList<Action>` or `ProbabilityList<DamageType>`.

Good when the AI should feel varied but still biased toward context.

Pair with influence providers for health, cooldown state, stamina, or player distance.

## Dialogue, voice lines, and audio responses

Use `ProbabilityList<AudioClip>` or `ProbabilityList<string>`.

Add repeat prevention so the same bark does not fire twice in a row. Usually `Repick` is a good default.

## Unique rewards

Use a depletable list where each item has `Units = 1`.

This is the cleanest way to say “once claimed, it is gone until refill.”

## Card deck with duplicates

Use a depletable list where each unique card is one item and `Units` holds the copy count.

If the design needs true top/bottom draw order, manually traverse by index instead of calling random pick methods.

## Distinct multi-pick rewards

Use depletable lists plus `PickValues(count)`.

This gives distinct results naturally while units remain.

If the requested count exceeds total remaining units, expect fewer results unless infinite items are mixed in.

## Weighted bool or gate checks

Use `ProbabilityList<bool>` for simple yes/no random gates.

Useful for:

- should spawn
- should crit
- should play idle animation

Keep it only for simple switches. If the design is richer than yes/no, model explicit outcomes instead.
