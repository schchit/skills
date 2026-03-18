# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

import subprocess
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class CoverageResult:
    """覆盖率分析结果"""
    line_coverage: float = 0.0
    branch_coverage: float = 0.0
    function_coverage: float = 0.0
    status: str = "BLOCK"  # PASS/WARN/FAIL/BLOCK
    message: str = ""


class CoverageAnalyzer:
    """调用coverage.py计算覆盖率，阈值告警"""

    def __init__(self, line_threshold: float = 80.0,
                 branch_threshold: float = 70.0,
                 function_threshold: float = 80.0):
        self.line_threshold = line_threshold
        self.branch_threshold = branch_threshold
        self.function_threshold = function_threshold

    def run_coverage(self, test_file: str, source_file: str = None) -> CoverageResult:
        """运行测试并收集覆盖率"""
        try:
            cmd = [
                'python', '-m', 'coverage', 'run',
                '--source', source_file or '.',
                '-m', 'pytest', test_file, '-q', '--tb=no',
            ]
            subprocess.run(cmd, capture_output=True, timeout=60, check=True)
            result = subprocess.run(
                ['python', '-m', 'coverage', 'report', '--format=total'],
                capture_output=True, timeout=30, text=True,
            )
            total = float(result.stdout.strip())
            return self._evaluate(total)
        except FileNotFoundError:
            return CoverageResult(status="BLOCK", message="coverage.py 未安装")
        except subprocess.TimeoutExpired:
            return CoverageResult(status="BLOCK", message="测试执行超时")
        except subprocess.CalledProcessError as e:
            return CoverageResult(status="FAIL", message=f"测试失败: {e}")

    def evaluate(self, line_pct: float, branch_pct: float = 0.0,
                 func_pct: float = 0.0) -> CoverageResult:
        """评估覆盖率"""
        if line_pct >= self.line_threshold and branch_pct >= self.branch_threshold:
            status = "PASS"
            message = "覆盖率达标"
        elif line_pct >= self.line_threshold * 0.8:
            status = "WARN"
            message = f"覆盖率偏低 (行:{line_pct:.1f}% 需>{self.line_threshold}%)"
        else:
            status = "FAIL"
            message = f"覆盖率不足 (行:{line_pct:.1f}% 需>{self.line_threshold}%)"
        return CoverageResult(
            line_coverage=line_pct,
            branch_coverage=branch_pct,
            function_coverage=func_pct,
            status=status,
            message=message,
        )

    def _evaluate(self, total: float) -> CoverageResult:
        return self.evaluate(total)

    @staticmethod
    def format_report(result: CoverageResult) -> str:
        """格式化覆盖率报告"""
        status_icons = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌", "BLOCK": "🚫"}
        icon = status_icons.get(result.status, "?")
        lines = [
            f"  {icon} 覆盖率: {result.line_coverage:.1f}%",
            f"     状态: {result.status}",
            f"     {result.message}",
        ]
        return '\n'.join(lines)
