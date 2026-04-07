---
name: jy-fund-research-report
description: 基于恒生聚源 MCP 金融服务（jy-financedata-api）生成基金深度投资研究报告（Markdown 格式）。覆盖基金基本概况、业绩分析（含同类排名）、资产配置、基金经理、基金公司、投资建议六大核心模块，所有数据可溯源、带时间戳。使用场景：当用户需要分析某只基金、生成基金研究报告、查询基金业绩、基金经理信息、持仓分析、风险评估、同类排名时触发。Generate in-depth fund investment research reports based on GILData MCP Financial Service (jy-financedata-api, Markdown format). Covers six core modules: fund overview, performance analysis (with peer ranking), asset allocation, fund manager, fund company, and investment recommendations. All data is traceable with timestamps. Use case: Triggered when users need to analyze a fund, generate fund research reports, query fund performance, manager information, holdings analysis, risk assessment, or peer ranking.
metadata:
 openclaw:
 requires:
 bins: ["node", "npm", "mcporter", "python3"]
 install:
 - id: install-mcporter
 kind: node
 package: mcporter
 label: Install mcporter via npm
---

# 基金深度研究报告生成器

基于 MCP 聚源金融数据库，自动生成专业深度的基金投资研究报告。报告包含基金概况、业绩分析、资产配置、基金经理、基金公司、投资建议六大模块，所有数据可溯源。

## 功能范围

本技能支持以下功能：

| 功能模块 | 说明 |
|----------|------|
| 基金基本概况 | 基金代码、名称、类型、规模、成立日期、业绩基准、费率等 |
| 业绩深度分析 | 各周期收益率、同类排名、风险指标（夏普/波动率/回撤等） |
| 资产配置分析 | 股票/债券/现金仓位、行业分布、持仓集中度 |
| 基金经理分析 | 现任/历任经理、管理业绩、投资风格、能力圈 |
| 基金公司分析 | 公司概况、管理规模、投研团队、财务数据 |
| 投资建议 | 适合投资者类型、配置建议、风险提示 |

**支持查询的基金类型：**
- 股票型基金
- 混合型基金
- 债券型基金
- QDII 基金
- FOF 基金

## 查询建议

**查询必备要素：**
- 基金代码（6 位数字，如 005827）或基金名称（如"易方达蓝筹精选混合"）

**推荐查询写法：**
- 使用基金代码最准确（如"005827"）
- 使用完整基金名称（如"易方达蓝筹精选混合"）
- 可指定分析维度（如"005827 业绩分析"、"005827 基金经理"）


## 查询示例

```bash
# 完整分析报告
./run.sh 005827

# 使用基金名称
./run.sh 易方达蓝筹精选混合

# 仅获取业绩数据
./run.sh 005827 performance

# 仅获取基金经理信息
./run.sh 005827 manager

# 仅获取资产配置
./run.sh 005827 allocation
```

**在 OpenClaw 中直接使用：**
```
帮我分析基金 005827，生成深度研究报告
分析易方达蓝筹精选混合的业绩和基金经理
生成 005827 的投资研究报告
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

#### 2.1 获取 JY_API_KEY

向恒生聚源官方邮箱发送邮件申请签发数据地图 JY_API_KEY，用于接口鉴权。

**申请邮箱：** datamap@gildata.com

**邮件标题：** 数据地图 KEY 申请-XX 公司 - 申请人姓名

**正文模板：**
```
• 姓名：
• 手机号：
• 公司/单位全称：
• 所属部门：
• 岗位：
• MCP_KEY 申请用途：基金研究报告生成
• Skill 申请列表：jy-fund-research-report
• 是否需要 Skill 安装包：（是，邮件提供/否，自行下载）
• 其他补充说明（可选）：
```

申请通过后，恒生聚源将发送【工具版和接口版】KEY。

#### 2.2 配置 MCP 服务

```bash
# 配置 jy-financedata-tool 服务
mcporter config add jy-financedata-tool --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-tool?token=你的 JY_API_KEY"

# 配置 jy-financedata-api 服务
mcporter config add jy-financedata-api --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-api?token=你的 JY_API_KEY"
```

#### 2.3 验证配置

```bash
# 验证服务配置
mcporter list
```

**预期输出应包含：**
```
jy-financedata-tool
jy-financedata-api
```

#### 2.4 测试调用

```bash
# 测试调用（所有工具入参均为 query）
mcporter call jy-financedata-api.FinancialDataAPI query="基金 005827 基本信息"
```

### 步骤 3：验证配置

```bash
# 验证服务配置
mcporter list

# 测试调用（注意：所有工具入参均为 query）
mcporter call jy-financedata-api.FinancialDataAPI query="基金 005827 基本信息"
```

**预期：** 返回基金基本信息的 JSON 数据。

### 步骤 4：运行环境检查脚本

```bash
cd ~/Desktop/jy-fund-research-report
./run.sh --check
```

脚本将自动检查：
- mcporter 是否安装
- MCP 服务是否配置
- Python 3 是否可用
- 输出目录是否存在

## 核心工作流程

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  1. 环境检查     │ -> │  2. 并发获取数据  │ -> │  3. AI 深度分析   │
│  (mcporter/MCP) │    │  (7 个维度)      │    │  (生成报告)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               ↓
┌─────────────────┐    ┌─────────────────┐
│  5. 完成输出     │ <- │  4. 保存数据     │
│  (markdown 报告) │    │  (output 目录)   │
└─────────────────┘    └─────────────────┘
```

所有数据获取步骤**并发执行**以提升速度，单次完整数据获取约 60-90 秒。

### 步骤 1：环境检查

启动时自动检查：
- mcporter 是否已安装
- api-mcp 服务是否已配置
- Python 3 是否可用
- 输出目录是否存在

如检查失败，脚本将提示用户进行相应配置。

### 步骤 2：并发获取基金数据

使用 Python 脚本并发调用 MCP 工具获取 7 个维度数据：

| 维度 | 查询示例 | 用途 |
|------|----------|------|
| basic | `基金{code} 基本信息` | 基金概况、规模、费率 |
| performance | `基金{code} 业绩表现` | 各周期收益率、排名 |
| risk | `基金{code} 风险指标` | 夏普比率、波动率、回撤 |
| manager | `基金{code} 基金经理` | 经理履历、管理业绩 |
| allocation | `基金{code} 资产配置` | 股票/债券仓位 |
| holdings | `基金{code} 重仓股` | 持仓集中度、重仓股 |
| company | `基金公司 概况` | 公司实力、财务数据 |

**调用方式：**
```bash
mcporter call jy-financedata-api.FinancialDataAPI query="基金 005827 基本信息"
```

### 步骤 3：AI 深度分析

将获取的原始数据发送给 AI，AI 根据参考报告格式进行深度分析：

1. 解析各维度数据
2. 进行业绩归因分析
3. 评估基金经理能力
4. 生成投资建议

### 步骤 4：生成报告

输出 Markdown 格式报告，包含：
- 基金基本概况
- 基金业绩分析（含业绩归因）
- 资产配置及持仓风格
- 基金经理投资框架
- 基金公司分析
- 综合评价及投资建议

## 快速开始

### 方式 A：命令行运行

```bash
# 1. 进入技能目录
cd ~/Desktop/jy-fund-research-report

# 2. 运行脚本（替换基金代码）
./run.sh 005827

# 3. 查看输出
ls -la output/
cat output/005827_data.md
```

### 方式 B：在 OpenClaw 中直接使用

```
帮我分析基金 005827，生成深度研究报告
```

AI 将自动：
1. 调用 MCP 工具获取数据
2. 进行深度分析
3. 输出完整报告

### 方式 C：使用 Python 脚本直接获取数据

```bash
python3 scripts/fetch_data.py 005827
```

### 数据获取策略

**优先级策略：**
1. 优先使用基金代码查询（最准确）
2. 代码查询失败时，尝试基金名称
3. 关键数据缺失时，尝试同义词查询

**超时处理：**
- 单次查询超时：30 秒
- 整体获取超时：180 秒
- 超时后输出已获取数据，标记缺失部分

**错误处理：**
- 查询无数据：标记为"暂缺"
- 服务不可用：提示用户检查配置
- 网络错误：重试 1 次后报错

## 资源清单

```
~/Desktop/jy-fund-research-report/
├── SKILL.md              # 技能说明文档（本文件）
├── run.sh                # 入口脚本（环境检查 + 数据获取）
├── scripts/
│   ├── fetch_data.py     # 数据获取脚本（并发调用 MCP）
│   └── ai_prompt.md      # AI 分析指令模板
├── references/
│   └── report_template.md  # 报告格式参考模板
└── output/               # 输出目录（运行时生成）
    ├── {code}_data.md    # 原始数据
    └── {code}_report.md  # 分析报告（AI 生成）
```

## 限制

### 数据源限制
- 依赖恒生聚源 MCP 服务，需有效 JY_API_KEY
- 部分新成立基金（<3 个月）数据可能不完整
- QDII 基金数据可能存在 T+2 延迟

### 输出限制
- 报告为 Markdown 格式，不支持直接导出 PDF/Word
- 实时净值数据需通过其他工具获取
- 不支持多基金对比分析（需分别查询）

### 注意事项
1. **JY_API_KEY 安全：** 请勿在公开场合分享你的 API_KEY
2. **数据时效性：** 基金数据通常为 T+1 更新
3. **投资建议：** 报告仅供参考，不构成投资建议

## 故障排查

### 问题 1：mcporter 命令未找到

**解决：**
```bash
npm install -g mcporter
```

### 问题 2：MCP 服务未配置

**解决：**
```bash
mcporter config add api-mcp --url "https://pure.warrenq.com/mcpdb/api-mcp?token=你的 JY_API_KEY"
```

### 问题 3：查询返回空数据

**可能原因：**
- 基金代码错误
- 基金名称不准确
- MCP 服务暂不可用

**解决：**
1. 验证基金代码是否正确（6 位数字）
2. 尝试使用基金全称查询
3. 检查网络连接和 API_KEY 有效性

### 问题 4：脚本执行超时

**解决：**
- 减少并发数量（修改 fetch_data.py 中的 max_workers）
- 增加超时时间（修改 CONFIG 中的 timeout 配置）
- 检查网络连接

## 免责声明

**本报告由 AI 基于公开数据生成，仅供参考，不构成任何投资建议。**

- 基金投资有风险，过往业绩不代表未来表现
- 投资者应根据自身风险承受能力独立决策
- 报告数据可能存在延迟或误差，请以基金公司官方披露为准
- 使用本技能产生的任何投资决策风险由用户自行承担

---

**技术支持：** 参考 references/report_template.md 获取完整报告格式示例。

**版本：** 1.0.0  
**最后更新：** 2026-04-02
