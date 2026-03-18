# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from src.code_parser import CodeParser, FunctionInfo
from src.equivalence_class import EquivalenceClassAnalyzer
from src.boundary_value import BoundaryValueAnalyzer
from src.scenario import ScenarioAnalyzer
from src.cause_effect import CauseEffectAnalyzer
from src.error_guessing import ErrorGuessingAnalyzer
import os


@dataclass
class AnalysisResult:
    """综合分析结果"""
    function: FunctionInfo
    equivalence_classes: List[Any] = field(default_factory=list)
    boundary_values: List[Any] = field(default_factory=list)
    scenarios: Any = None
    cause_effect: Any = None
    error_guessing: Any = None
    selected_methods: List[str] = field(default_factory=list)


class TestDesignEngine:
    """核心调度引擎"""

    def __init__(self):
        self.code_parser = CodeParser()
        self.eq_analyzer = EquivalenceClassAnalyzer()
        self.bv_analyzer = BoundaryValueAnalyzer()
        self.scenario_analyzer = ScenarioAnalyzer()
        self.ce_analyzer = CauseEffectAnalyzer()
        self.eg_analyzer = ErrorGuessingAnalyzer()

    def auto_select_methods(self, func: FunctionInfo) -> List[str]:
        """根据函数特征选择测试方法"""
        methods = []
        params = [{'name': p.name, 'type_hint': p.type_hint, 'has_default': p.has_default}
                  for p in func.params]
        docstring = func.docstring or ""

        # Always use equivalence class and boundary value
        methods.append('equivalence_class')
        methods.append('boundary_value')

        # Has conditional logic → scenario + cause-effect
        if self._has_conditions(docstring, func.source):
            methods.append('scenario')
            methods.append('cause_effect')

        # Has error handling → error guessing
        if self._has_error_handling(docstring):
            methods.append('error_guessing')

        # Many params → cause effect
        if len(func.params) >= 3:
            if 'cause_effect' not in methods:
                methods.append('cause_effect')

        return methods

    def analyze(self, func: FunctionInfo, methods: List[str] = None) -> AnalysisResult:
        """调度各分析器并合并结果"""
        params = [{'name': p.name, 'type_hint': p.type_hint, 'has_default': p.has_default}
                  for p in func.params]
        docstring = func.docstring or ""

        if methods is None:
            methods = self.auto_select_methods(func)

        result = AnalysisResult(function=func, selected_methods=methods)

        for method in methods:
            if method == 'equivalence_class':
                result.equivalence_classes = self.eq_analyzer.analyze_function(
                    func.name, params, docstring)
            elif method == 'boundary_value':
                result.boundary_values = self.bv_analyzer.analyze_function(
                    func.name, params, docstring)
            elif method == 'scenario':
                result.scenarios = self.scenario_analyzer.analyze(
                    func.name, docstring, params)
            elif method == 'cause_effect':
                result.cause_effect = self.ce_analyzer.analyze(
                    func.name, params, docstring)
            elif method == 'error_guessing':
                result.error_guessing = self.eg_analyzer.analyze(
                    func.name, params, docstring)

        return result

    def analyze_file(self, filepath: str) -> List[AnalysisResult]:
        """分析整个文件的所有函数"""
        functions = self.code_parser.parse_file(filepath)
        return [self.analyze(f) for f in functions]

    def _has_conditions(self, docstring: str, source: str) -> bool:
        import re
        keywords = ['如果', '否则', '如果.*则', 'if', 'else', 'elif',
                    r'raise', 'return.*if']
        return any(re.search(k, docstring or source, re.IGNORECASE) for k in keywords)

    def _has_error_handling(self, docstring: str) -> bool:
        import re
        return bool(re.search(r'raise|异常|error|ValueError|TypeError', docstring, re.IGNORECASE))
