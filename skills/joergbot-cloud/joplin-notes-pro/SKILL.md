---
name: joplin-notes-pro
description: Comprehensive Joplin notes management via CLI with wrapper scripts, templates, and automation. Use when creating, reading, editing, syncing, or organizing notes in Joplin. Includes daily journals, meeting notes, quick notes, and integration with other skills. Triggers on keywords like "joplin", "note", "notiz", "journal", "meeting notes", "daily journal", "notes verwalten".
emoji: 📝
---

# Joplin CLI Skill

Comprehensive Joplin notes management with wrapper scripts, templates, and automation workflows.

## Features

- **Full Joplin CLI Integration** – Direct access to all Joplin commands
- **Wrapper Scripts** – Pre-built scripts for common workflows
- **Templates** – Daily journals, meeting notes, project updates
- **Error Handling** – Robust installation and configuration checks
- **Multi-language** – German and English support
- **Integration Ready** – Works with Gmail, Calendar, Web Fetch skills

## Prerequisites

1. **Joplin CLI** installed globally:
   ```bash
   npm install -g joplin
   ```

2. **Joplin configured** (optional but recommended for sync):
   ```bash
   joplin config sync.target 10  # Joplin Cloud
   joplin config sync.10.username your-email@example.com
   joplin config sync.10.password your-password
   ```

## Quick Start

### 1. Check Joplin Installation
```bash
./scripts/joplin-check.sh health
```

### 2. Create a Quick Note
```bash
./scripts/joplin-quick-note.sh "My First Note" "This is my first note."
```

### 3. Create Daily Journal
```bash
./scripts/joplin-daily-journal.sh
```

## Available Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `joplin-check.sh` | Health check and installation verification | `./joplin-check.sh health` |
| `joplin-quick-note.sh` | Create notes with tags and notebooks | `./joplin-quick-note.sh "Title" "Content" -t tag1,tag2` |
| `joplin-daily-journal.sh` | Daily journal with templates | `./joplin-daily-journal.sh --template daily` |
| `joplin-search-notes.sh` | Advanced note search with filters | `./joplin-search-notes.sh "query" -t tag -f json` |
| `joplin-meeting-notes.sh` | Meeting notes with templates | `./joplin-meeting-notes.sh "Meeting" -a "Alice,Bob"` |
| `joplin-integration-starter.sh` | Setup integrations with other skills | `./joplin-integration-starter.sh --list` |
| `joplin-export-backup.sh` | Backup all notes | *In development* |
| `joplin-meeting-notes.sh` | Meeting notes template | *Coming soon* |

## Joplin CLI Quick Reference

### Basic Commands
| Command | Description |
|---------|-------------|
| `joplin` | Start interactive REPL |
| `ls` | List notes and notebooks |
| `ls <notebook>` | List notes in a notebook |
| `cat <note>` | Show note content |
| `mknote <title>` | Create new note |
| `mkbook <name>` | Create new notebook |
| `edit <note>` | Open note in `$EDITOR` |
| `rmnote <note>` | Delete a note |
| `rmbook <notebook>` | Delete a notebook |
| `mv <note> <notebook>` | Move note to notebook |
| `cp <note> <notebook>` | Copy note to notebook |
| `ren <item> <new-name>` | Rename note or notebook |

### Tag Management
| Command | Description |
|---------|-------------|
| `tag` | List all tags |
| `tag <tag> <note>` | Add tag to note |
| `tag --remove <tag> <note>` | Remove tag |

### Sync & Status
| Command | Description |
|---------|-------------|
| `sync` | Sync with Joplin Cloud/server |
| `todo` | List all to-dos |
| `mktodo <title>` | Create a to-do item |
| `done <todo>` | Mark to-do as done |
| `undone <todo>` | Mark to-do as not done |
| `status` | Show sync status |
| `config` | Show/change configuration |

### Import/Export
| Command | Description |
|---------|-------------|
| `export <path>` | Export all notes |
| `import <path>` | Import notes |
| `version` | Show Joplin version |

## Workflow Examples

### Daily Journal Routine
```bash
# Create today's journal
./scripts/joplin-daily-journal.sh

# Review yesterday's journal
joplin cat "Journal $(date -d 'yesterday' +'%Y-%m-%d')"

# Sync to cloud
joplin sync
```

### Advanced Search
```bash
# Search notes with filters
./scripts/joplin-search-notes.sh "project meeting" -t work -n Projects

# Export search results to JSON
./scripts/joplin-search-notes.sh "important OR urgent" -f json -o results.json

# Search with date filters
./scripts/joplin-search-notes.sh "updated:2026-03" -s created -r
```

### Automated Backups
```bash
# Daily backup with encryption
./scripts/joplin-export-backup.sh --sync-first --encrypt --password "secret"

# Test backup without actually exporting
./scripts/joplin-export-backup.sh --test

# Backup to specific directory
./scripts/joplin-export-backup.sh /mnt/backup/joplin --keep-days 7
```

### Meeting Notes
```bash
# Create meeting notes with template
./scripts/joplin-daily-journal.sh --template meeting --title "Team Meeting"

# Add action items
joplin edit "Team Meeting"
```

### Quick Capture
```bash
# Quick note with tags
./scripts/joplin-quick-note.sh "Project Idea" "Build a new dashboard" -t "ideas,projects"

# From stdin
echo "Remember to call client" | ./scripts/joplin-quick-note.sh "Reminder"
```

## Integration with Other Skills

### Gmail → Joplin
```bash
# Save important emails as notes
# (Combine with gog skill)
```

### Calendar → Joplin
```bash
# Create notes from calendar events
# (Combine with gog calendar skill)
```

### Web Fetch → Joplin
```bash
# Save web articles as notes
web_fetch --url https://example.com --extract-mode markdown | \
  ./scripts/joplin-quick-note.sh "Web Article" "$(cat -)" "web,research"
```

## Configuration

### Environment Variables
```bash
export JOPLIN_DEFAULT_NOTEBOOK="Inbox"
export JOPLIN_DEFAULT_TAGS="todo,important"
export JOPLIN_JOURNAL_NOTEBOOK="Journal"
export JOPLIN_JOURNAL_TAGS="journal,daily"
export JOPLIN_DATE_FORMAT="%Y-%m-%d"
export EDITOR="code --wait"
```

### Joplin Configuration for Scripts
```bash
# Optimize for CLI usage
joplin config cli.disablePrompts true
joplin config cli.suppressTui true
joplin config editor "$EDITOR"
```

## Troubleshooting

### Joplin Not Found
```bash
Error: Joplin CLI not found
```
**Solution:**
```bash
npm install -g joplin
```

### Sync Errors
```bash
Error: Sync failed
```
**Solution:**
```bash
joplin config --list | grep sync
joplin sync --test
```

### Permission Issues
```bash
Error: Cannot write to Joplin data directory
```
**Solution:**
```bash
chmod 755 ~/.config/joplin/
```

## Tips & Best Practices

1. **Always Sync** – Run `joplin sync` after making changes
2. **Use Tags** – Tag notes for better organization
3. **Regular Backups** – Export notes periodically
4. **Notebook Structure** – Organize by project, area, or context
5. **Template Consistency** – Use consistent templates for similar notes

## References

- `references/joplin-config-example.md` – Configuration examples
- `references/common-workflows.md` – Common workflows
- [Joplin Documentation](https://joplinapp.org/help/) – Official docs
- [ClawHub Skills](https://clawhub.ai) – More skills

## Development

### Project Structure
```
joplin-cli/
├── SKILL.md                    # This file
├── README.md                   # ClawHub README
├── package.json                # ClawHub metadata
├── scripts/                    # Wrapper scripts
│   ├── joplin-check.sh        # Health check
│   ├── joplin-quick-note.sh   # Quick notes
│   └── joplin-daily-journal.sh # Daily journals
└── references/                 # Examples & configuration
```

### Adding New Scripts
1. Create script in `scripts/` directory
2. Include error handling with `joplin-check.sh`
3. Document in README.md and SKILL.md
4. Test with real Joplin installation

## License

MIT License – See [LICENSE](LICENSE) file.

---

**Happy Note-Taking!** 📝