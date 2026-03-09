# 🛒 Best Product Recommender

Find the best products in any category with expert picks, value recommendations, and budget options across US, UK, and EU retailers.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/Version-1.0.0-blue)](https://github.com/openclaw/skills)
[![Platform](https://img.shields.io/badge/Platform-OpenClaw-green)](https://openclaw.ai)

## Features

- 🎯 **Expert Picks** — Top-rated products from trusted sources
- 💎 **Best Value** — Best performance per euro/dollar/pound
- 💶 **Budget Options** — Solid picks under $50/£40/€50
- 🌍 **Multi-Region** — US, UK, Germany, France, Italy, Spain, NL, BE, PL
- 📦 **Price Comparison** — Lowest price including shipping
- ⏱️ **6-Hour Cache** — Fast responses, fresh data

## Installation

```bash
clawhub install best-product
```

Or manually: Copy `SKILL.md` to your skills folder.

## Usage

```bash
# US (default)
/best earbuds
/best airfryer
/best laptop

# UK
/best earbuds uk

# Germany
/best earbuds de
/best toaster de

# France
/best headphones fr

# Netherlands
/best oordopjes nl
/best airfryer nl

# Belgium
/best headphones be

# Poland
/best laptop pl
```

## Supported Regions

| Region | Retailers |
|--------|-----------|
| US | Amazon, Best Buy, Walmart |
| UK | Amazon UK, Currys, John Lewis |
| DE | Amazon DE, MediaMarkt, Saturn |
| FR | Amazon FR, Fnac, Darty |
| IT | Amazon IT, MediaMarkt, Unieuro |
| ES | Amazon ES, MediaMarkt, El Corte Inglés |
| NL | Amazon NL, CoolBlue, MediaMarkt |
| BE | Amazon BE, MediaMarkt, CoolBlue |
| PL | Amazon PL, Media Expert, RTV Euro AGD |

## Review Sources

- **US:** Wirecutter, RTINGS, Consumer Reports
- **UK:** TechRadar UK, Which?
- **NL:** Tweakers, Kieskeurig, Consumentenbond
- **DE:** Testberichte.de, Stiftung Warentest
- **FR:** 01net, Les Numériques
- **IT:** Altroconsumo
- **ES:** Xataka
- **PL:** Benchmark.pl, Komputer Świat
- **BE:** Test-Aankoop

## Output Example

```
🎧 /best earbuds

📍 NL — 8 mrt 2026

🏆 TOP PICK
Sony WF-1000XM5
€182 • Amazon
Kleinste behuizing, beste ANC ooit, 8u accu
amazon.nl/dp/B0CXW2HWXR

💎 BEST VALUE
OnePlus Buds Pro 3
€109 • Proshop
Uitstekend geluid, prima ANC, 43u met case
proshop.nl/3318120

💶 BUDGET
Sony WF-C710N
€76 • Amazon
Goede ANC voor de prijs, 8.5u batterij
amazon.nl/dp/B0F1TG6JV6

Sources: AndroidPlanet, Consumentenbond
```

## Technical Details

- **Cache:** 6 hours in `~/.openclaw/cache/best-products/`
- **No credentials required:** Uses OpenClaw's web_search and web_fetch
- **Privacy:** Only search queries sent to Brave Search API

## License

MIT License — See [LICENSE](LICENSE) for details.

## Author

OpenClaw Community

---

*Part of the OpenClaw skill ecosystem — discover more at [clawhub.ai](https://clawhub.ai)*
