---
name: feishu-multiagent-setup
description: "OpenClaw 多飞书机器人一键自动化配置工具。当用户需要添加多个飞书机器人到 OpenClaw 时使用，包括：批量创建 agent 工作区、生成 auth-profiles.json、更新 gateway 配置（accounts + bindings + agents.list）、自动重启 Gateway。触发场景：'帮我配置多个机器人'、'批量添加飞书账号'、'一键安装多 agent'、'复制现有架构到新机器人'。"
---

# feishu-multiagent-setup

自动化配置 OpenClaw 多飞书机器人。一条命令完成全部设置。

## 工作流程

```
收集信息 → 执行脚本 → 验证结果 → 测试
```

## 使用步骤

### 第一步：收集信息

向用户收集以下信息：

1. **共用 API Key**：所有 agent 共享同一个 minimax API Key
2. **Agent 列表**：每个机器人的名字、AppId、AppSecret，格式如下：

```
名字, AppId, AppSecret
名字, AppId, AppSecret
```

**示例输入：**
```
jiance, cli_a93561f4f138dcd3, If7HCy0hcJnAo0ERXnjmkZz7mqNfJAgs
jiyi, cli_a935618fc2789cef, CNq8jnyPvqnSASvX79hDlgddr4pRpPqJ
```

3. **工作区根目录**（可选，默认为 `D:\Openclawagents`）
4. **模型**（可选，默认为 `minimax/MiniMax-M2.7-highspeed`，国产高速版）

### 第二步：执行脚本

将收集的信息传入 `setup-agents.ps1`：

```powershell
.\setup-agents.ps1 -ApiKey "sk-api-你的key" -AgentsCsv "名字,AppId,AppSecret`n名字2,AppId2,Secret2" -WorkspaceRoot "D:\Openclawagents"
```

### 第三步：验证结果

脚本执行后检查：

1. 验证 auth-profiles.json 是否写入成功：
   ```powershell
   Get-Content "D:\Openclawagents\jiance\agent\auth-profiles.json"
   ```
2. 验证 gateway 配置是否更新：
   ```powershell
   openclaw status
   ```

### 第四步：测试

到对应飞书机器人发一条消息，验证响应正常。

## 脚本功能

| 功能 | 说明 |
|------|------|
| 创建工作区目录 | `D:\Openclawagents\<name>` |
| 生成 auth-profiles.json | 写入共用 API Key，provider: `minimax` |
| 添加 Feishu 账号 | 写入 `channels.feishu.accounts.<name>` |
| 添加路由绑定 | 写入 `bindings[]`，格式：`feishu:<name> → agent:<name>` |
| 注册 Agent | 写入 `agents.list[]` |
| 重启 Gateway | 自动执行 `openclaw gateway restart` |

## 参考文档

详细说明见：`references/setup-guide.md`

## 故障排查

| 问题 | 解决方法 |
|------|---------|
| 脚本执行失败 | 用 `powershell -ExecutionPolicy Bypass -File setup-agents.ps1 ...` 执行 |
| API Key 401 | 确认 key 有效，provider 名为 `minimax`（国产） |
| 机器人无法回复 | 检查 `sessions.json` 是否缓存了错误的 authProfileOverride，删除让它重建 |
| Gateway 未重启 | 手动执行 `openclaw gateway restart` |

## 输出示例

```
[2026-03-23 17:10:00] [INFO] ========================================
[2026-03-23 17:10:00] [INFO] OpenClaw 多飞书机器人自动配置
[2026-03-23 17:10:00] [INFO] ========================================
[2026-03-23 17:10:00] [INFO] Parsed 4 agent(s)
[2026-03-23 17:10:00] [INFO] Shared API Key: sk-api-A2byRss...
[2026-03-23 17:10:00] [INFO] --- 步骤1: 创建工作区 ---
[2026-03-23 17:10:00] [OK] Created: D:\Openclawagents\jiance\agent
[2026-03-23 17:10:00] [OK] Written: D:\Openclawagents\jiance\agent\auth-profiles.json
...
[2026-03-23 17:10:05] [OK] Gateway 重启成功
[2026-03-23 17:10:05] [INFO] 配置完成！共 4 个机器人已就绪
```
