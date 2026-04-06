# Legacy Skill Compatibility

This guide explains how `hierarchical-memory` coexists with popular self-improvement skills and provides migration paths.

## Supported Skills

### 1. pskoett/self-improving-agent (v3.0.8+)
- **Storage:** `.learnings/` directory
- **Files:** `LEARNINGS.md`, `ERRORS.md`, `FEATURE_REQUESTS.md`
- **Architecture:** Append-only logs with promotion to workspace files (CLAUDE.md, AGENTS.md, etc.)

### 2. halthelobster/proactive-agent (v3.1.0+)
- **Storage:** `SESSION-STATE.md`, `memory/working-buffer.md`
- **Architecture:** WAL (Write-Ahead Logging) protocol, danger zone buffer, compaction recovery

### 3. ivangdavila/self-improving
- **Storage:** `~/self-improving/` directory
- **Files:** `memory.md` (HOT), `corrections.md`, tiered storage (HOT/WARM/COLD)
- **Architecture:** Tiered promotion/demotion with namespace isolation

## Coexistence Strategy

`hierarchical-memory` is designed to **complement**, not replace, these skills. They serve different purposes:

| Skill | Purpose | Coexistence |
|-------|---------|-------------|
| pskoett | Diagnostic logging (errors, corrections) | Use for **debugging only**; promote to `memory/lessons/` |
| proactive | Active working memory (WAL, danger zone) | Integrate `SESSION-STATE.md` and `working-buffer.md` into `memory/` |
| ivangdavila | Self-learning with tiered storage | Parallel system; optional migration to `memory/self/` |
| hierarchical-memory | Layered memory architecture for continuity | Primary memory system; reads from legacy skills |

## Compatibility Bridge

The `scripts/compatibility-bridge.sh` script provides automated detection and integration:

### Detect Installed Skills
```bash
./scripts/compatibility-bridge.sh detect
```

Output:
```
🔍 Detecting installed self-improvement skills...
Found: pskoett proactive
```

### Bridge (Symlink for Coexistence)
```bash
./scripts/compatibility-bridge.sh bridge
```

Creates symlinks:
- `.learnings/` → `memory/lessons/.learnings/`
- `SESSION-STATE.md` → `memory/SESSION-STATE.md`
- `~/self-improving/` → `memory/.self-improving/`

### Read Legacy Learnings
```bash
./scripts/compatibility-bridge.sh read
```

Displays recent entries from all detected legacy skills.

### Migrate (One-Time Copy)
```bash
./scripts/compatibility-bridge.sh migrate
```

Copies legacy learnings into `hierarchical-memory` structure:
- `.learnings/LEARNINGS.md` → `memory/lessons/pskoett-learnings.md`
- `.learnings/ERRORS.md` → `memory/lessons/pskoett-errors.md`
- `SESSION-STATE.md` → `memory/session-state-proactive.md`
- `~/self-improving/memory.md` → `memory/lessons/ivangdavila-memory.md`
- `~/self-improving/corrections.md` → `memory/lessons/ivangdavila-corrections.md`

## Integration Patterns

### Pattern 1: Diagnostic Layer (pskoett)
**Use pskoett for**: Errors, tool failures, immediate corrections
**Promote to hierarchical-memory**: During weekly consolidation

```markdown
## Weekly Consolidation (SKILL.md example)
1. Read `.learnings/LEARNINGS.md` (last 7 days)
2. Identify durable lessons (not one-off fixes)
3. Promote to `memory/lessons/tools.md` or `memory/lessons/workflows.md`
4. Mark original entry as `promoted` in `.learnings/`
```

### Pattern 2: Active Memory (proactive)
**Use proactive for**: Current task state, WAL protocol, danger zone survival
**Integrate with hierarchical-memory**: Read `SESSION-STATE.md` and `working-buffer.md` during daily/weekly consolidation

```markdown
## Daily Consolidation
1. Read `SESSION-STATE.md` (active task state)
2. Extract completed tasks or resolved issues
3. Promote important outcomes to `memory/projects/` or `memory/lessons/`
4. Clear stale entries from `SESSION-STATE.md`
```

### Pattern 3: Parallel Systems (ivangdavila)
**Use ivangdavila for**: Its own tiered storage and promotion logic
**Use hierarchical-memory for**: Structured projects/self/lessons/reflections

**No conflict**: Both can coexist. If you prefer one unified system, run `migrate` and then disable ivangdavila.

## Migration Decision Tree

```
Do you have legacy self-improvement skills installed?
│
├─ No → Install hierarchical-memory, you're done
│
└─ Yes → Answer these questions:
    │
    ├─ Do you want to keep using the legacy skill?
    │   ├─ Yes → Run `bridge` for coexistence
    │   └─ No → Run `migrate` to copy data, then uninstall legacy
    │
    └─ Do you want unified memory or parallel systems?
        ├─ Unified → Run `migrate`, consolidate into hierarchical-memory
        └─ Parallel → Run `bridge`, use both (read from both during consolidation)
```

## Version Compatibility

| Legacy Skill | Tested Version | Status | Notes |
|--------------|----------------|--------|-------|
| pskoett/self-improving-agent | v3.0.8 | ✅ Compatible | Stable `.learnings/` API |
| halthelobster/proactive-agent | v3.1.0 | ✅ Compatible | SESSION-STATE.md, working-buffer.md unchanged |
| ivangdavila/self-improving | Latest | ✅ Compatible | `~/self-improving/` structure stable |

### Future-Proofing Strategy

To ensure compatibility with future versions:

1. **Read-only integration**: The bridge **reads** from legacy skills but does not modify their files.
2. **Symlinks, not copies**: Bridges use symlinks so updates to legacy skills are automatically visible.
3. **Optional migration**: Migration is a **one-time copy**, so future changes to legacy skills don't affect hierarchical-memory.
4. **Graceful degradation**: If a legacy skill changes its structure, the bridge detects the old location and logs a warning instead of failing.

## Upgrade Procedures

### When pskoett updates to v4.x
If `.learnings/` directory structure changes:
1. Run `./scripts/compatibility-bridge.sh detect` to verify detection still works
2. Update symlink paths in `compatibility-bridge.sh` if needed
3. Test read/migration with new structure

### When proactive updates SESSION-STATE format
If WAL protocol changes:
1. Review new `SESSION-STATE.md` format
2. Update consolidation logic in `SKILL.md` to parse new format
3. Regenerate bridge if file locations change

### When ivangdavila changes tiering rules
If HOT/WARM/COLD promotion logic changes:
1. Re-run `migrate` to capture updated `memory.md`
2. Update routing map in `memory/index.md` if needed

## Rollback Procedures

### Undo Bridge
```bash
rm memory/lessons/.learnings
rm memory/SESSION-STATE.md
rm memory/.self-improving
```

### Undo Migration
```bash
rm memory/lessons/pskoett-*.md
rm memory/session-state-proactive.md
rm memory/lessons/ivangdavila-*.md
```

Legacy skills remain untouched.

## Best Practices

### 1. Keep pskoett for Diagnostics
- Don't disable pskoett — it's excellent for automatic error capture
- Use it as an **input stream** for hierarchical-memory
- Promote lessons during weekly consolidation

### 2. Adopt proactive's WAL Protocol
- Even if not using proactive skill, the WAL pattern is valuable
- Integrate `SESSION-STATE.md` into your daily routine
- Use `working-buffer.md` for danger zone survival

### 3. Consolidate Before Migrating
- If using ivangdavila, run its compaction logic first
- Then migrate HOT tier into hierarchical-memory
- Archive COLD tier separately if needed

### 4. Test Before Full Migration
- Run `bridge` first to test coexistence
- Use both systems in parallel for 1-2 weeks
- Only then run `migrate` if you're confident

## FAQ

**Q: Will hierarchical-memory break if pskoett updates to v4.0?**
A: No. The bridge reads `.learnings/` directory by path, not by version-specific logic. If pskoett changes file names, update `compatibility-bridge.sh`.

**Q: Can I use all three legacy skills with hierarchical-memory?**
A: Yes. Run `bridge` to symlink all three. During consolidation, read from all sources.

**Q: What if I want to uninstall a legacy skill after migration?**
A: Safe. Migration copies data, so the original can be deleted. Verify migration with `ls memory/lessons/` first.

**Q: Does hierarchical-memory replace proactive's WAL protocol?**
A: No. Hierarchical-memory is about **layered memory structure**. Proactive's WAL is about **write-ahead capture**. Use both: WAL writes to `SESSION-STATE.md`, hierarchical-memory consolidates it into structured layers.

**Q: Can I run the bridge script inside a cron?**
A: Yes. Add to your weekly consolidation cron:
```bash
./scripts/compatibility-bridge.sh read >> memory/daily/$(date +%Y-%m-%d).md
```

## Maintenance

### Weekly Check
```bash
# Detect if new skills were installed
./scripts/compatibility-bridge.sh detect

# Re-bridge if needed
./scripts/compatibility-bridge.sh bridge
```

### Monthly Audit
```bash
# Compare lesson counts
wc -l .learnings/LEARNINGS.md memory/lessons/pskoett-learnings.md

# Check for divergence
diff -u .learnings/LEARNINGS.md memory/lessons/pskoett-learnings.md | head -n 50
```

## Reporting Issues

If a legacy skill update breaks compatibility:

1. Run `./scripts/compatibility-bridge.sh detect` and save output
2. Check for error messages
3. Open an issue at: https://github.com/ShivaClaw/hierarchical-memory/issues
4. Include:
   - Legacy skill name + version
   - Output of `detect` command
   - Error message or unexpected behavior

---

**Version:** 1.0.0  
**Last Updated:** 2026-03-27  
**Maintainer:** ShivaClaw
