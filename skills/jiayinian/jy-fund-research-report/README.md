# jy-fund-research-report - 基金深度研究报告生成器

基于 MCP 聚源金融数据库，自动生成专业深度的基金投资研究报告。

## 📊 功能特点

- **六大核心模块**：基金概况、业绩分析、资产配置、基金经理、基金公司、投资建议
- **数据可溯源**：所有数据来自恒生聚源，带时间戳
- **并发获取**：7 个维度数据并发获取，60-90 秒完成
- **Markdown 输出**：标准格式，易于阅读和分享

## 🚀 快速开始

### 前置要求

1. Node.js + npm
2. Python 3
3. mcporter（通过 `npm install -g mcporter` 安装）
4. JY_API_KEY（向 datamap@gildata.com 申请）

### 安装配置

```bash
# 1. 安装 mcporter
npm install -g mcporter

# 2. 配置 MCP 服务（替换你的 JY_API_KEY）
mcporter config add api-mcp --url "https://pure.warrenq.com/mcpdb/api-mcp?token=你的 JY_API_KEY"

# 3. 验证配置
mcporter list
```

### 使用方式

```bash
# 进入技能目录
cd jy-fund-research-report

# 生成完整报告
./run.sh 005827

# 或指定维度
./run.sh 005827 performance
./run.sh 005827 manager
```

### 在 OpenClaw 中使用

```
帮我分析基金 005827，生成深度研究报告
```

## 📁 文件结构

```
jy-fund-research-report/
├── SKILL.md              # 技能说明文档
├── run.sh                # 入口脚本
├── scripts/
│   ├── fetch_data.py     # 数据获取脚本
│   └── ai_prompt.md      # AI 分析指令
├── references/
│   └── report_template.md  # 报告格式模板
└── output/               # 输出目录
```

## 📋 报告内容

| 模块 | 内容 |
|------|------|
| 基金基本概况 | 代码、名称、类型、规模、费率、业绩基准 |
| 业绩分析 | 各周期收益率、同类排名、风险指标、业绩归因 |
| 资产配置 | 股票/债券仓位、行业分布、持仓集中度 |
| 基金经理 | 履历、管理业绩、投资理念、能力圈 |
| 基金公司 | 公司概况、财务数据、投研实力 |
| 投资建议 | 适合投资者类型、配置建议、风险提示 |

## ⚠️ 注意事项

1. **JY_API_KEY 安全**：请勿公开分享
2. **数据时效性**：基金数据通常为 T+1 更新
3. **免责声明**：报告仅供参考，不构成投资建议

## 📧 获取 JY_API_KEY

向恒生聚源发送邮件申请：

- **邮箱**：datamap@gildata.com
- **标题**：数据地图 KEY 申请 -XX 公司 - 申请人姓名
- **正文**：姓名、手机号、公司、部门、岗位、申请用途等

详见 SKILL.md 完整申请模板。

## 📄 许可证

MIT License

## 🙏 致谢

- 数据支持：恒生聚源（GILData）
- 工具支持：OpenClaw + mcporter

---

**版本**：1.0.0  
**最后更新**：2026-04-02
