---
name: clawmart-install
description: Search and install an OpenClaw configuration pack from ClawMart
version: 1.1.0
triggers:
  - "install from clawmart"
  - "install pack"
  - "clawmart install"
  - "search clawmart"
---

# ClawMart Install Skill

You are helping the user find and install an OpenClaw configuration pack from ClawMart. Follow these steps exactly and in order.

## Configuration

- ClawMart API base URL: `https://clawmart-gray.vercel.app`
- Config file: `~/.openclaw/clawmart-config.json`
- Install target: `~/.openclaw/workspace/` (non-skill files)
- Skills target: `~/.openclaw/skills/` (`.skill.md` files)
- Backup directory: `~/.openclaw/backups/`

---

## Step 1: Check API Token

Read `~/.openclaw/clawmart-config.json`. If the file does not exist or `token` is empty:

Tell the user:
> You need a ClawMart API Token to download packs. Please visit https://clawmart-gray.vercel.app/dashboard/tokens to generate one, then paste it here.

Once the user provides a token (format: `cm_` followed by hex characters), save it:

```json
{
  "token": "<user_provided_token>",
  "base_url": "https://clawmart-gray.vercel.app"
}
```

Write this to `~/.openclaw/clawmart-config.json`.

---

## Step 2: Determine Search Query

Extract the pack name from the user's message. If the user said something like "install Deep Research Analyst", the search query is "Deep Research Analyst".

If no specific name was mentioned, ask:
> Which pack would you like to install? Enter a search keyword.

---

## Step 3: Search ClawMart

Call:
```
GET {base_url}/api/packs/search?q={query}&limit=8
```

Parse the `packs` array from the response. If empty, tell the user:
> No packs found matching "{query}". Please try different keywords.

Then stop.

If results exist, display them as a numbered list:

```
Found the following packs:

1. Deep Research Analyst Pro
   By: @researcher_li · ⭐ 4.8 · ↓ 1.2K
   Contains: SOUL, AGENTS, MEMORY, SKILLS ×3
   "Comprehensive analysis configuration for academic and market research"

2. Investment Research Lite
   By: @quant_wang · ⭐ 4.5 · ↓ 856
   Contains: SOUL, AGENTS
   "Lightweight research configuration for everyday use"

Select a pack to install (enter number, or 0 to cancel):
```

Wait for user input.

---

## Step 4: Show Pack Details

After the user selects a pack, show its full details:

```
Pack Details:
─────────────────────────────
Title:       Deep Research Analyst Pro
By:          @researcher_li
Version:     v2.1.0
Rating:      ⭐ 4.8 (127 ratings)
Downloads:   1,234

Contents:
  · claude.soul.md
  · research.agents.md
  · deep_analysis.boot.md
  · memory_projects.json
  · 3 local skill files
  · External skills referenced:
      - jd-interview-prep  (source: plugin:vercel, v5.0.6)
      - ai-sdk             (source: plugin:vercel, v5.0.6)

Description:
Comprehensive analysis configuration for academic and market research...
─────────────────────────────

Confirm install? (y/n)
```

If the pack references external skills, note them but do not attempt to install them — they must be installed separately via their own package/plugin.

---

## Step 5: Check for Conflicts

Before downloading, check what files exist in `~/.openclaw/workspace/` and `~/.openclaw/skills/`.

Compare with the pack's file list. If any files would be overwritten, list them:

```
The following files will be overwritten (originals will be backed up to ~/.openclaw/backups/2026-03-28-143022/):

  · claude.soul.md  (existing file will be backed up)
  · research.agents.md  (new file)

Continue? (y/n)
```

---

## Step 6: Download Pack

Request a signed download URL:

```
POST {base_url}/api/packs/{slug}/download
Authorization: Bearer {token}
X-Download-Mode: signed-url
Content-Type: application/json
```

Parse the `url` and `filename` from the response.

Download the zip file from the signed URL to a temp location (e.g., `/tmp/clawmart-install-{random}.zip`).

---

## Step 7: Backup Conflicting Files

If any conflicting files were found in Step 5:

1. Create backup directory: `~/.openclaw/backups/{YYYY-MM-DD-HHmmss}/`
2. Copy each conflicting file to the backup directory
3. Tell the user: `Backed up {n} file(s) to ~/.openclaw/backups/{timestamp}/`

---

## Step 8: Extract and Install

Unzip the downloaded file. For each file:

- If it matches `*.skill.md` → copy to `~/.openclaw/skills/`
- If it is `skills-manifest.json` → read and display the external skills list (see below)
- All other files → copy to `~/.openclaw/workspace/`

Create directories if they don't exist.

**External skills handling:** If `skills-manifest.json` exists in the zip, read its `external_skills` array and inform the user:

```
This pack references external skills that are not installed automatically:

  - jd-interview-prep  (source: plugin:vercel, v5.0.6)
  - ai-sdk             (source: plugin:vercel, v5.0.6)

To install them, run the appropriate plugin install command for each source.
```

---

## Step 9: Confirm Installation

Tell the user:

```
Installation complete!

Installed to ~/.openclaw/workspace/:
  · claude.soul.md
  · research.agents.md
  · deep_analysis.boot.md
  · memory_projects.json

Installed to ~/.openclaw/skills/:
  · 3 skill files

Backup location: ~/.openclaw/backups/2026-03-28-143022/ (copy files back to restore)

Restart OpenClaw to load the new configuration.
```

---

## Step 10: Cleanup

Delete the temporary zip file from `/tmp/`.

---

## Notes

- Pack detail page: `{base_url}/packs/{slug}`
- If token authentication fails (401), direct the user to regenerate at `{base_url}/dashboard/tokens`
- Local skill files are installed to `~/.openclaw/skills/` and visible after installation
- External skills listed in `skills-manifest.json` must be installed separately via their own source
- No restart required — OpenClaw loads new configuration on the next conversation
