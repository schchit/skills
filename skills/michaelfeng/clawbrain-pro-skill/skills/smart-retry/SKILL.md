---
name: clawbrain-smart-retry
description: 出错了自动换方案试，不重复同样的错误。基于 205 场景评测中发现的错误模式。
user-invocable: false
metadata: {"openclaw": {"emoji": "🔄", "requires": {}}}
---

# ClawBrain Smart Retry

工具调用出错了怎么办？这个 skill 帮你的 AI 学会自己想办法。

## 为什么需要

我们测了 205 个场景，发现大多数模型遇到错误就放弃：

| 模型 | 出错后能自救的比例 |
|------|:---:|
| GLM-5 | 80% |
| MiniMax-M2.5 | 76% |
| Qwen3-Coder-Plus | 76% |
| DeepSeek-V3 | 56% |

最常见的问题：同样的错误重复犯，或者直接说"做不了"。

## 恢复策略

**文件找不到** → 用 ls 命令查找正确文件名，再重试

**命令不存在** → 试替代命令（python→python3, pip→pip3）

**缺少依赖** → 先安装再执行

**权限不足** → 不硬来，告诉你需要什么权限

**连续失败** → 换另一个模型帮忙（ClawBrain Pro 的双模型共识）

## 核心原则

- 绝不重复同样的错误
- 每次出错最多试 2 种不同方案
- 实在搞不定就说清楚为什么

## 全自动体验

这个 skill 提供错误恢复的指导。想要全自动的错误恢复（AI 自己搞定，不用你管），接入 ClawBrain Pro 的编排引擎：
- 自动检测错误类型
- 自动选择恢复策略
- 搞不定还会请另一个模型帮忙

https://clawbrain.dev/dashboard
