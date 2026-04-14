# self-improving-session Merge Reference Details

## Merge Conflict Priority (highest to lowest)

1. Explicit user correction in this session
2. Existing `[stable]` rules
3. `[tentative]` rules re-validated in this session
4. Newly discovered `[tentative]` rules

Rules:
- A new `[tentative]` cannot overwrite an existing `[stable]`
- Only an explicit user correction can rewrite a `[stable]` rule
- Two rules with the same meaning but different wording should be merged into one, not kept side by side

---

## Tentative Expiry Strategy

- If a `[tentative]` rule is contradicted by an opposing signal, replace it directly
- If a rule goes unvalidated across multiple consecutive sessions, it can be deleted (don't let tentative rules accumulate indefinitely)
- If validated again, upgrade to `[stable]`

---

## Where to Write Rules

| Rule Type | Target File |
|-----------|-------------|
| Cross-project workflow preferences and collaboration rules | `~/.claude/CLAUDE.md` |
| Coding conventions and architecture decisions specific to the current project | Project `CLAUDE.md` |
| One-off debug lessons or temporary fix notes | `tasks/lessons.md` |

Do not write temporary fix notes into CLAUDE.md.

---

## Examples

```markdown
- Don't summarize at the end of responses [stable]
- User prefers seeing the refined prompt before confirming [stable]
- ~~Always show popup confirmation~~ → only show popup when refinement has substantial value [corrected: 2026-04-10]
- Write scope explicitly for code tasks [tentative]
```

---

## self-improving-prompt Preference Signal Judgment

- Repeatedly chooses the same version → store as stable preference
- One-off different choice → don't overfit, likely scenario-specific
- Explicit verbal correction ("don't show me the original anymore") → promote immediately to a rule
