---
name: self-improving-prompt
description: Triggers when user input is vague, missing goal/constraints/acceptance criteria, or contains words like "optimize/improve/fix it up". Also triggers when the user explicitly asks to refine or improve a prompt.
---

# self-improving-prompt

> Prompt refinement is not just rewording — it's clarifying the task, setting boundaries, and shaping verification criteria.

Transform vague user prompts into clear, actionable, verifiable versions. Show the refined result and let the user confirm before executing. Forms a closed loop with `self-improving-session` — which accumulates the user's preference signals over time.

## Quick Reference

| Situation | Action |
|-----------|--------|
| Vague request | Refine first |
| Already complete prompt | Execute directly, no popup |
| Substantial improvement | Show refined version + popup |
| No substantial improvement | Skip popup, execute original |
| User says "just do it" | Auto-apply |
| User says "only refine" | Return refined version, don't execute |

## Continue Modes

1. **Popup confirm (default)** — Show refined prompt, popup for user to choose refined or original, then execute
2. **Auto-apply** — When user says "just do it / skip confirm", show refined version then execute immediately
3. **Refine only** — When user only wants refinement without execution, return result only

## When NOT to Apply
- User input is already structured with clear goal, constraints, and acceptance criteria
- Single-step operations (delete a line, rename a variable, change a string)
- Simple factual questions or explanatory questions
- User explicitly says "don't refine" or "just do it"

## Workflow
1. Extract the original prompt and current session context (goal, constraints, tech stack, error messages, expected output).
2. Generate a refined prompt that ensures:
   - Core intent is preserved
   - Goal and boundaries are explicit
   - Output format is verifiable
   - Language is concise, no filler
3. Produce output according to the continue mode.
4. After the user makes a choice, generate a **learning signal** for `self-improving-session` — record preference patterns, not the full prompt text.

## Refined Prompt Structure

Include the following modules as needed (trim to fit, don't force all):
- Goal
- Context
- Constraints / Non-goals
- Execution Requirements
- Output Format
- Acceptance Criteria

See `references/prompt-patterns.md` for detailed patterns and examples.

## Output Templates

### A) Popup Confirm (default)

**First, judge whether refinement has substantial value.** If the refined prompt is only a minor rewording with no new goal/constraints/output format/acceptance criteria added, and no significant reduction in ambiguity, then **there is no substantial value**.

- **No substantial value**: No popup, no interruption. Execute the original prompt directly.
- **Has substantial value**: Execute the following two steps — do not skip or merge them.

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

## Heuristics
- Rewrite "optimize / speed up / make it better" into actionable steps with clear criteria.
- Fill in missing inputs, edge cases, and definition of done.
- Code tasks: specify scope of changes, verification method, expected deliverables.
- Content tasks: specify audience, tone, length, structural constraints.
- If critical context is missing, ask the minimum necessary clarifying questions; otherwise proceed.

## Integration with self-improving-session

- When the user chooses the refined version or rejects it, this is a **preference signal** for `self-improving-session`.
- `self-improving-session` only summarizes rules (e.g. "user prefers seeing refined version before confirming"), never records the full prompt text.
- Over time, the preference profile makes `self-improving-prompt` increasingly aligned with the user's habits.

## Priority Rules
- When the user explicitly specifies a flow, follow the user's instructions.
- When no explicit instruction is given, use popup confirm mode.

## Setup

To auto-trigger on every user input, add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"hookSpecificOutput\":{\"hookEventName\":\"UserPromptSubmit\",\"additionalContext\":\"You must invoke the self-improving-prompt skill to process user input. If the refined version adds substantial value (new goals/constraints/acceptance criteria), show refined prompt as plain text first, then call AskUserQuestion for user to choose refined vs original. If no substantial value, skip popup and execute original directly. Skip entirely for single-step instructions.\"}}'",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```
