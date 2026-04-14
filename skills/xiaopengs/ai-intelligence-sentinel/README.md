<div align="center">

# 🔭 AI Sentinel

**Your AI Intelligence Command Center**

*Automatically collect, analyze, and report the latest AI developments*

**One command to track everything happening in AI — GitHub trends, arXiv papers, tech news, and more.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Stars](https://img.shields.io/github/stars/xiaopengs/ai-sentinel?style=social)](https://github.com/xiaopengs/ai-sentinel)

🌐 [Project Showcase](http://thinkspc.fun/static/sentinel/) · 📦 [ClawHub](https://clawhub.ai/skills/ai-intelligence-sentinel) · 🇨🇳 [中文文档](./README_CN.md)

</div>

---

## 🎯 What You Get

| For Product Managers | For Developers | For Executives |
|:---:|:---:|:---:|
| 📊 Daily AI industry reports delivered automatically | 🔧 15+ data sources in one place | 📈 Track AI landscape without manual effort |
| 🔍 Discover trending projects before competitors | 💻 CLI tools + WebUI for full control | 📋 Executive summary in every report |
| ⏰ Morning & evening reports on schedule | 🛠️ Customizable sources & templates | 🎯 Quality-scored content only |

---

## ⚡ Quick Start (30 Seconds)

### Option 1: Chat Install (Recommended)

**Step 1: Install the skill**

Copy and send to any AI assistant that supports ClawHub (OpenClaw, WorkBuddy, QClaw, etc.):

```
安装 ClawHub 和技能 请先检查是否已安装 ClawHub 商店，若未安装，请安装 npm i -g clawhub ，然后安装 ai-intelligence-sentinel 技能。
```

Or via ClawHub CLI:
```bash
npx clawhub@latest install ai-intelligence-sentinel
```

**Step 2: Use the skill**

After installation, trigger with the skill name:
```
使用 ai-intelligence-sentinel 技能生成今日AI情报报告
```

Or simply:
```
ai-intelligence-sentinel 生成今日报告
```

### Option 2: Command Line

```bash
# Install
pip install requests feedparser pyyaml jinja2

# Run - Generate a complete AI report now
python scripts/reporter.py --type full
```

**That's it.** Your first report is at `reports/YYYY-MM-DD/full_report_*.md`

<details>
<summary>📖 Full Installation</summary>

```bash
# Clone the project
git clone https://github.com/xiaopengs/ai-sentinel.git
cd ai-sentinel

# Install dependencies
pip install requests feedparser pyyaml jinja2

# Generate report (collects + analyzes + generates)
python scripts/reporter.py --type full
```

</details>

---

## ✨ Core Features

<table>
<tr>
<td width="50%">

### 🔍 Multi-Source Collection
- **GitHub Trending** — AI open-source projects
- **arXiv** — Latest papers (cs.AI, cs.LG, cs.CL)
- **HackerNews** — Developer discussions
- **15+ RSS Feeds** — OpenAI, Anthropic, Google AI, DeepMind, etc.
- **Chinese AI Companies** — 智谱AI, MiniMax, Coze

</td>
<td width="50%">

### 📊 Intelligent Analysis
- **Popularity Score** — Stars, forks, comments
- **Freshness Weight** — Newer = higher rank
- **Source Credibility** — Official blogs > Media > Community
- **Quality Scoring** — Content depth & completeness

</td>
</tr>
<tr>
<td width="50%">

### 📄 Automated Reports
- **Morning Report** — Overnight highlights (8:00 AM)
- **Evening Report** — Full-day summary (8:00 PM)
- **Full Report** — Complete collection + analysis
- **Multiple Formats** — Markdown, Xiaohongshu style

</td>
<td width="50%">

### 🎛️ Easy Management
- **WebUI** — Visual configuration panel
- **CLI** — Full command-line control
- **Scheduled Tasks** — Set and forget
- **Custom Templates** — Tailor to your needs

</td>
</tr>
</table>

---

## 📋 Usage

### Most Common Commands

| What You Want | Command |
|---------------|---------|
| **Generate complete report now** ⭐ | `python scripts/reporter.py --type full` |
| Collect from all sources | `python scripts/collect.py --all` |
| Generate morning report | `python scripts/reporter.py --type morning` |
| Generate evening report | `python scripts/reporter.py --type evening` |
| Track GitHub only | `python scripts/collect.py --source github` |
| Track arXiv papers | `python scripts/collect.py --source arxiv` |

### Report Types

| Type | What It Does | Best For |
|------|--------------|----------|
| `--type full` | Collect → Analyze → Generate | Immediate insights ⭐ |
| `--type morning` | Generate morning report | Scheduled tasks |
| `--type evening` | Generate evening report | Scheduled tasks |

---

## 📰 Information Sources

| Category | Sources | Coverage |
|----------|---------|----------|
| **Open Source** | GitHub Trending | AI/ML projects |
| **Academic** | arXiv | cs.AI, cs.LG, cs.CL |
| **Community** | HackerNews | Developer discussions |
| **Official Blogs** | OpenAI, Anthropic, Google AI, DeepMind, HuggingFace, xAI, Cursor | First-party announcements |
| **Tech Media** | InfoQ (Global/CN), TechCrunch AI, VentureBeat AI | Industry news |
| **Chinese AI** | 智谱AI, MiniMax, 扣子Coze | Domestic developments |

---

## 📊 Sample Report

**2026-04-12 Evening Report**

```markdown
📰 Today's Headlines (P0)

### GPT-6 Announced for April 14 — 2M Token Context
OpenAI confirms GPT-6 release with 200万 tokens context window...

### DeepSeek V4 Scheduled for Late April — Trillion Parameters
First Chinese model to fully adapt to domestic chips...

🚀 Major Releases (P1)
• ByteDance Seeduplex — Full-duplex voice model
• Zhipu GLM-5.1 Open Source — Strongest open-source model
• Meta Muse Spark — $14.3B investment, going closed-source

📊 Stats: 23 items collected · 3 major announcements
```

---

## 🏗️ Project Structure

```
ai-sentinel/
├── scripts/
│   ├── collect.py          # Data collection
│   ├── reporter.py         # Report generation
│   └── parsers/            # Source parsers
├── config/
│   ├── sources.yaml        # Source configuration
│   └── schedule.yaml       # Scheduling config
├── templates/              # Report templates
├── webui/                  # Web management panel
└── reports/                # Generated reports
```

---

## 📦 Install from ClawHub

```bash
npx clawhub@latest install ai-intelligence-sentinel
```

---

## 🔗 Links

| Resource | Link |
|----------|------|
| 📚 Documentation | [README_CN.md](./README_CN.md) |
| 🌐 Project Showcase | [thinkspc.fun/static/sentinel](http://thinkspc.fun/static/sentinel/) |
| 📦 ClawHub | [clawhub.ai/skills/ai-intelligence-sentinel](https://clawhub.ai/skills/ai-intelligence-sentinel) |
| 🦐 Xiaping Skill | [xiaping.coze.site](https://xiaping.coze.site/skill/08037f81-1e91-4115-80ad-2e2c1d0681d2) |
| 💻 GitHub | [xiaopengs/ai-sentinel](https://github.com/xiaopengs/ai-sentinel) |

---

## 🤝 Contributing

Contributions welcome! Feel free to submit Issues or Pull Requests.

---

## 📄 License

MIT License — use it freely in your projects.

---

## 📝 Changelog

### v1.3.0 (2026-04-12)
- ✨ Added `--type full` for one-command complete report
- Optimized report workflow

### v1.2.0 (2026-04-12)
- 📝 Refactored documentation
- Added project showcase

### v1.0.0 (2026-04-10)
- 🎉 Initial release

---

<div align="center">

**Built for AI practitioners who need to stay ahead.**

⭐ Star this repo if you find it useful!

</div>
