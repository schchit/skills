---
name: clawbrain-pro
description: ClawBrain Pro — OpenClaw 最聪明的大脑。内置编排引擎，自动规划、多模型协作、结果验证。205 场景评测第一。
user-invocable: true
metadata: {"openclaw": {"emoji": "🧠", "homepage": "https://github.com/michaelfeng/clawbrain", "requires": {}}}
---

# ClawBrain Pro

给你的 OpenClaw 装上最聪明的大脑。不只是更聪明——会自己想、自己规划、自己做到底。

## 它能帮你做什么

- **复杂任务自动规划**：你说一句话，它拆成步骤按顺序执行
- **10 个 AI 模型智能调度**：简单的事用快模型，难的事用强模型
- **出错不放弃**：文件找不到自己去翻，命令出错换方法试，搞不定请另一个模型帮忙
- **做事做到底**：多步任务每一步都盯着，不半途而废
- **听得懂模糊的话**：说"帮我准备下"，它知道先查什么再做什么
- **结果自动验证**：回复前检查质量，不合格就重来

## 评测数据（205 场景 × 10 模型）

| 能力 | ClawBrain Pro | 最好的单模型 |
|------|:---:|:---:|
| 综合得分 | ~90% | 83% (GLM-5) |
| 错误恢复 | 90%+ | 80% (GLM-5) |
| 模糊指令 | 75%+ | 65% (GLM-5) |
| 多步任务 | 85%+ | 80% (DeepSeek) |

## 接入方法

```json
{
  "models": {
    "providers": {
      "clawbrain": {
        "baseUrl": "https://api.clawbrain.dev/v1",
        "apiKey": "你的 API Key",
        "api": "openai-completions",
        "models": [{"id": "clawbrain-pro", "name": "ClawBrain Pro", "contextWindow": 262144, "maxTokens": 65536}]
      }
    }
  },
  "agents": {"defaults": {"model": {"primary": "clawbrain/clawbrain-pro"}}}
}
```

然后 `openclaw gateway restart`。

## 其他工具

```bash
clawhub install clawbrain-benchmark    # 评测你的模型表现
clawhub install clawbrain-doctor       # 诊断配置问题
clawhub install clawbrain-smart-retry  # 出错自动换方案
```

获取 API Key：https://clawbrain.dev/dashboard
