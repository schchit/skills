#!/usr/bin/env python3
"""
从原始财务数据中提取年度和季度指标
"""

import json
from typing import Dict, List, Any


def extract_financial_metrics(data: Dict) -> Dict:
    """
    从原始数据中提取关键财务指标（包括年度和季度数据）
    
    Args:
        data: 原始财务数据字典，包含 rows 列表
    
    Returns:
        结构化财务指标字典
    """
    metrics = {
        # 年度数据
        "years": [],
        "annual_revenue": [],
        "annual_revenue_growth": [],
        "annual_profit": [],
        "annual_profit_growth": [],
        "annual_gross_margin": [],
        "annual_operating_cost": [],
        "annual_selling_expense": [],
        "annual_admin_expense": [],
        "annual_rd_expense": [],
        # 季度数据
        "quarters": [],
        "quarterly_revenue": [],
        "quarterly_revenue_growth": [],
        "quarterly_profit": [],
        "quarterly_profit_growth": [],
        "quarterly_gross_margin": [],
        "quarterly_net_margin": []
    }
    
    if not data or not data.get("rows"):
        return metrics
    
    rows = data["rows"]
    
    # 按日期和报告期类型分组
    annual_data = {}  # 年度数据：{year: {subject: value}}
    quarterly_data = {}  # 季度数据：{quarter: {subject: value}}
    
    for row in rows:
        # 支持中英文字段名
        date = row.get("date", row.get("时间", row.get("日期", "")))
        if not date or len(date) < 4:
            continue
        
        year = date[:4]
        if not year.isdigit():
            continue
        
        report_type = row.get("reportdate", row.get("报告期", ""))
        subject = row.get("finstatementsubject", row.get("财务科目名称", row.get("财务分析指标名称", "")))
        value_str = row.get("financevalue", row.get("财务科目数额", row.get("财务分析指标数额", "")))
        unit = row.get("unit", row.get("展示单位", ""))
        yoy_str = row.get("yoy", row.get("同比 (%)", None))
        
        # 转换数值
        try:
            if value_str and value_str not in ["null", "None", ""]:
                value = float(value_str)
                # 单位转换（万元→亿元）
                if unit == "万元":
                    value /= 10000
            else:
                value = None
        except (ValueError, TypeError):
            value = None
        
        # 转换同比增速
        try:
            yoy = float(yoy_str) if yoy_str and yoy_str not in ["null", "None", ""] else None
        except (ValueError, TypeError):
            yoy = None
        
        # 判断是年度还是季度数据
        is_annual = "年报" in report_type or "年度" in report_type or "12 月" in date
        is_quarterly = any(q in report_type for q in ["一季报", "中报", "三季报", "季报", "Q1", "Q2", "Q3"]) or \
                       any(m in date for m in ["-03-31", "-06-30", "-09-30"])
        
        if is_annual:
            if year not in annual_data:
                annual_data[year] = {}
            
            # 提取科目数据
            if "营业收入" in subject:
                annual_data[year]["revenue"] = value
                annual_data[year]["revenue_yoy"] = yoy
            elif "净利润" in subject and "归母" not in subject:
                annual_data[year]["profit"] = value
                annual_data[year]["profit_yoy"] = yoy
            elif "归母净利润" in subject or "归属母公司" in subject:
                annual_data[year]["profit"] = value
                annual_data[year]["profit_yoy"] = yoy
            elif "毛利率" in subject or "销售毛利率" in subject:
                annual_data[year]["gross_margin"] = value
            elif "净利率" in subject or "销售净利率" in subject:
                annual_data[year]["net_margin"] = value
            elif "营业成本" in subject:
                annual_data[year]["operating_cost"] = value
            elif "销售费用" in subject:
                annual_data[year]["selling_expense"] = value
            elif "管理费用" in subject:
                annual_data[year]["admin_expense"] = value
            elif "研发费用" in subject:
                annual_data[year]["rd_expense"] = value
                
        elif is_quarterly:
            # 季度标识
            if "一季报" in report_type or "一季" in report_type:
                quarter = f"{year}Q1"
            elif "中报" in report_type or "二季" in report_type or "半年报" in report_type:
                quarter = f"{year}Q2"
            elif "三季报" in report_type or "三季" in report_type:
                quarter = f"{year}Q3"
            elif "四季报" in report_type or "四季" in report_type:
                quarter = f"{year}Q4"
            else:
                continue
            
            if quarter not in quarterly_data:
                quarterly_data[quarter] = {}
            
            # 提取科目数据
            if "营业收入" in subject:
                quarterly_data[quarter]["revenue"] = value
                quarterly_data[quarter]["revenue_yoy"] = yoy
            elif "净利润" in subject and "归母" not in subject:
                quarterly_data[quarter]["profit"] = value
                quarterly_data[quarter]["profit_yoy"] = yoy
            elif "归母净利润" in subject or "归属母公司" in subject:
                quarterly_data[quarter]["profit"] = value
                quarterly_data[quarter]["profit_yoy"] = yoy
            elif "毛利率" in subject or "销售毛利率" in subject:
                quarterly_data[quarter]["gross_margin"] = value
            elif "净利率" in subject or "销售净利率" in subject:
                quarterly_data[quarter]["net_margin"] = value
    
    # 按年份排序
    sorted_years = sorted(annual_data.keys())
    metrics["years"] = sorted_years
    
    for year in sorted_years:
        yd = annual_data[year]
        metrics["annual_revenue"].append(yd.get("revenue"))
        metrics["annual_revenue_growth"].append(yd.get("revenue_yoy"))
        metrics["annual_profit"].append(yd.get("profit"))
        metrics["annual_profit_growth"].append(yd.get("profit_yoy"))
        if "annual_gross_margin" in metrics:
            metrics["annual_gross_margin"].append(yd.get("gross_margin"))
        if "annual_net_margin" in metrics:
            metrics["annual_net_margin"].append(yd.get("net_margin"))
        if "annual_operating_cost" in metrics:
            metrics["annual_operating_cost"].append(yd.get("operating_cost"))
        if "annual_selling_expense" in metrics:
            metrics["annual_selling_expense"].append(yd.get("selling_expense"))
        if "annual_admin_expense" in metrics:
            metrics["annual_admin_expense"].append(yd.get("admin_expense"))
        if "annual_rd_expense" in metrics:
            metrics["annual_rd_expense"].append(yd.get("rd_expense"))
    
    # 按季度排序
    sorted_quarters = sorted(quarterly_data.keys())
    metrics["quarters"] = sorted_quarters
    
    for quarter in sorted_quarters:
        qd = quarterly_data[quarter]
        metrics["quarterly_revenue"].append(qd.get("revenue"))
        metrics["quarterly_revenue_growth"].append(qd.get("revenue_yoy"))
        metrics["quarterly_profit"].append(qd.get("profit"))
        metrics["quarterly_profit_growth"].append(qd.get("profit_yoy"))
        metrics["quarterly_gross_margin"].append(qd.get("gross_margin"))
        metrics["quarterly_net_margin"].append(qd.get("net_margin"))
    
    return metrics


if __name__ == "__main__":
    # 测试
    test_data = {
        "rows": [
            {"时间": "2024-12-31", "报告期": "年报", "财务科目名称": "营业收入", "财务科目数额": "3620.13", "展示单位": "亿元", "同比 (%)": "-9.70"},
            {"时间": "2024-12-31", "报告期": "年报", "财务科目名称": "归母净利润", "财务科目数额": "540.07", "展示单位": "亿元", "同比 (%)": "15.50"},
            {"时间": "2024-09-30", "报告期": "三季报", "财务科目名称": "营业收入", "财务科目数额": "2590.45", "展示单位": "亿元", "同比 (%)": "-12.09"},
            {"时间": "2024-09-30", "报告期": "三季报", "财务科目名称": "归母净利润", "财务科目数额": "387.33", "展示单位": "亿元", "同比 (%)": "19.12"},
        ]
    }
    
    result = extract_financial_metrics(test_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
