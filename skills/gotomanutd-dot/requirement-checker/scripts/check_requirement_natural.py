#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
需求文档检查技能（子代理执行版 + 自然语言支持）
支持自然语言指定：
- 检查哪个需求文档（具体文件名）
- 检查什么日期的文档（按日期筛选）
- 检查最新的几个文档（按时间排序）
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta


def load_config() -> dict:
    """加载配置文件"""
    config_path = Path(__file__).parent / 'config.json'
    
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


def save_config(config: dict) -> bool:
    """保存配置文件"""
    config_path = Path(__file__).parent / 'config.json'
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def parse_natural_language_input(user_input: str, config: dict) -> dict:
    """
    解析自然语言输入，确定检查范围
    
    Args:
        user_input: 用户输入的自然语言
        config: 配置字典
        
    Returns:
        {
            'mode': 'all' | 'file' | 'date' | 'latest',
            'input_dir': str,
            'output_dir': str,
            'file_pattern': str,  # 文件名模式
            'date_filter': str,   # 日期过滤
            'limit': int,         # 数量限制
            'generate_summary': bool
        }
    """
    result = {
        'mode': 'all',
        'input_dir': config.get('directories', {}).get('input', ''),
        'output_dir': config.get('directories', {}).get('output', './requirement_reports'),
        'file_pattern': '*',
        'date_filter': None,
        'limit': None,
        'generate_summary': '汇总' in user_input or 'summary' in user_input.lower()
    }
    
    # 1. 检查是否指定具体文件
    file_patterns = [
        r'检查 (.+?\.docx)',
        r'检查 (.+?\.md)',
        r'检查 (.+?\.txt)',
        r'检查 (.+?\.pdf)',
        r'文件 [":：]?\s*(.+?\.(?:docx|md|txt|pdf))',
    ]
    
    for pattern in file_patterns:
        match = re.search(pattern, user_input)
        if match:
            result['mode'] = 'file'
            result['file_pattern'] = match.group(1).strip()
            return result
    
    # 2. 检查是否指定日期
    date_patterns = [
        (r'今天', datetime.now().strftime('%Y-%m-%d')),
        (r'昨天', (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')),
        (r'前天', (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')),
        (r'(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})[日号]?', lambda m: f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"),
        (r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', lambda m: f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"),
        (r'本周', 'week'),
        (r'上周', 'last_week'),
        (r'本月', 'month'),
        (r'上月', 'last_month'),
    ]
    
    for pattern, date_value in date_patterns:
        match = re.search(pattern, user_input)
        if match:
            result['mode'] = 'date'
            if callable(date_value):
                result['date_filter'] = date_value(match)
            else:
                result['date_filter'] = date_value
            break
    
    # 3. 检查是否指定最新 N 个
    latest_patterns = [
        r'最新 (\d+) 个',
        r'最近 (\d+) 个',
        r'最新的 (\d+) 个',
        r'最近的 (\d+) 个',
        r'最新 (\d+) 份',
        r'最近 (\d+) 份',
    ]
    
    for pattern in latest_patterns:
        match = re.search(pattern, user_input)
        if match:
            result['mode'] = 'latest'
            result['limit'] = int(match.group(1))
            break
    
    # 4. 检查是否指定文件名关键词
    keyword_patterns = [
        r'名字?包含 (.+?) 的',
        r'文件名?有 (.+?) 的',
        r'关于 (.+?) 的',
    ]
    
    for pattern in keyword_patterns:
        match = re.search(pattern, user_input)
        if match:
            result['mode'] = 'file'
            result['file_pattern'] = f"*{match.group(1).strip()}*"
            break
    
    return result


def find_files_by_criteria(input_dir: str, criteria: dict) -> list:
    """
    根据条件查找文件
    
    Args:
        input_dir: 输入目录
        criteria: 查找条件
        
    Returns:
        文件路径列表
    """
    input_path = Path(input_dir)
    
    if not input_path.exists():
        return []
    
    files = []
    
    # 模式 1：所有文件
    if criteria['mode'] == 'all':
        for ext in ['.docx', '.md', '.txt', '.pdf']:
            files.extend(input_path.rglob(f'*{ext}'))
    
    # 模式 2：指定文件
    elif criteria['mode'] == 'file':
        pattern = criteria['file_pattern']
        if '*' in pattern or '?' in pattern:
            # 通配符模式
            for ext in ['.docx', '.md', '.txt', '.pdf']:
                files.extend(input_path.rglob(f'{pattern}{ext}' if not pattern.endswith(ext) else pattern))
        else:
            # 精确文件名
            file_path = input_path / pattern
            if file_path.exists():
                files.append(file_path)
            else:
                # 尝试模糊匹配
                for ext in ['.docx', '.md', '.txt', '.pdf']:
                    matches = list(input_path.rglob(f'*{pattern}{ext}'))
                    files.extend(matches)
    
    # 模式 3：按日期筛选
    elif criteria['mode'] == 'date':
        date_filter = criteria['date_filter']
        
        if date_filter in ['week', 'last_week', 'month', 'last_month']:
            # 计算日期范围
            now = datetime.now()
            if date_filter == 'week':
                start_date = now - timedelta(days=now.weekday())
                end_date = now
            elif date_filter == 'last_week':
                start_date = now - timedelta(days=now.weekday() + 7)
                end_date = start_date + timedelta(days=6)
            elif date_filter == 'month':
                start_date = now.replace(day=1)
                end_date = now
            else:  # last_month
                if now.month == 1:
                    start_date = datetime(now.year - 1, 12, 1)
                    end_date = datetime(now.year - 1, 12, 31)
                else:
                    start_date = datetime(now.year, now.month - 1, 1)
                    end_date = datetime(now.year, now.month - 1, 
                                       (datetime(now.year, now.month, 1) - timedelta(days=1)).day)
        else:
            # 具体日期
            start_date = end_date = datetime.strptime(date_filter, '%Y-%m-%d')
        
        # 查找文件
        for ext in ['.docx', '.md', '.txt', '.pdf']:
            for file_path in input_path.rglob(f'*{ext}'):
                # 从文件名或修改时间判断日期
                file_date = None
                
                # 尝试从文件名提取日期
                date_match = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', file_path.name)
                if date_match:
                    try:
                        file_date = datetime.strptime(date_match.group(1).replace('/', '-'), '%Y-%m-%d')
                    except:
                        pass
                
                # 使用文件修改时间
                if not file_date:
                    file_date = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                # 判断是否在日期范围内
                if start_date <= file_date <= end_date:
                    files.append(file_path)
    
    # 模式 4：最新 N 个
    elif criteria['mode'] == 'latest':
        for ext in ['.docx', '.md', '.txt', '.pdf']:
            files.extend(input_path.rglob(f'*{ext}'))
        
        # 按修改时间排序，取最新 N 个
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        limit = criteria.get('limit', 5)
        files = files[:limit]
    
    # 过滤隐藏文件和临时文件
    files = [f for f in files if not f.name.startswith('.') and not f.name.startswith('~')]
    
    return sorted(files)


def check_requirement(input_path: str, output_path: str, generate_summary: bool = False) -> dict:
    """
    检查需求文档（通过子代理执行）
    """
    import sys
    sys.path.insert(0, '/Users/lifan/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw')
    try:
        from openclaw import sessions_spawn
    except ImportError:
        return {'error': '无法导入 openclaw 模块，请在 OpenClaw 环境中运行'}
    
    path = Path(input_path)
    if not path.exists():
        return {'error': f'路径不存在：{input_path}'}
    
    if path.is_dir():
        task = f"""请使用 requirement-checker 技能批量检查需求文档：

**输入目录**: {input_path}
**输出目录**: {output_path}
**汇总报告**: {'需要' if generate_summary else '不需要'}

请执行以下命令：
```bash
python3 ~/.openclaw/workspace/skills/requirement-checker/scripts/batch_check_ai.py {'--summary' if generate_summary else ''} -o {output_path} {input_path}
```

执行完毕后，请总结：
1. 检查了多少个文件
2. 平均合规率
3. 发现的主要问题
4. GWT 验收标准生成情况
"""
    else:
        task = f"""请使用 requirement-checker 技能检查需求文档：

**文件**: {input_path}
**输出目录**: {output_path}
**汇总报告**: {'需要' if generate_summary else '不需要'}

请执行以下命令：
```bash
python3 ~/.openclaw/workspace/skills/requirement-checker/scripts/batch_check_ai.py {'--summary' if generate_summary else ''} -o {output_path} {path.parent}
```

执行完毕后，请总结：
1. 文件合规率
2. 发现的主要问题
3. GWT 验收标准生成情况
"""
    
    try:
        result = sessions_spawn({
            runtime: "subagent",
            task: task,
            timeoutSeconds: 600,
            cleanup: "delete"
        })
        
        if result and 'response' in result:
            return {
                'success': True,
                'response': result['response'],
                'input_path': input_path,
                'output_path': output_path,
                'generate_summary': generate_summary
            }
        else:
            return {
                'success': False,
                'error': '子代理未返回结果'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'调用子代理失败：{str(e)}'
        }


def main():
    """主函数 - 自然语言支持"""
    # 加载配置
    config = load_config()
    
    # 获取用户输入（从命令行参数或环境变量）
    if len(sys.argv) > 1:
        user_input = ' '.join(sys.argv[1:])
    else:
        # 从环境变量读取（智能体调用时）
        user_input = sys.stdin.read().strip() if not sys.stdin.isatty() else ""
    
    # 解析自然语言输入
    criteria = parse_natural_language_input(user_input, config)
    
    # 检查目录配置
    if not criteria['input_dir']:
        print("⚠️  未配置输入目录，请先设置：")
        print("   python3 check_requirement.py --set-dir")
        sys.exit(1)
    
    # 查找文件
    files = find_files_by_criteria(criteria['input_dir'], criteria)
    
    if not files:
        print("❌ 未找到符合条件的需求文档")
        print()
        print(f"查找条件：")
        print(f"  目录：{criteria['input_dir']}")
        print(f"  模式：{criteria['mode']}")
        if criteria['file_pattern'] != '*':
            print(f"  文件名：{criteria['file_pattern']}")
        if criteria['date_filter']:
            print(f"  日期：{criteria['date_filter']}")
        if criteria['limit']:
            print(f"  数量：最新{criteria['limit']}个")
        sys.exit(1)
    
    print(f"📁 找到 {len(files)} 个需求文档")
    for i, f in enumerate(files[:5], 1):
        print(f"  {i}. {f.name}")
    if len(files) > 5:
        print(f"  ... 还有 {len(files) - 5} 个")
    print()
    
    # 执行检查
    print(f"🤖 正在调用子代理检查需求文档...")
    print(f"   输入目录：{criteria['input_dir']}")
    print(f"   输出目录：{criteria['output_dir']}")
    print(f"   汇总报告：{'需要' if criteria['generate_summary'] else '不需要'}")
    print(f"   检查范围：{criteria['mode']} 模式")
    print()
    
    # 如果是单个文件，直接检查
    if len(files) == 1:
        result = check_requirement(str(files[0]), criteria['output_dir'], criteria['generate_summary'])
    else:
        # 多个文件，检查整个目录
        result = check_requirement(criteria['input_dir'], criteria['output_dir'], criteria['generate_summary'])
    
    if result.get('success'):
        print("✅ 检查完成！")
        print()
        print(result.get('response', '无响应内容'))
        print()
        print(f"📁 报告已保存到：{criteria['output_dir']}")
    else:
        print(f"❌ 检查失败：{result.get('error', '未知错误')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
