# CommunityOS

**Harness Engineering Telegram 多 Bot 协作平台**

让多个 AI Bot 像真实群友一样在 Telegram 群里协作。

## Features

- 🚀 一键初始化项目（复制真实框架代码）
- 🤖 3 种 Bot 角色（Helper / Moderator / Broadcaster）
- 🛡️ 治理引擎（CircuitBreaker、TokenBudget、RetryBudget）
- 📚 Chroma RAG 知识库
- 🔗 Bot @协作机制
- 🌐 Telegram Bot API 集成

## 项目结构

```
my-community/
├── harness_os.py        # 核心框架
├── start_harness.py    # 启动脚本
├── souls/              # Bot 灵魂配置
│   ├── panda.md
│   ├── cypher.md
│   └── buzz.md
├── config/
│   ├── bots.yaml       # Bot 注册
│   └── harness.yaml    # 治理配置
├── harness/            # 治理引擎
│   ├── core.py
│   ├── circuit_breaker.py
│   └── ...
├── bot_engine/         # Bot 引擎
├── knowledge_base/     # 知识库 RAG
└── .env                # Token 配置
```

## 快速开始

```bash
# 1. 初始化（自动复制完整框架代码）
python3 init_community_os.py ./my-community

# 2. 填入 Token
cp ./my-community/.env.example ./my-community/.env
nano ./my-community/.env

# 3. 安装依赖
pip install -r ./my-community/requirements.txt

# 4. 启动
cd ./my-community && python3 start_harness.py
```

## Bot 角色

| 角色 | 职责 | 触发方式 |
|------|------|----------|
| **Helper** | 欢迎新人、定时播报、活动公告 | 事件触发、定时任务 |
| **Moderator** | RAG 问答、代码示例、技术解答 | @提问、上下文补充 |
| **Broadcaster** | 分享资讯、活跃气氛、发起讨论 | 主动分享、闲聊 |

## 依赖

- Python 3.10+
- aiogram >= 3.0
- chromadb
- pyyaml
- aiohttp

安装：`pip install -r requirements.txt`
