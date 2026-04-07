---
name: simple-websearch
description: 极简网络搜索技能 - 优先 Exa AI (OpenCode 同款)，备用百度/必应
version: 1.1.0
author: 鸭鸭 (Yaya)
license: MIT
tags:
  - search
  - web
  - internet
  - exa
  - opencode
  - lightweight
emoji: 🔍
---

# Simple Web Search Skill

极简网络搜索技能，无需任何 API Key，开箱即用。

## 特点

- 🚀 **Exa AI 优先** - OpenCode 同款搜索接口，免费无需 API Key
- 🔍 **多引擎备用** - Exa → 必应 → 百度，自动降级保证有结果
- 🎯 **结果精准** - 优化过的正则提取，过滤广告
- 📦 **开箱即用** - 无需配置，安装即可搜索
- ⚡ **轻量快速** - 仅需 `requests` 一个 Python 依赖

## 搜索引擎策略

1. **Exa AI 优先** - OpenCode 同款，免费、快速、质量好
2. **必应备用** - Exa 无结果时自动切换
3. **百度补充** - 中文内容补充

## 使用方法

### 基本搜索

```python
result = main({
    "action": "search",
    "query": "Python 教程",
    "num_results": 5
})
```

### 命令行

```bash
python scripts/search.py "搜索关键词"
python scripts/search.py "搜索关键词" 10  # 指定结果数量
```

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| action | string | 是 | 操作类型：`search` |
| query | string | 是 | 搜索关键词 |
| num_results | int | 否 | 结果数量，默认 5，最大 20 |

## 输出格式

```json
{
    "success": true,
    "query": "搜索关键词",
    "engine": "baidu+bing",
    "num_results": 5,
    "results": [
        {
            "title": "结果标题",
            "href": "https://...",
            "body": "摘要内容"
        }
    ],
    "message": "搜索完成"
}
```

## 示例

### 示例 1：搜索新闻

```python
result = main({
    "action": "search",
    "query": "AI 最新进展 2026",
    "num_results": 8
})

if result["success"]:
    for r in result["results"]:
        print(f"- {r['title']}: {r['href']}")
```

### 示例 2：搜索股票信息

```python
result = main({
    "action": "search",
    "query": "三六零 601360 股价",
    "num_results": 5
})
```

## 搜索引擎策略

1. **百度优先** - 中文内容更准确
2. **必应备用** - 百度无结果时自动切换
3. **广告过滤** - 自动过滤 IP 地址、推广链接

## 依赖

仅需一个 Python 包：

```bash
pip install requests
```

## 与 web-search-ex-skill 的区别

| 特性 | simple-websearch | web-search-ex-skill |
|------|------------------|---------------------|
| 依赖 | requests | requests + baidusearch + crawl4ai + playwright |
| 安装大小 | ~100KB | ~200MB+ |
| 启动速度 | 毫秒级 | 秒级（Playwright 冷启动） |
| 搜索深度 | 基础搜索 | 支持深度搜索/爬虫 |
| 适用场景 | 日常快速搜索 | 需要抓取网页详情 |

## 注意事项

1. 首次运行会自动安装 `requests`
2. 搜索结果可能因网络环境而异
3. 建议单次查询不超过 10 条结果

---

_简洁，但不简单。_ 🦆
