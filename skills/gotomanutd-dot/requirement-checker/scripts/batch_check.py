#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
需求文档批量检查工具（智能决策 + LLM 生成 GWT）
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# 导入解析器和检查器
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))  # 添加父目录以导入 generate_gwt_llm
from parse_requirement import RequirementParser
from check_requirement_agent import AgentRequirementChecker

# 使用 LLM 智能检查器
try:
    from check_with_llm import check_with_llm, get_openclaw_config
    USE_LLM_CHECKER = get_openclaw_config() is not None
    if USE_LLM_CHECKER:
        print("✅ 已启用 LLM 智能检查器（通用规则 + 具体内容生成）")
except ImportError as e:
    print(f"⚠️  LLM 检查器不可用：{e}")
    USE_LLM_CHECKER = False

# 导入 LLM 生成器（使用 OpenClaw 配置）
try:
    from generate_gwt_llm import generate_gwt_with_llm_batch, get_openclaw_config
    openclaw_config = get_openclaw_config()
    HAS_LLM = openclaw_config is not None
    if HAS_LLM:
        print(f"✅ 已加载 OpenClaw LLM 配置：{openclaw_config['base_url']}")
        print(f"⚠️  注意：LLM 调用可能较慢，请耐心等待（约 30-60 秒）")
except ImportError as e:
    print(f"⚠️  导入 LLM 生成器失败：{e}")
    HAS_LLM = False


def load_config(config_path: str = None) -> Dict:
    """加载配置文件"""
    if config_path is None:
        config_path = Path(__file__).parent.parent / 'config.json'
    else:
        config_path = Path(config_path)
    
    if not config_path.exists():
        print(f"⚠️  配置文件不存在：{config_path}")
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ 已加载配置文件：{config_path}")
        return config
    except Exception as e:
        print(f"⚠️  配置文件加载失败：{e}")
        return {}


class BatchRequirementChecker:
    """批量需求检查器"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.parser = RequirementParser()
        self.checker = AgentRequirementChecker()
        
        self.supported_extensions = {
            '.docx', '.md', '.markdown', '.txt', 
            '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.webp',
            '.html', '.htm'
        }
        
        self.stats = {
            'total_files': 0,
            'success_count': 0,
            'warning_count': 0,
            'issue_count': 0,
            'files_with_gwt': 0,
            'files_without_gwt': 0,
            'start_time': None,
            'end_time': None
        }
        
        self.results = []
    
    def scan_directory(self, input_dir: str, recursive: bool = True) -> List[Path]:
        """扫描目录中的所有需求文件"""
        input_path = Path(input_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"目录不存在：{input_dir}")
        
        files = []
        if recursive:
            for ext in self.supported_extensions:
                files.extend(input_path.rglob(f'*{ext}'))
        else:
            for ext in self.supported_extensions:
                files.extend(input_path.glob(f'*{ext}'))
        
        files = [f for f in files if not f.name.startswith('.') and not f.name.startswith('~')]
        return sorted(files)
    
    def check_file(self, file_path: Path) -> Dict:
        """检查单个文件（使用 LLM 智能检查）"""
        try:
            # 解析文件获取内容
            parse_result = self.parser.parse(str(file_path))
            
            if not parse_result['success']:
                return {
                    'success': False,
                    'file': str(file_path),
                    'error': parse_result.get('error', '解析失败')
                }
            
            content = parse_result['content']
            
            # 使用 LLM 智能检查
            if USE_LLM_CHECKER:
                print(f"  🤖 LLM 智能检查中...")
                llm_result = check_with_llm(content, str(file_path))
                
                # LLM 返回的结果直接作为 pre_check
                pre_check = {
                    'summary': llm_result.get('summary', {}),
                    'warnings': llm_result.get('warnings', []),
                    'passed': llm_result.get('passed', []),
                    'gwt_analysis': llm_result.get('gwt_acceptance', {})
                }
            else:
                # 降级到规则检查
                pre_check = self.checker.rule_checker.run_check(content)
            
            # 统计信息
            summary = pre_check.get('summary', {})
            
            self.stats['success_count'] += 1
            if summary.get('warning_count', 0) > 0:
                self.stats['warning_count'] += 1
            if summary.get('issue_count', 0) > 0:
                self.stats['issue_count'] += 1
            
            return {
                'success': True,
                'file': str(file_path),
                'result': {
                    'parse_result': parse_result,
                    'pre_check': pre_check
                },
                'content': content
            }
                
        except Exception as e:
            return {
                'success': False,
                'file': str(file_path),
                'error': str(e)
            }
    
    def generate_gwt_batch(self, use_llm: bool = True) -> None:
        """
        批量生成 GWT 验收标准（LLM 检查已包含 GWT 生成）
        
        如果使用 LLM 检查器，GWT 已经在 check_file 中生成，无需单独处理
        """
        # 如果使用 LLM 检查器，GWT 已经生成
        if USE_LLM_CHECKER:
            print("\n✅ LLM 智能检查已包含 GWT 生成，无需单独处理")
            return
        
        # 否则使用规则生成
        # ...（保留原有规则生成逻辑）
    
    def _generate_gwt_for_single_file(self, file_data: Dict) -> Dict:
        """为单个文件生成 GWT（规则生成）"""
        from generate_gwt import generate_gwt_for_file
        return generate_gwt_for_file(file_data['content'], file_data['filename'])
    
    def _call_llm_for_gwt_batch(self, files_for_gwt: List[Dict]) -> List[Dict]:
        """调用 LLM 批量生成 GWT（使用 OpenClaw 配置）"""
        if not HAS_LLM:
            print("⚠️  LLM 不可用，降级到规则生成")
            return self._generate_gwt_with_rules(files_for_gwt)
        
        try:
            print(f"   使用模型：glm-5")
            # 使用新的 LLM 生成器
            gwt_results = generate_gwt_with_llm_batch(files_for_gwt, model="glm-5")
            return gwt_results
        except Exception as e:
            print(f"⚠️  LLM 调用失败：{e}，降级到规则生成")
            return self._generate_gwt_with_rules(files_for_gwt)
    
    def _generate_gwt_with_rules(self, files_for_gwt: List[Dict]) -> List[Dict]:
        """使用规则生成 GWT（fallback）"""
        from generate_gwt import generate_gwt_for_file
        
        results = []
        for file_data in files_for_gwt:
            gwt_result = generate_gwt_for_file(file_data['content'], file_data['filename'])
            results.append({
                'filename': file_data['filename'],
                'auto_generated': gwt_result.get('auto_generated', []),
                'expert_comment': '基于规则生成（LLM 不可用）'
            })
        
        return results
    
    def _build_gwt_suggestion(self, gwt_result: Dict) -> str:
        """构建 GWT 建议文本"""
        auto_generated = gwt_result.get('auto_generated', [])
        
        if not auto_generated:
            return "未生成验收场景"
        
        lines = [
            '## 建议补充的验收标准（GWT 格式）',
            '',
            '**问题说明**：检测到文档中缺少 GWT（Given-When-Then）格式的验收标准。',
            '',
            gwt_result.get('expert_comment', '**作为测试专家，建议补充以下验收场景**：'),
            ''
        ]
        
        for i, item in enumerate(auto_generated, 1):
            lines.append(f'### 验收场景 {i}: {item.get("category", "验证")}')
            lines.append(f'- **Given**（给定）: {item.get("given", "")}')
            lines.append(f'  - 理由：{item.get("reason", "")}')
            lines.append(f'- **When**（当）: {item.get("when", "")}')
            lines.append(f'- **Then**（那么）: {item.get("then", "")}')
            lines.append('')
        
        return '\n'.join(lines)
    
    def generate_individual_report(self, file_result: Dict) -> str:
        """生成单个文件的检查报告"""
        if not file_result['success']:
            return f"""# ❌ 检查失败：{file_result['file']}

**错误**: {file_result.get('error', '未知错误')}

**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**结论**: 无法检查，请修复错误后重新提交
"""
        
        result = file_result['result']
        parse_result = result.get('parse_result', {})
        pre_check = result.get('pre_check', {})
        
        metadata = parse_result.get('metadata', {})
        summary = pre_check.get('summary', {})
        gwt_analysis = pre_check.get('gwt_analysis', {})
        
        # 计算评分和结论
        score_result = self.calculate_score_and_conclusion(pre_check)
        
        report = []
        report.append("# 📋 需求规范检查报告")
        report.append("")
        report.append(f"**文件**: {metadata.get('source', file_result['file'])}")
        report.append(f"**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 评分和结论
        report.append("## 🎯 检查结论")
        report.append("")
        
        conclusion = score_result['conclusion']
        score = score_result['score']
        
        if conclusion == '通过':
            report.append(f"**结论**: ✅ **通过**")
        elif conclusion == '部分通过':
            report.append(f"**结论**: ⚠️ **部分通过**")
        else:
            report.append(f"**结论**: ❌ **打回**")
        
        report.append("")
        report.append(f"**评分**: **{score}/100**")
        report.append("")
        report.append(f"**理由**: {score_result['reason']}")
        report.append("")
        
        # 摘要
        report.append("## 📊 检查摘要")
        report.append("")
        report.append(f"- **合规率**: {summary.get('compliance_rate', 100)}%")
        # 支持 LLM 返回的字段名和规则检查的字段名
        report.append(f"- **通过项**: {summary.get('passed_count', summary.get('total_passed', 0))}")
        report.append(f"- **警告项**: {summary.get('warning_count', summary.get('total_warnings', 0))}")
        report.append(f"- **问题项**: {summary.get('issue_count', 0)}")
        has_gwt = gwt_analysis.get('auto_generated', [])
        report.append(f"- **GWT 验收标准**: {'✅ 已生成' if has_gwt else '❌ 缺失'}")
        report.append("")
        
        # GWT 验收标准
        report.append("## 📋 GWT 验收标准检查")
        report.append("")
        if gwt_analysis.get('has_gwt'):
            report.append("✅ 文档已包含 GWT 格式的验收标准")
        elif has_gwt:
            report.append("⚠️ 文档缺少 GWT 格式的验收标准")
            report.append("")
            report.append("建议补充的验收标准:")
            report.append("")
            report.append(gwt_analysis.get('suggestion', gwt_analysis.get('expert_comment', '无')))
        else:
            report.append("⚠️ 文档缺少 GWT 格式的验收标准")
            report.append("")
            report.append("建议补充的验收标准:")
            report.append("")
            report.append(gwt_analysis.get('suggestion', gwt_analysis.get('expert_comment', '无')))
        report.append("")
        
        # 详细问题
        warnings = pre_check.get('warnings', [])
        if warnings:
            report.append("## ⚠️ 需要注意的问题")
            report.append("")
            for i, warning in enumerate(warnings, 1):
                report.append(f"### {i}. 【{warning['rule']}】")
                report.append("")
                report.append(f"**问题说明**:")
                report.append(f"{warning['issue']}")
                report.append("")
                report.append(f"**优化建议**:")
                report.append(f"{warning['suggestion']}")
                report.append("")
        
        # 通过项
        passed = pre_check.get('passed', [])
        if passed:
            report.append("## ✅ 通过检查")
            report.append("")
            for item in passed:
                report.append(f"- {item}")
            report.append("")
        
        return "\n".join(report)
    
    def calculate_score_and_conclusion(self, pre_check: Dict) -> Dict:
        """计算评分和结论"""
        summary = pre_check.get('summary', {})
        gwt_analysis = pre_check.get('gwt_analysis', {})
        
        # 支持 LLM 返回的字段名和规则检查的字段名
        compliance_rate = summary.get('compliance_rate', 100)
        warning_count = summary.get('warning_count', summary.get('total_warnings', 0))
        issue_count = summary.get('issue_count', 0)
        
        # 计算评分
        score = compliance_rate
        if not gwt_analysis.get('auto_generated'):
            score -= 15
        if issue_count > 0:
            score -= issue_count * 15
        score -= warning_count * 5
        score = max(0, min(100, score))
        score = round(score, 1)
        
        # 判断结论
        if issue_count > 0:
            conclusion = '打回'
            reason = f'存在{issue_count}个严重问题，需要重新分析并修改后再次提交检查'
        elif score >= 80:
            conclusion = '通过'
            reason = '文档质量良好，可以进入评审和开发阶段'
        elif score >= 60:
            conclusion = '部分通过'
            reason = f'存在{warning_count}个需要改进的问题，建议快速修改后无需再次检查，可直接进入评审'
        else:
            conclusion = '打回'
            reason = f'评分低于 60 分（当前{score}分），文档质量不达标，需要重新分析并修改后再次提交检查'
        
        return {
            'score': score,
            'conclusion': conclusion,
            'reason': reason
        }
    
    def generate_summary_report(self) -> str:
        """生成汇总报告"""
        report = []
        report.append("# 📊 需求文档批量检查汇总报告")
        report.append("")
        report.append(f"**检查时间**: {self.stats['start_time']} - {self.stats['end_time']}")
        report.append("")
        
        # 计算总体评分
        total_score = 0
        pass_count = 0
        partial_pass_count = 0
        reject_count = 0
        
        for result in self.results:
            if result['success']:
                pre_check = result['result'].get('pre_check', {})
                score_result = self.calculate_score_and_conclusion(pre_check)
                total_score += score_result['score']
                
                if score_result['conclusion'] == '通过':
                    pass_count += 1
                elif score_result['conclusion'] == '部分通过':
                    partial_pass_count += 1
                else:
                    reject_count += 1
        
        avg_score = round(total_score / self.stats['success_count'], 1) if self.stats['success_count'] > 0 else 0
        
        # 总体结论
        if reject_count > 0:
            overall_conclusion = f"❌ 有{reject_count}个文档需要打回，建议优先处理"
        elif partial_pass_count > self.stats['success_count'] * 0.5:
            overall_conclusion = f"⚠️ 超过半数文档部分通过，建议统一改进"
        else:
            overall_conclusion = f"✅ 整体质量良好，可以进入评审阶段"
        
        # 统计信息
        report.append("## 📈 统计信息")
        report.append("")
        report.append(f"- **总文件数**: {self.stats['total_files']}")
        report.append(f"- **检查成功**: {self.stats['success_count']}")
        report.append(f"- **存在警告**: {self.stats['warning_count']}")
        report.append(f"- **存在问题**: {self.stats['issue_count']}")
        report.append(f"- **已生成 GWT**: {self.stats['files_with_gwt']}")
        report.append(f"- **缺少 GWT**: {self.stats['files_without_gwt']}")
        report.append("")
        
        # 总体评分
        report.append("## 🎯 总体评分")
        report.append("")
        report.append(f"**平均评分**: **{avg_score}/100**")
        report.append("")
        report.append(f"**通过**: {pass_count} 个 ✅")
        report.append(f"**部分通过**: {partial_pass_count} 个 ⚠️")
        report.append(f"**打回**: {reject_count} 个 ❌")
        report.append("")
        report.append(f"**总体结论**: {overall_conclusion}")
        report.append("")
        
        # 文件列表
        report.append("## 📁 文件检查详情")
        report.append("")
        report.append("| 文件名 | 评分 | 结论 | 合规率 | 警告 | 问题 | GWT | 报告 |")
        report.append("|--------|------|------|--------|------|------|-----|------|")
        
        for result in self.results:
            filename = Path(result['file']).name
            
            if result['success']:
                pre_check = result['result'].get('pre_check', {})
                summary = pre_check.get('summary', {})
                score_result = self.calculate_score_and_conclusion(pre_check)
                
                score = score_result['score']
                conclusion = score_result['conclusion']
                
                if conclusion == '通过':
                    conclusion_icon = '✅'
                elif conclusion == '部分通过':
                    conclusion_icon = '⚠️'
                else:
                    conclusion_icon = '❌'
                
                compliance = summary.get('compliance_rate', 100)
                warnings = summary.get('total_warnings', 0)
                issues = summary.get('issue_count', 0)
                has_gwt = '✅' if pre_check.get('gwt_analysis', {}).get('auto_generated') else '❌'
                
                report_name = f"{Path(result['file']).stem}_report.md"
                report_link = f"[查看](./{report_name})"
                
                report.append(f"| {filename} | {score} | {conclusion_icon} {conclusion} | {compliance}% | {warnings} | {issues} | {has_gwt} | {report_link} |")
            else:
                report.append(f"| {filename} | N/A | ❌ 失败 | N/A | N/A | N/A | N/A | ❌ 失败 |")
        
        report.append("")
        
        return "\n".join(report)
    
    def run(self, input_dir: str, recursive: bool = True, use_llm: bool = None) -> None:
        """执行批量检查"""
        print(f"🔍 开始扫描目录：{input_dir}")
        print()
        
        self.stats['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 扫描文件
        files = self.scan_directory(input_dir, recursive)
        self.stats['total_files'] = len(files)
        
        print(f"📁 找到 {len(files)} 个需求文件")
        print()
        
        # 智能决策是否使用 LLM
        if use_llm is None:
            if len(files) <= 5:
                use_llm = True
                print("🤖 文件数 ≤ 5，自动启用 LLM 生成 GWT 验收标准")
            elif len(files) <= 20:
                print(f"⚠️  文件数 {len(files)} 个（>5），是否启用 LLM 生成 GWT？")
                print("   LLM 生成会更智能，但每个文件需要 5-10 秒")
                print()
                response = input("   是否启用？[y/N]: ").strip().lower()
                use_llm = response in ['y', 'yes']
            else:
                use_llm = False
                print(f"⚡ 文件数 {len(files)} 个（>20），为节省时间已自动跳过 LLM 生成")
                print("   如需启用，请使用：python3 batch_check.py --use-llm")
            print()
        
        # 逐个检查（预检查）
        for i, file_path in enumerate(files, 1):
            print(f"[{i}/{len(files)}] 检查：{file_path.name}")
            
            result = self.check_file(file_path)
            self.results.append(result)
            
            if result['success']:
                print(f"  ✅ 预检查完成")
            else:
                print(f"  ❌ 检查失败：{result.get('error', '未知错误')}")
        
        # 批量生成 GWT
        self.generate_gwt_batch(use_llm=use_llm)
        
        # 记录结束时间
        self.stats['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print()
        print("📝 生成报告...")
        
        # 生成 individual 报告
        for result in self.results:
            if result['success']:
                report_md = self.generate_individual_report(result)
                report_path = self.output_dir / f"{Path(result['file']).stem}_report.md"
                report_path.write_text(report_md, encoding='utf-8')
                print(f"  ✅ 生成报告：{report_path.name}")
        
        # 生成汇总报告
        summary_md = self.generate_summary_report()
        summary_path = self.output_dir / "00_汇总报告.md"
        summary_path.write_text(summary_md, encoding='utf-8')
        print(f"  ✅ 生成汇总报告：{summary_path.name}")
        
        # 生成 JSON 结果
        json_data = {
            'stats': self.stats,
            'results': []
        }
        
        for result in self.results:
            json_result = {
                'file': result['file'],
                'success': result['success']
            }
            
            if result['success']:
                pre_check = result['result'].get('pre_check', {})
                json_result['summary'] = pre_check.get('summary', {})
                json_result['gwt'] = pre_check.get('gwt_analysis', {})
                score_result = self.calculate_score_and_conclusion(pre_check)
                json_result['score'] = score_result['score']
                json_result['conclusion'] = score_result['conclusion']
            else:
                json_result['error'] = result.get('error', '')
            
            json_data['results'].append(json_result)
        
        json_path = self.output_dir / "检查结果.json"
        json_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"  ✅ 生成 JSON 结果：{json_path.name}")
        
        print()
        print("=" * 60)
        print("✅ 批量检查完成！")
        print("=" * 60)
        print()
        print(f"📊 统计信息:")
        print(f"  - 总文件数：{self.stats['total_files']}")
        print(f"  - 检查成功：{self.stats['success_count']}")
        print(f"  - 存在警告：{self.stats['warning_count']}")
        print(f"  - 存在问题：{self.stats['issue_count']}")
        print()
        print(f"📁 报告目录：{self.output_dir}")
        print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='需求文档批量检查工具（智能决策 + LLM 生成 GWT）')
    parser.add_argument('input_dir', nargs='?', default=None,
                       help='输入目录（包含需求文件的目录，可选，默认从 config.json 读取）')
    parser.add_argument('-o', '--output-dir', default=None,
                       help='报告输出目录（可选，默认从 config.json 读取）')
    parser.add_argument('--no-recursive', action='store_true',
                       help='不递归扫描子目录')
    parser.add_argument('--open', action='store_true',
                       help='检查完成后打开汇总报告')
    parser.add_argument('--config', default=None,
                       help='配置文件路径（默认：../config.json）')
    parser.add_argument('--use-llm', action='store_true',
                       help='强制启用 LLM 生成 GWT')
    parser.add_argument('--no-llm', action='store_true',
                       help='禁用 LLM，仅使用规则生成')
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 使用配置文件中的默认值
    input_dir = args.input_dir or config.get('directories', {}).get('input')
    output_dir = args.output_dir or config.get('directories', {}).get('output')
    recursive = not args.no_recursive and config.get('check_settings', {}).get('recursive', True)
    auto_open = args.open or config.get('check_settings', {}).get('auto_open_report', False)
    
    if not input_dir:
        print("❌ 错误：未指定输入目录")
        print()
        print("用法:")
        print("  1. 命令行指定：python3 batch_check.py /path/to/input/")
        print("  2. 配置文件：编辑 config.json 中的 directories.input")
        print()
        parser.print_help()
        sys.exit(1)
    
    if not output_dir:
        output_dir = './requirement_reports'
    
    # 确定是否使用 LLM
    if args.use_llm:
        use_llm = True
    elif args.no_llm:
        use_llm = False
    else:
        use_llm = None  # 智能决策
    
    # 创建批量检查器
    batch_checker = BatchRequirementChecker(output_dir)
    
    # 执行批量检查
    batch_checker.run(input_dir, recursive=recursive, use_llm=use_llm)
    
    # 打开汇总报告
    if auto_open:
        import webbrowser
        summary_path = Path(output_dir) / "00_汇总报告.md"
        if summary_path.exists():
            webbrowser.open(f"file://{summary_path.absolute()}")


if __name__ == '__main__':
    main()
