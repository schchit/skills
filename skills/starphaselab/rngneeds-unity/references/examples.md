# Examples

## Simple weighted loot roll

```csharp
using RNGNeeds;
using UnityEngine;

public class LootRoller : MonoBehaviour
{
    public ProbabilityList<Item> loot;

    public Item RollOne() => loot.PickValue();
}
```

## Distinct rewards from a finite pool

```csharp
using System.Collections.Generic;
using RNGNeeds;
using UnityEngine;

public class RewardChest : MonoBehaviour
{
    public ProbabilityList<Item> rewards;

    private void Awake()
    {
        rewards.IsDepletable = true;
        rewards.SetAllItemsDepletableProperties(true, 1, 1);
        rewards.MaintainPickCountIfDisabled = true;
    }

    public List<Item> OpenChest(int count)
    {
        rewards.RefillItems();
        return new List<Item>(rewards.PickValues(count));
    }
}
```

This matches the docs-preferred distinct-reward flow more closely than the older pick-then-disable loop.

## Health-based dynamic drop chance

```csharp
using RNGNeeds;
using UnityEngine;

public class HealthManager : MonoBehaviour, IProbabilityInfluenceProvider
{
    public float maxHealth = 100f;
    public float currentHealth = 100f;

    public float HealthPct => currentHealth / maxHealth;
    public float ProbabilityInfluence => Mathf.Lerp(1f, -1f, HealthPct);
    public string InfluenceInfo => $"Health {HealthPct:P0} -> influence {ProbabilityInfluence:F2}";
}
```

Use this with an influenced item whose spread increases the drop chance when the player is hurt.

```csharp
using RNGNeeds;
using UnityEngine;

public class LootDrops : MonoBehaviour
{
    public HealthManager health;
    public ProbabilityList<Item> loot;

    private void Awake()
    {
        loot.SetItemInfluenceProvider(0, health);
        loot.SetItemInfluenceSpread(0, new Vector2(-5f, 20f));
    }
}
```

## Prevent repeated voice lines

```csharp
using RNGNeeds;
using UnityEngine;

public class UnitAudio : MonoBehaviour
{
    public ProbabilityList<AudioClip> selectResponses;

    private void Awake()
    {
        selectResponses.PreventRepeat = PreventRepeatMethod.Repick;
    }

    public AudioClip GetResponse() => selectResponses.PickValue();
}
```

## Deterministic test setup

```csharp
using RNGNeeds;

public static class LootTestSetup
{
    public static void ForceDeterministicRuns(ProbabilityList<Item> list)
    {
        list.KeepSeed = true;
        list.Seed = 1337;
    }
}
```

## Multi-stage chest table

```csharp
using System.Collections.Generic;
using RNGNeeds;
using UnityEngine;

public class ItemCollection : ScriptableObject
{
    public ProbabilityList<Item> items;

    public List<Item> PickItems() => new List<Item>(items.PickValues());
}

public class SimpleChest : MonoBehaviour
{
    public ProbabilityList<ItemCollection> weaponCollections;
    public ProbabilityList<Item> armor;

    public List<Item> Open()
    {
        var picked = new List<Item>();

        foreach (var collection in weaponCollections.PickValues())
            picked.AddRange(collection.PickItems());

        picked.AddRange(armor.PickValues());
        return picked;
    }
}
```

## Top-of-deck draw with finite cards

Use indexed traversal, not random picking, when order matters.

```csharp
using System.Collections.Generic;
using RNGNeeds;

public static class DeckDraw
{
    public static List<Card> DrawFromTop(ProbabilityList<Card> cards, int count)
    {
        var results = new List<Card>();

        for (int i = 0; i < cards.ItemCount && results.Count < count; i++)
        {
            if (!cards.TryGetProbabilityItem(i, out var item))
                break;
            if (!item.IsSelectable)
                continue;

            results.Add(item.Value);
            item.Units--;
        }

        return results;
    }
}
```
