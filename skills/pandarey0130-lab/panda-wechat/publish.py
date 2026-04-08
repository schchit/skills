#!/usr/bin/env python3
"""
微信公众号文章发布脚本
用法：python3 publish.py "标题" "作者" article.html [封面图]
"""
import requests
import json
import subprocess
import sys
import os
import re

APP_ID = os.environ.get("WECHAT_APP_ID", "")
APP_SECRET = os.environ.get("WECHAT_APP_SECRET", "")

def load_config():
    global APP_ID, APP_SECRET
    if not APP_ID or not APP_SECRET:
        config_file = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_file):
            with open(config_file) as f:
                cfg = json.load(f)
                APP_ID = cfg.get("app_id", "")
                APP_SECRET = cfg.get("app_secret", "")
    if not APP_ID or not APP_SECRET:
        raise Exception(
            "❌ 缺少微信凭证！\n\n"
            "获取方式：\n"
            "1. 登录微信公众平台 https://mp.weixin.qq.com\n"
            "2. 设置与开发 → 基本配置\n"
            "3. 找到 AppID 和 AppSecret\n\n"
            "设置方式：\n"
            "- 环境变量：WECHAT_APP_ID 和 WECHAT_APP_SECRET\n"
            "- 或创建 config.json 文件（参考 config.example.json）"
        )


def get_token():
    load_config()
    r = requests.get("https://api.weixin.qq.com/cgi-bin/token",
        params={"grant_type": "client_credential", "appid": APP_ID, "secret": APP_SECRET}, timeout=10)
    d = r.json()
    if d.get("errcode"):
        raise Exception(f"Token失败: {d}")
    return d["access_token"]

def upload_cover(token, cover_path):
    """上传封面图到永久素材"""
    r = subprocess.run([
        "curl", "-s", "-X", "POST",
        f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image",
        "-F", f"media=@{cover_path};type=image/png"
    ], capture_output=True, text=True)
    d = json.loads(r.stdout)
    if d.get("errcode"):
        raise Exception(f"封面上传失败: {d}")
    return d["media_id"]

def create_draft(token, title, author, digest, content, cover_id):
    """创建草稿"""
    article = {
        "title": title,
        "author": author,
        "digest": digest or content[:54].replace("<", "").replace(">", "").strip(),
        "content": content,
        "content_source_url": "",
        "thumb_media_id": cover_id,
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }
    r = subprocess.run([
        "curl", "-s", "-X", "POST",
        f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"articles": [article]}, ensure_ascii=False),
    ], capture_output=True, text=True)
    d = json.loads(r.stdout)
    if d.get("errcode"):
        raise Exception(f"草稿创建失败: {d}")
    return d["media_id"]

def main():
    if len(sys.argv) < 4:
        print("用法: python3 publish.py <标题> <作者> <HTML文件> [封面图]")
        print("示例: python3 publish.py '我的文章' '作者名' article.html cover.png")
        sys.exit(1)

    title = sys.argv[1]
    author = sys.argv[2]
    html_file = sys.argv[3]
    cover = sys.argv[4] if len(sys.argv) > 4 else None

    with open(html_file, encoding="utf-8") as f:
        content = f.read()

    # 提取body内容
    m = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)
    content = m.group(1).strip() if m else content

    # 清理不需要的标签（保留内联样式）
    for pat in [
        r'<style[^>]*>[\s\S]*?</style>',
        r'<script[^>]*>[\s\S]*?</script>',
        r'\s+class="[^"]*"',
        r'</?o:[^>]+>',
        r'</?w:[^>]+>',
        r'<!--[\s\S]*?-->',
    ]:
        content = re.sub(pat, '', content)

    print("=" * 50)
    print(f"发布文章：{title}")
    print("=" * 50)

    token = get_token()
    print("[1] Token获取成功")

    cover_id = None
    if cover and os.path.exists(cover):
        print("[2] 上传封面图...")
        cover_id = upload_cover(token, cover)
        print(f"    封面ID: {cover_id}")
    else:
        print("[2] 无封面图，跳过")

    print("[3] 创建草稿...")
    draft_id = create_draft(token, title, author, "", content, cover_id)
    print(f"    草稿ID: {draft_id}")

    print("=" * 50)
    print("🎉 草稿创建成功！")
    print(f"   标题：{title}")
    print(f"   草稿ID：{draft_id}")
    print()
    print("请登录微信公众号后台 → 内容与互动 → 草稿箱 → 发布")
    print("=" * 50)

if __name__ == "__main__":
    main()
