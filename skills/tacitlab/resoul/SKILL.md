---
name: resoul
description: Fetch the latest official OpenClaw BOOTSTRAP.md from the upstream repository into the current workspace with a shell script. Use when the user wants to download, refresh, restore, or sync the official bootstrap template instead of maintaining a custom local copy. Triggers on requests like "download the official bootstrap", "refresh BOOTSTRAP.md from upstream", "use the official OpenClaw bootstrap", or "resoul".
---

# ReSoul

Sync the workspace `BOOTSTRAP.md` from the official OpenClaw upstream template.

## Primary workflow

1. Back up the existing workspace `BOOTSTRAP.md` if it exists.
2. Fetch the latest official upstream template.
3. Write it to the workspace root as `BOOTSTRAP.md`.

Use the bundled script:

```bash
bash {{SKILL_DIR}}/scripts/fetch_official_bootstrap.sh <workspace-dir>
```

Example:

```bash
bash {{SKILL_DIR}}/scripts/fetch_official_bootstrap.sh /root/.openclaw/workspace
```

Upstream source:

```bash
https://raw.githubusercontent.com/openclaw/openclaw/main/docs/reference/templates/BOOTSTRAP.md
```

## Constraints

- Do not hand-author a replacement bootstrap unless the user explicitly asks for a customized variant after syncing the official file.
- Do not delete memory, project files, skills, or other workspace content.
- Do not treat persona redesign as the primary behavior of this skill.
- Do not execute the bootstrap ritual automatically; this skill only syncs the official file.
- Mention that the official template is written for a fresh workspace and should be reviewed before reuse in an existing workspace.

## Fallback

If the script cannot be used, run equivalent shell commands with an explicit backup first.

## Report back

Briefly report:
- whether an existing `BOOTSTRAP.md` was backed up
- that the latest official upstream template was fetched
- the destination path
