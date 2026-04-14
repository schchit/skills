---
name: obsidian-wiki
description: >
  Build and maintain a compiled LLM Wiki inside an Obsidian vault following
  Karpathy's pattern. Use when working with an Obsidian vault as a persistent
  knowledge base: ingesting raw sources into `raw/`, compiling or updating
  interlinked wiki pages under `wiki/`, generating an index, linting for
  broken links/orphans/staleness, maintaining taxonomy/schema files, or
  answering questions from pages already compiled into the wiki.
  NOT for: general Obsidian note-taking or plugin management (use `obsidian`
  skill), simple note creation, vault syncing, or generic Q&A that doesn't
  involve a compiled wiki vault.
---

# Obsidian Wiki

Implements Karpathy's LLM Wiki pattern inside an Obsidian vault.
The agent is the compiler; Obsidian is the IDE; the wiki is the codebase.

## Prerequisites

- `bash`, `python3` — required by all scripts
- `pdftotext` — optional, for `extract-book-digests.sh` (install via `poppler`)
- `markdownlint-cli2` — optional, for markdown structure checks (auto-installed via `npx`)

## Vault Resolution

Resolve the vault path at runtime. Store it in `$VAULT` for all operations.

Preferred methods (in order):
1. If the user specifies a vault path, use it directly
2. Read the Obsidian config file to find the open vault:

```bash
python3 -c "
import json, pathlib, os
# Obsidian stores vault config in a platform-dependent location
for p in [
    'Library/Application Support/obsidian/obsidian.json',
    '.config/obsidian/obsidian.json',
    '.var/app/md.obsidian.Obsidian/config/obsidian/obsidian.json',
]:
    f = pathlib.Path.home() / p
    if f.exists():
        for v in json.loads(f.read_text()).get('vaults',{}).values():
            if v.get('open'): print(v['path']); break
        break
"
```

3. Use `obsidian-cli print-default --path-only` if available
4. Before any write, print the resolved `$VAULT` path. If it was inferred via Obsidian config or `obsidian-cli`, get user confirmation before continuing.

The skill and scripts make no assumptions about the vault location. All paths
are relative to `$VAULT`. Scripts require Bash and python3; they use BSD-compatible
grep/sed/awk and are tested on macOS and Linux.

## Vault Layout

```
<vault>/
├── raw/                    # Immutable source documents
│   ├── articles/           # Web clips, blog posts
│   ├── papers/             # arXiv, IEEE, ACM papers
│   ├── projects/           # Project notes, meeting transcripts
│   ├── books/              # Book chapters, excerpts
│   └── assets/             # Images, diagrams (downloaded locally)
├── wiki/                   # LLM-compiled pages (agent-owned)
│   ├── entities/           # People, systems, projects, orgs
│   ├── concepts/           # Ideas, patterns, technologies, methods
│   ├── syntheses/          # Cross-cutting summaries, comparisons
│   ├── sources/            # One summary page per ingested source
│   ├── reports/            # Agent-generated dashboards (agent creates during maintain workflow)
│   ├── index.md            # Auto-generated TOC
│   └── log.md              # Append-only chronological record
├── _meta/
│   ├── schema.md           # Wiki conventions (co-evolves with user)
│   └── taxonomy.md         # Canonical tag vocabulary
├── .wiki-meta/             # Machine state (not for humans)
│   └── manifest.json       # Delta tracking: ingested files + SHA-256 hashes
├── AGENTS.md               # Agent instructions for this vault
└── .obsidian/              # Obsidian config (don't touch)
```

### Ownership rules

- **`raw/`** — immutable. The agent reads but never modifies.
- **`wiki/`** — agent-owned. The agent creates, updates, and maintains all pages.
- **`_meta/`** — co-owned. The agent proposes changes; the user approves.
- **`.wiki-meta/`** — machine-only. Delta tracking, caches.
- Everything else in the vault is untouched.

## Page Format

See `_meta/schema.md` (initialized from `references/schema-template.md`) for full conventions.

Essential reminders:
- Filenames: `kebab-case.md`, ASCII only
- Wikilinks: `[[filename|Display Title]]` — in tables: `[[filename\|Display Title]]`
- Provenance: `%%from: raw/path%%` or `%%inferred%%`

## Workflows

### 1. Setup

Initialize the vault structure. Create dirs, then:
- Copy `references/schema-template.md` → `_meta/schema.md`
- Copy `references/taxonomy-template.md` → `_meta/taxonomy.md`
- Copy `references/agents-template.md` → `AGENTS.md`
- Customize `AGENTS.md` for the vault's domain
- Propose changes to `_meta/schema.md` and `_meta/taxonomy.md`; edit them only after user approval
- Create `wiki/index.md`, `wiki/log.md`

**Source of truth**: once copied, `_meta/` and `AGENTS.md` are the live instances.
`references/` are generic starter templates — they do not stay in sync.

### 2. Ingest

1. Run `scripts/wiki-manifest.sh "$VAULT" diff` to see pending sources
2. For each pending file:
   - Read the source, identify entities, concepts, claims, relationships
   - Create a source summary in `wiki/sources/`
   - Create or update entity/concept pages with [[wikilinks]]
   - Track provenance in frontmatter `sources:` field
3. Mark ingested: `scripts/wiki-manifest.sh "$VAULT" mark <file>`
4. Regenerate index: `scripts/wiki-index.sh "$VAULT"`
5. Append to `wiki/log.md`:
   ```
   ## [YYYY-MM-DD] ingest | <Source Title>
   - Source: raw/<path>
   - Pages created: <list>
   - Pages updated: <list>
   ```

**Source types:**
- `.md` / `.txt` — read directly with `read` tool
- `.pdf` — use `pdf` tool to extract content (copy to workspace first if the file is outside it, then clean up)
- `.epub` / `.html` — convert to text or extract content before ingesting
- URL — use `web_fetch` to save as .md in `raw/articles/`, then ingest the .md
- Images in `raw/assets/` — referenced by pages, not ingested independently (the manifest tracks only ingestable document sources)

### 3. Query

1. Read `wiki/index.md` to find relevant pages
2. Read relevant pages, synthesize an answer with [[wikilink]] citations
3. Offer to save valuable answers as new pages in `wiki/syntheses/`

### 4. Lint

Run `scripts/wiki-lint.sh "$VAULT"` for automated checks (frontmatter, broken
wikilinks, orphans, stale pages, tag drift, wikilink format, markdown structure).
Use `scripts/wiki-lint.sh "$VAULT" --fix` to auto-correct fixable issues
(requires python3; markdownlint fixes additionally require npx).
Then manually review for:

- Contradictions between pages (requires reading, not scriptable)
- Missing pages: concepts mentioned in text but lacking their own page
- Weak cross-references that should be strengthened

### 5. Maintain

Periodic (heartbeat or manual):

1. Run lint
2. Scan for unlinked mentions of entity/concept names → add [[wikilinks]]
3. If new tags emerged, propose an update to `_meta/taxonomy.md`; edit it only after user approval
4. Populate `wiki/reports/` with dashboards (open questions, contradictions, stale)
5. Review stale pages, flag for update or archival

### 6. Navigate

Use the `obsidian` skill (if available) for CLI operations (search, open, move/rename with
wikilink refactoring). For bulk reads/writes, use `read`/`write` tools directly.

## Scripts

Bundled shell scripts require Bash (BSD-compatible grep/sed/awk). `wiki-lint.sh` and `wiki-manifest.sh` require `python3`. `extract-book-digests.sh` additionally requires `pdftotext`. `wiki-manifest.sh` uses `shasum` or `sha256sum` when available and falls back to Python `hashlib` otherwise. `wiki-lint.sh` optionally uses `markdownlint-cli2` (via npx) for markdown structure checks.
Resolve `<skill-dir>` to the directory containing this SKILL.md.

### `scripts/wiki-index.sh "$VAULT"`

Regenerate `wiki/index.md` from frontmatter of all wiki pages.

### `scripts/wiki-lint.sh "$VAULT" [--fix]`

All-in-one wiki linter. Runs all checks by default. `--fix` auto-corrects fixable
issues (wikilink format, markdown structure). Internally calls `wiki-lint-links.py`
for wikilink resolution and `markdownlint-cli2` (via npx) for markdown structure.

### `scripts/wiki-manifest.sh "$VAULT" <command>`

Delta tracking via SHA-256 hashes in `.wiki-meta/manifest.json`.

```bash
wiki-manifest.sh "$VAULT" status        # raw vs ingested vs pending counts
wiki-manifest.sh "$VAULT" diff          # list files needing ingest
wiki-manifest.sh "$VAULT" mark <file>   # mark a file as ingested
```

### `scripts/extract-book-digests.sh <books-dir> <output-dir>`

Extract first 12 pages of each PDF as text via `pdftotext`. Used for cross-validating
wiki source pages against actual book content. Writes `.txt` outputs to `<output-dir>`;
prefer a directory under `$VAULT/.wiki-meta/` unless the user explicitly asks for another location.

## Tips

- **Ingest one source at a time** for best quality. Stay involved.
- **Good answers → wiki pages.** Don't let syntheses disappear into chat history.
- **Graph view** in Obsidian shows wiki shape: hubs, orphans, clusters.
- **Dataview plugin** queries frontmatter if installed.
- **Git** the vault for version history (recommended).
- **Web Clipper** browser extension gets articles into `raw/` fastest.
