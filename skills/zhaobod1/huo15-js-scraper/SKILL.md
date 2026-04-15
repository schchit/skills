---
name: huo15-js-scraper
description: JavaScript渲染网站抓取工具。当需要抓取JS渲染的页面（如企微文档、Vue/React SPA）、绕过反爬、或者普通curl/wget/web_fetch无法获取内容的网站时使用此技能。支持Playwright和scrapling双引擎自动切换。
identifier: huo15-js-scraper
version: 1.0.0
author: 贾维斯
category: web-scraping
---

# huo15-js-scraper

JavaScript渲染网站抓取技能，支持Playwright和scrapling双引擎。

## 快速使用

```bash
# 基本用法（自动选择引擎）
python3 ~/.openclaw/workspace/skills/huo15-js-scraper/scripts/scrape.py <URL>

# 指定选择器
python3 ~/.openclaw/workspace/skills/huo15-js-scraper/scripts/scrape.py <URL> --selector ".content"

# 输出JSON
python3 ~/.openclaw/workspace/skills/huo15-js-scraper/scripts/scrape.py <URL> --output json

# 强制使用scrapling引擎
python3 ~/.openclaw/workspace/skills/huo15-js-scraper/scripts/scrape.py <URL> --engine scrapling
```

## 引擎选择策略

| 场景 | 推荐引擎 |
|------|---------|
| 企微文档 / 微信相关 | Playwright |
| Cloudflare保护站 | scrapling (stealth) |
| Vue/React SPA | Playwright |
| 简单静态页 | scrapling (basic) |
| 未知站 | Playwright（更稳定） |

## Python API

```python
from huo15_js_scraper import scrape

# 方式1：自动选择（推荐）
result = scrape('https://example.com')
print(result['content'])

# 方式2：强制Playwright
result = scrape('https://developer.work.weixin.qq.com/document/path/91756', engine='playwright')
```

## 企业微信文档知识库

已构建完整的企微官方文档知识库，位于：
`~/workspace/knowledge-base/企业微信文档/`

### 知识库结构

```
企业微信文档/
├── README.md (索引)
├── 01-快速入门/      - 开发前必读
├── 02-服务端API/     - 通讯录、消息、客户联系、企业支付...
├── 03-客户端API/     - 小程序API、JS-SDK
├── 04-工具资源/       - WeUI、错误码、频率限制
└── 99-附录/          - FAQ、更新日志
```

### 更新企微文档知识库

```bash
# 列出所有可抓取文档
python3 ~/.openclaw/workspace/skills/huo15-js-scraper/scripts/wecom_docs_scraper.py --list

# 抓取单个文档
python3 ~/.openclaw/workspace/skills/huo15-js-scraper/scripts/wecom_docs_scraper.py --path-id 90556 --category "01-快速入门" --title "快速入门"

# 批量抓取（更新全部52个文档）
python3 ~/.openclaw/workspace/skills/huo15-js-scraper/scripts/wecom_docs_scraper.py --all
```

### 核心文档

| 文档 | 路径ID | 说明 |
|------|--------|------|
| 快速入门 | 90556 | 开发前必读 |
| 获取access_token | 91039 | API认证基础 |
| 发送应用消息 | 90235 | 消息推送核心 |
| 创建成员 | 90195 | 通讯录管理 |
| 客户联系概述 | 92109 | 客户管理基础 |
| JS-SDK签名算法 | 90506 | 前端开发必备 |

## 常见问题

### Q: 企微文档怎么抓？
```bash
python3 ~/.openclaw/workspace/skills/huo15-js-scraper/scripts/scrape.py \
  "https://developer.work.weixin.qq.com/document/path/91756" \
  --wait 5
```

### Q: 提示playwright未安装？
```bash
pip3 install playwright --break-system-packages
playwright install chromium
```

### Q: scrapling安装？
```bash
pip3 install "scrapling[all]" --break-system-packages
scrapling install
```

### Q: 内容为空或获取到跳转页面？
增加 `--wait` 时间，让JS有更多时间渲染：
```bash
python3 ...scrape.py <URL> --wait 5
```

## 依赖安装

```bash
# Playwright（主引擎）
pip3 install playwright --break-system-packages
playwright install chromium

# scrapling（降级引擎）
pip3 install "scrapling[all]" --break-system-packages
scrapling install
```

## 工作原理

1. 优先使用 Playwright（chromium headless）加载页面，等待networkidle
2. 等待指定时间让JS渲染完成
3. 通过CSS选择器提取内容
4. 如果Playwright失败，自动降级到scrapling
