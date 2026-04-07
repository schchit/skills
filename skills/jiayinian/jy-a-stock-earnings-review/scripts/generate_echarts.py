#!/usr/bin/env python3
"""
echarts 图表生成脚本
为 A 股财报点评报告生成标准化 echarts 配置
"""

import json
from typing import Dict, List, Any, Optional


class EchartsGenerator:
    """财报点评图表生成器"""
    
    # 研报风格配色
    COLORS = {
        "primary": "#5470C6",      # 主色蓝
        "secondary": "#91CC75",    # 辅助色绿
        "accent": "#EE6666",       # 强调色红
        "neutral": "#73C0DE",      # 中性色
        "dark": "#3BA274",         # 深色
        "light": "#FAC858",        # 浅色
        "gray": "#999999",         # 灰色
    }
    
    def __init__(self):
        self.default_theme = "white"
    
    def generate_revenue_annual_chart(self, years: List[str], 
                                       revenue: List[float], 
                                       growth: List[float]) -> Dict:
        """
        图表 1：公司年度营业收入及同比增速
        
        Args:
            years: 年份列表 ["2021", "2022", "2023", "2024", "2025"]
            revenue: 营业收入列表（亿元）
            growth: 同比增速列表（%）
        """
        return {
            "title": {
                "text": "图 1：公司年度营业收入及同比增速",
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "cross"}
            },
            "legend": {
                "data": ["营业收入", "同比增速"],
                "bottom": "10%"
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "15%",
                "containLabel": True
            },
            "xAxis": [
                {
                    "type": "category",
                    "data": years,
                    "axisTick": {"alignWithLabel": True}
                }
            ],
            "yAxis": [
                {
                    "type": "value",
                    "name": "营业收入 (亿元)",
                    "position": "left",
                    "axisLine": {"show": True, "lineStyle": {"color": self.COLORS["primary"]}},
                    "axisLabel": {"formatter": "{value}"}
                },
                {
                    "type": "value",
                    "name": "同比增速 (%)",
                    "position": "right",
                    "axisLine": {"show": True, "lineStyle": {"color": self.COLORS["accent"]}},
                    "axisLabel": {"formatter": "{value}%"},
                    "splitLine": {"show": False}
                }
            ],
            "series": [
                {
                    "name": "营业收入",
                    "type": "bar",
                    "barWidth": "40%",
                    "itemStyle": {"color": self.COLORS["primary"]},
                    "data": revenue,
                    "label": {"show": True, "position": "top", "formatter": "{c}"}
                },
                {
                    "name": "同比增速",
                    "type": "line",
                    "yAxisIndex": 1,
                    "itemStyle": {"color": self.COLORS["accent"]},
                    "lineStyle": {"width": 3},
                    "symbol": "circle",
                    "symbolSize": 8,
                    "data": growth,
                    "label": {"show": True, "position": "top", "formatter": "{c}%"}
                }
            ]
        }
    
    def generate_revenue_quarterly_chart(self, quarters: List[str],
                                          revenue: List[float],
                                          growth: List[float]) -> Dict:
        """
        图表 2：公司单季度营业收入及同比增速
        """
        return {
            "title": {
                "text": "图 2：公司单季度营业收入及同比增速",
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "cross"}
            },
            "legend": {
                "data": ["营业收入", "同比增速"],
                "bottom": "10%"
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "15%",
                "containLabel": True
            },
            "xAxis": [
                {
                    "type": "category",
                    "data": quarters,
                    "axisTick": {"alignWithLabel": True}
                }
            ],
            "yAxis": [
                {
                    "type": "value",
                    "name": "营业收入 (亿元)",
                    "position": "left",
                    "axisLine": {"show": True, "lineStyle": {"color": self.COLORS["primary"]}}
                },
                {
                    "type": "value",
                    "name": "同比增速 (%)",
                    "position": "right",
                    "axisLine": {"show": True, "lineStyle": {"color": self.COLORS["accent"]}},
                    "axisLabel": {"formatter": "{value}%"},
                    "splitLine": {"show": False}
                }
            ],
            "series": [
                {
                    "name": "营业收入",
                    "type": "bar",
                    "barWidth": "40%",
                    "itemStyle": {"color": self.COLORS["neutral"]},
                    "data": revenue
                },
                {
                    "name": "同比增速",
                    "type": "line",
                    "yAxisIndex": 1,
                    "itemStyle": {"color": self.COLORS["accent"]},
                    "lineStyle": {"width": 3},
                    "symbol": "circle",
                    "symbolSize": 8,
                    "data": growth
                }
            ]
        }
    
    def generate_profit_annual_chart(self, years: List[str],
                                      profit: List[float],
                                      growth: List[float]) -> Dict:
        """
        图表 3：公司年度归母净利润及同比增速
        """
        return {
            "title": {
                "text": "图 3：公司年度归母净利润及同比增速",
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "cross"}
            },
            "legend": {
                "data": ["归母净利润", "同比增速"],
                "bottom": "10%"
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "15%",
                "containLabel": True
            },
            "xAxis": [
                {
                    "type": "category",
                    "data": years,
                    "axisTick": {"alignWithLabel": True}
                }
            ],
            "yAxis": [
                {
                    "type": "value",
                    "name": "归母净利润 (亿元)",
                    "position": "left",
                    "axisLine": {"show": True, "lineStyle": {"color": self.COLORS["secondary"]}}
                },
                {
                    "type": "value",
                    "name": "同比增速 (%)",
                    "position": "right",
                    "axisLine": {"show": True, "lineStyle": {"color": self.COLORS["accent"]}},
                    "axisLabel": {"formatter": "{value}%"},
                    "splitLine": {"show": False}
                }
            ],
            "series": [
                {
                    "name": "归母净利润",
                    "type": "bar",
                    "barWidth": "40%",
                    "itemStyle": {"color": self.COLORS["secondary"]},
                    "data": profit,
                    "label": {"show": True, "position": "top", "formatter": "{c}"}
                },
                {
                    "name": "同比增速",
                    "type": "line",
                    "yAxisIndex": 1,
                    "itemStyle": {"color": self.COLORS["accent"]},
                    "lineStyle": {"width": 3},
                    "symbol": "circle",
                    "symbolSize": 8,
                    "data": growth,
                    "label": {"show": True, "position": "top", "formatter": "{c}%"}
                }
            ]
        }
    
    def generate_profit_quarterly_chart(self, quarters: List[str],
                                         profit: List[float],
                                         growth: List[float]) -> Dict:
        """
        图表 4：公司单季度归母净利润及同比增速
        """
        return {
            "title": {
                "text": "图 4：公司单季度归母净利润及同比增速",
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "cross"}
            },
            "legend": {
                "data": ["归母净利润", "同比增速"],
                "bottom": "10%"
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "15%",
                "containLabel": True
            },
            "xAxis": [
                {
                    "type": "category",
                    "data": quarters,
                    "axisTick": {"alignWithLabel": True}
                }
            ],
            "yAxis": [
                {
                    "type": "value",
                    "name": "归母净利润 (亿元)",
                    "position": "left",
                    "axisLine": {"show": True, "lineStyle": {"color": self.COLORS["dark"]}}
                },
                {
                    "type": "value",
                    "name": "同比增速 (%)",
                    "position": "right",
                    "axisLine": {"show": True, "lineStyle": {"color": self.COLORS["accent"]}},
                    "axisLabel": {"formatter": "{value}%"},
                    "splitLine": {"show": False}
                }
            ],
            "series": [
                {
                    "name": "归母净利润",
                    "type": "bar",
                    "barWidth": "40%",
                    "itemStyle": {"color": self.COLORS["dark"]},
                    "data": profit
                },
                {
                    "name": "同比增速",
                    "type": "line",
                    "yAxisIndex": 1,
                    "itemStyle": {"color": self.COLORS["accent"]},
                    "lineStyle": {"width": 3},
                    "symbol": "circle",
                    "symbolSize": 8,
                    "data": growth
                }
            ]
        }
    
    def generate_margin_annual_chart(self, years: List[str],
                                      gross_margin: List[float],
                                      net_margin: List[float]) -> Dict:
        """
        图表 5：公司年度毛利率、净利率
        """
        return {
            "title": {
                "text": "图 5：公司年度毛利率、净利率",
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "line"}
            },
            "legend": {
                "data": ["毛利率", "净利率"],
                "bottom": "10%"
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "15%",
                "containLabel": True
            },
            "xAxis": [
                {
                    "type": "category",
                    "data": years,
                    "axisTick": {"alignWithLabel": True}
                }
            ],
            "yAxis": [
                {
                    "type": "value",
                    "name": "毛利率 (%)",
                    "position": "left",
                    "axisLine": {"show": True, "lineStyle": {"color": self.COLORS["primary"]}},
                    "axisLabel": {"formatter": "{value}%"}
                },
                {
                    "type": "value",
                    "name": "净利率 (%)",
                    "position": "right",
                    "axisLine": {"show": True, "lineStyle": {"color": self.COLORS["secondary"]}},
                    "axisLabel": {"formatter": "{value}%"},
                    "splitLine": {"show": True, "lineStyle": {"type": "dashed"}}
                }
            ],
            "series": [
                {
                    "name": "毛利率",
                    "type": "line",
                    "smooth": True,
                    "itemStyle": {"color": self.COLORS["primary"]},
                    "lineStyle": {"width": 3},
                    "symbol": "circle",
                    "symbolSize": 8,
                    "data": gross_margin,
                    "label": {"show": True, "position": "top", "formatter": "{c}%"}
                },
                {
                    "name": "净利率",
                    "type": "line",
                    "smooth": True,
                    "itemStyle": {"color": self.COLORS["secondary"]},
                    "lineStyle": {"width": 3},
                    "symbol": "circle",
                    "symbolSize": 8,
                    "data": net_margin,
                    "label": {"show": True, "position": "bottom", "formatter": "{c}%"}
                }
            ]
        }
    
    def generate_margin_quarterly_chart(self, quarters: List[str],
                                         gross_margin: List[float],
                                         net_margin: List[float]) -> Dict:
        """
        图表 6：公司单季度毛利率和净利率
        """
        return {
            "title": {
                "text": "图 6：公司单季度毛利率和净利率",
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "line"}
            },
            "legend": {
                "data": ["毛利率", "净利率"],
                "bottom": "10%"
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "15%",
                "containLabel": True
            },
            "xAxis": [
                {
                    "type": "category",
                    "data": quarters,
                    "axisTick": {"alignWithLabel": True}
                }
            ],
            "yAxis": [
                {
                    "type": "value",
                    "name": "毛利率 (%)",
                    "position": "left",
                    "axisLine": {"show": True, "lineStyle": {"color": self.COLORS["primary"]}},
                    "axisLabel": {"formatter": "{value}%"}
                },
                {
                    "type": "value",
                    "name": "净利率 (%)",
                    "position": "right",
                    "axisLine": {"show": True, "lineStyle": {"color": self.COLORS["secondary"]}},
                    "axisLabel": {"formatter": "{value}%"},
                    "splitLine": {"show": True, "lineStyle": {"type": "dashed"}}
                }
            ],
            "series": [
                {
                    "name": "毛利率",
                    "type": "line",
                    "smooth": True,
                    "itemStyle": {"color": self.COLORS["primary"]},
                    "lineStyle": {"width": 3},
                    "symbol": "circle",
                    "symbolSize": 8,
                    "data": gross_margin
                },
                {
                    "name": "净利率",
                    "type": "line",
                    "smooth": True,
                    "itemStyle": {"color": self.COLORS["secondary"]},
                    "lineStyle": {"width": 3},
                    "symbol": "circle",
                    "symbolSize": 8,
                    "data": net_margin
                }
            ]
        }
    
    def generate_expense_ratio_annual_chart(self, years: List[str],
                                             expense_data: Dict[str, List[float]]) -> Dict:
        """
        图表 7：公司年度期间费用率
        
        Args:
            expense_data: 费用数据字典
                {
                    "销售费用率": [x, x, x],
                    "管理费用率": [x, x, x],
                    "研发费用率": [x, x, x],
                    "财务费用率": [x, x, x]
                }
        """
        series_list = []
        colors = [self.COLORS["primary"], self.COLORS["secondary"], 
                  self.COLORS["neutral"], self.COLORS["dark"]]
        
        for i, (name, data) in enumerate(expense_data.items()):
            series_list.append({
                "name": name,
                "type": "line",
                "smooth": True,
                "itemStyle": {"color": colors[i % len(colors)]},
                "lineStyle": {"width": 3},
                "symbol": "circle",
                "symbolSize": 8,
                "data": data
            })
        
        return {
            "title": {
                "text": "图 7：公司年度期间费用率",
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "line"}
            },
            "legend": {
                "data": list(expense_data.keys()),
                "bottom": "10%"
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "15%",
                "containLabel": True
            },
            "xAxis": [
                {
                    "type": "category",
                    "data": years,
                    "axisTick": {"alignWithLabel": True}
                }
            ],
            "yAxis": [
                {
                    "type": "value",
                    "name": "费用率 (%)",
                    "axisLabel": {"formatter": "{value}%"}
                }
            ],
            "series": series_list
        }
    
    def generate_expense_ratio_quarterly_chart(self, quarters: List[str],
                                                expense_data: Dict[str, List[float]]) -> Dict:
        """
        图表 8：公司单季度期间费用率
        """
        series_list = []
        colors = [self.COLORS["primary"], self.COLORS["secondary"], 
                  self.COLORS["neutral"], self.COLORS["dark"]]
        
        for i, (name, data) in enumerate(expense_data.items()):
            series_list.append({
                "name": name,
                "type": "line",
                "smooth": True,
                "itemStyle": {"color": colors[i % len(colors)]},
                "lineStyle": {"width": 2},
                "symbol": "circle",
                "symbolSize": 6,
                "data": data
            })
        
        return {
            "title": {
                "text": "图 8：公司单季度期间费用率",
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "line"}
            },
            "legend": {
                "data": list(expense_data.keys()),
                "bottom": "10%"
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "15%",
                "containLabel": True
            },
            "xAxis": [
                {
                    "type": "category",
                    "data": quarters,
                    "axisTick": {"alignWithLabel": True}
                }
            ],
            "yAxis": [
                {
                    "type": "value",
                    "name": "费用率 (%)",
                    "axisLabel": {"formatter": "{value}%"}
                }
            ],
            "series": series_list
        }
    
    def generate_all_charts(self, financial_data: Dict) -> Dict[str, Dict]:
        """
        生成全部 8 个图表
        """
        charts = {}
        
        charts["chart1_revenue_annual"] = self.generate_revenue_annual_chart(
            financial_data.get("years", []),
            financial_data.get("annual_revenue", []),
            financial_data.get("annual_revenue_growth", [])
        )
        
        charts["chart2_revenue_quarterly"] = self.generate_revenue_quarterly_chart(
            financial_data.get("quarters", []),
            financial_data.get("quarterly_revenue", []),
            financial_data.get("quarterly_revenue_growth", [])
        )
        
        charts["chart3_profit_annual"] = self.generate_profit_annual_chart(
            financial_data.get("years", []),
            financial_data.get("annual_profit", []),
            financial_data.get("annual_profit_growth", [])
        )
        
        charts["chart4_profit_quarterly"] = self.generate_profit_quarterly_chart(
            financial_data.get("quarters", []),
            financial_data.get("quarterly_profit", []),
            financial_data.get("quarterly_profit_growth", [])
        )
        
        charts["chart5_margin_annual"] = self.generate_margin_annual_chart(
            financial_data.get("years", []),
            financial_data.get("annual_gross_margin", []),
            financial_data.get("annual_net_margin", [])
        )
        
        charts["chart6_margin_quarterly"] = self.generate_margin_quarterly_chart(
            financial_data.get("quarters", []),
            financial_data.get("quarterly_gross_margin", []),
            financial_data.get("quarterly_net_margin", [])
        )
        
        charts["chart7_expense_annual"] = self.generate_expense_ratio_annual_chart(
            financial_data.get("years", []),
            financial_data.get("annual_expense_ratio", {})
        )
        
        charts["chart8_expense_quarterly"] = self.generate_expense_ratio_quarterly_chart(
            financial_data.get("quarters", []),
            financial_data.get("quarterly_expense_ratio", {})
        )
        
        return charts


def generate_charts_from_data(financial_data: Dict) -> str:
    """从财务数据生成 echarts 配置 JSON 字符串"""
    generator = EchartsGenerator()
    charts = generator.generate_all_charts(financial_data)
    return json.dumps(charts, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    sample_data = {
        "years": ["2021", "2022", "2023", "2024", "2025"],
        "quarters": ["24Q1", "24Q2", "24Q3", "24Q4", "25Q1"],
        "annual_revenue": [100, 120, 140, 160, 180],
        "annual_revenue_growth": [10, 20, 16.7, 14.3, 12.5],
        "quarterly_revenue": [38, 42, 45, 50, 43],
        "quarterly_revenue_growth": [15, 18, 12, 10, 13],
        "annual_profit": [20, 25, 30, 35, 40],
        "annual_profit_growth": [15, 25, 20, 16.7, 14.3],
        "quarterly_profit": [8, 9, 10, 11, 9],
        "quarterly_profit_growth": [18, 20, 15, 12, 14],
        "annual_gross_margin": [45, 46, 47, 48, 49],
        "annual_net_margin": [20, 21, 22, 23, 24],
        "quarterly_gross_margin": [47, 48, 48, 49, 49],
        "quarterly_net_margin": [22, 23, 23, 24, 24],
        "annual_expense_ratio": {
            "销售费用率": [10, 9.5, 9, 8.5, 8],
            "管理费用率": [5, 4.8, 4.5, 4.3, 4],
            "研发费用率": [3, 3.2, 3.5, 3.8, 4],
            "财务费用率": [0.5, 0.4, 0.3, 0.2, 0.1]
        },
        "quarterly_expense_ratio": {
            "销售费用率": [8.5, 8.2, 8, 7.8, 7.5],
            "管理费用率": [4.2, 4, 3.9, 3.8, 3.7],
            "研发费用率": [3.9, 4, 4.1, 4.2, 4.3],
            "财务费用率": [0.2, 0.15, 0.1, 0.1, 0.05]
        }
    }
    
    charts = generate_charts_from_data(sample_data)
    print(charts)
