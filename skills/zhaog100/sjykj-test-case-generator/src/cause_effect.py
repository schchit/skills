# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from itertools import product


@dataclass
class Cause:
    """因"""
    id: int
    name: str
    states: List[str]


@dataclass
class Effect:
    """果"""
    id: int
    name: str


@dataclass
class DecisionRule:
    """判定规则"""
    cause_values: Dict[int, str]
    effect_values: Dict[int, str]


@dataclass
class CauseEffectAnalysis:
    """因果图分析结果"""
    method: str
    causes: List[Cause] = field(default_factory=list)
    effects: List[Effect] = field(default_factory=list)
    decision_table: List[DecisionRule] = field(default_factory=list)
    optimized_rules: List[DecisionRule] = field(default_factory=list)


class CauseEffectAnalyzer:
    """因果图 - 生成判定表，支持优化"""

    def analyze(self, method: str, params: List[Dict[str, Any]] = None,
                docstring: str = "", **kwargs) -> CauseEffectAnalysis:
        """根据参数和docstring生成因果图"""
        params = params or []

        # Build causes from params
        causes = []
        for i, p in enumerate(params, 1):
            ptype = p.get('type_hint', 'str') or 'str'
            states = self._type_states(ptype, p.get('has_default', False))
            causes.append(Cause(id=i, name=p['name'], states=states))

        # Build effects from docstring
        effects = self._extract_effects(docstring)
        if not effects:
            effects = [Effect(id=1, name="正常返回"), Effect(id=2, name="异常/错误")]

        # Generate decision table
        state_lists = [c.states for c in causes]
        all_combos = list(product(*state_lists)) if state_lists else [()]

        decision_table = []
        for combo in all_combos:
            cause_values = {c.id: combo[i] for i, c in enumerate(causes)}
            effect_values = self._evaluate_effects(causes, effects, cause_values, docstring)
            decision_table.append(DecisionRule(cause_values=cause_values, effect_values=effect_values))

        # Optimize: remove impossible/duplicate rules
        optimized = self._optimize(causes, effects, decision_table, docstring)

        return CauseEffectAnalysis(
            method=method,
            causes=causes,
            effects=effects,
            decision_table=decision_table,
            optimized_rules=optimized,
        )

    def _type_states(self, type_hint: str, has_default: bool) -> List[str]:
        """根据类型生成因的状态"""
        base = type_hint.strip().split('.')[-1].lower() if type_hint else 'str'
        base = base.replace('optional[', '').replace(']', '')

        if base in ('int', 'float'):
            states = ['正值', '零值', '负值']
        elif base == 'str':
            states = ['有效字符串', '空字符串']
        elif base == 'bool':
            states = ['True', 'False']
        else:
            states = ['有效值', '无效值']

        if has_default:
            states.append('默认值')
        return states

    def _extract_effects(self, docstring: str) -> List[Effect]:
        """从docstring提取果"""
        effects = []
        import re
        # Look for 返回/return patterns
        returns = re.findall(r'返回\s*(.+?)(?:[，,。.]|$)', docstring)
        for i, ret in enumerate(returns, 1):
            effects.append(Effect(id=i, name=f"返回{ret.strip()[:20]}"))
        return effects

    def _evaluate_effects(self, causes, effects, cause_values, docstring) -> Dict[int, str]:
        """评估因的组合对应的果"""
        result = {}
        import re

        has_invalid = any('无效' in v or '空' in v for v in cause_values.values())
        has_zero_negative = any(v in ('零值', '负值') for v in cause_values.values())

        if has_invalid:
            result[2] = '异常/错误'
        elif has_zero_negative and re.search(r'<=\s*0|>\s*0|positive|必须.*正', docstring):
            result[2] = '异常/错误'
        else:
            result[1] = '正常返回'

        return result

    def _optimize(self, causes, effects, decision_table, docstring) -> List[DecisionRule]:
        """优化判定表：合并等价规则"""
        if len(decision_table) <= 1:
            return decision_table

        # Remove duplicate effect patterns, keep representative
        seen_effects = []
        optimized = []
        for rule in decision_table:
            key = tuple(sorted(rule.effect_values.items()))
            if key not in seen_effects:
                seen_effects.append(key)
                optimized.append(rule)

        return optimized
