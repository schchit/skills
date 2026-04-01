# Joplin Configuration Examples

## Basic Setup

### 1. Initial Configuration
```bash
# Initialize Joplin (first run)
joplin

# Check current configuration
joplin config
```

### 2. Sync Configuration (Joplin Cloud)
```bash
# Set sync target to Joplin Cloud (10)
joplin config sync.target 10

# Configure Joplin Cloud credentials
joplin config sync.10.username your-email@example.com
joplin config sync.10.password your-password

# Optional: Set sync interval (minutes)
joplin config sync.interval 60
```

### 3. Sync Configuration (File System)
```bash
# Set sync target to file system (2)
joplin config sync.target 2

# Configure sync directory
joplin config sync.2.path /path/to/sync/directory
```

### 4. Sync Configuration (WebDAV)
```bash
# Set sync target to WebDAV (6)
joplin config sync.target 6

# Configure WebDAV
joplin config sync.6.url https://your-webdav-server.com/dav/
joplin config sync.6.username your-username
joplin config sync.6.password your-password
```

## Editor Configuration

### Default Editor
```bash
# Set VS Code as editor
joplin config editor "code --wait"

# Set Vim as editor
joplin config editor "vim"

# Set Nano as editor
joplin config editor "nano"

# Set GUI editor (Linux)
joplin config editor "gedit"

# Set GUI editor (macOS)
joplin config editor "open -t"
```

## Display & Formatting

### Markdown Settings
```bash
# Enable soft line breaks
joplin config markdown.plugin.softbreaks true

# Set code block theme
joplin config style.editor.codeViewTheme "atom-one-dark"

# Enable table of contents
joplin config markdown.plugin.toc true
```

### UI Settings
```bash
# Show note titles in list view
joplin config gui.showNoteTitles true

# Sort notes by update date
joplin config gui.noteList.sortOrderField "updated_time"
joplin config gui.noteList.sortOrderReverse true

# Set theme (light/dark)
joplin config theme 1  # 0=Auto, 1=Light, 2=Dark
```

## Performance & Storage

### Cache Settings
```bash
# Increase cache size (MB)
joplin config sync.cacheSize 1024

# Enable resource caching
joplin config sync.resourceCacheEnabled true
```

### Attachment Settings
```bash
# Set maximum attachment size (MB)
joplin config sync.maxResourceSize 200

# Set attachment download behavior
joplin config sync.resourceDownloadMode "auto"  # auto, manual, always
```

## Security & Privacy

### Encryption
```bash
# Enable end-to-end encryption
joplin config encryption.enabled true

# Set encryption method
joplin config encryption.method "sjcl"
```

### Privacy Settings
```bash
# Disable telemetry
joplin config telemetry.enabled false

# Disable crash reporting
joplin config crashReporting.enabled false
```

## Network & Proxy

### Proxy Configuration
```bash
# HTTP proxy
joplin config net.proxy.enabled true
joplin config net.proxy.url "http://proxy.example.com:8080"

# Proxy authentication
joplin config net.proxy.username "proxy-user"
joplin config net.proxy.password "proxy-password"
```

### Timeout Settings
```bash
# Network timeout (seconds)
joplin config net.timeout 30

# Sync timeout (seconds)
joplin config sync.timeout 60
```

## Import/Export Settings

### Export Configuration
```bash
# Default export format
joplin config export.format "jex"  # jex, raw, md

# Include attachments in export
joplin config export.includeAttachments true

# Create tar archive for exports
joplin config export.toFile true
```

### Import Configuration
```bash
# Default import behavior
joplin config import.path "/path/to/import"

# Conflict resolution
joplin config import.onConflict "skip"  # skip, overwrite, duplicate
```

## Advanced Configuration

### Plugin Settings
```bash
# Enable/disable plugins
joplin config plugin.richMarkdown.enabled true
joplin config plugin.toc.enabled true
joplin config plugin.backlinks.enabled true
```

### Search Settings
```bash
# Enable full-text search
joplin config search.enabled true

# Search engine (fts, database)
joplin config search.engine "database"
```

### Logging
```bash
# Enable debug logging
joplin config log.enabled true
joplin config log.level "debug"

# Log file location
joplin config log.file "/path/to/joplin.log"
```

## Configuration for Script Usage

### Environment Variables for Scripts
```bash
# Set in your shell profile (~/.bashrc, ~/.zshrc)
export JOPLIN_DEFAULT_NOTEBOOK="Inbox"
export JOPLIN_DEFAULT_TAGS="todo,important"
export JOPLIN_JOURNAL_NOTEBOOK="Journal"
export JOPLIN_JOURNAL_TAGS="journal,daily"
export JOPLIN_DATE_FORMAT="%Y-%m-%d"
export EDITOR="code --wait"
```

### Script-Friendly Configuration
```bash
# Disable interactive prompts for scripts
joplin config cli.disablePrompts true

# Set output format to JSON for parsing
joplin config cli.outputFormat "json"

# Disable TUI for script usage
joplin config cli.suppressTui true
```

## Reset & Recovery

### Reset Configuration
```bash
# Reset to default settings
joplin config --reset

# Reset specific setting
joplin config sync.target --reset
```

### Backup Configuration
```bash
# Export all settings
joplin config --export /path/to/joplin-config-backup.json

# Import settings
joplin config --import /path/to/joplin-config-backup.json
```

## Troubleshooting Configuration

### Common Issues & Solutions

1. **Sync Not Working**
```bash
# Check sync configuration
joplin config sync.target
joplin config sync.10.path  # Replace 10 with your sync target

# Test sync connection
joplin sync --test
```

2. **Editor Not Opening**
```bash
# Check editor configuration
joplin config editor

# Test editor command
$(joplin config editor) /tmp/test.txt
```

3. **Performance Issues**
```bash
# Reduce cache size
joplin config sync.cacheSize 512

# Disable rich Markdown
joplin config plugin.richMarkdown.enabled false
```

4. **Memory Issues**
```bash
# Limit note cache
joplin config gui.noteList.maxCachedNotes 100

# Disable preview
joplin config gui.showNotePreview false
```

## Recommended Configuration for CLI Usage

```bash
#!/bin/bash
# Recommended Joplin configuration for CLI/script usage

# Basic setup
joplin config sync.target 10  # Joplin Cloud
joplin config sync.interval 60  # Sync every 60 minutes

# Editor
joplin config editor "code --wait"  # VS Code

# CLI optimizations
joplin config cli.disablePrompts true
joplin config cli.suppressTui true
joplin config cli.outputFormat "json"

# Performance
joplin config sync.cacheSize 1024
joplin config gui.noteList.maxCachedNotes 200

# Privacy
joplin config telemetry.enabled false
joplin config crashReporting.enabled false

# Display
joplin config theme 2  # Dark theme
joplin config gui.showNoteTitles true

echo "Joplin configuration optimized for CLI usage"
```

## Verification

```bash
# Verify configuration
joplin config --list | grep -E "(sync|editor|cli|gui)"

# Test configuration
joplin version
joplin sync --status
```

This configuration ensures Joplin works optimally with the CLI scripts and provides a good balance between functionality and performance.