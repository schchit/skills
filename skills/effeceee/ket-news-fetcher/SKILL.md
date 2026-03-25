---
name: ket-news-fetcher
description: 抓取KET级别英语新闻文章并生成PDF学习材料
author:
  name: Maosi English Team
  github: https://github.com/effecE
homepage: https://clawhub.com
license: Apache-2.0
metadata:
  {
    "openclaw":
      {
        "version": "1.2.0",
        "emoji": "📰",
        "tags": ["english", "news", "KET", "learning", "education", "pdf"],
        "requires": { "bins": ["python3"] },
        "install":
          [
            {
              "id": "pip",
              "kind": "pip",
              "package": "requests-html",
              "label": "Install requests-html (for JavaScript rendering)",
            },
            {
              "id": "pip",
              "kind": "pip",
              "package": "beautifulsoup4",
              "label": "Install beautifulsoup4",
            },
            {
              "id": "pip",
              "kind": "pip",
              "package": "reportlab",
              "label": "Install reportlab (for PDF generation)",
            },
          ],
      },
  }
---

# KET News Fetcher - 英语新闻PDF生成器

抓取KET级别英语新闻，生成可打印的PDF学习材料。

## 支持来源

| 来源 | 难度 | 说明 |
|------|------|------|
| BBC Learning English | KET-PET | BBC官方学习内容 |
| VOA Learning English | KET | 美国之音慢速英语 |
| News in Levels 1 | KET | 基础英语新闻 |

## 工具脚本

### 1. ket_news_fetcher.py - 新闻列表获取

```bash
# 获取BBC新闻
python3 ket_news_fetcher.py --source bbc --count 5

# 获取所有来源
python3 ket_news_fetcher.py --source all --count 10
```

### 2. ket_news_pdf.py - PDF生成

```bash
# 生成BBC新闻PDF
python3 ket_news_pdf.py --source bbc --count 3 --output daily_news.pdf

# 生成所有来源PDF
python3 ket_news_pdf.py --source all --count 3 --output /tmp/daily_english_news.pdf
```

## PDF内容

每个PDF包含：
- 📰 新闻来源标题
- 📝 文章标题
- 📊 词汇分析（KET覆盖率）
- 🔤 生词标注

## 输出格式

```
Daily English News PDF/
├── 标题：Daily English News
├── 日期：2026-03-25
├── 来源1：BBC Learning English
│   ├── 标题
│   ├── 难度级别
│   ├── 词汇分析
│   └── 文章内容摘要
├── 来源2：VOA Learning English
│   └── ...
└── 词汇统计
```

## 技术实现

- requests-html: JavaScript渲染
- BeautifulSoup: HTML解析
- reportlab: PDF生成
- KET词汇表: 1500+词

## License
Apache License 2.0
