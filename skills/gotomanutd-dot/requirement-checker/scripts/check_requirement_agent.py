#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
需求内容自动检查脚本（智能体原生版 v2.0）
集成多格式解析：Word、Markdown、文本、图片（OCR）
专为 OpenClaw 智能体设计，利用智能体自身的 LLM 能力进行检查
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Optional

# 导入解析器
from parse_requirement import RequirementParser, parse_input

# 基础规则检查器（提供快速预检）
from check_requirement import RequirementChecker


class AgentRequirementChecker:
    """
    智能体需求检查器（集成多格式解析）
    
    设计理念：
    1. 自动解析多种格式输入（Word/Markdown/文本/图片）
    2. 规则检查作为预处理，快速发现问题
    3. 智能体 LLM 作为主检查器，进行语义分析
    4. 输出结构化结果，便于智能体生成报告
    """
    
    def __init__(self):
        self.parser = RequirementParser()
        self.rule_checker = RequirementChecker()
        
        # 检查规则定义（供智能体参考）
        self.rules = [
            {
                'id': 'flow_description',
                'name': '流程描述',
                'description': '多步处理或多步操作的需求要有流程描述',
                'checkpoints': [
                    '是否涉及多步操作（关键词：流程、步骤、依次、然后、第一步等）',
                    '是否有清晰的流程说明或流程图',
                    '流程节点是否清晰完整'
                ]
            },
            {
                'id': 'gwt_acceptance',
                'name': 'GWT 验收标准',
                'description': '需求应当包含 GWT（Given-When-Then）格式的验收标准',
                'checkpoints': [
                    '是否有验收标准章节',
                    '是否使用 GWT 格式（Given-When-Then）',
                    'Given 前置条件是否清晰',
                    'When 操作/事件是否明确',
                    'Then 预期结果是否可验证'
                ]
            },
            {
                'id': 'modification_elements',
                'name': '改造内容标注',
                'description': '明确改造涉及的接口、交易、菜单、定时任务、清算节点名称，用括号【】等标注',
                'checkpoints': [
                    '接口名称是否用【】标注',
                    '交易名称是否用【】标注',
                    '菜单名称是否用【】标注（管理台位置要明确）',
                    '定时任务名称是否用【】标注',
                    '清算节点名称是否用【】标注'
                ]
            },
            {
                'id': 'itemized_description',
                'name': '分项描述',
                'description': '不同的改造内容要分项、分点描述',
                'checkpoints': [
                    '不同改造内容是否分项描述',
                    '是否使用分点格式（1. 2. 3. 或 •）',
                    '相同改造是否合并后列举功能点'
                ]
            },
            {
                'id': 'element_completeness',
                'name': '元素完整性',
                'description': '报表、接口、字典项的需求必须列明所有涉及的元素名称及其取值规则',
                'checkpoints': [
                    '报表字段是否列全（名称、类型、精度、说明）',
                    '接口参数是否列全（入参、出参）',
                    '字典项取值是否列全（代码、名称、说明）',
                    '是否有取值规则说明'
                ]
            },
            {
                'id': 'interaction_logic',
                'name': '交互逻辑',
                'description': '涉及用户操作的需求必须说明操作前后的系统处理逻辑和交互表现',
                'checkpoints': [
                    '操作前校验是否说明',
                    '系统处理逻辑是否说明',
                    '成功交互表现是否说明',
                    '失败交互表现是否说明'
                ]
            },
            {
                'id': 'ui_details',
                'name': '界面细节',
                'description': '涉及界面改造需要明确写明元素类型、位置、样式、精度',
                'checkpoints': [
                    '元素类型是否明确（输入框/下拉框/按钮等）',
                    '元素位置是否明确',
                    '样式要求是否明确（宽度、颜色等）',
                    '数据精度是否明确（小数位数等）'
                ]
            },
            {
                'id': 'algorithm_formula',
                'name': '算法公式',
                'description': '涉及算法公式的需求应当写明公式并做出参数说明',
                'checkpoints': [
                    '公式是否完整',
                    '参数是否有说明',
                    '计算精度是否说明',
                    '舍入规则是否说明'
                ]
            },
            {
                'id': 'query_association',
                'name': '查询关联',
                'description': '查询类需求要说明是否关联查询历史表及关联规则',
                'checkpoints': [
                    '是否说明关联历史表',
                    '关联条件是否说明',
                    '关联规则是否说明'
                ]
            },
            {
                'id': 'exception_handling',
                'name': '异常处理',
                'description': '异常场景的处理需要说明',
                'checkpoints': [
                    '网络异常是否说明',
                    '数据校验失败是否说明',
                    '权限不足是否说明',
                    '系统超时是否说明'
                ]
            },
            {
                'id': 'modification_type',
                'name': '改造类型',
                'description': '必须说明是标准化改造还是个性化改造，考虑授权控制',
                'checkpoints': [
                    '是否说明标准化/个性化改造',
                    '授权控制是否说明',
                    '角色权限是否说明',
                    '数据范围是否说明'
                ]
            },
            {
                'id': 'prototype_attachment',
                'name': '原型附件',
                'description': '新增界面、修改界面需要附上原型图片或 URL',
                'checkpoints': [
                    '新增界面是否有原型（图片或 URL）',
                    '修改界面是否有原型（图片或 URL）'
                ]
            }
        ]
    
    def parse_and_check(self, input_path: str) -> Dict:
        """
        解析输入并检查（一体化流程）
        
        Args:
            input_path: 文件路径或文本内容
            
        Returns:
            完整的检查结果，包括解析信息和检查报告
        """
        # Step 1: 解析输入内容
        parse_result = self.parser.parse(input_path)
        
        if not parse_result['success']:
            return {
                'success': False,
                'error': parse_result.get('error', '解析失败'),
                'stage': 'parse'
            }
        
        content = parse_result['content']
        
        # Step 2: 运行规则预检查
        pre_check = self.rule_checker.run_check(content)
        
        # Step 3: 检查 GWT 验收标准
        gwt_analysis = self._check_gwt_acceptance(content)
        pre_check['gwt_analysis'] = gwt_analysis
        
        # Step 4: 构建智能体 prompt
        agent_prompt = self.build_agent_prompt(content, pre_check, parse_result['metadata'])
        
        return {
            'success': True,
            'parse_result': parse_result,
            'pre_check': pre_check,
            'agent_prompt': agent_prompt,
            'rules_context': self.get_rules_context()
        }
    
    def _check_gwt_acceptance(self, content: str) -> Dict:
        """
        检查 GWT 验收标准
        
        Args:
            content: 需求文档内容
            
        Returns:
            {
                'has_gwt': True/False,
                'gwt_items': [...],  # 已有的 GWT 条目
                'auto_generated': [],  # 占位，由智能体生成
                'suggestion': '建议文本（占位，由智能体生成）'
            }
        """
        result = {
            'has_gwt': False,
            'gwt_items': [],
            'auto_generated': [],
            'suggestion': ''
        }
        
        # 检测是否已有 GWT 格式内容
        gwt_keywords = ['given', 'when', 'then', '前提', '当', '那么', '则', '验收标准', 'acceptance']
        has_gwt = any(kw in content.lower() for kw in gwt_keywords)
        
        # 提取已有的 GWT 条目
        if has_gwt:
            import re
            # 尝试提取 GWT 格式的条目
            gwt_pattern = r'(?:[Gg]iven|[Ww]hen|[Tt]hen|前提 | 当 | 那么 | 则)[:：]([^\n]+)'
            matches = re.findall(gwt_pattern, content)
            if matches:
                result['has_gwt'] = True
                result['gwt_items'] = matches
        
        # 不再自动生成，交给智能体处理
        # 智能体会根据需求内容、复杂度、业务场景自主决定需要多少个验收场景
        
        return result
    
    def _generate_gwt(self, content: str) -> List[Dict]:
        """
        根据需求内容自动生成 GWT 验收标准
        
        Args:
            content: 需求文档内容
            
        Returns:
            GWT 条目列表
        """
        gwt_items = []
        
        # 分析需求内容，提取关键信息
        content_lower = content.lower()
        
        # 规则 1: 如果是界面/功能移除类需求
        if any(kw in content_lower for kw in ['去掉', '移除', '删除', '去掉', '不显示']):
            gwt_items.append({
                'given': '用户进入相关页面/功能',
                'when': '查看筛选条件/功能列表',
                'then': '不应看到被移除的功能/筛选项',
                'category': 'UI 验证'
            })
            gwt_items.append({
                'given': '用户使用该功能',
                'when': '执行相关操作',
                'then': '功能正常工作，不受移除项影响',
                'category': '功能验证'
            })
        
        # 规则 2: 如果是新增功能类需求
        if any(kw in content_lower for kw in ['新增', '添加', '增加', 'new', 'add']):
            gwt_items.append({
                'given': '用户进入相关页面',
                'when': '查看新增功能',
                'then': '能看到新增的功能/元素',
                'category': 'UI 验证'
            })
            gwt_items.append({
                'given': '用户使用新增功能',
                'when': '执行操作',
                'then': '功能按预期工作',
                'category': '功能验证'
            })
        
        # 规则 3: 如果是修改/优化类需求
        if any(kw in content_lower for kw in ['修改', '优化', '调整', 'modify', 'update']):
            gwt_items.append({
                'given': '用户进入修改后的页面',
                'when': '查看修改内容',
                'then': '能看到修改后的效果',
                'category': 'UI 验证'
            })
        
        # 规则 4: 通用数据验证
        gwt_items.append({
            'given': '系统正常运行',
            'when': '执行相关操作',
            'then': '数据正确保存/显示，无错误',
            'category': '数据验证'
        })
        
        # 规则 5: 异常场景
        gwt_items.append({
            'given': '网络异常或数据错误',
            'when': '执行操作',
            'then': '系统显示友好错误提示，不崩溃',
            'category': '异常验证'
        })
        
        return gwt_items
    
    def _build_gwt_suggestion(self, gwt_items: List[Dict]) -> str:
        """
        构建 GWT 建议文本（增强版：包含详细说明）
        
        Args:
            gwt_items: GWT 条目列表
            
        Returns:
            格式化的建议文本
        """
        if not gwt_items:
            return ''
        
        lines = []
        lines.append('## 建议补充的验收标准（GWT 格式）')
        lines.append('')
        lines.append('**问题说明**：检测到文档中缺少 GWT（Given-When-Then）格式的验收标准。')
        lines.append('')
        lines.append('**为什么需要 GWT**：')
        lines.append('- ✅ 明确验收条件，避免需求理解偏差')
        lines.append('- ✅ 便于测试人员编写测试用例')
        lines.append('- ✅ 帮助开发人员理解预期行为')
        lines.append('- ✅ 作为上线验收的依据')
        lines.append('')
        lines.append('**建议补充以下验收场景**：')
        lines.append('')
        
        for i, item in enumerate(gwt_items, 1):
            lines.append(f'### 验收场景 {i}: {item["category"]}')
            lines.append(f'- **Given**（给定）: {item["given"]}')
            lines.append(f'  - 说明：描述测试前的前置条件和初始状态')
            lines.append(f'- **When**（当）: {item["when"]}')
            lines.append(f'  - 说明：描述用户操作或系统触发的事件')
            lines.append(f'- **Then**（那么）: {item["then"]}')
            lines.append(f'  - 说明：描述可验证的预期结果')
            lines.append('')
        
        lines.append('**使用说明**：')
        lines.append('1. 根据实际业务场景调整上述验收标准')
        lines.append('2. 补充更多特定于本需求的验收场景')
        lines.append('3. 确保每个验收标准都是可测试、可验证的')
        lines.append('4. 将验收标准添加到需求文档的“验收标准”章节')
        lines.append('')
        
        return '\n'.join(lines)
    
    def get_rules_context(self) -> str:
        """获取规则上下文（供智能体加载到 prompt 中）"""
        lines = []
        lines.append("# 需求文档规范检查规则")
        lines.append("")
        
        for i, rule in enumerate(self.rules, 1):
            lines.append(f"## {i}. {rule['name']}")
            lines.append(f"**要求**: {rule['description']}")
            lines.append("")
            lines.append("检查要点:")
            for checkpoint in rule['checkpoints']:
                lines.append(f"- {checkpoint}")
            lines.append("")
        
        return "\n".join(lines)
    
    def build_agent_prompt(self, content: str, pre_check_result: Dict, metadata: Dict = None) -> str:
        """
        构建智能体检查 prompt
        
        Args:
            content: 解析后的需求文档内容
            pre_check_result: 预检查结果
            metadata: 解析元数据
            
        Returns:
            给智能体的检查指令
        """
        format_info = metadata.get('source', '直接输入') if metadata else '直接输入'
        
        # GWT 分析结果
        gwt_analysis = pre_check_result.get('gwt_analysis', {})
        gwt_section = ""
        if gwt_analysis:
            if not gwt_analysis.get('has_gwt'):
                gwt_section = f"""

## ⚠️ GWT 验收标准缺失 - 请你作为测试专家生成
检测到文档中缺少 GWT（Given-When-Then）格式的验收标准。

**请你作为资深测试专家，根据以下因素自主决定验收标准**：
1. **需求复杂度**：简单需求 2-3 个场景，中等需求 4-6 个场景，复杂需求 8+ 个场景
2. **业务类型**：
   - 查询类：查询条件验证、结果排序、分页、导出等
   - 表单类：必填项验证、格式验证、提交验证、成功/失败提示等
   - 列表类：筛选验证、排序验证、分页验证、批量操作等
   - 报表类：统计准确性、数据一致性、钻取功能等
3. **影响范围**：
   - 前端改动：UI 验证、交互验证、兼容性验证
   - 后端改动：数据验证、接口验证、性能验证
   - 全栈改动：全方位验收
4. **风险等级**：核心功能需要更多验收场景，边缘功能可适当简化

**输出要求**：
- 在 gwt_acceptance.auto_generated 中列出生成的验收场景
- 每个场景说明 category（验收类别）和 reason（为什么需要这个场景）
- 在 expert_comment 中说明你的决策理由（为什么选择这些场景、覆盖了多少方面）
"""
            else:
                gwt_section = f"""

## ✅ GWT 验收标准
检测到文档已包含 GWT 格式的验收标准：
{json.dumps(gwt_analysis.get('gwt_items', []), ensure_ascii=False, indent=2)}

请评估这些验收标准是否完整、是否需要补充。
"""
        
        prompt = f"""你是一个专业的需求文档评审专家。请检查以下需求文档是否符合规范要求。

## 输入信息
- **来源**: {format_info}
- **内容长度**: {len(content)} 字

## 检查规则
{self.get_rules_context()}
{gwt_section}

## 预检查结果（参考）
规则检查发现 {len(pre_check_result.get('warnings', []))} 个潜在问题：
{json.dumps(pre_check_result.get('warnings', []), ensure_ascii=False, indent=2)}

注意：预检查基于关键词匹配，可能有误判或遗漏，请以你的语义分析为准。

## 需求文档内容
{content}

## 输出要求
请按照以下 JSON 格式输出检查结果：

```json
{{
  "summary": {{
    "total_rules": 12,
    "passed_count": 通过的规则数，
    "warning_count": 警告数，
    "issue_count": 严重问题数，
    "compliance_rate": 合规率百分比（数字）
  }},
  "details": [
    {{
      "rule_id": "规则 ID",
      "rule_name": "规则名称",
      "status": "passed/warning/issue",
      "finding": "具体发现（详细说明问题是什么，为什么是问题）",
      "suggestion": "改进建议（具体可操作的建议，包含示例）",
      "evidence": "文档中的相关原文引用（如有）"
    }}
  ],
  "overall_comment": "总体评价和建议（200 字以内）",
  "priority_fixes": [
    {{
      "issue": "问题描述",
      "reason": "为什么需要优先修正",
      "suggestion": "如何修正"
    }}
  ],
  "gwt_acceptance": {{
    "has_gwt": true/false,
    "gwt_items": ["已有的 GWT 条目"],
    "auto_generated": [
      {{
        "given": "前置条件",
        "when": "操作/事件",
        "then": "预期结果",
        "category": "验收类别（如 UI 验证/功能验证/数据验证/异常验证等）",
        "reason": "为什么需要这个验收场景"
      }}
    ],
    "expert_comment": "作为测试专家，说明生成了多少个验收场景、为什么选择这些场景、覆盖了哪些方面"
  }}
}}
```

注意：
1. 必须输出合法的 JSON 格式
2. 每项检查都要有明确的 status（passed/warning/issue）
3. **finding 要具体**：说明问题是什么、在哪里、为什么是问题
4. **suggestion 要可操作**：给出具体的修改建议，最好包含示例
5. **evidence 要引用原文**：让读者知道问题出在哪里
6. 如果文档内容不足以判断，标记为 warning 并说明需要补充什么
7. **priority_fixes 要说明优先级原因**：为什么这个问题需要优先处理
8. **gwt_acceptance 作为测试专家自主决定**：
   - 根据需求复杂度决定验收场景数量（简单需求 2-3 个，中等需求 4-6 个，复杂需求 8+ 个）
   - 根据业务类型选择合适的验收类别（查询类/表单类/列表类/报表类等）
   - 根据影响范围确定验证重点（前端/后端/全栈）
   - 在 expert_comment 中说明你的决策理由
"""
        return prompt
    
    def format_report(self, llm_result: Dict, pre_check_result: Dict, parse_result: Dict) -> str:
        """
        格式化检查报告（供智能体展示给用户）
        
        Args:
            llm_result: LLM 分析结果
            pre_check_result: 预检查结果
            parse_result: 解析结果
            
        Returns:
            格式化的报告文本
        """
        lines = []
        lines.append("📋 需求规范检查报告")
        lines.append("=" * 60)
        lines.append("")
        
        # 输入信息
        metadata = parse_result.get('metadata', {})
        lines.append(f"📄 输入来源：{metadata.get('source', '未知')}")
        lines.append(f"📝 内容长度：{len(parse_result.get('content', ''))} 字")
        lines.append("")
        
        # 摘要
        summary = llm_result.get('summary', {})
        lines.append(f"📊 合规率：{summary.get('compliance_rate', 0)}%")
        lines.append(f"✅ 通过：{summary.get('passed_count', 0)}")
        lines.append(f"⚠️ 警告：{summary.get('warning_count', 0)}")
        lines.append(f"❌ 问题：{summary.get('issue_count', 0)}")
        lines.append("")
        
        # 总体评价
        if llm_result.get('overall_comment'):
            lines.append("💬 总体评价:")
            lines.append(f"   {llm_result['overall_comment']}")
            lines.append("")
        
        # 优先修正项
        if llm_result.get('priority_fixes'):
            lines.append("🔴 优先修正:")
            for i, fix in enumerate(llm_result['priority_fixes'], 1):
                lines.append(f"  {i}. {fix}")
            lines.append("")
        
        # 详细检查结果
        details = llm_result.get('details', [])
        
        # 通过项
        passed = [d for d in details if d.get('status') == 'passed']
        if passed:
            lines.append("✅ 通过检查:")
            for item in passed:
                lines.append(f"  • {item['rule_name']}: {item.get('finding', '检查通过')}")
            lines.append("")
        
        # 警告和问题项
        issues = [d for d in details if d.get('status') in ['warning', 'issue']]
        if issues:
            lines.append("⚠️ 需要注意:")
            for i, item in enumerate(issues, 1):
                status_icon = "❌" if item['status'] == 'issue' else "⚠️"
                lines.append(f"  {i}. {status_icon} 【{item['rule_name']}】")
                lines.append(f"     问题：{item.get('finding', '')}")
                if item.get('suggestion'):
                    lines.append(f"     建议：{item['suggestion']}")
                if item.get('evidence'):
                    lines.append(f"     原文：\"{item['evidence']}\"")
                lines.append("")
        
        return "\n".join(lines)


def check_file(file_path: str) -> Dict:
    """检查文件（一体化流程）"""
    checker = AgentRequirementChecker()
    return checker.parse_and_check(file_path)


def check_text(text: str) -> Dict:
    """检查文本（一体化流程）"""
    checker = AgentRequirementChecker()
    return checker.parse_and_check(text)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='需求规范检查工具（智能体原生版 v2.0 - 多格式支持）')
    parser.add_argument('input', nargs='?', help='文件路径或文本内容')
    parser.add_argument('--text', action='store_true', help='输入为文本内容')
    parser.add_argument('--prompt-only', action='store_true', help='仅输出给智能体的 prompt')
    parser.add_argument('--rules', action='store_true', help='仅输出检查规则')
    parser.add_argument('--parse-only', action='store_true', help='仅解析内容，不检查')
    parser.add_argument('--list-formats', action='store_true', help='列出支持的格式')
    
    args = parser.parse_args()
    
    if args.list_formats:
        p = RequirementParser()
        print(p.get_supported_formats())
        sys.exit(0)
    
    if not args.input:
        print("用法：python check_requirement_agent.py [选项] <文件路径 | 文本>")
        print("")
        print("选项:")
        print("  --text          输入为文本内容")
        print("  --prompt-only   仅输出给智能体的 prompt（供智能体调用）")
        print("  --rules         仅输出检查规则")
        print("  --parse-only    仅解析内容，不检查")
        print("  --list-formats  列出支持的格式")
        print("")
        print("支持的格式:")
        print("  .docx       - Word 文档")
        print("  .md/.txt    - Markdown/纯文本")
        print("  .pdf        - PDF 文档")
        print("  .jpg/.png   - 图片（OCR 识别）")
        print("  .html       - HTML 页面")
        print("")
        print("示例:")
        print("  # 检查 Word 文档")
        print("  python check_requirement_agent.py requirement.docx")
        print("")
        print("  # 检查文本")
        print("  python check_requirement_agent.py --text \"需求内容...\"")
        print("")
        print("  # 图片 OCR + 检查")
        print("  python check_requirement_agent.py requirement.png")
        print("")
        print("  # 获取智能体 prompt")
        print("  python check_requirement_agent.py --prompt-only requirement.md")
        sys.exit(1)
    
    if args.rules:
        checker = AgentRequirementChecker()
        print(checker.get_rules_context())
        sys.exit(0)
    
    # 解析输入
    input_parser = RequirementParser()
    parse_result = input_parser.parse(args.input)
    
    if not parse_result['success']:
        print(f"❌ 解析失败：{parse_result.get('error', '未知错误')}")
        sys.exit(1)
    
    if args.parse_only:
        # 仅解析
        print("✅ 解析成功")
        print(f"格式：{parse_result['format']}")
        print(f"元数据：{json.dumps(parse_result.get('metadata', {}), indent=2, ensure_ascii=False)}")
        print("")
        print("=" * 60)
        print("内容预览（前 500 字）:")
        print("=" * 60)
        content = parse_result.get('content', '')
        if len(content) > 500:
            print(content[:500] + "\n...（还有 {} 字）".format(len(content) - 500))
        else:
            print(content)
        sys.exit(0)
    
    # 完整检查流程
    checker = AgentRequirementChecker()
    result = checker.parse_and_check(args.input)
    
    if not result['success']:
        print(f"❌ 检查失败：{result.get('error', '未知错误')}")
        sys.exit(1)
    
    if args.prompt_only:
        # 仅输出 prompt，供智能体使用
        print(result['agent_prompt'])
    else:
        # 输出预检查结果
        print("📋 需求规范预检查报告")
        print("=" * 60)
        print("")
        
        # 输入信息
        metadata = result['parse_result'].get('metadata', {})
        print(f"📄 输入来源：{metadata.get('source', '未知')}")
        print(f"📝 内容长度：{len(result['parse_result'].get('content', ''))} 字")
        print("")
        
        pre_check = result.get('pre_check', {})
        summary = pre_check.get('summary', {})
        
        print(f"📊 合规率：{summary.get('compliance_rate', 100)}%")
        print(f"✅ 通过：{summary.get('total_passed', 0)}")
        print(f"⚠️ 警告：{summary.get('total_warnings', 0)}")
        print("")
        
        if pre_check.get('passed'):
            print("✅ 通过检查:")
            for item in pre_check['passed'][:5]:
                print(f"  • {item}")
            print("")
        
        if pre_check.get('warnings'):
            print("⚠️ 潜在问题:")
            for i, item in enumerate(pre_check['warnings'], 1):
                print(f"  {i}. 【{item['rule']}】{item['issue']}")
                print(f"     建议：{item['suggestion']}")
            print("")
        
        # GWT 检查结果
        gwt_analysis = pre_check.get('gwt_analysis', {})
        if gwt_analysis:
            print("=" * 60)
            print("📋 GWT 验收标准检查")
            print("=" * 60)
            print()
            
            if gwt_analysis.get('has_gwt'):
                print("✅ 文档已包含 GWT 格式的验收标准")
                print()
                print("已有的验收标准:")
                for item in gwt_analysis.get('gwt_items', [])[:5]:
                    print(f"  • {item}")
            else:
                print("⚠️ 文档缺少 GWT 格式的验收标准")
                print()
                print("已自动生成建议的验收标准:")
                print()
                print(gwt_analysis.get('suggestion', '无'))
            print()
        
        print("💡 提示：使用 --prompt-only 获取智能体检查 prompt，进行深度分析")
    
    sys.exit(0)


if __name__ == '__main__':
    main()
