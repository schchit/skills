#!/usr/bin/env python3
"""
hnews — Markdown → 科技新闻网页转换器
将 Markdown 格式的新闻列表转换为暗色主题的精美 HTML 网页。
"""

import argparse
import html as html_mod
import os
import re
import sys
from datetime import datetime


def parse_markdown(text: str) -> dict:
    """解析 Markdown 新闻文件，返回结构化数据。"""
    lines = text.strip().split('\n')
    title = '科技新闻'
    snapshot = ''
    items = []

    i = 0
    # 提取标题
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('# '):
            title = line[2:].strip()
            i += 1
            break
        i += 1

    # 提取时间戳
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('*') and line.endswith('*'):
            snapshot = line.strip('*').strip()
            i += 1
            break
        if re.match(r'\d+\.', line):
            break
        i += 1

    # 提取新闻条目
    total_points = 0
    total_comments = 0

    while i < len(lines):
        line = lines[i].strip()
        m = re.match(r'(\d+)\.\s+\[(.+?)\]\((.+?)\)(?:\s+\((.+?)\))?', line)
        if m:
            rank = int(m.group(1))
            item_title = m.group(2)
            url = m.group(3)
            source = m.group(4) or ''

            # 下一行可能是元数据
            points = 0
            author = ''
            comments = ''
            if i + 1 < len(lines):
                meta_line = lines[i + 1].strip()
                pm = re.search(r'(\d+)\s*points?', meta_line)
                #am = re.search(r'@?(\w[\w-]*)', meta_line)
                am = re.search(r"\|\s*([^|]+?)\s*\|", meta_line)
                cm = re.search(r'(\d+)\s*评论', meta_line)
                if not cm:
                    cm = re.search(r'(\d+)\s*comments?', meta_line)
                if pm:
                    points = int(pm.group(1))
                    total_points += points
                if cm:
                    comments = cm.group(1)
                    total_comments += int(comments)
                # author: 取 points 后的第一个 @xxx 或单词
                if not am:
                    am = re.search(r'by\s+(\S+)', meta_line)
                if am:
                    author = am.group(1)
                if pm or am or cm:
                    i += 1
            
            items.append({
                'rank': rank,
                'title': item_title,
                'url': url,
                'source': source,
                'points': points,
                'author': author,
                'comments': comments,
            })
        i += 1

    return {
        'title': title,
        'snapshot': snapshot,
        'items': items,
        'total_points': total_points,
        'total_comments': total_comments,
    }


CSS = """\
:root {
  --bg: #0d1117;
  --card-bg: #161b22;
  --card-hover: #1c2333;
  --accent: #ff6600;
  --accent-dim: #ff660033;
  --text: #e6edf3;
  --text-muted: #8b949e;
  --border: #30363d;
  --green: #3fb950;
  --blue: #58a6ff;
  --purple: #bc8cff;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans SC', sans-serif;
  line-height: 1.6;
  min-height: 100vh;
}
.header {
  background: linear-gradient(135deg, #1a1207 0%, #2a1505 50%, #1a1207 100%);
  border-bottom: 1px solid var(--border);
  padding: 2rem 0;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.header::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(ellipse at 50% 0%, var(--accent-dim) 0%, transparent 70%);
  pointer-events: none;
}
.header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--accent);
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: .6rem;
}
.header h1 .logo {
  width: 36px; height: 36px;
  border: 2px solid var(--accent);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 1.1rem;
}
.header .meta {
  color: var(--text-muted);
  font-size: .85rem;
  margin-top: .5rem;
  position: relative;
}
.header .stats {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-top: 1rem;
  position: relative;
}
.header .stat { text-align: center; }
.header .stat .num {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent);
}
.header .stat .label {
  font-size: .75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: .05em;
}
.container {
  max-width: 820px;
  margin: 0 auto;
  padding: 1.5rem 1rem 3rem;
}
.news-card {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 1.2rem;
  margin-bottom: .5rem;
  border-radius: 10px;
  background: var(--card-bg);
  border: 1px solid var(--border);
  transition: all .2s ease;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
}
.news-card:hover {
  background: var(--card-hover);
  border-color: var(--accent);
  transform: translateX(4px);
  box-shadow: -4px 0 0 var(--accent), 0 4px 20px rgba(255,102,0,.1);
}
.rank {
  flex-shrink: 0;
  width: 36px; height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: .85rem;
  border-radius: 8px;
  background: var(--accent-dim);
  color: var(--accent);
}
.news-card:nth-child(-n+3) .rank {
  background: var(--accent);
  color: #fff;
}
.card-body { flex: 1; min-width: 0; }
.card-title {
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.4;
  color: var(--text);
  display: block;
}
.news-card:hover .card-title { color: var(--accent); }
.card-source {
  display: inline-block;
  font-size: .75rem;
  color: var(--blue);
  background: rgba(88,166,255,.1);
  padding: .1rem .45rem;
  border-radius: 4px;
  margin-left: .5rem;
  vertical-align: middle;
  font-weight: 500;
}
.card-meta {
  display: flex;
  gap: 1rem;
  margin-top: .4rem;
  font-size: .8rem;
  color: var(--text-muted);
  flex-wrap: wrap;
}
.card-meta .points { color: var(--accent); font-weight: 600; }
.card-meta .author { color: var(--purple); }
.card-meta .comments { color: var(--green); }
.news-card.job { border-left: 3px solid var(--text-muted); }
.news-card.job .card-title { color: var(--text-muted); }
.footer {
  text-align: center;
  padding: 2rem 0;
  color: var(--text-muted);
  font-size: .8rem;
  border-top: 1px solid var(--border);
}
.footer a { color: var(--blue); text-decoration: none; }
@media (max-width: 600px) {
  .header h1 { font-size: 1.4rem; }
  .news-card { padding: .8rem; gap: .7rem; }
  .rank { width: 30px; height: 30px; font-size: .75rem; }
  .card-title { font-size: .9rem; }
  .header .stats { gap: 1.2rem; }
}\
"""


def build_card(item: dict) -> str:
    """生成单条新闻的 HTML 卡片。"""
    e = html_mod.escape
    title = e(item['title'])
    url = e(item['url'])
    rank = item['rank']

    source_html = ''
    if item['source']:
        source_html = f'<span class="card-source">{e(item["source"])}</span>'

    meta_parts = []
    if item['points']:
        meta_parts.append(f'<span class="points">{item["points"]} points</span>')
    if item['author']:
        meta_parts.append(f'<span class="author">@{item["author"]}</span>')
    if item['comments']:
        meta_parts.append(f'<span class="comments">{item["comments"]} 评论</span>')
    meta_html = '\n      '.join(meta_parts)

    return f'''\
<a class="news-card" href="{url}" target="_blank" rel="noopener">
  <div class="rank">{rank}</div>
  <div class="card-body">
    <span class="card-title">{title}{source_html}</span>
    <div class="card-meta">
      {meta_html}
    </div>
  </div>
</a>'''


def render_html(data: dict) -> str:
    """将解析后的数据渲染为完整 HTML 页面。"""
    e = html_mod.escape
    title = e(data['title'])
    snapshot = e(data['snapshot'])
    count = len(data['items'])
    tp = data['total_points']
    tc = data['total_comments']

    # logo 首字母
    logo_char = title[0].upper() if title else 'N'

    cards = '\n\n'.join(build_card(item) for item in data['items'])

    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    return f'''\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
{CSS}
</style>
</head>
<body>

<div class="header">
  <h1><span class="logo">{e(logo_char)}</span> {title}</h1>
  <div class="meta">{snapshot}</div>
  <div class="stats">
    <div class="stat"><div class="num">{count}</div><div class="label">条新闻</div></div>
    <div class="stat"><div class="num">{tp:,}</div><div class="label">总得分</div></div>
    <div class="stat"><div class="num">{tc:,}</div><div class="label">评论数</div></div>
  </div>
</div>

<div class="container">

{cards}

</div>

<div class="footer">
  由 hnews 技能自动生成 · {now}
</div>

</body>
</html>
'''


def main():
    parser = argparse.ArgumentParser(
        description='hnews — Markdown → 科技新闻网页转换器'
    )
    parser.add_argument('input', help='输入 Markdown 文件路径')
    parser.add_argument('-o', '--output', help='输出 HTML 文件路径')
    parser.add_argument('--title', help='自定义页面标题')
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f'错误: 文件不存在 — {args.input}', file=sys.stderr)
        sys.exit(1)

    with open(args.input, 'r', encoding='utf-8') as f:
        text = f.read()

    data = parse_markdown(text)

    if args.title:
        data['title'] = args.title

    if not data['items']:
        print('警告: 未解析到任何新闻条目，请检查 Markdown 格式。', file=sys.stderr)
        sys.exit(1)

    output_path = args.output
    if not output_path:
        base, _ = os.path.splitext(args.input)
        output_path = base + '.html'

    html_str = render_html(data)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_str)

    print(f'[OK] 已生成: {output_path}')
    print(f'   {len(data["items"])} 条新闻 · {data["total_points"]:,} 总得分 · {data["total_comments"]:,} 评论')


if __name__ == '__main__':
    main()
