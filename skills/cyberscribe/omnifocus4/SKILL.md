---
name: omnifocus4
description: "Live OmniFocus access via native Omni Automation — tasks, projects, inbox, tags. Use for ANY OmniFocus query: 'show my tasks', 'what's in my inbox', 'omnifocus summary', 'what's due today', 'flagged items', 'add a task', 'complete a task', 'search omnifocus', 'show my projects', 'GTD review'. Always run a command to get live data — never answer from memory."
---

# OmniFocus

**IMPORTANT:** OmniFocus data is live. When asked anything about tasks, projects, inbox, flagged items, due dates, or reviews — RUN A COMMAND. Do not answer from memory, do not say you cannot access OmniFocus, do not ask clarifying questions. Just run the appropriate command below and return the result.

| User asks about… | Command to run |
|------------------|----------------|
| summary / overview / stats | `scripts/of summary` |
| inbox | `scripts/of inbox` |
| today / overdue / due | `scripts/of today` |
| flagged tasks | `scripts/of flagged` |
| what to do / available tasks | `scripts/of available 10` |
| projects | `scripts/of projects` |
| search for something | `scripts/of search "query"` |

Control OmniFocus via Omni Automation JS, called from a Python wrapper.

## Requirements

- macOS with OmniFocus 3 or 4 installed
- OmniFocus must be running (or will auto-launch)
- Python 3 (system Python is fine)

## Quick Reference

```bash
scripts/of <command> [args...]
```

All commands return JSON to stdout. Errors print `{"error": "..."}` and exit 1.

## Commands

### Read

| Command | Args | Description |
|---------|------|-------------|
| `inbox` | | List inbox tasks |
| `folders` | | List all folders |
| `projects` | `[folder] [--all]` | List active projects (default); `--all` includes on-hold, dropped, completed |
| `tasks` | `<project>` | List tasks in a project |
| `tags` | `[--all]` | List tags with available tasks (default); `--all` includes empty tags |
| `today` | | Tasks due today or overdue |
| `flagged` | | Flagged incomplete tasks |
| `search` | `<query>` | Search tasks by name or note |
| `info` | `<taskId>` | Full task details by ID |
| `summary` | | Database counts (projects, tasks, flagged, due, available, inbox) |
| `project-tree` | `<name> [limit]` | Recursive subtask tree with depth |
| `project-search` | `<term> [limit]` | Find projects by partial name |
| `folder` | `<name> [limit]` | Detail a folder: child folders + projects (default limit 50 — use a higher limit for large folders) |
| `root` | `[limit]` | Top-level folders and unfiled projects |
| `tag-summary` | `<name> [limit]` | Tasks for a tag, grouped by folder/project |
| `tag-family` | `<name> [limit]` | Tasks across a tag and all its children |
| `available` | `[limit]` | All available (actionable) tasks |
| `review` | `[limit] [--all]` | Active projects with task counts (default); `--all` includes all statuses |

### Create

| Command | Args | Description |
|---------|------|-------------|
| `add` | `<name> [project]` | Add task to inbox or project |
| `newproject` | `<name> [folder]` | Create project |
| `newfolder` | `<name>` | Create top-level folder |
| `newtag` | `<name>` | Create or get tag |

### Modify

| Command | Args | Description |
|---------|------|-------------|
| `complete` | `<taskId>` | Mark complete |
| `uncomplete` | `<taskId>` | Mark incomplete |
| `delete` | `<taskId>` | Permanently delete |
| `rename` | `<taskId> <name>` | Rename task |
| `note` | `<taskId> <text>` | Append to note |
| `setnote` | `<taskId> <text>` | Replace note |
| `defer` | `<taskId> <date>` | Set defer date (YYYY-MM-DD) |
| `due` | `<taskId> <date>` | Set due date (YYYY-MM-DD) |
| `flag` | `<taskId> [true\|false]` | Set flagged (default true) |
| `tag` | `<taskId> <tag>` | Add tag (creates if needed) |
| `untag` | `<taskId> <tag>` | Remove tag |
| `move` | `<taskId> <project>` | Move to project |

### Repeat

```bash
# repeat <taskId> <method> <interval> <unit>
scripts/of repeat abc123 fixed 1 weeks
scripts/of repeat abc123 due-after-completion 2 days
scripts/of repeat abc123 defer-after-completion 1 months
scripts/of unrepeat abc123
```

Methods: `fixed`, `due-after-completion`, `defer-after-completion`
Units: `days`, `weeks`, `months`, `years`

## Output Format

All commands return JSON. Task records include:

```json
{
  "id": "abc123",
  "name": "Task name",
  "note": "Notes here",
  "flagged": false,
  "completed": false,
  "available": true,
  "deferDate": "2026-04-01",
  "dueDate": "2026-04-10",
  "effectiveDueDate": "2026-04-10",
  "completionDate": null,
  "estimatedMinutes": 30,
  "project": "Project Name",
  "folder": "Folder Name",
  "tags": ["tag1", "tag2"],
  "repeat": {"method": "fixed", "recurrence": "FREQ=WEEKLY;INTERVAL=1"}
}
```

Write commands return `{"success": true, "task": {...}}`.

## Examples

```bash
# Add task to inbox
scripts/of add "Buy groceries"

# Add task to specific project
scripts/of add "Review docs" "Work Projects"

# Get today's tasks
scripts/of today

# Search name and notes
scripts/of search "quarterly report"

# Set due date and flag
scripts/of due abc123 2026-04-10
scripts/of flag abc123 true

# Add tags
scripts/of tag abc123 "urgent"

# Create recurring task
scripts/of add "Weekly review" "Habits"
scripts/of repeat xyz789 fixed 1 weeks

# Hierarchical views
scripts/of summary
scripts/of root
scripts/of folder "Personal"
scripts/of project-tree "Work" 50
scripts/of tag-family "review"
```

## Performance

OmniJS loads all task objects on first access (~5-7 s for large databases).
Commands are grouped by expected latency:

**Fast (<1 s):** `inbox`, `folders`, `root`, `folder`, `projects`, `project-search`,
`project-tree`, `tags`, `tag-summary`, `tag-family`

**Medium (4-6 s):** `summary`, `flagged`, `today`, `search`, `available`, `review`

Prefer fast structural commands for navigation. Use medium commands only when
task-level data is actually needed — and batch related queries when possible
(e.g. ask for `flagged` once rather than `flagged` + `available` separately).

## Technical Details

Uses Omni Automation JS evaluated inside OmniFocus via AppleScript
`evaluate javascript`. This is more reliable than JXA for OmniFocus-specific
APIs — no cross-process type-conversion bugs.

Key implementation patterns:
- `filter()` not `byName()` — `byName()` returns an ObjectSpecifier proxy
  whose child collections fail to enumerate
- `asArray()` helper — `Array.isArray()` returns false for OmniJS collection types
- `safe()` wrapper — prevents crashes on null/undefined properties
- `id.primaryKey` — stable canonical ID in Omni Automation
- `effectiveDueDate` — respects project-cascaded due dates
- Dates output as ISO 8601 YYYY-MM-DD via `Date.toISOString()`
- `isAvailableApprox` — fast approximation: not completed + not deferred to future
- `listTaskRecord` / `listProjectRecord` — slim records for bulk list commands

**First run:** OmniFocus may prompt to allow automation access. Enable in
System Settings > Privacy & Security > Automation.

## Notes

- Task IDs are OmniFocus internal primary keys (returned in all task responses)
- Dates use ISO 8601: YYYY-MM-DD
- Project and tag names are case-sensitive
- Tags are created automatically when using `tag` command
- `isAvailableApprox` respects defer dates but not sequential project ordering
