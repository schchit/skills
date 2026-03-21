---
name: wecom-bot
description: This skill provides the ability to send messages to WeCom (企业微信) group chats via Webhook bots. It should be used when users need to push notifications, reports, alerts, or any text/markdown messages to a WeCom group chat. Trigger phrases include "推送到企微", "发送到企微群", "企微机器人", "wecom bot", "群消息推送", "发送企微通知", "push to wecom", or when the user asks to send any content to a WeCom group.
---

# 企业微信群机器人推送 Skill

## 概述

本 Skill 封装了企业微信群机器人的消息推送能力，通过 Webhook 接口向企微群发送文本或 Markdown 格式的消息。无需额外依赖，仅使用 Python 标准库。

## 使用场景

- 将生成的报告、数据分析结果推送到企微群
- 发送定时通知、提醒消息
- 推送告警、监控信息到群聊
- 发送带 @成员 功能的文本通知

## 前置要求

在使用之前，确认以下条件：

1. **获取 Webhook Key**：在企业微信群中 → 群设置 → 群机器人 → 添加/查看机器人 → 复制 Webhook 地址中 `key=` 后的 UUID 值
2. 用户需要提供 Webhook Key（或已在上下文/历史对话中提供过）

## 使用方式

### 方式一：通过脚本直接发送（推荐）

`scripts/wecom_send.py` 是一个独立的命令行工具，可直接执行发送消息：

```bash
# 发送纯文本
python3 scripts/wecom_send.py --key <KEY> --type text --content "Hello World"

# 发送 Markdown
python3 scripts/wecom_send.py --key <KEY> --type markdown --content "## 标题\n内容"

# 从文件读取内容发送
python3 scripts/wecom_send.py --key <KEY> --type markdown --file /path/to/report.md

# @所有人
python3 scripts/wecom_send.py --key <KEY> --type text --content "紧急通知" --mention-all

# @指定成员
python3 scripts/wecom_send.py --key <KEY> --type text --content "请查收" --mention userid1,userid2
```

### 方式二：在 Python 代码中调用

当需要在自定义脚本中集成企微推送时，读取 `scripts/wecom_send.py` 中的 `send_text()` 和 `send_markdown()` 函数作为参考，将其集成到目标脚本中。

核心函数签名：

```python
def send_text(key: str, content: str,
              mentioned_list: list = None,
              mentioned_mobile_list: list = None) -> dict:
    """发送纯文本消息，返回 dict，errcode=0 表示成功"""

def send_markdown(key: str, content: str) -> dict:
    """发送 Markdown 消息，返回 dict，errcode=0 表示成功"""
```

## 推送工作流

执行推送任务时，按照以下步骤操作：

1. **确认 Webhook Key**：从用户处获取或从对话上下文中提取。若用户未提供，提示用户去企微群设置中获取。
2. **确定消息类型**：
   - 简单通知、需要 @成员 → 使用 **text** 类型
   - 带格式的报告、数据表格 → 使用 **markdown** 类型
3. **构建消息内容**：根据用户需求组装内容。如涉及数据查询，先完成查询再构建消息。
4. **执行发送**：调用 `scripts/wecom_send.py` 脚本发送消息。
5. **检查结果**：确认 `errcode=0` 表示成功。如失败，参考 `references/api_reference.md` 中的错误码排查。

## Markdown 消息格式要点

企微群机器人的 Markdown 支持**有限子集**（非标准 Markdown），可用的格式：

- 标题：`#` / `##` / `###`
- 加粗：`**文字**`
- 链接：`[文字](URL)`
- 引用：`> 引用`
- 列表：`- 无序` 或 `1. 有序`
- 字体颜色：`<font color="info">绿色</font>`、`<font color="comment">灰色</font>`、`<font color="warning">橙红色</font>`

**不支持**：图片、表格、代码块、@成员。详见 `references/api_reference.md`。

## 注意事项

- 每个机器人发送频率上限 **20条/分钟**，批量发送时需注意节流
- 文本消息内容最大 **2048 字节**
- Markdown 消息内容最大 **4096 字节**
- macOS 环境下脚本已内置 SSL 证书兼容处理
