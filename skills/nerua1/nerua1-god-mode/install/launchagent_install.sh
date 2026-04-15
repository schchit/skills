#!/bin/bash
# Optional: install god-mode-watcher as macOS LaunchAgent (auto-start on login)
# Run manually if you want background model watching.

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="$(which python3)"
PLIST="$HOME/Library/LaunchAgents/ai.openclaw.god-mode-watcher.plist"
LABEL="ai.openclaw.god-mode-watcher"
LOG="$HOME/Library/Logs/god-mode-watcher.log"

cat > "$PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>$LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON</string>
        <string>$SKILL_DIR/scripts/probe_watcher.py</string>
    </array>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>StandardOutPath</key><string>$LOG</string>
    <key>StandardErrorPath</key><string>$LOG</string>
</dict>
</plist>
EOF

launchctl load "$PLIST" && echo "✅ Installed: $LABEL" || echo "❌ Failed"
echo "Logs: $LOG"
