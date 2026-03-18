# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

from typing import List, Optional
from src.test_design_engine import TestDesignEngine, AnalysisResult


class TestGenerator:
    """生成pytest和Markdown格式测试用例"""

    def __init__(self):
        self.engine = TestDesignEngine()

    def generate_pytest(self, filepath: str, output_path: str = None) -> str:
        """从源文件生成pytest测试代码"""
        results = self.engine.analyze_file(filepath)
        code = self._build_pytest(results, filepath)
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(code)
        return code

    def generate_markdown(self, filepath: str, output_path: str = None) -> str:
        """从源文件生成Markdown测试用例文档"""
        results = self.engine.analyze_file(filepath)
        md = self._build_markdown(results, filepath)
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md)
        return md

    def generate_from_source(self, source: str, module_name: str = "example") -> str:
        """从源码字符串生成pytest"""
        from .code_parser import CodeParser
        parser = CodeParser()
        functions = parser.parse_source(source)
        results = [self.engine.analyze(f) for f in functions]
        return self._build_pytest(results, module_name)

    def _build_pytest(self, results: List[AnalysisResult], source_ref: str) -> str:
        """构建pytest代码"""
        lines = [
            '# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)',
            '# Auto-generated test cases',
            'import pytest',
            '',
        ]

        case_id = 0
        for result in results:
            func = result.function
            lines.append(f'# === {func.name} ===')
            lines.append(f'# Methods: {", ".join(result.selected_methods)}')

            # Generate cases from equivalence classes
            for ec in result.equivalence_classes:
                for vc in ec.valid_classes:
                    case_id += 1
                    lines.append(f'def test_{func.name}_{ec.param}_valid_{case_id}():')
                    lines.append(f'    """TC-{case_id:03d}: {func.name} {ec.param} 等价类-有效: {vc}"""')
                    lines.append(f'    # TODO: implement')
                    lines.append(f'    pass')
                    lines.append('')

            for ec in result.equivalence_classes:
                for ic in ec.invalid_classes:
                    case_id += 1
                    lines.append(f'def test_{func.name}_{ec.param}_invalid_{case_id}():')
                    lines.append(f'    """TC-{case_id:03d}: {func.name} {ec.param} 等价类-无效: {ic}"""')
                    lines.append(f'    # TODO: implement')
                    lines.append(f'    pass')
                    lines.append('')

            # Generate from boundary values
            for bv in result.boundary_values:
                for bp in bv.boundary_points:
                    case_id += 1
                    status = "有效" if bp.is_valid else "无效"
                    safe_desc = bp.description.replace(' ', '_').replace('-', '_')
                    lines.append(f'def test_{func.name}_{bv.param}_boundary_{case_id}():')
                    lines.append(f'    """TC-{case_id:03d}: {func.name} {bv.param} 边界值-{status}: {bp.description}"""')
                    lines.append(f'    # TODO: implement')
                    lines.append(f'    pass')
                    lines.append('')

            # Generate from scenarios
            if result.scenarios:
                for sc in result.scenarios.scenarios:
                    case_id += 1
                    safe_name = sc.name.replace(' ', '_').replace(':', '')[:30]
                    lines.append(f'def test_{func.name}_scenario_{case_id}():')
                    lines.append(f'    """TC-{case_id:03d}: {func.name} 场景-{sc.type}: {sc.name}"""')
                    lines.append(f'    # Conditions: {", ".join(sc.conditions)}')
                    lines.append(f'    # TODO: implement')
                    lines.append(f'    pass')
                    lines.append('')

            lines.append('')

        return '\n'.join(lines)

    def _build_markdown(self, results: List[AnalysisResult], source_ref: str) -> str:
        """构建Markdown测试用例文档"""
        lines = [
            '# 测试用例文档',
            f'\n> 自动生成，源文件: `{source_ref}`\n',
        ]

        case_id = 0
        for result in results:
            func = result.function
            lines.append(f'## {func.name}')
            lines.append(f'- 返回类型: {func.return_type or "Unknown"}')
            lines.append(f'- 使用方法: {", ".join(result.selected_methods)}')
            lines.append('')
            lines.append('| 用例编号 | 类型 | 参数 | 测试点 | 预期结果 | 优先级 |')
            lines.append('|---------|------|------|--------|---------|--------|')

            for ec in result.equivalence_classes:
                for vc in ec.valid_classes:
                    case_id += 1
                    lines.append(f'| TC-{case_id:03d} | 等价类-有效 | {ec.param} | {vc} | 正常 | P1 |')
                for ic in ec.invalid_classes:
                    case_id += 1
                    lines.append(f'| TC-{case_id:03d} | 等价类-无效 | {ec.param} | {ic} | 异常 | P2 |')

            for bv in result.boundary_values:
                for bp in bv.boundary_points:
                    case_id += 1
                    exp = "正常" if bp.is_valid else "异常"
                    lines.append(f'| TC-{case_id:03d} | 边界值 | {bv.param} | {bp.description} | {exp} | P1 |')

            if result.scenarios:
                for sc in result.scenarios.scenarios:
                    case_id += 1
                    lines.append(f'| TC-{case_id:03d} | 场景-{sc.type} | - | {sc.name} | - | P1 |')

            lines.append('')

        return '\n'.join(lines)
