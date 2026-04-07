---
name: gold-daily-report
description: "每日金价快报 - 国际现货(XAU/USD) + 国内Au99.99 + 近期资讯。运行 scripts/gold_report.js 获取报告并发送给用户。"
---

# Gold Daily Report

## Overview

每日金价快报 skill。拉取国际+国内金价数据，附带简要资讯，适合定时推送。

## Data Sources
- **国际金价**: gold-api.com (XAU/USD)
- **国内金价**: 东方财富 (上海金交所 Au99.99)
- **汇率**: er-api.com (USD/CNY)
- **资讯**: 东方财富财经频道

## Output Format

```
💰 金价日报 | YYYY/M/D HH:MM

━━━ 国际金价 ━━━
XAU/USD: XXXX.00 美元/盎司
  换算: XXX.00 元/克
汇率(USD/CNY): X.XXXX

━━━ 国内金价 ━━━
Au99.99: XXXX.XX 元/克  涨跌: X.XX%
  最高: XXXX.XX  最低: XXXX.XX  昨收: XXXX.XX
  成交额: XX.00亿元

🌍 国际金价分析
📊 国内溢价/折价分析

━━━ 近期资讯 ━━━
1. 新闻标题1
2. 新闻标题2
...

📌 数据来源: gold-api.com | 东方财富 | er-api.com
```

## Usage

### Manual Run

```bash
node <skill-dir>/scripts/gold_report.js
```

### Via Cron (Daily at 9:00 AM)

```bash
openclaw cron add \
  --name "金价日报" \
  --cron "0 9 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "运行 gold-daily-report skill 的脚本获取金价报告，发送给飞书用户" \
  --announce \
  --channel feishu
```

### Programmatically (Agent)

When triggered by a heartbeat or cron, execute the script and send the report:

1. Run `node <skill-dir>/scripts/gold_report.js`
2. Capture output
3. Send to user via preferred channel (feishu, telegram, etc.)

## Notes

- All API calls are free, no authentication required
- Script is written in Node.js (no external dependencies)
- Falls back gracefully if any data source fails
- Works well as a cron job but can be run manually anytime
