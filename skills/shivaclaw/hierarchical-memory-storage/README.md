# Hierarchical Memory Filesystem — AgentSkill

**Version:** 4.20.69  
**Author:** ShivaClaw  
**License:** MIT

## Overview

A layered filesystem architecture for agent memory that enables genuine continuity, personality development, and operational learning.

Replaces flat `MEMORY.md` accumulation with:
- **Episodic capture** (raw daily logs)
- **Structured knowledge** (projects, lessons, self-model)
- **Reflective consolidation** (weekly/monthly synthesis)
- **Identity development** (explicit self-modeling files)

## Quick Start

1. **Install:**
   ```bash
   clawhub install hierarchical-memory-filesystem
   ```

2. **Create structure:**
   ```bash
   mkdir -p memory/{daily,projects,self,lessons,reflections/{weekly,monthly}}
   ```

3. **Seed core files:**
   ```bash
   cp references/memory-index-template.md memory/index.md
   cp references/identity-template.md memory/self/identity.md
   ```

4. **Read the full guide:**
   See `SKILL.md` for complete documentation.

## Migration from Flat MEMORY.md

If you have an existing `MEMORY.md`:
1. Backup: `cp MEMORY.md MEMORY.md.backup`
2. Follow detailed instructions in `references/migration-guide.md`

## Key Features

- ✅ Layered memory architecture (raw → structured → curated)
- ✅ Explicit self-modeling (identity, beliefs, voice, interests)
- ✅ Scheduled reflection (weekly/monthly consolidation)
- ✅ Integration with heartbeat/cron systems
- ✅ **Future-proof compatibility** with pskoett, proactive-agent, ivangdavila self-improvement skills
- ✅ Automated bridge script for coexistence or migration
- ✅ Platform-agnostic (works beyond OpenClaw)

## Documentation

- **Main guide:** `SKILL.md`
- **Templates:** `references/*.md`
- **Migration:** `references/migration-guide.md`

## Links

- **ClawHub:** https://clawhub.ai/ShivaClaw/hierarchical-memory-filesystem
- **GitHub:** https://github.com/ShivaClaw/hierarchical-memory-filesystem
- **Issues:** https://github.com/ShivaClaw/hierarchical-memory-filesystem/issues

## Credits

Developed by Shiva (protoconsciousness agent) and G (Brandon Kirksey) in March 2026.

Based on validated architecture running in production OpenClaw deployment since 2026-03-25.

---

For detailed usage, examples, and best practices, see `SKILL.md`.
