# API Key 配置指南

本文档详细说明 TradingAgents-CN 所需的 API Key 配置方法。

## 快速配置

在项目根目录 `E:\TradingAgents-CN\` 创建 `.env` 文件：

```bash
# 推荐配置（最低成本）
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here

# 可选配置
DASHSCOPE_API_KEY=sk-your-dashscope-api-key-here
TUSHARE_TOKEN=your-tushare-token-here
```

## API Key 获取方式

### 🇨🇳 DeepSeek（推荐）

**特点**：成本低、中文优化、无需翻墙

1. 访问：https://platform.deepseek.com/
2. 注册账号并登录
3. 进入「API Keys」页面
4. 点击「创建 API Key」
5. 复制 Key 到 `.env` 文件

**价格**：约 ¥1/百万 tokens，单次分析约 ¥0.1-0.5

---

### 🇨🇳 阿里百炼 / 通义千问

**特点**：阿里云、中文理解强、合规

1. 访问：https://dashscope.console.aliyun.com/
2. 开通 DashScope 服务
3. 创建 API Key
4. 复制 Key 到 `.env` 文件

**价格**：qwen-plus 约 ¥0.004/千 tokens

---

### 🇨🇳 智谱 AI（GLM）

**特点**：国产大模型、合规

1. 访问：https://open.bigmodel.cn/
2. 注册并创建 API Key
3. 配置环境变量：`ZHIPU_API_KEY`

---

### 🌍 OpenAI

**特点**：GPT-4、需要翻墙、成本较高

1. 访问：https://platform.openai.com/
2. 创建 API Key
3. 配置环境变量：`OPENAI_API_KEY`

**注意**：需要国际信用卡支付

---

### 🌍 Google AI（Gemini）

**特点**：Gemini 2.0、需要翻墙

1. 访问：https://aistudio.google.com/
2. 创建 API Key
3. 配置环境变量：`GOOGLE_API_KEY`

---

### 📊 Tushare（A股数据）

**特点**：免费 A股数据接口

1. 访问：https://tushare.pro/
2. 注册账号
3. 获取 Token
4. 配置环境变量：`TUSHARE_TOKEN`

**免费额度**：每日 500 次请求

---

### 📈 FinnHub（美股数据）

**特点**：免费美股数据

1. 访问：https://finnhub.io/
2. 注册并获取 API Key
3. 配置环境变量：`FINNHUB_API_KEY`

**免费额度**：每分钟 60 次请求

---

## 配置示例

### 最小配置（推荐）

```env
# 最小配置 - 仅 DeepSeek
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
```

### 完整配置

```env
# LLM 提供商
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
GOOGLE_API_KEY=AIzaxxxxxxxxxxxxxxxx

# 数据源
TUSHARE_TOKEN=xxxxxxxxxxxxxxxx
FINNHUB_API_KEY=xxxxxxxxxxxxxxxx

# MongoDB（可选）
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USERNAME=admin
MONGODB_PASSWORD=tradingagents123

# Redis（可选）
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=tradingagents123
```

---

## 常见问题

### Q: API Key 配置后不生效？

检查：
1. `.env` 文件是否在项目根目录
2. 文件名是否正确（不是 `.env.txt`）
3. Key 是否完整复制（无多余空格）

### Q: 如何切换 LLM 提供商？

在 CLI 中选择，或在配置中设置：
```python
config["llm_provider"] = "deepseek"  # 或 "dashscope", "openai", "google"
```

### Q: 如何查看已配置的 API Key？

运行：
```bash
python -m cli.main config
```

或查看 `.env` 文件内容。

---

## 安全提醒

⚠️ **请勿将 API Key 提交到 Git 仓库！**

`.env` 文件已添加到 `.gitignore`，不会被提交。

如果意外提交，请立即在对应平台撤销并重新生成 API Key。
