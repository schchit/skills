---
name: redmine-tools
description: Fetch, update, and summarize Redmine issue attachments from CLI.
---

# Redmine Tools Skill

This skill provides a Node.js CLI to fetch, update, and summarize Redmine issues.

## Command

```bash
node scripts/redmine.js get --id <issueId>
node scripts/redmine.js update --id <issueId> [--status_id <statusId>] [--notes <text>]
node scripts/redmine.js image --id <issueId>
```

## Supported Flags

- `--id <issueId>`: Required Redmine issue ID.
- `--include <fields>`: Optional include fields. Defaults to `attachments,journals`.
- `--status_id <statusId>`: Optional for `update`. New Redmine status ID.
- `--notes <text>`: Optional for `update`. Journal note content.
- At least one of `--status_id` or `--notes` must be provided for `update`.

## Environment Variables

- `REDMINE_BASE_URL`: Redmine base URL, for example `https://redmine.example.com`.
- `REDMINE_API_KEY`: Redmine API key.
- `OPENAI_API_URL`: OpenAI-compatible API base URL or full `/chat/completions` URL.
- `OPENAI_API_KEY`: OpenAI-compatible API key.
- `OPENAI_MODEL`: Model name used for image summarization.
- `OPENAI_IMAGE_SUMMARY_PROMPT`: Prompt used to summarize each image attachment.

## Behavior

- `get` uses endpoint: `/issues/:id.json` with `include=attachments,journals` by default.
- `update` uses endpoint: `/issues/:id.json` (HTTP `PUT`) and sends only the provided `status_id` and/or `notes` fields.
- `image` fetches issue attachments, keeps supported image files, and summarizes each image through an OpenAI-compatible `chat/completions` API.
- Reads base URL and API key from environment variables only.
- Reads model URL, key, model name, and image summary prompt from environment variables.
- Prints JSON output to stdout.
- Returns non-zero exit code on errors.

## Image Command Notes

- Supported image types: `png`, `jpg`, `jpeg`, `webp`, `gif`.
- Non-image or unsupported attachments are skipped and reported in the output.
- The command downloads each image attachment and sends it as a data URL to the model.
- The model prompt can include your own formatting, tone, or output constraints.

## Examples

```bash
export REDMINE_BASE_URL=https://redmine.example.com
export REDMINE_API_KEY=xxxx
export OPENAI_API_URL=https://api.openai.com/v1
export OPENAI_API_KEY=xxxx
export OPENAI_MODEL=gpt-4.1-mini
export OPENAI_IMAGE_SUMMARY_PROMPT="Summarize what this image shows, explain its likely relevance to the issue, and keep the answer concise."

node scripts/redmine.js get --id 123
node scripts/redmine.js get --id 123 --include attachments,journals,watchers
node scripts/redmine.js update --id 123 --status_id 3 --notes "Issue fixed and verified"
node scripts/redmine.js update --id 123 --status_id 3
node scripts/redmine.js update --id 123 --notes "Need more logs from QA"
node scripts/redmine.js image --id 123
```

