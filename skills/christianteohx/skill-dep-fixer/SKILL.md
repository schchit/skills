---
name: skill-dep-fixer
description: Scan installed OpenClaw skills, detect missing dependencies (npm, pip, brew, system binaries), and auto-fix what's fixable. Use when: user asks to check/fix skill dependencies, "skills are broken", "openclaw doctor shows missing requirements", or installing a new skill that won't load. Trigger phrases: "fix skill deps", "check skill dependencies", "skill-dep-fixer".
homepage: https://github.com/christianteohx/skill-dep-fixer
user-invocable: true
metadata:
  {
    "openclaw":
      {
        "emoji": "🔧",
        "requires": { "bins": ["node", "npm", "git"] },
        "install":
          [
            {
              "id": "chalk",
              "kind": "npm",
              "bins": [],
              "label": "Install chalk (for colored terminal output)",
            },
            {
              "id": "js-yaml",
              "kind": "npm",
              "bins": [],
              "label": "Install js-yaml (for YAML parsing)",
            },
          ],
      },
  }
---

# skill-dep-fixer

Scans all installed OpenClaw skills, detects missing dependencies, and optionally auto-fixes them.

## Usage

```bash
# Check all skills (dry run — safe, no changes)
skill-dep-fixer --dry-run

# Actually install missing dependencies
skill-dep-fixer --fix

# Check a specific skill only
skill-dep-fixer --skill <skill-name>

# JSON output (for automation/webhooks)
skill-dep-fixer --json

# Discord-formatted report
skill-dep-fixer --report

# Full help
skill-dep-fixer --help
```

## What it checks

| Type | Detection | Auto-fixable |
|------|-----------|--------------|
| System binary (`jq`, `curl`) | `which <bin>` | No — report only |
| Homebrew package | `brew list <pkg>` | Yes — `brew install` |
| NPM package | `npm list -g <pkg>` | Yes — `npm install -g` |
| Pip package | `pip show <pkg>` | Yes — `pip install` |

## Dependency declaration format

Skills declare dependencies in `SKILL.md` YAML frontmatter:

```yaml
metadata:
  openclaw:
    requires: { "bins": ["gh", "curl"] }
    install:
      - id: brew
        kind: brew
        formula: gh
        bins: ["gh"]
        label: "Install GitHub CLI"
```

The fixer parses this standard format from all skills in:
- `~/.openclaw/skills/*/SKILL.md`
- `~/.openclaw/workspace/skills/*/SKILL.md`

## Output example

```
Skill Dependency Report

✅ github          — all deps satisfied
✅ weather         — all deps satisfied
❌ summarize       — missing: summarize (brew) → installed ✅
⚠️  some-skill    — missing: some-binary (not auto-fixable)

Summary: 48 skills checked, 46 fixed, 1 skipped, 1 failed
```

## Exit codes

- `0` — all dependencies satisfied or all fixed
- `1` — some dependencies could not be fixed
