---
name: feishu-notifier
description: 通过飞书 Open API 发送通知消息，支持即时通知、定时提醒和系统监控。Use when user needs to send notifications via Feishu (Lark), set up scheduled reminders, or integrate system monitoring alerts with Feishu messaging.
---

# Feishu Notifier

通过飞书 Open API 发送通知消息的 OpenClaw Skill。

## 功能

- **即时通知** - 发送即时消息到飞书
- **定时提醒** - 创建和管理定时提醒任务
- **系统监控** - 磁盘监控示例，可扩展更多监控项

## 前置准备

1. 在 [飞书开放平台](https://open.feishu.cn/app) 创建企业自建应用
2. 获取 **App ID** 和 **App Secret**
3. 添加权限：`im:message:send_as_bot`
4. 获取目标用户的 **Open ID** (格式: `ou_xxxx`)
5. 发布应用

## 使用方法

### 即时通知

```bash
# 设置环境变量
export FEISHU_APP_ID="cli_xxxxxxxxxx"
export FEISHU_APP_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export FEISHU_USER_ID="ou_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 发送通知
./scripts/feishu-notify.sh -t "标题" -m "消息内容"
```

### 脚本选项

```
-h, --help          显示帮助
-t, --title TITLE   消息标题
-m, --message MSG   消息内容
-u, --user USER_ID  指定接收用户
--test              发送测试消息
```

### 在 crontab 中使用

```bash
# 每5分钟检查磁盘并发送警告
*/5 * * * * /path/to/disk_monitor.sh -c

# 每天9点发送早安提醒
0 9 * * * /path/to/feishu-notify.sh -t "早安" -m "新的一天开始了！"
```

## 脚本说明

### feishu-notify.sh

核心通知脚本，负责：
1. 使用 App ID 和 App Secret 获取 tenant_access_token
2. 构建消息卡片（JSON 格式）
3. 调用飞书消息 API 发送通知

消息格式使用飞书消息卡片（interactive card），包含：
- 标题（header，蓝色主题）
- 内容（Markdown 格式）
- 发送时间（footer）

## 扩展

基于此脚本可以开发更多监控功能：
- CPU/内存监控
- 服务状态监控
- 日志异常检测
- 定时任务执行通知

## 参考

- [飞书开放平台文档](https://open.feishu.cn/document/home/index)
- [发送消息 API](https://open.feishu.cn/document/server-docs/im-v1/message/create)
