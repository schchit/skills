# Diagnosis Checklist — OpenClaw Gateway Linux

Run these checks in order to locate the issue.

## Quick full check (one command)

```bash
echo "=== Service status ===" && \
  systemctl --user status openclaw-gateway --no-pager | grep -E "Loaded|Active" && \
  echo "=== Unit env vars ===" && \
  grep -E "XDG_RUNTIME|DBUS" ~/.config/systemd/user/openclaw-gateway.service || echo "MISSING - run Issue 1 fix" && \
  echo "=== Linger ===" && \
  loginctl show-user $(whoami) 2>/dev/null | grep Linger && \
  echo "=== OpenClaw status ===" && \
  openclaw status 2>/dev/null | grep "Gateway service"
```

Expected output:
```
Loaded: loaded (...; enabled; ...)
Active: active (running)
Environment=XDG_RUNTIME_DIR=/run/user/0
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/0/bus
Linger=yes
systemd installed · enabled · running
```

---

## Step-by-step

### 1. Is the service running?
```bash
systemctl --user status openclaw-gateway
```
If not running: `systemctl --user start openclaw-gateway`

### 2. Does the unit file have the required env vars?
```bash
grep -E "XDG_RUNTIME|DBUS" ~/.config/systemd/user/openclaw-gateway.service
```
If missing → apply **Issue 1 fix** from SKILL.md.

### 3. Can systemctl --user reach the user bus?
```bash
systemctl --user is-enabled openclaw-gateway
```
Expected: `enabled`. If "Failed to connect to bus" → missing vars in unit file (Step 2).

### 4. Is linger enabled?
```bash
loginctl show-user $(whoami) | grep Linger
```
Expected: `Linger=yes`. If no: `loginctl enable-linger $(whoami)`

### 5. Does OpenClaw see correct status?
```bash
openclaw status 2>/dev/null | grep "Gateway service"
```
Expected: `systemd installed · enabled · running (pid ...)`

### 6. What UID/runtime dir is in use?
```bash
id -u           # your UID
ls /run/user/   # should contain a directory named after your UID
```
Make sure unit file uses the correct path: `/run/user/<UID>`.
