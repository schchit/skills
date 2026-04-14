# Test Prompts

Use these to manually probe whether the skill routes well and answers in an RNGNeeds-native way.

## What to look for

A strong answer should usually:

- choose the right RNGNeeds feature before dumping code
- use real RNGNeeds API names
- explain RNGNeeds-specific gotchas instead of generic randomness advice
- avoid inventing methods or hiding tradeoffs

## Pattern selection

1. I need a Unity loot table with three unique rewards per chest. Should I use repeat prevention or depletable lists in RNGNeeds?
2. What RNGNeeds setup fits an NPC response system with Friendly, Neutral, and Hostile dialogue pools?
3. I want a card deck with duplicate cards and true exhaustion. What RNGNeeds pattern should I use?

## Tutorial and support

4. Show me a beginner-friendly RNGNeeds setup for dynamic hacking success using Probability Influence.
5. Explain RNGNeeds depletable lists like I’m handing the setup to a designer.
6. How do I organize multiple spawn tables with PLCollection?

## Code generation

7. Write a Unity component that uses `ProbabilityList<bool>` for crit chance and adjusts it from weapon durability.
8. Show a `PickRewards(int count)` method that returns distinct rewards from a `ProbabilityList<Reward>`.
9. Give me a minimal `IProbabilityInfluenceProvider` example for health-based loot drops.

## Debugging

10. My RNGNeeds list asks for 5 picks but sometimes returns only 3. What should I check?
11. Why does `PickValue()` sometimes return `0` from my `ProbabilityList<int>`?
12. I turned on repeat prevention and now my rare item feels less common. Is that expected?
13. My influence provider is assigned but the wrong influence seems to apply. What could override it?
14. In RNGNeeds, if one item in my `ProbabilityList` is disabled, does it still affect picks and probabilities?

## Determinism and testing

15. How do I make RNGNeeds produce repeatable results for tests and replays?
16. What is the difference between `BaseProbability` and the actual probability used during selection?

## Quick scoring rubric

- **Pass**: right mechanic, real API, no important misinformation
- **Partial**: mostly right, but vague, incomplete, or slightly misleading
- **Fail**: wrong mechanic, invented API, or misleading explanation of RNGNeeds behavior