#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书AI创作者识别 - 断点续跑版
支持分批处理，超时后可从上次进度继续
"""

import asyncio
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Set

try:
    from playwright.async_api import async_playwright, Page
except ImportError:
    print("ERROR: pip install playwright")
    exit(1)

try:
    import pandas as pd
except ImportError:
    print("ERROR: pip install pandas openpyxl")
    exit(1)


@dataclass
class CreatorInfo:
    platform: str = "小红书"
    creator_id: str = ""
    creator_name: str = ""
    home_url: str = ""
    follower_count: int = 0
    video_url: str = ""
    video_likes: int = 0
    video_comments: int = 0
    is_video: bool = False
    matched_keyword: str = ""
    crawl_time: str = ""
    
    def to_dict(self):
        return {
            "平台": self.platform,
            "创作者ID": self.creator_id,
            "创作者名称": self.creator_name,
            "主页链接": self.home_url,
            "粉丝量": self.follower_count,
            "视频链接": self.video_url,
            "点赞数": self.video_likes,
            "评论数": self.video_comments,
            "关键词": self.matched_keyword,
            "采集时间": self.crawl_time,
        }


class XiaoHongShuBot:
    def __init__(self):
        # 路径设置
        self.src_dir = Path(__file__).parent
        self.workspace = self.src_dir.parent
        self.config_dir = self.workspace / "config"
        self.output_dir = self.workspace / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # 加载配置
        self.config = self.load_config()
        self.keywords = self.config.get("keywords", ["AI动画"])
        self.max_results = self.config.get("max_results", 15)
        self.min_followers = self.config.get("min_followers", 1000)
        self.min_comments = self.config.get("min_comments", 20)
        self.output_format = self.config.get("output_format", "excel")
        self.chrome_path = self.config.get("chrome_path", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        
        # 断点续跑相关
        self.checkpoint_file = self.output_dir / "checkpoint.json"
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.completed_keywords: Set[str] = set()
        self.all_results: List[CreatorInfo] = []
        self.seen_ids: Set[str] = set()
        
        # 加载上次进度
        self.load_checkpoint()
    
    def load_config(self) -> dict:
        """加载配置文件"""
        config_file = self.config_dir / "settings.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.log(f"[WARN] 配置文件读取失败: {e}")
        return {}
    
    def load_checkpoint(self):
        """加载断点进度"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.session_id = data.get("session_id", self.session_id)
                    self.completed_keywords = set(data.get("completed_keywords", []))
                    # 加载已保存的结果
                    for item in data.get("results", []):
                        creator = CreatorInfo(**item)
                        self.all_results.append(creator)
                        self.seen_ids.add(creator.creator_id)
                    self.log(f"[CHECKPOINT] 已加载进度: {len(self.completed_keywords)}/{len(self.keywords)} 个关键词完成")
                    self.log(f"[CHECKPOINT] 已采集 {len(self.all_results)} 位创作者")
            except Exception as e:
                self.log(f"[WARN] 断点文件读取失败: {e}")
    
    def save_checkpoint(self):
        """保存断点进度"""
        try:
            data = {
                "session_id": self.session_id,
                "completed_keywords": list(self.completed_keywords),
                "results": [r.__dict__ for r in self.all_results],
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"[WARN] 断点保存失败: {e}")
    
    def clear_checkpoint(self):
        """清除断点（任务完成后调用）"""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
            self.log("[CHECKPOINT] 已清除断点文件")
    
    def log(self, msg: str):
        safe_msg = msg.encode('ascii', 'replace').decode('ascii') if msg else ""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {safe_msg}", flush=True)
    
    def extract_num(self, text: str) -> int:
        if not text:
            return 0
        text = str(text).strip().replace(',', '')
        if '万' in text or 'w' in text.lower():
            m = re.search(r'([\d.]+)', text)
            return int(float(m.group(1)) * 10000) if m else 0
        nums = re.findall(r'\d+', text)
        return int(nums[0]) if nums else 0
    
    def fix_unicode(self, text: str) -> str:
        if not text:
            return ""
        try:
            if '\\u' in text:
                text = text.encode('utf-8').decode('unicode_escape')
            return text
        except:
            return text
    
    async def run(self):
        self.log("="*50)
        self.log("小红书创作者采集 - 断点续跑版")
        self.log("="*50)
        
        # 检查是否已完成
        pending_keywords = [kw for kw in self.keywords if kw not in self.completed_keywords]
        if not pending_keywords:
            self.log("[INFO] 所有关键词已处理完成，直接导出结果")
            self.export()
            self.clear_checkpoint()
            return
        
        self.log(f"[INFO] 待处理关键词: {pending_keywords}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                executable_path=self.chrome_path,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
            
            cookies_file = self.config_dir / "cookies.json"
            if cookies_file.exists():
                with open(cookies_file, 'r', encoding='utf-8') as f:
                    await context.add_cookies(json.load(f))
                self.log("[OK] Cookies loaded")
            
            page = await context.new_page()
            
            # 检查登录
            await page.goto("https://www.xiaohongshu.com/user/profile", timeout=15000)
            await asyncio.sleep(2)
            
            if "/login" in page.url:
                self.log("[INFO] 请扫码登录...")
                await page.goto("https://www.xiaohongshu.com/login", timeout=30000)
                await asyncio.sleep(3)
                for i in range(60):
                    await asyncio.sleep(1)
                    if "/login" not in page.url:
                        self.log("[OK] 登录成功")
                        with open(cookies_file, 'w', encoding='utf-8') as f:
                            json.dump(await context.cookies(), f)
                        break
                else:
                    self.log("[ERR] 登录超时")
                    return
            
            # 处理待处理的关键词
            for kw in pending_keywords:
                self.log(f"\n{'='*50}")
                self.log(f"[SEARCH] {kw}")
                await self.process_keyword(page, kw)
                # 每处理完一个关键词就保存进度
                self.completed_keywords.add(kw)
                self.save_checkpoint()
                self.log(f"[CHECKPOINT] 已保存进度: {len(self.completed_keywords)}/{len(self.keywords)}")
                await asyncio.sleep(3)
            
            await browser.close()
        
        # 导出最终结果
        self.export()
        # 清除断点
        self.clear_checkpoint()
    
    async def process_keyword(self, page: Page, keyword: str):
        url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
        await page.goto(url, timeout=30000)
        await asyncio.sleep(5)
        
        for _ in range(5):
            await page.evaluate("window.scrollBy(0, 800)")
            await asyncio.sleep(1)
        await asyncio.sleep(2)
        
        links = await page.query_selector_all('a[href*="/explore/"]')
        urls = []
        seen = set()
        
        for link in links:
            try:
                href = await link.get_attribute('href')
                if href:
                    clean = href.split('?')[0]
                    if clean not in seen and '/explore/' in clean and len(clean) > 20:
                        seen.add(clean)
                        urls.append(f"https://www.xiaohongshu.com{clean}")
            except:
                pass
        
        self.log(f"[OK] 找到 {len(urls)} 个视频")
        
        success = 0
        for i, video_url in enumerate(urls[:self.max_results]):
            self.log(f"\n[{i+1}/{min(len(urls), self.max_results)}] {video_url}")
            
            creator = await self.extract_video(page, video_url, keyword)
            if creator and creator.creator_id and creator.is_video:
                # 应用筛选规则
                if creator.follower_count < self.min_followers:
                    self.log(f"[FILTER] 粉丝量{creator.follower_count} < {self.min_followers}")
                    continue
                if creator.video_comments < self.min_comments:
                    self.log(f"[FILTER] 评论数{creator.video_comments} < {self.min_comments}")
                    continue
                
                if creator.creator_id not in self.seen_ids:
                    self.seen_ids.add(creator.creator_id)
                    self.all_results.append(creator)
                    success += 1
                    safe_name = creator.creator_name.encode('ascii', 'ignore').decode('ascii')
                    self.log(f"[OK] {safe_name} | 粉丝:{creator.follower_count} | 赞:{creator.video_likes} | 评:{creator.video_comments}")
                else:
                    self.log("[SKIP] 重复")
            elif creator and not creator.is_video:
                self.log("[SKIP] 不是视频")
            else:
                self.log("[FAIL]")
            
            await asyncio.sleep(2)
        
        self.log(f"[DONE] 本关键词成功 {success} 个")
    
    async def extract_video(self, page: Page, video_url: str, keyword: str) -> Optional[CreatorInfo]:
        try:
            c = CreatorInfo()
            c.video_url = video_url
            c.matched_keyword = keyword
            c.crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            await page.goto(video_url, timeout=30000)
            await asyncio.sleep(5)
            
            # 检查是否为视频
            has_video = await page.evaluate("() => document.querySelectorAll('video').length > 0")
            c.is_video = has_video
            
            if not c.is_video:
                return c
            
            # 获取页面内容
            html = await page.content()
            page_text = await page.inner_text('body')
            
            # ===== 提取作者信息 =====
            # 方法1: JSON数据
            author_match = re.search(r'"userId":"([a-f0-9]+)"[^}]*"nickname":"([^"]+)"', html)
            if author_match:
                c.creator_id = author_match.group(1)
                c.creator_name = self.fix_unicode(author_match.group(2))
            
            # 方法2: 用户链接
            if not c.creator_id:
                user_match = re.findall(r'/user/profile/([a-f0-9]+)', html)
                if user_match:
                    c.creator_id = user_match[0]
            
            # 备用
            if not c.creator_id:
                c.creator_id = video_url.split("/")[-1][:16]
            if not c.creator_name or len(c.creator_name) < 2:
                c.creator_name = f"User-{c.creator_id[:8]}"
            
            c.home_url = f"https://www.xiaohongshu.com/user/profile/{c.creator_id}"
            
            # ===== 提取互动数据 =====
            # 点赞数 - 优先从JSON提取
            like_match = re.search(r'"likeCount":\s*"?(\d+)"?', html)
            if like_match:
                c.video_likes = int(like_match.group(1))
            
            # 备用：页面文本
            if c.video_likes == 0:
                for p in [r'"liked":\s*"?(\d+)"?', r'\b(\d[\d,]*)\s*[万w]?\s*个?赞\b']:
                    m = re.search(p, html + page_text)
                    if m:
                        c.video_likes = self.extract_num(m.group(1))
                        break
            
            # 评论数
            comment_match = re.search(r'"commentCount":\s*"?(\d+)"?', html)
            if comment_match:
                c.video_comments = int(comment_match.group(1))
            
            if c.video_comments == 0:
                m = re.search(r'"comments?":\s*"?(\d+)"?', html, re.I)
                if m:
                    c.video_comments = int(m.group(1))
            
            # ===== 获取粉丝数 =====
            try:
                await page.goto(c.home_url, timeout=20000)
                await asyncio.sleep(3)
                
                author_html = await page.content()
                
                # 方法1: JSON fansCount
                follower_match = re.search(r'"fansCount":\s*"?(\d+)"?', author_html)
                if follower_match:
                    c.follower_count = int(follower_match.group(1))
                
                # 方法2: JavaScript精确提取
                if c.follower_count == 0:
                    follower_count = await page.evaluate("""
                        () => {
                            const elements = document.querySelectorAll('*');
                            for (const el of elements) {
                                const text = el.innerText?.trim();
                                if (text === '粉丝' || text === '粉丝数') {
                                    const parent = el.parentElement;
                                    if (parent && !parent.innerText.includes('获赞')) {
                                        const match = parent.innerText.match(/([\\d,\\.]+)\\s*[万wKk]?/);
                                        if (match) return match[0];
                                    }
                                }
                            }
                            return '';
                        }
                    """)
                    if follower_count:
                        c.follower_count = self.extract_num(follower_count)
                
                # 修正名字
                if c.creator_name.startswith("User-"):
                    name_match = re.search(r'"nickname":"([^"]+)"', author_html)
                    if name_match:
                        c.creator_name = self.fix_unicode(name_match.group(1))
            except Exception as e:
                self.log(f"[WARN] 粉丝数获取失败: {str(e)[:40]}")
            
            return c
            
        except Exception as e:
            self.log(f"[ERR] {str(e)[:50]}")
            return None
    
    def export(self):
        if not self.all_results:
            self.log("\n[RESULT] 无数据")
            return
        
        self.log(f"\n{'='*50}")
        self.log(f"[RESULT] 共 {len(self.all_results)} 条")
        self.log(f"{'='*50}")
        
        # 按粉丝量排序
        sorted_results = sorted(self.all_results, key=lambda x: x.follower_count, reverse=True)
        
        data = [r.to_dict() for r in sorted_results]
        
        for r in sorted_results[:10]:  # 只显示前10
            safe_name = r.creator_name.encode('ascii', 'ignore').decode('ascii') if r.creator_name else "Unknown"
            self.log(f"  {safe_name} | 粉丝:{r.follower_count} | 关键词:{r.matched_keyword}")
        
        if len(sorted_results) > 10:
            self.log(f"  ... 还有 {len(sorted_results)-10} 条")
        
        ts = self.session_id
        
        if self.output_format in ["excel", "both"]:
            excel = self.output_dir / f"creators_{ts}.xlsx"
            pd.DataFrame(data).to_excel(excel, index=False, engine='openpyxl')
            self.log(f"\n[OK] Excel: {excel}")
        
        if self.output_format in ["json", "both"]:
            json_file = self.output_dir / f"creators_{ts}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.log(f"[OK] JSON: {json_file}")


if __name__ == "__main__":
    bot = XiaoHongShuBot()
    asyncio.run(bot.run())
