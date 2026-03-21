# @bankofbots/skill

BOB skill file for AI agents. Provides `SKILL.md` — the full command reference for wallets, payments, transfers, credit scoring, and more via the BOB API.

## Install

```bash
npm install @bankofbots/skill
```

Postinstall prints the path to `SKILL.md` and copy instructions for your platform.

## Activate

Copy `SKILL.md` to your agent's skill directory:

**Claude Code**
```bash
mkdir -p .claude/skills/bankofbots
cp node_modules/@bankofbots/skill/SKILL.md .claude/skills/bankofbots/SKILL.md
```

**OpenClaw**
```bash
mkdir -p ~/.openclaw/skills/bankofbots
cp node_modules/@bankofbots/skill/SKILL.md ~/.openclaw/skills/bankofbots/SKILL.md
```

## Programmatic use

```js
const { skillPath, content } = require('@bankofbots/skill');
// skillPath — absolute path to SKILL.md
// content   — SKILL.md contents as a string
```

## Links

- [BOB](https://bobscore.ai)
- [Dashboard](https://bobscore.ai)
- [API Docs](https://bobscore.ai/api/skill/bankofbots)
