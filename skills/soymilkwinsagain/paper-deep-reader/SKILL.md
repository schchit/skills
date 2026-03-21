---
name: paper-deep-reader
slug: paper-deep-reader
version: 1.0.0
description: Read one research paper carefully, reconstruct its logic, and write a detailed markdown note with equations, evidence, limitations, and implementation details.
metadata: {"openclaw":{"emoji":"📚"}}
---

# Paper Deep Reader

## When to Use

Use this skill when the task is to read one selected paper carefully and produce a **detailed `.md` note**, not a shallow summary.

Use it for papers in any field. Adapt the note to the paper: theory, methods, experiments, systems, economics, statistics, social science, biology, or interdisciplinary work.

## First Read

Before writing, read `{baseDir}/references/reading-workflow.md` and `{baseDir}/references/note-template.md`.

## Output Standard

Produce a note that helps a strong graduate student understand:

1. What problem the paper solves and why it matters.
2. What the core idea is.
3. How the method works in enough detail to re-derive or implement it.
4. What assumptions, tradeoffs, and limitations matter.
5. How this paper connects to neighboring literature and to future work.

The note should be pedagogical, precise, and evidence-based. Prefer exact claims over praise.

## Core Rules

1. **Read the paper before judging it.** Do not infer the contribution from title and abstract alone.
2. **Separate the authors’ claims from your evaluation.** Mark clearly what is stated in the paper and what is your interpretation.
3. **Preserve the mathematical spine.** Include the main notation, objective, derivation, theorem statement, estimator, algorithm, or complexity result when relevant.
4. **Trace evidence to sections, figures, tables, or experiments.** If a claim is weakly supported, say so.
5. **Explain mechanisms, not just outcomes.** A good note answers “why should this work?” and “when will it fail?”
6. **Be field-aware.** For theory papers, emphasize assumptions and proofs; for empirical papers, emphasize identification, data, baselines, ablations, and robustness; for systems papers, emphasize workloads, bottlenecks, and real performance metrics.
7. **Use formulas and code blocks when they clarify.** Do not add them decoratively.

## Writing Rules

- Default to markdown headings and short paragraphs.
- Use displayed math for key equations.
- Use code blocks for algorithm sketches, pseudocode, or implementation caveats.
- Prefer a note length that is substantial enough to be useful; do not compress a dense paper into a few bullets.
- If the paper is unclear, incomplete, or overstated, record that explicitly.

## File Saving

When the user asks for a saved note, create a markdown file.

Default save behavior:

- Save the note to the specified directory if given, using the designed filename if provided.
- Otherwise save the note next to the paper as `detailed-note.md`.

## Quick Reference

- Workflow: `{baseDir}/references/reading-workflow.md`
- Note template: `{baseDir}/references/note-template.md`
- Quality checklist: `{baseDir}/references/quality-checklist.md`
