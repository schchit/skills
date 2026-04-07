#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基金数据获取脚本 - 并发调用 MCP 工具获取基金数据
输出原始数据供 AI 进行深度分析
"""

import subprocess, json, sys, os, tempfile, time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR.parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 配置
CONFIG = {
    "mcp_timeout": 45,
    "max_workers": 4,
}

# 数据查询列表（核心维度）
# 注意：所有查询使用 query 参数，确保能获取同类排名数据
QUERIES = {
    "basic": [
        "基金{code} 基本信息",
    ],
    "performance": [
        # 使用 StageIncreaseReport 获取带同类排名的业绩数据
        "基金{code} 阶段涨幅 同类排名",
        "基金{code} 业绩排名 收益率",
    ],
    "risk": [
        "基金{code} 风险指标 夏普比率",
        "基金{code} 波动率 最大回撤 卡玛比率",
    ],
    "manager": [
        "基金{code} 基金经理",
        "基金{code} 现任经理 履历",
    ],
    "allocation": [
        "基金{code} 资产配置",
        "基金{code} 股票仓位 债券仓位",
    ],
    "holdings": [
        "基金{code} 重仓股",
        "基金{code} 前十大持仓 集中度",
    ],
    "company": [
        "基金公司 概况",
    ],
}

# 颜色输出
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'

def print_color(color, text):
    print(f"{color}{text}{Colors.NC}")

def call_mcp(query: str, timeout: int = None) -> dict:
    """调用 MCP 工具获取数据"""
    if timeout is None:
        timeout = CONFIG["mcp_timeout"]
    
    # 使用 jy-financedata-api 服务（恒生聚源官方 MCP 服务）
    cmd = ["mcporter", "call", "jy-financedata-api.FinancialDataAPI", f"query={query}"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            try:
                # 使用更宽松的 JSON 解析，处理可能的特殊字符
                data = json.loads(result.stdout, strict=False)
                if data.get("code") == 0 and data.get("results"):
                    return {
                        "success": True,
                        "data": data["results"],
                        "query": query
                    }
            except json.JSONDecodeError as e:
                # JSON 解析失败时，尝试提取 table_markdown
                import re
                markdown_match = re.search(r'"table_markdown"\s*:\s*"([^"]*(?:\\.[^"])*)"', result.stdout)
                if markdown_match:
                    markdown = markdown_match.group(1).replace('\\n', '\n').replace('\\"', '"')
                    return {
                        "success": True,
                        "data": [{"table_markdown": markdown}],
                        "query": query
                    }
                return {"success": False, "error": f"JSON parse error: {e}", "query": query}
        return {"success": False, "error": result.stderr or "Unknown error", "query": query}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Timeout ({timeout}s)", "query": query}
    except Exception as e:
        return {"success": False, "error": str(e), "query": query}

def extract_markdown(results: list) -> str:
    """从 MCP 结果中提取 markdown 表格"""
    md_parts = []
    
    def process_result(r):
        """处理单个结果"""
        if not isinstance(r, dict):
            return
        
        if r.get("table_markdown"):
            md_parts.append(r["table_markdown"])
        elif r.get("origin_data"):
            origin = r["origin_data"]
            if isinstance(origin, dict) and origin.get("rows"):
                md_parts.append(json.dumps(origin, ensure_ascii=False, indent=2))
            elif isinstance(origin, list):
                md_parts.append(json.dumps(origin, ensure_ascii=False, indent=2))
            else:
                md_parts.append(str(origin))
    
    def flatten(items):
        """递归展平嵌套列表"""
        for item in items:
            if isinstance(item, list):
                flatten(item)
            else:
                process_result(item)
    
    flatten(results)
    return "\n\n".join(md_parts) if md_parts else "暂无数据"

def fetch_category(category: str, queries: list, fund_code: str) -> tuple:
    """获取单个维度的数据"""
    results = []
    for q in queries:
        query = q.replace("{code}", fund_code)
        result = call_mcp(query)
        if result["success"]:
            results.append(result["data"])
    return category, extract_markdown(results) if results else "暂无数据"

def fetch_fund_data(fund_code: str, dimension: str = "all") -> dict:
    """获取基金数据（支持并发）"""
    print_color(Colors.GREEN, f"\n📊 开始获取基金 {fund_code} 数据...\n")
    
    data = {}
    
    # 确定要获取的维度
    if dimension == "all":
        categories = QUERIES
    elif dimension in QUERIES:
        categories = {dimension: QUERIES[dimension]}
    else:
        print_color(Colors.RED, f"✗ 未知维度：{dimension}")
        print(f"可用维度：{', '.join(QUERIES.keys())}")
        sys.exit(1)
    
    total = sum(len(v) for v in categories.values())
    current = 0
    
    # 并发获取数据
    with ThreadPoolExecutor(max_workers=CONFIG["max_workers"]) as executor:
        futures = {}
        for category, queries in categories.items():
            future = executor.submit(fetch_category, category, queries, fund_code)
            futures[future] = category
        
        for future in as_completed(futures, timeout=CONFIG["mcp_timeout"] * len(categories)):
            category = futures[future]
            try:
                cat, content = future.result()
                data[cat] = content
                lines = len(content.split("\n"))
                print_color(Colors.GREEN, f"  ✓ {cat}: {lines} 行")
            except Exception as e:
                print_color(Colors.RED, f"  ✗ {category} 失败：{e}")
                data[category] = "获取失败"
    
    return data

def save_data(fund_code: str, data: dict) -> Path:
    """保存数据到 markdown 文件"""
    output_file = OUTPUT_DIR / f"{fund_code}_data.md"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# 基金 {fund_code} 原始数据\n\n")
        f.write(f"**获取时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        for category, content in data.items():
            f.write(f"## {category.upper()}\n\n")
            f.write(content)
            f.write("\n\n---\n\n")
    
    return output_file

def main():
    if len(sys.argv) < 2:
        print("用法：python3 fetch_data.py <基金代码> [维度]")
        print("示例：python3 fetch_data.py 005827")
        print("维度：all, basic, performance, risk, manager, allocation, holdings, company")
        sys.exit(1)
    
    fund_code = sys.argv[1]
    dimension = sys.argv[2] if len(sys.argv) > 2 else "all"
    
    start_time = time.time()
    data = fetch_fund_data(fund_code, dimension)
    output_file = save_data(fund_code, data)
    total_time = time.time() - start_time
    
    print("")
    print("=" * 60)
    print_color(Colors.GREEN, f"✅ 数据已保存：{output_file}")
    print(f"⏱️  总耗时：{total_time:.1f}秒")
    print("=" * 60)
    
    # 显示数据摘要
    print("\n📋 数据摘要:\n")
    for cat, content in data.items():
        lines = len(content.split("\n"))
        status = Colors.GREEN + "✓" + Colors.NC if content != "暂无数据" else Colors.YELLOW + "⚠" + Colors.NC
        print(f"  {status} {cat}: {lines} 行")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
