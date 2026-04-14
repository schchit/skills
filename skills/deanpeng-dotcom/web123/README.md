[🇺🇸 English](#english) · [🇨🇳 中文](#chinese)

---

<a name="english"></a>

# web123 — Web3 Skill Navigator

> **"New to Web3? Start with web123."**

Describe your need in plain language — get the right Web3 skill recommendation instantly.

## 🚀 Quick Start

```bash
# Install
openclaw skill install https://github.com/AntalphaAI/web123

# Then just talk to your AI agent:
"I want to trade tokens"          → recommends web3-trader
"Check my wallet balance"         → recommends wallet-balance
"I'm new to Web3, where to start" → recommends Beginner Pack
"What Web3 skills are available"  → shows all 13 skills
```

## 📦 What's Inside

**13 official AntalphaAI Skills** across 5 categories:

| Category | Skill | Description |
|----------|-------|-------------|
| 🔄 Trading | `web3-trader` | DEX swap + Hyperliquid perpetuals |
| 🔄 Trading | `poly-master` | Polymarket prediction market |
| 💰 Invest | `antalpha-rwa` | RWA on-chain yield |
| 💰 Invest | `web3-investor` | DeFi portfolio management |
| 📊 Data | `wallet-balance` | Multi-chain wallet balance |
| 📊 Data | `transaction-receipt` | On-chain transaction decoder |
| 📊 Data | `smart-money` | Whale / smart money tracking |
| 📊 Data | `defillama-data-aggregator` | DeFi TVL & yield data |
| 🛡️ Safety | `wallet-guard` | Wallet approval risk scan |
| 🛡️ Safety | `meme-token-analyzer` | Meme token analysis |
| 🛡️ Safety | `airdrop-hunter` | Daily airdrop intel |
| 💳 Payment | `eth-payment` | EIP-681 payment link generator |
| 💳 Payment | `walletconnect-requester` | WalletConnect wallet connector |

## 🎒 Starter Packs

### Web3 Beginner
```bash
openclaw skill install https://github.com/AntalphaAI/wallet-balance https://github.com/AntalphaAI/web3-trader https://github.com/AntalphaAI/transaction-receipt
```
Check balance + trade tokens + verify transactions

### Safety Pack
```bash
openclaw skill install https://github.com/AntalphaAI/wallet-guard https://github.com/AntalphaAI/airdrop-hunter https://github.com/AntalphaAI/Meme-Token-Analyzer
```
Wallet guard + airdrop hunter + meme analysis

### Trading Pack
```bash
openclaw skill install https://github.com/AntalphaAI/web3-trader https://github.com/AntalphaAI/wallet-balance https://github.com/AntalphaAI/transaction-receipt
```
Full trading stack: swap + balance + tx verification

## 💡 How It Works

```
User natural language input
        ↓
Intent detection (beginner / browse / match / full list)
        ↓
Tag-weighted matching (tags×3 + scenarios×2 + description×1)
        ↓
Return Top 3 recommendations + install commands
```

## 📁 File Structure

```
web123/
├── README.md              ← You are here
├── SKILL.md               ← Agent instruction file
└── references/
    └── skills.json        ← Skill metadata (13 skills)
```

## 🔗 AntalphaAI GitHub

All skills sourced from:
👉 [github.com/AntalphaAI](https://github.com/AntalphaAI)

---

*Powered by Antalpha AI · web123 v1.2.0*

---

<a name="chinese"></a>

# web123 — Web3 技能导航站

> **"Web3 不会用，就上 web123"**

一句话描述需求，AI 自动推荐最合适的 Web3 工具并给出安装命令。

## 🚀 快速开始

```bash
# 安装
openclaw skill install https://github.com/AntalphaAI/web123

# 然后直接跟 AI 说：
"我想交易代币"        → 推荐 web3-trader
"查我的钱包余额"      → 推荐 wallet-balance
"Web3 新手，怎么开始" → 推荐新手入门套装
"有哪些 Web3 技能"   → 展示全部 13 个 skill
```

## 📦 收录内容

共收录 **13 个** AntalphaAI 官方 Skill，覆盖 5 大分类：

| 分类 | Skill | 一句话描述 |
|------|-------|-----------|
| 🔄 交易 | `web3-trader` | DEX 聚合交易 + Hyperliquid 合约 |
| 🔄 交易 | `poly-master` | Polymarket 预测市场 |
| 💰 投资 | `antalpha-rwa` | RWA 链上理财 |
| 💰 投资 | `web3-investor` | DeFi 投资组合管理 |
| 📊 数据 | `wallet-balance` | 多链钱包余额查询 |
| 📊 数据 | `transaction-receipt` | 链上交易解析 |
| 📊 数据 | `smart-money` | 聪明钱鲸鱼追踪 |
| 📊 数据 | `defillama-data-aggregator` | DeFi TVL 数据聚合 |
| 🛡️ 安全 | `wallet-guard` | 钱包高风险授权扫描 |
| 🛡️ 安全 | `meme-token-analyzer` | Meme 币财富基因检测 |
| 🛡️ 安全 | `airdrop-hunter` | 空投情报日报 |
| 💳 支付 | `eth-payment` | EIP-681 收款链接生成 |
| 💳 支付 | `walletconnect-requester` | WalletConnect 钱包连接 |

## 🎒 新手套装

### 新手入门
```bash
openclaw skill install https://github.com/AntalphaAI/wallet-balance https://github.com/AntalphaAI/web3-trader https://github.com/AntalphaAI/transaction-receipt
```
查余额 + 交易代币 + 查交易记录

### 安全套装
```bash
openclaw skill install https://github.com/AntalphaAI/wallet-guard https://github.com/AntalphaAI/airdrop-hunter https://github.com/AntalphaAI/Meme-Token-Analyzer
```
钱包防护 + 空投猎手 + Meme 币分析

### 交易套装
```bash
openclaw skill install https://github.com/AntalphaAI/web3-trader https://github.com/AntalphaAI/wallet-balance https://github.com/AntalphaAI/transaction-receipt
```
完整交易工具链：DEX 兑换 + 余额查询 + 交易验证

## 💡 工作原理

```
用户自然语言输入
        ↓
意图识别（新手 / 分类浏览 / 需求匹配 / 全览）
        ↓
标签权重匹配算法（tags×3 + scenarios×2 + description×1）
        ↓
返回 Top 3 推荐 + 安装命令
```

## 📁 文件结构

```
web123/
├── README.md              ← 你在这里
├── SKILL.md               ← AI Agent 执行规范
└── references/
    └── skills.json        ← 13 个 skill 元数据
```

## 🔗 AntalphaAI GitHub

所有收录 skill 均来自：
👉 [github.com/AntalphaAI](https://github.com/AntalphaAI)

---

*Powered by Antalpha AI · web123 v1.2.0*
