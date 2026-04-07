#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Web Search - 极简网络搜索
优先使用 Exa AI (OpenCode 同款)，备用百度/必应双引擎
"""

import sys
import json
import subprocess
import urllib.parse
import re
from html import unescape
from typing import Dict, Any, List

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

EXA_SEARCH_SCRIPT = "/home/lin/.openclaw/scripts/exa-search.sh"


def search_exa(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """Exa AI 搜索 (OpenCode 同款) - 优先使用"""
    results = []
    
    try:
        # 调用 Exa 搜索脚本
        cmd = [EXA_SEARCH_SCRIPT, query, str(num_results)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30, encoding='utf-8')
        
        if proc.returncode == 0 and proc.stdout:
            lines = proc.stdout.strip().split('\n')
            current = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 跳过 event: message 行
                if line.startswith('event:') or line.startswith('data:'):
                    continue
                    
                # 匹配标题行 - emoji + 空格 + 文本
                # 使用 \S 匹配 emoji (单个 Unicode 字符)
                title_match = re.match(r'^\S\s+(.+)', line)
                if title_match and 'http' not in line:
                    if current.get('title') and current.get('href'):
                        results.append(current)
                        if len(results) >= num_results:
                            break
                    current = {'title': title_match.group(1).strip(), 'href': '', 'body': ''}
                # 匹配 URL 行
                elif 'https://' in line or 'http://' in line:
                    url_match = re.match(r'^\S\s+(https?://\S+)', line)
                    if url_match:
                        current['href'] = url_match.group(1).strip()
            
            # 添加最后一个结果
            if current.get('title') and current.get('href'):
                results.append(current)
                
    except Exception as e:
        pass
    
    return results


def search_baidu(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """百度搜索"""
    results = []
    
    if not HAS_REQUESTS:
        return results
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.baidu.com/s?wd={encoded_query}&rn={num_results * 2}"
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            html = response.text
            
            # 匹配百度搜索结果：class="result" 或 class="c-container"
            patterns = [
                r'<h3[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>\s*</h3>',
                r'class="t"[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
                for href, title in matches:
                    if len(results) >= num_results:
                        break
                    
                    title = re.sub(r'<[^>]+>', '', title).strip()
                    title = unescape(title)
                    
                    # 过滤无效结果
                    if not title or len(title) < 4:
                        continue
                    if not href.startswith('http'):
                        continue
                    if any(x in href for x in ['baidu.com/home', 'passport.baidu.com']):
                        continue
                    
                    results.append({
                        'title': title,
                        'href': href,
                        'body': ''
                    })
                    
    except Exception:
        pass
    
    return results


def search_bing(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """必应搜索"""
    results = []
    
    if not HAS_REQUESTS:
        return results
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        encoded_query = urllib.parse.quote(query)
        url = f"https://cn.bing.com/search?q={encoded_query}&count=20"
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            html = response.text
            
            # 匹配必应搜索结果
            pattern = r'<h2[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>([^<]+)'
            matches = re.findall(pattern, html, re.IGNORECASE)
            
            for href, title in matches:
                if len(results) >= num_results:
                    break
                
                title = re.sub(r'<[^>]+>', '', title).strip()
                title = unescape(title)
                
                # 过滤无效结果
                if not title or len(title) < 4:
                    continue
                if not is_valid_link(href):
                    continue
                
                results.append({
                    'title': title,
                    'href': href,
                    'body': ''
                })
                    
    except Exception:
        pass
    
    return results


def is_valid_link(href: str) -> bool:
    """检查链接是否有效"""
    # 必须是 http/https 开头
    if not href.startswith(('http://', 'https://')):
        return False
    
    # 屏蔽的域名和模式
    blocked = [
        'bing.com/search',
        'bing.com/images',
        'bing.com/videos',
        'bing.com/maps',
        'javascript:',
        'passport.bing.com',
        'login.live.com',
    ]
    
    if any(b in href for b in blocked):
        return False
    
    # 跳过 IP 地址（通常是广告）
    if re.match(r'^https?://\d+\.\d+\.\d+\.\d+', href):
        return False
    
    return True


def web_search(query: str, num_results: int = 5) -> Dict[str, Any]:
    """执行搜索 - 优先使用 Exa AI"""
    if not query or not isinstance(query, str):
        return {
            'success': False,
            'message': '搜索关键词不能为空'
        }
    
    query = query.strip()
    num_results = max(1, min(int(num_results), 20))
    
    all_results = []
    engines_used = []
    
    # 1. 优先 Exa AI (OpenCode 同款) - 免费，无需 API Key
    exa_results = search_exa(query, num_results)
    if exa_results:
        all_results.extend(exa_results)
        engines_used.append('exa')
    
    # 2. 结果不足时用必应补充
    if len(all_results) < num_results and HAS_REQUESTS:
        bing_results = search_bing(query, num_results)
        if bing_results:
            existing_hrefs = {r['href'] for r in all_results}
            for r in bing_results:
                if r['href'] not in existing_hrefs:
                    all_results.append(r)
                    existing_hrefs.add(r['href'])
            engines_used.append('bing')
    
    # 3. 仍不足时用百度补充
    if len(all_results) < num_results and HAS_REQUESTS:
        baidu_results = search_baidu(query, num_results)
        if baidu_results:
            existing_hrefs = {r['href'] for r in all_results}
            for r in baidu_results:
                if r['href'] not in existing_hrefs:
                    all_results.append(r)
                    existing_hrefs.add(r['href'])
            engines_used.append('baidu')
    
    # 截取指定数量
    results = all_results[:num_results]
    
    return {
        'success': len(results) > 0,
        'query': query,
        'engine': '+'.join(engines_used) if engines_used else 'none',
        'num_results': len(results),
        'results': results,
        'message': '搜索完成' if results else '未找到结果'
    }


def main(input_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """入口函数"""
    if input_data is None:
        input_data = {}
    
    action = input_data.get('action', 'search')
    query = input_data.get('query', '')
    num_results = input_data.get('num_results', 5)
    
    if action != 'search':
        return {
            'success': False,
            'message': f'不支持的操作：{action}'
        }
    
    return web_search(query, num_results)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = sys.argv[1]
        num = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    else:
        query = "Python 教程"
        num = 5
    
    result = main({'action': 'search', 'query': query, 'num_results': num})
    print(json.dumps(result, ensure_ascii=False, indent=2))
