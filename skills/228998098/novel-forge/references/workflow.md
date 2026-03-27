# Workflow

## 1. Project bootstrap

### 1.1 Decide execution mode
- If the request is a continuation/resume, run project discovery first and show candidate projects before anything else.
- Default to multi-agent unless the user explicitly asks for single-agent.
- If you will use multiple agents, read the current model inventory and ask the user to map models to roles.
- If you will use a single agent, state that explicitly and do not fabricate a role table.

### 1.2 Gather and lock bootstrap inputs
1. Create a project state bundle.
2. Confirm target genre, audience, tone, length or chapter count, and taboo list.
3. Confirm the core premise.
4. Require author confirmation before locking premise, hard canon, and style.

### 1.3 Bootstrap gate criteria
Do not proceed to canon generation until all of these are satisfied:
- title exists
- genre / audience exist
- target length or chapter count exists
- taboo list exists
- premise is explicitly confirmed
- execution mode is explicit (single-agent or multi-agent)

If any item is missing, stop and ask for it instead of drafting ahead.

### 1.4 Operational state
- Treat `state/current.json` as the concise runtime snapshot when present.
- Keep it aligned with `project.json`, chapter state, and recovery notes.
- Use it as the first place to check the latest chapter boundary and recovery target.
- After each accepted chapter, write back `workflow.step`, `chapter.currentChapterIndex`, `chapter.nextChapterIndex`, `recoveryCheckpoint`, and the latest state delta.

## 2. Canon generation order

Only enter this stage after the bootstrap gate has passed.

1. Worldbuilding
2. Characters
3. Full outline
4. Volume plan, if needed
5. Chapter beats
6. Style samples
7. Style lock

## 3. Style sampling

Use one fixed scenario for every candidate.

Do not sample style before the premise and core tone are locked; otherwise the samples will drift and mislead the author.

Suggested scenario ingredients:
- protagonist entrance
- a mild conflict
- one dialogue exchange
- one sensory detail block
- one inner thought
- one ending hook

## 4. Resume / 断档续写

When the user wants to continue from a truncated draft or restore a partial chapter:

1. Discover candidate projects first if the workspace may contain more than one active novel.
2. Present the matching projects with title, genre, latest chapter, checkpoint, and resume metadata.
3. Let the user choose the project before recovering canon.
4. Identify the last stable checkpoint.
5. Read only the project state, outline, recent summaries, and partial draft needed to recover context.
6. Separate hard canon from inferred material.
7. State the resume target before generating new prose.
8. Resume from the last stable sentence or beat boundary.
9. Never rewrite unrelated sections unless the user asks.
10. If essential facts are missing, stop and ask.
11. If the fragment is too short to recover safely, ask for the missing paragraph, summary, or chapter beat instead of manufacturing a bridge.
12. When resuming, lead with a recovery summary so the author can verify the recovered state before the prose continues.

## 5. Chapter production loop

1. Load only the relevant canon slice.
2. Draft the chapter.
3. Review against canon and style.
4. Revise if needed.
5. Archive state and memory.

## 6. Long-run maintenance

Run periodic checkpoints every 5–10 chapters:
- refresh summary
- compress memory
- compare outline vs reality
- identify style drift
- identify dangling plot threads
- ask the user before large retcons

## 7. Batch writing

For 3+ chapters:
- split into small batches
- checkpoint between batches
- do not let unresolved conflicts accumulate
- keep chapter endings forward-driving
