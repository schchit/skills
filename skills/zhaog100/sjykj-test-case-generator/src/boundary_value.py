# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import re


@dataclass
class BoundaryPoint:
    """边界值点"""
    value: Any
    description: str
    is_valid: bool = True


@dataclass
class BoundaryAnalysis:
    """边界值分析结果"""
    method: str
    param: str
    param_type: str
    range_info: str = ""
    boundary_points: List[BoundaryPoint] = field(default_factory=list)


class BoundaryValueAnalyzer:
    """边界值分析"""

    def analyze(self, method: str, param_name: str, param_type: str,
                docstring: str = "", **kwargs) -> BoundaryAnalysis:
        """对单个参数进行边界值分析"""
        base_type = self._normalize_type(param_type)
        points = []

        if base_type in ('int', 'float'):
            points = self._numeric_boundaries(base_type, docstring)
        elif base_type == 'str':
            points = self._string_boundaries(docstring)
        elif base_type == 'list':
            points = self._collection_boundaries('列表')
        elif base_type == 'dict':
            points = self._collection_boundaries('字典')
        else:
            points = self._generic_boundaries(base_type)

        return BoundaryAnalysis(
            method=method,
            param=param_name,
            param_type=param_type,
            range_info=self._extract_range(docstring),
            boundary_points=points,
        )

    def analyze_function(self, method: str, params: List[Dict[str, Any]],
                         docstring: str = "") -> List[BoundaryAnalysis]:
        """对函数所有参数进行边界值分析"""
        results = []
        for p in params:
            ba = self.analyze(
                method=method,
                param_name=p.get('name', ''),
                param_type=p.get('type_hint', '') or '',
                docstring=docstring,
            )
            results.append(ba)
        return results

    def _numeric_boundaries(self, base_type: str, docstring: str) -> List[BoundaryPoint]:
        """数值类型边界值"""
        points = []
        # Extract explicit ranges from docstring
        ranges = self._extract_explicit_ranges(docstring)

        if ranges:
            for low, high, desc in ranges:
                step = 1 if base_type == 'int' else 0.1
                points.extend([
                    BoundaryPoint(low - step, f"{desc}下界-1 (越界)", False),
                    BoundaryPoint(low, f"{desc}下界 (临界)", True),
                    BoundaryPoint(low + step, f"{desc}下界+1 (正常)", True),
                    BoundaryPoint(high - step, f"{desc}上界-1 (正常)", True),
                    BoundaryPoint(high, f"{desc}上界 (临界)", True),
                    BoundaryPoint(high + step, f"{desc}上界+1 (越界)", False),
                ])
        else:
            # Generic numeric boundaries
            if base_type == 'int':
                points = [
                    BoundaryPoint(0, "零", True),
                    BoundaryPoint(1, "最小正整数", True),
                    BoundaryPoint(-1, "负一", True),
                    BoundaryPoint(2**31 - 1, "最大32位整数", True),
                    BoundaryPoint(-(2**31), "最小32位整数", True),
                ]
            else:
                points = [
                    BoundaryPoint(0.0, "零", True),
                    BoundaryPoint(1e-10, "极小正数", True),
                    BoundaryPoint(-1e-10, "极小负数", True),
                    BoundaryPoint(float('inf'), "正无穷", False),
                    BoundaryPoint(float('-inf'), "负无穷", False),
                ]
        return points

    def _string_boundaries(self, docstring: str) -> List[BoundaryPoint]:
        """字符串边界值"""
        points = [
            BoundaryPoint("", "空字符串", True),
            BoundaryPoint("a", "单字符", True),
            BoundaryPoint("a" * 10000, "超长字符串", True),
            BoundaryPoint(None, "None", False),
            BoundaryPoint(" ", "空白字符", True),
            BoundaryPoint("中文测试", "中文字符串", True),
        ]
        return points

    def _collection_boundaries(self, name: str) -> List[BoundaryPoint]:
        """集合类型边界值"""
        if name == '列表':
            return [
                BoundaryPoint([], "空列表", True),
                BoundaryPoint([1], "单元素列表", True),
                BoundaryPoint(None, "None代替列表", False),
            ]
        return [
            BoundaryPoint({}, "空字典", True),
            BoundaryPoint({"a": 1}, "单元素字典", True),
            BoundaryPoint(None, "None代替字典", False),
        ]

    def _generic_boundaries(self, base_type: str) -> List[BoundaryPoint]:
        """通用边界值"""
        return [
            BoundaryPoint(None, "None", False),
        ]

    def _normalize_type(self, type_hint: str) -> str:
        if not type_hint:
            return 'str'
        import re
        m = re.match(r'Optional\[(.+)\]', type_hint)
        if m:
            return m.group(1).strip().split('.')[-1]
        return type_hint.strip().split('.')[-1]

    def _extract_range(self, docstring: str) -> str:
        import re
        ranges = re.findall(r'(\d+(?:\.\d+)?)\s*[-~到]\s*(\d+(?:\.\d+)?)', docstring)
        return ', '.join(f"[{a}, {b}]" for a, b in ranges)

    def _extract_explicit_ranges(self, docstring: str) -> List[tuple]:
        """从docstring提取显式范围 [low, high]"""
        import re
        ranges = []
        # Pattern: >= X or <= X or X to Y
        lower = None
        upper = None
        for m in re.finditer(r'([><=!]+)\s*(\d+(?:\.\d+)?)', docstring):
            op, val = m.group(1), float(m.group(2))
            if '>' in op:
                lower = val + (0 if '>=' in op else 1)
            elif '<' in op:
                upper = val - (0 if '<=' in op else 1)
        if lower is not None and upper is not None:
            ranges.append((lower, upper, "文档范围"))
        return ranges
