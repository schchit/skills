#!/usr/bin/env python3
"""
A 股财报数据获取脚本（重构版）
通过 mcporter CLI 调用聚源 MCP 接口获取财务数据

支持获取：
- 年度数据（年报）
- 季度数据（一季报、中报、三季报）
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# 导入指标提取模块
from extract_metrics import extract_financial_metrics


# mcporter 配置路径
MCP_CONFIG_PATH = "/home/liust/openclaw/workspace/config/mcporter.json"
# MCP 服务名称（需在 mcporter 中预先配置）
# jy-financedata-tool: 主营构成等工具
# jy-financedata-api: 财务数据、财务指标等 API
MCP_TOOL_SERVER = "jy-financedata-tool"
MCP_API_SERVER = "jy-financedata-api"

# 可用工具列表：
# - FinancialDataAPI: 获取财务报表数据（利润表、资产负债表、现金流量表、财务指标）- 使用 jy-financedata-api
# - MainOperIncData: 获取主营构成数据（分产品/行业/地区收入）- 使用 jy-financedata-tool


def call_mcp_tool(tool_name: str, query: str, server: str = None) -> Optional[Dict]:
    """
    通过 mcporter CLI 调用 MCP 工具
    
    Args:
        tool_name: MCP 工具名称（如 FinancialDataAPI、MainOperIncData）
        query: 自然语言查询（所有工具统一使用 query 参数）
        server: MCP 服务名称，默认自动选择
    
    Returns:
        工具返回结果字典
    """
    # 自动选择服务：主营构成用 jy-financedata-tool，其他用 jy-financedata-api
    if server is None:
        if tool_name == "MainOperIncData":
            server = MCP_TOOL_SERVER
        else:
            server = MCP_API_SERVER
    
    try:
        cmd = [
            "mcporter",
            "call",
            f"{server}.{tool_name}",
            f"query={query}",
            "--config",
            MCP_CONFIG_PATH
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            if response.get("code") == 0 and response.get("results"):
                return response["results"][0]
            else:
                print(f"警告：{tool_name} 返回空结果")
                return None
        else:
            print(f"错误：调用 {tool_name} 失败 - {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"错误：调用 {tool_name} 超时")
        return None
    except json.JSONDecodeError as e:
        print(f"错误：解析 {tool_name} 响应失败 - {e}")
        return None
    except Exception as e:
        print(f"错误：调用 {tool_name} 异常 - {e}")
        return None


def parse_financial_data(result: Dict) -> Dict:
    """解析 FinancialDataAPI 返回的数据"""
    if not result or not result.get("origin_data", {}).get("rows"):
        return {}
    
    data = result["origin_data"]
    rows = data.get("rows", [])
    nlpcolumnname = data.get("nlpcolumnname", {})
    
    # 构建字段映射
    parsed = {
        "rows": [],
        "columns": list(nlpcolumnname.values()) if nlpcolumnname else []
    }
    
    for row in rows:
        parsed_row = {}
        for key, value in row.items():
            # 使用中文列名作为键
            cn_name = nlpcolumnname.get(key, key)
            parsed_row[cn_name] = value
        parsed["rows"].append(parsed_row)
    
    return parsed


def get_financial_statement(stock_code: str, company_name: str, 
                            years: List[str] = None,
                            include_quarters: bool = True) -> Dict:
    """
    获取财务报表数据（利润表、资产负债表、现金流量表）
    
    Args:
        stock_code: 股票代码
        company_name: 公司名称
        years: 年份列表，默认最近 4 年
        include_quarters: 是否包含季度数据
    
    Returns:
        财务报表数据字典
    """
    if years is None:
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 4, current_year)]
    
    # 构建查询：同时获取年报和季报数据
    queries = []
    for year in years:
        # 年报
        queries.append(f"{company_name} {stock_code} {year}年 年报 营业收入 净利润 营业成本")
        # 季报（一季报、中报、三季报）
        if include_quarters:
            queries.append(f"{company_name} {stock_code} {year}年 一季报 营业收入 净利润")
            queries.append(f"{company_name} {stock_code} {year}年 中报 营业收入 净利润")
            queries.append(f"{company_name} {stock_code} {year}年 三季报 营业收入 净利润")
    
    all_rows = []
    for query in queries:
        print(f"  → {query[:60]}...")
        # 使用 FinancialDataAPI 工具获取利润表数据
        result = call_mcp_tool("FinancialDataAPI", query)
        if result and result.get("origin_data", {}).get("rows"):
            all_rows.extend(result["origin_data"]["rows"])
    
    # 合并结果
    if all_rows:
        return {
            "rows": all_rows,
            "columns": ["时间", "报告期", "财务科目名称", "财务科目数额", "同比 (%)", "展示单位"]
        }
    return {}


def get_profitability_analysis(stock_code: str, company_name: str,
                                years: List[str] = None,
                                include_quarters: bool = True) -> Dict:
    """
    获取盈利能力分析数据（毛利率、净利率、ROE 等）
    
    Args:
        stock_code: 股票代码
        company_name: 公司名称
        years: 年份列表
        include_quarters: 是否包含季度数据
    
    Returns:
        盈利能力分析数据字典
    """
    if years is None:
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 4, current_year)]
    
    # 构建查询：同时获取年报和季报的盈利能力数据
    queries = []
    for year in years:
        queries.append(f"{company_name} {stock_code} {year}年 年报 毛利率 净利率 销售费用 管理费用 研发费用")
        if include_quarters:
            queries.append(f"{company_name} {stock_code} {year}年 一季报 毛利率 净利率")
            queries.append(f"{company_name} {stock_code} {year}年 中报 毛利率 净利率")
            queries.append(f"{company_name} {stock_code} {year}年 三季报 毛利率 净利率")
    
    all_rows = []
    for query in queries:
        print(f"  → {query[:60]}...")
        # 使用 FinancialDataAPI 工具获取财务指标数据
        result = call_mcp_tool("FinancialDataAPI", query)
        if result and result.get("origin_data", {}).get("rows"):
            all_rows.extend(result["origin_data"]["rows"])
    
    if all_rows:
        return {
            "rows": all_rows,
            "columns": ["时间", "报告期", "财务分析指标名称", "财务分析指标数额", "展示单位"]
        }
    return {}


def get_main_business_composition(stock_code: str, company_name: str,
                                   report_year: str = None) -> Dict:
    """
    获取主营构成数据（分产品/行业/地区）
    
    Args:
        stock_code: 股票代码
        company_name: 公司名称
        report_year: 报告年份，默认最新
    
    Returns:
        主营构成数据字典
    """
    if report_year is None:
        report_year = str(datetime.now().year - 1)
    
    query = f"{company_name} {stock_code} {report_year} 年 主营业务收入 分产品 分行业 分地区"
    
    print(f"获取主营构成：{query}")
    # 使用 MainOperIncData 工具获取主营构成
    result = call_mcp_tool("MainOperIncData", query)
    
    if result:
        return parse_financial_data(result)
    return {}


def get_cash_flow_data(stock_code: str, company_name: str,
                       years: List[str] = None) -> Dict:
    """
    获取现金流量表数据
    
    Args:
        stock_code: 股票代码
        company_name: 公司名称
        years: 年份列表
    
    Returns:
        现金流量数据字典
    """
    if years is None:
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 4, current_year)]
    
    years_str = " ".join(years)
    query = f"{company_name} {stock_code} {years_str} 年 经营活动现金流 投资活动现金流 筹资活动现金流"
    
    print(f"获取现金流量数据：{query}")
    # 使用 FinancialDataAPI 工具获取现金流量表数据
    result = call_mcp_tool("FinancialDataAPI", query)
    
    if result:
        return parse_financial_data(result)
    return {}


def get_performance_forecast(stock_code: str, company_name: str) -> Dict:
    """
    获取业绩预测数据
    
    Args:
        stock_code: 股票代码
        company_name: 公司名称
    
    Returns:
        业绩预测数据字典
    """
    query = f"{company_name} {stock_code} 盈利预测 营收预测 净利润预测"
    
    print(f"获取业绩预测：{query}")
    # 使用 FinancialDataAPI 工具获取盈利预测
    result = call_mcp_tool("FinancialDataAPI", query)
    
    if result:
        return parse_financial_data(result)
    return {}


def get_consensus_expectation(stock_code: str, company_name: str) -> Dict:
    """
    获取一致预期数据（分析师 consensus）
    
    Args:
        stock_code: 股票代码
        company_name: 公司名称
    
    Returns:
        一致预期数据字典
    """
    query = f"{company_name} {stock_code} 一致预期 目标价 评级 盈利预测"
    
    print(f"获取一致预期：{query}")
    # 使用 FinancialDataAPI 工具获取一致预期
    result = call_mcp_tool("FinancialDataAPI", query)
    
    if result:
        return parse_financial_data(result)
    return {}


def get_stock_news(stock_code: str, company_name: str,
                   days: int = 90) -> List[Dict]:
    """
    获取股票舆情/新闻数据
    
    Args:
        stock_code: 股票代码
        company_name: 公司名称
        days: 获取最近 N 天的新闻
    
    Returns:
        新闻舆情列表
    """
    query = f"{company_name} {stock_code} 最近{days}天 新闻 舆情 公告 重大事项"
    
    print(f"获取股票舆情（最近{days}天）：{query}")
    # 使用 FinancialDataAPI 工具获取股票舆情/新闻
    result = call_mcp_tool("FinancialDataAPI", query)
    
    if result:
        return [parse_financial_data(result)]
    return []


def get_announcements(stock_code: str, company_name: str,
                      days: int = 90) -> List[Dict]:
    """
    获取公司公告数据
    
    Args:
        stock_code: 股票代码
        company_name: 公司名称
        days: 获取最近 N 天的公告
    
    Returns:
        公告列表
    """
    query = f"{company_name} {stock_code} 最近{days}天 公告 财报公告 业绩预告"
    
    print(f"获取公司公告（最近{days}天）：{query}")
    # 使用 FinancialDataAPI 工具获取公司公告
    result = call_mcp_tool("FinancialDataAPI", query)
    
    if result:
        return [parse_financial_data(result)]
    return []


def fetch_all_financial_data(stock_code: str, company_name: str = None,
                              years: List[str] = None) -> Dict:
    """
    获取财报点评所需的全部数据
    
    Args:
        stock_code: 股票代码
        company_name: 公司名称（可选，会自动识别）
        years: 年份列表（可选，默认最近 4 年）
    
    Returns:
        包含所有财务数据的字典
    """
    print(f"\n{'='*60}")
    print(f"开始获取 {stock_code} 财务数据...")
    print(f"{'='*60}\n")
    
    data = {
        "stock_code": stock_code,
        "company_name": company_name,
        "fetch_time": datetime.now().isoformat(),
        "mcp_config": MCP_CONFIG_PATH,
        "raw_data": {},
        "metrics": {}
    }
    
    # 1. 获取财务报表数据
    print("[1/7] 获取财务报表数据...")
    data["raw_data"]["financial_statement"] = get_financial_statement(
        stock_code, company_name or stock_code, years
    )
    
    # 2. 获取盈利能力分析
    print("[2/7] 获取盈利能力分析...")
    data["raw_data"]["profitability"] = get_profitability_analysis(
        stock_code, company_name or stock_code, years
    )
    
    # 3. 获取主营构成
    print("[3/7] 获取主营构成...")
    data["raw_data"]["main_business"] = get_main_business_composition(
        stock_code, company_name or stock_code
    )
    
    # 4. 获取现金流量
    print("[4/7] 获取现金流量数据...")
    data["raw_data"]["cash_flow"] = get_cash_flow_data(
        stock_code, company_name or stock_code, years
    )
    
    # 5. 获取业绩预测
    print("[5/7] 获取业绩预测...")
    data["raw_data"]["performance_forecast"] = get_performance_forecast(
        stock_code, company_name or stock_code
    )
    
    # 6. 获取一致预期
    print("[6/7] 获取一致预期...")
    data["raw_data"]["consensus"] = get_consensus_expectation(
        stock_code, company_name or stock_code
    )
    
    # 7. 获取舆情和公告
    print("[7/7] 获取舆情和公告...")
    data["raw_data"]["news"] = get_stock_news(stock_code, company_name or stock_code)
    data["raw_data"]["announcements"] = get_announcements(stock_code, company_name or stock_code)
    
    # 提取关键指标
    print("\n提取关键财务指标...")
    all_data = {}
    for key, value in data["raw_data"].items():
        if isinstance(value, dict) and value.get("rows"):
            if "rows" not in all_data:
                all_data["rows"] = []
            all_data["rows"].extend(value.get("rows", []))
    
    data["metrics"] = extract_financial_metrics(all_data)
    
    print(f"\n{'='*60}")
    print(f"数据获取完成！")
    print(f"{'='*60}\n")
    
    return data


def save_to_json(data: Dict, output_path: str):
    """保存数据到 JSON 文件"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存到：{output_path}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python fetch_financial_data.py <股票代码> [公司名称] [年份...]")
        print("示例：python fetch_financial_data.py 300750 宁德时代")
        print("      python fetch_financial_data.py 300750 宁德时代 2024 2023 2022 2021")
        sys.exit(1)
    
    stock_code = sys.argv[1]
    company_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 提取年份参数
    years = []
    for arg in sys.argv[3:]:
        if arg.isdigit() and len(arg) == 4:
            years.append(arg)
    
    if not years:
        years = None  # 使用默认最近 4 年
    
    # 获取数据
    data = fetch_all_financial_data(stock_code, company_name, years)
    
    # 保存数据
    output_file = f"{stock_code}_financial_data.json"
    save_to_json(data, output_file)
    
    # 输出摘要
    print("\n=== 数据摘要 ===")
    metrics = data.get("metrics", {})
    print(f"年份：{metrics.get('years', [])}")
    print(f"营收：{metrics.get('annual_revenue', [])}")
    print(f"净利润：{metrics.get('annual_profit', [])}")
    print(f"毛利率：{metrics.get('gross_margin', [])}")
    
    print("\n✅ 完成！")


if __name__ == "__main__":
    main()