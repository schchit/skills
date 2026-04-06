# WebPrinter Skill

`webprinter` is a Codex/Skills-compatible skill for the WebPrinter cloud printing service (`webprinter.cn`).

Required environment variable: `WEBPRINTER_ACCESS_TOKEN`
Required runtime: `Python 3.10+`
Required setup: `pip install -r requirements.txt`

It helps an AI agent:

- query available printers
- upload local documents
- create roaming print tasks
- print directly to a selected device
- update duplex settings
- update color settings
- update copy-count settings

## Repository Structure

This repository follows the common Skills layout used by tools such as `skills` and listing sites like `skills.sh`:

```text
webprinter/
- SKILL.md
- _meta.json
- agents/
  - openai.yaml
- scripts/
  - mcp_client.py
- requirements.txt
```

## Install

Before using this skill, install the required runtime and Python package:

```bash
python --version
pip install -r requirements.txt
```

If this repository is published to GitHub, users can typically install it with:

```bash
npx skills add https://github.com/<owner>/<repo> --skill webprinter
```

Some environments also support the owner/repo shorthand:

```bash
npx skills add <owner>/<repo>
```

Sites such as `skills.sh` primarily surface skills after users install them through the `skills` CLI, so publishing the repository is necessary but not always sufficient for immediate discovery.

## Requirements

- Python 3.10+
- A valid `WEBPRINTER_ACCESS_TOKEN` bearer token
- Python dependencies installed via `pip install -r requirements.txt`
- Access to the official WebPrinter service at `https://any.webprinter.cn`

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Authentication

Obtain a token from the official WebPrinter OAuth page:

```text
https://any.webprinter.cn/get-ai-server-token
```

Then set:

```bash
WEBPRINTER_ACCESS_TOKEN=...
```

## Quick Commands

Check install status:

```bash
python scripts/mcp_client.py check-install-progress
```

Query printers:

```bash
python scripts/mcp_client.py query-printers
```

Upload a local file:

```bash
python scripts/mcp_client.py upload-file --file-path "C:/path/to/document.pdf"
```

Create a roaming task:

```bash
python scripts/mcp_client.py create-roaming-task --file-name "document.pdf" --url "https://any.webprinter.cn/files/abc123/document.pdf" --media-format PDF
```

Update duplex mode:

```bash
python scripts/mcp_client.py update-printer-side --task-id "TASK_20240324_001" --side DUPLEX
```

Update color mode:

```bash
python scripts/mcp_client.py update-printer-color --task-id "TASK_20240324_001" --color COLOR
```

Update copies:

```bash
python scripts/mcp_client.py update-printer-copies --task-id "TASK_20240324_001" --copies 2
```

Direct print to a named device:

```bash
python scripts/mcp_client.py print-document --file-name "report.pdf" --url "https://any.webprinter.cn/files/abc123/report.pdf" --media-format PDF --device-name "HP LaserJet Pro" --control-sn "SERVER123456"
```

## Notes For Discovery

To maximize the chance of being indexed cleanly:

- keep `SKILL.md` at the repository root or in a clearly installable skill path
- keep frontmatter `name` and `description` accurate
- keep `agents/openai.yaml` aligned with the skill behavior
- keep the repository public
- provide a working installation example in this README
