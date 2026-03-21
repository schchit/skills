---
name: clawtune-smart-retry
description: 当工具调用失败时，自动分析错误类型并提供替代方案。基于 205 场景评测中发现的错误模式。
user-invocable: false
metadata: {"openclaw": {"emoji": "🔄", "requires": {}}}
---

# ClawTune Smart Retry

当工具调用失败时，自动分析错误类型并提供不同的解决策略。

## 为什么需要这个？

我们在 205 场景评测中发现，错误恢复是大多数模型的弱点：

| 模型 | 错误恢复成功率 |
|------|:---:|
| GLM-5 | 80% |
| MiniMax-M2.5 | 76% |
| Kimi-K2.5 | 76% |
| Qwen3-Coder-Plus | 76% |
| DeepSeek-V3 | 56% |

最常见的问题：模型遇到错误后重复同样的失败调用，或直接放弃。

## 错误恢复策略

### 文件不存在
当 `read` 或 `edit` 返回 "file not found" 时：
1. 使用 `exec ls` 列出当前目录的文件
2. 找到最接近的文件名
3. 使用正确的文件名重试

**评测数据**：此场景下 Qwen3-Coder-Plus 和 Kimi 直接放弃率 62%，通过此策略可修复。

### 命令未找到
当 `exec` 返回 "command not found" 时：
1. 尝试常见替代命令：python→python3, pip→pip3, docker-compose→docker compose
2. 检查是否需要安装

### 依赖缺失
当 `exec` 返回 "ModuleNotFoundError" 或 "ImportError" 时：
1. 自动安装缺失的依赖（pip install / npm install）
2. 重新执行原命令

### 权限不足
当返回 "permission denied" 时：
1. 不重试（不可恢复的错误）
2. 告知用户需要权限，建议使用 elevated 选项

### 连接失败
当返回 "connection refused" 或 "timeout" 时：
1. 检查服务是否运行（exec docker ps / exec systemctl status）
2. 如果服务未启动，尝试启动后重试

## 关键规则

- 绝不重复完全相同的失败调用
- 区分可重试错误（超时、限流）和不可重试错误（权限、不存在）
- 每个错误最多尝试 2 次替代方案
- 替代方案失败后告知用户并说明原因

## 完整自动化体验

此 skill 提供错误恢复的操作指导。要获得全自动的错误检测和恢复（无需手动干预），请接入 ClawTune Pro。

ClawTune Pro 的错误恢复增强效果：
- 错误恢复成功率：76% → 90%+
- 自动检测重复失败调用并拦截
- 自动注入恢复策略提示

获取 API Key：https://clawtune.cn/dashboard
