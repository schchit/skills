---
name: im-framework
description: |
  Reference, explain, and apply the Immanent Metaphysics (IM) framework by Forrest Landry.
  Uses a structured ontology of 767 entities as an index into the live source text at mflb.com.
  Use when asked to explain IM concepts, apply the framework to a situation, trace derivation
  chains, or find source references. Triggers on: "immanent metaphysics", "IM framework",
  modality questions, axiom references, ICT, symmetry/continuity ethics, effective choice,
  path of right action, or any request to ground claims in the framework.
---

# Immanent Metaphysics Framework

Source: **https://mflb.com/8192** — Forrest Landry's whitebook. This is the canonical text.
The ontology in `references/graph.jsonl` is an index into it. Always fetch the source URL and quote exactly.

## Workflow

1. **Search the ontology** — find the relevant entity in `graph.jsonl`
2. **Get the URL** — use the `location` field
3. **Fetch the source** — `web_fetch(location_url)` to get exact text
4. **Quote verbatim** — cite with URL

```bash
# Search by concept name
grep -i '"name": "symmetry"' references/graph.jsonl

# Search by keyword across definitions
python3 -c "
import json
for line in open('references/graph.jsonl'):
    d = json.loads(line)
    e = d.get('entity', {})
    p = e.get('properties', {})
    name = p.get('name', p.get('word', p.get('text', '')))
    defn = p.get('definition', '')
    loc = p.get('location', '')
    if 'TERM' in (name + defn).lower():
        print(f\"{e['type']}: {name}\")
        print(f\"  URL: {loc}\")
        print(f\"  Def: {defn[:200]}\")
        print()
"
```

## Quoting Rules (MANDATORY)

- **Always use exact quotes from the source at mflb.com.** Never paraphrase when the original is available.
- **Every quote must include the direct URL** from the entity's `location` field.
- **Quote format:**
  > "[exact text from mflb.com]"
  > — *An Immanent Metaphysics*, [section], [URL]
- **If the exact wording isn't in the ontology:** `web_fetch` the URL directly — get the real text.
- **Aphorisms:** use the `text` field from `graph.jsonl` verbatim. Do not alter.
- **Definitions:** use the `definition` field verbatim when citing what a term means.
- **Label synthesis clearly:** if applying the framework to a new situation, say so — don't present inference as direct quote.

## Ontology Contents (`references/graph.jsonl`)

767 entities across 5 types:

| Type | Count | Description |
|------|-------|-------------|
| Concept | 134 | Named ideas — modality, domain, definition, source URL |
| Axiom | 3 | Foundational axioms — statement, implications, source URL |
| Theorem | 11 | ICT, Symmetry Ethics, Continuity Ethics, Bell's/Godel mappings |
| Aphorism | 147 | From *Effective Choice* — exact text, themes, source URL |
| Implication | 4 | Cross-domain applications (physics, logic, ethics, consciousness) |

Relations: `implies`, `paired_with`, `contrasts_with`, `depends_on`, `has_modality`, `illuminates`, `defined_in`

## Chapter URLs

| Topic | URL |
|-------|-----|
| Entry point | https://mflb.com/8192 |
| Three Modalities | https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch1.htm#1_modalities |
| Axioms | https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch1.htm#1_axioms |
| ICT | https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch3.htm#1_ict |
| Symmetry / Continuity | https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch3.htm#1_symmetry |
| Ethics | https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch6.htm |
| Path of Right Action | https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch6.htm#2_path |
| Basal Motivations | https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch6.htm#2_basal |
| Aphorisms of Effective Choice | https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch5.htm |
| Mind | https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch8.htm |

## Attribution

Always attribute to Forrest Landry's *An Immanent Metaphysics*. Distinguish:
1. **Direct citation** — exact quote with source URL
2. **Close paraphrase** — labeled as paraphrase with source URL
3. **Agent synthesis** — labeled as your own application

Do not invent positions. Do not imply Forrest's endorsement of claims not grounded in the source text.
