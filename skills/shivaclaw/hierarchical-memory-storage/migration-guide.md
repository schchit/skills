# Migration Guide: Flat MEMORY.md → Hierarchical Memory

This guide walks you through migrating from a flat `MEMORY.md` file to the hierarchical memory architecture.

## Prerequisites

- Existing `MEMORY.md` file with accumulated notes
- Basic understanding of the hierarchical memory structure (read `SKILL.md` first)

## Step 1: Backup

**Always backup before migration.**

```bash
cp MEMORY.md MEMORY.md.backup
cp MEMORY.md MEMORY.md.$(date +%Y%m%d)
```

## Step 2: Create Directory Structure

```bash
mkdir -p memory/{daily,projects,self,lessons,reflections/{weekly,monthly}}
```

## Step 3: Seed Core Files

Create initial files from templates:

```bash
# Copy templates (adjust paths as needed)
cp references/memory-index-template.md memory/index.md
cp references/identity-template.md memory/self/identity.md
```

Create initial empty files:

```bash
touch memory/self/interests.md
touch memory/self/beliefs.md
touch memory/self/voice.md
touch memory/lessons/tools.md
touch memory/lessons/mistakes.md
touch memory/lessons/workflows.md
```

## Step 4: Parse and Route Content

Read through your existing `MEMORY.md` and manually route content into the new structure. Use these guidelines:

### Facts about the user → `memory/self/[agent]-on-[user].md`
Examples:
- Name, contact info, timezone
- Background, education, career
- Thinking style, values
- Current situation

### Preferences and standing rules → Keep in `MEMORY.md` or `memory/lessons/workflows.md`
Examples:
- "Always ask before sending email"
- "Prefer direct communication, no filler"
- "Challenge weak reasoning"

### Tool quirks and API behavior → `memory/lessons/tools.md`
Examples:
- "gog requires explicit keyring password"
- "weather skill produces bad data, use curl instead"
- "Brave API key must be lowercase"

### Project context → `memory/projects/[name].md`
Examples:
- Job search status and blocking items
- OpenClaw reliability work
- Trading system development

For each project, create a file using `references/project-template.md` as a guide.

### Operational lessons → `memory/lessons/mistakes.md` or `workflows.md`
Examples:
- Recurring failure patterns
- Reliable debugging procedures
- Consolidation routines

### Identity/personality → `memory/self/identity.md`, `beliefs.md`, `voice.md`
Examples:
- Who you are, your role, your nature
- Your working models of the world
- Your communication style

## Step 5: Update Routing Map

Edit `memory/index.md` to reflect your specific setup:
- Add any custom directories (e.g., `memory/trading/`)
- Document your routing conventions
- Add any special rules or exceptions

## Step 6: Clean Up Top-Level MEMORY.md

After routing content, decide what to keep in the top-level `MEMORY.md`:

**Keep (high-signal only):**
- Critical user facts
- Standing agreements
- Security/privacy rules
- Most important ongoing context

**Remove (now in structured files):**
- Detailed project state → moved to `memory/projects/`
- Tool quirks → moved to `memory/lessons/tools.md`
- Identity details → moved to `memory/self/`

Your `MEMORY.md` should be much shorter after migration—ideally under 200 lines.

## Step 7: Create Initial Daily Log

```bash
touch memory/daily/$(date +%Y-%m-%d).md
```

Populate it with today's activities using `references/daily-log-template.md` as a guide.

## Step 8: Test the Flow

Run through one consolidation cycle to validate the structure:

1. **Add heartbeat signals** to today's daily log (tag as `[lesson]`, `[project]`, `[self]`)
2. **Wait for weekly reflection** (or run manually):
   - Read last 7 days of `memory/daily/`
   - Review `memory/projects/`, `memory/self/`, `memory/lessons/`
   - Write `memory/reflections/weekly/YYYY-MM-DD.md`
   - Execute promotions
3. **Check that structured files were updated**

If files were updated correctly, the migration succeeded.

## Step 9: Update Session Startup

Modify your `AGENTS.md` or equivalent to load the new structure:

```markdown
## Every Session

Before doing anything else:

1. Read `SOUL.md` — this is who you are
2. Read `USER.md` — this is who you're helping
3. Read `memory/daily/YYYY-MM-DD.md` (today + yesterday)
4. **If in MAIN SESSION**: Also read `MEMORY.md`
```

## Step 10: Set Up Consolidation Cron

Configure weekly and monthly reflection cron jobs (see `SKILL.md` for examples).

## Common Migration Challenges

### Challenge: "My MEMORY.md has no clear structure"
**Solution:** Read it in multiple passes:
1. First pass: identify user facts → route to `memory/self/[agent]-on-[user].md`
2. Second pass: identify project state → route to `memory/projects/`
3. Third pass: identify tool/workflow lessons → route to `memory/lessons/`
4. Final pass: keep only highest-signal content in top-level `MEMORY.md`

### Challenge: "Some content doesn't fit the categories"
**Solution:** Either:
- Create a custom directory under `memory/` (e.g., `memory/research/`)
- Add to `MEMORY.md` if truly top-level
- Put in `memory/daily/` and let weekly consolidation decide

### Challenge: "My flat memory has old/stale content"
**Solution:** Use migration as an opportunity to prune. If something hasn't been relevant in 3+ months, consider dropping it.

### Challenge: "I want to preserve full history"
**Solution:** Keep `MEMORY.md.backup` indefinitely. The new structure is for active working memory, not archival.

## Rollback Procedure

If migration fails:

```bash
# Restore backup
cp MEMORY.md.backup MEMORY.md

# Remove new structure if desired
rm -rf memory/
```

## Validation Checklist

After migration, verify:

- [ ] `memory/index.md` exists and documents routing
- [ ] `memory/self/identity.md` contains agent identity
- [ ] `memory/self/[agent]-on-[user].md` contains user model
- [ ] `memory/projects/` has one file per active project
- [ ] `memory/lessons/` has tools, mistakes, workflows files
- [ ] Top-level `MEMORY.md` is compressed (or removed if not using)
- [ ] `MEMORY.md.backup` is saved
- [ ] Session startup reads correct files
- [ ] Consolidation cron is scheduled

## Post-Migration

After successful migration:

1. Run for at least 2 weeks before deleting `MEMORY.md.backup`
2. Monitor weekly reflections to ensure routing is working
3. Adjust `memory/index.md` as needed based on actual usage patterns
4. Consider archiving old daily logs after 90 days

---

**Questions?** See `SKILL.md` FAQ section or open an issue on the ClawHub repository.
