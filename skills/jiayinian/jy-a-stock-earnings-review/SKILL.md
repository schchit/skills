---
name: jy-a-stock-earnings-review
description: 生成 A 股上市公司财报点评报告。基于聚源数据 MCP 接口（通过 mcporter 调用）获取财务数据、行业指标、舆情资讯、估值数据，结合 echarts 图表可视化，按券商研报风格撰写财报点评。使用场景：当用户需要分析 A 股上市公司财报、生成业绩点评报告、查看财务数据分析、了解某公司股票业绩表现时触发。触发词：财报点评、业绩分析、财报报告、财务分析、XX 公司财报、股票代码 + 财报/业绩、XX 股票业绩、上市公司财报分析。Generate A-share listed company earnings review reports via GILData MCP (using mcporter calls), fetching financial data, industry metrics, sentiment analysis, and valuation data. Creates professional research reports with echarts visualizations in broker analyst style. Trigger on earnings analysis requests, financial report reviews, stock performance queries.
metadata:
  openclaw:
    requires:
      bins: ["node", "npm", "mcporter"]
    install:
      - id: install-mcporter
        kind: node
        package: mcporter
        label: Install mcporter via npm
---

# 【A 股财报点评报告】

本技能基于聚源数据 MCP 接口生成专业 A 股上市公司财报点评报告，严格按照券商研报风格撰写，包含财务数据分析、8 个 echarts 图表可视化、风险提示和投资建议。所有数据通过 mcporter 调用获取，可溯源、带时间戳。

**详细文档：** 报告结构、图表规范、行文风格详见 `references/research_report_template.md`。

## 功能范围

- 生成 A 股上市公司财报点评报告（Markdown 格式，支持 echarts 渲染）
- 覆盖 6 大核心章节：公司整体情况、分业务分析、盈利能力与费用分析、经营展望、风险提示、投资建议
- 自动生成 8 个标准化 echarts 图表（营收、利润、毛利率、费用率等）
- 支持指定股票代码或公司名称查询
- 支持指定报告期（默认最新报告期）
- 所有数据标注来源和截止日期

## 查询建议

**查询要素：**
- 必须：公司名称或股票代码（如"贵州茅台"、"600519"）
- 可选：报告期（如"2025 年报"、"2026 年中报"，**默认获取最新报告期**）
- 可选：特殊分析重点（如"重点关注毛利率"、"分析现金流"）

**查询写法：**
- `<公司名/股票代码> + 财报/业绩/财报点评`
- `分析<公司名> 的财务数据`
- `<股票代码> 最新报告期业绩`

**报告期优先级：**
1. 最新年报（如 2025 年年报）
2. 最新季报（如 2025 年三季报/中报/一季报）
3. 如用户指定则使用指定报告期

## 查询示例

```
贵州茅台 财报点评
600519 业绩分析
000858 五粮液 2025 年报
分析宁德时代的盈利能力
300750 最新财报数据
```

## 环境检查与配置

**每次使用本技能前，必须先检查 mcporter 安装和 MCP 服务配置状态！**

### 步骤 1：检查 mcporter 是否安装

```bash
mcporter --version
```

**如未安装**，按以下流程安装：

```bash
# 1. 通过 npm 全局安装
npm install -g mcporter

# 2. 验证安装
mcporter --version
```

### 步骤 2：检查 MCP 服务配置

```bash
# 列出所有已配置的 MCP 服务
mcporter list
```

**预期输出**（必须包含以下两个服务）：
- jy-financedata-tool
- jy-financedata-api

**如服务未配置**，需要获取 JY_API_KEY 并配置：

1. **获取 JY_API_KEY**（首次配置需提供，配置一次即可）

向恒生聚源官方邮箱发送邮件申请签发数据地图 JY_API_KEY，用于接口鉴权。申请通过后，恒生聚源将默认发送【工具版和接口版】KEY。

**申请邮箱：** datamap@gildata.com

**邮件标题：** 数据地图 KEY 申请 -XX 公司 - 申请人姓名

**正文模板：**
- 姓名：
- 手机号：
- 公司/单位全称：
- 所属部门：
- 岗位：
- MCP_KEY 申请用途：
- Skill 申请列表：
- 是否需要 Skill 安装包：（是，邮件提供/否，自行下载）
- 其他补充说明（可选）：

2. **配置 MCP 服务**：

```bash
# 配置 jy-financedata-tool 服务
mcporter config add jy-financedata-tool --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-tool?token=你的 JY_API_KEY"

# 配置 jy-financedata-api 服务
mcporter config add jy-financedata-api --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-api?token=你的 JY_API_KEY"
```

3. **验证配置**：

```bash
mcporter list
```

4. **使用方式**：
```bash
# 基础调用格式（所有工具统一使用 query 参数）
mcporter call 服务名称。工具 query="查询内容"

# 示例：获取财务数据（使用 jy-financedata-api 服务）
mcporter call jy-financedata-api.FinancialDataAPI query="贵州茅台 600519 2025 年 年报 营业收入 净利润"

# 示例：获取主营构成（使用 jy-financedata-tool 服务）
mcporter call jy-financedata-tool.MainOperIncData query="贵州茅台 600519 2025 年 分产品 主营业务收入"
```

### 步骤 3：在 OpenClaw 中启用 mcporter（如未配置）

**mcporter 配置文件路径：**
- Linux/MacOS: `/root/config/mcporter.json` 或 `~/.config/mcporter.json`
- Windows: `C:\Users\你的用户名\config\mcporter.json`

**OpenClaw 配置文件路径：**
- Linux/MacOS: `~/.openclaw/openclaw.json`
- Windows: `C:\Users\你的用户名\.openclaw\openclaw.json`

**编辑 openclaw.json**，在 skills 部分添加 mcporter 配置：

```json
{
  "skills": {
    "entries": {
      "mcporter": {
        "enabled": true,
        "env": {
          "MCPORTER_CONFIG": "/root/config/mcporter.json"
        }
      }
    }
  }
}
```

**重启 OpenClaw 使配置生效**：

```bash
openclaw gateway restart
```

## 核心工作流程

流程中所有 MCP 工具调用均使用 `mcporter call` 命令，能够并发的调用尽量并发执行以提升速度。

### 步骤 1：解析用户请求

- **标的识别**：从用户 query 中提取公司名称或股票代码
- **报告期确认**：默认获取最新报告期，如用户指定则使用指定报告期
- **特殊需求**：识别用户是否有特殊分析重点

### 步骤 2：数据获取（通过 mcporter 调用聚源 MCP 接口）

**🎯 获取最新财报数据的标准流程（必须严格执行）：**

**第一步：确定当前年份和报告期**
```bash
# 获取当前年份（如 2026 年）
# 最新年报应为：当前年份 - 1（如 2025 年年报）
# 最新季报应为：当前年份的最新季度（如 2025 年三季报/中报/一季报）
```

**第二步：优先查询最新年报**
```bash
# 先尝试获取最新年报数据（当前年份 -1）
mcporter call jy-financedata-api.FinancialDataAPI query="公司名 股票代码 2025 年 年报 营业收入 净利润 归属于母公司所有者的净利润"
```

**⚠️ 关键验证：检查返回数据的 `date` 字段**
- 如果 `date` 字段显示为多年前（如 2018 年），说明该年报数据不存在
- 必须降级查询最新季报

**第三步：如年报无数据，按优先级查询最新季报**
```bash
# 按优先级查询：三季报 > 中报 > 一季报
# 1. 先查询三季报（10 月 - 次年 3 月可用）
mcporter call jy-financedata-api.FinancialDataAPI query="公司名 股票代码 2025 年 三季报 营业收入 净利润"

# 2. 如三季报无数据，查询中报（7 月 -9 月可用）
mcporter call jy-financedata-api.FinancialDataAPI query="公司名 股票代码 2025 年 中报 营业收入 净利润"

# 3. 如中报无数据，查询一季报（4 月 -6 月可用）
mcporter call jy-financedata-api.FinancialDataAPI query="公司名 股票代码 2025 年 一季报 营业收入 净利润"
```

**第四步：获取上年同期数据用于对比**
```bash
# 根据最新报告期，获取上年同期数据计算同比增速
# 如最新为 2025 年三季报，则获取 2024 年三季报
mcporter call jy-financedata-api.FinancialDataAPI query="公司名 股票代码 2024 年 三季报 营业收入 净利润"
```

**第五步：验证数据时效性（必须执行）**
- [ ] 检查返回数据的 `date` 字段，确认是最新报告期（如 2025-09-30）
- [ ] 如 `date` 字段显示为多年前（如 2018-12-31），说明数据不存在，必须降级
- [ ] 在报告中明确标注报告期类型（年报/三季报/中报/一季报）
- [ ] 在报告中标注数据截止日期（如 2025-09-30）

**必须获取的数据模块：**

| 数据类别 | mcporter 调用示例 | 使用服务 |
|---------|------------------|---------|
| 利润表 | `mcporter call jy-financedata-api.FinancialDataAPI query="公司名 股票代码 报告期 营业收入 净利润 归母净利润"` | jy-financedata-api |
| 资产负债表 | `mcporter call jy-financedata-api.FinancialDataAPI query="公司名 股票代码 报告期 总资产 总负债 净资产"` | jy-financedata-api |
| 现金流量表 | `mcporter call jy-financedata-api.FinancialDataAPI query="公司名 股票代码 报告期 经营现金流 投资现金流 筹资现金流"` | jy-financedata-api |
| 主营构成 | `mcporter call jy-financedata-tool.MainOperIncData query="公司名 股票代码 报告期 分产品 主营业务收入"` | jy-financedata-tool |
| 财务指标 | `mcporter call jy-financedata-api.FinancialDataAPI query="公司名 股票代码 报告期 毛利率 净利率 销售费用 管理费用 研发费用"` | jy-financedata-api |
| 盈利预测 | `mcporter call jy-financedata-api.FinancialDataAPI query="公司名 股票代码 盈利预测 一致预期"` | jy-financedata-api |

**数据获取原则：**
- 所有调用必须使用 `mcporter call` 命令
- 所有工具入参统一使用 `query` 参数
- 所有数据必须记录来源和时间戳
- **必须验证数据是否为最新报告期**（检查 `date` 字段）
- **必须获取上年同期数据验证同比增速**
- **如最新报告期数据为空，必须降级查询上一报告期**
- **所有数据必须标注报告期（年报/三季报/中报/一季报）**

**⚠️ 数据时效性验证（强制要求）：**
1. 检查返回数据的 `date` 字段
   - 正确：`"date": "2025-09-30"`（最新三季报）
   - 错误：`"date": "2018-12-31"`（旧数据，说明该报告期不存在）
2. 如发现 `date` 字段为多年前，必须立即降级查询上一报告期
3. 在报告中必须明确标注：
   - 数据截止日期（如 2025-09-30）
   - 报告期类型（如 三季报）
   - 数据来源（如 jy-financedata-api）

### 步骤 3：报告撰写

**标准报告 6 章节：**

1. **公司整体情况**：营收、归母净利润及同比变化，增长驱动因素
2. **分业务分析**：按产品/业务线拆分收入结构，各板块增速及贡献
3. **盈利能力与费用分析**：毛利率、净利率趋势，期间费用率拆解
4. **经营展望**：经营计划、分析师盈利预测、行业景气度
5. **风险提示**：财务风险、经营风险、行业风险
6. **投资建议**：未来 3 年预测、估值区间、投资评级

**详细报告模板：** 见 `references/research_report_template.md`

### 步骤 4：图表生成

**8 个标准化 echarts 图表：**
- 图表 1-2：年度/单季度营业收入及同比增速
- 图表 3-4：年度/单季度归母净利润及同比增速
- 图表 5-6：年度/单季度毛利率、净利率
- 图表 7-8：年度/单季度期间费用率

**echarts 配置示例：** 见 `references/gildata_mcp_api.md`

### 步骤 5：报告输出

**输出格式：** Markdown (.md)，支持 echarts 直接渲染

**输出目录：** `reports/`

**文件命名：** `<股票代码>_earnings_review_YYYYMMDD.md`

### 步骤 6：信息来源标注

**必须在报告末尾标注：**
```markdown
---
**数据来源：** 聚源数据、公司公告、Wind、分析师研报
**数据截止日期：** YYYY-MM-DD
**报告生成时间：** YYYY-MM-DD HH:MM
**免责声明：** 本报告仅供参考，不构成投资建议
```

## 快速开始

**基础调用流程：**

1. **确认环境配置完成**（见"环境检查与配置"章节）

2. **数据获取示例**：
```bash
# 获取利润表数据（营业收入、净利润）
mcporter call gildata_datamap-sse.FinancialDataAPI query="贵州茅台 600519 2025 年 年报 营业收入 净利润"

# 获取主营构成（分产品收入）
mcporter call gildata_datamap-sse.MainOperIncData query="贵州茅台 600519 2025 年 分产品 主营业务收入"

# 获取财务指标（毛利率、净利率、费用率）
mcporter call gildata_datamap-sse.FinancialDataAPI query="贵州茅台 600519 2025 年 年报 毛利率 净利率 销售费用 管理费用 研发费用"

# 获取盈利预测
mcporter call gildata_datamap-sse.FinancialDataAPI query="贵州茅台 600519 盈利预测 一致预期 目标价"
```

3. **生成报告**：
- 使用 `scripts/generate_report.py` 脚本生成标准化报告
- 或使用 `scripts/generate_echarts.py` 生成图表配置

4. **查看报告**：
- 报告保存在 `reports/` 目录
- 支持 Markdown 直接查看或导出为其他格式

## 资源清单

```
/home/liust/openclaw/workspace/skills/jy-a-stock-earnings-review/
├── SKILL.md                 # 本技能说明文档
├── README.md                # 快速入门指南
├── scripts/                 # 脚本工具目录
│   ├── generate_report.py   # 报告生成脚本
│   ├── generate_echarts.py  # echarts 图表生成脚本
│   ├── fetch_financial_data.py  # 财务数据获取脚本
│   └── extract_metrics.py   # 指标提取脚本
├── references/              # 参考文档目录
│   ├── financial_metrics.md # 财务指标定义
│   ├── research_report_template.md  # 券商研报模板
│   └── gildata_mcp_api.md   # MCP 接口文档和调用示例
├── reports/                 # 生成的报告输出目录
└── assets/                  # 资源文件
```

**详细文档说明：**
- 财务指标定义和计算公式：见 `references/financial_metrics.md`
- 券商研报标准模板和行文规范：见 `references/research_report_template.md`
- MCP 接口完整文档和工具列表：见 `references/gildata_mcp_api.md`

## 限制

**数据源限制：**
- 必须使用聚源数据 MCP 接口（通过 mcporter 调用）
- 配置的服务名称：`gildata_datamap-sse`
- 可用工具：`FinancialDataAPI`（财务数据）、`MainOperIncData`（主营构成）
- 所有数据延迟至少 15 分钟（非实时）

**使用限制：**
- 仅限 A 股上市公司
- 港股、美股不适用本技能
- 不构成投资建议，仅供参考

**注意事项：**
- JY_API_KEY 需妥善保管，不得泄露
- 首次使用需完成环境配置（约 10-15 分钟）
- 报告生成时间约 2-5 分钟（取决于数据获取速度）
- **所有业务数据必须通过 MCP 实际查询，不得使用估计值**
- **生成报告前必须核实关键数据（营收、利润、分业务收入等）**


