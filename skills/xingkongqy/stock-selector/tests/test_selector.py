#!/usr/bin/env python3
"""
stock-selector 测试用例
"""

import unittest
import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_selector import (
    stage1_filter_change_pct,
    stage2_filter_amount,
    stage3_filter_turnover,
    stage4_filter_exclusions
)


class TestStockSelector(unittest.TestCase):
    """选股工具测试"""
    
    def setUp(self):
        """准备测试数据"""
        self.test_quotes = [
            {
                'code': '000001',
                'name': '平安银行',
                'price': 10.0,
                'change_pct': 5.0,
                'amount': 200000000,
                'turnover_rate': 8.0,
                'market_cap': 10000000000,
                'high': 10.5,
                'low': 9.8,
            },
            {
                'code': '000002',
                'name': '万科 A',
                'price': 20.0,
                'change_pct': 2.0,  # 不符合涨跌幅
                'amount': 300000000,
                'turnover_rate': 5.0,
                'market_cap': 20000000000,
                'high': 20.5,
                'low': 19.8,
            },
            {
                'code': '000003',
                'name': '*ST 生态',  # ST 股票
                'price': 5.0,
                'change_pct': 4.0,
                'amount': 100000000,
                'turnover_rate': 6.0,
                'market_cap': 5000000000,
                'high': 5.2,
                'low': 4.9,
            },
        ]
    
    def test_stage1_filter_change_pct(self):
        """测试第 1 阶段：涨跌幅筛选"""
        results = stage1_filter_change_pct(self.test_quotes, min_pct=3, max_pct=7)
        self.assertEqual(len(results), 2)  # 000001 和 000003 符合
        self.assertNotIn('000002', [r['code'] for r in results])
    
    def test_stage2_filter_amount(self):
        """测试第 2 阶段：成交额筛选"""
        results = stage2_filter_amount(self.test_quotes, min_amount=1)
        self.assertEqual(len(results), 3)  # 都符合>1 亿
    
    def test_stage3_filter_turnover(self):
        """测试第 3 阶段：换手率筛选"""
        results = stage3_filter_turnover(self.test_quotes, min_rate=3, max_rate=15)
        self.assertEqual(len(results), 3)  # 都符合 3-15%
    
    def test_stage4_filter_exclusions(self):
        """测试第 4 阶段：排除 ST"""
        results = stage4_filter_exclusions(self.test_quotes)
        self.assertEqual(len(results), 2)  # 排除*ST 生态
        self.assertNotIn('*ST 生态', [r['name'] for r in results])


if __name__ == '__main__':
    unittest.main()
