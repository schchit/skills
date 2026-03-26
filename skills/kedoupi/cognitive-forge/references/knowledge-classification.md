# Knowledge Classification Guide

## Thinking Patterns vs Concepts

### Thinking Patterns (思维框架)

**Definition**: Reusable mental models, decision frameworks, or strategic principles that can be applied across different contexts.

**Characteristics**:
- ✅ Provides a lens for future decisions
- ✅ Can be triggered by specific situations
- ✅ Has broad applicability beyond the original domain
- ✅ Includes decision rules or heuristics

**Examples**:
- **Disruptive Innovation Framework**: "When evaluating competition, check if you're serving top customers (vulnerable) or edge markets (opportunity)"
- **Escape Mechanism**: "When seeing inequality, ask 'who is escaping?' before judging"
- **First Principles Thinking**: "Break down problems to fundamental truths, rebuild from there"

**What to write in thinking-patterns.md**:
```markdown
## [Framework Name]

**Trigger**: When you see/encounter...
**Decision Rule**: Ask/Do...
**Blind Spots**: This fails when...
**Source**: [Book Name] - [Author]
**Date Added**: YYYY-MM-DD
```

---

### Concepts (具体概念)

**Definition**: Specific domain knowledge, terminology, facts, or theories that provide understanding but aren't directly reusable as decision tools.

**Characteristics**:
- ✅ Domain-specific knowledge
- ✅ Explains "what" or "how" something works
- ✅ May not have broad applicability
- ✅ Factual or descriptive

**Examples**:
- **Variolation**: "18th-century inoculation technique using live smallpox virus"
- **Energy Density Ceiling**: "Physical limit to battery energy storage per unit volume"
- **Edge AI Models**: "AI models running on local devices (watches, phones) vs cloud"

**What to write in concepts.md**:
```markdown
## [Concept Name]

**Definition**: ...
**Context**: Where/why this matters
**Related Theories**: Links to thinking patterns
**Source**: [Book Name] - [Author]
**Date Added**: YYYY-MM-DD
```

---

## Decision Tree

```
Extracted knowledge
    │
    ├─ Can I apply this to future decisions in different contexts?
    │  └─ YES → Thinking Pattern
    │  └─ NO ↓
    │
    └─ Is this domain-specific knowledge or terminology?
       └─ YES → Concept
       └─ NO → Re-evaluate (might be too vague)
```

---

## Edge Cases

**When both apply**:
- If a concept **also provides a decision framework**, split it:
  - Core theory → Concept
  - Decision application → Thinking Pattern

**Example**: 
- Concept: "Disruptive Innovation Theory - Christensen's research on how incumbents fail"
- Thinking Pattern: "When evaluating markets, prioritize 'edge' over 'top' customers"

**When neither apply**:
- If the extracted knowledge is too vague or generic, refine it or discard it
- Example: "Innovation is important" (too vague) vs "Disruptive Innovation Framework" (specific, reusable)
