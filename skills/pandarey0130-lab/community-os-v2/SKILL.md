---
name: community-os
description: "Deploy and manage CommunityOS - a Harness Engineering Telegram multi-bot collaboration platform. Use when: setting up a Telegram multi-bot community system, creating bot souls and roles, configuring bot governance (CircuitBreaker, TokenBudget), managing bot knowledge bases, automating community operations (welcome messages, scheduled broadcasts). Triggers on: deploy CommunityOS, Telegram bot, multi-bot system, bot collaboration, community automation."
metadata:
  {
    "openclaw":
      {
        "emoji": "🤖",
        "requires": { "anyBins": ["python3"] },
        "env":
          [
            { "name": "BOT_TOKEN", "description": "Telegram Bot Token from @BotFather (per bot, defaults to TELEGRAM_BOT_TOKEN_PANDA)" },
            { "name": "TELEGRAM_BOT_TOKEN_PANDA", "description": "Telegram Bot Token for the panda helper bot" },
            { "name": "TELEGRAM_BOT_TOKEN_CYPHER", "description": "Telegram Bot Token for the cypher moderator bot" },
            { "name": "TELEGRAM_BOT_TOKEN_BUZZ", "description": "Telegram Bot Token for the buzz broadcaster bot" },
            { "name": "MINIMAX_API_KEY", "description": "MiniMax API Key for LLM (from minimax-portal.com)" },
            { "name": "CLAUDE_API_KEY", "description": "Optional: Anthropic Claude API Key for alternative LLM" },
            { "name": "APIYI_KEY", "description": "Optional: APIYI Key for alternative LLM" },
            { "name": "OPENAI_API_KEY", "description": "Optional: OpenAI API Key for alternative LLM" }
          ],
        "warning": "This skill reads a local .env file created by the user in their own project directory. All env vars are user-provided credentials for their own Telegram bots and LLM accounts. No credentials are hardcoded; users fill in their own values during setup."
      },
  }
---

# CommunityOS

**Harness Engineering Telegram 多 Bot 协作平台**

让多个 AI Bot 像真实群友一样在 Telegram 群里协作。

---

## 核心架构

```
┌─────────────────────────────────────────┐
│          HarnessOS (主控中心)             │
│  PolicyGate | CircuitBreaker            │
│  RetryBudget | TokenBudget              │
└─────────────────────────────────────────┘
        │                    │
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │  Panda  │◄──►│  Cypher │◄──►│   Buzz  │
    │ Helper  │    │Moderator│    │Broadcaster│
    └─────────┘    └─────────┘    └─────────┘
```

**三种 Bot 角色：**

| 角色 | 职责 | 触发方式 |
|------|------|----------|
| **Helper** | 欢迎新人、定时播报、活动公告 | 事件触发、定时任务 |
| **Moderator** | RAG 问答、代码示例、技术解答 | @提问、上下文补充 |
| **Broadcaster** | 分享资讯、活跃气氛、发起讨论 | 主动分享、闲聊 |

---

## 快速部署（4 步跑起来）

### 1. 安装 Skill
```bash
clawhub install community-os
```

### 2. 初始化项目

交互式（推荐）：
```bash
python3 ~/.openclaw/workspace/skills/community-os/scripts/init_community_os.py ./my-community
```

向导会要求填写：
- Bot Token（从 @BotFather 获取）
- MiniMax API Key
- Bot 名字和角色

### 3. 填 Token

```bash
cd ./my-community
nano .env
```

必须填：
```
MINIMAX_API_KEY=你的MiniMax_API_Key
BOT_TOKEN=你的Telegram_Bot_Token
```

### 4. 安装依赖 & 启动

```bash
pip install -r requirements.txt
python3 start_harness.py
```

看到 `HarnessOS running...` 即成功。

---

## 管理命令

### 创建新 Bot

```bash
python3 ~/.openclaw/workspace/skills/community-os/scripts/create_bot.py <项目路径> <bot_id> "<名字>" --role <角色>

# 示例
python3 scripts/create_bot.py ./my-community newsbot "资讯Bot" --role broadcaster
```

### 配置知识库

```bash
# 初始化知识库
python3 ~/.openclaw/workspace/skills/community-os/scripts/setup_knowledge.py ./my-community cypher

# 添加文档后索引
python3 scripts/setup_knowledge.py ./my-community cypher --index

# 文档放在：my-community/knowledge/cypher/
```

### 治理配置

编辑 `config/harness.yaml`：

```yaml
circuit_breaker:
  failure_threshold: 5    # 熔断阈值
  recovery_timeout: 60   # 恢复等待秒数

token_budget:
  max_tokens_per_session: 8192
  max_cost_cny_per_session: 1.0
```

---

## 项目结构（初始化后）

```
my-community/
├── harness_os.py        # 🚀 核心框架（633行）
├── start_harness.py    # 启动脚本
├── souls/              # Bot 灵魂配置
│   ├── panda.md
│   ├── cypher.md
│   └── buzz.md
├── config/
│   ├── bots.yaml       # Bot 注册
│   └── harness.yaml    # 治理配置
├── harness/            # 治理引擎
│   ├── core.py         # GovernanceEngine
│   ├── circuit_breaker.py
│   ├── token_budget.py
│   ├── retry_budget.py
│   └── ...
├── bot_engine/         # Bot 引擎
│   ├── manager.py
│   ├── bot_instance.py
│   └── config_parser.py
├── knowledge_base/     # 知识库 RAG
│   ├── rag.py
│   ├── vector_store.py
│   └── indexer.py
├── telegram/           # Telegram API
├── deploy/             # 部署脚本
└── .env                # Token 配置
```

---

## 故障排查

| 问题 | 解决 |
|------|------|
| Bot 无响应 | 检查 `.env` 的 Token 是否正确 |
| LLM 报错 | 确认 `MINIMAX_API_KEY` 有效 |
| 知识库空 | 运行 `setup_knowledge.py --index` |
| 熔断触发 | 等待 60 秒或重启 |
| 缺少模块 | `pip install -r requirements.txt` |

---

## 自定义 Bot Soul

编辑 `souls/<bot_id>.md`：

```markdown
# 你的Bot名字

你是<名字>，<角色定位>。

**核心职责：**
- <职责1>
- <职责2>

**性格特点：**
- <特点1>
- <特点2>

**协作方式：**
- 需要<什么>时 @<哪个Bot>
```

编辑后重启 harness 生效。
