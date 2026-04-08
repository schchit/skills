# OpenClaw Migration Notes

## Goal

Prepare this skill so the same workflow can later run inside OpenClaw with minimal rewriting.

## Keep Stable Interfaces

Keep these boundaries stable:

1. Input adapter: convert markdown or a vision-transcribed mind map into normalized JSON.
2. Retrieval adapter: load historical quotation corpus and return top similar cases.
3. Estimation engine: produce line items, role effort, assumptions, and total price.
4. Renderer: output markdown now; add DOCX renderer later without changing the estimate payload.

## Recommended OpenClaw Flow

1. Vision step: read the uploaded mind map image and convert it into structured markdown.
2. Parsing step: normalize markdown into the quotation input contract.
3. Retrieval step: query indexed historical quotation samples.
4. Estimation step: calculate module-level quote draft.
5. Rendering step: produce markdown, JSON, and optionally DOCX.

For the detailed node graph and contract-level design, read:

- [openclaw-workflow.md](openclaw-workflow.md)
- [../assets/openclaw-node-contracts.json](../assets/openclaw-node-contracts.json)

## Migration Constraints

- Avoid hard-coding Codex-only paths in runtime logic.
- Keep scripts runnable by `python3` with standard library only.
- Treat `/Users/m1/Documents/price` as seed training data, not a fixed production dependency.
- Preserve JSON output so OpenClaw can display or post-process the estimate.
- Add a dedicated OCR or multimodal step upstream instead of teaching this skill to OCR images itself.

## Suggested Future Upgrades

- Replace keyword matching with embeddings or reranking over historical quotations.
- Add a DOCX renderer that fills a branded quote template.
- Add configurable rate cards per project type.
- Store approved quotations and actual settlement data to improve calibration.
