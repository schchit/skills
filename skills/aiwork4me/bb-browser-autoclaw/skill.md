---
name: bb-browser
description: "Turn any website into a CLI command. 36+ platforms, 100+ commands — Twitter, Reddit, GitHub, YouTube, Zhihu, Bilibili, Weibo, and more. Fetch structured JSON data from any website using your browser login state. No API keys needed."
requires:
  bins: bb-browser
allowed-tools: Bash(bb-browser:*)
---

# bb-browser — Your Browser is the API

**Core idea**: Instead of configuring API keys, bb-browser reuses your browser's login state. You're logged into Twitter, Reddit, Zhihu? bb-browser uses that directly.

## ⚡ Quick Start

```bash
npm install -g bb-browser
bb-browser site update                  # Pull community adapters

# Use with OpenClaw's browser (--openclaw flag, no extension needed)
bb-browser site hackernews/top 5 --openclaw
bb-browser site zhihu/hot --openclaw
bb-browser site weibo/hot --openclaw
bb-browser site twitter/search "AI Agent" --openclaw
bb-browser site reddit/hot --openclaw
```

If `--openclaw` commands time out, ensure `openclaw browser status` reports `running: true`.

## 🌐 Site System — The Web as CLI

### Commands

```bash
bb-browser site update              # Pull community adapters
bb-browser site list                # List all adapters
bb-browser site search <query>      # Search adapters by keyword
bb-browser site info <name>         # View adapter details and args
bb-browser site recommend           # Recommend based on browsing habits
bb-browser site <name> [args...] --openclaw  # Run adapter
```

### Platform Coverage (36 platforms, 100+ commands)

| Category | Platforms |
|----------|-----------|
| **Search** | Google, Baidu, Bing, DuckDuckGo, Sogou WeChat |
| **Social** | Twitter/X, Reddit, Weibo, Xiaohongshu, Jike, LinkedIn, Hupu |
| **News** | BBC, Reuters, 36kr, Toutiao, Eastmoney |
| **Dev** | GitHub, StackOverflow, HackerNews, CSDN, cnblogs, V2EX, Dev.to, npm, PyPI, arXiv |
| **Video** | YouTube, Bilibili |
| **Finance** | Xueqiu, Eastmoney, Yahoo Finance |
| **Jobs** | BOSS Zhipin, LinkedIn |
| **Knowledge** | Wikipedia, Zhihu, Open Library |
| **Tools** | Youdao, GSMArena, Product Hunt, Ctrip |

### Common Usage

```bash
# Social
bb-browser site twitter/search "OpenClaw" --openclaw
bb-browser site twitter/tweets elonmusk --count 5 --openclaw --json
bb-browser site reddit/hot --openclaw
bb-browser site weibo/hot --openclaw

# Dev
bb-browser site github/repo owner/repo --openclaw
bb-browser site hackernews/top 10 --openclaw
bb-browser site arxiv/search "transformer" --openclaw
bb-browser site npm/package bb-browser --openclaw

# Finance
bb-browser site xueqiu/stock SH600519 --openclaw
bb-browser site eastmoney/stock "茅台" --openclaw

# News & Knowledge
bb-browser site zhihu/hot --openclaw
bb-browser site 36kr/newsflash --openclaw
bb-browser site wikipedia/summary "Python" --openclaw

# Video
bb-browser site youtube/transcript VIDEO_ID --openclaw
bb-browser site bilibili/popular --openclaw
```

### Data Filtering with --jq

```bash
bb-browser site xueqiu/hot-stock 5 --openclaw --jq '.items[] | {name, changePercent}'
bb-browser site reddit/hot --openclaw --jq '.posts[] | {title, score}'
bb-browser site xueqiu/hot-stock 5 --openclaw --jq '.items[].name'
```

### Login State

Adapters run inside browser tabs. If a site requires login:

1. Adapter returns `{"error": "HTTP 401", "hint": "Not logged in?"}`
2. Open the site: `openclaw browser open https://twitter.com`
3. Complete login manually
4. Retry the bb-browser command

## 🖥️ Browser Automation

For tasks beyond site adapters:

### Core Workflow

```bash
bb-browser open https://example.com    # 1. Open page
bb-browser snapshot -i                 # 2. Get interactive elements
bb-browser click @5                    # 3. Interact
bb-browser snapshot -i                 # 4. Re-snapshot after changes
bb-browser get text @5                 # 5. Extract data
bb-browser close                       # 6. Clean up
```

### Command Reference

**Navigation**: `open <url>`, `open <url> --tab current`, `back`, `forward`, `refresh`, `close`

**Snapshot**: `snapshot -i` (interactive only, recommended), `snapshot -i -c` (compact), `snapshot -i -d 3` (depth limit), `snapshot -s ".main"` (scoped)

**Interaction**: `click @N`, `hover @N`, `fill @N "text"`, `type @N "text"`, `select @N "option"`, `press Enter`, `scroll down`

**Data**: `get text @N`, `get url`, `get title`, `screenshot`

**Tabs**: `tab` (list), `tab new [url]`, `tab N` (switch by index), `tab close`

### Ref Best Practices

- Page navigation invalidates refs — always re-snapshot after clicks/redirects
- Dynamic content — `wait 1000` then re-snapshot
- Use `-i` flag to filter to interactive elements only
- Elements not showing? — try `scroll down` then re-snapshot

### Extracting Article Text

For long text, `get text` is more efficient than snapshot:

```bash
bb-browser get text @5
bb-browser snapshot -s ".article-content"
```

## 🐛 Known Issues

| Issue | Details |
|-------|---------|
| Xiaohongshu adapters | Results may be unreliable due to caching |
| CORS restrictions | Some public APIs may be blocked in browser context |
| Gateway timeout | Default 120s; reduce `--count` for complex queries |
| China firewall | x.com requires proxy in browser |

### Verified Adapters

| Platform | Adapter | Status |
|----------|---------|--------|
| HackerNews | hackernews/top | ✅ |
| Twitter/X | twitter/tweets, twitter/search | ✅ |
| Reddit | reddit/hot, reddit/thread | ✅ |
| Zhihu | zhihu/hot | ✅ (needs login) |
| Weibo | weibo/hot | ✅ |
| GitHub | github/repo, github/issues | ✅ |

## 📖 Custom Adapters

```bash
bb-browser guide  # Full tutorial
```

Three tiers of complexity:
- **Tier 1** (~1 min): Public or cookie-based fetch
- **Tier 2** (~3 min): Bearer token + CSRF header
- **Tier 3** (~10 min): Webpack module discovery

Private adapters: `~/.bb-browser/sites/` (priority). Community: `~/.bb-browser/bb-sites/`.
