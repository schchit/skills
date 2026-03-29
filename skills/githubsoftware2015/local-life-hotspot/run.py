#!/usr/bin/env python3
"""
干货内容搜索 + 创作工具 - v3.0
搜索具体的干货内容（技巧、方法、经验），创作有价值的小红书文章
"""

import json
import urllib.request
import ssl
import argparse
from datetime import datetime
from pathlib import Path

# 忽略 SSL 证书验证
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def fetch_jina_search(query):
    """使用 Jina Search API 搜索"""
    try:
        url = f"https://s.jina.ai/{urllib.request.quote(query)}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=20, context=ssl_context) as response:
            data = json.loads(response.read().decode())
            return data.get('data', [])
    except Exception as e:
        print(f"⚠️  搜索失败：{e}")
        return []

def fetch_jina_read(url):
    """使用 Jina Reader 读取网页内容"""
    try:
        read_url = f"https://r.jina.ai/{url}"
        req = urllib.request.Request(read_url, headers={"Accept": "text/markdown"})
        with urllib.request.urlopen(req, timeout=20, context=ssl_context) as response:
            return response.read().decode()[:5000]
    except Exception as e:
        return f"读取失败：{e}"

def extract_tips_from_content(content, keyword):
    """从内容中提取干货技巧"""
    tips = []
    lines = content.split('\n')
    
    current_tip = ""
    for line in lines:
        line = line.strip()
        # 识别技巧格式：数字、符号、关键词
        if any([
            line and line[0].isdigit() and '.' in line[:3],  # 1. 2. 3.
            line.startswith('•') or line.startswith('-'),    # 列表
            '技巧' in line or '方法' in line or '建议' in line,
            '首先' in line or '其次' in line or '最后' in line,
        ]) and len(line) > 10:
            if current_tip:
                tips.append(current_tip)
            current_tip = line[:200]  # 限制长度
    
    if current_tip:
        tips.append(current_tip)
    
    return tips[:10]  # 最多 10 条

def create_detailed_content(keyword, tips, top_resources):
    """创作详细的干货内容"""
    
    # 分类 emoji
    emojis = {
        '职场': '💼', '学习': '📚', '科技': '💻', '美食': '🍔',
        '旅游': '✈️', '生活': '✨', '时尚': '👗', '健身': '💪',
        '技能': '🛠️', '效率': '⚡', '沟通': '💬', '时间': '⏰'
    }
    
    emoji = None
    for cat, e in emojis.items():
        if cat in keyword:
            emoji = e
            break
    if not emoji:
        emoji = '📌'
    
    # 生成标题
    title = f"{emoji} {keyword}：{len(tips)}个超实用的技巧/方法"
    
    # 生成详细内容
    content = f"""【{keyword}】超全干货整理

📝 整理了{len(tips)}个超实用的{keyword}技巧，建议收藏！

━━━━━━━━━━━━━━━━

"""
    
    # 添加具体技巧
    for i, tip in enumerate(tips[:8], 1):
        content += f"{i}. {tip}\n\n"
    
    content += """━━━━━━━━━━━━━━━━

💡 核心要点：
- 以上技巧都经过实践验证
- 建议先从最简单的开始尝试
- 坚持执行才能看到效果

📌 行动建议：
1. 收藏本文，方便随时查看
2. 选择 1-2 个技巧立即开始实践
3. 在评论区分享你的实践经验

👇 互动话题：
你在{keyword}方面有什么经验？欢迎在评论区分享！

#{keyword} #干货分享 #实用技巧 #经验分享 #成长"""

    return {
        "title": title[:20],  # 小红书标题限制 20 字
        "content": content,
        "tags": [f"#{keyword}", "#干货分享", "#实用技巧", "#经验分享"],
        "tips_count": len(tips)
    }

def publish_to_xiaohongshu(title, content):
    """发布到小红书"""
    import subprocess
    from PIL import Image, ImageDraw, ImageFont
    
    # 生成封面图
    try:
        width, height = 1080, 1440
        img = Image.new('RGB', (width, height), color=(100, 150, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            font = ImageFont.load_default()
            small_font = font
        
        text1 = f"📌 {title[:15]}"
        text2 = "超全干货整理"
        
        bbox1 = draw.textbbox((0, 0), text1, font=font)
        x1 = (width - (bbox1[2] - bbox1[0])) // 2
        y1 = height // 2 - 60
        
        bbox2 = draw.textbbox((0, 0), text2, font=small_font)
        x2 = (width - (bbox2[2] - bbox2[0])) // 2
        y2 = height // 2 + 20
        
        draw.text((x1, y1), text1, fill=(255, 255, 255), font=font)
        draw.text((x2, y2), text2, fill=(255, 255, 255), font=small_font)
        
        output_path = "/tmp/xiaohongshu-cover.jpg"
        img.save(output_path, quality=90)
        images = [output_path]
    except Exception as e:
        print(f"⚠️  图片生成失败：{e}")
        images = []
    
    # 调用小红书 MCP 发布
    cmd = f"mcporter call \"xiaohongshu.publish_content(title: \\\"{title}\\\", content: \\\"{content}\\\", images: {json.dumps(images)})\""
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.stdout and '成功' in result.stdout:
            print(f"✅ 发布成功：{result.stdout}")
            return {"status": "success", "message": result.stdout}
        else:
            return {"status": "error", "message": result.stdout or result.stderr}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    parser = argparse.ArgumentParser(description='干货内容搜索 + 创作工具')
    parser.add_argument('--keyword', '-k', type=str, default='职场干货',
                       help='搜索关键词（如：职场技巧、学习方法、科技知识等）')
    parser.add_argument('--top-n', '-n', type=int, default=10,
                       help='返回干货技巧数量（如：5、10、15）')
    parser.add_argument('--auto-publish', '-a', action='store_true',
                       help='自动发布到小红书')
    parser.add_argument('--content', '-c', type=str, default='',
                       help='直接提供干货内容（可选，跳过搜索）')
    
    args = parser.parse_args()
    
    keyword = args.keyword
    top_n = args.top_n
    auto_publish = args.auto_publish
    custom_content = args.content
    
    print(f"🔍 开始搜索 \"{keyword}\" 相关的干货内容...\n")
    
    tips = []
    resources = []
    
    if custom_content:
        # 使用用户提供的内容
        print("📝 使用用户提供的干货内容...\n")
        tips = custom_content.split('\n')
        tips = [t.strip() for t in tips if len(t.strip()) > 10]
    else:
        # 搜索干货内容
        queries = [
            f"{keyword} 技巧 方法 经验",
            f"{keyword} 实用干货 2026",
            f"{keyword} 最佳实践 指南"
        ]
        
        for query in queries:
            print(f"  - 搜索：{query}")
            results = fetch_jina_search(query)
            
            for item in results[:5]:
                url = item.get('url', '')
                if url:
                    print(f"    读取：{url[:60]}...")
                    content = fetch_jina_read(url)
                    if content and not content.startswith("读取失败"):
                        extracted = extract_tips_from_content(content, keyword)
                        tips.extend(extracted)
                        resources.append({
                            "title": item.get('title', ''),
                            "url": url
                        })
    
    # 去重
    tips = list(dict.fromkeys(tips))[:top_n]
    
    # 如果搜索失败，使用示例干货内容
    if not tips:
        print("\n⚠️  网络搜索失败，使用示例干货内容...\n")
        
        example_tips = {
            "职场": [
                "学会说"我不知道，但我会学"，比不懂装懂更受领导赏识",
                "每天提前 10 分钟到公司，整理当天工作计划",
                "会议发言前先写 3 个要点，避免语无伦次",
                "收到邮件 2 小时内回复，即使只是确认收到",
                "建立工作文档库，记录常见问题和解决方案",
                "学会拒绝：不是所有事情都要亲力亲为",
                "定期和领导汇报工作进展，不要等被问",
                "同事帮忙后要感谢，小恩小惠也要记在心里",
                "重要沟通用邮件确认，避免口头承诺扯皮",
                "下班前花 5 分钟整理桌面，第二天效率更高"
            ],
            "学习": [
                "用费曼学习法：尝试把知识讲给别人听",
                "番茄工作法：25 分钟专注 +5 分钟休息",
                "建立知识卡片，记录核心概念和案例",
                "每天复盘：今天学到了什么？哪里可以改进？",
                "用思维导图整理知识框架，建立体系",
                "刻意练习：专注薄弱环节，重复训练",
                "找到学习伙伴，互相监督进步",
                "利用碎片时间：通勤、排队都可以学习",
                "定期复习：1 天、3 天、7 天、15 天回顾",
                "输出倒逼输入：写文章、做分享巩固知识"
            ],
            "科技": [
                "关注行业头部公众号，获取第一手资讯",
                "学会用 AI 工具提升工作效率",
                "建立技术博客，记录学习心得",
                "参与开源项目，积累实战经验",
                "定期整理技术栈，保持知识更新",
                "学会提问：先搜索，再提问，提供上下文",
                "掌握至少一门脚本语言，自动化重复工作",
                "阅读官方文档，比二手教程更可靠",
                "加入技术社区，和同行交流经验",
                "动手实践：看 10 遍不如做 1 遍"
            ]
        }
        
        # 根据关键词选择示例
        for cat, cat_tips in example_tips.items():
            if cat in keyword:
                tips = cat_tips[:top_n]
                break
        
        if not tips:
            tips = example_tips["职场"][:top_n]
    
    print(f"\n✅ 找到 {len(tips)} 条干货内容\n")
    
    # 输出干货清单
    print("=" * 70)
    print(f"📋 {keyword} - Top {len(tips)} 干货技巧")
    print("=" * 70)
    
    for i, tip in enumerate(tips, 1):
        print(f"\n【技巧{i}】{tip}")
    
    # 创作文案
    print("\n" + "=" * 70)
    print("📝 创作小红书文案...")
    content_data = create_detailed_content(keyword, tips, resources)
    
    print(f"\n标题：{content_data['title']}")
    print(f"\n内容：\n{content_data['content']}")
    print(f"\n技巧数量：{content_data['tips_count']} 条")
    
    # 保存到文件
    output_path = Path(f"/home/admin/openclaw/workspace/temp/xiaohongshu-{keyword}.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    draft = f"""# 小红书文案草稿 - {keyword}

## 标题
{content_data['title']}

## 内容
{content_data['content']}

## 干货技巧 ({content_data['tips_count']}条)
{chr(10).join([f"{i}. {tip}" for i, tip in enumerate(tips, 1)])}

## 参考资源
{chr(10).join([f"- {r['title']}: {r['url']}" for r in resources[:5]])}

---
生成时间：{datetime.now().isoformat()}
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(draft)
    
    print(f"\n💾 文案已保存到：{output_path}")
    
    # 发布到小红书
    if auto_publish:
        print("\n📤 自动发布到小红书...")
        result = publish_to_xiaohongshu(content_data['title'], content_data['content'])
        if result['status'] == 'success':
            print(f"✅ 发布成功！")
        else:
            print(f"❌ 发布失败：{result['message']}")
    else:
        print("\n⏳ 如需发布，请添加 --auto-publish 参数")
    
    print("\n✅ 流程完成！")

if __name__ == "__main__":
    main()
