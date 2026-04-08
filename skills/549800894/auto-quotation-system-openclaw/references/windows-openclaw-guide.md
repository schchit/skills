# Windows OpenClaw Guide

## Goal

Run the auto quotation workflow reliably in Windows-based OpenClaw environments.

## Recommended defaults

- Python launcher: `python`
- DOCX renderer: `native`
- Working directory: a writable project-local folder such as `C:\openclaw\work\quotation`
- Historical quotation directory: configure explicitly, do not rely on any macOS path

## Required dependency for native DOCX

Install:

```bash
python -m pip install python-docx
```

If `python-docx` is missing, the native renderer now exits with a clear installation hint instead of a raw import traceback.

## Why the old mode failed

The earlier version assumed:
- macOS `textutil` exists
- `/Users/...` style absolute paths are valid
- `/tmp/...` is available and meaningful
- `python3` is always the right launcher

These assumptions are not stable in Windows/OpenClaw.

## Current cross-platform behavior

### `generate_quote_draft.py`

Supports:
- `--docx-renderer auto`
- `--docx-renderer native`
- `--docx-renderer html`

Recommendation on Windows/OpenClaw:

```bash
python scripts/generate_quote_draft.py \
  --input C:\openclaw\work\requirement.md \
  --project-name "项目名称" \
  --vendor-name "深圳市小程序科技有限公司" \
  --quote-date "2026-04-07" \
  --tax-note "含税1个点普票" \
  --sample-library assets\seed-quote-sample-library.json \
  --profiles assets\seed-quote-calibration-profiles.json \
  --rate-cards assets\seed-domain-rate-cards.json \
  --output-md C:\openclaw\work\quote.md \
  --output-json C:\openclaw\work\quote.json \
  --output-docx C:\openclaw\work\quote.docx \
  --docx-renderer native
```

### DOCX rendering

Preferred renderer:
- `scripts/render_manual_quote_docx.py`

Fallback behavior:
- `scripts/render_quote_docx.py` will use `textutil` only when available
- if `textutil` is unavailable, it now falls back to the native renderer automatically

## OpenClaw node recommendation

- `input_router`: pass `work_dir` and `docx_renderer_mode`
- `estimate_engine`: propagate `docx_renderer_mode`
- `docx_renderer`: use `native` by default on Windows nodes

## Operational recommendation

For Windows/OpenClaw production:
1. Keep historical assets in a configurable workspace folder
2. Use the native DOCX renderer only
3. Treat seed sample library paths as reference labels, not executable file paths
4. Prefer manually curated business-module quotation mode for final client-facing quotes
