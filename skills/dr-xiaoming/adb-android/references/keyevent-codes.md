# ADB KeyEvent Codes Reference

Common keyevent codes for `adb shell input keyevent <code>`.

## Navigation & System

| Code | Key | Description |
|------|-----|-------------|
| 3 | HOME | Home button |
| 4 | BACK | Back button |
| 24 | VOLUME_UP | Volume up |
| 25 | VOLUME_DOWN | Volume down |
| 26 | POWER | Power/Lock |
| 27 | CAMERA | Camera button |
| 82 | MENU | Menu button |
| 187 | APP_SWITCH | Recent apps |
| 220 | BRIGHTNESS_DOWN | |
| 221 | BRIGHTNESS_UP | |

## Text Input

| Code | Key | Description |
|------|-----|-------------|
| 66 | ENTER | Enter/Return |
| 67 | DEL | Backspace |
| 112 | FORWARD_DEL | Delete forward |
| 61 | TAB | Tab |
| 62 | SPACE | Space |
| 59 | SHIFT_LEFT | |
| 113 | CTRL_LEFT | |

## D-Pad / Arrow Keys

| Code | Key |
|------|-----|
| 19 | DPAD_UP |
| 20 | DPAD_DOWN |
| 21 | DPAD_LEFT |
| 22 | DPAD_RIGHT |
| 23 | DPAD_CENTER |

## Media

| Code | Key |
|------|-----|
| 85 | MEDIA_PLAY_PAUSE |
| 86 | MEDIA_STOP |
| 87 | MEDIA_NEXT |
| 88 | MEDIA_PREVIOUS |
| 126 | MEDIA_PLAY |
| 127 | MEDIA_PAUSE |
| 164 | MUTE |

## Letters & Numbers

- Letters: A=29, B=30, ... Z=54
- Numbers: 0=7, 1=8, ... 9=16
- F1-F12: 131-142

## Usage Patterns

```bash
# Press Home
adb shell input keyevent 3

# Long press Power (3 seconds) — use sendevent for long press
adb shell input keyevent --longpress 26

# Key combo: Ctrl+A (select all) — not directly supported, use:
adb shell input keyevent 29 --meta CTRL_LEFT
```
