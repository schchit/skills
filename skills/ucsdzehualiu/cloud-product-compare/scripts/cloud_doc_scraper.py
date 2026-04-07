"""
阿里云 & 华为云产品文档深度爬虫 v2
逻辑：先解析左侧目录 → 按优先级筛选核心页面 → 并发抓取 → 输出供 Claude 分析的 markdown

依赖安装：
    pip install playwright
    playwright install chromium

用法：
    python cloud_doc_scraper.py --product ecs
    python cloud_doc_scraper.py --product redis --output redis_docs.md
    python cloud_doc_scraper.py --product ecs --max-pages 20   # 最多抓20个子页面（默认12）
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# ─── 产品入口配置 ──────────────────────────────────────────────────────────────

PRODUCTS = {
    "ecs": {
        "name": "云服务器 ECS",
        "aliyun":  { "doc": "https://help.aliyun.com/zh/ecs",         "changelog": "https://help.aliyun.com/zh/ecs/product-overview/release-notes" },
        "huawei":  { "doc": "https://support.huaweicloud.cn/ecs/index.html", "changelog": "https://support.huaweicloud.cn/wtsnew-ecs/index.html" },
    },
    "oss": {
        "name": "对象存储 OSS / OBS",
        "aliyun":  { "doc": "https://help.aliyun.com/zh/oss",         "changelog": "https://help.aliyun.com/zh/oss/product-overview/release-notes" },
        "huawei":  { "doc": "https://support.huaweicloud.cn/obs/index.html", "changelog": "https://support.huaweicloud.cn/wtsnew-obs/index.html" },
    },
    "rds": {
        "name": "云数据库 RDS",
        "aliyun":  { "doc": "https://help.aliyun.com/zh/rds",         "changelog": "https://help.aliyun.com/zh/rds/product-overview/release-notes" },
        "huawei":  { "doc": "https://support.huaweicloud.cn/rds/index.html", "changelog": "https://support.huaweicloud.cn/wtsnew-rds/index.html" },
    },
    "redis": {
        "name": "云数据库 Redis / DCS",
        "aliyun":  { "doc": "https://help.aliyun.com/zh/redis",       "changelog": "https://help.aliyun.com/zh/redis/product-overview/release-notes" },
        "huawei":  { "doc": "https://support.huaweicloud.cn/dcs/index.html",  "changelog": "https://support.huaweicloud.cn/wtsnew-dcs/index.html" },
    },
    "ack": {
        "name": "容器服务 ACK / CCE",
        "aliyun":  { "doc": "https://help.aliyun.com/zh/ack",         "changelog": "https://help.aliyun.com/zh/ack/product-overview/release-notes" },
        "huawei":  { "doc": "https://support.huaweicloud.cn/cce/index.html",  "changelog": "https://support.huaweicloud.cn/wtsnew-cce/index.html" },
    },
    "fc": {
        "name": "函数计算 FC / FunctionGraph",
        "aliyun":  { "doc": "https://help.aliyun.com/zh/fc",          "changelog": "https://help.aliyun.com/zh/fc/product-overview/release-notes" },
        "huawei":  { "doc": "https://support.huaweicloud.cn/functiongraph/index.html", "changelog": "https://support.huaweicloud.cn/wtsnew-functiongraph/index.html" },
    },
    "slb": {
        "name": "负载均衡 SLB / ELB",
        "aliyun":  { "doc": "https://help.aliyun.com/zh/slb",         "changelog": "https://help.aliyun.com/zh/slb/product-overview/release-notes" },
        "huawei":  { "doc": "https://support.huaweicloud.cn/elb/index.html",  "changelog": "https://support.huaweicloud.cn/wtsnew-elb/index.html" },
    },
    "maxcompute": {
        "name": "大数据 MaxCompute / MRS",
        "aliyun":  { "doc": "https://help.aliyun.com/zh/maxcompute",  "changelog": "https://help.aliyun.com/zh/maxcompute/product-overview/Release-notes" },
        "huawei":  { "doc": "https://support.huaweicloud.cn/mrs/index.html",  "changelog": "https://support.huaweicloud.cn/wtsnew-mrs/index.html" },
    },
    "pai": {
        "name": "AI 平台 PAI / ModelArts",
        "aliyun":  { "doc": "https://help.aliyun.com/zh/pai",         "changelog": "https://help.aliyun.com/zh/pai/user-guide/api-aiworkspace-2021-02-04-changeset" },
        "huawei":  { "doc": "https://support.huaweicloud.cn/modelarts/index.html", "changelog": "https://support.huaweicloud.cn/wtsnew-modelarts/index.html" },
    },
    "bailian": {
        "name": "大模型平台 百炼 / 盘古",
        "aliyun":  { "doc": "https://help.aliyun.com/zh/bailian",     "changelog": "https://help.aliyun.com/zh/bailian/release-notes" },
        "huawei":  { "doc": "https://support.huaweicloud.cn/pangu/index.html", "changelog": "https://support.huaweicloud.cn/wtsnew-pangu/index.html" },
    },
}

# ─── 优先级关键词 ──────────────────────────────────────────────────────────────
# 每条 (权重, [关键词列表])，命中任意一个关键词即得该权重分

PRIORITY_KEYWORDS = [
    ( 3, ["产品简介", "产品概述", "什么是", "功能特性", "核心功能", "产品功能",
          "product overview", "what is", "features", "capabilities"]),
    ( 2, ["规格", "实例规格", "配置", "限制", "约束", "性能", "指标", "参数",
          "specification", "limits", "quota", "performance", "benchmark"]),
    ( 2, ["计费", "定价", "费用", "价格", "版本对比", "版本说明",
          "pricing", "billing", "edition"]),
    ( 1, ["应用场景", "使用场景", "适用场景", "最佳实践",
          "use case", "scenario", "best practice"]),
    (-1, ["常见问题", "faq", "故障排除", "troubleshoot", "sdk",
          "api参考", "api reference", "错误码", "error code", "迁移指南"]),
]

def score_link(text: str, href: str) -> int:
    combined = (text + " " + href).lower()
    score = 0
    for weight, keywords in PRIORITY_KEYWORDS:
        if any(kw in combined for kw in keywords):
            score += weight
    return score


# ─── 目录解析 ─────────────────────────────────────────────────────────────────

# 阿里云和华为云各自的左侧导航选择器，按可能性从高到低排列
ALIYUN_NAV_SELECTORS = [
    ".toc-menu a", ".sidebar-menu a", ".helpcenter-menu a",
    "nav a", ".left-menu a",
    "[class*='nav'] a", "[class*='sidebar'] a", "[class*='toc'] a", "[class*='menu'] a",
]
HUAWEI_NAV_SELECTORS = [
    ".book-left-menu a", ".toc a", ".sidebar a", ".tree-menu a",
    "[class*='catalog'] a", "[class*='tree'] a", "[class*='nav'] a", "[class*='menu'] a",
]

async def parse_toc(page, base_url: str, nav_selectors: list[str], label: str) -> list[dict]:
    base_domain = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}"
    links = []

    for selector in nav_selectors:
        try:
            els = await page.query_selector_all(selector)
            if len(els) <= 3:
                continue
            for el in els:
                href = await el.get_attribute("href") or ""
                text = (await el.inner_text()).strip()
                if not href or not text:
                    continue
                full_url = urljoin(base_domain, href) if href.startswith("/") else href
                if urlparse(base_domain).netloc not in urlparse(full_url).netloc:
                    continue
                links.append({"url": full_url, "text": text, "score": score_link(text, href)})
            if links:
                print(f"    [{label}] 目录命中选择器 '{selector}'，共 {len(links)} 个链接")
                return links
        except Exception:
            continue

    print(f"    [{label}] ⚠️  所有选择器均未命中，目录解析失败")
    return []


# ─── 正文提取 ─────────────────────────────────────────────────────────────────

CONTENT_SELECTORS = [
    ".help-detail-content", ".article-content", ".doc-body",  # 阿里云
    ".book-desc", ".content-block",                            # 华为云
    "article", ".markdown-body", "#content", "main", ".main-content", ".content",
]

async def extract_text(page) -> str:
    for selector in CONTENT_SELECTORS:
        try:
            el = await page.query_selector(selector)
            if el:
                text = await el.inner_text()
                if len(text.strip()) > 300:
                    return text.strip()
        except Exception:
            continue
    body = await page.query_selector("body")
    return (await body.inner_text()).strip() if body else ""

async def fetch_content(browser, url: str) -> str:
    page = await browser.new_page()
    try:
        await page.goto(url, wait_until="networkidle", timeout=25000)
        for selector in CONTENT_SELECTORS:
            try:
                await page.wait_for_selector(selector, timeout=3000)
                break
            except PlaywrightTimeout:
                continue
        return await extract_text(page)
    except PlaywrightTimeout:
        return f"[超时，请手动访问：{url}]"
    except Exception as e:
        return f"[失败：{e}]"
    finally:
        await page.close()


# ─── 单侧完整抓取 ─────────────────────────────────────────────────────────────

async def scrape_side(browser, label: str, doc_url: str, changelog_url: str,
                      nav_selectors: list[str], max_pages: int) -> dict:
    result = {"label": label, "doc_url": doc_url, "changelog_url": changelog_url,
              "pages": [], "changelog": "", "toc_total": 0}

    # Step 1: 打开首页 + 解析目录
    print(f"\n  [{label}] 解析文档目录...")
    index_page = await browser.new_page()
    toc = []
    try:
        await index_page.goto(doc_url, wait_until="networkidle", timeout=30000)
        toc = await parse_toc(index_page, doc_url, nav_selectors, label)
        result["toc_total"] = len(toc)

        if not toc:
            # 目录失败则至少把首页内容抓下来
            print(f"  [{label}] 回退：仅抓首页")
            result["pages"].append(("产品首页", doc_url, await extract_text(index_page)))
    finally:
        await index_page.close()

    # Step 2: 去重 → 过滤负分 → 排序 → 取 top-N
    if toc:
        seen = set()
        unique = []
        for lk in toc:
            if lk["url"] not in seen:
                seen.add(lk["url"])
                unique.append(lk)

        candidates = sorted(
            [lk for lk in unique if lk["score"] >= 0],
            key=lambda x: x["score"], reverse=True
        )[:max_pages]

        print(f"  [{label}] 筛选出 {len(candidates)}/{len(unique)} 个核心页面：")
        for i, lk in enumerate(candidates):
            print(f"    {i+1:2d}. [{lk['score']:+d}] {lk['text'][:45]}")

        # Step 3: 并发抓取（限制并发数避免被封）
        sem = asyncio.Semaphore(4)

        async def fetch_one(lk):
            async with sem:
                content = await fetch_content(browser, lk["url"])
                ok = "✅" if not content.startswith("[") else "❌"
                print(f"  [{label}] {ok} {lk['text'][:40]}")
                return (lk["text"], lk["url"], content)

        result["pages"] = list(await asyncio.gather(*[fetch_one(lk) for lk in candidates]))

    # Step 4: 更新日志
    print(f"  [{label}] 抓取更新日志...")
    result["changelog"] = await fetch_content(browser, changelog_url)
    ok = "✅" if not result["changelog"].startswith("[") else "❌"
    print(f"  [{label}] {ok} 更新日志完成")

    return result


# ─── 拼装输出 Markdown ────────────────────────────────────────────────────────

def build_markdown(product_name: str, aliyun: dict, huawei: dict) -> str:
    now = datetime.now().strftime("%Y-%m-%d")
    lines = [
        f"# 竞品分析原始资料：{product_name}",
        f"> 抓取时间：{now}",
        f"> 阿里云：目录 {aliyun['toc_total']} 页，本次抓取 {len(aliyun['pages'])} 页",
        f"> 华为云：目录 {huawei['toc_total']} 页，本次抓取 {len(huawei['pages'])} 页",
        "",
        "**给 Claude 的指令：** 基于以下官方文档原文，分析两款产品的真实差异。",
        "重点挖掘：关键指标的数字差距、一方有而另一方没有的能力、相同功能的成熟度差异、近期迭代方向的分歧。",
        "无差异或差异不明显的维度直接略过，不要凑字数。",
        "", "---", "",
    ]

    for side in [aliyun, huawei]:
        label = side["label"]
        lines += [f"# {label}", ""]

        if not side["pages"]:
            lines.append(f"> ⚠️ 文档抓取失败，请手动访问：{side['doc_url']}")
        else:
            for title, url, content in side["pages"]:
                lines += [f"## {label} · {title}", f"> 来源：{url}", ""]
                body = content[:8000]
                if len(content) > 8000:
                    body += "\n\n[...已截断，完整内容见来源链接...]"
                lines += [body, "", "---", ""]

        # 更新日志
        lines += [f"## {label} · 更新日志", f"> 来源：{side['changelog_url']}", ""]
        cl = side["changelog"][:6000]
        if len(side["changelog"]) > 6000:
            cl += "\n\n[...已截断...]"
        lines += [cl or f"> ⚠️ 抓取失败，请手动访问：{side['changelog_url']}", "", "---", ""]

    return "\n".join(lines)


# ─── 主入口 ───────────────────────────────────────────────────────────────────

async def main_async(product_key: str, max_pages: int, output: str):
    if product_key not in PRODUCTS:
        print(f"❌ 未知产品 '{product_key}'，可选：{', '.join(PRODUCTS.keys())}")
        sys.exit(1)

    cfg = PRODUCTS[product_key]
    print(f"\n{'='*60}\n  {cfg['name']}  （每侧最多 {max_pages} 个核心页面）\n{'='*60}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            aliyun = await scrape_side(browser, "阿里云",
                cfg["aliyun"]["doc"], cfg["aliyun"]["changelog"],
                ALIYUN_NAV_SELECTORS, max_pages)
            huawei = await scrape_side(browser, "华为云",
                cfg["huawei"]["doc"], cfg["huawei"]["changelog"],
                HUAWEI_NAV_SELECTORS, max_pages)
        finally:
            await browser.close()

    md = build_markdown(cfg["name"], aliyun, huawei)

    if output:
        Path(output).write_text(md, encoding="utf-8")
        print(f"\n✅ 完成！已保存到 {output}（{len(md.encode())//1024} KB）")
        print("   将文件内容粘给 Claude 即可开始竞品分析。")
    else:
        print("\n" + "="*60 + "\n" + md)


def main():
    parser = argparse.ArgumentParser(description="阿里云 & 华为云文档深度爬虫 v2")
    parser.add_argument("--product",   required=True, help=f"产品代码，可选：{', '.join(PRODUCTS.keys())}")
    parser.add_argument("--output",    default="",    help="输出文件路径（默认打印到终端）")
    parser.add_argument("--max-pages", type=int, default=12, help="每侧最多抓取的核心页面数（默认 12）")
    args = parser.parse_args()
    asyncio.run(main_async(args.product, args.max_pages, args.output))

if __name__ == "__main__":
    main()
