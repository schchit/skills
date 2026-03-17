---
name: clawclau
description: 'ClawClau v1.1.0 — The ONLY authorized way to dispatch Claude Code tasks. Spawns Claude Code in isolated tmux sessions with automatic background monitoring and completion notification. NOT for: interactive Claude Code sessions or environments without tmux/claude/jq.'
metadata:
  {
    "openclaw":
      {
        "emoji": "🦞",
        "requires": { "bins": ["tmux", "jq", "claude"] },
        "install":
          [
            { "id": "tmux", "kind": "brew", "package": "tmux" },
            { "id": "jq", "kind": "brew", "package": "jq" },
            {
              "id": "claude",
              "kind": "npm",
              "package": "@anthropic-ai/claude-code",
              "bins": ["claude"],
            },
          ],
      },
  }
---

# ClawClau v1.1.0 — Claude Code 唯一调度方式

小八调度 Claude Code 的唯一合法方式。通过 tmux 隔离会话派发任务，自动启动后台 monitor，任务完成后自动通知。

## When to Use

**所有** Claude Code 任务都必须通过 ClawClau 派发（`exec` 调用 `claude-spawn.sh`）。

**绝对禁止**：
- ❌ `exec` 直接调用 `claude -p`（会超时挂死）
- ❌ `sessions_spawn` + `runtime: "acp"`（ACP 已弃用）

Do NOT use for:
- Tasks requiring real-time streaming output
- Environments without tmux, jq, or Claude Code

## First-Time Setup

```bash
# Set up the working directory
export CLAWCLAU_HOME="$HOME/.clawclau"
mkdir -p "$CLAWCLAU_HOME/logs"
echo '[]' > "$CLAWCLAU_HOME/active-tasks.json"
```

Add to shell profile for persistence:
```bash
echo 'export CLAWCLAU_HOME="$HOME/.clawclau"' >> ~/.zshrc
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CLAWCLAU_HOME` | `~/.clawclau` | Base directory for registry and logs |
| `CLAWCLAU_SHELL` | `bash` | Shell for launching Claude Code in tmux |

## Scripts

All scripts are in `scripts/` relative to this skill directory. Set `CLAWCLAU_HOME` before calling.

### Spawn a task

```bash
CLAWCLAU_HOME="$HOME/.clawclau" ./scripts/claude-spawn.sh <task-id> "<prompt>" [workdir] [timeout-seconds]
```

- `<task-id>`: alphanumeric + dash/underscore only
- `<prompt>`: the task for Claude Code
- `[workdir]`: defaults to current directory
- `[timeout-seconds]`: defaults to 600 (10 min)

Example:
```bash
CLAWCLAU_HOME="$HOME/.clawclau" ./scripts/claude-spawn.sh "refactor-auth" \
  "Refactor src/auth.ts to use JWT tokens instead of sessions" \
  "$HOME/my-project" 300
```

### Check task status

```bash
CLAWCLAU_HOME="$HOME/.clawclau" ./scripts/claude-check.sh [task-id]
```

Without argument: lists all tasks. With argument: shows details + last output.

### Get results

```bash
CLAWCLAU_HOME="$HOME/.clawclau" ./scripts/claude-result.sh <task-id>
```

### Monitor (auto-detect completion)

```bash
CLAWCLAU_HOME="$HOME/.clawclau" ./scripts/claude-monitor.sh
```

Set up cron for automatic monitoring:
```bash
# crontab -e
*/2 * * * * CLAWCLAU_HOME="$HOME/.clawclau" /path/to/skills/clawclau/scripts/claude-monitor.sh
```

### Kill a task

```bash
CLAWCLAU_HOME="$HOME/.clawclau" ./scripts/claude-kill.sh <task-id>
```

### Steer a running task

```bash
CLAWCLAU_HOME="$HOME/.clawclau" ./scripts/claude-steer.sh <task-id> "<message>"
```

Note: steering only works with interactive Claude Code sessions, not `claude -p`.

## Task Lifecycle

```
running → done     (tmux ended, log has content)
running → failed   (tmux ended, log empty)
running → timeout  (exceeded timeout)
running → killed   (manually terminated)
```

## v1.1.0 Key Features

- **spawn 自动启动后台 monitor**：无需手动 cron，`claude-spawn.sh` 完成后自动在后台运行 `claude-monitor.sh`
- **完成自动通知**：monitor 检测到任务结束后自动执行 `openclaw system event --mode now`
- **数据目录**：`~/.clawclau/`（active-tasks.json + logs/ + prompts/）

## Security

`claude-spawn.sh` uses `--dangerously-skip-permissions`. Only use in trusted environments.
