#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
需求内容自动检查脚本（LLM 增强版）
使用大模型进行语义理解 + 规则检查，提升检查准确性
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# 检查是否安装了 openai 库
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# 基础规则检查器（复用原有逻辑）
from check_requirement import RequirementChecker


class LLMRequirementChecker:
    """基于大模型的需求检查器"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: str = "qwen-plus"):
        """
        初始化 LLM 检查器
        
        Args:
            api_key: API Key（可选，不传则使用环境变量）
            base_url: API Base URL（可选）
            model: 模型名称（默认 qwen-plus）
        """
        self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY') or os.getenv('OPENAI_API_KEY')
        self.base_url = base_url or os.getenv('OPENAI_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        self.model = model
        self.client = None
        
        if HAS_OPENAI and self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
    
    def check_with_llm(self, content: str, rules: List[Dict]) -> Dict:
        """
        使用大模型检查需求文档
        
        Args:
            content: 需求文档内容
            rules: 检查规则列表
            
        Returns:
            检查结果
        """
        if not self.client:
            return {
                'error': 'LLM 未初始化，请设置 API Key 或安装 openai 库',
                'fallback': True
            }
        
        # 构建检查提示词
        prompt = self._build_prompt(content, rules)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的需求文档评审专家，擅长检查 PRD/需求文档是否符合规范要求。请仔细分析文档内容，按照给定的检查规则逐项检查，并给出详细的检查报告。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # 降低随机性，提高一致性
                max_tokens=4000
            )
            
            result_text = response.choices[0].message.content
            
            # 解析 LLM 返回结果
            return self._parse_llm_result(result_text)
            
        except Exception as e:
            return {
                'error': f'LLM 调用失败：{str(e)}',
                'fallback': True
            }
    
    def _build_prompt(self, content: str, rules: List[Dict]) -> str:
        """构建检查提示词"""
        
        rules_text = "\n".join([
            f"{i+1}. {rule['name']}: {rule['description']}"
            for i, rule in enumerate(rules)
        ])
        
        prompt = f"""请检查以下需求文档是否符合规范要求：

## 检查规则
{rules_text}

## 需求文档内容
{content}

## 输出要求
请按照以下 JSON 格式输出检查结果（不要输出其他内容）：

```json
{{
  "summary": {{
    "total_rules": 检查规则总数，
    "passed_count": 通过的规则数，
    "warning_count": 警告数，
    "issue_count": 问题数，
    "compliance_rate": 合规率百分比（数字）
  }},
  "details": [
    {{
      "rule": "规则名称",
      "status": "passed/warning/issue",
      "finding": "具体发现",
      "suggestion": "改进建议（如有问题）",
      "evidence": "文档中的相关证据或引用"
    }}
  ],
  "overall_comment": "总体评价和建议"
}}
```

注意：
1. 必须输出合法的 JSON 格式
2. 每项检查都要有明确的 status（passed/warning/issue）
3. finding 要具体，不能笼统
4. evidence 要引用文档中的原文（如有）
5. 如果文档内容不足以判断，标记为 warning 并说明需要补充什么
"""
        
        return prompt
    
    def _parse_llm_result(self, result_text: str) -> Dict:
        """解析 LLM 返回结果"""
        try:
            # 尝试提取 JSON
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 如果没有 markdown 代码块，尝试直接解析
                json_str = result_text.strip()
            
            result = json.loads(json_str)
            result['llm_enhanced'] = True
            return result
            
        except Exception as e:
            # JSON 解析失败，返回原始文本
            return {
                'raw_result': result_text,
                'parse_error': str(e),
                'llm_enhanced': True
            }


class HybridRequirementChecker:
    """混合检查器：规则检查 + LLM 语义检查"""
    
    def __init__(self, use_llm: bool = True):
        """
        初始化混合检查器
        
        Args:
            use_llm: 是否启用 LLM 增强
        """
        self.rule_checker = RequirementChecker()
        self.use_llm = use_llm
        self.llm_checker = LLMRequirementChecker() if use_llm else None
        
        # 定义检查规则
        self.rules = [
            {
                'name': '流程描述',
                'description': '多步处理或多步操作的需求要有流程描述'
            },
            {
                'name': '改造内容标注',
                'description': '明确改造涉及的接口、交易、菜单、定时任务、清算节点名称，用括号【】等标注'
            },
            {
                'name': '分项描述',
                'description': '不同的改造内容要分项、分点描述'
            },
            {
                'name': '元素完整性',
                'description': '报表、接口、字典项的需求必须列明所有涉及的元素名称及其取值规则'
            },
            {
                'name': '交互逻辑',
                'description': '涉及用户操作的需求必须说明操作前后的系统处理逻辑和交互表现'
            },
            {
                'name': '界面细节',
                'description': '涉及界面改造需要明确写明元素类型、位置、样式、精度'
            },
            {
                'name': '算法公式',
                'description': '涉及算法公式的需求应当写明公式并做出参数说明'
            },
            {
                'name': '查询关联',
                'description': '查询类需求要说明是否关联查询历史表及关联规则'
            },
            {
                'name': '异常处理',
                'description': '异常场景的处理需要说明'
            },
            {
                'name': '改造类型',
                'description': '必须说明是标准化改造还是个性化改造，考虑授权控制'
            },
            {
                'name': '原型附件',
                'description': '新增界面、修改界面需要附上原型图片或 URL'
            }
        ]
    
    def run_check(self, content: str) -> Dict:
        """运行混合检查"""
        results = {
            'rule_based': None,
            'llm_based': None,
            'merged': None
        }
        
        # 1. 规则检查
        results['rule_based'] = self.rule_checker.run_check(content)
        
        # 2. LLM 检查（如果启用）
        if self.use_llm and self.llm_checker:
            results['llm_based'] = self.llm_checker.check_with_llm(content, self.rules)
        
        # 3. 合并结果
        results['merged'] = self._merge_results(results['rule_based'], results.get('llm_based'))
        
        return results
    
    def _merge_results(self, rule_result: Dict, llm_result: Optional[Dict]) -> Dict:
        """合并规则检查和 LLM 检查结果"""
        
        if not llm_result or llm_result.get('error'):
            # LLM 不可用，只返回规则检查结果
            warnings = rule_result.get('warnings', [])
            passed = rule_result.get('passed', [])
            return {
                'summary': rule_result.get('summary', {}),
                'warnings': warnings,
                'passed': passed,
                'details': self._convert_rule_details(rule_result),
                'source': 'rule_based_only',
                'llm_available': False
            }
        
        # 合并两种检查结果
        merged_warnings = []
        merged_passed = []
        
        # 使用 LLM 的详细分析作为主结果
        if 'details' in llm_result:
            for item in llm_result['details']:
                if item['status'] == 'passed':
                    merged_passed.append(f"{item['rule']}: {item.get('finding', '检查通过')}")
                else:
                    merged_warnings.append({
                        'rule': item['rule'],
                        'issue': item.get('finding', ''),
                        'suggestion': item.get('suggestion', ''),
                        'evidence': item.get('evidence', ''),
                        'source': 'llm'
                    })
        
        # 补充规则检查发现的问题（LLM 可能遗漏的）
        for warning in rule_result.get('warnings', []):
            # 检查是否已有类似问题
            existing = any(w['rule'] == warning['rule'] for w in merged_warnings)
            if not existing:
                warning['source'] = 'rule'
                merged_warnings.append(warning)
        
        return {
            'summary': llm_result.get('summary', rule_result.get('summary', {})),
            'details': self._convert_rule_details(rule_result),
            'warnings': merged_warnings,
            'passed': merged_passed,
            'overall_comment': llm_result.get('overall_comment', ''),
            'source': 'hybrid',
            'llm_available': True
        }
    
    def _convert_rule_details(self, rule_result: Dict) -> List[Dict]:
        """将规则检查结果转换为统一格式"""
        details = []
        
        for warning in rule_result.get('warnings', []):
            details.append({
                'rule': warning['rule'],
                'status': 'warning',
                'finding': warning['issue'],
                'suggestion': warning['suggestion'],
                'source': 'rule'
            })
        
        return details


def check_file(file_path: str, use_llm: bool = True) -> Dict:
    """检查文件"""
    path = Path(file_path)
    
    if not path.exists():
        return {'error': f'文件不存在：{file_path}'}
    
    # 读取文件内容
    try:
        content = path.read_text(encoding='utf-8')
    except Exception as e:
        return {'error': f'读取文件失败：{str(e)}'}
    
    # 运行检查
    checker = HybridRequirementChecker(use_llm=use_llm)
    result = checker.run_check(content)
    result['file'] = str(path)
    
    return result


def check_text(text: str, use_llm: bool = True) -> Dict:
    """检查文本"""
    checker = HybridRequirementChecker(use_llm=use_llm)
    return checker.run_check(text)


def format_report(result: Dict) -> str:
    """格式化检查报告"""
    if 'error' in result:
        return f"❌ 错误：{result['error']}"
    
    # 如果是 merged 结果，直接使用
    if 'merged' in result:
        result = result['merged']
    
    report = []
    report.append("📋 需求规范检查报告（LLM 增强版）")
    report.append("=" * 60)
    report.append("")
    
    # 检查来源
    source = result.get('source', 'unknown')
    if source == 'hybrid':
        report.append("🔧 检查模式：规则检查 + LLM 语义分析")
    elif source == 'rule_based_only':
        report.append("🔧 检查模式：规则检查（LLM 不可用）")
    else:
        report.append(f"🔧 检查模式：{source}")
    report.append("")
    
    # 摘要
    summary = result.get('summary', {})
    warnings = result.get('warnings', [])
    passed = result.get('passed', [])
    
    report.append(f"📊 合规率：{summary.get('compliance_rate', 100)}%")
    report.append(f"✅ 通过：{summary.get('passed_count', len(passed))}")
    report.append(f"⚠️ 警告：{summary.get('warning_count', len(warnings))}")
    report.append(f"❌ 问题：{summary.get('issue_count', 0)}")
    report.append("")
    
    # 总体评价
    if result.get('overall_comment'):
        report.append("💬 总体评价:")
        report.append(f"   {result['overall_comment']}")
        report.append("")
    
    # 通过项
    if result.get('passed'):
        report.append("✅ 通过检查:")
        for item in result['passed'][:10]:  # 限制显示数量
            report.append(f"  • {item}")
        if len(result['passed']) > 10:
            report.append(f"  ... 还有 {len(result['passed']) - 10} 项")
        report.append("")
    
    # 警告项
    if result.get('warnings'):
        report.append("⚠️ 需要注意:")
        for i, item in enumerate(result['warnings'], 1):
            source_tag = "[LLM]" if item.get('source') == 'llm' else "[规则]"
            report.append(f"  {i}. 【{item['rule']}】{source_tag}")
            report.append(f"     问题：{item.get('issue', '')}")
            if item.get('suggestion'):
                report.append(f"     建议：{item['suggestion']}")
            if item.get('evidence'):
                report.append(f"     原文：\"{item['evidence']}\"")
            report.append("")
    
    return '\n'.join(report)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='需求规范检查工具（LLM 增强版）')
    parser.add_argument('input', nargs='?', help='文件路径或文本内容')
    parser.add_argument('--text', action='store_true', help='输入为文本内容')
    parser.add_argument('--no-llm', action='store_true', help='禁用 LLM 增强，仅使用规则检查')
    parser.add_argument('--api-key', type=str, help='API Key（可选，不传则使用环境变量）')
    parser.add_argument('--model', type=str, default='qwen-plus', help='模型名称（默认 qwen-plus）')
    
    args = parser.parse_args()
    
    if not args.input:
        print("用法：python check_requirement_llm.py [选项] <文件路径 | 文本>")
        print("")
        print("选项:")
        print("  --text      输入为文本内容")
        print("  --no-llm    禁用 LLM 增强")
        print("  --api-key   指定 API Key")
        print("  --model     指定模型名称")
        print("")
        print("示例:")
        print("  # 检查文件（启用 LLM）")
        print("  python check_requirement_llm.py requirement.md")
        print("")
        print("  # 检查文本（启用 LLM）")
        print("  python check_requirement_llm.py --text \"需求内容...\"")
        print("")
        print("  # 仅规则检查")
        print("  python check_requirement_llm.py --no-llm requirement.md")
        print("")
        print("  # 指定模型")
        print("  python check_requirement_llm.py --model qwen-max requirement.md")
        sys.exit(1)
    
    use_llm = not args.no_llm
    
    if args.text:
        result = check_text(args.input, use_llm=use_llm)
    else:
        result = check_file(args.input, use_llm=use_llm)
    
    # 设置 API Key 到环境变量（如果提供了）
    if args.api_key:
        os.environ['OPENAI_API_KEY'] = args.api_key
    
    print(format_report(result))
    
    # 如果有警告或问题，返回非零退出码
    if result.get('warnings') or result.get('summary', {}).get('warning_count', 0) > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
