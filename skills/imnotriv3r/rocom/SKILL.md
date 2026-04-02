---
name: rocom
description: "Roco Kingdom:World full data query and guide. Pet pokedex, skills, element counters, formations, evolution chains, stats, mark system, dungeons, regions, natures. All data bundled — install and use instantly. No sync needed."
metadata: { "openclaw": { "emoji": "castle", "requires": { "bins": ["node"] } } }
---

# Roco Kingdom:World Full Data Guide

Data from wiki.biligame.com/rocom (Bilibili WIKI). All data is **bundled** — install and query instantly, no network required.

## Usage

```bash
node rocom.mjs pet search 酷拉
node rocom.mjs formation list
node rocom.mjs analyze stats
```

## Update

Data is updated by the skill publisher. When a new version is available:

```bash
clawhub update rocom
# or
openclaw skills update rocom
```

## Commands

### Pets
| Command | Description |
|---------|-------------|
| `pet list [--element X] [--stage X] [--boss] [--region]` | Pet list / filter |
| `pet search <name>` | Search pet |
| `pet detail <name>` | Pet details (stats / skills / traits / distribution) |
| `pet evolve <name>` | Evolution chain |

### Skills / Items / Quests
| Command | Description |
|---------|-------------|
| `search <keyword>` | Cross-category search |
| `skill list [--element X] [--type X]` | Skill list / filter |
| `skill search <name>` | Search skill |
| `item list` / `item search <name>` | Items |
| `quest list` | Quests |

### Formations / Marks / Dungeons / Regions / Natures
| Command | Description |
|---------|-------------|
| `formation list/search/detail <q>` | Formations (with natures / skills / strategy) |
| `mark list` / `search <q>` | Mark system (positive / negative) |
| `dungeon list` / `search <q>` | Dungeons |
| `region list/detail/search <q>` | Regions |
| `nature list` / `search <name>` | Natures (stat boosts / reductions) |

### Analysis
| Command | Description |
|---------|-------------|
| `analyze element` | Element distribution |
| `analyze stats` | Stats ranking (final forms) |
| `analyze top --stat 速度 --n 20` | Top N by single stat |

### Other
| Command | Description |
|---------|-------------|
| `status` | Data status |
| `update` | Check for skill updates |

## Game Knowledge

See `references/game-knowledge.md` for: element matchup chart, mark system, stat guide, nature selection, team building tips.

Quick summary:
- Elements: Fire beats Grass/Bug/Ice/Mechanical, weak to Water/Ground. Water beats Fire/Ground, weak to Grass/Electric (18 types total)
- Marks: Each side has 1 positive + 1 negative at a time, new replaces old
- Stats: Final forms total 500-700+, Speed determines turn order
- Team building: Element coverage + offense/defense balance + mark synergy
