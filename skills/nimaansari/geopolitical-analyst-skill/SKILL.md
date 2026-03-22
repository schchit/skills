---
name: geopolitical-analyst
description: Professional geopolitical intelligence analysis framework enabling systematic analysis of any geopolitical situation with live data integration (GDELT, ACLED, ReliefWeb). Generates probability-weighted scenarios, identifies intelligence gaps, and provides confidence-scored assessments. Use when analyzing geopolitical events, conflicts, regional tensions, or political scenarios.
icon: 🌍
authors:
  - Nima Ansari
repository: https://github.com/nimaansari/geopolitical-analyst-skill
license: MIT
tags:
  - intelligence-analysis
  - geopolitical
  - scenario-planning
  - conflict-analysis
  - data-analysis
  - research
  - live-data
runtime: python
---

# Geopolitical Analyst Intelligence Framework

A professional-grade intelligence analysis system that enables systematic geopolitical understanding through live data integration and rigorous analytical frameworks.

## Description

This skill provides AI agents with a comprehensive framework for analyzing any geopolitical situation. Rather than relying on intuition, it combines:

- **39 analytical modules** organized across 4 analytical tiers
- **9-step intelligence workflow** automating data acquisition through scenario planning
- **Live data integration** pulling real-time articles, conflict events, humanitarian reports, and economic indicators
- **Probability-weighted scenario modeling** with base case, upside, downside, and catastrophic futures
- **Explicit intelligence gap identification** documenting what is unknown
- **Confidence-scored assessments** tracking analytical certainty

## Key Features

### 39 Analytical Modules

**Foundational:** Game theory, early warning, international law, elections, climate/resources, treaties, dead reckoning, actor behavior, diaspora networks

**Strategic Thinking:** Multi-perspective analysis, scenario modeling, trend detection, calibration, causal chains, elite factionalism, geospatial dynamics

**Rigorous Analysis:** Credible commitment, alliance stability, escalation ladder, thresholds, spiral dynamics, intelligence gaps, information asymmetry, sanctions, hybrid warfare, historical analogs

**Specialized:** Art of War strategic framework, network analysis, economic coercion

### 9-Step Workflow

1. Data Acquisition → Pull live data from GDELT, ACLED, ReliefWeb
2. Source Bias Assessment → Evaluate reliability of each source
3. Actor Mapping → Identify key players, interests, capabilities
4. Economic Analysis → Trade, sanctions, currency, resource stress
5. Network Mapping → Patrons, proxies, alliances, diaspora
6. Historical Patterns → Compare to archetypes, extract lessons
7. Information Warfare → Analyze narratives, detect operations
8. Red Team Analysis → Challenge assessment, find blind spots
9. Output & Scenarios → Decision-ready findings with 4 alternative futures

### Live Data Sources

- **GDELT:** Real-time articles, media tone, event themes (300M+ articles)
- **ACLED:** Armed conflict events, casualties, event types (200+ countries)
- **ReliefWeb:** Humanitarian reports, affected populations (UN-curated)
- **Frankfurter:** Currency rates, economic stress signals (150+ currencies)
- **UN Sanctions:** Current sanctions regimes, OFAC data

### Error Handling & Fallbacks

- Automatic fallback to RSS feeds if primary APIs fail
- Explicit data quality tracking and degradation warnings
- No silent failures - all errors logged explicitly
- Graceful handling of rate limiting and network issues

## Usage

### CLI (Interactive Mode)

```bash
# Analyze any geopolitical topic
python3 interactive_monitor.py

# Type topic when prompted
# 📍 Analyze: Gaza
# 📍 Analyze: Ukraine|BRIEF
# 📍 Analyze: Taiwan|FLASH
```

### Python API

```python
from geopolitical_analyst_agent import run_analysis

# Analyze any geopolitical situation
result = run_analysis(
    country="Ukraine",
    keywords=["Ukraine", "Russia", "military", "NATO"],
    depth="FULL"  # FLASH (90s), BRIEF (5m), FULL (15m)
)

# Returns live data + 39-module analysis + scenarios + gaps
```

### Command Line

```bash
# Full analysis
python3 interactive_monitor.py Ukraine FULL

# Quick analysis
python3 interactive_monitor.py Gaza BRIEF

# Flash update
python3 interactive_monitor.py Taiwan FLASH

# Any topic
python3 interactive_monitor.py "South China Sea" FULL
```

## Installation

```bash
# Clone
git clone https://github.com/nimaansari/geopolitical-analyst-skill.git
cd geopolitical-analyst-skill

# Install dependencies
pip install -r requirements.txt

# Run
python3 interactive_monitor.py
```

## Configuration

Edit `monitor_config.json` to configure automated monitoring:

```json
{
  "monitor_topics": [
    {"topic": "Gaza", "depth": "FULL"},
    {"topic": "Ukraine", "depth": "BRIEF"},
    {"topic": "Taiwan", "depth": "BRIEF"}
  ],
  "run_interval_hours": 6
}
```

Or use interactive configuration:

```bash
python3 configure_monitor.py
```

## Output

Each analysis returns:

- **Live Data:** Current news articles, conflict events, humanitarian status, economic indicators
- **Analysis:** All 9-step workflow applied, 39 modules integrated, multi-perspective views
- **Scenarios:** 4 alternative futures with probability distribution
- **Intelligence Assessment:** Key observables, gaps, confidence scores
- **Timestamped JSON Report:** Full analysis saved for tracking

## Requirements

```
Python 3.9+
requests
python-dateutil
```

Optional: schedule, feedparser (for RSS fallback)

## Documentation

- **README.md** - Overview and quick start
- **QUICK_REFERENCE.md** - Cheat sheet
- **LIVE_DATA_USAGE.md** - API reference
- **SKILL_USAGE.md** - How AIs use this skill
- **FIXES.md** - Error handling
- **SECURITY_AUDIT.md** - Security verification
- **CONTRIBUTING.md** - Contributing guidelines

## Performance

| Metric | Value |
|--------|-------|
| Package Size | 154.6 KB (compressed) |
| Modules | 39 |
| API Sources | 5 (all public) |
| Analysis Time | FLASH: 90s, BRIEF: 5m, FULL: 15m |
| Data Freshness | Real-time articles, 1-3 day conflict data, daily humanitarian reports |

## Limitations

- GDELT subject to rate limiting (429 errors handled gracefully)
- ACLED has 1-3 day lag in conflict data
- Cannot predict classified military actions
- Scenarios are probabilistic, not deterministic
- Confidence depends on data quality and information availability

## Security

- ✅ No API keys stored in code
- ✅ All APIs use public endpoints
- ✅ No credentials hardcoded
- ✅ Security audit passed
- See SECURITY_AUDIT.md for details

## Real-World Validation

Validated against actual intelligence reports. Framework demonstrates:

- ✅ Correct application of all 9 workflow steps
- ✅ Accurate multi-perspective analysis
- ✅ Realistic scenario modeling
- ✅ Proper intelligence gap identification
- ✅ Appropriate confidence scoring

## License

MIT - See LICENSE file

## Support

- **Issues:** GitHub issues for bugs, suggestions, feedback
- **Questions:** See documentation files
- **Contributing:** See CONTRIBUTING.md
