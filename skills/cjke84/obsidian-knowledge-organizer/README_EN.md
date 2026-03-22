# obsidian-knowledge-organizer

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-cjke84%2Fobsidian--knowledge--organizer-blue?logo=github)](https://github.com/cjke84/obsidian-knowledge-organizer)

An Obsidian vault workflow skill that turns article links, drafts, and notes into structured Obsidian-ready Markdown with duplicate checks, tags, summaries, related-note suggestions, and image downloads.

## What it does

- extract the article
- check duplicates and return a structured decision
- generate tags, summary, and metadata
- download images into `assets/` and keep readable references, including common fields like `src`, `data_src`, `data-original`, `data-lazy-src`, `srcset`, `url`, `image_url`, and `original`
- render an Obsidian-ready note

## Capabilities

- OpenClaw- and Codex-compatible skill for Obsidian-native knowledge organization
- Supports public-account posts, Xiaohongshu links, and ordinary web pages
- Obsidian-ready note generator for vault workflows
- validates tags against the repository tag contract
- recommends directly linkable related notes

## Use cases

- store in the knowledge base
- organize articles
- apply tags
- archive notes
- generate summaries
- suggest related notes

## `draft.images` example

```yaml
images:
  - path: /absolute/path/to/local.png
    alt: Local image
  - src: https://example.com/cover.png
    alt: Remote image
  - srcset: https://example.com/cover-1x.png 1x, https://example.com/cover-2x.png 2x
    alt: Responsive image
```

`path` is for local files. `src` / `data_src` / `data-original` / `data-lazy-src` / `original` etc. are used for remote images; `srcset` prefers the highest-value candidate.

## Quick start

```bash
pytest -q
python scripts/check_duplicate.py "New Title" --content "$(cat draft.md)" --json
python scripts/find_related.py alpha beta --title "New Title" --json
```

## Related

- [中文介绍](README_CN.md)
- [Install Skill for Agent](INSTALL.md)
- [GitHub Repository](https://github.com/cjke84/obsidian-knowledge-organizer)
