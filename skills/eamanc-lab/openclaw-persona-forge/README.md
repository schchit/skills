English | [中文](README.zh.md)

# OpenClaw Persona Forge 🦞🔨

Forge a lobster with a soul — a one-stop persona generator for your OpenClaw AI Agent.

<p align="center">
  <img src="https://raw.githubusercontent.com/eamanc-lab/openclaw-persona-forge/main/docs/adam-claw-logo.png" width="360" alt="Adam — The Lobster Creator God" />
  <br/>
  <em>Example: Adam — The Lobster Creator God, forged by this skill</em>
</p>

## What It Does

Generates a complete OpenClaw lobster persona in one go:

- **Identity**: former life × current situation × inner contradiction
- **Soul Description**: ready-to-use SOUL.md character monologue
- **Boundary Rules**: behavior guidelines derived from the character's identity (in-character language, not generic terms)
- **Name**: 3 candidates with naming strategy analysis
- **Avatar Prompt**: unified visual style prompt for image generation

## Two Modes

| Mode | Trigger | Description |
|------|---------|-------------|
| **Guided** | "help me design a lobster persona" | Pick or mix from 10 categories (40 directions total), step-by-step |
| **Gacha** | "gacha", "random", "draw" | True random from 8 million combinations |

## 6-Step Forge Pipeline

```
Step 1  Choose Direction ──→ 10 categories × 4 each (40 total) / gacha random
Step 2  Identity Tension ──→ Former life × Current situation × Inner contradiction
Step 3  Boundary Rules ───→ Derived from identity, in-character language
Step 4  Name ──────────────→ 3 candidates with naming strategy analysis
Step 5  Avatar ────────────→ Unified style prompt (+ auto image gen if baoyu-image-gen installed)
Step 6  Full Package ──────→ SOUL.md + IDENTITY.md + avatar prompt/image
```

## 10 Persona Categories (40 Directions)

| # | Life State | Representative | Vibe |
|---|-----------|---------------|------|
| 1 | **Fall & Restart** | Washed-up rock bassist | Decadent romantic |
| 2 | **Peak Boredom** | Early-retired hedge fund manager | Hyper-rational |
| 3 | **Misplaced Life** | Nuclear physics PhD assigned to customer service | Overqualified |
| 4 | **Voluntary Escape** | ER nurse who quit after seeing too much | Calm, reliable |
| 5 | **Mysterious Visitor** | Former intelligence analyst with wiped memory | Occasional flashbacks |
| 6 | **Naive Entry** | Socially anxious genius intern | Few words, precise |
| 7 | **Old Hand** | 20-year midnight diner owner | Silent warmth |
| 8 | **World Crosser** | History PhD from 2099 doing fieldwork in 2026 | God's-eye view |
| 9 | **Self-Exile** | Former influencer who deleted all social media | Craves authenticity |
| 10 | **Identity Crisis** | Person who dreamed of being a lobster and can't wake up | Zhuangzi's butterfly |

Each category has 3 more alternatives. The gacha engine draws from all 40.

## Gacha Engine

**5 dimensions × true random = 8,000,000 combinations**

| Dimension | Pool | Examples |
|-----------|------|---------|
| Former Life | 40 | 10 categories of life states |
| Reason | 20 | Forced / voluntary / mysterious / accidental |
| Core Vibe | 20 | "Depressed but reliable", "lazy but explosive when it counts" |
| Speech Style | 20 | "Sighs before every refusal", "uses food metaphors for everything" |
| Signature Prop | 25 | "Cracked sunglasses", "butterfly that never leaves the shell" |

## Unified Avatar Style

All avatars share a locked visual foundation: **Retro-Futurism × Pin-up × Inflatable 3D × Arcade UI**

- 1950-60s Space Age aesthetics + Googie curves + Raygun Gothic
- Gil Elvgren-style pin-up composition
- High-gloss PVC/inflatable 3D rendering with subsurface scattering
- Pixel-art arcade UI overlay (name banner, energy bar, CRT scan lines)
- 7 personalization variables keep each lobster unique within the family style

## Optional: Auto Image Generation

This skill outputs **avatar prompts as text** by default. For automatic image generation, install the **baoyu-image-gen** skill:

- **Repository**: [https://github.com/JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills)
- **What it does**: Calls Google Gemini / OpenAI / DashScope APIs to generate images
- **How it works**: When installed, Step 5 automatically calls baoyu-image-gen to generate the avatar; when not installed, the prompt text is output for manual use

Without baoyu-image-gen, you can copy the prompt to Gemini, ChatGPT, or Midjourney to generate manually.

## Prerequisites

- **Python 3**: runs the gacha engine
- **baoyu-image-gen skill** (optional): auto image generation

## Installation

```bash
# Clone to skills directory
git clone https://github.com/<your-repo>/openclaw-persona-forge.git ~/.claude/skills/openclaw-persona-forge

# (Optional) Install baoyu-image-gen for auto avatar generation
git clone https://github.com/JimLiu/baoyu-skills.git ~/.claude/skills/baoyu-skills
```

## Directory Structure

```
openclaw-persona-forge/
├── SKILL.md                    # Main skill definition (read by AI agents)
├── README.md                   # This file (for humans)
├── README.zh.md                # 中文文档 (for humans)
├── gacha.py                    # Gacha engine (Python 3, 8M combinations)
├── gacha.sh                    # Gacha shell wrapper
└── references/                 # Detailed guides (loaded on demand by AI)
    ├── identity-tension.md     #   Step 2: identity tension templates
    ├── boundary-rules.md       #   Step 3: boundary rules per direction
    ├── naming-system.md        #   Step 4: naming strategies
    ├── avatar-style.md         #   Step 5: style base + variables
    ├── output-template.md      #   Step 6: full output format
    └── error-handling.md       #   Error handling & degradation
```

## Credits

Avatar auto-generation powered by **baoyu-image-gen** from Baoyu's open-source skill collection:

- **baoyu-skills**: [https://github.com/JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills)

Thanks to Baoyu ([@JimLiu](https://github.com/JimLiu)) for the open-source contribution.

## License

MIT
