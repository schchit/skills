#!/usr/bin/env python3
"""快速测试所有报告期数据获取"""

import json
import subprocess
from extract_metrics import extract_financial_metrics

def test_one_query(query):
    """测试单个查询"""
    cmd = [
        "mcporter", "call", "gildata_datamap-sse.FinancialDataAPI",
        f"query={query}",
        "--config", "/home/liust/openclaw/workspace/config/mcporter.json"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    if result.returncode == 0:
        response = json.loads(result.stdout)
        if response.get("code") == 0 and response.get("results"):
            rows = response["results"][0].get("origin_data", {}).get("rows", [])
            return rows
    return []

# 测试查询
queries = [
    "宁德时代 300750 2024 年年报 营业收入 净利润",
    "宁德时代 300750 2024 年一季报 营业收入 净利润",
    "宁德时代 300750 2024 年半年报 营业收入 净利润",
    "宁德时代 300750 2024 年三季报 营业收入 净利润",
]

all_rows = []
for query in queries:
    print(f"测试：{query[:50]}...", end=" ")
    rows = test_one_query(query)
    if rows:
        print(f"✅ {len(rows)}条")
        all_rows.extend(rows)
    else:
        print("❌ 无数据")

print(f"\n总数据行数：{len(all_rows)}")

# 显示第一行数据结构
if all_rows:
    print(f"\n第一行数据结构:")
    print(json.dumps(all_rows[0], ensure_ascii=False, indent=2))

# 提取指标
print(f"\n提取指标...")
metrics = extract_financial_metrics({"rows": all_rows})

print(f"\n年度数据:")
print(f"  年份：{metrics['years']}")
print(f"  营收：{metrics['annual_revenue']}")
print(f"  净利润：{metrics['annual_profit']}")

print(f"\n季度数据:")
print(f"  季度：{metrics['quarters']}")
print(f"  季度营收：{metrics['quarterly_revenue']}")
print(f"  季度净利润：{metrics['quarterly_profit']}")
