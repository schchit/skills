#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
需求文档批量检查工具（智能体调用版）
通过 OpenClaw sessions_spawn 调用智能体进行 GWT 生成
"""

import sys
import json
from pathlib import Path

# 使用 OpenClaw 的 sessions_spawn 调用智能体
def check_with_agent(file_path: str) -> dict:
    """
    调用智能体检查单个文件并生成 GWT
    
    Args:
        file_path: 文件路径
        
    Returns:
        智能体返回的检查结果
    """
    from openclaw import sessions_spawn
    
    try:
        # 调用智能体
        result = sessions_spawn({
            runtime: "subagent",
            task=f"""请使用 requirement-checker 技能检查以下需求文档，并作为测试专家生成 GWT 验收标准：

文件路径：{file_path}

请完成以下任务：
1. 检查需求文档是否符合 12 项规范
2. 作为测试专家，根据需求内容自动生成 GWT 验收标准：
   - 根据需求复杂度决定验收场景数量（简单 2-3 个，中等 4-6 个，复杂 8+ 个）
   - 根据业务类型选择验收类别（UI 验证/功能验证/数据验证/异常验证等）
   - 每个场景说明 category 和 reason
3. 在 expert_comment 中说明你的决策理由

输出格式要求（JSON）：
```json
{{
  "summary": {{
    "compliance_rate": 合规率，
    "passed_count": 通过数，
    "warning_count": 警告数，
    "issue_count": 问题数
  }},
  "warnings": [
    {{
      "rule": "规则名称",
      "issue": "问题说明",
      "suggestion": "优化建议"
    }}
  ],
  "gwt_acceptance": {{
    "has_gwt": false,
    "auto_generated": [
      {{
        "given": "前置条件",
        "when": "操作",
        "then": "预期结果",
        "category": "验收类别",
        "reason": "理由"
      }}
    ],
    "expert_comment": "作为测试专家的决策理由"
  }}
}}
```

请直接返回 JSON 格式的检查结果。""",
            timeoutSeconds: 120
        })
        
        # 解析智能体返回的结果
        if result and 'response' in result:
            response_text = result['response']
            # 尝试提取 JSON
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                # 尝试直接解析
                return json.loads(response_text)
        else:
            return {'error': '智能体未返回结果'}
            
    except Exception as e:
        return {'error': f'调用智能体失败：{str(e)}'}


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python3 batch_check_with_agent.py <文件路径>")
        print("示例：python3 batch_check_with_agent.py /path/to/requirement.docx")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    print(f"🤖 正在调用智能体检查：{file_path}")
    result = check_with_agent(file_path)
    
    if 'error' in result:
        print(f"❌ 错误：{result['error']}")
        sys.exit(1)
    
    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
