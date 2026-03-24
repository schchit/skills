<div align="center">
  <h1>Claude Remote Control</h1>
  <p><strong>Headless Claude Code sessions in tmux with remote control URLs, idle timeout, and push notifications.</strong></p>
  <p>An <a href="https://github.com/nicepkg/openclaw">OpenClaw</a> skill.</p>
  <p>
    <a href="#install"><strong>Install</strong></a>
    ·
    <a href="#usage"><strong>Usage</strong></a>
    ·
    <a href="#notifications"><strong>Notifications</strong></a>
  </p>
</div>

---

## Install

```bash
clawhub install claude-remote-control
```

Or clone manually:

```bash
git clone https://github.com/oobagi/awesome-remote-control.git ~/.openclaw/skills/claude-remote-control
```

Requires `tmux` and `python3`. Notifications require [`openclaw`](https://github.com/nicepkg/openclaw).

Start a new session and the skill is available automatically.

## Usage

Ask your agent:

> "Start a remote session for my-project"

> "Spin up 3 Claude sessions with Discord notifications to my-channel"

> "List my remote sessions"

Each session gets a unique name like `🦊 Fox | my-project`, a remote control URL, and auto-exits after 30 minutes idle.

```bash
# Attach to a running session
tmux attach -t cc-fox-my-project

# Kill it
tmux kill-session -t cc-fox-my-project

# Resume a dead session by UUID
claude -r "<uuid>" --dangerously-skip-permissions --remote-control
```

## Notifications

Get pinged when a session finishes its task or shuts down. Works with any [openclaw-supported channel](https://docs.openclaw.ai/cli) — Discord, Telegram, Slack, etc.

> "Start a remote session for my-project and notify me on Discord in my-channel"

Uses Claude Code's native hook system. No polling, no cron jobs.

## How It Works

Sessions launch with `--dangerously-skip-permissions --remote-control` and `CLAUDE_CODE_EXIT_AFTER_STOP_DELAY` for automatic idle timeout. Workspace trust is pre-seeded so headless starts never block on prompts. A JSON registry tracks active/dead sessions with UUIDs for resumption.

## License

MIT
