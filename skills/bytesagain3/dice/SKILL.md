---
name: dice
version: 1.0.0
author: BytesAgain
license: MIT-0
tags: [dice, tool, utility]
---

# Dice

Dice roller — roll any dice, statistics, probability, and game presets.

## Commands

| Command | Description |
|---------|-------------|
| `dice help` | Show usage info |
| `dice run` | Run main task |
| `dice status` | Check state |
| `dice list` | List items |
| `dice add <item>` | Add item |
| `dice export <fmt>` | Export data |

## Usage

```bash
dice help
dice run
dice status
```

## Examples

```bash
dice help
dice run
dice export json
```

## Output

Results go to stdout. Save with `dice run > output.txt`.

## Configuration

Set `DICE_DIR` to change data directory. Default: `~/.local/share/dice/`

---
*Powered by BytesAgain | bytesagain.com*
*Feedback & Feature Requests: https://bytesagain.com/feedback*
