#!/usr/bin/env python3
"""
Daily English News PDF - 精美排版版
"""

import os
import re
import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime
from fpdf import FPDF

try:
    from requests_html import AsyncHTMLSession
    from bs4 import BeautifulSoup
except ImportError:
    pass

# BBC News RSS - 时事新闻
BBC_RSS = "https://feeds.bbci.co.uk/news/rss.xml"

# 中文字体路径
FONT_PATH = "/usr/share/fonts/google-noto-cjk/NotoSansCJK-DemiLight.ttc"

# 缓存翻译结果
TRANS_CACHE = {}


def get_translation(word):
    """获取单词翻译 - 使用Google翻译API"""
    global TRANS_CACHE
    
    if word.lower() in TRANS_CACHE:
        return TRANS_CACHE[word.lower()]
    
    import urllib.request
    import json
    import time
    
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q={word}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            result = response.read().decode('utf-8')
            data = json.loads(result)
            if data and data[0] and data[0][0]:
                translation = data[0][0][0]
                TRANS_CACHE[word.lower()] = translation
                time.sleep(0.1)
                return translation
    except:
        pass
    return ""


def get_rss_articles(rss_url, count=4):
    try:
        import urllib.request
        req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8')
        
        root = ET.fromstring(content)
        articles = []
        
        for item in root.findall('.//item')[:count]:
            title = item.find('title')
            link = item.find('link')
            if title is not None and link is not None:
                articles.append({
                    "title": title.text or "No title",
                    "url": link.text or ""
                })
        
        return articles
    except Exception as e:
        print(f"RSS Error: {e}")
        return []


async def fetch_article(url, session):
    try:
        r = await session.get(url, timeout=20)
        await r.html.arender(timeout=20)
        return r.html.html
    except:
        return ""


def extract_text(html):
    """提取文章内容 - 获取更多段落"""
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    for t in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        t.decompose()
    
    paras = []
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        # 过滤掉太短的内容
        if len(text) > 50:
            paras.append(text)
    
    return paras[:8]  # 返回更多段落


def analyze_vocab(text):
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    total = len(words)
    # 提取有意义的生词
    non_ket = [w for w in set(words) if len(w) > 3][:20]
    
    return {
        "total": total,
        "new_words": non_ket
    }


def draw_header(pdf):
    """绘制精美标题"""
    # 渐变背景色块
    pdf.set_fill_color(25, 55, 135)  # 深蓝色
    pdf.rect(0, 0, 210, 45, 'F')
    
    # 装饰线
    pdf.set_fill_color(255, 193, 7)  # 金色
    pdf.rect(0, 45, 210, 3, 'F')
    
    # 主标题
    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(8)
    pdf.cell(0, 15, 'Daily English News', ln=True, align='C')
    
    # 副标题
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(200, 220, 255)
    pdf.cell(0, 8, 'English Team', ln=True, align='C')
    
    # 日期
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(180, 200, 240)
    pdf.cell(0, 6, datetime.now().strftime('%Y-%m-%d'), ln=True, align='C')


def draw_word_card(pdf, word, translation, index):
    """绘制单词卡片"""
    card_width = 88
    card_height = 12
    
    # 计算位置
    col = index % 2
    row = index // 2
    x = 11 + col * 92
    y = pdf.get_y() + row * 14
    
    # 卡片背景
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(200, 210, 220)
    pdf.rect(x, y, card_width, card_height, 'FD')
    
    # 单词
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(30, 80, 150)
    pdf.set_xy(x + 3, y + 2)
    pdf.cell(35, 5, word[:12], ln=0)
    
    # 翻译
    pdf.set_font('Chinese', '', 9)
    pdf.set_text_color(80, 80, 80)
    pdf.set_xy(x + 40, y + 2)
    pdf.cell(45, 5, translation[:10], ln=0)


def draw_exercises(pdf, article_title, article_keywords):
    """绘制多样化练习"""
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(30, 55, 135)
    pdf.cell(0, 8, 'Exercises', ln=True)
    
    # 生成多样化练习
    import random
    
    exercises = []
    
    # 1. True or False
    short_title = article_title[:70] if len(article_title) > 70 else article_title
    exercises.append(f"1. True or False: {short_title}...")
    
    # 2. 填空题
    if any(k in article_keywords for k in ['hospital', 'health', 'medical']):
        exercises.append("2. The hospital waited _____ days before raising the alarm.")
    elif any(k in article_keywords for k in ['government', 'political', 'election']):
        exercises.append("2. _____ announced the new policy yesterday.")
    elif any(k in article_keywords for k in ['tech', 'google', 'apple', 'ai']):
        exercises.append("2. _____ company made a major announcement.")
    elif any(k in article_keywords for k in ['attack', 'war', 'military']):
        exercises.append("2. A _____ attack happened in the city.")
    else:
        exercises.append("2. The main event happened in _____ (place/name).")
    
    # 3. 单选题
    exercises.append("3. What was the main purpose of this article?")
    exercises.append("   A. To inform  B. To persuade  C. To entertain  D. To advertise")
    
    # 4. 搭配题
    exercises.append("4. Match the words with their meanings:")
    for i, kw in enumerate(article_keywords[:4], 1):
        cn = get_translation(kw)
        exercises.append(f"   {i}. {kw:<15} - _____ ({cn})")
    
    # 5. 讨论题
    exercises.append("5. Discussion: What would you do if you were in this situation?")
    
    pdf.set_font('Chinese', '', 9)
    pdf.set_text_color(60, 60, 60)
    for ex in exercises:
        pdf.cell(0, 6, ex, ln=True)


def create_pdf(articles, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('Chinese', '', FONT_PATH)
    
    # 精美标题
    draw_header(pdf)
    pdf.ln(10)
    
    for i, art in enumerate(articles):
        vocab = art.get('vocab', {})
        new_words = vocab.get('new_words', [])
        paras = art.get('paras', [])
        
        # 文章标题区域
        pdf.set_fill_color(245, 247, 255)
        pdf.set_draw_color(180, 200, 240)
        pdf.rect(10, pdf.get_y(), 190, 35, 'FD')
        
        # 文章编号和标题
        pdf.set_font('Helvetica', 'B', 13)
        pdf.set_text_color(25, 55, 135)
        pdf.set_xy(15, pdf.get_y() + 3)
        pdf.cell(0, 7, f"Article {i+1}", ln=True)
        
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(40, 40, 40)
        pdf.set_x(15)
        pdf.multi_cell(180, 6, art.get('title', 'N/A'), ln=True)
        
        pdf.ln(5)
        
        # 文章内容 - 更长更完整
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(50, 50, 50)
        
        full_text = ' '.join(paras)
        # 显示更多内容
        display_text = full_text[:800] + "..." if len(full_text) > 800 else full_text
        
        # 分段显示
        for para in paras[:5]:
            text = para[:180] + "..." if len(para) > 180 else para
            pdf.multi_cell(0, 5.5, text)
            pdf.ln(2)
        
        pdf.ln(5)
        
        # 生词表标题
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(25, 55, 135)
        pdf.cell(0, 8, f"Vocabulary ({len(new_words)} words)", ln=True)
        
        # 绘制单词卡片
        start_y = pdf.get_y() + 2
        for idx, w in enumerate(new_words[:8]):
            cn = get_translation(w)
            draw_word_card(pdf, w, cn, idx)
        
        pdf.set_y(start_y + 14 * 4 + 5)
        
        # 绘制练习
        draw_exercises(pdf, art.get('title', ''), new_words[:8])
        
        # 分隔线
        pdf.ln(8)
        pdf.set_draw_color(200, 210, 230)
        pdf.set_line_width(0.5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(8)
        
        # 分页
        if i < len(articles) - 1:
            pdf.add_page()
            # 页面顶部小标题
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(0, 6, f"Daily English News - Article {i+2}", ln=True)
            pdf.ln(3)
    
    pdf.output(output_path)
    return True


async def main():
    pdf_output = '/tmp/daily_english_news.pdf'
    
    print("="*50)
    print("Daily English News PDF Generator - Premium Edition")
    print("="*50)
    
    session = AsyncHTMLSession()
    
    print("\nFetching BBC News RSS...")
    articles = get_rss_articles(BBC_RSS, count=4)
    print(f"Found {len(articles)} articles")
    
    all_articles = []
    
    for i, art in enumerate(articles):
        print(f"\n[{i+1}] {art['title'][:50]}...")
        html = await fetch_article(art['url'], session)
        paras = extract_text(html)
        
        if paras:
            text = ' '.join(paras)
            vocab = analyze_vocab(text)
            art['paras'] = paras
            art['vocab'] = vocab
            all_articles.append(art)
            print(f"    OK: {vocab['total']} words, {len(vocab.get('new_words', []))} new words")
    
    if not all_articles:
        print("No articles!")
        return
    
    print(f"\nGenerating PDF...")
    print(f"Translation cache: {len(TRANS_CACHE)} words")
    
    if create_pdf(all_articles, pdf_output):
        print(f"PDF: {pdf_output}")
        dest = "/root/.openclaw/workspace-explodegao/english-audio/daily_english_news.pdf"
        import shutil
        shutil.copy(pdf_output, dest)
        print(f"Copied to: {dest}")


if __name__ == "__main__":
    asyncio.run(main())
