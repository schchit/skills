---
name: ifind-mcp
description: 同花顺iFinD金融数据MCP工具。用于查询A股股票、公募基金、宏观经济和新闻资讯数据。当用户需要查询股票、基金、宏观经济指标或新闻资讯时使用。
---

# iFind MCP Skill

同花顺 iFinD MCP 服务，提供专业金融数据查询。

## 配置

### 配置文件位置
`~/.config/mcporter.json`

### MCP 服务器

| 服务器 | 用途 |
|--------|------|
| hexin-ifind-stock | A股股票数据 |
| hexin-ifind-fund | 公募基金数据 |
| hexin-ifind-edb | 宏观经济数据 |
| hexin-ifind-news | 公告资讯 |

## 调用方式

```bash
mcporter call <server>.<tool>

# 或使用便捷脚本
./scripts/query.sh stock "贵州茅台"
```

### 便捷脚本

```bash
./scripts/query.sh stock "贵州茅台"   # 股票查询
./scripts/query.sh fund "易方达"       # 基金查询
./scripts/query.sh edb "中国GDP"       # 宏观数据
./scripts/query.sh news "华为公告"      # 新闻资讯
```

## 股票工具 (hexin-ifind-stock)

| 工具 | 说明 |
|------|------|
| get_stock_summary | 股票信息摘要 |
| search_stocks | 智能选股 |
| get_stock_perfomance | 历史行情与技术指标 |
| get_stock_info | 基本资料查询 |
| get_stock_shareholders | 股本结构与股东数据 |
| get_stock_financials | 财务数据与指标 |
| get_risk_indicators | 风险指标 |
| get_stock_events | 公开披露事件 |
| get_esg_data | ESG评级 |

### 使用示例

```bash
mcporter call hexin-ifind-stock.get_stock_summary query:"贵州茅台财务状况"
mcporter call hexin-ifind-stock.search_stocks query:"新能源汽车行业市值大于1000亿"
mcporter call hexin-ifind-stock.get_stock_perfomance query:"宁德时代最近5日涨跌幅"
```

## 基金工具 (hexin-ifind-fund)

| 工具 | 说明 |
|------|------|
| search_funds | 模糊基金名称匹配 |
| get_fund_profile | 基金基本资料 |
| get_fund_market_performance | 行情与业绩 |
| get_fund_ownership | 份额与持有人结构 |
| get_fund_portfolio | 投资标的与资产配置 |
| get_fund_financials | 基金财务指标 |
| get_fund_company_info | 基金公司信息 |

### 使用示例

```bash
mcporter call hexin-ifind-fund.search_funds query:"易方达科技ETF"
mcporter call hexin-ifind-fund.get_fund_market_performance query:"富国天惠近一年收益率"
```

## 宏观/新闻工具

```bash
# 宏观经济
mcporter call hexin-ifind-edb.get_macro_data query:"中国GDP增速"

# 新闻资讯
mcporter call hexin-ifind-news.get_company_news query:"华为最新公告"
```

## 配置检查

```bash
mcporter list
```

## API 文档

详细 API 说明见 [references/API.md](references/API.md)
