#!/usr/bin/env python3
"""
九章案例库自动填充工具 - 案例生成脚本
基于AI模型和模板自动生成结构化案例
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# 添加DeepSeek API支持
try:
    import requests
except ImportError:
    print("请先安装依赖: pip install requests")
    sys.exit(1)

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

CASE_TEMPLATE = {
    "id": "",
    "category": "",
    "title": "",
    "source": "",
    "date": "",
    "location": "",
    "facts": "",
    "legal_issues": [],
    "applicable_laws": [],
    "regulatory_authority": "",
    "decision": "",
    "penalty": "",
    "compliance_insights": "",
    "risk_level": "medium",
    "tags": [],
    "related_cases": [],
    "created_at": "",
    "updated_at": ""
}

def generate_case(skill_name, category, scenario, count=1):
    """基于场景生成案例"""
    
    if not DEEPSEEK_API_KEY:
        print("❌ 请设置 DEEPSEEK_API_KEY 环境变量")
        return None
    
    prompt = f"""你是一个专业的法律案例生成专家。请基于以下信息生成{count}个结构化法律案例：

技能领域: {skill_name}
案例分类: {category}
场景描述: {scenario}

请生成符合以下JSON格式的案例:
{json.dumps(CASE_TEMPLATE, indent=2, ensure_ascii=False)}

要求:
1. id格式: 使用技能缩写+序号 (如 AI法用 ALG-XXX, 芯片法用 CHP-XXX)
2. date: 使用2023-2024年的日期
3. facts: 200-500字的案情描述
4. legal_issues: 1-5个核心法律问题
5. compliance_insights: 100-300字的合规建议
6. risk_level: high/medium/low
7. tags: 3-8个关键词

只返回JSON数组格式,不要其他说明文字。"""

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            # 提取JSON部分
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                cases = json.loads(json_match.group())
                # 添加创建时间
                now = datetime.now().strftime('%Y-%m-%d')
                for case in cases:
                    case['created_at'] = now
                    case['updated_at'] = now
                return cases
        else:
            print(f"❌ API调用失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return None

def generate_batch(skill_name, category, scenarios, output_file):
    """批量生成案例"""
    all_cases = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"正在生成第 {i}/{len(scenarios)} 个案例...")
        cases = generate_case(skill_name, category, scenario, count=1)
        if cases:
            all_cases.extend(cases)
            print(f"✅ 已生成: {cases[0]['title'][:50]}...")
    
    # 保存到文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_cases, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 批量生成完成: {len(all_cases)} 个案例已保存到 {output_file}")
    return all_cases

def main():
    if len(sys.argv) < 5:
        print("用法: python generate.py <skill_name> <category> <scenario> <count>")
        print("示例: python generate.py zhang-ai-law algorithm_filing '短视频平台算法备案违规' 5")
        sys.exit(1)
    
    skill_name = sys.argv[1]
    category = sys.argv[2]
    scenario = sys.argv[3]
    count = int(sys.argv[4])
    
    cases = generate_case(skill_name, category, scenario, count)
    
    if cases:
        print(f"\n✅ 成功生成 {len(cases)} 个案例:\n")
        for case in cases:
            print(f"ID: {case['id']}")
            print(f"标题: {case['title']}")
            print(f"风险等级: {case['risk_level']}")
            print("-" * 50)

if __name__ == '__main__':
    main()
