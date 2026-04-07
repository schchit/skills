#!/usr/bin/env python3
"""
A 股财报数据获取脚本 - 获取所有报告期（一季报、半年报、三季报、年报）
通过 mcporter CLI 调用聚源 MCP 接口

确保获取：
- 一季报（3 月 31 日）
- 半年报/中报（6 月 30 日）
- 三季报（9 月 30 日）
- 年报（12 月 31 日）
"""

import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, '/home/liust/openclaw/workspace/skills/a-share-earnings-review-v2/scripts')
from extract_metrics import extract_financial_metrics

MCP_CONFIG_PATH = "/home/liust/openclaw/workspace/config/mcporter.json"
MCP_SERVER = "gildata_datamap-sse"


# 报告期配置：同时使用多种表述确保能获取到数据
REPORT_PERIODS = {
    "年报": {
        "keywords": ["年报", "年度报告", "12 月 31 日"],
        "months": [12]
    },
    "一季报": {
        "keywords": ["一季报", "一季报告", "Q1", "3 月 31 日"],
        "months": [3]
    },
    "半年报": {
        "keywords": ["半年报", "中报", "半年度报告", "Q2", "6 月 30 日"],
        "months": [6]
    },
    "三季报": {
        "keywords": ["三季报", "三季报告", "Q3", "9 月 30 日"],
        "months": [9]
    }
}


def call_mcp_tool(tool_name: str, query: str, timeout: int = 90) -> Optional[Dict]:
    """
    通过 mcporter CLI 调用 MCP 工具
    
    Args:
        tool_name: MCP 工具名称
        query: 查询语句
        timeout: 超时时间（秒）
    
    Returns:
        工具返回结果
    """
    try:
        cmd = [
            "mcporter", "call", f"{MCP_SERVER}.{tool_name}",
            f"query={query}", "--config", MCP_CONFIG_PATH
        ]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            if response.get("code") == 0 and response.get("results"):
                return response["results"][0]
        
        return None
        
    except subprocess.TimeoutExpired:
        print(f"    ⚠ 超时（{timeout}秒）")
        return None
    except json.JSONDecodeError as e:
        print(f"    ⚠ JSON 解析错误：{e}")
        return None
    except Exception as e:
        print(f"    ⚠ 异常：{e}")
        return None


def fetch_all_periods_data(stock_code: str, company_name: str, 
                           years: List[str] = None,
                           verbose: bool = True) -> Dict:
    """
    获取所有报告期的财务数据
    
    Args:
        stock_code: 股票代码
        company_name: 公司名称
        years: 年份列表，默认最近 4 年
        verbose: 是否输出详细信息
    
    Returns:
        包含所有财务数据的字典
    """
    if years is None:
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 4, current_year)]
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"获取 {company_name} ({stock_code}) 所有报告期数据...")
        print(f"年份范围：{years}")
        print(f"报告期类型：一季报、半年报、三季报、年报")
        print(f"{'='*70}\n")
    
    all_rows = []
    successful_queries = 0
    total_queries = 0
    
    # 遍历每一年
    for year in years:
        if verbose:
            print(f"[{year}年]")
        
        # 遍历每个报告期
        for period_name, period_config in REPORT_PERIODS.items():
            # 为每个报告期尝试多种查询方式
            queries = []
            
            # 方式 1：使用报告期名称
            queries.append(f"{company_name} {stock_code} {year}年{period_name} 营业收入 净利润")
            
            # 方式 2：使用具体日期
            for keyword in period_config["keywords"]:
                if "月" in keyword and "日" in keyword:
                    queries.append(f"{company_name} {stock_code} {year}年{keyword} 利润表 营业收入 净利润")
                    break
            
            # 方式 3：简化查询（如果前两种方式失败）
            queries.append(f"{stock_code} {year}{period_name} 营业收入 净利润")
            
            # 执行查询
            period_data_obtained = False
            for query in queries:
                total_queries += 1
                
                if verbose:
                    print(f"  → 查询：{query[:55]}...", end=" ")
                
                result = call_mcp_tool("FinancialDataAPI", query)
                
                if result and result.get("origin_data", {}).get("rows"):
                    rows = result["origin_data"]["rows"]
                    all_rows.extend(rows)
                    
                    if verbose:
                        print(f"✅ {len(rows)}条")
                    
                    successful_queries += 1
                    period_data_obtained = True
                    break  # 成功后不再尝试其他查询
                else:
                    if verbose:
                        print("⚠ 无数据")
        
        if verbose:
            print()
    
    # 提取指标
    if verbose:
        print(f"{'='*70}")
        print(f"数据提取完成")
        print(f"  总查询次数：{total_queries}")
        print(f"  成功查询：{successful_queries}")
        print(f"  原始数据行数：{len(all_rows)}")
        print(f"{'='*70}\n")
    
    # 使用 extract_metrics 提取年度和季度指标
    combined_data = {"rows": all_rows}
    metrics = extract_financial_metrics(combined_data)
    
    # 构建返回数据（包含原始 rows 以便调试）
    data = {
        "stock_code": stock_code,
        "company_name": company_name,
        "fetch_time": datetime.now().isoformat(),
        "years_requested": years,
        "statistics": {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "success_rate": f"{successful_queries/total_queries*100:.1f}%" if total_queries > 0 else "0%",
            "raw_rows_count": len(all_rows)
        },
        "raw_data": {"rows": all_rows},  # 保存原始数据
        "metrics": metrics
    }
    
    return data


def print_summary(data: Dict):
    """打印数据摘要"""
    metrics = data["metrics"]
    
    print(f"\n{'='*70}")
    print("数据摘要")
    print(f"{'='*70}")
    
    # 年度数据
    print(f"\n📊 年度数据 ({len(metrics['years'])}年):")
    if metrics['years']:
        for i, year in enumerate(metrics['years']):
            revenue = metrics['annual_revenue'][i] if i < len(metrics['annual_revenue']) else None
            profit = metrics['annual_profit'][i] if i < len(metrics['annual_profit']) else None
            revenue_growth = metrics['annual_revenue_growth'][i] if i < len(metrics['annual_revenue_growth']) else None
            profit_growth = metrics['annual_profit_growth'][i] if i < len(metrics['annual_profit_growth']) else None
            
            print(f"  {year}年:")
            print(f"    营收：{revenue}亿元 (同比：{revenue_growth}%)")
            print(f"    净利润：{profit}亿元 (同比：{profit_growth}%)")
    else:
        print("  ⚠ 无年度数据")
    
    # 季度数据
    print(f"\n📈 季度数据 ({len(metrics['quarters'])}个季度):")
    if metrics['quarters']:
        for i, quarter in enumerate(metrics['quarters']):
            revenue = metrics['quarterly_revenue'][i] if i < len(metrics['quarterly_revenue']) else None
            profit = metrics['quarterly_profit'][i] if i < len(metrics['quarterly_profit']) else None
            revenue_growth = metrics['quarterly_revenue_growth'][i] if i < len(metrics['quarterly_revenue_growth']) else None
            profit_growth = metrics['quarterly_profit_growth'][i] if i < len(metrics['quarterly_profit_growth']) else None
            
            print(f"  {quarter}:")
            print(f"    营收：{revenue}亿元 (同比：{revenue_growth}%)")
            print(f"    净利润：{profit}亿元 (同比：{profit_growth}%)")
    else:
        print("  ⚠ 无季度数据")
    
    print(f"\n{'='*70}\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='获取 A 股所有报告期财务数据')
    parser.add_argument('stock_code', help='股票代码（如 300750）')
    parser.add_argument('company_name', nargs='?', help='公司名称（如 宁德时代）')
    parser.add_argument('years', nargs='*', help='年份列表（如 2024 2023 2022 2021）')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-q', '--quiet', action='store_true', help='静默模式')
    
    args = parser.parse_args()
    
    stock_code = args.stock_code
    company_name = args.company_name or stock_code
    years = args.years if args.years else ["2024", "2023", "2022", "2021"]
    
    # 获取数据
    data = fetch_all_periods_data(stock_code, company_name, years, verbose=not args.quiet)
    
    # 打印摘要
    if not args.quiet:
        print_summary(data)
    
    # 保存文件
    output_file = args.output or f"{stock_code}_all_periods.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 数据已保存到：{output_file}")
    
    # 返回状态码
    if data["statistics"]["successful_queries"] > 0:
        return 0
    else:
        print("⚠ 警告：未获取到任何数据")
        return 1


if __name__ == "__main__":
    sys.exit(main())
