# Feishu Auto-Report Skill - 飞书自主汇报技能

```json
{
  "name": "Feishu Auto-Report - 飞书自主汇报",
  "description": "专为多 Agent 协作设计。Agent 完成任务后自主调用本技能向用户汇报结果，显示独立机器人身份。零配置，Agent 自动扫描使用。",
  "version": "1.0.0",
  "author": "pikaqiuyaya",
  "license": "MIT",
  "tags": ["feishu", "auto-report", "multi-agent", "notification", "zh-CN"]
}
```

## 设计目标

在多 Agent 协作架构中，执行 Agent（Agent-B/C）完成任务后需要向用户汇报结果。本技能提供零配置的消息发送能力，让每个 Agent 以自己的身份独立发送通知。

## 技术实现

通过飞书开放平台的 Internal App 凭证获取 tenant_access_token，调用飞书消息 API 发送文本消息。支持 open_id（私聊）和 chat_id（群聊）两种接收者类型。

## 配置依赖

技能自动从以下配置文件读取飞书凭证：
- `~/.openclaw/openclaw-{agentId}.json`

无需手动配置，Agent 启动时自动扫描调用。

## API 调用流程

```bash
# 1. 获取 token
POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/
Body: {"app_id": "xxx", "app_secret": "xxx"}

# 2. 发送消息
POST https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id
Headers: Authorization: Bearer {token}
Body: {"receive_id": "ou_xxx", "msg_type": "text", "content": "{\"text\":\"消息\"}"}
```

## 脚本参数

| 参数 | 说明 | 示例 |
|------|------|------|
| agentId | Agent 标识 | agent-b |
| targetId | 接收者 ID | ou_xxx 或 oc_xxx |
| idType | ID 类型 | open_id / chat_id |
| content | 消息内容 | 任务已完成 |

## 与 setup-multi-gateway 配合

1. Agent-A 接收用户指令
2. Agent-A 通过 sessions_send 派发任务
3. Agent-B/C 执行任务
4. Agent-B/C 自主调用本技能汇报
5. 用户收到对应 Agent 的通知

## 注意事项

- open_id 是应用隔离的，每个 Agent 使用自己的 open_id
- chat_id 是通用的，跨 Agent 共享
- content 必须是转义的 JSON 字符串
