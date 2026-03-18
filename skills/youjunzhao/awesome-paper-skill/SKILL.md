---
name: awesome-research-tracker
description: Research-topic literature scouting across multiple platforms (not only arXiv), paper categorization, publication-status labeling, Awesome-style GitHub README generation, repository creation (private/public), and scheduled auto-updates. Use when user asks to investigate papers for a topic, collect journal/conference/preprint works, build an awesome list repo, or set/modify daily/weekly update times.
---

# Awesome Research Tracker

Perform end-to-end literature operations for a user-provided research topic:

1. Collect papers from multiple sources (arXiv + published literature platforms).
2. Detect publication status (journal/conference) when available.
3. Classify papers by topic and publication type.
4. Generate Awesome README in the user's existing repository style.
5. Create and maintain a GitHub repository.
6. Configure and edit timed update jobs.

## Inputs to ask for first

Collect these parameters before execution:

- `topic` (required): research direction keyword(s)
- `repo_owner` (required): GitHub username/org
- `repo_name` (optional): default `awesome-<topic-slug>-papers`
- `visibility` (optional): `private` or `public` (default `private`)
- `schedule` (optional): cron expression + timezone
  - example: `0 12 * * *`, `Asia/Shanghai`
- `notify_channel` (optional): Telegram/Discord destination for update notices

## Multi-source retrieval workflow

Run `scripts/fetch_papers.py` first, then enrich links manually when needed.

```bash
python3 skills/awesome-research-tracker/scripts/fetch_papers.py \
  --topic "<topic>" \
  --max-arxiv 40 \
  --max-crossref 40 \
  --max-semantic 40 \
  --out /tmp/research_papers.json
```

### Source policy

- arXiv: latest preprints
- Crossref: journal/proceedings articles with venue metadata
- Semantic Scholar: metadata enrichment and additional publication records

If one source fails, continue with others and report partial coverage.

## Publication labeling rule (mandatory)

For any paper with a known publication venue (journal/conference/workshop), write a prefix **before arXiv badge**:

- `[<Venue>]`

If venue is unknown:

- `[Preprint]`

## Classification rule

Classify entries into both dimensions:

1. **Publication bucket**
   - Published Papers (Conference)
   - Published Papers (Journal)
   - Preprints / Unpublished

2. **Topical bucket** (examples)
   - Security & Safety
   - Agent Systems & Architecture
   - Learning, Memory & Evaluation
   - Domain Applications

Use title+abstract keywords for topical assignment. Keep one primary topical bucket per paper.

## README generation (must follow user repo style)

Before generating README, fetch the user's current README style and mirror it:

```bash
gh api repos/<owner>/<repo>/readme -H 'Accept: application/vnd.github.raw+json' > /tmp/style_readme.md
```

Then generate README using `scripts/build_awesome_readme.py`:

```bash
python3 skills/awesome-research-tracker/scripts/build_awesome_readme.py \
  --topic "<topic>" \
  --input /tmp/research_papers.json \
  --output /tmp/README.md
```

Format each entry in the user's awesome style (English-only), matching headings, bullet style, badges, and spacing:

```markdown
+ [Paper Title](primary_link)
  [Venue Name]
  [![arXiv](...)](arxiv_link)
  [![GitHub](...)](github_link_or_placeholder)
  [![Website](...)](website_link_or_placeholder) **(YYYY-MM-DD)**
```

Rules:
- Do not include author names unless user asks.
- Keep language English by default.
- Put date on the same line as `Website` (right side).

## GitHub repo workflow

Use `gh` CLI (must be authenticated):

```bash
gh auth status
```

Create/update repo:

```bash
python3 skills/awesome-research-tracker/scripts/publish_repo.py \
  --owner "<repo_owner>" \
  --name "<repo_name>" \
  --readme /tmp/README.md \
  --visibility private
```

If repo already exists, update README and push.

## Scheduled auto-update workflow

Create a cron job via OpenClaw CLI:

```bash
openclaw cron add \
  --name "daily-<topic-slug>-papers" \
  --cron "0 12 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "Check multi-platform new papers for <topic>, update repo <owner>/<repo>, keep awesome format, and notify user only when changed." \
  --announce --channel telegram --to <chat_id> --best-effort-deliver
```

### User can modify time later

Edit schedule with:

```bash
openclaw cron edit <job-id> --cron "30 9 * * *" --tz "Asia/Shanghai"
```

Disable/enable:

```bash
openclaw cron disable <job-id>
openclaw cron enable <job-id>
```

## Memory logging (mandatory)

After discussing/adding papers, append to:

- `memory/RESEARCH_LOG.md`

Use format:

```markdown
### [YYYY-MM-DD] TITLE
- **Published**: Venue or Preprint
- **Link**: Primary URL
- **Summary**: 1-2 lines
```

## Quality checklist

- Multi-source retrieval completed (not arXiv-only)
- Published venue shown before arXiv link when available
- Reasonable topical classification
- README passes Markdown rendering
- Repo visibility matches user request
- Cron schedule created or updated as requested
