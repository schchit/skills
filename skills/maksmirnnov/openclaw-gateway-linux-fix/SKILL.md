---
name: openclaw-gateway-linux-fix
description: Fix and diagnose OpenClaw Gateway service issues on Linux. Use when the gateway service shows "disabled" status despite running, when `openclaw gateway status` or `openclaw status` reports incorrect service state, or when systemctl --user fails with "No medium found" or "Failed to connect to bus". The most common fix — adding XDG_RUNTIME_DIR to shell environment — does NOT work. The correct fix is adding these vars to the systemd unit file so the gateway process itself can query its own status. Also covers safe restart without self-kill and shell escalation gotchas.
---

# OpenClaw Gateway — Linux Fixes

## Issue 1: Gateway shows "disabled" despite running

**Symptom:** `openclaw status` or `openclaw gateway status` shows `disabled`, but the service is actually running.

**Root cause:** The gateway process spawns `systemctl --user is-enabled` without `XDG_RUNTIME_DIR` and `DBUS_SESSION_BUS_ADDRESS` in its environment. Without these, systemd user bus is unreachable → "Failed to connect to bus: No medium found".

**⚠️ Common wrong fix:** Adding vars to `~/.bashrc` or shell environment does NOT help — the gateway daemon doesn't inherit your shell env.

**Correct fix:** Add vars directly to the systemd unit file:

```bash
# Detect the correct runtime dir for current user
RUNTIME_DIR="/run/user/$(id -u)"

# Add env vars to the unit file
sed -i "/^\[Service\]/a Environment=XDG_RUNTIME_DIR=${RUNTIME_DIR}\nEnvironment=DBUS_SESSION_BUS_ADDRESS=unix:path=${RUNTIME_DIR}/bus" \
  ~/.config/systemd/user/openclaw-gateway.service

# Reload and restart safely
systemctl --user daemon-reload
nohup bash -c 'sleep 2 && systemctl --user restart openclaw-gateway' > /tmp/gw-restart.log 2>&1 &
```

Verify:
```bash
openclaw gateway status  # should show: systemd (enabled)
```

---

## Issue 2: Safe gateway restart

**Problem:** `openclaw gateway restart` and `systemctl --user restart openclaw-gateway` send SIGTERM to the gateway process — which kills the shell running the command mid-execution.

**Always use this pattern instead:**
```bash
nohup bash -c 'sleep 2 && systemctl --user restart openclaw-gateway' > /tmp/gw-restart.log 2>&1 &
```

The `sleep 2` + background `&` detaches the restart from the current process tree before shutdown.

---

## Issue 3: `openclaw gateway status` shows "disabled" in SSH session

**Root cause:** Shell session lacks `XDG_RUNTIME_DIR`. Affects `sudo su` (without `-`), non-login shells, cron.

**Fix:** Add to `~/.bashrc` and `/etc/profile.d/openclaw-env.sh`:
```bash
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
```

**Shell escalation — what works:**
| Command | Login shell | Works |
|---|---|---|
| `sudo su -` | ✅ | ✅ |
| `sudo -i` | ✅ | ✅ (if vars in `.bashrc`) |
| `sudo su` | ❌ | ❌ |
| `sudo openclaw` | ❌ | ❌ |

---

## Issue 4: Service not persisting after reboot

OpenClaw runs as a **user-scope** systemd service (`~/.config/systemd/user/`), not system-scope. Enable linger to keep it running after logout:

```bash
loginctl enable-linger $(whoami)
systemctl --user enable openclaw-gateway
```

---

See `references/diagnosis.md` for a step-by-step diagnostic checklist.
