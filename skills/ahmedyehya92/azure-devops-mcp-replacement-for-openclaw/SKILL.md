---
name: azure-devops-mcp-replacement-for-openclaw
version: 1.0.0
description: Interact with Azure DevOps — list and manage projects, repos, work items, pipelines, builds, wikis, test plans, and teams. Use this skill whenever the user mentions Azure DevOps, ADO, work items, sprints, boards, iterations, pull requests, pipelines, builds, or wikis in an Azure DevOps context.
homepage: https://github.com/microsoft/azure-devops-mcp
metadata:
  clawdbot:
    emoji: "🔷"
    requires:
      env: ["AZURE_DEVOPS_ORG", "AZURE_DEVOPS_PAT"]
    primaryEnv: "AZURE_DEVOPS_PAT"
    files: ["scripts/*"]
---

# Azure DevOps Skill

Connects OpenClaw to Azure DevOps via the REST API. All calls use a Personal Access Token (PAT) and run locally through Node.js scripts — no MCP required.

## Setup

### 1. Create a Personal Access Token (PAT)

1. Go to `https://dev.azure.com/<your-org>/_usersSettings/tokens`
2. Click **New Token**
3. Grant scopes: **Work Items** (Read & Write), **Code** (Read), **Build** (Read), **Release** (Read), **Test Management** (Read), **Wiki** (Read & Write), **Project and Team** (Read)
4. Copy the token — it won't be shown again

### 2. Set Environment Variables

```bash
export AZURE_DEVOPS_ORG=contoso          # your org name only, no URL
export AZURE_DEVOPS_PAT=your_token_here
```

Or add them to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "azure-devops": {
        "enabled": true,
        "env": {
          "AZURE_DEVOPS_ORG": "contoso",
          "AZURE_DEVOPS_PAT": "your_token_here"
        }
      }
    }
  }
}
```

### 3. Install Script Dependencies

```bash
cd {baseDir}
npm install
```

---

## Available Scripts

All scripts are in `{baseDir}/scripts/`. Run them via OpenClaw's exec tool. Arguments are always positional and listed per script.

### Projects & Teams

```bash
node {baseDir}/scripts/projects.js list
node {baseDir}/scripts/projects.js get <project>
node {baseDir}/scripts/teams.js list <project>
node {baseDir}/scripts/teams.js iterations <project> <team>
```

### Work Items

```bash
node {baseDir}/scripts/workitems.js list <project>
node {baseDir}/scripts/workitems.js get <id>
node {baseDir}/scripts/workitems.js current-sprint <project> <team>
node {baseDir}/scripts/workitems.js create <project> <type> <title>
node {baseDir}/scripts/workitems.js update <id> <field> <value>
node {baseDir}/scripts/workitems.js query <project> "<WIQL query>"
```

### Repositories & Pull Requests

```bash
node {baseDir}/scripts/repos.js list <project>
node {baseDir}/scripts/repos.js get <project> <repo>
node {baseDir}/scripts/repos.js prs <project> <repo> [status]
node {baseDir}/scripts/repos.js pr-detail <project> <repo> <pr-id>
```

### Pipelines & Builds

```bash
node {baseDir}/scripts/pipelines.js list <project>
node {baseDir}/scripts/pipelines.js runs <project> <pipeline-id> [limit]
node {baseDir}/scripts/builds.js list <project> [limit]
node {baseDir}/scripts/builds.js get <project> <build-id>
```

### Wikis

```bash
node {baseDir}/scripts/wiki.js list <project>
node {baseDir}/scripts/wiki.js get-page <project> <wiki-id> <page-path>
node {baseDir}/scripts/wiki.js create-page <project> <wiki-id> <page-path> "<content>"
node {baseDir}/scripts/wiki.js update-page <project> <wiki-id> <page-path> "<content>"
```

### Test Plans

```bash
node {baseDir}/scripts/testplans.js list <project>
node {baseDir}/scripts/testplans.js suites <project> <plan-id>
```

---

## Usage Instructions

When the user asks about Azure DevOps:

1. **Confirm credentials** — if `AZURE_DEVOPS_ORG` or `AZURE_DEVOPS_PAT` are not set, ask for them before proceeding.
2. **Pick the right script** — use the script that matches what the user needs (see list above).
3. **Run via exec** — use OpenClaw's exec tool to run the Node.js script in `{baseDir}/scripts/`.
4. **Present output** — scripts return JSON; parse and summarize clearly. For lists, show the key fields (id, title/name, state). For details, show all relevant fields.
5. **For mutations** (create, update) — always confirm with the user before running, unless explicitly told not to.

---

## External Endpoints

| Endpoint | Purpose | Data Sent |
|---|---|---|
| `https://dev.azure.com/{org}/` | All project/work/repo/pipeline/wiki APIs | PAT auth header, query params, JSON body |
| `https://vsrm.dev.azure.com/{org}/` | Release management (builds) | PAT auth header |
| `https://vssps.visualstudio.com/{org}/` | Profile/identity APIs | PAT auth header |

## Security & Privacy

- Your PAT and org name never leave your machine except as HTTP headers to Microsoft's Azure DevOps endpoints.
- Scripts use `set -euo pipefail` where applicable; Node scripts validate all inputs before interpolation.
- No data is sent to any third party.

**Trust statement:** This skill sends authenticated requests to `dev.azure.com` using your PAT. Only install if you trust Microsoft's Azure DevOps service with your work data.
