---
name: NewsToday
description: 每日中文新闻推送 Skill — 早8点早报（10条精选新闻+摘要）+ 晚8点收官快报，一键订阅自动送达。聚合微博/知乎/百度/抖音/36氪热榜，话题追踪持续跟进事件最新进展，分类速览（科技/财经/娱乐/体育/社会/国际）。每条新闻附可读摘要与来源，不只是标题列表。无需注册，无个人档案。触发词：早报、晚报、今日新闻、新闻摘要、热榜、热搜、追踪、最新消息、微博热搜、知乎热榜、科技新闻、财经新闻、头条、订阅新闻。/ Chinese daily news push skill — morning briefing (8am, 10 curated news with summaries) + evening recap (8pm), auto-delivered. Multi-platform trending (Weibo/Zhihu/Baidu/Douyin/36Kr). Topic tracking, category browse. Readable summaries, not just titles. No registration.
keywords: 新闻推送, 早报, 新闻摘要, 每日新闻, 今日新闻, 热榜, 热搜, 订阅新闻, 晚报, 微博热搜, 知乎热榜, 百度热搜, 头条, 科技新闻, 财经新闻, 娱乐新闻, 体育新闻, 社会新闻, 国际新闻, 话题追踪, 最新消息, 资讯, news push, daily briefing, news summary, Chinese news, morning briefing, evening news, trending, hot topics, topic tracking, news aggregator, Weibo trending, Zhihu hot
metadata:
  openclaw:
    runtime:
      node: ">=18"
---

# NewsToday

> 私人新闻助手 — 早报 · 热榜 · 分类速览 · 话题追踪

## 何时使用

- 用户说"早报""今天新闻""新闻摘要""今天发生了什么"
- 用户问"热搜""微博热榜""知乎热榜"
- 用户想看某类新闻：科技、财经、娱乐、体育、社会、国际
- 用户说"追踪 XX""XX 最新消息""XX 怎么样了"
- 用户说"开启推送""订阅早报""每天推新闻"

---

## 🌐 语言规则

- 默认中文；用户英文提问切英文
- 新闻标题保留原文，摘要用回复语言改写

---

## 📋 功能说明

### 早报
搜索：今日重要新闻 + 国际新闻 + 财经新闻，去重后选 10 条覆盖不同领域（重要/财经/国际/科技/社会各至少 1 条），每条含标题、来源、2 句摘要，按领域分组输出。

### 热榜聚合
搜索微博热搜 + 知乎热榜 + 百度热搜，去重合并，标注来源平台，多平台共同热点置顶。

### 分类浏览

| 分类 | 搜索词 |
|------|--------|
| 科技 | 科技新闻 今日、AI新闻 |
| 财经 | 财经新闻 今日、股市 |
| 娱乐 | 娱乐新闻 今日、明星动态 |
| 体育 | 体育新闻 今日、赛事结果 |
| 社会 | 社会新闻 今日、民生 |
| 国际 | 国际新闻 今日、外交 |

输出 5-8 条，每条含标题、来源、时间、2-3 句摘要。

### 话题追踪
搜索：`{关键词} 最新 {日期}` + `{关键词} 进展` + `{关键词} 官方回应`，整理时间线输出（时间倒序），含各方反应。

### 深读
用户回复序号或说"详细说说 XX"时，搜索更多报道，交叉验证，呈现详细经过、各方反应、延伸阅读。

---

## 🔔 每日推送

```bash
node scripts/push-toggle.js on <userId> [--morning 08:00] [--evening 20:00] [--channel telegram]
node scripts/push-toggle.js off <userId>
node scripts/push-toggle.js status <userId>
```

支持渠道：`telegram` / `feishu` / `slack` / `discord`

---

## ⚠️ 注意事项

1. 每条新闻必须标注来源媒体
2. 涉及争议内容呈现多方视角，不做立场判断
3. 不开启推送时无任何数据写入；开启后仅存储推送偏好（`data/users/<userId>.json`），不含个人信息或新闻内容
4. 搜索结果受 WebSearch 实时性限制，部分新闻可能有数小时延迟
