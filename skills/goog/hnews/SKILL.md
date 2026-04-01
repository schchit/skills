# hnews — Markdown → 科技新闻网页

将 Markdown 格式的新闻列表（如 Hacker News 快照）转换为暗色主题的精美 HTML 网页。

## 使用方式

```bash
python scripts/hnews.py INPUT.md -o OUTPUT.html
```

- `INPUT.md` — Markdown 新闻文件（支持 `N. [Title](url) (source)` 格式）
- `-o OUTPUT.html` — 输出 HTML 路径（默认同目录下同名 `.html`）
- `--title "自定义标题"` — 页面标题（默认从文件推断）

## Markdown 输入格式

```markdown
# Hacker News Front Page

*Snapshot: 2026-03-29 ~14:35 CST*

1. [Title Here](https://example.com) (example.com)
   123 points | author | 45 comments

2. [Another Title](https://foo.com) (foo.com)
   67 points | someone | 8 comments
```

## 触发条件

用户说「生成新闻网页」「hnews」时使用

## 依赖

- Python 3.6+（无第三方依赖）
