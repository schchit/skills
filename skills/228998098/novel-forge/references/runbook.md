# Novel Forge Runbook

## 1. Resume or new project
- If the user says continue/resume/truncated, discover candidate projects first.
- Show the candidates with title, latest chapter, and checkpoint.
- Ask the user to choose if more than one matches.
- If only one project matches, confirm it and continue.

## 2. Model mapping
- Read current model inventory.
- Ask for a role→model mapping for multi-agent work.
- Persist the mapping in `project.json.models`.
- If only one model is available, ask whether to reuse it across roles.
- If single-agent is selected, set `orchestrator` and collapse the rest into `n/a` or the same model by policy.

## 3. Bootstrap gate
Do not generate canon until these are known:
- title
- genre / audience
- target length or chapter count
- taboo list
- core premise
- execution mode
- model assignment table when multi-agent is selected
- chapter/scene checkpoint for resume work

## 4. Canon order
Use this order and do not parallelize phase 0:
1. Worldbuilding
2. Characters
3. Outline
4. Volume plan if needed
5. Chapter beats
6. Style samples
7. Style lock

## 5. Chapter loop
For each chapter:
1. Load the smallest relevant canon slice.
2. Write the draft.
3. Review the draft.
4. Revise if needed.
5. Accept the chapter.
6. Update memory and state.
7. Write `state/current.json` immediately after acceptance.

## 6. Resume summary
When resuming, begin with:
- what is known
- what is uncertain
- where the next prose starts

## 7. Long-run maintenance
- Refresh summaries every 2–3 chapters.
- Run a deeper canon/style audit every 5–10 chapters.
- Stop before unresolved conflicts pile up.
- After each checkpoint, update `state/current.json` so the latest chapter boundary is always visible in one place.

## 8. Minimal task packet
Send writers only:
- chapter goal
- opening state
- key beats
- ending hook
- relevant canon slice
- style constraints
- forbidden deviations
- current character state
