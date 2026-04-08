---
name: service-persistence
description: >
  macOS service persistence and reboot recovery. Manages a three-tier architecture
  (LaunchAgent / tmux bootstrap / wrapper daemon) to ensure all services auto-recover
  after reboot. Use when: (1) adding a persistent service, (2) upgrading a tmux session
  to LaunchAgent, (3) creating a wrapper daemon for interactive programs,
  (4) checking or fixing post-reboot service state, (5) updating the service registry,
  (6) generating or updating bootstrap/restore scripts,
  (7) diagnosing why a service didn't auto-start after reboot.
---

# Service Persistence — macOS 服務持久化

## Problem

macOS clears `/tmp` on reboot → tmux sockets disappear → all tmux sessions die.
Services that only run in tmux vanish silently. This skill solves that with a three-tier architecture.

## File Structure

```
service-persistence/
├── SKILL.md                              ← This file (methodology + workflows)
├── references/
│   ├── registry-spec.md                  ← service-registry.json format spec
│   ├── launchagent-template.md           ← plist templates (3 types)
│   ├── bootstrap-template.md             ← tmux bootstrap script template
│   ├── wrapper-template.md               ← wrapper daemon script template
│   └── example-registry.json             ← Example config (fill in your own services)
```

After setup, your machine will also have:
- `~/.openclaw/workspace/service-registry.json` — your machine's service list
- `~/.openclaw/scripts/bootstrap-services.sh` — generated bootstrap script
- `~/.openclaw/scripts/restore-*.sh` — generated wrapper scripts
- `~/Library/LaunchAgents/` — generated plist files
- `~/.openclaw/RECOVER-SERVICES.md` — human-readable recovery quickref

## Three-Tier Architecture

### Tier 1: LaunchAgent (Infrastructure)

**When to use** (any of):
- Service is a shared dependency (if it dies, many others break)
- No interactive terminal needed
- Must auto-restart on crash (seconds)

**Features**:
- `RunAtLoad: true` → starts on boot
- `KeepAlive: true` → auto-restarts on crash
- macOS has built-in backoff, won't loop infinitely

**Examples**: tunnel clients, proxy daemons, gateway processes

Template: `references/launchagent-template.md`

### Tier 2: tmux + bootstrap script (App Services)

**When to use**:
- Need terminal access (occasionally attach to check logs)
- Dev servers / watch mode
- Boot recovery is enough (no crash auto-restart needed)

**Features**:
- All sessions on OpenClaw tmux socket: `/tmp/openclaw-tmux/openclaw.sock`
- One bootstrap script recreates all sessions
- One LaunchAgent (`KeepAlive: false`) runs bootstrap once on boot

**Examples**: dev servers, crawlers, sync processes

Template: `references/bootstrap-template.md`

### Tier 3: wrapper daemon (Persistent Interactive Services)

**When to use**:
- Needs PTY + attachable terminal + human takeover
- Too important for boot-only recovery
- Must auto-recover from crash

**Features**:
- Long-running daemon (`KeepAlive: true`), checks every N seconds
- Checks **pane process** not just session existence (catches "session alive but program exited to shell" blind spot)
- Cooldown after N consecutive failures (prevents infinite restart loops)
- Uses **default tmux socket** (convenient for human `tmux attach`)

**Examples**: Claude Code channels, persistent coding agents, long-running interactive services

Template: `references/wrapper-template.md`

#### 🚨 Tier 3 Setup Checklist

Every new Tier 3 service must complete all steps:

1. **Decide tmux session name** — fixed name, wrapper uses this
2. **Create dedicated working directory** — don't use `/` or `~`
3. **Verify exact startup command** — use `ps aux` on a running instance, never guess
4. **Decide tmux socket** — default (human-operated) or OpenClaw (agent-managed)
5. **First manual startup + trust confirmation** — trust is per-directory, one-time
6. **Write wrapper script** — from `references/wrapper-template.md`
7. **Create LaunchAgent plist** — `KeepAlive: true`
8. **Test: kill session → wrapper auto-rebuilds**
9. **Test: kill program but session survives → wrapper detects shell in pane → auto-rebuilds**
10. **Update service-registry.json**
11. **Update recovery docs**

## tmux Socket Convention

| Socket | Path | Who uses it | Visible in `tmux ls` |
|---|---|---|---|
| Default | `/tmp/tmux-$(id -u)/default` | Human manual ops | ✅ |
| OpenClaw | `/tmp/openclaw-tmux/openclaw.sock` | Agent management | ❌ needs `-S` |

**Rule**: Human-operated → default socket. Agent-managed → OpenClaw socket.

## Service Registry

Each machine has one `service-registry.json` defining all persistent services.

Location: `~/.openclaw/workspace/service-registry.json`

Format spec + all fields: `references/registry-spec.md`
Example: `references/example-registry.json`

**Update this file every time you add/remove/modify a service.**

## Workflows

### Add a Service

1. Determine Tier (see criteria above)
2. Add entry to `service-registry.json`
3. Based on Tier:
   - Tier 1: Generate plist from template → deploy to `~/Library/LaunchAgents/` → `launchctl load`
   - Tier 2: Update bootstrap script → copy to deploy location
   - Tier 3: Follow the 11-step checklist above
4. Test
5. Update recovery docs

### Upgrade a Service (e.g. tmux → LaunchAgent)

1. Change tier and type in registry
2. Generate new plist
3. Remove from bootstrap script
4. Kill tmux session
5. Deploy plist → `launchctl load`
6. Verify
7. Update recovery docs

### Diagnose a Service

```bash
# Tier 1
launchctl list | grep <label>
tail -20 ~/.openclaw/logs/<service>.err.log

# Tier 2
tmux -S /tmp/openclaw-tmux/openclaw.sock has-session -t <session>
tmux -S /tmp/openclaw-tmux/openclaw.sock capture-pane -pt <session>:0.0 | tail -20

# Tier 3
launchctl list | grep <wrapper-label>
tail -20 ~/.openclaw/logs/<wrapper>.log
tmux list-panes -t <session> -F '#{pane_current_command}'
# zsh/bash = program exited, wrapper should auto-rebuild
```

## Doc Sync Rule

Any infra change must update:
1. `service-registry.json`
2. Corresponding scripts/plists
3. `~/.openclaw/RECOVER-SERVICES.md`
4. Design docs (Obsidian or equivalent)

**Not updated = task not complete.**

## Known Limitations

1. **Tier 2 has no crash auto-restart**: bootstrap only covers boot recovery
2. **Tier 3 wrapper can't detect internal program state**: only checks pane process, not whether the program is functioning correctly
3. **Auth expiry**: services requiring manual re-login (e.g. OAuth) will trigger wrapper cooldown but can't self-heal
