# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json
import os


@dataclass
class ErrorScenario:
    """错误推测场景"""
    param: str
    error_type: str
    description: str
    test_value: str = ""


@dataclass
class ErrorGuessingResult:
    """错误推测分析结果"""
    method: str
    error_scenarios: List[ErrorScenario] = field(default_factory=list)


class ErrorGuessingAnalyzer:
    """错误推测法 - 基于内置错误模式库"""

    def __init__(self, patterns_path: str = None):
        self.patterns_path = patterns_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'data', 'error_patterns.json'
        )
        self.patterns = self._load_patterns()

    def analyze(self, method: str, params: List[Dict[str, Any]] = None,
                docstring: str = "", **kwargs) -> ErrorGuessingResult:
        """对函数进行错误推测"""
        params = params or []
        scenarios = []

        for p in params:
            ptype = p.get('type_hint', '') or ''
            pname = p['name']
            scenarios.extend(self._guess_for_param(pname, ptype, docstring))

        # Global checks from docstring
        scenarios.extend(self._guess_from_docstring(method, docstring))

        return ErrorGuessingResult(method=method, error_scenarios=scenarios)

    def _guess_for_param(self, name: str, type_hint: str, docstring: str) -> List[ErrorScenario]:
        """对单个参数进行错误推测"""
        scenarios = []

        # Check built-in patterns
        for pattern in self.patterns:
            if self._match_pattern(pattern, name, type_hint, docstring):
                scenarios.append(ErrorScenario(
                    param=name,
                    error_type=pattern.get('error_type', '未知'),
                    description=pattern.get('description', ''),
                    test_value=pattern.get('test_value', ''),
                ))

        return scenarios

    def _guess_from_docstring(self, method: str, docstring: str) -> List[ErrorScenario]:
        """从docstring中的线索推测错误"""
        scenarios = []
        import re

        # raise ValueError → check zero/empty
        if re.search(r'raise\s+ValueError|ValueError', docstring):
            scenarios.append(ErrorScenario(
                param="*", error_type="ValueError",
                description="触发ValueError的输入",
                test_value="边界值或非法值",
            ))

        # Division → division by zero
        if '/' in docstring or '除' in docstring or 'divide' in docstring.lower():
            scenarios.append(ErrorScenario(
                param="*", error_type="ZeroDivisionError",
                description="除零错误",
                test_value="0",
            ))

        return scenarios

    def _match_pattern(self, pattern: Dict, name: str, type_hint: str, docstring: str) -> bool:
        """检查参数是否匹配错误模式"""
        # Match by type keyword
        type_keywords = pattern.get('type_keywords', [])
        if any(kw.lower() in type_hint.lower() for kw in type_keywords):
            return True

        # Match by name keyword
        name_keywords = pattern.get('name_keywords', [])
        if any(kw.lower() in name.lower() for kw in name_keywords):
            return True

        # Match by docstring keyword
        doc_keywords = pattern.get('doc_keywords', [])
        if any(kw.lower() in docstring.lower() for kw in doc_keywords):
            return True

        return False

    def _load_patterns(self) -> List[Dict]:
        """加载错误模式库"""
        if os.path.exists(self.patterns_path):
            with open(self.patterns_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._default_patterns()

    def _default_patterns(self) -> List[Dict]:
        """默认错误模式"""
        return [
            {
                "name_keywords": ["email", "邮箱"],
                "type_keywords": ["str"],
                "error_type": "FormatError",
                "description": "无效邮箱格式",
                "test_value": "'not-an-email'",
            },
            {
                "name_keywords": ["age", "年龄", "count", "数量", "n"],
                "type_keywords": ["int"],
                "error_type": "RangeError",
                "description": "负数或零作为非负参数",
                "test_value": "-1",
            },
            {
                "name_keywords": ["height", "weight", "身高", "体重"],
                "type_keywords": ["float", "int"],
                "error_type": "ValueError",
                "description": "非正数值",
                "test_value": "0",
            },
            {
                "type_keywords": ["Optional"],
                "error_type": "NoneError",
                "description": "None值传入非Optional参数",
                "test_value": "None",
            },
            {
                "name_keywords": ["path", "file", "文件", "路径"],
                "type_keywords": ["str"],
                "error_type": "FileNotFoundError",
                "description": "不存在的文件路径",
                "test_value": "'/nonexistent/path'",
            },
            {
                "doc_keywords": ["validate", "验证", "检查"],
                "error_type": "ValidationError",
                "description": "验证失败场景",
                "test_value": "非法输入",
            },
        ]
