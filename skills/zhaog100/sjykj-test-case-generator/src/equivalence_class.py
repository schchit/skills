# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class EquivalenceClass:
    """等价类划分结果"""
    method: str
    param: str
    param_type: str
    valid_classes: List[str] = field(default_factory=list)
    invalid_classes: List[str] = field(default_factory=list)


class EquivalenceClassAnalyzer:
    """等价类划分"""

    # Type-specific valid/invalid classes
    TYPE_CLASSES = {
        'int': {
            'valid': ['正整数', '零', '负整数'],
            'invalid': ['浮点数', '字符串', 'None', '超大数'],
        },
        'float': {
            'valid': ['正数', '负数', '零'],
            'invalid': ['字符串', 'None', 'NaN', 'Infinity'],
        },
        'str': {
            'valid': ['有效字符串', '空字符串'],
            'invalid': ['None', '数字', '特殊字符超长串'],
        },
        'bool': {
            'valid': ['True', 'False'],
            'invalid': ['字符串"True"', '整数1', 'None'],
        },
        'list': {
            'valid': ['非空列表', '空列表'],
            'invalid': ['None', '字符串', '字典'],
        },
        'dict': {
            'valid': ['非空字典', '空字典'],
            'invalid': ['None', '列表', '字符串'],
        },
    }

    def analyze(self, method: str, param_name: str, param_type: str,
                docstring: str = "", **kwargs) -> EquivalenceClass:
        """对单个参数进行等价类划分"""
        base_type = self._normalize_type(param_type)

        classes = self.TYPE_CLASSES.get(base_type, {
            'valid': ['有效值'],
            'invalid': ['None', '错误类型'],
        })

        # Customize based on Optional
        if 'Optional' in param_type or param_type.startswith('Optional['):
            classes['valid'].append('None')

        # Customize based on Union
        if 'Union[' in param_type or '|' in param_type:
            classes['invalid'] = [c for c in classes['invalid'] if c != 'None']

        # Customize based on docstring hints
        valid, invalid = self._extract_from_docstring(docstring, classes['valid'], classes['invalid'])

        return EquivalenceClass(
            method=method,
            param=param_name,
            param_type=param_type,
            valid_classes=valid,
            invalid_classes=invalid,
        )

    def analyze_function(self, method: str, params: List[Dict[str, Any]],
                         docstring: str = "") -> List[EquivalenceClass]:
        """对函数所有参数进行等价类划分"""
        results = []
        for p in params:
            ec = self.analyze(
                method=method,
                param_name=p.get('name', ''),
                param_type=p.get('type_hint', '') or '',
                docstring=docstring,
            )
            results.append(ec)
        return results

    def _normalize_type(self, type_hint: str) -> str:
        """规范化类型名称"""
        if not type_hint:
            return 'str'
        # Handle Optional[X] -> X
        import re
        m = re.match(r'Optional\[(.+)\]', type_hint)
        if m:
            return m.group(1).strip().split('.')[-1]
        m = re.match(r'Union\[(.+)\]', type_hint)
        if m:
            types = [t.strip().split('.')[-1] for t in m.group(1).split(',')]
            return types[0] if types else 'str'
        return type_hint.strip().split('.')[-1]

    def _extract_from_docstring(self, docstring: str, default_valid: List[str],
                                 default_invalid: List[str]) -> tuple:
        """从docstring中提取额外的等价类信息"""
        valid = list(default_valid)
        invalid = list(default_invalid)
        if not docstring:
            return valid, invalid
        # Look for range hints
        import re
        if re.search(r'>\s*0|positive|正', docstring):
            invalid.append('零或负数')
        if re.search(r'非空|not\s+empty|不为空', docstring):
            invalid.append('空字符串')
            valid = [v for v in valid if '空' not in v]
        return valid, invalid
