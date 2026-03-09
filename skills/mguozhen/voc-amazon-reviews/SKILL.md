---
name: voc-amazon-reviews
description: "VOC AI - Amazon 评论智能分析 Skill，为亚马逊卖家提供深度评论洞察。输入 ASIN 自动抓取评论，输出双语结构化报告：情感分析、痛点提炼、卖点发现、Listing 优化建议。Triggers: voc, amazon review analysis, 评论分析, asin分析, 亚马逊评论, voice of customer, listing优化, 痛点分析, 卖点分析"
allowed-tools: Bash
metadata:
  openclaw:
    requires:
      skills:
        - browser
    homepage: https://github.com/your-org/voc-amazon-reviews
---

# VOC AI — Amazon 评论智能分析

> 输入 ASIN，AI 自动抓取并深度分析亚马逊评论，输出双语结构化洞察报告。
> Input an ASIN, AI scrapes and analyzes Amazon reviews, outputs bilingual structured insights.

## 前置要求 / Prerequisites

确保已安装 browser skill（用于抓取评论）：

```bash
npx skills add browserbase/skills@browser
```

确保已设置 Claude API Key：

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

## 快速使用 / Quick Start

```bash
# 基础分析（默认抓取最近 100 条评论）
bash ~/.agents/skills/voc-amazon-reviews/voc.sh B08N5WRWNW

# 指定抓取数量
bash ~/.agents/skills/voc-amazon-reviews/voc.sh B08N5WRWNW --limit 200

# 指定市场（默认 amazon.com，支持 amazon.co.uk / amazon.de 等）
bash ~/.agents/skills/voc-amazon-reviews/voc.sh B08N5WRWNW --market amazon.co.uk

# 保存报告到文件
bash ~/.agents/skills/voc-amazon-reviews/voc.sh B08N5WRWNW --output report.md
```

## 输出示例 / Output Example

```
╔══════════════════════════════════════════════════════╗
║  VOC AI 分析报告 / VOC AI Analysis Report           ║
║  ASIN: B08N5WRWNW  |  分析评论: 100 条             ║
║  市场: amazon.com  |  生成时间: 2026-03-08          ║
╚══════════════════════════════════════════════════════╝

📊 情感分布 / Sentiment Distribution
  正面 Positive  ████████████░░░░  74%  (74条)
  中性 Neutral   ███░░░░░░░░░░░░░  16%  (16条)
  负面 Negative  ██░░░░░░░░░░░░░░  10%  (10条)

🔴 Top 5 痛点 / Pain Points
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 电池续航不足 / Short battery life（28条提及）
   "只用了两天电池就耗尽了，严重影响体验"
   "Battery drained in 2 days, very disappointed"

2. 连接不稳定 / Unstable connection（19条提及）
   "蓝牙经常断连，需要重新配对"
   "Bluetooth keeps disconnecting randomly"
   ...

🟢 Top 5 卖点 / Selling Points
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 音质出色 / Excellent sound quality（52条提及）
   "低音浑厚，高音清晰，性价比极高"
   "Amazing bass and crystal clear highs for the price"
   ...

💡 Listing 优化建议 / Optimization Suggestions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 【标题优化】在标题中明确标注电池容量（如 800mAh）和续航时长，
   减少因期望不匹配造成的差评
   [Title] Add battery capacity (e.g. 800mAh) and playtime to title
   to reduce negative reviews from mismatched expectations

2. 【图片优化】增加一张展示蓝牙连接范围的场景图，
   并在 A+ Content 中说明配对步骤
   [Images] Add a scene image showing Bluetooth range and add
   pairing instructions in A+ Content

3. 【bullet points】第一条 bullet 重点突出音质卖点，
   引用用户真实好评词汇如 "crystal clear" "deep bass"
   [Bullets] Lead with sound quality in first bullet,
   use authentic customer language like "crystal clear" "deep bass"
```

## 工作流程 / How It Works

```
① 输入 ASIN
      ↓
② browse CLI 打开 Amazon 评论页（支持分页）
      ↓
③ 解析评论数据（评分、正文、日期、Verified标记）
      ↓
④ Claude API 深度语义分析
      ↓
⑤ 输出双语结构化报告
```

## 脚本文件 / Scripts

| 文件 | 说明 |
|---|---|
| `voc.sh` | 主入口脚本 |
| `scraper.sh` | Amazon 评论抓取脚本（基于 browse CLI） |
| `analyze.sh` | Claude API 分析脚本 |

## 注意事项 / Notes

- Amazon 反爬机制较强，建议配置 `BROWSERBASE_API_KEY` 使用远程浏览器
- 单次分析约消耗 Claude API 2000-5000 tokens（约 $0.01-$0.03）
- 评论抓取每页约需 5-10 秒，100条约 1-2 分钟
- 请合理使用，避免频繁大量抓取同一商品

## 相关资源 / Resources

- [Amazon 卖家 Listing 优化指南](#)
- [VOC 数据如何驱动产品改进](#)
- [如何用评论数据击败竞品](#)
