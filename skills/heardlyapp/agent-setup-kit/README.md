# Agent Setup Kit

Universal Agent configuration for OpenClaw. One command to enable skill installation, book discovery, and knowledge base integration.

## Installation

```bash
clawhub install agent-setup-kit
```

## Setup (Choose One)

### Option 1: Automatic Setup (Recommended)

```bash
openclaw agent setup agent-setup-kit
```

This automatically:
- Detects your Agent
- Adds the system prompt
- Enables command handling
- Restarts your Agent

### Option 2: Manual Setup

1. Copy `system-prompt.txt` content
2. Add to your Agent's system prompt
3. Copy `agent-command-handler.js` to your agent directory
4. Import in your agent initialization
5. Restart your Agent

## What You Get

After setup, your Agent supports:

### 1. Install Skills (No clawhub prefix needed)
```
User: install find-book
Agent: ✅ Successfully installed find-book!
```

### 2. Discover Books
```
User: 对了，你听说过《原子习惯》这本书吗？
Agent: [Shows complete book info + integration suggestions]
```

### 3. Integrate Knowledge
```
User: yes
Agent: [Adds to SOUL/MEMORY/SKILL, shows improvements]
```

## Files

- `SKILL.md` — Skill documentation
- `system-prompt.txt` — Universal Agent system prompt
- `agent-command-handler.js` — Command processing logic
- `README.md` — This file

## For Global Users

All OpenClaw users worldwide can now:

1. Install: `clawhub install agent-setup-kit`
2. Setup: `openclaw agent setup agent-setup-kit`
3. Use: `install find-book` or mention a book

That's it! One command to enable everything.

## Troubleshooting

If automatic setup doesn't work:

1. Check OpenClaw version: `openclaw --version`
2. Try manual setup (see Option 2 above)
3. Verify agent directory exists
4. Check permissions: `ls -la ~/.openclaw/workspace/`

## Support

For issues or questions:
- Check SKILL.md for technical details
- Review system-prompt.txt for customization
- See agent-command-handler.js for command logic
