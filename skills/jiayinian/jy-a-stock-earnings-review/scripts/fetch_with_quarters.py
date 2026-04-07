#!/usr/bin/env python3
"""
A 股财报数据获取脚本（支持季度数据）
通过 mcporter CLI 调用聚源 MCP 接口获取财务数据

关键改进：同时获取年报和季报数据
"""

import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional
from extract_metrics import extract_financial_metrics

MCP_CONFIG_PATH = "/home/liust/openclaw/workspace/config/mcporter.json"
MCP_SERVER = "gildata_datamap-sse"


def call_mcp_tool(tool_name: str, query: str) -> Optional[Dict]:
    """通过 mcporter CLI 调用 MCP 工具"""
    try:
        cmd = [
            "mcporter", "call", f"{MCP_SERVER}.{tool_name}",
            f"query={query}", "--config", MCP_CONFIG_PATH
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            if response.get("code") == 0 and response.get("results"):
                return response["results"][0]
        return None
    except Exception as e:
        print(f"  ⚠ 调用失败：{e}")
        return None


def fetch_data_with_quarters(stock_code: str, company_name: str, years: List[str] = None) -> Dict:
    """
    获取财务数据（包含年度和季度）
    """
    if years is None:
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 4, current_year)]
    
    print(f"\n{'='*60}")
    print(f"获取 {company_name} ({stock_code}) 财务数据...")
    print(f"年份范围：{years}")
    print(f"{'='*60}\n")
    
    all_rows = []
    
    # 遍历每一年，获取年报和季报
    for year in years:
        print(f"[{year}] 获取年度和季度数据...")
        
        # 1. 年报
        queries = [
            f"{company_name} {stock_code} {year}年 年报 营业收入 净利润 营业成本",
            f"{company_name} {stock_code} {year}年 年报 毛利率 净利率 销售费用 管理费用 研发费用",
        ]
        
        # 2. 季报（一季报、中报、三季报）
        quarter_names = ["一季报", "中报", "三季报"]
        for q in quarter_names:
            queries.append(f"{company_name} {stock_code} {year}年 {q} 营业收入 净利润")
            queries.append(f"{company_name} {stock_code} {year}年 {q} 毛利率 净利率")
        
        # 执行查询
        for query in queries:
            result = call_mcp_tool("FinancialDataAPI", query)
            if result and result.get("origin_data", {}).get("rows"):
                rows = result["origin_data"]["rows"]
                all_rows.extend(rows)
                print(f"  ✓ {query[:50]}... ({len(rows)}条)")
    
    # 提取指标
    print(f"\n提取关键指标...")
    combined_data = {"rows": all_rows}
    metrics = extract_financial_metrics(combined_data)
    
    # 构建返回数据
    data = {
        "stock_code": stock_code,
        "company_name": company_name,
        "fetch_time": datetime.now().isoformat(),
        "raw_rows_count": len(all_rows),
        "metrics": metrics
    }
    
    return data


def main():
    if len(sys.argv) < 2:
        print("用法：python fetch_with_quarters.py <股票代码> [公司名称] [年份...]")
        print("示例：python fetch_with_quarters.py 300750 宁德时代 2024 2023")
        sys.exit(1)
    
    stock_code = sys.argv[1]
    company_name = sys.argv[2] if len(sys.argv) > 2 else stock_code
    
    years = [arg for arg in sys.argv[3:] if arg.isdigit() and len(arg) == 4]
    if not years:
        years = ["2024", "2023", "2022", "2021"]
    
    # 获取数据
    data = fetch_data_with_quarters(stock_code, company_name, years)
    
    # 保存
    output_file = f"{stock_code}_with_quarters.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 输出摘要
    metrics = data["metrics"]
    print(f"\n{'='*60}")
    print("数据摘要:")
    print(f"{'='*60}")
    print(f"年度数据：{len(metrics['years'])} 年")
    print(f"  营收：{metrics['annual_revenue']}")
    print(f"  净利润：{metrics['annual_profit']}")
    print(f"\n季度数据：{len(metrics['quarters'])} 个季度")
    print(f"  季度：{metrics['quarters']}")
    print(f"  季度营收：{metrics['quarterly_revenue']}")
    print(f"  季度净利润：{metrics['quarterly_profit']}")
    print(f"\n✅ 数据已保存到：{output_file}")


if __name__ == "__main__":
    main()
