# self-improving-prompt Reference Details

## Output Templates

### A) Popup Confirm (default)

**Step 1 (required): Output the refined prompt as plain text in the chat first.**

> **Refined Prompt**
> <full refined content>

**Step 2 (required, after Step 1): Call AskUserQuestion popup for user to choose.**
Options:
- A: Continue with refined prompt (recommended)
- B: Continue with original prompt

Prohibited:
- Do not show the popup without first displaying the refined content
- Do not put the refined content inside AskUserQuestion's description as a substitute for Step 1
- Step 1 and Step 2 must be completed in the same reply

Execute after the user chooses.

### B) Auto-apply

> **Refined Prompt**
> <refined content>

---
Then execute immediately.

### C) Refine only

> **Refined Prompt**
> <refined content>

Do not execute the task.

---

## Learning Signal Event Types

Normalized preference events passed to `self-improving-session`:

| Event | Meaning |
|-------|---------|
| `choose_refined` | User chose the refined version |
| `choose_original` | User chose the original version |
| `auto_apply_requested` | User requested direct execution, no popup |
| `explicit_no_popup` | User explicitly said no popup |
| `explicit_show_both` | User explicitly requested to compare both versions |
| `explicit_refine_only` | User only wants the refined result, no execution |

Rules:
- Only record preference labels, never record the full refined prompt text
- Do not record specific task details — avoid mistaking a one-off scenario for a long-term rule
- If the user gives an explicit verbal correction, treat it as a correction rule first, not a regular preference stat

---

## Clarification Question Rules

If critical context is missing:
- Ask at most **1–2 blocking questions** (prerequisites without which execution is impossible)
- If what's missing is "optional enhancement info" rather than "execution prerequisites", don't interrupt — proceed directly
- Don't ask unnecessary questions just to appear thorough
