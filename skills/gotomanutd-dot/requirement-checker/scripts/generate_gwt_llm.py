#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 LLM 生成 GWT 验收标准
直接使用 requests 调用 API（避免 OpenAI 库超时问题）
"""

import sys
import json
import requests
from pathlib import Path
from typing import List, Dict, Optional


def get_openclaw_config() -> Optional[Dict]:
    """读取 OpenClaw 配置文件"""
    config_path = Path.home() / '.openclaw' / 'openclaw.json'
    
    if not config_path.exists():
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        models_config = config.get('models', {})
        providers = models_config.get('providers', {})
        bailian_config = providers.get('bailian', {})
        
        if bailian_config:
            return {
                'api_key': bailian_config.get('apiKey', ''),
                'base_url': bailian_config.get('baseUrl', 'https://dashscope.aliyuncs.com/compatible-mode/v1'),
                'models': bailian_config.get('models', [])
            }
        
        return None
        
    except Exception as e:
        print(f"⚠️  读取 OpenClaw 配置失败：{e}")
        return None


def generate_gwt_with_llm_batch(files_data: List[Dict], model: str = "glm-5") -> List[Dict]:
    """
    批量调用 LLM 生成 GWT 验收标准（使用 requests 直接调用）
    """
    # 获取配置
    config = get_openclaw_config()
    if not config:
        print("⚠️  未找到 OpenClaw 配置", file=sys.stderr)
        return []
    
    api_key = config['api_key']
    base_url = config['base_url']
    
    # 构建批量请求的 prompt
    files_prompt = ""
    for i, file_data in enumerate(files_data, 1):
        filename = file_data['filename']
        content = file_data['content'][:2000]
        
        files_prompt += f"""
### 文件 {i}: {filename}

**需求内容**:
{content}

"""
    
    # 构建请求
    task = f"""你是一个专业的测试专家。请为以下需求文档批量生成 GWT（Given-When-Then）格式的验收标准。

{files_prompt}

## 任务要求

对**每个文件**，请完成：

1. **分析需求类型和复杂度**，决定验收场景数量：
   - 简单需求（1-2 个功能点）：2-3 个场景
   - 中等需求（3-5 个功能点）：4-6 个场景
   - 复杂需求（6+ 功能点）：8+ 个场景

2. **根据业务类型选择验收类别**：
   - UI 验证、功能验证、数据验证、异常验证、兼容性验证等

3. **每个验收场景包含**：
   - Given（给定）：前置条件
   - When（当）：操作或事件
   - Then（那么）：预期结果
   - category：验收类别
   - reason：为什么需要这个场景

## 输出格式

请严格按以下 JSON 格式输出（不要其他内容）：

```json
{{
  "results": [
    {{
      "filename": "文件名",
      "auto_generated": [
        {{
          "given": "前置条件",
          "when": "操作",
          "then": "预期结果",
          "category": "UI 验证",
          "reason": "理由"
        }}
      ],
      "expert_comment": "作为测试专家的决策理由"
    }}
  ]
}}
```

现在请开始分析并生成 GWT 验收标准。"""
    
    try:
        # 直接调用 API
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "你是一个专业的测试专家，擅长生成 GWT 验收标准。"},
                    {"role": "user", "content": task}
                ],
                "temperature": 0.3,
                "max_tokens": 4000
            },
            timeout=120  # 2 分钟超时
        )
        
        response.raise_for_status()
        result = response.json()
        
        response_text = result['choices'][0]['message']['content']
        
        # 提取 JSON
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            llm_result = json.loads(json_match.group(1))
            return llm_result.get('results', [])
        else:
            llm_result = json.loads(response_text)
            return llm_result.get('results', [])
        
    except Exception as e:
        print(f"⚠️  LLM 调用失败：{e}，降级到规则生成", file=sys.stderr)
        return []


def generate_gwt_for_single_file(content: str, filename: str, model: str = "glm-5") -> Dict:
    """为单个文件生成 GWT"""
    results = generate_gwt_with_llm_batch([{'filename': filename, 'content': content}], model=model)
    
    if results and len(results) > 0:
        return results[0]
    else:
        return {'error': 'LLM 生成失败'}


if __name__ == '__main__':
    # 测试配置
    config = get_openclaw_config()
    if config:
        print("✅ OpenClaw 配置:")
        print(f"   Base URL: {config['base_url']}")
        print(f"   API Key: {config['api_key'][:20]}...")
        print(f"   可用模型：{[m['id'] for m in config.get('models', [])]}")
        print()
    else:
        print("❌ 未找到 OpenClaw 配置")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("用法：python3 generate_gwt_llm.py <文件路径> [模型名称]")
        sys.exit(1)
    
    # 读取文件
    from parse_requirement import RequirementParser
    
    parser = RequirementParser()
    result = parser.parse(sys.argv[1])
    
    if not result['success']:
        print(f"❌ 解析失败：{result.get('error')}")
        sys.exit(1)
    
    # 获取模型名称
    model = sys.argv[2] if len(sys.argv) > 2 else "glm-5"
    
    # 生成 GWT
    print(f"🤖 正在使用 {model} 生成 GWT...")
    gwt_result = generate_gwt_for_single_file(result['content'], sys.argv[1], model=model)
    
    print(json.dumps(gwt_result, ensure_ascii=False, indent=2))
