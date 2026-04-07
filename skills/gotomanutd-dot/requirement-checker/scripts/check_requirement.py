#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
需求内容自动检查脚本
检查 PRD/需求文档是否符合规范
"""

import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple


class RequirementChecker:
    """需求检查器"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed = []
        
    def check_flow_description(self, content: str) -> None:
        """检查 1: 多步处理/操作的需求是否有流程描述"""
        # 检测是否涉及多步操作
        multi_step_keywords = ['流程', '步骤', '依次', '然后', '接着', '第一步', '第二步', 
                               '首先', '其次', '最后', '顺序', '先后']
        
        has_multi_step = any(kw in content for kw in multi_step_keywords)
        has_flow_desc = '流程' in content or '步骤' in content or '→' in content or '->' in content
        
        if has_multi_step and not has_flow_desc:
            self.warnings.append({
                'rule': '流程描述',
                'issue': '检测到多步操作描述（如"依次"、"然后"等），但未提供清晰的流程图或步骤说明',
                'suggestion': '建议补充：\n1. 使用流程图工具（如 draw.io、Visio）绘制流程图\n2. 或用文字分步骤说明：第一步...第二步...第三步...\n3. 明确每个步骤的输入、处理、输出\n示例：\n  用户操作流程：\n  1. 用户点击【查询】按钮\n  2. 系统校验查询条件\n  3. 系统返回查询结果列表'
            })
        elif has_flow_desc:
            self.passed.append('流程描述检查通过')
    
    def check_modification_details(self, content: str) -> None:
        """检查 2a: 改造内容是否明确标注涉及的元素名称"""
        # 检测是否有括号标注的元素名称
        bracket_pattern = r'【[^】]+】|[^（（]\([^)]+\)|\[[^\]]+\]|\{[^}]+\}'
        brackets_found = re.findall(bracket_pattern, content)
        
        # 检测是否涉及改造内容
        modification_keywords = ['改造', '修改', '新增', '调整', '优化', '变更']
        has_modification = any(kw in content for kw in modification_keywords)
        
        # 检测是否有接口/交易/菜单/定时任务/清算节点等关键词
        element_keywords = ['接口', '交易', '菜单', '定时任务', '清算节点', '功能点']
        has_elements = any(kw in content for kw in element_keywords)
        
        if has_modification and has_elements and not brackets_found:
            self.warnings.append({
                'rule': '改造内容标注',
                'issue': '检测到改造内容涉及接口/交易/菜单等元素，但未使用括号【】() 等明确标注',
                'suggestion': '请用【接口名称】、【菜单名称】等形式明确标注涉及的元素'
            })
        elif brackets_found:
            self.passed.append('改造内容标注检查通过')
    
    def check_itemized_description(self, content: str) -> None:
        """检查 2b: 不同改造内容是否分项分点描述"""
        # 检测是否有分点描述
        itemized_patterns = [r'\d+[\.,]', r'[①②③④⑤]', r'[一二三四五六七八九十]+[、]', 
                            r'^\s*[-*•]\s+', r'^\s*\d+\.\s+']
        
        has_items = any(re.search(p, content, re.MULTILINE) for p in itemized_patterns)
        
        # 检测是否有多个改造内容
        modification_count = len(re.findall(r'(改造 | 修改 | 新增 | 调整)', content))
        
        if modification_count > 1 and not has_items:
            self.warnings.append({
                'rule': '分项描述',
                'issue': f'检测到{modification_count}处改造内容，但未分项分点描述',
                'suggestion': '建议将不同改造内容分项、分点描述，相同改造可合并后列举涉及的功能点'
            })
        elif has_items:
            self.passed.append('分项描述检查通过')
    
    def check_report_interface_dict(self, content: str) -> None:
        """检查 2c: 报表/接口/字典项是否列明所有元素名称及取值规则"""
        # 检测是否涉及报表/接口/字典
        report_keywords = ['报表', '统计', '清单', '导出']
        interface_keywords = ['接口', 'API', '报文', '入参', '出参']
        dict_keywords = ['字典', '枚举', '下拉', '选项', '取值']
        
        has_report = any(kw in content for kw in report_keywords)
        has_interface = any(kw in content for kw in interface_keywords)
        has_dict = any(kw in content for kw in dict_keywords)
        
        # 检查是否有详细的元素列表
        element_list_patterns = [r'元素.*?:', r'字段.*?:', r'参数.*?:', r'名称.*?:', 
                                 r'取值.*?:', r'规则.*?:', r':\s*\n\s*[-*]']
        
        has_element_list = any(re.search(p, content, re.IGNORECASE) for p in element_list_patterns)
        
        if (has_report or has_interface or has_dict) and not has_element_list:
            self.warnings.append({
                'rule': '元素完整性',
                'issue': '检测到报表/接口/字典项需求，但未列明所有涉及的元素名称及取值规则',
                'suggestion': '请列明所有字段/参数名称、类型、取值规则；数据字典要列全'
            })
        elif has_report or has_interface or has_dict:
            self.passed.append('报表/接口/字典项检查通过')
    
    def check_user_interaction(self, content: str) -> None:
        """检查 2d: 用户操作是否说明前后系统处理逻辑和交互表现"""
        # 检测是否涉及用户操作
        user_action_keywords = ['点击', '输入', '选择', '提交', '保存', '删除', '确认', '用户操作']
        
        has_user_action = any(kw in content for kw in user_action_keywords)
        
        # 检查是否有处理逻辑说明
        logic_keywords = ['系统处理', '处理逻辑', '校验', '判断', '如果', '则', '否则', '交互', '提示']
        
        has_logic = any(kw in content for kw in logic_keywords)
        
        if has_user_action and not has_logic:
            self.warnings.append({
                'rule': '交互逻辑',
                'issue': '检测到用户操作需求，但未说明操作前后的系统处理逻辑和交互表现',
                'suggestion': '请说明操作前校验、操作后系统处理、成功/失败的交互提示'
            })
        elif has_user_action:
            self.passed.append('用户交互逻辑检查通过')
    
    def check_ui_details(self, content: str) -> None:
        """检查 2e: 界面改造是否明确元素类型、位置、样式、精度"""
        # 检测是否涉及界面改造
        ui_keywords = ['界面', '页面', 'UI', '布局', '样式', '表单', '按钮', '输入框']
        
        has_ui = any(kw in content for kw in ui_keywords)
        
        # 检查是否有元素细节描述
        detail_keywords = ['类型', '位置', '样式', '精度', '宽度', '高度', '颜色', '必填', '只读']
        
        has_details = any(kw in content for kw in detail_keywords)
        
        if has_ui and not has_details:
            self.warnings.append({
                'rule': '界面细节',
                'issue': '检测到界面改造需求，但未明确元素类型、位置、样式、精度',
                'suggestion': '请写明元素类型（输入框/下拉框/按钮等）、位置、样式要求、数据精度'
            })
        elif has_ui:
            self.passed.append('界面细节检查通过')
    
    def check_algorithm_formula(self, content: str) -> None:
        """检查 2f: 算法公式需求是否写明公式和参数说明"""
        # 检测是否涉及算法/公式
        algo_keywords = ['算法', '公式', '计算', '费率', '利息', '税额', '摊销', '折旧']
        
        has_algo = any(kw in content for kw in algo_keywords)
        
        # 检查是否有公式或参数说明
        formula_patterns = [r'[=+*/]', r'参数.*?:', r'说明.*?:', r'其中:', r'变量']
        
        has_formula = any(re.search(p, content, re.IGNORECASE) for p in formula_patterns)
        
        if has_algo and not has_formula:
            self.warnings.append({
                'rule': '算法公式',
                'issue': '检测到算法/公式需求，但未写明完整公式和参数说明',
                'suggestion': '请写明完整公式，并对每个参数进行说明'
            })
        elif has_algo:
            self.passed.append('算法公式检查通过')
    
    def check_query_history(self, content: str) -> None:
        """检查 2g: 查询类需求是否说明关联查询历史表"""
        # 检测是否涉及查询
        query_keywords = ['查询', '搜索', '筛选', '列表', '查看']
        
        has_query = any(kw in content for kw in query_keywords)
        
        # 检查是否有历史表说明
        history_keywords = ['历史', '历史表', '关联', 'JOIN', '关联规则', '查询条件']
        
        has_history = any(kw in content for kw in history_keywords)
        
        if has_query and not has_history:
            self.warnings.append({
                'rule': '查询关联',
                'issue': '检测到查询类需求，但未说明是否关联查询历史表及关联规则',
                'suggestion': '请说明是否需要关联历史表；如有关联条件，需说明关联规则'
            })
        elif has_query:
            self.passed.append('查询关联检查通过')
    
    def check_exception_handling(self, content: str) -> None:
        """检查 2h: 是否说明异常场景处理"""
        # 检测是否有异常场景说明
        exception_keywords = ['异常', '错误', '失败', '超时', '网络', '校验失败', '权限不足', 
                             '为空', '无效', '重复', '冲突']
        
        has_exception_desc = any(kw in content for kw in exception_keywords)
        
        # 检测是否有处理说明
        handling_keywords = ['处理', '提示', '返回', '日志', '回滚', '重试']
        
        has_handling = any(kw in content for kw in handling_keywords)
        
        # 如果提到异常但没有处理说明
        if has_exception_desc and not has_handling:
            self.warnings.append({
                'rule': '异常处理',
                'issue': '文档中提到异常场景（如"错误"、"失败"等），但未说明具体的处理方式',
                'suggestion': '建议针对每个异常场景补充：\n1. 用户提示：显示什么错误信息\n2. 系统处理：记录日志/回滚事务/重试等\n3. 后续操作：用户是否可以重试/返回上一步等\n示例：\n  - 网络异常：提示"网络连接失败"，支持重试按钮，自动重试 3 次\n  - 数据校验失败：高亮错误字段，显示具体错误信息，阻止提交\n  - 权限不足：提示"您没有权限"，隐藏或禁用相关功能'
            })
        elif not has_exception_desc:
            self.warnings.append({
                'rule': '异常处理',
                'issue': '文档中未说明任何异常场景的处理方式',
                'suggestion': '建议补充常见异常场景的处理说明：\n1. 网络异常：连接失败、超时等\n2. 数据校验失败：必填字段为空、格式错误、重复数据等\n3. 权限不足：未登录、无权限访问等\n4. 系统异常：服务不可用、数据库错误等\n5. 业务异常：库存不足、余额不足等\n每个场景需说明：用户提示、系统处理、后续操作'
            })
        else:
            self.passed.append('异常处理检查通过')
    
    def check_modification_type(self, content: str) -> None:
        """检查 3: 是否说明标准化改造还是个性化改造，授权控制"""
        # 检测是否有改造类型说明
        standard_keywords = ['标准化', '标准版', '通用', '统一']
        custom_keywords = ['个性化', '定制', '专属', '特定客户', '本项目']
        auth_keywords = ['授权', '权限', '控制', '角色', '可见范围']
        
        has_standard = any(kw in content for kw in standard_keywords)
        has_custom = any(kw in content for kw in custom_keywords)
        has_auth = any(kw in content for kw in auth_keywords)
        
        if not has_standard and not has_custom:
            self.warnings.append({
                'rule': '改造类型',
                'issue': '未说明是标准化改造还是个性化改造',
                'suggestion': '请明确说明是标准化改造（所有客户适用）还是个性化改造（针对特定客户）'
            })
        elif not has_auth:
            self.warnings.append({
                'rule': '授权控制',
                'issue': '未说明授权控制是否需要增加控制内容',
                'suggestion': '请说明是否需要考虑授权控制（角色权限、可见范围等）'
            })
        else:
            self.passed.append('改造类型和授权控制检查通过')
    
    def check_prototype(self, content: str) -> None:
        """检查 4: 新增/修改界面是否附上原型图片或 URL"""
        # 检测是否涉及界面新增/修改
        ui_change_keywords = ['新增界面', '新增页面', '修改界面', '修改页面', '新界面', '新页面']
        
        has_ui_change = any(kw in content for kw in ui_change_keywords)
        
        # 检查是否有原型引用
        prototype_patterns = [r'原型', r'截图', r'图片', r'附件', r'http[s]?://', 
                             r'!\[.*?\]\(.*?\)', r'<img', r'见附图', '见附件']
        
        has_prototype = any(re.search(p, content, re.IGNORECASE) for p in prototype_patterns)
        
        if has_ui_change and not has_prototype:
            self.warnings.append({
                'rule': '原型附件',
                'issue': '检测到新增/修改界面需求，但未附上原型图片或 URL',
                'suggestion': '请附上原型图片、截图或原型设计 URL'
            })
        elif has_ui_change:
            self.passed.append('原型附件检查通过')
    
    def run_check(self, content: str) -> Dict:
        """运行所有检查"""
        self.check_flow_description(content)
        self.check_modification_details(content)
        self.check_itemized_description(content)
        self.check_report_interface_dict(content)
        self.check_user_interaction(content)
        self.check_ui_details(content)
        self.check_algorithm_formula(content)
        self.check_query_history(content)
        self.check_exception_handling(content)
        self.check_modification_type(content)
        self.check_prototype(content)
        
        return {
            'passed': self.passed,
            'warnings': self.warnings,
            'issues': self.issues,
            'summary': {
                'total_passed': len(self.passed),
                'total_warnings': len(self.warnings),
                'total_issues': len(self.issues),
                'compliance_rate': round(len(self.passed) / (len(self.passed) + len(self.warnings) + len(self.issues)) * 100, 1) if (len(self.passed) + len(self.warnings) + len(self.issues)) > 0 else 100
            }
        }


def check_file(file_path: str) -> Dict:
    """检查文件"""
    path = Path(file_path)
    
    if not path.exists():
        return {'error': f'文件不存在：{file_path}'}
    
    # 支持的文件类型
    supported_extensions = ['.md', '.txt', '.docx']
    
    if path.suffix.lower() not in supported_extensions:
        return {'error': f'不支持的文件类型：{path.suffix}'}
    
    # 读取文件内容
    try:
        if path.suffix.lower() == '.docx':
            # 需要 python-docx 库
            try:
                from docx import Document
                doc = Document(path)
                content = '\n'.join([para.text for para in doc.paragraphs])
            except ImportError:
                return {'error': '需要安装 python-docx: pip install python-docx'}
        else:
            content = path.read_text(encoding='utf-8')
    except Exception as e:
        return {'error': f'读取文件失败：{str(e)}'}
    
    # 运行检查
    checker = RequirementChecker()
    result = checker.run_check(content)
    result['file'] = str(path)
    
    return result


def check_text(text: str) -> Dict:
    """检查文本"""
    checker = RequirementChecker()
    return checker.run_check(text)


def format_report(result: Dict) -> str:
    """格式化检查报告"""
    if 'error' in result:
        return f"❌ 错误：{result['error']}"
    
    report = []
    report.append("📋 需求规范检查报告")
    report.append("=" * 50)
    report.append("")
    
    # 摘要
    summary = result.get('summary', {})
    report.append(f"✅ 通过项：{summary.get('total_passed', 0)}")
    report.append(f"⚠️ 警告项：{summary.get('total_warnings', 0)}")
    report.append(f"❌ 问题项：{summary.get('total_issues', 0)}")
    report.append(f"📊 合规率：{summary.get('compliance_rate', 100)}%")
    report.append("")
    
    # 通过项
    if result.get('passed'):
        report.append("✅ 通过检查:")
        for item in result['passed']:
            report.append(f"  • {item}")
        report.append("")
    
    # 警告项
    if result.get('warnings'):
        report.append("⚠️ 需要注意:")
        for item in result['warnings']:
            report.append(f"  • 【{item['rule']}】{item['issue']}")
            report.append(f"    建议：{item['suggestion']}")
        report.append("")
    
    # 问题项
    if result.get('issues'):
        report.append("❌ 必须修正:")
        for item in result['issues']:
            report.append(f"  • 【{item['rule']}】{item['issue']}")
        report.append("")
    
    return '\n'.join(report)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python check_requirement.py <文件路径 | 文本>")
        print("示例:")
        print("  python check_requirement.py requirement.md")
        print("  python check_requirement.py --text \"需求内容...\"")
        sys.exit(1)
    
    if sys.argv[1] == '--text' and len(sys.argv) > 2:
        text = ' '.join(sys.argv[2:])
        result = check_text(text)
    else:
        result = check_file(sys.argv[1])
    
    print(format_report(result))
    
    # 如果有警告或问题，返回非零退出码
    if result.get('warnings') or result.get('issues'):
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
