# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

from typing import List, Dict, Optional
from src.test_design_engine import AnalysisResult


class ReportGenerator:
    """ASCII可视化报告 + 覆盖率统计"""

    def generate_report(self, results: List[AnalysisResult]) -> str:
        """生成ASCII报告"""
        lines = [
            "=" * 70,
            "  测试设计分析报告",
            "=" * 70,
            "",
        ]

        total_cases = 0
        for result in results:
            func = result.function
            case_count = self._count_cases(result)
            total_cases += case_count

            lines.append(f"┌─ {func.name}({'(' + ', '.join(p.name for p in func.params) + ')'})")
            lines.append(f"│  返回: {func.return_type or 'Unknown'}")
            lines.append(f"│  方法: {', '.join(result.selected_methods)}")
            lines.append(f"│  用例: {case_count}")
            lines.append("│")

            if result.equivalence_classes:
                lines.append("│  等价类划分:")
                for ec in result.equivalence_classes:
                    lines.append(f"│    {ec.param} ({ec.param_type}):")
                    lines.append(f"│      有效: {', '.join(ec.valid_classes)}")
                    lines.append(f"│      无效: {', '.join(ec.invalid_classes)}")

            if result.boundary_values:
                lines.append("│  边界值:")
                for bv in result.boundary_values:
                    for bp in bv.boundary_points[:3]:  # Show top 3
                        mark = "✓" if bp.is_valid else "✗"
                        lines.append(f"│    [{mark}] {bp.description} = {bp.value}")
                    if len(bv.boundary_points) > 3:
                        lines.append(f"│    ... 还有 {len(bv.boundary_points) - 3} 个")

            if result.scenarios:
                lines.append("│  场景法:")
                type_map = {'basic': '基本流', 'alternative': '备选流', 'exception': '异常流'}
                for sc in result.scenarios.scenarios:
                    cn_type = type_map.get(sc.type, sc.type)
                    lines.append(f"│    {cn_type}: {sc.name}")

            if result.error_guessing:
                lines.append("│  错误推测:")
                for es in result.error_guessing.error_scenarios[:3]:
                    lines.append(f"│    {es.param}: {es.description}")
                if len(result.error_guessing.error_scenarios) > 3:
                    lines.append(f"│    ... 还有 {len(result.error_guessing.error_scenarios) - 3} 个")

            lines.append("└" + "─" * 60)
            lines.append("")

        # Summary
        lines.append("=" * 70)
        lines.append(f"  总计: {len(results)} 个函数, {total_cases} 个测试用例")
        lines.append("=" * 70)

        return '\n'.join(lines)

    def generate_coverage_summary(self, results: List[AnalysisResult]) -> str:
        """生成覆盖率统计摘要"""
        lines = ["覆盖率统计", "-" * 40]

        method_counts: Dict[str, int] = {}
        for result in results:
            for m in result.selected_methods:
                method_counts[m] = method_counts.get(m, 0) + 1

        total = len(results)
        for method, count in sorted(method_counts.items()):
            bar_len = int(count / max(total, 1) * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            pct = count / max(total, 1) * 100
            lines.append(f"  {method:20s} {bar} {count}/{total} ({pct:.0f}%)")

        return '\n'.join(lines)

    def _count_cases(self, result: AnalysisResult) -> int:
        count = 0
        for ec in result.equivalence_classes:
            count += len(ec.valid_classes) + len(ec.invalid_classes)
        for bv in result.boundary_values:
            count += len(bv.boundary_points)
        if result.scenarios:
            count += len(result.scenarios.scenarios)
        return count
