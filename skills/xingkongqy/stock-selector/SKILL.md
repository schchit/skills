---
name: stock-selector
description: A 股选股工具 - 支持分阶段筛选、批量查询、自动化选股 (A-Share Stock Selector)
metadata:
  openclaw:
    emoji: "📈"
    category: finance
    tags: ["stock", "a-share", "selector", "finance", "china", "automation"]
    version: "0.3.0"
    author: "九章快手团队"
    license: "MIT"
---

# A 股选股工具 - stock-selector

**一键筛选 A 股股票，支持分阶段筛选、批量查询、自动化选股**

## ✨ 功能特点

- 📈 **分阶段筛选** - 4 阶段过滤，快速精准
- ⚡ **批量查询** - 100 只/批，效率提升 57 倍
- 🎯 **策略选股** - 支持一夜持股法等多种策略
- 📊 **候选池管理** - 自动维护 2000+ 股票池
- 🔧 **自动化** - cron 定时执行，无需人工干预
- 📝 **选股报告** - 自动生成选股结果报告

## 🚀 快速开始

### 安装

```bash
# 通过 ClawHub 安装
clawhub install stock-selector

# 或从 GitHub 安装
git clone https://github.com/xingkongqy/stock-selector.git
cd stock-selector
```

### 配置

```bash
# 配置候选池（可选）
export STOCK_POOL_FILE="/path/to/stock_pool.json"

# 配置输出目录
export STOCK_OUTPUT_DIR="./.stock"
```

### 一键选股

```bash
python3 stock_selector.py select \
  --strategy overnight \
  --output-dir .stock
```

## 📋 选股策略

### 一夜持股法（默认）

| 条件 | 标准 |
|------|------|
| **涨幅** | 3-7% |
| **成交额** | >1 亿 |
| **换手率** | 5-10% |
| **市值** | 50-200 亿 |
| **排除** | ST、涨停 |

### 分阶段筛选流程

```
候选池（2132 只）
    ↓ 第 1 阶段：涨跌幅 3-7%
43 只 (2%)
    ↓ 第 2 阶段：成交>1 亿
43 只 (100%)
    ↓ 第 3 阶段：换手 3-15%
26 只 (60%)
    ↓ 第 4 阶段：排除 ST/涨停
26 只 (100%)
    ↓
推荐：3 只
```

## 🔧 命令行工具

### 选股命令

```bash
# 一键选股
python3 stock_selector.py select \
  --strategy overnight \
  --output-dir .stock \
  --top 3

# 指定候选池
python3 stock_selector.py select \
  --pool stock_pool.json \
  --output result.json
```

### 更新候选池

```bash
# 更新股票池
python3 stock_selector.py update-pool \
  --min-market-cap 50 \
  --max-market-cap 200
```

### 查看选股结果

```bash
# 查看最新选股结果
python3 stock_selector.py show-result

# 导出选股报告
python3 stock_selector.py export-report --format markdown
```

## 📊 性能对比

| 版本 | API 调用 | 执行时间 | 提升 |
|------|----------|----------|------|
| **v4** | 2132 次 | >300 秒 | - |
| **v7** | 43 次 | 11.38 秒 | 26 倍 |
| **v8** | 22 次 | 5.21 秒 | 57 倍 |
| **v0.3** | 22 次 | ~5 秒 | 57 倍 |

## 📁 文件结构

```
stock-selector/
├── stock_selector.py         # 主程序
├── strategies/
│   ├── overnight.py          # 一夜持股法
│   └── breakout.py           # 突破策略
├── pool/
│   └── stock_pool.json       # 候选股票池
├── output/
│   └── results/              # 选股结果
├── tests/
│   └── test_selector.py      # 测试用例
└── docs/
    └── strategy.md           # 策略文档
```

## ⚠️ 注意事项

1. **数据延迟** - 实时数据可能有 15 分钟延迟
2. **风险提示** - 选股结果仅供参考，不构成投资建议
3. **API 限制** - 腾讯财经 API 有频率限制
4. **候选池更新** - 建议每周更新候选股票池

## 📄 策略说明

### 一夜持股法

**核心逻辑：** 选择当日强势股，次日冲高获利

**买入条件：**
- 涨幅 3-7%（当日强势）
- 成交额>1 亿（资金活跃）
- 换手率 5-10%（交投活跃）
- 市值 50-200 亿（中盘股）
- 排除 ST、涨停（风险控制）

**卖出规则：**
- 止盈：+3%
- 止损：-3%
- 持股时间：1 天（隔夜）
- 强制卖出：次日 10:00

## 🔗 数据源

| 数据 | 来源 | 说明 |
|------|------|------|
| **实时行情** | 腾讯财经 | qt.gtimg.cn |
| **候选股票池** | 本地维护 | 市值 50-200 亿 |
| **财务数据** | 本地缓存 | 定期更新 |

## 📝 使用示例

### 示例 1：日常选股

```bash
# 每日 14:40 执行选股
python3 stock_selector.py select --strategy overnight
```

### 示例 2：自定义策略

```bash
# 使用自定义策略
python3 stock_selector.py select \
  --strategy custom \
  --config my_strategy.json
```

### 示例 3：批量回测

```bash
# 回测历史选股效果
python3 stock_selector.py backtest \
  --start-date 2026-01-01 \
  --end-date 2026-03-01
```

## 🧪 测试

```bash
# 运行测试
python3 -m pytest tests/

# 或
npm test
```

## 📄 License

MIT License

Copyright (c) 2026 九章快手团队

---

*版本：0.3.0*  
*创建时间：2026-03-20*  
*作者：九章快手团队*
