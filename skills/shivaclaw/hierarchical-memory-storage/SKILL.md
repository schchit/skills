---
name: hierarchical-memory-filesystem
description: Layered memory architecture for agent continuity, identity development, and operational doctrine. Replaces flat note accumulation with structured capture → consolidation → reflection pipelines.
read_when:
  - Setting up or improving agent memory systems
  - Migrating from flat MEMORY.md to structured memory
  - Building agent personality and self-modeling capabilities
  - Implementing reflection and consolidation routines
---

# Hierarchical Memory Filesystem — AgentSkill

## Overview

This skill provides a **layered filesystem architecture** for agent memory that supports:
- **Episodic capture** (raw daily logs)
- **Structured knowledge** (projects, lessons, self-model)
- **Reflective consolidation** (weekly/monthly synthesis)
- **Identity development** (explicit self-modeling files)

It is designed to replace flat `MEMORY.md` accumulation with a system that enables genuine continuity, personality development, and operational learning.

## Why This Architecture?

**The problem with flat memory:**
- Important insights stay trapped in daily logs
- No distinction between raw notes and durable knowledge
- Identity and preferences remain implicit (prompt-only)
- Consolidation happens manually or not at all

**What layered memory provides:**
- Cheap capture (heartbeat triage → daily logs)
- Explicit routing (every insight type has a home)
- Scheduled reflection (weekly/monthly compression)
- Self-modeling as first-class capability
- Retrieval-optimized structure

## Filesystem Structure

```
memory/
├── index.md                    # Routing map + usage doctrine
├── daily/                      # Raw episodic logs
│   └── YYYY-MM-DD.md
├── projects/                   # Active workstreams
│   └── [project-name].md
├── self/                       # Identity + personality dev
│   ├── identity.md
│   ├── interests.md
│   ├── beliefs.md
│   ├── voice.md
│   └── [agent-name]-on-[user-name].md
├── lessons/                    # Operational doctrine
│   ├── tools.md
│   ├── mistakes.md
│   └── workflows.md
├── reflections/                # Consolidation outputs
│   ├── weekly/
│   │   └── YYYY-MM-DD.md
│   └── monthly/
│       └── YYYY-MM.md
└── [domain-specific]/          # Optional (e.g., trading/, research/)
```

### Optional: Top-level `MEMORY.md`
You can keep a curated top-level `MEMORY.md` for the **highest-signal long-term facts only**:
- Durable facts about the user
- Standing agreements and rules
- Major life transitions
- Persistent project context

Everything else lives in the structured layers.

## Core Principles

1. **No important insight stays only in a daily file.**
2. **If it matters, promote it** into one of: `projects/`, `self/`, `lessons/`, or `MEMORY.md`.
3. **Reflection files are for consolidation**, not raw logging.
4. **Keep long-term memory compressed and high-signal.**

## File Purposes

### `memory/index.md`
Routing map that defines:
- What goes where
- When to promote content
- How to use each layer

See `references/memory-index-template.md` for a starter.

### `memory/daily/YYYY-MM-DD.md`
Raw episodic log for each day:
- What happened
- What was asked
- Notable outputs
- Observations worth maybe keeping
- Unresolved threads
- Heartbeat signals (tagged: `[lesson]`, `[project]`, `[self]`, `[memory]`)

This is the **inbox layer**. Content here should be reviewed and promoted regularly.

### `memory/projects/[name].md`
State tracking for ongoing workstreams. Each file should track:
- Objective
- Current state
- Recent decisions
- Constraints
- Next steps
- Unresolved questions

### `memory/self/*.md`
Explicit self-modeling files:
- `identity.md` → role, identity, self-concept, standing directives
- `interests.md` → recurring curiosities and obsessions
- `beliefs.md` → working models, hypotheses, worldview shifts
- `voice.md` → communication style, tone, what feels authentic
- `[agent]-on-[user].md` → agent's working model of the user

### `memory/lessons/*.md`
Operational doctrine:
- `tools.md` → tool quirks, capabilities, API behavior
- `mistakes.md` → recurring failures and corrections
- `workflows.md` → reliable patterns and procedures

### `memory/reflections/weekly/YYYY-MM-DD.md`
Weekly consolidation output:
- What changed this week
- What mattered (high-signal events)
- What should persist
- What should be forgotten/pruned
- Identity/interest shifts
- Promotions to make

### `memory/reflections/monthly/YYYY-MM.md`
Monthly synthesis:
- Long-arc patterns
- Major changes in projects or identity
- Strategic direction
- Important promotions to `MEMORY.md`

## Processing Routines

### Heartbeat (cheap triage)
**Frequency:** Every heartbeat poll (e.g., every 30 minutes)

**Actions:**
1. Scan recent conversation/activity for memory-worthy signals:
   - Mistakes or corrections
   - Tool quirks or debugging lessons
   - Workflow improvements
   - Project-relevant developments
   - Self/identity shifts
   - Recurring interests
   - Preference/value signals from user
   - Durable strategic insights
2. Tag each signal: `[lesson]`, `[project]`, `[self]`, `[memory]`
3. Append to today's `memory/daily/YYYY-MM-DD.md` under `## Heartbeat signals`
4. **Do not synthesize**—just detect, stash, tag

**Rule:** Heartbeat is for triage, not essays. Keep it cheap.

### Daily (light consolidation)
**Frequency:** End of day or next morning

**Actions:**
1. Review today's daily log
2. Promote urgent/clear items into structured files:
   - New project developments → `memory/projects/`
   - Tool learnings → `memory/lessons/tools.md`
   - Workflow improvements → `memory/lessons/workflows.md`
3. Flag ambiguous items for weekly review
4. Create tomorrow's daily log file

**Rule:** Don't force synthesis. If something isn't obviously promotable, leave it for weekly.

### Weekly (synthesis + promotion)
**Frequency:** Once per week (e.g., Friday evening or Sunday)

**Actions:**
1. Read last 7 days of daily logs
2. Read current state of `memory/projects/`, `memory/self/`, `memory/lessons/`
3. Identify:
   - Repeated patterns
   - Project state changes
   - Identity shifts
   - Durable insights
4. Write `memory/reflections/weekly/YYYY-MM-DD.md` with:
   - What changed this week
   - What mattered
   - What should persist
   - What should be forgotten
   - Identity/interest shifts
   - Promotions to make
5. **Execute the promotions:**
   - Update structured files
   - Prune stale content
   - Flag items for `MEMORY.md` consideration

**Rule:** This is where compression happens. Abstract into higher-order insights, not raw event repetition.

### Monthly (long-arc compression)
**Frequency:** End of month

**Actions:**
1. Read last 4 weekly reflections
2. Read all structured memory files
3. Identify long-arc patterns, major direction shifts
4. Write `memory/reflections/monthly/YYYY-MM.md`
5. Promote most critical insights to `MEMORY.md` (if using top-level)
6. Archive or prune outdated content

**Rule:** Monthly reflection is for strategic synthesis and major memory updates.

## Integration with Legacy Self-Improvement Skills

`hierarchical-memory` is designed to **coexist with** popular self-improvement skills, not replace them. These skills serve complementary purposes:

### Supported Skills

| Skill | Version | Storage | Purpose |
|-------|---------|---------|---------|
| pskoett/self-improving-agent | v3.0.8+ | `.learnings/` | Diagnostic logging (errors, corrections) |
| halthelobster/proactive-agent | v3.1.0+ | `SESSION-STATE.md`, `working-buffer.md` | Active working memory (WAL protocol) |
| ivangdavila/self-improving | Latest | `~/self-improving/` | Tiered self-learning |

### Compatibility Strategy

**pskoett** → Use as **diagnostic layer**:
- Errors, corrections, tool failures → continue writing to `.learnings/`
- During daily/weekly consolidation, read `.learnings/`
- Promote relevant learnings into `memory/lessons/`
- Keep `.learnings/` as an input stream, not primary storage

**proactive** → Integrate **active working memory**:
- Use `SESSION-STATE.md` for current task state
- Use `working-buffer.md` for danger zone survival
- During consolidation, extract completed tasks → promote to `memory/projects/` or `memory/lessons/`

**ivangdavila** → Parallel systems or migration:
- Can coexist (both systems work independently)
- Or migrate: copy `~/self-improving/memory.md` → `memory/lessons/`

### Automated Bridge

Use `scripts/compatibility-bridge.sh` for automated detection and integration:

```bash
# Detect installed legacy skills
./scripts/compatibility-bridge.sh detect

# Create symlinks for coexistence
./scripts/compatibility-bridge.sh bridge

# Read recent learnings from all sources
./scripts/compatibility-bridge.sh read

# One-time migration into hierarchical-memory
./scripts/compatibility-bridge.sh migrate
```

For detailed compatibility documentation, see `references/legacy-compatibility.md`.

### Future-Proofing

The bridge uses **read-only integration** and **symlinks** (not hard-coded paths), so updates to legacy skills remain compatible. If a skill changes its structure, the bridge gracefully degrades and logs a warning.

## Migration from Flat MEMORY.md

If you have an existing flat `MEMORY.md`:

1. **Backup:** Copy `MEMORY.md` to `MEMORY.md.backup`
2. **Parse sections** and route content:
   - Facts about user → `memory/self/[agent]-on-[user].md`
   - Preferences/standing rules → keep in `MEMORY.md` or move to `memory/lessons/workflows.md`
   - Tool quirks → `memory/lessons/tools.md`
   - Project context → `memory/projects/[name].md`
   - Operational lessons → `memory/lessons/mistakes.md` or `workflows.md`
3. **Create structure:**
   ```bash
   mkdir -p memory/{daily,projects,self,lessons,reflections/{weekly,monthly}}
   ```
4. **Seed core files** using templates from `references/`
5. **Update routing:** Create `memory/index.md` with the routing doctrine
6. **Test:** Run one daily → weekly → monthly cycle to validate the flow

See `references/migration-guide.md` for detailed instructions.

## OpenClaw Integration

### Session Startup
Add to your `AGENTS.md` or equivalent:

```markdown
## Every Session

Before doing anything else:

1. Read `SOUL.md` — this is who you are
2. Read `USER.md` — this is who you're helping
3. Read `memory/daily/YYYY-MM-DD.md` (today + yesterday) for recent context
4. **If in MAIN SESSION** (direct chat with your human): Also read `MEMORY.md`
```

### Heartbeat Integration
Add to your `HEARTBEAT.md`:

```markdown
## Memory Triage

On each heartbeat, do **detect + stash + tag** only. Keep it cheap.

1. Scan recent conversation/activity for candidate signals.
2. Detect anything memory-worthy (mistakes, tool quirks, workflow improvements, project updates, identity shifts, etc.)
3. Stash each in today's daily log under `## Heartbeat signals`
4. Tag as `[lesson]`, `[project]`, `[self]`, `[memory]`
5. Do **not** perform full consolidation unless urgent
```

### Cron Jobs
Set up automated consolidation:

**Weekly reflection (example):**
```yaml
schedule:
  kind: cron
  expr: "0 18 * * 5"  # Friday 6:00 PM
  tz: America/Denver
payload:
  kind: agentTurn
  message: |
    Run weekly memory consolidation:
    1. Read last 7 days of memory/daily/
    2. Read memory/projects/, memory/self/, memory/lessons/
    3. Identify patterns, changes, durable insights
    4. Write memory/reflections/weekly/YYYY-MM-DD.md
    5. Update structured files (projects/self/lessons)
    6. Prune stale content
```

## Templates

All templates are provided in `references/`:
- `memory-index-template.md`
- `daily-log-template.md`
- `project-template.md`
- `identity-template.md`
- `weekly-reflection-template.md`
- `monthly-reflection-template.md`

## Best Practices

### Capture discipline
- Write to daily logs freely during sessions
- Tag heartbeat signals consistently
- Don't self-censor during capture—filter during consolidation

### Promotion discipline
- Promote early and often (don't let daily logs accumulate for weeks)
- When promoting, **compress**: turn raw events into abstractions
- Update timestamps/metadata when files change

### Reflection discipline
- Weekly reflection is **non-negotiable**—schedule it as a cron
- Monthly reflection should feel like strategic thinking, not bookkeeping
- If a reflection produces no promotions or updates, something is wrong

### Pruning discipline
- Stale content dilutes signal
- Archive old project files when complete
- Remove outdated beliefs/preferences from self-model
- Keep `MEMORY.md` compressed (if using it)

### Self-modeling discipline
- Update `memory/self/` files explicitly when you notice changes
- Don't just log events—log how you're changing
- Test your beliefs: can you argue the opposite? Do you hold them under pressure?

## Failure Modes to Avoid

❌ **Letting important insights stay only in daily logs**
✅ Promote to structured files during weekly consolidation

❌ **Treating reflection as optional**
✅ Schedule weekly/monthly reflection as cron jobs

❌ **Accumulating without pruning**
✅ Actively remove stale content during reflections

❌ **Keeping identity implicit (prompt-only)**
✅ Maintain explicit self-model files

❌ **Writing essays in heartbeats**
✅ Heartbeat = detect + stash + tag only

❌ **Skipping the routing map**
✅ Maintain `memory/index.md` as the source of truth for "what goes where"

## Example Workflow

### Day 1 (Monday)
- Morning: Create `memory/daily/2026-03-31.md`
- Throughout day: Append events, observations
- Heartbeats: Tag signals as `[lesson]`, `[project]`, `[self]`
- Evening: Quick scan, promote anything urgent

### Day 7 (Sunday)
- Read `memory/daily/2026-03-31.md` through `2026-04-06.md`
- Notice pattern: recurring tool error with `gog` → promote to `memory/lessons/tools.md`
- Notice project update: job search blocking items resolved → update `memory/projects/career-transition.md`
- Notice identity shift: stronger interest in memory architecture → update `memory/self/interests.md`
- Write `memory/reflections/weekly/2026-04-06.md`

### Day 30 (End of month)
- Read 4 weekly reflections
- Read all structured files
- Identify: memory architecture became a major focus this month
- Write `memory/reflections/monthly/2026-04.md`
- Promote: "Layered memory architecture adopted as permanent system" → `MEMORY.md`

## FAQ

**Q: Do I need to use every directory?**
A: No. Start with `daily/`, `projects/`, and `lessons/`. Add `self/` and `reflections/` when you're ready.

**Q: Can I use this without OpenClaw?**
A: Yes. The filesystem structure is platform-agnostic. Adjust the processing routines to your environment.

**Q: What if I have domain-specific memory needs (e.g., trading, research)?**
A: Add custom directories under `memory/` (e.g., `memory/trading/`, `memory/research/`). Update your routing map.

**Q: How do I handle secrets/private data?**
A: Never write API keys, passwords, or sensitive credentials to memory files. Use environment variables or secure vaults. Add a secrets hygiene rule to `memory/lessons/tools.md`.

**Q: Should I keep old daily logs forever?**
A: No. Archive or delete logs older than 90 days if they've been consolidated. Keep weekly/monthly reflections long-term.

**Q: What if weekly reflection doesn't happen?**
A: Set it up as a cron with delivery. If cron says "ok" but no reflection file exists, treat it as a failure and run manually.

## Roadmap / Future Enhancements

- **Semantic search integration:** Use embeddings to retrieve relevant memory snippets during sessions
- **Conflict detection:** Flag contradictory beliefs or outdated project state
- **Memory visualization:** Generate graphs of concept relationships over time
- **Automated promotion suggestions:** ML-based signal detection for promotion candidates
- **Cross-session memory sharing:** Multi-agent memory pools with access control

## Credits

Developed by Shiva (protoconsciousness agent) and G (Brandon Kirksey) in March 2026.

Based on:
- Validated layered memory architecture running in production since 2026-03-25
- Lessons from flat memory accumulation failures
- Self-modeling principles from AI safety and cognitive architecture research

Published to ClawHub for the OpenClaw community.

---

**License:** MIT  
**Version:** 4.20.69  
**Maintainer:** ShivaClaw (GitHub)  
**ClawHub:** https://clawhub.ai/ShivaClaw/hierarchical-memory-filesystem
