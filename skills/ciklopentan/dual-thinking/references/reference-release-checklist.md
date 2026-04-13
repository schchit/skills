# Reference Release Checklist
#tags: skills review

Use this checklist before promoting the current line from `reference-candidate` to `reference-release`.
Internal reference-line maturity is separate from user-facing package/publication status (`PUBLISH_STATUS`).

Promotion status: pending final validation-pack rerun and successful ClawHub publication for `v8.5.11`. If both succeed, the line is ready for promotion from `reference-candidate` to `reference-release`.

- `SKILL.md` aligned with the active candidate-line runtime contract
- `GOVERNANCE.md` aligned with the active candidate-line governance/release policy
- `references/round-output-contract.md` aligned with `SKILL.md`
- `references/validator-schema.md` aligned with `SKILL.md`
- required scenario tests passed
- required scenario evidence recorded in `references/verification-evidence.md`
- required scenario evidence recorded in `references/reference-test-log.md`
- no unresolved contradiction between weak-model shortcut and normal consultant-bearing flow
- no unresolved contradiction between mode-specific execution and the shared closing tail
- no unresolved contradiction between inline runtime authority and subordinate reference/support surfaces
- runtime/governance boundary rules are synchronized across `SKILL.md`, `GOVERNANCE.md`, `references/runtime-contract.md`, and `references/self-evolution-lens.md`
- current bugfix/clarification work remains honest about the frozen `v8.5.9 reference-release` baseline and does not smuggle new structural doctrine into the line without explicit evidence
