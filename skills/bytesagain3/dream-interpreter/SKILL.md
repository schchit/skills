---
version: "3.0.0"
name: Dream Interpreter
description: "Interpret dream symbols and maintain a journal with psychology insights. Use when analyzing dreams, journaling patterns, exploring meanings."
author: BytesAgain
homepage: https://bytesagain.com
source: https://github.com/bytesagain/ai-skills
---
# Dream Interpreter

Multi-purpose utility tool for running tasks, managing configuration, tracking entries, searching data, and exporting results. A lightweight CLI for organizing and retrieving structured data from the command line.

## Commands

| Command | Description |
|---------|-------------|
| `dream-interpreter run <args>` | Execute the main function and log the action |
| `dream-interpreter config <args>` | Show or update configuration (data dir path) |
| `dream-interpreter status <args>` | Display current status ("ready") |
| `dream-interpreter init <args>` | Initialize the data directory |
| `dream-interpreter list <args>` | List all entries in the data log |
| `dream-interpreter add <entry>` | Add a new timestamped entry to the data log |
| `dream-interpreter remove <entry>` | Remove an entry from the log |
| `dream-interpreter search <term>` | Search the data log for a term (case-insensitive) |
| `dream-interpreter export <args>` | Export the full data log to stdout |
| `dream-interpreter info <args>` | Show version and data directory path |
| `dream-interpreter help` | Show all available commands |
| `dream-interpreter version` | Show current version |

## Data Storage

All data is stored in `~/.local/share/dream-interpreter/` (override with `$DREAM_INTERPRETER_DIR` or `$XDG_DATA_HOME`):

- **Data log** — `data.log` (main entry store, one line per entry with date prefix)
- **Activity history** — `history.log` (unified timeline of all command invocations)
- **Config** — `config.json` (referenced by the `config` command)

Data format for `data.log`: each entry is stored as `YYYY-MM-DD <value>`, space-delimited. History entries use `MM-DD HH:MM <command>: <value>`.

## Requirements

- Bash 4+ with `set -euo pipefail`
- Standard POSIX utilities (`date`, `grep`, `cat`, `echo`)
- No external dependencies or API keys required

## When to Use

1. **Quick data journaling** — add timestamped entries from the command line without opening an editor or app
2. **Searching past entries** — find specific notes or records with case-insensitive search across the full log
3. **Lightweight task tracking** — use `add` and `list` as a minimal to-do or event log
4. **Data export for analysis** — dump the full log to stdout and pipe to other tools (grep, awk, jq)
5. **Bootstrapping a new environment** — run `init` to set up the data directory, then `config` to verify paths

## Examples

```bash
# Initialize the data directory
dream-interpreter init

# Add a new entry
dream-interpreter add "Completed server migration to new host"

# Add another entry
dream-interpreter add "Updated SSL certificates for api.example.com"

# List all entries
dream-interpreter list

# Search for entries containing "server"
dream-interpreter search server

# Check current status
dream-interpreter status

# Show version and data path
dream-interpreter info

# Export all data to a file
dream-interpreter export > backup.txt

# Show configuration
dream-interpreter config

# Run the main function
dream-interpreter run "daily-check"
```

## Output

All command output goes to stdout. Redirect to a file if needed:

```bash
dream-interpreter list > entries.txt
dream-interpreter export > full-backup.txt
```

The `search` command uses case-insensitive matching and prints matching lines or "Not found" if no results.

---

*Powered by BytesAgain | bytesagain.com | hello@bytesagain.com*
