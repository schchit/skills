# super_memori v3 — Weak Model Guidance

## Why this file exists
The target operator is a weaker model. The interface must be safe under literal, uneven execution.

## Rules
1. Expose only four public commands.
2. Hide backend choice behind `query-memory.sh`.
3. Prefer `--mode auto` by default.
4. Use explicit exit codes and explicit warnings.
5. Do not require the model to interpret index freshness from raw logs.
6. Do not use absolute wording like "never grep manually" unless it is truly always correct.
7. Degraded mode is valid operation, but must be surfaced clearly.

## Good pattern
"Run `query-memory.sh --json <query>` and use the returned warnings/results."

## Bad pattern
"Decide whether to use grep, vectors, or direct file scans based on intuition."
