# OpenClaw 多飞书机器人自动配置脚本

## 功能说明

本脚本自动化完成以下操作：
1. 为每个 agent 创建工作区目录
2. 为每个 agent 生成 `auth-profiles.json`
3. 更新 OpenClaw gateway 配置（accounts + bindings + agents.list）
4. 自动重启 Gateway

## 使用方式

在 AI Agent 中运行本技能时，提供以下信息：

### 必需信息
- **共用 API Key**: minimax 国产版 API Key（所有 agent 共用）
- **Agent 列表**: 每个机器人的 appId、appSecret、工作区目录

### Agent 信息格式
```
name, appId, appSecret
```
示例：
```
jiance, cli_a93561f4f138dcd3, If7HCy0hcJnAo0ERXnjmkZz7mqNfJAgs
jiyi, cli_a935618fc2789cef, CNq8jnyPvqnSASvX79hDlgddr4pRpPqJ
```

## 输出

- `D:\Openclawagents\<name>\agent\auth-profiles.json`
- 更新 `openclaw.json` 中的：
  - `channels.feishu.accounts.<name>`
  - `bindings`（自动追加路由规则）
  - `agents.list`（自动追加 agent 条目）
- 自动执行 Gateway 重启

## 注意事项

- API Key 存于各 agent 的 `auth-profiles.json`，不在 openclaw.json
- auth-profiles.json 中的 provider 名为 `minimax`（国产）或 `minimax-portal`（国际）
- 所有 agent 需在 `bindings` 中有独立路由规则，否则消息会被路由到默认 agent
