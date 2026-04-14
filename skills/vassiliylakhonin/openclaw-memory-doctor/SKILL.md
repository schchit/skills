---
name: openclaw-memory-doctor
description: Restore OpenClaw memory reliability in minutes: diagnose and fix missing recall, Dreaming stalls, embedding/provider errors, index drift, and weak promotion quality. Use when memory answers are poor or semantic recall is unavailable, and return clear root cause + verified fix steps.
user-invocable: true
metadata: {"openclaw":{"emoji":"🧠","os":["linux","darwin","win32"]}}
---

# OpenClaw Memory Doctor

Run symptom-first diagnostics for memory and dreaming issues.

## 2-minute wins

- "memory search пустой" -> run baseline + provider check, return root cause.
- "Dreaming ON, но diary не двигается" -> verify config/schedule + diary freshness.
- "после апдейта качество recall упало" -> reindex + promote diagnostics + verification gate.

## Use Cases

- semantic recall is weak or empty
- `memory_search` gives poor/no matches
- Dreaming status is off or not progressing
- embedding provider is not ready
- index is stale or missing chunks
- promotion flow does not move useful items

## Baseline Checks

Run first:

```bash
openclaw status
openclaw doctor --non-interactive
openclaw memory status
openclaw memory status --deep
```

## Symptom Routes

### A) "Semantic recall does not work"

```bash
openclaw doctor --non-interactive
openclaw memory status --deep
```

Check:
- provider selected in `agents.defaults.memorySearch.provider`
- API key/dependency readiness
- fallback behavior

### B) "Dreaming is off or not moving"

```bash
/dreaming status
openclaw memory status
```

Check:
- `plugins.entries.memory-core.config.dreaming.enabled`
- schedule/frequency/timezone
- recent dream diary updates (`DREAMS.md`)

### C) "Index is stale or empty"

```bash
openclaw memory index --force
openclaw memory status
```

Check:
- indexed files/chunks > 0
- source paths include MEMORY.md + memory/*.md

### D) "Promotion quality is poor"

```bash
openclaw memory promote --limit 10
openclaw memory promote-explain "<candidate text>"
```

Check:
- recency and relevance signals
- noisy/duplicate entries
- thresholds too strict for current corpus

## Safe Fix Policy

1. Prefer read-only checks first.
2. Apply smallest config change.
3. Re-run verification gates after each fix.
4. Ask confirmation before broad config rewrites.

## Verification Gates

After fixes, verify:

```bash
openclaw memory status --deep
openclaw doctor --non-interactive
```

Success criteria:
- embedding probe ready (or expected local mode)
- memory index healthy
- dreaming status matches intended config
- recall results improve on known test query

## Output Contract

Always return:
- symptom
- commands run
- root cause (or top 2 suspects)
- fix applied
- verification result
- next action

## Author

Vassiliy Lakhonin
