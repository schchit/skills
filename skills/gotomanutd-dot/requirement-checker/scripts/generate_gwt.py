#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GWT 验收标准生成器（结合实际需求内容）
"""

from typing import List, Dict


def extract_keywords(content: str) -> Dict:
    """提取需求中的关键词（移除/新增/修改的功能名称）"""
    removed_items = []
    added_items = []
    modified_items = []
    
    # 简单字符串匹配方法
    lines = content.split('\n')
    for line in lines:
        # 移除类
        if '去掉' in line:
            start = line.find('去掉') + 2
            # 找后面的引号内容或名词
            rest = line[start:start+50]
            # 找第一个和第二个引号的位置
            first_quote = -1
            second_quote = -1
            for i, c in enumerate(rest):
                if c in ['"', '"', '"']:
                    if first_quote < 0:
                        first_quote = i
                    else:
                        second_quote = i
                        break
            
            if first_quote >= 0 and second_quote > first_quote:
                item = rest[first_quote+1:second_quote]
                if item.strip():  # 确保不是空字符串
                    removed_items.append(item)
        
        # 新增类
        if '新增' in line or '添加' in line:
            for kw in ['新增', '添加']:
                if kw in line:
                    start = line.find(kw) + len(kw)
                    rest = line[start:start+50]
                    if '"' in rest and '"' in rest:
                        item = rest[rest.find('"')+1:rest.find('"')]
                        added_items.append(item)
        
        # 修改类
        if '修改' in line or '优化' in line:
            for kw in ['修改', '优化']:
                if kw in line:
                    start = line.find(kw) + len(kw)
                    rest = line[start:start+50]
                    if '"' in rest and '"' in rest:
                        item = rest[rest.find('"')+1:rest.find('"')]
                        modified_items.append(item)
    
    return {
        'removed': removed_items,
        'added': added_items,
        'modified': modified_items
    }


def generate_gwt_for_file(content: str, filename: str) -> Dict:
    """
    为单个文件生成 GWT 验收标准（结合实际需求内容）
    """
    gwt_items = []
    content_lower = content.lower()
    
    # 提取关键词
    keywords = extract_keywords(content)
    removed_items = keywords['removed']
    added_items = keywords['added']
    modified_items = keywords['modified']
    
    # 2. 确定主功能点（从文件名提取）
    main_feature = filename.replace('.docx', '').replace('.md', '').replace('【', '').replace('】', '')
    
    # 规则 1: 移除类需求（结合实际功能名称）
    if any(kw in content_lower for kw in ['去掉', '移除', '删除', '不显示']) and removed_items:
        item_name = removed_items[0].strip()
        gwt_items.append({
            'given': f'用户进入{main_feature}页面',
            'when': '查看筛选条件或功能列表',
            'then': f'不应看到"{item_name}"筛选项或功能',
            'category': 'UI 验证',
            'reason': f'核心改动点，必须验证"{item_name}"已移除'
        })
        gwt_items.append({
            'given': f'用户使用{main_feature}功能',
            'when': f'执行查询或操作（不包含{item_name}相关条件）',
            'then': '功能正常工作，查询结果不受移除项影响',
            'category': '功能验证',
            'reason': f'确保移除"{item_name}"后功能完整性'
        })
        gwt_items.append({
            'given': f'用户之前使用过{item_name}筛选或功能',
            'when': '再次进入页面查看收藏的查询条件',
            'then': f'已收藏的查询条件中"{item_name}"相关条件应被忽略或提示已失效',
            'category': '兼容性验证',
            'reason': f'处理历史遗留的"{item_name}"相关配置'
        })
    
    # 规则 2: 新增类需求（结合实际功能名称）
    elif any(kw in content_lower for kw in ['新增', '添加', '增加', '支持']) and added_items:
        item_name = added_items[0].strip()
        gwt_items.append({
            'given': f'用户进入{main_feature}页面',
            'when': f'查看新增的"{item_name}"功能',
            'then': f'能看到"{item_name}"功能入口或元素',
            'category': 'UI 验证',
            'reason': f'验证新增"{item_name}"功能可见性'
        })
        gwt_items.append({
            'given': f'用户使用新增的"{item_name}"功能',
            'when': '执行相关操作',
            'then': f'"{item_name}"功能按预期工作',
            'category': '功能验证',
            'reason': f'验证新增"{item_name}"功能可用性'
        })
    
    # 规则 3: 修改类需求（结合实际功能名称）
    elif any(kw in content_lower for kw in ['修改', '优化', '调整']) and modified_items:
        item_name = modified_items[0].strip()
        gwt_items.append({
            'given': f'用户进入修改后的{main_feature}页面',
            'when': f'查看"{item_name}"相关内容',
            'then': f'能看到"{item_name}"修改后的效果',
            'category': 'UI 验证',
            'reason': f'验证"{item_name}"修改效果'
        })
    
    # 规则 4: 总是添加数据验证（结合实际业务）
    gwt_items.append({
        'given': f'{main_feature}系统正常运行',
        'when': '用户执行查询或操作',
        'then': '数据正确保存和显示，无错误',
        'category': '数据验证',
        'reason': '确保业务数据一致性'
    })
    
    # 规则 5: 异常场景（结合实际业务）
    gwt_items.append({
        'given': '网络异常或数据错误',
        'when': '用户执行操作',
        'then': '系统显示友好错误提示，不崩溃，支持重试',
        'category': '异常验证',
        'reason': '确保异常场景用户体验'
    })
    
    # 构建建议文本
    suggestion_lines = [
        '## 建议补充的验收标准（GWT 格式）',
        '',
        '**问题说明**：检测到文档中缺少 GWT（Given-When-Then）格式的验收标准。',
        '',
        f'**作为测试专家，针对"{main_feature}"需求，建议补充以下验收场景**：',
        ''
    ]
    
    for i, item in enumerate(gwt_items, 1):
        suggestion_lines.append(f'### 验收场景 {i}: {item["category"]}')
        suggestion_lines.append(f'- **Given**（给定）: {item["given"]}')
        suggestion_lines.append(f'  - 理由：{item["reason"]}')
        suggestion_lines.append(f'- **When**（当）: {item["when"]}')
        suggestion_lines.append(f'- **Then**（那么）: {item["then"]}')
        suggestion_lines.append('')
    
    return {
        'has_gwt': False,
        'gwt_items': [],
        'auto_generated': gwt_items,
        'suggestion': '\n'.join(suggestion_lines)
    }


if __name__ == '__main__':
    # 测试
    test_content = """
    企微端新客规划列表 H5 去掉"规划状态"筛选条件
    需求背景
    目前企微端新客规划列表 H5 中筛选条件包含了"规划状态"
    """
    
    result = generate_gwt_for_file(test_content, "【潍坊银行】企微端新客规划列表 H5 去掉规划状态筛选条件.docx")
    print(result['suggestion'])
