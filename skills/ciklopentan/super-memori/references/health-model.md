# super_memori v3 — Health Model

## Core health checks
These determine `OK/WARN/FAIL`.
1. canonical files readable
2. lexical DB openable
3. FTS query works
4. semantic backend reachable
5. embedding/rerank dependencies available
6. queue backlog within threshold
7. freshness age acceptable

## Quality checks
These are important, but should not alone define system health.
8. orphaned metadata/chunks below threshold
9. duplicate growth under control
10. pending review load acceptable

## Health statuses
- `OK` — core retrieval layers healthy
- `WARN` — degraded but usable
- `FAIL` — reliable retrieval is not available

## Freshness policy
- lexical stale: canonical files changed after last lexical index time
- semantic stale: canonical files changed after last semantic index time
- warning threshold: 24 hours stale
- critical threshold: 7 days stale
- stale results should be returned with warnings rather than silently hidden

## Freshness fields
- lexical freshness
- semantic freshness
- queue backlog age
- last successful full build
- last successful incremental update

## Rule
If users or agents are likely to make wrong decisions because memory is stale or degraded, health must say so explicitly.
