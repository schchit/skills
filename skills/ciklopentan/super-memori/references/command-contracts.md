# super_memori v3 — Command Contracts

## Public commands
The target v3 public interface is exactly four commands:

1. `query-memory.sh`
2. `memorize.sh`
3. `index-memory.sh`
4. `health-check.sh`

## `query-memory.sh`
### Purpose
Retrieve memory by exact, semantic, hybrid, recent, or learning-oriented query.

### Target flags
- `--mode auto|exact|semantic|hybrid|recent|learning`
- `--type episodic|semantic|procedural|learning|buffer|all`
- `--json`
- `--limit N`
- `--from DATE`
- `--to DATE`
- `--tags a,b,c`
- `--reviewed-only`

### Target exit codes
- `0` results found
- `1` no results
- `2` degraded mode but partial/usable results returned
- `3` retrieval stack unavailable
- `4` bad arguments
- `5` internal error

### Required output fields
- `mode_requested`
- `mode_used`
- `degraded`
- `warnings`
- `index_fresh`
- `results`

## `memorize.sh`
### Purpose
Write a useful learning record that can improve future behavior.

### Target types
- `error`
- `correction`
- `lesson`
- `insight`

### Rule
Do not auto-log every failure. Only write when the event teaches future behavior.

## `index-memory.sh`
### Purpose
Manage lexical and semantic index maintenance.

### Target modes
- `--incremental`
- `--full`
- `--rebuild-fts`
- `--rebuild-vectors`
- `--stats`
- `--vacuum`

## `health-check.sh`
### Purpose
Verify the health of canonical files, indexes, freshness, and backlog.

### Status model
- `OK`
- `WARN`
- `FAIL`
