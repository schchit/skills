# Prompt Refinement Patterns

## By Task Type

### Code Tasks
When refining code-related prompts, prioritize clarifying:
- **Scope**: Which files / modules / functions are involved
- **Verification**: How to confirm the change works (tests, manual check, build)
- **Deliverables**: What the final output should be (diff, new file, refactored module)
- **Non-goals**: What should explicitly not be changed

**Example — before:**
> Help me optimize login performance

**Example — after:**
> Goal: Reduce login API response time from ~2s to <500ms
> Context: Backend is Express + PostgreSQL, login endpoint is /api/auth/login
> Constraints: Do not change the database schema or authentication logic
> Execution: Profile the endpoint first, identify the top 3 bottlenecks and fix them
> Verification: Run load tests before and after, compare p95 latency
> Acceptance: p95 < 500ms under 100 concurrent users

### Content Tasks
When refining writing or content prompts, prioritize clarifying:
- **Audience**: Who will read it
- **Tone**: Formal, casual, technical, friendly
- **Length**: Word count range or number of paragraphs
- **Structure**: Required sections and formatting constraints

**Example — before:**
> Write a project introduction for me

**Example — after:**
> Goal: Write a project introduction for our open-source CLI tool
> Audience: Developers using Claude Code
> Tone: Technically friendly and accessible, no marketing speak
> Length: 200–300 words
> Structure: What it does → Why it exists → How to install → Quick example

### General Tasks
When refining vague or open-ended tasks, prioritize clarifying:
- **Goal**: What does "done" look like
- **Context**: What do you already know
- **Boundaries**: What is out of scope
- **Output format**: How should the result be delivered

## Common Vague Phrases → Actionable Rewrites

| Vague phrase | Actionable rewrite |
|---|---|
| "optimize it" | Specify: which metric, target value, and constraints |
| "make it faster" | Specify: target latency/throughput, current baseline, acceptable tradeoffs |
| "make it better" | Specify: what the current problem is, what "better" means |
| "fix it up" | Specify: what to change, what to preserve, how to verify |
| "check if there are any issues" | Specify: review scope, types of issues to look for, severity threshold |
