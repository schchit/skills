---
name: auto-quotation-system
description: Build a reusable quotation workflow for software projects from markdown requirements, feature outlines, or mind-map screenshots that have been transcribed into text. Use when Codex needs to mine historical quotation DOCX files, normalize pricing inputs, estimate module-level effort, generate a quotation draft in markdown and JSON, or prepare the workflow for later migration into OpenClaw.
---

# Auto Quotation System

## Overview

Use this skill to turn historical quotation files and a new requirement document into a structured quotation draft. Prefer module-level estimation, explicit assumptions, and stable JSON output over a single total-price guess.

This skill is intended to run in both macOS and Windows/OpenClaw environments. Avoid hard-coded local paths, prefer `python` over platform-specific launchers in documentation, and prefer the native DOCX renderer when cross-platform stability matters.

## Workflow

### 1. Normalize the input

Follow this decision order:

1. If the user provides markdown or a plain-text requirement document, use it directly.
2. If the user provides a mind-map image or a screenshot embedded in a document, first transcribe it into structured markdown with a multimodal step.
3. If the user provides a DOCX requirement file, extract or summarize the requirement text before pricing.

Do not estimate directly from an unreadable image. First convert the mind map into a text outline with modules, features, and notable dependencies.

Use this normalized structure:

- Project name
- Delivery channels
- Business goal
- Feature list
- Non-functional requirements
- Assumptions and exclusions

Read [references/quotation-data-model.md](references/quotation-data-model.md) when you need the exact input and output shape.

### 2. Build or refresh the historical quotation corpus

When the task needs historical calibration, run:

```bash
python scripts/extract_docx_corpus.py \
  --input-dir /path/to/history-docx-dir \
  --output /path/to/work/quotation-corpus.json
```

This script extracts:

- Paragraph text
- Table rows
- Section labels
- Image counts
- Domain hints
- Top keywords per document

Use the corpus to find similar past quotations, common section layouts, and common delivery boundaries. Treat the historical documents as calibration data, not as exact truth to copy.

### 3. Generate a quotation draft

After the requirement is normalized, run:

```bash
python scripts/generate_quote_draft.py \
  --input /path/to/requirement.md \
  --project-name "项目名称" \
  --vendor-name "深圳市小程序科技有限公司" \
  --quote-date "2026-04-07" \
  --tax-note "含税 1 个点普票" \
  --corpus /path/to/work/quotation-corpus.json \
  --sample-library assets/seed-quote-sample-library.json \
  --profiles assets/seed-quote-calibration-profiles.json \
  --rate-cards assets/seed-domain-rate-cards.json \
  --output-md /path/to/work/quote.md \
  --output-json /path/to/work/quote.json \
  --output-docx /path/to/work/quote.docx \
  --docx-renderer auto
```

The generator currently produces:

- Requirement summary
- Module-level quotation detail
- Role-based effort summary
- Suggested payment schedule
- Delivery boundaries
- Similar historical cases
- Open questions

The generator uses a hybrid estimation strategy:

- Start with transparent heuristic effort estimation
- Calibrate module prices against the structured sample library when matching historical samples exist
- Prefer stratified calibration profiles when category, domain, and channel signals are available
- Surface matched domain rate cards so the operator can quickly sanity-check the overall price band
- Emit calibration evidence in the markdown and JSON output

If the result feels off, revise the normalized requirement, refresh the sample library, or adjust the generated line items instead of hiding the uncertainty.

If the user needs a client-facing quotation file, prefer generating DOCX in the same run by passing `--output-docx`. In Windows/OpenClaw environments, the default `auto` renderer will choose the native DOCX path instead of the macOS-only HTML conversion path.

### 4. Review before presenting

Always check:

1. Whether third-party costs were incorrectly included in development fees
2. Whether AI, OCR, ERP, hardware, multi-end delivery, or private deployment require higher effort
3. Whether the quote is missing a management backend, testing, deployment, or maintenance phase
4. Whether the output clearly states assumptions, exclusions, and change-control rules

If the requirement is incomplete, still produce a draft, but add pending questions rather than silently guessing.

## Resources

### `scripts/extract_docx_corpus.py`

Use this script to mine historical quotation DOCX files under a directory and export a reusable JSON corpus.

### `scripts/generate_quote_draft.py`

Use this script to convert a markdown requirement document into:

- A markdown quotation draft
- A machine-friendly JSON payload

### `scripts/build_quote_sample_library.py`

Use this script after refreshing the corpus to extract reusable pricing samples such as:

- Project total prices
- Module or sub-system prices
- Design, testing, deployment, and distribution items
- Role-effort rows from staffing tables

Example:

```bash
python scripts/build_quote_sample_library.py \
  --corpus /path/to/work/quotation-corpus.json \
  --output /path/to/work/quote-sample-library.json
```

Use the resulting sample library to calibrate later estimators, detect common price bands, or build project-type-specific rate cards.

### `scripts/build_quote_calibration_profiles.py`

Use this script to compile the sample library into stratified calibration profiles by:

- category
- domain mix
- delivery channel mix

Example:

```bash
python scripts/build_quote_calibration_profiles.py \
  --corpus /path/to/work/quotation-corpus.json \
  --sample-library /path/to/work/quote-sample-library.json \
  --output /path/to/work/quote-calibration-profiles.json
```

Use the generated profile file when you want calibration to distinguish between project types such as AI platforms, mini-program systems, app projects, or cross-border products.

### `scripts/build_domain_rate_cards.py`

Use this script to compile domain-level rate cards for major project families such as:

- AI projects
- Mini-program projects
- APP projects
- Platform projects
- IoT projects
- Cross-border projects

Example:

```bash
python scripts/build_domain_rate_cards.py \
  --corpus /path/to/work/quotation-corpus.json \
  --sample-library /path/to/work/quote-sample-library.json \
  --output /path/to/work/domain-rate-cards.json
```

Use the rate card file to:

- show top-level price bands early
- provide a safer fallback when fine-grained profiles are sparse
- explain why one project family is priced differently from another

### `scripts/render_quote_docx.py`

Use this script when you already have a quote JSON payload and need a formal Word document.

Example:

```bash
python scripts/render_quote_docx.py \
  --input-json /path/to/work/quote.json \
  --output-docx /path/to/work/quote.docx
```

Implementation note:

- The script renders structured HTML first
- On macOS, it converts the HTML into `.docx` via `textutil`
- On Windows/OpenClaw or when `textutil` is unavailable, it falls back to the native renderer automatically
- The default renderer includes a cover block, summary info cards, numbered sections, and styled tables for a more business-ready quotation layout
- The renderer also supports template-aligned fields such as vendor name, quote date, and tax note so the generated DOCX can more closely match the existing quotation style

### `scripts/render_manual_quote_docx.py`

Use this script when you need a cross-platform native `.docx` renderer, especially in Windows/OpenClaw environments.

Dependency:

```bash
python -m pip install python-docx
```

Example:

```bash
python scripts/render_manual_quote_docx.py \
  --input-json /path/to/work/quote.json \
  --output-docx /path/to/work/quote.docx
```

Use it when:

- the operator has already regrouped the modules by business workflow
- the environment is Windows/OpenClaw
- you want native Word output without relying on `textutil`

### `references/quotation-data-model.md`

Read this file when you need the normalized input contract, output contract, and pricing heuristics.

### `references/openclaw-migration.md`

Read this file when the user asks how to migrate the workflow into OpenClaw or how to keep interfaces stable for a later system integration.

### `references/openclaw-workflow.md`

Read this file when the user wants the OpenClaw workflow broken into concrete nodes, execution order, fallback behavior, or migration order.

### `references/validation-report.md`

Read this file when the user asks how well the current system performs on real historical examples or what the next calibration targets should be.

### `assets/quotation-template.md`

Use this template when you need a human-edited quotation shell or a baseline format for a later DOCX renderer.

### `assets/seed-quote-sample-library.json`

Use this as a seed dataset extracted from `/Users/m1/Documents/price`. It is useful for inspection, prototyping, and downstream OpenClaw migration, but it should be refreshable rather than treated as immutable truth.

### `assets/seed-quote-calibration-profiles.json`

Use this as the seed stratified rate-card layer built from the seed sample library. Prefer it over the flat sample library when the current project has a clear domain and channel signature.

### `assets/seed-domain-rate-cards.json`

Use this as the seed domain rate-card layer. It summarizes the median total project price and median category prices for each major project domain.

### `assets/openclaw-node-contracts.json`

Use this as the machine-readable contract sketch for an OpenClaw implementation. It describes the primary nodes, their inputs, and their outputs.

## Editing Guidance

Prefer this sequence when doing real work with the skill:

1. Normalize the requirement into structured markdown
2. Refresh the corpus if the historical files changed
3. Generate the draft markdown and JSON
4. Review and tighten assumptions
5. If needed, convert the markdown into a branded Word document in a separate step

Keep runtime logic lightweight:

- Prefer `python3` plus standard library
- Keep paths configurable
- Keep JSON output stable for downstream systems
- Keep OCR or vision outside this skill and upstream of the estimation step

## Output Standard

The final response to the user should usually include:

1. A short pricing conclusion
2. The main assumptions and exclusions
3. The generated quote file locations
4. Any open questions that materially affect price

### `references/windows-openclaw-guide.md`

Read this file when the skill is being installed or executed in a Windows/OpenClaw environment and you need the platform-safe renderer, command style, and path conventions.

### `assets/openclaw-windows-example.json`

Use this file as a reference payload when wiring the skill into a Windows-based OpenClaw workflow. It demonstrates `work_dir` and `docx_renderer_mode: native`.
