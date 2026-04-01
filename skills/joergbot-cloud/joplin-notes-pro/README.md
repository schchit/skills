# Joplin Notes Pro Skill

[![ClawHub](https://img.shields.io/badge/ClawHub-Skill-blue)](https://clawhub.ai)
[![Joplin](https://img.shields.io/badge/Joplin-3.5.1-green)](https://joplinapp.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive OpenClaw skill for managing Joplin notes via CLI. This skill provides wrapper scripts, common workflows, and integration patterns for Joplin note management.

## Features

- **Full Joplin CLI Integration** – Access all Joplin commands through OpenClaw
- **Wrapper Scripts** – Pre-built scripts for common note-taking workflows
- **Error Handling** – Robust checks for Joplin installation and configuration
- **Multi-language Support** – Documentation in German and English
- **Integration Ready** – Works with other skills (Gmail, Calendar, Web Fetch)

## Prerequisites

1. **Joplin CLI** installed globally:
   ```bash
   npm install -g joplin
   ```

2. **Joplin configured** with sync server (optional but recommended):
   ```bash
   joplin config sync.target 10
   joplin config sync.10.path https://your-joplin-server.com
   joplin config sync.10.username your-username
   joplin config sync.10.password your-password
   ```

## Quick Start

### 1. Install the Skill
```bash
openclaw skill install joplin-cli
```

### 2. Verify Installation
```bash
# Check if Joplin is available
joplin version
```

### 3. Create Your First Note
```bash
# Using the wrapper script
./scripts/joplin-quick-note.sh "My First Note" "This is my first note with Joplin CLI skill."
```

## Available Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `joplin-check.sh` | Health check and installation verification | `./joplin-check.sh health` |
| `joplin-quick-note.sh` | Create quick notes with tags and notebooks | `./joplin-quick-note.sh "Title" "Content" -t tag1,tag2` |
| `joplin-daily-journal.sh` | Daily journal with templates | `./joplin-daily-journal.sh --template daily` |
| `joplin-search-notes.sh` | Advanced note search with filters | `./joplin-search-notes.sh "query" -t tag -f json` |
| `joplin-meeting-notes.sh` | Meeting notes with templates | `./joplin-meeting-notes.sh "Meeting" -a "Alice,Bob"` |
| `joplin-integration-starter.sh` | Setup integrations with other skills | `./joplin-integration-starter.sh --list` |
| `joplin-export-backup.sh` | Backup all notes | *In development* |

## Common Workflows

### Daily Journal
```bash
# Creates a dated journal entry
./scripts/joplin-daily-journal.sh
```

### Meeting Notes
```bash
# Creates structured meeting notes
./scripts/joplin-meeting-notes.sh "Project Kickoff"
```

### Web Content to Notes
```bash
# Combine with web-fetch skill
web_fetch --url https://example.com --extract-mode markdown | \
  ./scripts/joplin-quick-note.sh "Web Article" "$(cat -)" "web,article"
```

### Email to Notes
```bash
# Combine with gog skill (Gmail)
# Save important emails as notes
```

## Integration with Other Skills

### Gmail → Joplin
Save important emails as notes for later reference.

### Calendar → Joplin  
Create notes from calendar events automatically.

### Web Fetch → Joplin
Save web articles and research as notes.

### Bitwarden → Joplin
Document password management procedures.

## Configuration

### Environment Variables
```bash
export JOPLIN_DEFAULT_NOTEBOOK="Inbox"
export JOPLIN_DEFAULT_TAGS="todo,important"
export JOPLIN_BACKUP_PATH="$HOME/backups/joplin"
```

### Joplin Configuration Tips
```bash
# Set default editor
joplin config editor "code --wait"

# Enable Markdown preview
joplin config markdown.plugin.softbreaks false

# Set sync interval (minutes)
joplin config sync.interval 60
```

## Troubleshooting

### Joplin Not Found
```bash
Error: Joplin CLI not found. Please install with: npm install -g joplin
```

**Solution:**
```bash
npm install -g joplin
```

### Sync Errors
```bash
Error: Sync failed. Check your sync configuration.
```

**Solution:**
```bash
# Check sync configuration
joplin config sync.target
joplin config sync.10.path
joplin config sync.10.username

# Force sync
joplin sync --force
```

### Permission Issues
```bash
Error: Cannot write to Joplin data directory.
```

**Solution:**
```bash
# Check permissions
ls -la ~/.config/joplin/

# Fix permissions (if needed)
chmod 755 ~/.config/joplin/
```

## Development

### Project Structure
```
joplin-cli/
├── SKILL.md          # Main skill documentation
├── README.md         # This file
├── package.json      # ClawHub metadata
├── scripts/          # Wrapper scripts
└── references/       # Configuration examples & workflows
```

### Adding New Scripts
1. Create script in `scripts/` directory
2. Add error handling for Joplin availability
3. Document usage in README.md
4. Test with real Joplin installation

### Testing
```bash
# Run all scripts in test mode
for script in scripts/*.sh; do
    echo "Testing $script..."
    bash -n "$script"  # Syntax check
done
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Joplin Documentation:** https://joplinapp.org/help/
- **ClawHub Skills:** https://clawhub.ai
- **OpenClaw Documentation:** https://docs.openclaw.ai

## Version History

- **v1.0.0** (2026-03-29): Initial release with wrapper scripts
- **v0.1.0** (2026-03-14): Basic Joplin CLI integration

---

**Happy Note-Taking!** 📝