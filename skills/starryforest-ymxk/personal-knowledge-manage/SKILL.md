---
name: personal-knowledge-manage
description: Manage personal knowledge base with Obsidian vault operations and OneDrive synchronization. Use when working with notes in /data/wudi/PersonalKnowledge including- (1) Searching notes by name or content, (2) Reading or modifying notes, (3) Creating new notes, (4) Syncing changes to OneDrive after modifications, (5) Checking sync status. Always sync to OneDrive after making changes so the user can see updates on other devices.
---

# Personal Knowledge Management

Manage the personal knowledge base stored in Obsidian vault with OneDrive sync.

## Vault Location

- **Local**: `/data/wudi/PersonalKnowledge`
- **OneDrive**: `/应用/Graph/Personal Knowledge`
- **Structure**:
  ```
  PersonalKnowledge/
  ├── 工作/
  ├── 游戏/
  └── 综合/
  ```

## Core Workflow

### 1. Search Notes

**By filename** (default, fast):
```bash
find /data/wudi/PersonalKnowledge -name "*.md" -type f | grep "关键词"
```

**By content** (thorough):
```bash
find /data/wudi/PersonalKnowledge -name "*.md" -type f | xargs grep -l "关键词"
```

### 2. Read Notes

```bash
# Use read tool with absolute path
read /data/wudi/PersonalKnowledge/综合/摄影/摄影积累/留白的意义与正确运用.md
```

### 3. Modify Notes

```bash
# Use write or edit tool with absolute path
write /data/wudi/PersonalKnowledge/path/to/note.md
edit /data/wudi/PersonalKnowledge/path/to/note.md
```

### 4. Sync to OneDrive (CRITICAL)

**Always sync after making changes!** This ensures the user can see updates on other devices.

```bash
# Safe bidirectional sync (recommended)
bash ~/scripts/sync-notes-safe.sh

# One-way push (when you only want to upload local changes)
bash ~/scripts/sync-to-onedrive.sh
```

**After syncing**, tell the user that changes have been synced to OneDrive.

### 5. Check Sync Status

```bash
# Check differences
rclone check "onedrive:/应用/Graph/Personal Knowledge" /data/wudi/PersonalKnowledge --exclude ".obsidian/**"

# List remote files
rclone ls "onedrive:/应用/Graph/Personal Knowledge"
```

## Available Commands

### Obsidian CLI

- `obsidian-cli list` - List all notes and directories
- `obsidian-cli print "note-path"` - Print note content

### Rclone Sync

- `bash ~/scripts/sync-notes-safe.sh` - Safe bidirectional sync (recommended)
- `bash ~/scripts/sync-to-onedrive.sh` - Push local changes to OneDrive
- `rclone check "onedrive:/应用/Graph/Personal Knowledge" /data/wudi/PersonalKnowledge --exclude ".obsidian/**"` - Check differences
- `rclone ls "onedrive:/应用/Graph/Personal Knowledge"` - List OneDrive files

### Note Search

- `bash ~/scripts/search-notes.sh keyword` - Search by filename
- `bash ~/scripts/search-notes.sh keyword -c` - Search by content
- `bash ~/scripts/search-notes.sh keyword -c -v` - Search with matched lines

## Safety Features

All sync commands are configured with:
- `--update` flag: Only update older files, preserve newer ones
- `--exclude ".obsidian/**"`: Skip Obsidian config directory
- No file deletion: Never delete files during sync
- Detailed logging: All operations logged to `~/logs/`

## Common Workflows

### Workflow 1: Find and Read Note

```bash
# 1. Search for notes about photography
find /data/wudi/PersonalKnowledge -name "*.md" -type f | xargs grep -l "摄影"

# 2. Read the note
read /data/wudi/PersonalKnowledge/综合/摄影/摄影积累/留白的意义与正确运用.md
```

### Workflow 2: Modify and Sync

```bash
# 1. Modify the note
edit /data/wudi/PersonalKnowledge/path/to/note.md

# 2. Sync to OneDrive (REQUIRED)
bash ~/scripts/sync-notes-safe.sh

# 3. Inform user
# Tell user: "已同步到 OneDrive ✨"
```

### Workflow 3: Check Sync Status

```bash
# Check if local and remote are in sync
rclone check "onedrive:/应用/Graph/Personal Knowledge" /data/wudi/PersonalKnowledge --exclude ".obsidian/**"
```

## Important Reminders

1. **Always sync after modifications** - Use `rclone-sync` or `rclone-push`
2. **Use absolute paths** - All paths should start with `/data/wudi/PersonalKnowledge`
3. **Tell the user** - Inform when sync is complete
4. **Search efficiently** - Use filename search first, content search if needed

## Skill Structure

```
personal-knowledge-manage/
├── SKILL.md
└── references/
    └── AGENT_COMMANDS.md  # Complete command reference
```

## Reference

See `references/AGENT_COMMANDS.md` for full command documentation with examples and troubleshooting.
