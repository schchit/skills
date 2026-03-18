# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import re


@dataclass
class Scenario:
    """测试场景"""
    name: str
    type: str  # 'basic', 'alternative', 'exception'
    conditions: List[str] = field(default_factory=list)


@dataclass
class ScenarioAnalysis:
    """场景法分析结果"""
    method: str
    scenarios: List[Scenario] = field(default_factory=list)


class ScenarioAnalyzer:
    """场景法 - 基本流/备选流/异常流"""

    def analyze(self, method: str, docstring: str = "",
                params: List[Dict[str, Any]] = None, **kwargs) -> ScenarioAnalysis:
        """从docstring和函数签名提取场景"""
        params = params or []
        scenarios = []

        # Extract from docstring
        if docstring:
            scenarios.extend(self._extract_from_docstring(docstring))

        # Generate generic scenarios if none found
        if not scenarios:
            scenarios.append(Scenario(name="正常流程", type="basic", conditions=["所有参数有效"]))
            scenarios.append(Scenario(name="参数为空", type="exception", conditions=["参数为None或空"]))
            if params:
                for p in params:
                    if not p.get('has_default'):
                        scenarios.append(Scenario(
                            name=f"{p['name']}无效",
                            type="exception",
                            conditions=[f"{p['name']}为无效值"],
                        ))

        return ScenarioAnalysis(method=method, scenarios=scenarios)

    def _extract_from_docstring(self, docstring: str) -> List[Scenario]:
        """从docstring提取场景"""
        scenarios = []

        # Pattern: raise/抛出/异常 → exception scenario
        if re.search(r'raise\s+\w+|抛出|异常|error', docstring, re.IGNORECASE):
            scenarios.append(Scenario(name="异常流程", type="exception",
                                      conditions=["触发异常条件"]))

        # Pattern: 如果...返回/如果...则 → conditional flows
        conditions = re.findall(r'如果\s*(.+?)[，,。]', docstring)
        for cond in conditions:
            cond = cond.strip()
            if '抛出' in cond or 'raise' in cond.lower() or '<=' in cond or '>=' in cond:
                scenarios.append(Scenario(name=f"条件: {cond[:30]}", type="exception",
                                          conditions=[cond]))
            else:
                scenarios.append(Scenario(name=f"条件: {cond[:30]}", type="alternative",
                                          conditions=[cond]))

        # If only exception found, add a basic flow
        has_basic = any(s.type == 'basic' for s in scenarios)
        if scenarios and not has_basic:
            scenarios.insert(0, Scenario(name="正常流程", type="basic",
                                         conditions=["所有正常条件满足"]))

        return scenarios
