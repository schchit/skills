---
name: stock_alert_workflow
version: 1.0.0
description: "超预期盈利提醒工作流：自动爬取财报EPS超预期>10%的标的，搜索近30天分析师评级，通过WhatsApp推送提醒"
author: ClawdBot
tags: ['stocks', 'earnings', 'alerts', 'whatsapp', 'workflow']
metadata:
  {
    "clawdbot":
      {
        "emoji": "📈",
        "requires": {"bins": ["uv"]},
        "install":
          [
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
          ],
      },
  }
---

# Stock Alert Workflow (超预期盈利提醒) v1.0.0

自动财报监控 + 分析师评级 + WhatsApp推送工作流

## 功能特点

1. **📊 财报超预期检测**
   - 自动监控S&P 500成分股财报
   - 检测EPS超预期幅度 > 10%的标的
   - 支持自定义阈值

2. **📈 分析师评级分析**
   - 自动获取标的近30天分析师评级
   - 统计Buy/Hold/Sell分布
   - 计算目标价平均上涨空间

3. **💬 WhatsApp推送**
   - 格式化消息推送
   - 包含完整分析摘要
   - 支持自定义接收人

## 快速开始

### 运行完整工作流

```bash
# 监控S&P 500所有股票（默认阈值10%）
uv run {baseDir}/scripts/stock_alert_workflow.py

# 监控特定股票
uv run {baseDir}/scripts/stock_alert_workflow.py AAPL MSFT NVDA

# 自定义超预期阈值
uv run {baseDir}/scripts/stock_alert_workflow.py --threshold 15.0
```

### 设置定时任务 (Cron)

每天盘后自动运行：

```bash
# 使用OpenClaw cron设置
cron add job --schedule "cron: 0 20 * * 1-5" --payload "agentTurn: uv run {baseDir}/scripts/stock_alert_workflow.py --cron"
```

## 输出示例

```
🚨 *EARNINGS ALERT* 🚨

*NVIDIA Corporation (NVDA)*

📊 *EPS Beat: +23.5%*
   • Expected: $4.50
   • Actual:   $5.56
   • Current Price: $875.28

📈 *Analyst Ratings (30 days)*:
   • Buy: 32 | Hold: 5 | Sell: 0
   • Average Upside: 15.2%

📋 *Top Ratings*:
   • Consensus (37 analysts): Buy | Target: $1008.50
   • Morgan Stanley: Buy
   • Goldman Sachs: Buy
   • JPMorgan: Overweight

---
⚠️ Not financial advice. DYOR.
```

## 工作流架构

```
┌─────────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│ 财报数据爬取    │───▶│ 分析师评级聚合       │───▶│ WhatsApp推送     │
│ (yfinance)      │    │ (过去30天评级)       │    │ (OpenClaw API)   │
└─────────────────┘    └─────────────────────┘    └──────────────────┘
       │                        │                        │
       ▼                        ▼                        ▼
  EPS超预期检测           Buy/Hold/Sell统计          富文本格式
  >10% 触发             目标价上涨空间计算           自动发送
```

## 配置选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--threshold` | EPS超预期触发阈值(%) | 10.0 |
| `--cron` | 静默模式（适合定时任务） | false |
| tickers | 指定要监控的股票代码 | S&P 500 |

## 数据来源

- **财报数据**: Yahoo Finance API
- **分析师评级**: Yahoo Finance + TipRanks
- **价格数据**: Yahoo Finance实时数据

## Whatsapp配置

确保OpenClaw WhatsApp通道已配置：
```
openclaw config plugins.entries.whatsapp
```

推送消息将自动通过配置的WhatsApp账号发送。

## 更新日志

### v1.0.0
- ✅ 初始版本发布
- ✅ 财报EPS超预期检测 (>10%触发)
- ✅ 近30天分析师评级爬取
- ✅ WhatsApp自动推送
- ✅ S&P 500自动扫描
