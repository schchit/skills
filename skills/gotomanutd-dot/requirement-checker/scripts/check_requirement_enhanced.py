#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
需求内容自动检查脚本（增强版）
支持原文引用、位置定位、针对性建议
"""

import re
from typing import List, Dict, Tuple


class RequirementCheckerEnhanced:
    """增强版需求检查器"""
    
    def __init__(self):
        self.warnings = []
        self.passed = []
    
    def _find_evidence(self, content: str, keywords: List[str], context_chars: int = 50) -> List[Dict]:
        """
        查找证据（原文引用）
        
        Args:
            content: 文档内容
            keywords: 关键词列表
            context_chars: 上下文长度
            
        Returns:
            证据列表，每项包含 {line, position, excerpt}
        """
        evidence_list = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for kw in keywords:
                if kw in line:
                    # 找到关键词位置
                    pos = line.find(kw)
                    # 提取上下文
                    start = max(0, pos - context_chars)
                    end = min(len(line), pos + len(kw) + context_chars)
                    excerpt = line[start:end].strip()
                    
                    evidence_list.append({
                        'line': line_num,
                        'position': pos,
                        'excerpt': excerpt,
                        'keyword': kw
                    })
        
        return evidence_list
    
    def check_exception_handling(self, content: str) -> None:
        """检查异常处理（增强版：带原文引用）"""
        # 异常场景关键词
        exception_keywords = ['异常', '错误', '失败', '超时', '网络', '校验失败', '权限不足', 
                             '为空', '无效', '重复', '冲突']
        
        # 处理说明关键词
        handling_keywords = ['处理', '提示', '返回', '日志', '回滚', '重试']
        
        # 查找异常相关内容的证据
        exception_evidence = self._find_evidence(content, exception_keywords)
        handling_evidence = self._find_evidence(content, handling_keywords)
        
        if exception_evidence and not handling_evidence:
            # 提到异常但没有处理说明
            excerpts = [e['excerpt'] for e in exception_evidence[:3]]
            lines = [str(e['line']) for e in exception_evidence[:3]]
            
            self.warnings.append({
                'rule': '异常处理',
                'issue': f'文档中提到异常相关词汇（第{", ".join(lines)}行），但未说明具体的处理方式',
                'evidence': excerpts,
                'suggestion': f'建议在"需求说明"章节后添加"异常处理"章节，针对本需求可能遇到的异常场景进行说明：\n\n1. 网络异常：查询接口超时如何处理？是否支持重试？\n2. 数据异常：如果"规划状态"数据不存在或格式错误怎么办？\n3. 权限异常：用户没有查看规划列表的权限时如何提示？\n\n每个场景需说明：\n- 用户提示：显示什么错误信息\n- 系统处理：记录日志/回滚事务等\n- 后续操作：用户是否可以重试/返回等'
            })
        elif not exception_evidence:
            # 完全没有提到异常
            self.warnings.append({
                'rule': '异常处理',
                'issue': '文档中未说明任何异常场景的处理方式',
                'evidence': [],
                'suggestion': '建议补充常见异常场景的处理说明：\n\n1. 网络异常：连接失败、超时等\n   - 用户提示："网络连接失败，请检查网络设置"\n   - 系统处理：记录日志，支持自动重试 3 次\n   - 后续操作：显示重试按钮\n\n2. 数据校验失败：必填字段为空、格式错误等\n   - 用户提示：高亮错误字段，显示具体错误信息\n   - 系统处理：阻止提交\n   - 后续操作：用户修正后重新提交\n\n3. 权限不足：未登录、无权限访问等\n   - 用户提示："您没有权限访问此功能"\n   - 系统处理：记录访问日志\n   - 后续操作：引导用户申请权限或登录'
            })
        else:
            self.passed.append('异常处理检查通过')
    
    def check_ui_details(self, content: str) -> None:
        """检查界面细节（增强版）"""
        # 界面相关关键词
        ui_keywords = ['界面', '页面', 'UI', '布局', '样式', '表单', '按钮', '输入框', '筛选', '列表']
        
        # 细节描述关键词
        detail_keywords = ['类型', '位置', '样式', '精度', '宽度', '高度', '颜色', '必填', '只读', 'px', '%']
        
        ui_evidence = self._find_evidence(content, ui_keywords)
        detail_evidence = self._find_evidence(content, detail_keywords)
        
        if ui_evidence and not detail_evidence:
            excerpts = [e['excerpt'] for e in ui_evidence[:3]]
            lines = [str(e['line']) for e in ui_evidence[:3]]
            
            self.warnings.append({
                'rule': '界面细节',
                'issue': f'检测到界面改造需求（第{", ".join(lines)}行），但未明确元素类型、位置、样式、精度',
                'evidence': excerpts,
                'suggestion': f'建议补充界面元素的详细描述。例如针对"去掉规划状态筛选条件"：\n\n1. 元素类型：筛选条件区域中的下拉选择框\n2. 位置：筛选条件区域的第 X 个位置（原"规划状态"所在位置）\n3. 样式：\n   - 宽度：200px\n   - 高度：32px\n   - 边框：1px solid #d9d9d9\n4. 交互：\n   - 默认状态：显示"请选择"\n   - 点击后：展开下拉选项\n   - 选择后：触发查询\n5. 精度：不涉及数值精度\n\n请根据实际改动补充类似描述'
            })
        elif ui_evidence:
            self.passed.append('界面细节检查通过')
    
    def check_interaction_logic(self, content: str) -> None:
        """检查交互逻辑（增强版）"""
        # 用户操作关键词
        action_keywords = ['点击', '输入', '选择', '提交', '保存', '删除', '确认', '用户操作', '查询', '筛选']
        
        # 处理逻辑关键词
        logic_keywords = ['系统处理', '处理逻辑', '校验', '判断', '如果', '则', '否则', '交互', '提示', '返回']
        
        action_evidence = self._find_evidence(content, action_keywords)
        logic_evidence = self._find_evidence(content, logic_keywords)
        
        if action_evidence and not logic_evidence:
            excerpts = [e['excerpt'] for e in action_evidence[:3]]
            lines = [str(e['line']) for e in action_evidence[:3]]
            
            self.warnings.append({
                'rule': '交互逻辑',
                'issue': f'检测到用户操作需求（第{", ".join(lines)}行），但未说明操作前后的系统处理逻辑和交互表现',
                'evidence': excerpts,
                'suggestion': f'建议补充用户操作的完整流程。例如针对"去掉规划状态筛选条件"：\n\n**操作前校验**：\n1. 检查用户是否有查看规划列表的权限\n2. 检查列表数据是否已加载\n\n**系统处理**：\n1. 用户进入页面时，筛选条件区域不显示"规划状态"选项\n2. 查询接口请求参数中不包含"规划状态"字段\n3. 查询结果返回所有状态的规划数据（包括"规划完成"）\n\n**交互表现**：\n- 成功：列表正常加载，显示所有规划数据\n- 失败：显示错误提示"加载失败，请重试"'
            })
        elif action_evidence:
            self.passed.append('交互逻辑检查通过')
    
    def check_element_completeness(self, content: str) -> None:
        """检查元素完整性（增强版）"""
        # 报表/接口/字典相关关键词
        element_keywords = ['报表', '接口', 'API', '字典', '枚举', '字段', '参数', '入参', '出参']
        
        # 完整性关键词
        completeness_keywords = ['类型', '必填', '取值', '规则', '说明', '格式', '长度']
        
        element_evidence = self._find_evidence(content, element_keywords)
        completeness_evidence = self._find_evidence(content, completeness_keywords)
        
        if element_evidence and not completeness_evidence:
            excerpts = [e['excerpt'] for e in element_evidence[:3]]
            lines = [str(e['line']) for e in element_evidence[:3]]
            
            self.warnings.append({
                'rule': '元素完整性',
                'issue': f'检测到报表/接口/字典项需求（第{", ".join(lines)}行），但未列明所有涉及的元素名称及取值规则',
                'evidence': excerpts,
                'suggestion': f'建议补充完整的元素定义。例如如果涉及查询接口：\n\n**接口名称**：【planQueryApi】\n\n**入参**：\n| 参数名 | 类型 | 必填 | 取值规则 | 说明 |\n|--------|------|------|----------|------|\n| customerId | String | 是 | 最长 32 位 | 客户号 |\n| planType | String | 否 | PLAN/PROPOSAL | 规划类型 |\n| startDate | Date | 否 | yyyy-MM-dd | 开始日期 |\n\n**出参**：\n| 参数名 | 类型 | 说明 |\n|--------|------|------|\n| code | Integer | 返回码（0=成功） |\n| data | Array | 规划列表数据 |\n\n**数据字典**：\n- planType: PLAN=正式规划，PROPOSAL=规划建议书'
            })
        elif element_evidence:
            self.passed.append('元素完整性检查通过')
    
    def check_query_association(self, content: str) -> None:
        """检查查询关联（增强版）"""
        # 查询相关关键词
        query_keywords = ['查询', '搜索', '筛选', '列表', '查看']
        
        # 历史表相关关键词
        history_keywords = ['历史', '历史表', '关联', 'JOIN', '关联规则', '查询条件']
        
        query_evidence = self._find_evidence(content, query_keywords)
        history_evidence = self._find_evidence(content, history_keywords)
        
        if query_evidence and not history_evidence:
            excerpts = [e['excerpt'] for e in query_evidence[:3]]
            lines = [str(e['line']) for e in query_evidence[:3]]
            
            self.warnings.append({
                'rule': '查询关联',
                'issue': f'检测到查询类需求（第{", ".join(lines)}行），但未说明是否关联查询历史表及关联规则',
                'evidence': excerpts,
                'suggestion': f'建议明确说明查询的数据范围。例如：\n\n**查询范围**：\n- 仅查询当前数据表（plan_table）\n- 或包含历史数据（plan_table JOIN plan_history_table）\n\n**关联规则**（如有关联）：\n- 关联条件：plan_id = history.plan_id\n- 关联类型：LEFT JOIN（保留主表所有记录）\n- 过滤条件：history.date >= DATE_SUB(NOW(), INTERVAL 3 YEAR)\n\n**性能考虑**：\n- 如果数据量大，建议添加索引\n- 考虑分页查询，每页显示 20 条'
            })
        elif query_evidence:
            self.passed.append('查询关联检查通过')
    
    def check_modification_type(self, content: str) -> None:
        """检查改造类型（增强版）"""
        # 改造类型关键词
        type_keywords = ['标准化', '标准版', '通用', '统一', '个性化', '定制', '专属', '特定客户', '本项目']
        
        # 授权控制关键词
        auth_keywords = ['授权', '权限', '控制', '角色', '可见范围', '菜单', '功能权限']
        
        type_evidence = self._find_evidence(content, type_keywords)
        auth_evidence = self._find_evidence(content, auth_keywords)
        
        if not type_evidence:
            self.warnings.append({
                'rule': '改造类型',
                'issue': '未说明是标准化改造还是个性化改造',
                'evidence': [],
                'suggestion': '建议明确说明改造类型：\n\n**标准化改造**（所有客户适用）：\n- 说明：此改动将应用到所有客户/机构\n- 影响范围：全行所有使用企微端的理财经理\n- 上线方式：统一版本发布\n\n**个性化改造**（针对特定客户）：\n- 说明：此改动仅适用于潍坊银行\n- 影响范围：潍坊银行企微端用户\n- 上线方式：通过配置开关控制\n\n同时需要说明授权控制：\n- 是否需要新增角色权限？\n- 可见范围：所有理财经理/特定机构？\n- 是否需要菜单权限控制？'
            })
        elif not auth_evidence:
            self.warnings.append({
                'rule': '授权控制',
                'issue': '未说明授权控制是否需要增加控制内容',
                'evidence': [],
                'suggestion': '建议补充授权控制说明：\n\n**角色权限**：\n- 现有角色是否支持此功能？\n- 是否需要新增角色（如"规划管理员"）？\n\n**可见范围**：\n- 所有理财经理可见？\n- 还是仅特定机构/团队可见？\n\n**菜单权限**：\n- 是否需要配置菜单权限？\n- 菜单路径：【财富管理】>【规划管理】>【规划列表】\n\n**数据权限**：\n- 是否只能查看本机构的规划？\n- 还是跨机构可见？'
            })
        else:
            self.passed.append('改造类型和授权控制检查通过')
    
    def run_check(self, content: str) -> Dict:
        """运行所有检查"""
        self.warnings = []
        self.passed = []
        
        self.check_exception_handling(content)
        self.check_ui_details(content)
        self.check_interaction_logic(content)
        self.check_element_completeness(content)
        self.check_query_association(content)
        self.check_modification_type(content)
        
        return {
            'warnings': self.warnings,
            'passed': self.passed,
            'summary': {
                'total_passed': len(self.passed),
                'total_warnings': len(self.warnings),
                'total_issues': 0,
                'compliance_rate': round(len(self.passed) / (len(self.passed) + len(self.warnings)) * 100, 1) if (len(self.passed) + len(self.warnings)) > 0 else 100
            }
        }
