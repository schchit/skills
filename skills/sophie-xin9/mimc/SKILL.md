---
name: mimic
description: Turn your AI into anyone. Say a name — auto-collect real data from Weibo/Bilibili/Douyin/Wikipedia, analyze speech patterns and personality with statistical precision, generate SOUL.md. Data-driven character creation, not imagination-driven. Use for roleplay, personalized AI, character simulation, and creative writing. 说一个名字，自动从社交平台采集真实数据，统计分析说话风格和人格特征，生成 SOUL.md 让 AI 变成任何人。
version: 3.1.0
depends: manobrowser
---

# Mimic — 让 AI 变成任何人

> 给一个名字，造一个灵魂。从公开数据中提取任何人的人格，生成 SOUL.md 让你的 AI 像 TA 一样说话、思考、回应。

**⚠️ 这是 ClawHub 精简版。完整版（含详细采集指南、自动化脚本、模板）请从 GitHub 下载：**
**https://github.com/ClawCap/Mimic**

## 核心能力

- 🌟 **说一个名字就行** — 全自动采集微博/B站/抖音/百科公开数据
- 🔬 **数据驱动** — 口头禅 TOP5 有统计频率、平均句长有数据、书面体 vs 口语体有对比
- 🎭 **11种角色类型** — 明星/动漫角色/影视角色/历史人物/KOL/英文日文角色/身边的人
- 🔀 **角色混搭** — "70%罗永浩+30%周星驰"，结构化 SOUL.md 自由混搭
- 🔄 **一键切换** — 已生成角色可快速切换、刷新、断点续采

## 流程

```
前置检测 → 用户说名字 → 识别角色类型 → 搜索找人 → 用户确认 → 采集数据 → 数据确认 → 人格分析 → 生成 SOUL.md → 验证对话
```

## 依赖

- [ManoBrowser](https://github.com/ClawCap/ManoBrowser) — 推荐安装（自动从 GitHub 下载），不装也能用基础模式

## 完整安装

```bash
git clone https://github.com/ClawCap/Mimic.git
```

完整版包含：
- 4 个详细采集指南（社交媒体/百科台词/视频字幕/人格分析）
- 7 个自动化脚本（微博采集/风格分析/B站字幕/抖音转写等）
- SOUL.md 模板（真人/虚构/历史三变体）
- 示例角色（罗永浩/张凌赫）

## 隐私

- 只采集公开数据，不需要用户登录任何账号
- 数据全存本地 `mimic-data/` 目录
- 一键删除：删掉 `mimic-data/` 即可
