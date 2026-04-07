#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 LLM 生成 GWT 验收标准
调用阿里云 DashScope API（使用 OpenClaw 配置的模型）
"""

import os
import json
from typing import Dict, List


def call_llm_for_gwt(content: str, filename: str) -> Dict:
    """
    调用 LLM 生成 GWT 验收标准
    
    Args:
        content: 需求文档内容
        filename: 文件名
        
    Returns:
        GWT 生成结果
    """
    try:
        # 尝试使用阿里云 DashScope
        from openai import OpenAI
        
        # 获取 API Key（从环境变量或 OpenClaw 配置）
        api_key = os.getenv('DASHSCOPE_API_KEY') or os.getenv('OPENAI_API_KEY')
        base_url = os.getenv('OPENAI_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        model = os.getenv('LLM_MODEL', 'qwen-plus')
        
        if not api_key:
            return {
                'error': '未配置 API Key',
                'fallback': True,
                'message': '请设置 DASHSCOPE_API_KEY 或 OPENAI_API_KEY 环境变量'
            }
        
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        # 构建 prompt
        prompt = f"""你是一个专业的测试专家。请为以下需求文档生成 GWT（Given-When-Then）格式的验收标准。

**文件名**: {filename}

**需求内容**:
{content[:3000]}  # 限制内容长度

**要求**:
1. 作为测试专家，根据需求内容自主决定验收场景数量：
   - 简单需求（1-2 个功能点）：2-3 个场景
   - 中等需求（3-5 个功能点）：4-6 个场景
   - 复杂需求（6+ 功能点）：8+ 个场景

2. 根据业务类型选择合适的验收类别：
   - UI 验证：界面元素、显示/隐藏、布局等
   - 功能验证：业务流程、操作结果等
   - 数据验证：数据准确性、一致性等
   - 异常验证：错误处理、边界条件等
   - 兼容性验证：多设备、多浏览器等
   - 性能验证：响应时间、并发等

3. 每个验收场景必须包含：
   - Given（给定）：前置条件
   - When（当）：操作或事件
   - Then（那么）：预期结果
   - category：验收类别
   - reason：为什么需要这个场景

**输出格式**（严格 JSON）**:
```json
{{
  "auto_generated": [
    {{
      "given": "前置条件",
      "when": "操作",
      "then": "预期结果",
      "category": "UI 验证",
      "reason": "理由"
    }}
  ],
  "expert_comment": "作为测试专家，我生成了 X 个验收场景，因为...（说明决策理由）"
}}
```

请直接返回 JSON，不要其他内容。"""
        
        # 调用 LLM
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个专业的测试专家，擅长生成 GWT 验收标准。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=3000
        )
        
        # 解析响应
        response_text = response.choices[0].message.content
        
        # 提取 JSON
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(1))
        else:
            # 尝试直接解析
            result = json.loads(response_text)
        
        return {
            'success': True,
            'auto_generated': result.get('auto_generated', []),
            'expert_comment': result.get('expert_comment', ''),
            'source': 'llm'
        }
        
    except ImportError:
        return {
            'error': '需要安装 openai 库：pip install openai',
            'fallback': True
        }
    except Exception as e:
        return {
            'error': f'LLM 调用失败：{str(e)}',
            'fallback': True
        }


def generate_gwt_with_llm(content: str, filename: str) -> Dict:
    """
    生成 GWT 验收标准（优先使用 LLM，失败则使用规则）
    
    Args:
        content: 需求文档内容
        filename: 文件名
        
    Returns:
        GWT 生成结果
    """
    # 尝试使用 LLM
    llm_result = call_llm_for_gwt(content, filename)
    
    if llm_result.get('success'):
        return llm_result
    
    # LLM 失败，使用规则生成作为 fallback
    from generate_gwt import generate_gwt_for_file
    return generate_gwt_for_file(content, filename)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python3 generate_gwt_with_llm.py <文件路径>")
        sys.exit(1)
    
    # 读取文件内容
    from parse_requirement import RequirementParser
    
    parser = RequirementParser()
    result = parser.parse(sys.argv[1])
    
    if not result['success']:
        print(f"❌ 解析失败：{result.get('error')}")
        sys.exit(1)
    
    # 生成 GWT
    gwt_result = generate_gwt_with_llm(result['content'], sys.argv[1])
    
    print(json.dumps(gwt_result, ensure_ascii=False, indent=2))
