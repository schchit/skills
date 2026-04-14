---
name: web123
version: 1.2.0
description: "Web3 Skill Navigator / Web3 技能导航站. Describe your need in plain language to get matched AntalphaAI skill recommendations with install commands. Triggers: web123, recommend skill, I want to trade tokens, check wallet balance, Web3 beginner, invest RWA, whale tracking, airdrop, meme token analysis, payment link, what Web3 skills are there / 触发词：web123、推荐技能、我想交易代币、查余额、Web3新手、投资理财、聪明钱追踪、空投、meme币分析、收款链接、Web3技能有哪些"
author: Antalpha AI
---

# web123 — Web3 Skill Navigator / Web3 技能导航站

> **"Web3 不会用，就上 web123" / "New to Web3? Start with web123."**
>
> AntalphaAI 官方 13 个 Skill 导航，自然语言匹配推荐
> Official navigator for 13 AntalphaAI skills — match by natural language

---

## Data Source / 数据来源

Skill metadata is stored in `references/skills.json`.
Only skills from the official [AntalphaAI GitHub org](https://github.com/AntalphaAI) are included.

技能元数据存储于 `references/skills.json`，仅收录 AntalphaAI GitHub org 真实发布的仓库。

**13 Skills / 13 个技能：**
`web3-trader` · `poly-master` · `defillama-data-aggregator` · `wallet-balance` · `meme-token-analyzer` · `airdrop-hunter` · `wallet-guard` · `web3-investor` · `antalpha-rwa-skill` · `eth-payment` · `smart-money` · `walletconnect-requester` · `transaction-receipt`

---

## Trigger Conditions / 触发条件

Activate this skill when: / 以下情况触发本 skill：

- User mentions `web123`
- User describes a Web3 need in natural language (e.g. "I want to trade tokens", "check wallet balance")
- User says "Web3 beginner", "starter", "recommend a skill"
- User asks "what Web3 tools are there", "what skills does AntalphaAI have"
- User browses by category (e.g. "safety skills", "trading tools")

---

## Recommendation Algorithm / 推荐算法 (MVP)

### Weights / 权重

```
tags match      → +3 per match / 每次匹配 +3
scenarios match → +2 per match / 每次匹配 +2
description     → +1 per match / 每次匹配 +1
beginner keyword → +5 bonus / 新手关键词额外 +5
```

### Steps / 步骤

1. Tokenize user input / 将用户输入分词
2. Score all skills by weight + priority / 按权重 + 优先级打分
3. Return Top 3 / 返回 Top 3
4. If beginner keyword detected → return starter pack / 检测到新手词 → 返回新手套装

### Edge Cases / 边界处理

| Situation / 情况 | Action / 处理 |
|-----------------|--------------|
| No match / 无匹配 | Return `hot_skills` Top 3 / 返回热门 Top 3 |
| >3 matches | Sort by score × priority, Top 3 |
| "新手" / "beginner" | Return 新手入门套装 |
| Category browse / 分类浏览 | List all skills in that category / 列出该分类所有技能 |

---

## Execution Flow / 执行流程

### Step 1: Load Data / 加载数据

Load `references/skills.json` (relative to SKILL.md directory).
读取 `references/skills.json`（相对于 SKILL.md 目录）。

### Step 2: Detect Intent / 意图识别

| Intent / 意图 | Example / 示例 | Action / 处理 |
|--------------|---------------|--------------|
| Need match / 需求匹配 | "I want to trade" / "我想交易" | Keyword match → Top 3 |
| Beginner / 新手入门 | "Web3 beginner" / "新手入门" | Return starter pack / 返回新手套装 |
| Category browse / 分类浏览 | "Safety skills" / "安全类技能" | List category / 列出分类 |
| Exact lookup / 精确查找 | "How to install web3-trader" | Return skill detail / 返回详情 |
| Full list / 全览 | "What skills are there" / "有哪些技能" | Full matrix / 全景矩阵 |

### Step 3: Output / 输出

Use the templates below. / 按下方模板输出。

---

## Output Templates / 输出模板

### Single Skill / 单个推荐

```
🎯 Recommended / 推荐技能：{name}
📝 {description}
💡 Use cases / 使用场景：
- {example_1}
- {example_2}
📦 Install / 安装：{install}
🔗 GitHub：{github}
```

### Top 3 List / Top 3 推荐

```
🔍 Based on your need / 根据你的需求，推荐以下技能：

━━━━━━━━━━━━━━━━━━━
🥇 {name_1} — {description_1}
   💡 {scenario_1}
   📦 {install_1}

🥈 {name_2} — {description_2}
   💡 {scenario_2}
   📦 {install_2}

🥉 {name_3} — {description_3}
   💡 {scenario_3}
   📦 {install_3}
━━━━━━━━━━━━━━━━━━━
💡 Batch install / 批量安装：
openclaw skill install {github_1} {github_2} {github_3}
```

### Starter Pack / 新手套装

```
🎒 {pack_label}
{pack_description}

Includes / 包含 {count} skills:
- {skill_1} — {desc_1}
- {skill_2} — {desc_2}
- {skill_3} — {desc_3}

One-click install / 一键安装：
{install_command}
```

### Full Matrix / 全景产品矩阵

```
🌐 AntalphaAI Skills (13 total / 共 13 个)

🔄 Trading / 交易
  • web3-trader — DEX swap + Hyperliquid perpetuals / DEX聚合交易+合约
  • poly-master — Polymarket prediction market / 预测市场

💰 Investment / 投资
  • antalpha-rwa — RWA on-chain yield / RWA链上理财
  • web3-investor — DeFi/NFT portfolio / DeFi投资组合

📊 Data / 数据
  • wallet-balance — Multi-chain balance / 多链钱包余额
  • transaction-receipt — On-chain tx decoder / 链上交易解析
  • smart-money — Whale tracking / 聪明钱鲸鱼追踪
  • defillama-data-aggregator — DeFi TVL data / DeFi数据

🛡️ Safety / 安全
  • wallet-guard — Wallet approval scan / 钱包授权扫描
  • meme-token-analyzer — Meme token analysis / Meme币分析
  • airdrop-hunter — Daily airdrop intel / 空投情报日报

💳 Payment / 支付
  • eth-payment — EIP-681 payment links / 收款链接生成
  • walletconnect-requester — WalletConnect v2 / 钱包连接

💬 Tell me what you want to do, I'll recommend the best skill.
   告诉我你想做什么，我来推荐最合适的技能！
```

---

## Quick Reference / 验收速查

| User says / 用户说 | Returns / 推荐 |
|-------------------|--------------|
| "I want to trade tokens" / "我想交易代币" | web3-trader |
| "Check wallet balance" / "查钱包余额" | wallet-balance |
| "Invest in RWA" / "投资RWA" | antalpha-rwa |
| "What are whales buying" / "聪明钱在买什么" | smart-money |
| "Check for rug pull" / "检测rug pull" | wallet-guard + meme-token-analyzer |
| "Airdrop tasks" / "空投任务" | airdrop-hunter |
| "Generate payment link" / "生成收款链接" | eth-payment |
| "Web3 beginner" / "Web3新手入门" | Starter pack / 新手套装 |
| "Safety skills" / "有哪些安全工具" | Safety category / 安全分类 |
| "All skills" / "有哪些技能" | Full matrix / 全景矩阵 |
| No match / 无匹配 | Hot Top 3 |

---

## Install / 安装

```bash
# Install web123 itself / 安装 web123
openclaw skill install https://github.com/AntalphaAI/web123

# Single skill / 安装单个
openclaw skill install https://github.com/AntalphaAI/web3-trader

# Batch / 批量安装（新手包）
openclaw skill install https://github.com/AntalphaAI/wallet-balance https://github.com/AntalphaAI/web3-trader https://github.com/AntalphaAI/transaction-receipt
```

---

*Powered by Antalpha AI · web123 v1.2.0 · github.com/AntalphaAI*
