# jy-a-stock-earnings-review - A 股财报点评技能

基于聚源数据 MCP 接口（`gildata_datamap-sse`）生成专业 A 股上市公司财报点评报告。

## 快速开始

### 1. 环境配置

**安装 mcporter：**
```bash
npm install -g mcporter
```

**配置 MCP 服务（需要 JY_API_KEY）：**
```bash
# 配置 jy-financedata-tool 服务
mcporter config add jy-financedata-tool --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-tool?token=你的 JY_API_KEY"

# 配置 jy-financedata-api 服务
mcporter config add jy-financedata-api --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-api?token=你的 JY_API_KEY"
```

**验证配置：**
```bash
mcporter list
# 预期输出：jy-financedata-tool, jy-financedata-api
```

### 2. 使用技能

在 OpenClaw 中直接询问：
```
贵州茅台 财报点评
600519 业绩分析
宁德时代 2025 年报
```

### 3. 手动运行脚本

```bash
# 获取财务数据
cd scripts
python3 fetch_financial_data.py 300750 宁德时代 2025 2024 2023

# 生成报告
python3 generate_report.py 300750 ../reports/300750_financial_data.json
```

## 文件结构

```
jy-a-stock-earnings-review/
├── SKILL.md                 # 技能说明文档
├── README.md                # 本文件
├── requirements.txt         # Python 依赖
├── scripts/                 # 脚本工具
│   ├── fetch_financial_data.py    # 数据获取（使用 FinancialDataAPI）
│   ├── generate_report.py         # 报告生成
│   ├── generate_echarts.py        # 图表生成
│   └── extract_metrics.py         # 指标提取
├── references/              # 参考文档
│   ├── financial_metrics.md       # 财务指标定义
│   ├── research_report_template.md # 研报模板
│   ├── gildata_mcp_api.md         # MCP 接口文档
│   └── data-validation-checklist.md # 数据校验清单 ⭐
├── reports/                 # 生成的报告输出
└── assets/                  # 资源文件
```

## 获取 JY_API_KEY

向恒生聚源官方邮箱发送邮件申请：
- **邮箱：** datamap@gildata.com
- **标题：** 数据地图 KEY 申请 -XX 公司 - 申请人姓名

详见 SKILL.md "环境检查与配置" 章节。

## 输出示例

报告保存在 `reports/` 目录，格式为 Markdown，支持 echarts 图表渲染。

```
reports/
└── 300750_earnings_review_20260402.md
```

## ⚠️ 重要提醒

**使用前必须阅读：** `references/data-validation-checklist.md`

该文档包含：
- 历史数据错误教训（2026-04-02 宁德时代事件）
- 数据校验清单
- 正确的 MCP 工具调用方式
- 常见错误及避免方法
- **获取最新财报数据的逻辑** ⭐

**核心原则：**
1. 所有数据必须通过 MCP 实际查询，**禁止使用估计值**
2. 使用正确的服务名：`jy-financedata-tool`、`jy-financedata-api`
3. 使用正确的工具名：`FinancialDataAPI`（api 服务）、`MainOperIncData`（tool 服务）
4. 生成报告前必须核实关键数据（营收、利润、分业务收入等）
5. **必须获取最新报告期数据**（年报优先，季报降级）

---

## 📋 获取最新财报数据流程（必须严格执行）

**步骤 1：确定当前年份和报告期**
```bash
# 当前年份：2026 年
# 最新年报：2025 年年报（当前年份 -1）
# 最新季报：2025 年三季报/中报/一季报
```

**步骤 2：优先查询最新年报**
```bash
mcporter call jy-financedata-api.FinancialDataAPI query="公司名 股票代码 2025 年 年报 营业收入 净利润 归属于母公司所有者的净利润"
```

**⚠️ 关键验证：检查返回数据的 `date` 字段**
- 正确：`"date": "2025-12-31"`（2025 年年报）
- 错误：`"date": "2018-12-31"`（旧数据，说明 2025 年年报不存在）
- 如为旧数据，必须降级查询最新季报

**步骤 3：如年报无数据，查询最新季报**
```bash
# 按优先级：三季报 > 中报 > 一季报
# 1. 先查询三季报（10 月 - 次年 3 月可用）
mcporter call jy-financedata-api.FinancialDataAPI query="公司名 股票代码 2025 年 三季报 营业收入 净利润"

# 2. 如三季报无数据，查询中报（7 月 -9 月可用）
mcporter call jy-financedata-api.FinancialDataAPI query="公司名 股票代码 2025 年 中报 营业收入 净利润"

# 3. 如中报无数据，查询一季报（4 月 -6 月可用）
mcporter call jy-financedata-api.FinancialDataAPI query="公司名 股票代码 2025 年 一季报 营业收入 净利润"
```

**步骤 4：获取上年同期数据**
```bash
# 根据最新报告期，获取上年同期数据计算同比增速
# 如最新为 2025 年三季报，则获取 2024 年三季报
mcporter call jy-financedata-api.FinancialDataAPI query="公司名 股票代码 2024 年 三季报 营业收入 净利润"
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

## 注意事项

- 所有 MCP 工具调用统一使用 `query` 参数
- 数据延迟至少 15 分钟（非实时）
- 不构成投资建议，仅供参考
