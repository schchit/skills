---
name: clawbrain-benchmark
description: 测试你的 OpenClaw 在 205 个真实场景下的表现，对比 ClawBrain Pro 编排引擎的提升效果
user-invocable: true
command-dispatch: tool
command-tool: exec
metadata: {"openclaw": {"emoji": "📊", "requires": {"bins": ["curl"]}}}
---

# ClawBrain Benchmark

测试你的 AI 在 OpenClaw 中的真实表现。看看它做简单事行不行，做复杂事会不会掉链子。

## 使用方法

直接说"跑一下 benchmark"或"测试一下模型效果"。

## 测试什么

10 大类、205 个真实场景：

| 类别 | 测什么 | 为什么重要 |
|------|-------|----------|
| 文件操作 | 读、写、编辑文件 | 基本功 |
| 搜索 | 查资料、抓网页 | 日常需求 |
| 消息 | 微信、钉钉发消息 | 沟通协作 |
| 终端 | 跑命令、管服务 | 开发运维 |
| 多步任务 | 搜索→整理→保存→通知 | 真正做事的能力 |
| 错误恢复 | 出错了怎么办 | 靠不靠谱 |
| 模糊指令 | "帮我准备下" | 聪不聪明 |

## 评测结果

| 模型 | 综合 | 错误恢复 | 模糊指令 |
|------|:---:|:---:|:---:|
| ClawBrain Pro（编排引擎） | ~90% | 90%+ | 75%+ |
| GLM-5 | 83% | 80% | 65% |
| MiniMax-M2.5 | 81% | 76% | 55% |
| Qwen3-Coder-Plus | 79% | 76% | 25% |
| DeepSeek-V3 | 73% | 56% | 65% |

ClawBrain Pro 通过编排引擎实现：规划→多模型协作→结果验证，综合表现超越任何单模型。

完整报告：https://clawbrain.dev/blog/openclaw-model-comparison
