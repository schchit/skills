# 聚源数据 MCP 接口文档

## 接口配置

**服务配置（通过 mcporter）：**
- **jy-financedata-tool:** `https://api.gildata.com/mcp-servers/aidata-assistant-srv-tool?token=你的 JY_API_KEY`
- **jy-financedata-api:** `https://api.gildata.com/mcp-servers/aidata-assistant-srv-api?token=你的 JY_API_KEY`

**认证方式：** Token 认证（JY_API_KEY）

**配置命令：**
```bash
mcporter config add jy-financedata-tool --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-tool?token=你的 JY_API_KEY"
mcporter config add jy-financedata-api --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-api?token=你的 JY_API_KEY"
```

**验证配置：**
```bash
mcporter list
# 预期输出：jy-financedata-tool, jy-financedata-api
```

## 可用工具

**主要工具列表：**

| 工具名称 | 用途 | 使用服务 | 示例 |
|---------|------|---------|------|
| `FinancialDataAPI` | 获取财务报表数据（利润表、资产负债表、现金流量表、财务指标） | jy-financedata-api | 营收、净利润、毛利率等 |
| `MainOperIncData` | 获取主营构成数据（分产品/行业/地区收入、利润） | jy-financedata-tool | 动力电池收入、储能收入等 |

## 工具调用方式

**使用 mcporter call 命令（所有工具统一使用 query 参数）：**
```bash
# 基础格式
mcporter call 服务名称。工具名称 query="查询内容"

# 示例：获取财务数据（使用 jy-financedata-api）
mcporter call jy-financedata-api.FinancialDataAPI query="贵州茅台 600519 2025 年 年报 营业收入 净利润"

# 示例：获取主营构成（使用 jy-financedata-tool）
mcporter call jy-financedata-tool.MainOperIncData query="贵州茅台 600519 2025 年 分产品 主营业务收入"
```

## 调用示例

### 🎯 获取最新财报数据（标准流程 - 必须严格执行）

**⚠️ 重要教训（2026-04-02 明阳电气案例）：**
- 查询 2025 年年报时，返回的 `date` 字段为 "2018-12-31"，说明 2025 年年报数据不存在
- 必须降级查询 2025 年三季报，`date` 字段为 "2025-09-30"，确认是最新数据
- 在报告中必须明确标注数据截止日期和报告期类型

---

**步骤 1：确定当前年份和报告期**
```bash
# 当前年份：2026 年
# 最新年报：2025 年年报（当前年份 -1）
# 最新季报：2025 年三季报/中报/一季报
```

**步骤 2：优先查询最新年报**
```bash
# 先尝试获取最新年报数据（当前年份 -1）
mcporter call jy-financedata-api.FinancialDataAPI query="宁德时代 300750 2025 年 年报 营业收入 净利润 归属于母公司所有者的净利润"
```

**⚠️ 关键验证：检查返回数据的 `date` 字段**
```json
// ✅ 正确：2025 年年报存在
{
  "date": "2025-12-31",
  "reportdate": "年报",
  "financevalue": "4237.02"
}

// ❌ 错误：2025 年年报不存在，返回旧数据
{
  "date": "2018-12-31",  // ⚠️ 这是 2018 年数据，不是 2025 年！
  "reportdate": "年报",
  "financevalue": "0.20"
}
```

**如 `date` 字段显示为多年前，说明该年报数据不存在，必须降级查询最新季报！**

**步骤 3：如年报无数据，查询最新季报**
```bash
# 按优先级查询：三季报 > 中报 > 一季报

# 3.1 先查询三季报（10 月 - 次年 3 月可用）
mcporter call jy-financedata-api.FinancialDataAPI query="宁德时代 300750 2025 年 三季报 营业收入 净利润"

# 3.2 如三季报无数据，查询中报（7 月 -9 月可用）
mcporter call jy-financedata-api.FinancialDataAPI query="宁德时代 300750 2025 年 中报 营业收入 净利润"

# 3.3 如中报无数据，查询一季报（4 月 -6 月可用）
mcporter call jy-financedata-api.FinancialDataAPI query="宁德时代 300750 2025 年 一季报 营业收入 净利润"
```

**步骤 4：获取上年同期数据用于对比**
```bash
# 根据最新报告期，获取上年同期数据计算同比增速
# 如最新为 2025 年三季报，则获取 2024 年三季报
mcporter call jy-financedata-api.FinancialDataAPI query="宁德时代 300750 2024 年 三季报 营业收入 净利润"
```

**步骤 5：验证数据时效性（必须执行）**
- [ ] 检查返回数据的 `date` 字段，确认是最新报告期（如 2025-09-30）
- [ ] 如 `date` 字段显示为多年前（如 2018-12-31），说明数据不存在，必须降级
- [ ] 在报告中明确标注报告期类型（年报/三季报/中报/一季报）
- [ ] 在报告中标注数据截止日期（如 2025-09-30）

**步骤 6：在报告中标注数据来源和报告期**
```markdown
**数据来源：** 聚源数据（jy-financedata-api、jy-financedata-tool）、公司公告
**数据截止日期：** 2025-09-30
**报告期：** 2025 年三季报
```

---

### 财务报表数据（使用 jy-financedata-api）

```bash
# 获取利润表数据（营业收入、净利润、归母净利润）
mcporter call jy-financedata-api.FinancialDataAPI query="宁德时代 300750 2025 年 年报 营业收入 净利润 归属于母公司所有者的净利润"

# 获取资产负债表数据
mcporter call jy-financedata-api.FinancialDataAPI query="宁德时代 300750 2025 年 年报 总资产 总负债 净资产"

# 获取现金流量表数据
mcporter call jy-financedata-api.FinancialDataAPI query="宁德时代 300750 2025 年 年报 经营现金流 投资现金流 筹资现金流"

# 获取财务指标（毛利率、净利率、费用率）
mcporter call jy-financedata-api.FinancialDataAPI query="宁德时代 300750 2025 年 年报 毛利率 净利率 销售费用 管理费用 研发费用"
```

### 主营构成数据（使用 jy-financedata-tool）

```bash
# 获取分产品收入
mcporter call jy-financedata-tool.MainOperIncData query="宁德时代 300750 2025 年 分产品 主营业务收入 动力电池 储能"

# 获取分行业收入
mcporter call jy-financedata-tool.MainOperIncData query="宁德时代 300750 2025 年 分行业 主营业务收入"

# 获取分地区收入
mcporter call jy-financedata-tool.MainOperIncData query="宁德时代 300750 2025 年 分地区 主营业务收入 国内 国外"
```

### 盈利预测与舆情（使用 jy-financedata-api）

```bash
# 获取盈利预测
mcporter call jy-financedata-api.FinancialDataAPI query="宁德时代 300750 盈利预测 一致预期 目标价"

# 获取股票舆情/新闻
mcporter call jy-financedata-api.FinancialDataAPI query="宁德时代 300750 最近 90 天 新闻 舆情"

# 获取公司公告
mcporter call jy-financedata-api.FinancialDataAPI query="宁德时代 300750 最近 90 天 公告 财报公告"
```

## 响应数据格式

**标准响应包含：**
- `table_markdown`: Markdown 格式的表格数据
- `origin_data`: 原始 JSON 数据
  - `rows`: 数据行数组
  - `columnmeta`: 列元数据
  - `nlpcolumnname`: 中文列名映射

**示例响应（利润表数据）：**
```json
{
  "code": 0,
  "results": [
    {
      "api_name": "财务报表",
      "table_markdown": "|股票名称 | 股票代码 | 时间 | 报告期 | 财务科目名称 | 财务科目数额 | 同比 (%)|展示单位|\n|---|---|---|---|---|---|---|---|\n|宁德时代|300750|2025-12-31|年报 | 营业收入|4237.02|17.04|亿元|\n|宁德时代|300750|2025-12-31|年报 | 净利润|767.86|42.18|亿元|",
      "origin_data": {
        "rows": [
          {
            "stockname": "宁德时代",
            "stockcode": "300750",
            "date": "2025-12-31",
            "reportdate": "年报",
            "finstatementsubject": "营业收入",
            "financevalue": "4237.02",
            "yoy": "17.04",
            "unit": "亿元"
          }
        ]
      }
    }
  ]
}
```

## 注意事项

1. **所有工具统一使用 `query` 参数**，不支持其他参数名
2. **查询语句使用自然语言**，包含：公司名、股票代码、年份、报告期、所需指标
3. **服务区分**：
   - `jy-financedata-api`：财务数据、财务指标、盈利预测等
   - `jy-financedata-tool`：主营构成数据
4. **数据延迟**：财报数据延迟至少 15 分钟（非实时）
5. **JY_API_KEY**：需向恒生聚源申请（datamap@gildata.com）

## 错误处理

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `Unknown tool` | 工具名称错误 | 使用 `FinancialDataAPI` 或 `MainOperIncData` |
| `No servers listed` | 服务未配置 | 运行 `mcporter config add jy-financedata-tool/api --url="..."` |
| 空响应 | 查询语句不清晰 | 完善 query，包含公司名、代码、年份、指标 |

---

**更新日期：** 2026-04-02
