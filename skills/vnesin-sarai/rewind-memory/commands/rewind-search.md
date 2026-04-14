# /rewind-search

Search your Rewind memory for relevant context from previous sessions.

## Usage

```
/rewind-search <query>
```

## Instructions

When the user runs `/rewind-search`, execute:

```bash
rewind search "$ARGUMENTS" --limit 10
```

Display the results in a readable format, showing:
- The matched text (truncated to ~200 chars)
- The source (file, session, tool output)
- The relevance score

If no results found, suggest the user run `/rewind-index` to index their workspace.
