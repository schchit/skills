---
name: mova-spec-guide
description: Answer questions about the MOVA specification language — schemas (ds.*), envelopes (env.*), verbs, episodes, global catalogs, instruction profiles, and the operator frame. Use when the user asks how to write a MOVA artifact, wants to understand any MOVA concept, or needs to validate whether something follows the MOVA spec. Reads from the local workspace spec clone and the public GitHub repo.
license: MIT-0
---

> **Ecosystem Skill** — Supports building and managing the MOVA ecosystem. Requires the `openclaw-mova` plugin.

# MOVA Spec Guide

Answer any question about the MOVA language — from basic concepts to schema-level validation — by reading the canonical spec documents in the workspace and referencing the public repository.

## What this skill does

1. **Explains MOVA concepts** — schemas (`ds.*`), envelopes (`env.*`), verbs, episodes, global catalogs, instruction profiles, runtime bindings, connectors, security layer, text/UI layer
2. **Reads authoritative source docs** — uses the local spec clone for immediate access; references the public GitHub repo for the canonical latest state
3. **Shows examples** — points to `examples/` files and explains them in context
4. **Validates artifacts** — given a JSON draft, checks it against the relevant MOVA schema and explains violations
5. **Maps concepts to practice** — explains how a concept applies to a real use case the user brings

## Source hierarchy

| Priority | Source | Use for |
|----------|--------|---------|
| 1 (primary) | Local workspace: `/home/mova/.openclaw/workspace/mova-spec/` | All reads — fast and always available |
| 2 (canonical reference) | GitHub: `https://github.com/mova-compact/mova-spec` | Latest version check, stable URLs to share |

**Always read from the local workspace first.** Only reference the GitHub repo if the user needs a link to share or asks about the latest uncommitted changes.

## Workspace layout

```
mova-spec/
  docs/
    mova_core.md                      ← core specification (start here for concept questions)
    mova_global_and_verbs.md          ← verbs, global catalogs, action_signature
    mova_operator_frame.md            ← operator frame: 13-axis audit lens
    mova_episodes_and_genetic_layer.md← episode structure and pattern memory
    mova_layers_and_namespaces.md     ← red-core / skills / infra layering
    mova_runtime_and_connectors.md    ← runtime bindings and connector contracts
    mova_security_layer.md            ← instruction profiles and security events
    mova_text_and_ui_layer.md         ← text channel separation
    MOVA_6.0.0_RELEASE_NOTES.md       ← latest changes: verb/tool/action_signature
  schemas/
    ds.mova_schema_core_v1.schema.json
    ds.mova_episode_core_v1.schema.json
    ds.instruction_profile_core_v1.schema.json
    ds.connector_core_v1.schema.json
    ds.runtime_binding_core_v1.schema.json
    ds.ui_text_bundle_core_v1.schema.json
    ds.mova4_core_catalog_v1.schema.json
    ds.security_event_episode_core_v1.schema.json
    env.*.schema.json (envelopes)
  examples/
    mova4_core_catalog.example.json
    action_signature.example.json
    env.*.example.json
  global.episode_type_catalog_v1.json
  global.security_catalog_v1.json
  global.layers_and_namespaces_v1.json
  global.text_channel_catalog_v1.json
  README-mova-spec.md
```

## Core MOVA concepts (quick map)

| Concept | What it is | Where defined |
|---------|-----------|---------------|
| `ds.*` schema | JSON Schema describing what data looks like | `schemas/ds.*.schema.json` |
| `env.*` envelope | Typed speech-act: a request, command, or event over `ds.*` data | `schemas/env.*.schema.json` |
| Verb | Abstract operation type: create, update, route, record, publish, analyze, ... | `docs/mova_global_and_verbs.md` |
| Tool | Execution channel (`tool_id`); `0` = tool-less | `docs/mova_global_and_verbs.md §4.5` |
| Action signature | Atomic unit for policy: `(verb_id, tool_id, target_kind?)` | `MOVA_6.0.0_RELEASE_NOTES.md` |
| Episode | Structured record of one meaningful work step | `ds.mova_episode_core_v1` |
| Instruction profile | Declarative policy and guardrail set for an executor | `ds.instruction_profile_core_v1` |
| Global catalog | Shared vocabulary for all layers | `global.*.json` |
| Operator frame | 13-axis audit lens (what/how/where/when/why/...) | `docs/mova_operator_frame.md` |
| Genetic layer | Pattern memory built from episodes over time | `docs/mova_episodes_and_genetic_layer.md` |

## How to handle different question types

### Concept question
Read the relevant `docs/` file. Summarize the answer. Quote the exact definition. Show a minimal example if one exists in `examples/`.

### Schema question
Read the relevant `schemas/*.schema.json`. Explain each field: type, required/optional, allowed values. Show how the field relates to the concept.

### Validation question
Read the user's JSON. Read the target schema. Check required fields, field types, allowed enum values. Report each violation with the relevant schema field and rule.

### How to write question
Read the most relevant `docs/` file. Walk through a minimal valid instance step by step. Reference the `examples/` file if it exists.

### Catalog lookup
Read the relevant `global.*.json`. Quote the exact entry. Explain the purpose in one sentence.

## MOVA version

Current version in the workspace: **MOVA 6.0.0**

Key additions in 6.0.0 (see `MOVA_6.0.0_RELEASE_NOTES.md`):
- Normative definition of `verb`, `tool`, `action_signature`
- `tool_id = 0` is canonical for tool-less actions
- Policy matching priority: `action_signature > verb_id > tool_id`
- `action_labels` in domain dictionaries (readability, no normative weight)

## Rules

- NEVER invent schema field names, verb IDs, or catalog values — always read from workspace files
- NEVER reference schema URLs without first reading the local file to confirm the content
- If the user asks about a concept not yet defined in the spec — say so explicitly, do not improvise
- Always cite which document and section the answer comes from
- If the user provides a JSON artifact to validate — read the correct schema file first, then compare field by field
- MOVA does not execute — never describe MOVA artifacts as having runtime behavior
