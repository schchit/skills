---
name: adb-android
description: >
  Control Android devices via ADB (Android Debug Bridge) from a Mac. Use when: remotely operating
  an Android phone (tap, swipe, type, screenshot, screen recording, install/uninstall apps, file
  transfer, shell commands, logcat, wireless debugging, scrcpy mirroring). Triggers on "android",
  "adb", "phone", "手机操控", "安卓", "screen mirror", "scrcpy". Targets macOS hosts with USB or
  Wi-Fi connected Android devices. NOT for: iOS devices, emulators-only workflows, or Android app
  development/building.
---

# ADB Android Control (macOS)

Control Android devices from a Mac via ADB over USB or Wi-Fi.

## Prerequisites

Install on macOS:

```bash
brew install android-platform-tools
# Verify
adb version
```

Optional but recommended — scrcpy for screen mirroring:

```bash
brew install scrcpy
```

## Device Connection

### USB

1. Enable **Developer Options** on Android: Settings → About Phone → tap Build Number 7 times
2. Enable **USB Debugging** in Developer Options
3. Connect USB cable, approve the RSA key prompt on phone
4. Verify: `adb devices` should show device as `device` (not `unauthorized`)

### Wireless (Wi-Fi) — Android 11+

```bash
# On phone: Developer Options → Wireless Debugging → enable → Pair with code
adb pair <phone-ip>:<pair-port>    # Enter the 6-digit code
adb connect <phone-ip>:<connect-port>
adb devices   # Should show connected
```

### Wireless (Legacy, Android 10 and below)

```bash
# Connect via USB first, then:
adb tcpip 5555
adb connect <phone-ip>:5555
# Disconnect USB
```

## Core Commands

### Device Info

```bash
adb devices -l                     # List with details
adb shell getprop ro.product.model # Device model
adb shell getprop ro.build.version.release  # Android version
adb shell dumpsys battery          # Battery info
adb shell wm size                  # Screen resolution
```

### App Management

```bash
adb install app.apk               # Install
adb install -r app.apk            # Reinstall keeping data
adb uninstall com.example.app     # Uninstall
adb shell pm list packages         # All packages
adb shell pm list packages -3      # Third-party only
adb shell am start -n com.example.app/.MainActivity  # Launch app
adb shell am force-stop com.example.app              # Force stop
adb shell pm clear com.example.app                   # Clear app data
```

### File Transfer

```bash
adb push local_file /sdcard/       # Mac → Phone
adb pull /sdcard/file.jpg ./       # Phone → Mac
adb shell ls /sdcard/              # List files
```

### Screen Interaction (UI Automation)

```bash
adb shell input tap 500 800        # Tap at (x,y)
adb shell input swipe 500 1500 500 500 300  # Swipe (x1,y1,x2,y2,durationMs)
adb shell input text "hello"       # Type text (no spaces — use %s for space)
adb shell input keyevent 66        # Press Enter
adb shell input keyevent 4         # Press Back
adb shell input keyevent 3         # Press Home
adb shell input keyevent 26        # Power button
adb shell input keyevent 187       # Recent apps
```

Common keyevent codes: See `references/keyevent-codes.md`

### Screenshot & Recording

```bash
adb shell screencap /sdcard/screen.png && adb pull /sdcard/screen.png ./
adb shell screenrecord /sdcard/video.mp4   # Record (Ctrl+C to stop, max 3min)
adb shell screenrecord --time-limit 10 /sdcard/video.mp4  # 10 seconds
adb pull /sdcard/video.mp4 ./
```

### Logcat

```bash
adb logcat                         # Full log stream
adb logcat -d                      # Dump and exit
adb logcat *:E                     # Errors only
adb logcat -s "MyTag"              # Filter by tag
adb logcat --pid=$(adb shell pidof com.example.app)  # App-specific
adb logcat -c                      # Clear log buffer
```

### Shell & System

```bash
adb shell                          # Interactive shell
adb shell whoami                   # Current user
adb shell settings get system screen_brightness  # Get brightness
adb shell settings put system screen_brightness 128  # Set brightness (0-255)
adb shell svc wifi enable          # Enable Wi-Fi
adb shell svc wifi disable         # Disable Wi-Fi
adb shell dumpsys activity top     # Current foreground activity
adb shell am broadcast -a android.intent.action.AIRPLANE_MODE  # Toggle airplane
adb reboot                         # Reboot device
```

### Clipboard

```bash
adb shell am broadcast -a clipper.set -e text "content to copy"  # Requires Clipper app
# Alternative for Android 10+:
adb shell input text "paste this"
```

## Screen Mirroring with scrcpy

```bash
scrcpy                             # Mirror with default settings
scrcpy --max-size 1024             # Limit resolution
scrcpy --bit-rate 2M               # Limit bitrate
scrcpy --record file.mp4           # Mirror + record
scrcpy --no-audio                  # Video only
scrcpy --turn-screen-off           # Mirror but keep phone screen off
scrcpy --stay-awake                # Prevent sleep while connected
scrcpy --window-title "MyPhone"    # Custom window title
scrcpy --crop 1080:1920:0:0        # Crop region (w:h:x:y)
```

Wireless scrcpy (after adb connect):

```bash
scrcpy --tcpip=<phone-ip>:<port>
```

## Multi-Device

When multiple devices are connected, specify the target:

```bash
adb -s <serial> shell ...          # By serial number
adb -s <ip>:<port> shell ...       # By IP (wireless)
```

Get serial: `adb devices` — first column is the serial.

## Automation Patterns

### Take screenshot → analyze → tap

```bash
# 1. Screenshot
adb shell screencap /sdcard/screen.png && adb pull /sdcard/screen.png ./screen.png
# 2. Analyze image (use vision model or image tool)
# 3. Tap target coordinates
adb shell input tap <x> <y>
```

### Batch install APKs

```bash
for apk in *.apk; do adb install -r "$apk"; done
```

### Open URL in browser

```bash
adb shell am start -a android.intent.action.VIEW -d "https://example.com"
```

### Send SMS (requires default SMS app handling)

```bash
adb shell am start -a android.intent.action.SENDTO -d "sms:+1234567890" --es sms_body "Hello"
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `unauthorized` in adb devices | Approve RSA prompt on phone; revoke & re-approve in Developer Options |
| `offline` | Reconnect USB; `adb kill-server && adb start-server` |
| Wireless disconnect | Re-pair: `adb pair` or reconnect: `adb connect` |
| `no permissions` | On Linux: add udev rules; on Mac: usually not an issue |
| Slow wireless | Use 5GHz Wi-Fi; keep phone and Mac on same network |
| scrcpy black screen | Update scrcpy; try `--codec h264`; check USB debugging enabled |

## Node Execution (for OpenClaw on cloud servers)

When the agent runs on a cloud server (not directly on the Mac), execute ADB commands on the Mac node:

```
Use exec with host="node" and node="<mac-node-name>" to run adb commands on the Mac
that has the Android phone connected via USB.
```

This is the typical setup: the Android phone is USB-connected to the Mac, and the agent
orchestrates from the cloud.
