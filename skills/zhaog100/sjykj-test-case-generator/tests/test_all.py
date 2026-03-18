# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.code_parser import CodeParser, FunctionInfo, ParamInfo
from src.requirement_analyzer import RequirementAnalyzer, _TestDataPoint as TestPoint
from src.equivalence_class import EquivalenceClassAnalyzer
from src.boundary_value import BoundaryValueAnalyzer
from src.scenario import ScenarioAnalyzer
from src.cause_effect import CauseEffectAnalyzer
from src.error_guessing import ErrorGuessingAnalyzer
from src.test_design_engine import TestDesignEngine as TDEngine
from src.test_generator import TestGenerator as TGen
from src.report_generator import ReportGenerator
from src.coverage_analyzer import CoverageAnalyzer

EXAMPLE_PATH = os.path.join(os.path.dirname(__file__), '..', 'examples', 'example_code.py')

# ============================================================
# CodeParser Tests (1-8)
# ============================================================

class TestCodeParser:
    def test_parse_file_returns_functions(self):
        """TC-01: 解析文件返回函数列表"""
        parser = CodeParser()
        funcs = parser.parse_file(EXAMPLE_PATH)
        assert len(funcs) >= 4
        names = [f.name for f in funcs]
        assert 'calculate_bmi' in names
        assert 'is_adult' in names

    def test_parse_file_function_params(self):
        """TC-02: 解析函数参数"""
        parser = CodeParser()
        funcs = parser.parse_file(EXAMPLE_PATH)
        bmi = next(f for f in funcs if f.name == 'calculate_bmi')
        assert len(bmi.params) == 2
        assert bmi.params[0].name == 'weight'
        assert bmi.params[0].type_hint == 'float'

    def test_parse_file_return_type(self):
        """TC-03: 解析返回类型"""
        parser = CodeParser()
        funcs = parser.parse_file(EXAMPLE_PATH)
        bmi = next(f for f in funcs if f.name == 'calculate_bmi')
        assert bmi.return_type == 'float'

    def test_parse_file_docstring(self):
        """TC-04: 解析docstring"""
        parser = CodeParser()
        funcs = parser.parse_file(EXAMPLE_PATH)
        bmi = next(f for f in funcs if f.name == 'calculate_bmi')
        assert 'BMI' in (bmi.docstring or '')

    def test_parse_default_param(self):
        """TC-05: 解析默认参数"""
        parser = CodeParser()
        funcs = parser.parse_file(EXAMPLE_PATH)
        adult = next(f for f in funcs if f.name == 'is_adult')
        assert adult.params[1].has_default is True
        assert adult.params[1].default == "'CN'"

    def test_parse_source(self):
        """TC-06: 获取函数源码"""
        parser = CodeParser()
        funcs = parser.parse_file(EXAMPLE_PATH)
        fib = next(f for f in funcs if f.name == 'fibonacci')
        assert 'fibonacci' in fib.source
        assert fib.start_line > 0

    def test_parse_source_string(self):
        """TC-07: 解析源码字符串"""
        parser = CodeParser()
        source = "def foo(x: int) -> int:\n    return x + 1\n"
        funcs = parser.parse_source(source)
        assert len(funcs) == 1
        assert funcs[0].name == 'foo'
        assert funcs[0].return_type == 'int'

    def test_parse_no_file_raises(self):
        """TC-08: 不存在的文件"""
        parser = CodeParser()
        try:
            parser.parse_file('/nonexistent/file.py')
            assert False, "Should raise"
        except FileNotFoundError:
            pass


# ============================================================
# RequirementAnalyzer Tests (9-15)
# ============================================================

class TestRequirementAnalyzer:
    def setup_method(self):
        self.analyzer = RequirementAnalyzer()

    def test_parse_heading_as_feature(self):
        """TC-09: ##标题识别为feature"""
        md = "## 登录功能\n一些内容"
        tps = self.analyzer.parse_text(md)
        assert len(tps) == 0  # no test points, just feature

    def test_parse_bold_input_output(self):
        """TC-10: 解析**输入**/**输出**模式"""
        md = "## 功能\n- **输入**: 用户名和密码\n- **输出**: 登录成功"
        tps = self.analyzer.parse_text(md)
        assert len(tps) == 2
        assert tps[0].input_conditions == "用户名和密码"

    def test_parse_numbered_list(self):
        """TC-11: 解析编号列表"""
        md = "## 功能\n1. 测试正常登录\n2. 测试密码错误"
        tps = self.analyzer.parse_text(md)
        assert len(tps) == 2

    def test_parse_priority(self):
        """TC-12: 解析优先级"""
        md = "## 功能\n- **优先级**: P1\n- **输入**: 测试数据"
        tps = self.analyzer.parse_text(md)
        assert any(tp.priority == "P1" for tp in tps)

    def test_parse_exception_pattern(self):
        """TC-13: 解析异常模式"""
        md = "## 功能\n- **异常**: 密码为空"
        tps = self.analyzer.parse_text(md)
        assert len(tps) >= 1

    def test_parse_empty_text(self):
        """TC-14: 空文本"""
        tps = self.analyzer.parse_text("")
        assert len(tps) == 0

    def test_parse_file(self):
        """TC-15: 解析文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write("## 功能\n- **输入**: 数据\n- **输出**: 结果\n")
            path = f.name
        try:
            tps = self.analyzer.parse_file(path)
            assert len(tps) == 2
        finally:
            os.unlink(path)


# ============================================================
# EquivalenceClassAnalyzer Tests (16-22)
# ============================================================

class TestEquivalenceClass:
    def setup_method(self):
        self.analyzer = EquivalenceClassAnalyzer()

    def test_int_type_classes(self):
        """TC-16: int类型等价类"""
        ec = self.analyzer.analyze("foo", "age", "int")
        assert '正整数' in ec.valid_classes
        assert '字符串' in ec.invalid_classes

    def test_str_type_classes(self):
        """TC-17: str类型等价类"""
        ec = self.analyzer.analyze("foo", "name", "str")
        assert '有效字符串' in ec.valid_classes

    def test_optional_type(self):
        """TC-18: Optional类型包含None在有效类"""
        ec = self.analyzer.analyze("foo", "x", "Optional[int]")
        assert 'None' in ec.valid_classes

    def test_union_type(self):
        """TC-19: Union类型移除None无效类"""
        ec = self.analyzer.analyze("foo", "x", "Union[str, int]")
        assert 'None' not in ec.invalid_classes

    def test_float_type(self):
        """TC-20: float类型等价类"""
        ec = self.analyzer.analyze("foo", "weight", "float")
        assert '正数' in ec.valid_classes

    def test_analyze_function(self):
        """TC-21: 分析函数多个参数"""
        params = [{'name': 'x', 'type_hint': 'int'}, {'name': 'y', 'type_hint': 'str'}]
        results = self.analyzer.analyze_function("foo", params)
        assert len(results) == 2

    def test_docstring_positive_hint(self):
        """TC-22: docstring中正数提示"""
        ec = self.analyzer.analyze("foo", "height", "float", "height must be positive")
        assert '零或负数' in ec.invalid_classes


# ============================================================
# BoundaryValueAnalyzer Tests (23-30)
# ============================================================

class TestBoundaryValue:
    def setup_method(self):
        self.analyzer = BoundaryValueAnalyzer()

    def test_int_boundaries(self):
        """TC-23: int类型边界值"""
        ba = self.analyzer.analyze("foo", "n", "int")
        values = [bp.value for bp in ba.boundary_points]
        assert 0 in values
        assert 1 in values

    def test_float_boundaries(self):
        """TC-24: float类型边界值"""
        ba = self.analyzer.analyze("foo", "weight", "float")
        assert len(ba.boundary_points) > 0

    def test_str_boundaries(self):
        """TC-25: str类型边界值"""
        ba = self.analyzer.analyze("foo", "name", "str")
        values = [bp.value for bp in ba.boundary_points]
        assert "" in values

    def test_list_boundaries(self):
        """TC-26: list类型边界值"""
        ba = self.analyzer.analyze("foo", "items", "list")
        values = [bp.value for bp in ba.boundary_points]
        assert [] in values

    def test_boundary_validity(self):
        """TC-27: 边界值有效性标记"""
        ba = self.analyzer.analyze("foo", "n", "int")
        for bp in ba.boundary_points:
            assert isinstance(bp.is_valid, bool)

    def test_explicit_range(self):
        """TC-28: 从docstring提取显式范围"""
        ba = self.analyzer.analyze("foo", "x", "int", "x >= 18")
        assert len(ba.boundary_points) > 0

    def test_dict_boundaries(self):
        """TC-29: dict类型边界值"""
        ba = self.analyzer.analyze("foo", "config", "dict")
        values = [bp.value for bp in ba.boundary_points]
        assert {} in values

    def test_analyze_function(self):
        """TC-30: 分析函数多个参数"""
        params = [{'name': 'a', 'type_hint': 'int'}, {'name': 'b', 'type_hint': 'str'}]
        results = self.analyzer.analyze_function("foo", params)
        assert len(results) == 2


# ============================================================
# ScenarioAnalyzer Tests (31-36)
# ============================================================

class TestScenario:
    def setup_method(self):
        self.analyzer = ScenarioAnalyzer()

    def test_basic_exception_from_docstring(self):
        """TC-31: docstring含raise生成异常流"""
        result = self.analyzer.analyze("foo", "如果x<=0抛出ValueError")
        types = [s.type for s in result.scenarios]
        assert 'exception' in types

    def test_basic_flow_added(self):
        """TC-32: 有异常流时自动添加基本流"""
        result = self.analyzer.analyze("foo", "如果x<=0抛出ValueError")
        types = [s.type for s in result.scenarios]
        assert 'basic' in types

    def test_condition_extraction(self):
        """TC-33: 条件提取"""
        result = self.analyzer.analyze("foo", "如果age>=18则返回True，如果age<18则返回False")
        assert len(result.scenarios) >= 2

    def test_generic_when_no_docstring(self):
        """TC-34: 无docstring生成通用场景"""
        result = self.analyzer.analyze("foo", "")
        assert len(result.scenarios) >= 1

    def test_params_generate_exception(self):
        """TC-35: 必选参数生成异常场景"""
        params = [{'name': 'x', 'type_hint': 'int', 'has_default': False}]
        result = self.analyzer.analyze("foo", "", params)
        assert any('x' in s.name for s in result.scenarios)

    def test_method_name(self):
        """TC-36: 方法名正确"""
        result = self.analyzer.analyze("calculate_bmi", "test doc")
        assert result.method == "calculate_bmi"


# ============================================================
# CauseEffectAnalyzer Tests (37-43)
# ============================================================

class TestCauseEffect:
    def setup_method(self):
        self.analyzer = CauseEffectAnalyzer()

    def test_causes_from_params(self):
        """TC-37: 从参数生成因"""
        params = [{'name': 'x', 'type_hint': 'int'}, {'name': 'y', 'type_hint': 'str'}]
        result = self.analyzer.analyze("foo", params)
        assert len(result.causes) == 2

    def test_cause_states_int(self):
        """TC-38: int参数的状态"""
        params = [{'name': 'n', 'type_hint': 'int'}]
        result = self.analyzer.analyze("foo", params)
        assert len(result.causes[0].states) >= 3

    def test_decision_table_generated(self):
        """TC-39: 判定表生成"""
        params = [{'name': 'x', 'type_hint': 'int'}]
        result = self.analyzer.analyze("foo", params)
        assert len(result.decision_table) > 0

    def test_optimized_smaller(self):
        """TC-40: 优化后规则数<=原始"""
        params = [{'name': 'x', 'type_hint': 'int'}, {'name': 'y', 'type_hint': 'int'}]
        result = self.analyzer.analyze("foo", params)
        assert len(result.optimized_rules) <= len(result.decision_table)

    def test_default_param_state(self):
        """TC-41: 有默认值的参数有默认状态"""
        params = [{'name': 'x', 'type_hint': 'int', 'has_default': True}]
        result = self.analyzer.analyze("foo", params)
        assert '默认值' in result.causes[0].states

    def test_effects_from_docstring(self):
        """TC-42: 从docstring提取果"""
        params = [{'name': 'x', 'type_hint': 'int'}]
        result = self.analyzer.analyze("foo", params, "返回True，返回False")
        assert len(result.effects) >= 1

    def test_no_params(self):
        """TC-43: 无参数"""
        result = self.analyzer.analyze("foo", [])
        assert len(result.causes) == 0


# ============================================================
# ErrorGuessingAnalyzer Tests (44-51)
# ============================================================

class TestErrorGuessing:
    def setup_method(self):
        self.analyzer = ErrorGuessingAnalyzer()

    def test_email_param(self):
        """TC-44: email参数触发格式错误"""
        params = [{'name': 'email', 'type_hint': 'str'}]
        result = self.analyzer.analyze("foo", params, "验证邮箱格式")
        types = [e.error_type for e in result.error_scenarios]
        assert 'FormatError' in types

    def test_age_param(self):
        """TC-45: age参数触发范围错误"""
        params = [{'name': 'age', 'type_hint': 'int'}]
        result = self.analyzer.analyze("foo", params)
        types = [e.error_type for e in result.error_scenarios]
        assert 'RangeError' in types

    def test_value_error_from_docstring(self):
        """TC-46: docstring含ValueError"""
        params = [{'name': 'x', 'type_hint': 'int'}]
        result = self.analyzer.analyze("foo", params, "raise ValueError if x<=0")
        types = [e.error_type for e in result.error_scenarios]
        assert 'ValueError' in types

    def test_division_by_zero(self):
        """TC-47: 除法触发除零"""
        params = [{'name': 'x', 'type_hint': 'int'}]
        result = self.analyzer.analyze("foo", params, "x / y")
        types = [e.error_type for e in result.error_scenarios]
        assert 'ZeroDivisionError' in types

    def test_custom_patterns_file(self):
        """TC-48: 自定义模式文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump([{"name_keywords": ["custom"], "type_keywords": ["str"],
                        "error_type": "CustomError", "description": "自定义错误", "test_value": "x"}], f)
            path = f.name
        analyzer = ErrorGuessingAnalyzer(patterns_path=path)
        result = analyzer.analyze("foo", [{'name': 'custom_field', 'type_hint': 'str'}])
        os.unlink(path)
        assert any(e.error_type == "CustomError" for e in result.error_scenarios)

    def test_optional_type(self):
        """TC-49: Optional类型触发NoneError"""
        params = [{'name': 'x', 'type_hint': 'Optional[str]'}]
        result = self.analyzer.analyze("foo", params)
        types = [e.error_type for e in result.error_scenarios]
        assert 'NoneError' in types

    def test_validate_keyword(self):
        """TC-50: validate关键词触发ValidationError"""
        params = [{'name': 'x', 'type_hint': 'str'}]
        result = self.analyzer.analyze("foo", params, "validate input")
        types = [e.error_type for e in result.error_scenarios]
        assert 'ValidationError' in types

    def test_no_params(self):
        """TC-51: 无参数无错误推测"""
        result = self.analyzer.analyze("foo", [], "")
        assert len(result.error_scenarios) == 0


# ============================================================
# TestDesignEngine Tests (52-58)
# ============================================================

class TestDesignEngine:
    def setup_method(self):
        self.engine = TDEngine()

    def test_auto_select_basic(self):
        """TC-52: 基本选择等价类和边界值"""
        from src.code_parser import FunctionInfo
        func = FunctionInfo(name="foo", params=[])
        methods = self.engine.auto_select_methods(func)
        assert 'equivalence_class' in methods
        assert 'boundary_value' in methods

    def test_auto_select_conditions(self):
        """TC-53: 有条件逻辑选择场景法和因果图"""
        from src.code_parser import FunctionInfo
        func = FunctionInfo(name="foo", params=[],
                            docstring="如果x>0返回True，否则返回False",
                            source="if x > 0: return True")
        methods = self.engine.auto_select_methods(func)
        assert 'scenario' in methods

    def test_auto_select_error(self):
        """TC-54: 有错误处理选择错误推测"""
        from src.code_parser import FunctionInfo
        func = FunctionInfo(name="foo", params=[],
                            docstring="raise ValueError")
        methods = self.engine.auto_select_methods(func)
        assert 'error_guessing' in methods

    def test_analyze_returns_result(self):
        """TC-55: analyze返回AnalysisResult"""
        from src.code_parser import FunctionInfo
        func = FunctionInfo(name="foo", params=[
            ParamInfo(name='x', type_hint='int')
        ])
        result = self.engine.analyze(func)
        assert result.function.name == "foo"
        assert len(result.equivalence_classes) > 0

    def test_analyze_file(self):
        """TC-56: 分析整个文件"""
        results = self.engine.analyze_file(EXAMPLE_PATH)
        assert len(results) >= 4

    def test_analyze_with_explicit_methods(self):
        """TC-57: 指定方法列表"""
        from src.code_parser import FunctionInfo
        func = FunctionInfo(name="foo", params=[ParamInfo(name='x', type_hint='int')])
        result = self.engine.analyze(func, methods=['equivalence_class'])
        assert len(result.equivalence_classes) > 0
        assert result.scenarios is None

    def test_analyze_all_methods(self):
        """TC-58: 有条件+错误的函数选择所有方法"""
        from src.code_parser import FunctionInfo
        func = FunctionInfo(name="foo", params=[
            ParamInfo(name='x', type_hint='int'),
            ParamInfo(name='y', type_hint='int'),
            ParamInfo(name='z', type_hint='int'),
        ], docstring="如果x<=0 raise ValueError",
           source="if x <= 0: raise ValueError")
        methods = self.engine.auto_select_methods(func)
        assert 'error_guessing' in methods


# ============================================================
# TestGenerator Tests (59-64)
# ============================================================

class TestTestGenerator:
    def setup_method(self):
        self.gen = TGen()

    def test_generate_pytest(self):
        """TC-59: 生成pytest代码"""
        code = self.gen.generate_pytest(EXAMPLE_PATH)
        assert 'import pytest' in code
        assert 'def test_' in code

    def test_generate_markdown(self):
        """TC-60: 生成Markdown文档"""
        md = self.gen.generate_markdown(EXAMPLE_PATH)
        assert '# 测试用例文档' in md
        assert '|' in md

    def test_generate_from_source(self):
        """TC-61: 从源码字符串生成"""
        source = "def foo(x: int) -> int:\n    if x <= 0: raise ValueError\n    return x\n"
        code = self.gen.generate_from_source(source)
        assert 'def test_' in code

    def test_pytest_contains_docstrings(self):
        """TC-62: pytest用例包含docstring"""
        code = self.gen.generate_pytest(EXAMPLE_PATH)
        assert 'TC-' in code

    def test_markdown_has_table(self):
        """TC-63: Markdown包含表格"""
        md = self.gen.generate_markdown(EXAMPLE_PATH)
        assert '用例编号' in md

    def test_generate_to_file(self):
        """TC-64: 输出到文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            path = f.name
        try:
            self.gen.generate_pytest(EXAMPLE_PATH, path)
            with open(path, 'r', encoding='utf-8') as f:
                assert 'import pytest' in f.read()
        finally:
            os.unlink(path)


# ============================================================
# ReportGenerator Tests (65-68)
# ============================================================

class TestReportGenerator:
    def setup_method(self):
        self.gen = ReportGenerator()
        self.engine = TDEngine()  # type: ignore

    def test_generate_report(self):
        """TC-65: 生成ASCII报告"""
        results = self.engine.analyze_file(EXAMPLE_PATH)
        report = self.gen.generate_report(results)
        assert '测试设计分析报告' in report
        assert 'calculate_bmi' in report

    def test_generate_coverage_summary(self):
        """TC-66: 生成覆盖率统计"""
        results = self.engine.analyze_file(EXAMPLE_PATH)
        summary = self.gen.generate_coverage_summary(results)
        assert '覆盖率统计' in summary

    def test_report_contains_box_drawing(self):
        """TC-67: 报告包含ASCII边框"""
        results = self.engine.analyze_file(EXAMPLE_PATH)
        report = self.gen.generate_report(results)
        assert '┌' in report
        assert '└' in report

    def test_report_total_count(self):
        """TC-68: 报告包含总数统计"""
        results = self.engine.analyze_file(EXAMPLE_PATH)
        report = self.gen.generate_report(results)
        assert '总计' in report


# ============================================================
# CoverageAnalyzer Tests (69-71)
# ============================================================

class TestCoverageAnalyzer:
    def test_evaluate_pass(self):
        """TC-69: 覆盖率达标"""
        analyzer = CoverageAnalyzer(line_threshold=80.0)
        result = analyzer.evaluate(90.0, 80.0, 85.0)
        assert result.status == "PASS"

    def test_evaluate_warn(self):
        """TC-70: 覆盖率偏低"""
        analyzer = CoverageAnalyzer(line_threshold=80.0)
        result = analyzer.evaluate(65.0, 50.0, 60.0)
        assert result.status == "WARN"

    def test_format_report(self):
        """TC-71: 格式化覆盖率报告"""
        from src.coverage_analyzer import CoverageResult
        result = CoverageResult(line_coverage=85.0, status="PASS", message="OK")
        report = CoverageAnalyzer.format_report(result)
        assert '✅' in report
