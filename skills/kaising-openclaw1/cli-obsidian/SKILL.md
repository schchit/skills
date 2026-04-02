# CLI-Obsidian SKILL.md

**Version**: 1.0.0  
**Type**: CLI Tool  
**Interface**: Command Line + JSON  

---

## Description

CLI-Obsidian 是 Obsidian 笔记的命令行接口，让 AI Agent 可以直接操作你的笔记库。

支持功能：
- 笔记创建、读取、搜索
- 笔记库统计
- 导出为 Markdown/HTML/JSON

---

## Installation

```bash
cd cli-obsidian
pip install -e .
```

---

## Commands

### Note Management

```bash
# Create note
cli-obsidian note create --title "Meeting Notes" --tags "meeting,work"

# List notes
cli-obsidian note list --limit 20

# Open note
cli-obsidian note open "Meeting Notes"

# JSON output (for agents)
cli-obsidian --json note list
```

### Vault Management

```bash
# Vault info
cli-obsidian vault info

# Vault stats
cli-obsidian vault stats
```

### Search

```bash
# Search notes
cli-obsidian search "query"

# JSON output
cli-obsidian --json search "project"
```

### Export

```bash
# Export all notes
cli-obsidian export markdown --output ./export/

# Export as JSON
cli-obsidian export json --output ./json-export/
```

### REPL Mode

```bash
# Enter interactive mode
cli-obsidian

# REPL commands:
# > note create -t "Title"
# > note list
# > search "query"
# > vault info
# > help
# > quit
```

---

## JSON Schema

### Note List Response
```json
{
  "notes": [
    {
      "name": "Meeting-Notes",
      "path": "/path/to/Meeting-Notes.md",
      "modified": "2026-04-01T12:00:00"
    }
  ]
}
```

### Create Note Response
```json
{
  "action": "create",
  "path": "/path/to/Note.md",
  "title": "Note Title",
  "tags": ["tag1", "tag2"],
  "created": "2026-04-01T12:00:00"
}
```

### Search Response
```json
{
  "results": [
    {
      "name": "Note-Name",
      "path": "/path/to/Note.md",
      "match": "filename|content",
      "context": "...matching context..."
    }
  ]
}
```

---

## Agent Integration

### OpenClaw
```yaml
skill: cli-obsidian
type: cli
commands:
  - note.create
  - note.list
  - note.open
  - vault.info
  - search
  - export
```

### Usage Example
```python
# In OpenClaw skill
result = await cli_run("cli-obsidian --json note list")
notes = json.loads(result)
```

---

## Limitations

- 仅支持本地文件操作（无 Obsidian API）
- 不支持双向链接解析
- 不支持插件集成

---

## License

MIT License
