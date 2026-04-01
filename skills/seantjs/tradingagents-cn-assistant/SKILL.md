---
name: tradingagents-cn-assistant
version: 1.2.1
description: |
  多智能体大语言模型金融交易分析助手。基于 TradingAgents-CN 框架，使用多个专业AI分析师协作分析股票（A股/港股/美股），生成投资建议和专业报告。

  触发场景：
  - 用户说"分析某只股票"、"帮我看看茅台"、"股票怎么样"
  - 用户说"股票分析"、"投资建议"、"股票研究报告"
  - 用户提到股票代码（如 600519、AAPL、0700.HK）并需要分析
  - 用户需要股票基本面分析、技术分析、新闻分析
  - 用户需要生成股票分析报告（Markdown/Word/PDF）

  核心功能：
  - 多智能体协作：5类分析师（市场/A股市场/新闻/基本面/情绪）并行工作
  - 研究团队辩论：看涨 vs 看跌研究员观点交锋
  - 风险管理三方辩论：激进/保守/中性分析师
  - 支持A股/港股/美股实时数据
  - 国产LLM支持（DeepSeek、硅基流动、通义千问等）
license: Apache-2.0
---

# TradingAgents-CN 股票分析助手

基于 [hsliuping/TradingAgents-CN](https://github.com/hsliuping/TradingAgents-CN) 的多智能体股票分析框架。

## ⚠️ 重要声明

**本技能仅供学习研究用途，不构成任何投资建议。**
- 股票分析结果仅供参考，投资决策请咨询专业顾问
- 模型分析可能存在偏差，请结合多方面信息判断
- 使用本技能进行投资决策的风险由用户自行承担

---

## 一、前置条件

1. **克隆 TradingAgents-CN 项目到本地**，记录项目路径（下文用 `{PROJECT_DIR}` 表示）
   ```bash
   git clone https://github.com/hsliuping/TradingAgents-CN.git
   ```
2. **Python 环境**：Python 3.10 - 3.13
3. **已配置 API Key**（见下方配置说明）

> 💡 首次使用时告诉 AI："我的 TradingAgents-CN 项目路径是 [你的路径]"，AI 会记住并自动使用。

---

## 二、配置说明

### 2.1 API Key 配置（`{PROJECT_DIR}/.env`）

```env
# 硅基流动（推荐，支持国产模型）
SILICONFLOW_API_KEY=sk-your-key
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_DEEP_THINK_MODEL=Qwen/Qwen3.5-4B
SILICONFLOW_QUICK_THINK_MODEL=Qwen/Qwen3.5-4B

# DeepSeek（成本低）
DEEPSEEK_API_KEY=sk-your-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_ENABLED=true
```

### 2.2 分析参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `max_debate_rounds` | 1 | 看涨/看跌辩论轮数 |
| `max_risk_discuss_rounds` | 1 | 风险管理辩论轮数 |
| `online_tools` | false | 是否启用在线工具 |

---

## 三、完整分析流程（9步多智能体协作）

```
用户输入股票代码
        ↓
【第1步】数据获取层（AKShare 实时拉取）
        ↓
【第2步】5个分析师并行工作
  ├── 市场分析师       → 技术指标（MA/MACD/RSI/BOLL）
  ├── A股市场分析师    → A股专项（北向资金/板块/涨跌停）
  ├── 基本面分析师     → 财务数据（PE/PB/ROE/DCF）
  ├── 新闻分析师       → 舆情监控（公告/新闻/事件）
  └── 社交媒体分析师   → 情绪分析（论坛/社交媒体）
        ↓
【第3步】看涨研究员 ←→ 看跌研究员（多空辩论 N 轮）
  - 看涨研究员：构建增长潜力、竞争优势论证
  - 看跌研究员：构建风险挑战、负面指标论证
        ↓
【第4步】投资研究总监（综合判断）
  - 主持多空辩论，批判性评估双方论点
  - 输出：明确投资建议 + 目标价位区间 + 投资计划
        ↓
【第5步】交易员（具体交易决策）
  - 接收投资计划，结合四份分析报告
  - 输出：买入/持有/卖出 + 具体目标价 + 置信度 + 风险评分
        ↓
【第6步】激进/保守/中性风险分析师（三方风险辩论 N 轮）
  - 激进分析师：倡导高回报高风险策略
  - 保守分析师：强调风险缓解和稳健策略
  - 中性分析师：提供平衡视角，调和两端
        ↓
【第7步】风险管理总监（最终风险评估）
  - 综合三方辩论，完善交易员计划
  - 输出：最终风险调整后的投资建议
        ↓
【第8步】投资组合经理（最终决策）
  - 批判性评估全部辩论，做出最终承诺
  - 输出：明确的买入/持有/卖出 + 目标价格区间（保守/基准/乐观）
        ↓
【第9步】结果输出
  - 控制台打印完整分析报告
  - 可选：整理为 Markdown/Word/PDF 文档
```

---

## 四、执行方法

### 4.1 AI 助手触发（推荐）

直接告诉 AI 要分析的股票：
- "分析 300339 润和软件"
- "帮我看看 600519 贵州茅台"
- "生成一份腾讯 0700.HK 的投资报告"

### 4.2 AI 执行时的标准命令

```powershell
cd {PROJECT_DIR}
python analyze_simple.py {股票代码} {日期(可选)}
```

示例：
```powershell
cd {PROJECT_DIR}
python analyze_simple.py 300339 2026-03-31
```

### 4.3 执行进度说明

AI 在执行时应向用户汇报当前进度，例如：
- "正在运行第2步：5个分析师并行采集数据..."
- "正在运行第3步：看涨/看跌研究员辩论中..."
- "正在运行第4步：投资研究总监综合判断..."
- "分析完成，正在整理报告..."

---

## 五、各角色职责速查

### 分析师层（第2步）

| 角色 | 文件 | 核心职责 |
|------|------|---------|
| 市场分析师 | `agents/analysts/market_analyst.py` | MA/MACD/RSI/BOLL 技术指标 |
| A股市场分析师 | `agents/analysts/china_market_analyst.py` | 北向资金、板块轮动、A股特色指标 |
| 基本面分析师 | `agents/analysts/fundamentals_analyst.py` | PE/PB/ROE/DCF 财务分析 |
| 新闻分析师 | `agents/analysts/news_analyst.py` | 公告、新闻、重大事件 |
| 社交媒体分析师 | `agents/analysts/social_media_analyst.py` | 论坛情绪、社交媒体舆情 |

### 研究辩论层（第3-4步）

| 角色 | 文件 | 核心职责 |
|------|------|---------|
| 看涨研究员 | `agents/researchers/bull_researcher.py` | 构建多头论证，反驳空头 |
| 看跌研究员 | `agents/researchers/bear_researcher.py` | 构建空头论证，反驳多头 |
| 投资研究总监 | `agents/managers/research_manager.py` | 主持辩论，输出投资计划 |

### 交易执行层（第5步）

| 角色 | 文件 | 核心职责 |
|------|------|---------|
| 交易员 | `agents/trader/trader.py` | 制定具体交易计划，强制给出目标价 |

### 风险管理层（第6-8步）

| 角色 | 文件 | 核心职责 |
|------|------|---------|
| 激进风险分析师 | `agents/risk_mgmt/aggresive_debator.py` | 倡导高风险高回报 |
| 保守风险分析师 | `agents/risk_mgmt/conservative_debator.py` | 强调风险缓解稳健增长 |
| 中性风险分析师 | `agents/risk_mgmt/neutral_debator.py` | 平衡视角，调和两端 |
| 风险管理总监 | `agents/managers/risk_manager.py` | 综合风险辩论，完善交易计划 |
| 投资组合经理 | `graph/trading_graph.py` | 最终决策，输出目标价区间 |

---

## 六、输出报告结构

分析完成后，AI 应将控制台输出整理为以下结构：

```markdown
# {公司名称}（{股票代码}）投资分析报告
> 分析日期：{日期}

## 一、市场技术分析
- 趋势判断：
- 关键价位：
- 技术指标信号：

## 二、基本面分析
- 估值水平（PE/PB）：
- 盈利能力（ROE）：
- 成长性：

## 三、消息面分析
- 近期重要公告：
- 行业动态：
- 风险事件：

## 四、情绪面分析
- 市场情绪：
- 社交媒体热度：

## 五、多空辩论摘要
- 看涨核心论点：
- 看跌核心论点：
- 研究总监判断：

## 六、风险评估
- 激进观点：
- 保守观点：
- 风险管理总监结论：

## 七、最终投资建议
- **投资评级**：买入 / 持有 / 卖出
- **目标价格**：
  - 保守目标：
  - 基准目标：
  - 乐观目标：
- **时间范围**：
- **置信度**：
- **风险评分**：
- **核心理由**：
```

---

## 七、股票代码格式

| 市场 | 格式 | 示例 |
|------|------|------|
| A股 | 6位数字 | 600519, 000001, 300339 |
| 港股 | 数字.HK | 0700.HK, 09988.HK |
| 美股 | 字母代码 | AAPL, NVDA, TSLA |

---

## 八、已知问题与处理

| 问题 | 说明 | 处理方式 |
|------|------|---------|
| AKShare 网络抖动 | `Connection aborted` | 重试一次，通常自动恢复 |
| Tushare Token 无效 | 日志显示"您的token不对" | 忽略，不影响 AKShare 数据 |
| MongoDB/Redis 无需安装 | 命令行分析不需要数据库 | 直接实时拉取，无需配置 |
| Pydantic 警告 | Python 3.14 兼容性警告 | 不影响功能，忽略即可 |
| 分析时间较长 | 约 5-15 分钟 | 正常现象，LLM 调用耗时 |

---

## 九、支持的 LLM 提供商

| 提供商 | 推荐模型 | 成本 | 获取地址 |
|--------|---------|------|---------|
| 硅基流动 | Qwen/Qwen3.5-4B | 低 | https://www.siliconflow.cn/ |
| DeepSeek | deepseek-chat | 最低 | https://platform.deepseek.com/ |
| 通义千问 | qwen-plus | 低 | https://dashscope.aliyun.com/ |
| OpenAI | gpt-4o | 高 | https://platform.openai.com/ |
| Google | gemini-2.0-flash | 中 | https://ai.google.dev/ |

---

## 项目信息

- **项目路径**：`{PROJECT_DIR}`（用户自行配置）
- **分析脚本**：`{PROJECT_DIR}/analyze_simple.py`
- **GitHub**：https://github.com/hsliuping/TradingAgents-CN
- **许可证**：Apache 2.0
