# Pitfalls

## `PickValues()` returns a shared list

Do not hold onto the returned list across later picks unless you copy it.

Bad assumption: “I stored the last result, so it is stable forever.”

Safe pattern:

```csharp
var stableCopy = new List<Item>(lootTable.PickValues(3));
```

## Disabled items can silently lower pick counts

Disabled items still occupy probability space.
If selection lands on one, that pick is ignored.

Symptoms:

- requested 100 picks, got about 66
- `PickValue()` returned `null` or `default(T)`

Check `MaintainPickCountIfDisabled` if the design values exact count more than exact distribution.

## Failed single picks can look real for value types

If a failed single pick returns `0`, `false`, or another default value, do not assume it was a valid selection.

Prefer `TryPickValue(out var value)` when success matters.

## Repeat prevention changes feel and distribution

Do not promise “same probabilities, just no repeats” unless you are specifically using `Shuffle` and even then explain the limitation.

- `Spread`: stronger correction, more bias
- `Repick`: lower bias, still altered
- `Shuffle`: better preservation, weaker cross-pick guarantees

## Influence can make preview math look surprising

If one item goes up, other items can effectively go down after normalization.

Common mistaken conclusion: “RNGNeeds ignored my spread.”

Often the real cause is that total effective probability exceeded 100%, so normalization changed the final percentages.

## Value-as-provider overrides external provider

If an item's value implements `IProbabilityInfluenceProvider`, that provider takes precedence over an externally assigned provider.

Debug this first when the wrong influence source seems to be active.

## Depletable items do nothing unless the list is depletable

Setting `item.IsDepletable = true` is not enough by itself.

The parent list also needs `list.IsDepletable = true`.

## Maintain-pick-count can intentionally bend outcomes

`MaintainPickCountIfDisabled` keeps filling until it reaches the requested count.

That is useful, but it no longer represents the same distribution as “pick once and ignore disabled/depleted results.”

## Very small enabled probability can cause skipped selection

RNGNeeds has fail-safe protection when maintaining pick count would otherwise take too long or hang because enabled probability is tiny.

If nothing is returned and a warning appears, check:

- too few enabled items
- too many disabled/depleted items
- too large pick count
- influenced outcomes driving enabled probability near zero

## History is index-based

History refers to item indices, not immutable IDs.

Removing items can invalidate assumptions about old picks, so do not build persistence logic on raw indices without your own mapping.

## Weights are authoring helpers, not sacred percentages

When weights are converted back to probabilities, rounding and snapping can make the displayed percentages differ slightly from an intended exact decimal setup.

Use precise probabilities when exact percentages matter more than friendly weight editing.
