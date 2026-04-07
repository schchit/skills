#!/usr/bin/env python3
"""
测试季度数据获取
"""

import sys
sys.path.insert(0, '/home/liust/openclaw/workspace/skills/a-share-earnings-review-v2/scripts')

from fetch_financial_data import get_financial_statement, get_profitability_analysis, extract_financial_metrics
import json

def test_quarterly_data():
    """测试季度数据获取"""
    
    stock_code = "300750"
    company_name = "宁德时代"
    years = ["2024", "2023"]
    
    print("="*60)
    print(f"测试季度数据获取：{company_name} ({stock_code})")
    print("="*60)
    
    # 1. 获取财务报表数据（包含季度）
    print("\n[1/2] 获取财务报表数据（含季度）...")
    financial_data = get_financial_statement(
        stock_code, company_name, years, include_quarters=True
    )
    
    # 2. 获取盈利能力数据（包含季度）
    print("\n[2/2] 获取盈利能力分析（含季度）...")
    profitability_data = get_profitability_analysis(
        stock_code, company_name, years, include_quarters=True
    )
    
    # 3. 合并数据
    all_rows = []
    if financial_data.get("rows"):
        all_rows.extend(financial_data["rows"])
    if profitability_data.get("rows"):
        all_rows.extend(profitability_data["rows"])
    
    combined_data = {"rows": all_rows}
    
    # 4. 提取指标
    print("\n提取关键指标...")
    metrics = extract_financial_metrics(combined_data)
    
    # 5. 输出结果
    print("\n" + "="*60)
    print("年度数据:")
    print("="*60)
    print(f"年份：{metrics['years']}")
    print(f"营收：{metrics['annual_revenue']}")
    print(f"营收增速：{metrics['annual_revenue_growth']}")
    print(f"净利润：{metrics['annual_profit']}")
    print(f"净利润增速：{metrics['annual_profit_growth']}")
    
    print("\n" + "="*60)
    print("季度数据:")
    print("="*60)
    print(f"季度：{metrics['quarters']}")
    print(f"季度营收：{metrics['quarterly_revenue']}")
    print(f"季度营收增速：{metrics['quarterly_revenue_growth']}")
    print(f"季度净利润：{metrics['quarterly_profit']}")
    print(f"季度净利润增速：{metrics['quarterly_profit_growth']}")
    
    # 6. 保存结果
    output_file = "300750_quarterly_test.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 数据已保存到：{output_file}")
    
    return metrics

if __name__ == "__main__":
    test_quarterly_data()
