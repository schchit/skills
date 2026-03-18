# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class _TestDataPoint:
    """测试点"""
    feature: str = ""
    name: str = ""
    input_conditions: str = ""
    expected_output: str = ""
    priority: str = "P2"
    source_line: int = 0


class RequirementAnalyzer:
    """解析Markdown需求文档提取测试点"""

    def parse_file(self, filepath: str) -> List[_TestDataPoint]:
        with open(filepath, 'r', encoding='utf-8') as f:
            return self.parse_text(f.read())

    def parse_text(self, text: str) -> List[_TestDataPoint]:
        """解析Markdown文本提取测试点"""
        test_points = []
        current_feature = ""
        lines = text.splitlines()

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Detect ## heading as feature
            if stripped.startswith('## ') and not stripped.startswith('### '):
                current_feature = stripped[3:].strip()
                i += 1
                continue

            # Detect test point patterns
            tp = self._parse_line_as_test_point(stripped, current_feature, i + 1)
            if tp:
                test_points.append(tp)
            i += 1

        return test_points

    def _parse_line_as_test_point(self, line: str, feature: str, line_no: int) -> Optional[_TestDataPoint]:
        """尝试将一行解析为测试点"""
        # Pattern: - **输入**: ... / **输出**: ... / **规则**: ... / **异常**: ...
        if line.startswith('- ') or line.startswith('* '):
            content = line[2:]
            name = ""
            input_conditions = ""
            expected_output = ""
            priority = "P2"

            # Extract name (before colon if no bold)
            if '**' in content:
                # Parse key-value pairs
                parts = content.split('**')
                # parts: ['prefix', 'key', 'value', 'key', 'value', ...]
                for j in range(1, len(parts) - 1, 2):
                    key = parts[j].rstrip(':')
                    val = parts[j + 1].strip().strip(':').strip()
                    if key == '输入':
                        input_conditions = val
                    elif key == '输出' or key == '预期':
                        expected_output = val
                    elif key == '规则':
                        name = val
                    elif key == '异常':
                        input_conditions = val
                        name = name or f"异常-{val[:20]}"
                    elif key == '优先级':
                        priority = val

                # If no name extracted, use first value as name
                if not name and len(parts) > 1:
                    name = parts[1].strip().rstrip(':')
            else:
                name = content.strip()
                if not name:
                    return None

            if name:
                return _TestDataPoint(
                    feature=feature,
                    name=name,
                    input_conditions=input_conditions,
                    expected_output=expected_output,
                    priority=priority,
                    source_line=line_no,
                )

        # Pattern: numbered list 1. 2. 3.
        import re
        m = re.match(r'^(\d+)\.\s+(.+)', line)
        if m:
            content = m.group(2)
            return _TestDataPoint(
                feature=feature,
                name=content.strip(),
                priority="P2",
                source_line=line_no,
            )

        return None
