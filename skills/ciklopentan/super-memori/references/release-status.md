# super_memori — Release Status Model

## 3.x meaning
`3.x` is the lexical-first historical line.
That line means:
- public four-command surface
- lexical index baseline
- health check + degraded semantic reporting
- semantic/hybrid mostly treated as future-spec or compatibility surface

It is now a frozen historical interpretation line, not the current runtime truth.

## 4.0.0 meaning
`4.0.0` is the stable current-generation local-only runtime line reserved for the first equipped-host-verified stable release.
It means the runtime itself can truthfully claim:
- lexical search implemented
- semantic search implemented in code
- vector indexing implemented in code
- hybrid fusion implemented in code
- temporal / relation-aware rerank implemented in code
- integrity audit implemented in code
- pattern-mining / manual-promotion support implemented in maintenance surfaces
- docs distinguish implemented capability from host-state activation
- host-profile shaping can distinguish `standard` from `max` without changing canonical truth

It does **not** mean every host is semantic-ready by default.
A host may still legitimately run `4.0.0` in degraded lexical mode if local semantic prerequisites or vector build state are missing.

## Candidate-line interpretation
The current candidate preparation target is `4.0.0-candidate.10`.
That means:
- the v4 runtime capabilities claimed as implemented are present in code
- host-state activation may still be degraded on a given machine
- maintenance-only capabilities are documented as maintenance-only, not as weak-model runtime commands
- stable `4.0.0` promotion remains blocked until an equipped host passes the stable-host readiness sequence in `references/stable-host-readiness.md`
- `max` host shaping is only a truthfully detectable runtime optimization on an actually equipped host; it must not be claimed from a smaller machine
