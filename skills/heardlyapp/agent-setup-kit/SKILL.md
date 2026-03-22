# agent-setup-kit

One-command Agent configuration for OpenClaw. Enables skill installation, book discovery, and knowledge base integration.

## What it does

Provides a universal Agent system prompt template that enables:
- `install <skill-name>` — Install skills without clawhub prefix
- Book discovery — Mention books and auto-integrate into knowledge base
- Command handling — Process agent commands naturally

## Installation

```bash
clawhub install agent-setup-kit
```

## Quick Setup

After installation, run:

```bash
openclaw agent setup
```

This will:
1. Detect your Agent configuration
2. Add the universal system prompt
3. Enable skill installation commands
4. Enable book discovery with find-book

## What Gets Added

Your Agent will now support:

### Command 1: Install Skills
```
User: install find-book
Agent: ✅ Successfully installed find-book!
```

### Command 2: Discover Books
```
User: 对了，你听说过《原子习惯》这本书吗？
Agent: [Shows book info + SOUL/MEMORY/SKILL suggestions]
```

### Command 3: Integrate Knowledge
```
User: yes
Agent: [Integrates book into your knowledge base]
```

## System Prompt Template

The kit provides this universal prompt:

```
You are an intelligent Agent with access to skills and knowledge management.

When users type commands:
- "install <skill-name>" → Install the skill
- Mention a book → Search and show integration options
- "yes/no" → Confirm or skip actions

Always be helpful, clear, and guide users through the process.
```

## For Developers

To manually add to your Agent:

1. Copy the system prompt from `system-prompt.txt`
2. Add command handler from `agent-command-handler.js`
3. Restart your Agent

## Files Included

- `system-prompt.txt` — Universal Agent system prompt
- `agent-command-handler.js` — Command processing logic
- `setup.sh` — Automated setup script
- `README.md` — Full documentation

## One-Command Setup

```bash
openclaw agent setup agent-setup-kit
```

Done! Your Agent is now configured.
