# Stock Alert Workflow - 超预期盈利提醒工作流

📈 自动财报监控 + 分析师评级 + WhatsApp推送

## 功能概述

这是一个自动化的股票财报监控工作流，当爬取到财报EPS超预期幅度超过10%的标的时，自动搜索该股票近30天的分析师评级，整理结果后通过WhatsApp推送提醒。

### 核心功能

1. **🔍 财报超预期检测** - 自动检测EPS超预期>10%的股票
2. **📊 分析师评级分析** - 汇总近30天Buy/Hold/Sell评级分布
3. **💬 WhatsApp推送** - 格式化消息自动推送到指定联系人
4. **⏰ 定时任务支持** - 可配置为每日盘后自动运行

## 安装

### 通过 ClawHub 安装 (推荐)

```bash
clawhub install stock_alert_workflow
```

### 手动安装

```bash
cd ~/.openclaw/skills
git clone <repository-url> stock_alert_workflow
cd stock_alert_workflow
```

## 使用方法

### 基础使用

```bash
# 监控S&P 500所有股票
uv run scripts/stock_alert_workflow.py

# 监控特定股票
uv run scripts/stock_alert_workflow.py AAPL MSFT NVDA TSLA

# 自定义超预期阈值为15%
uv run scripts/stock_alert_workflow.py --threshold 15.0
```

### 配置定时任务

使用OpenClaw cron设置每日盘后自动检查：

```bash
# 周一至周五，美国东部时间下午4点（北京时间凌晨4点）运行
openclaw cron add
```

然后配置：
- Schedule: `0 20 * * 1-5` (每天20:00 UTC)
- Payload: `uv run ~/.openclaw/skills/stock_alert_workflow/scripts/stock_alert_workflow.py --cron`

## 技术栈

- **Python 3.10+**
- **yfinance** - Yahoo Finance API
- **pandas** - 数据处理
- **uv** - 包管理
- **OpenClaw Message API** - WhatsApp推送

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
```

## 注意事项

⚠️ **免责声明**: 本工具仅供参考，不构成任何投资建议。股市有风险，投资需谨慎。

- 数据来源为公开API，准确性不做保证
- 延迟可能存在，实际交易请以官方数据为准
- WhatsApp推送需要配置OpenClaw对应通道

## License

MIT
