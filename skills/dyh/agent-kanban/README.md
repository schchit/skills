# Agent Kanban

OpenClaw Agent Dashboard - Real-time monitoring of all Agent status and session history.

![Bloomberg Terminal Style](https://img.shields.io/badge/style-Bloomberg%20Terminal-orange)

## Features

- **Real-time Monitoring** - View all Agent online status and last active time
- **Auto Grouping** - Group by project prefix (main, pmo, alpha, beta)
- **Heartbeat Display** - Show agent heartbeat interval from openclaw.json
- **Session History** - Click cards to view recent conversation history
- **File Viewer** - View Agent's OKR.md, SOUL.md, HEARTBEAT.md
- **Session Size Monitor** - Display .jsonl file size with threshold warnings
- **Font Size Control** - 10px-24px with reset button (R)
- **Bloomberg Style** - Bloomberg Terminal style interface
- **Auto Config Reload** - Hot reload when openclaw.json changes

## Tech Stack

- **Backend**: Node.js + Express
- **Frontend**: React 18 (CDN)
- **Avatar**: DiceBear Pixel Art API
- **API**: OpenClaw Gateway HTTP API

---

## Quick Start

### Prerequisites

1. **Install OpenClaw**

```bash
npm install -g openclaw
```

2. **Start Gateway**

```bash
openclaw gateway start
```

### 1. Install Dependencies

```bash
cd agent-kanban/
npm install
```

### 2. Start (No Manual Config Needed!)

```bash
npm start
# Access http://localhost:3100
```

**Gateway Token is auto-loaded from `~/.openclaw/openclaw.json`** - no manual configuration required!

### 3. (Optional) Custom Config

```bash
cp config.js config.local.js
# Edit config.local.js if needed
```

Config options:

```javascript
module.exports = {
  server: { port: 3100, host: '0.0.0.0' },
  gateway: {
    url: 'http://127.0.0.1:18789',
    token: ''  // Leave empty to auto-load from openclaw.json
  },
  openclaw: { homeDir: '.openclaw', configFilename: 'openclaw.json' },
  refreshInterval: 60000,
  sessionSizeThresholds: { warning: 500, danger: 1024 }
};
```

---

## Error Handling

Agent Kanban provides clear error messages for common issues:

| Error | Code | Solution |
|-------|------|----------|
| Gateway 未启动 | `GATEWAY_NOT_RUNNING` | Run `openclaw gateway start` |
| Gateway 响应超时 | `GATEWAY_TIMEOUT` | Check Gateway health |
| Gateway Token 无效 | `TOKEN_INVALID` | Check token in openclaw.json |
| Gateway Token 未配置 | `TOKEN_MISSING` | Run `openclaw wizard` |
| 网络错误 | `NETWORK_ERROR` | Check network connection |

---

## Security

- **Local Access Only**: Gateway URL must be `localhost` or private IP (192.168.x.x, 10.x.x.x, 172.x.x.x)
- **CORS Protected**: Only allows requests from localhost:3100
- **Token Validation**: Validates Gateway token before API calls

---

## Agent Naming Convention

OpenClaw uses a unified Agent naming convention for easy management and extension.

### Naming Format

```
{project}-{role}-{number}
```

| Part | Description | Example |
|------|-------------|---------|
| `{project}` | Project/department prefix | `alpha`, `beta`, `pmo` |
| `{role}` | Role type | `pm`, `algo`, `sre` |
| `{number}` | Instance number (optional) | `1`, `2`, `3` |

### Project Prefixes

| Prefix | Meaning | Description |
|--------|---------|-------------|
| `main` | Main Agent | Entry Agent that talks directly to user |
| `pmo` | Project Management Office | Coordination, monitoring, auditing |
| `alpha` | Project Alpha | Example project Alpha |
| `beta` | Project Beta | Example project Beta |

### Role Types

| Role | Full Name | Responsibility |
|------|-----------|----------------|
| `pm` | Project Manager | Project manager, coordinate team |
| `sre` | Site Reliability Engineer | Operations engineer, monitor services |
| `researcher` | Researcher | Researcher, explore new directions |
| `algo` | Algorithm Engineer | Algorithm engineer, implement algorithms |
| `qa` | Quality Assurance | QA, audit and verify |
| `submitter` | Submitter | Submitter, submit tasks |
| `tracker` | Tracker | Tracker, monitor progress |
| `director` | Director | Director, manage overall |
| `auditor` | Auditor | Auditor, supervise and inspect |
| `clocksmith` | Clocksmith | Clocksmith, automation mechanisms |

---

## Gateway API Configuration

### Get Gateway Token

```bash
# Method 1: From config file
cat ~/.openclaw/openclaw.json | jq '.gateway.auth.token'

# Method 2: From CLI
openclaw gateway status

# Method 3: From Web UI
# http://localhost:18790 → Settings → API Tokens
```

### API Usage

```bash
curl -X POST http://127.0.0.1:18789/tools/invoke \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tool": "sessions_list", "args": {}}'
```

---

## License

MIT

---

# Agent Kanban（中文）

OpenClaw Agent 状态监控面板 - 实时查看所有 Agent 的运行状态和会话历史。

![Bloomberg Terminal Style](https://img.shields.io/badge/style-Bloomberg%20Terminal-orange)

## 功能特性

- **实时监控** - 显示所有 Agent 的在线状态、最后活跃时间
- **自动分组** - 按项目前缀自动分组（main、pmo、alpha、beta）
- **心跳显示** - 从 openclaw.json 读取并显示 Agent 心跳间隔
- **会话历史** - 点击卡片查看最近的对话记录
- **文件查看** - 查看 Agent 的 OKR.md、SOUL.md、HEARTBEAT.md 文件
- **Session 大小监控** - 显示每个 Agent 的 Session 文件大小，超过阈值高亮警告
- **字号调节** - 支持调节所有文字的字号大小（10px-24px）
- **彭博风格** - Bloomberg Terminal 风格界面
- **配置热更新** - 自动检测 openclaw.json 变化并重新加载

## 技术栈

- **后端**: Node.js + Express
- **前端**: React 18 (CDN)
- **头像**: DiceBear Pixel Art API
- **API**: OpenClaw Gateway HTTP API

---

## 快速开始

### 前置条件

1. **安装 OpenClaw**

```bash
npm install -g openclaw
```

2. **启动 Gateway**

```bash
openclaw gateway start
```

### 1. 安装依赖

```bash
cd agent-kanban/
npm install
```

### 2. 启动（无需手动配置！）

```bash
npm start
# 访问 http://localhost:3100
```

**Gateway Token 自动从 `~/.openclaw/openclaw.json` 读取，无需手动配置！**

### 3. （可选）自定义配置

```bash
cp config.js config.local.js
# 编辑 config.local.js
```

---

## 错误处理

Agent Kanban 针对常见问题提供清晰的错误提示：

| 错误 | 代码 | 解决方案 |
|------|------|----------|
| Gateway 未启动 | `GATEWAY_NOT_RUNNING` | 运行 `openclaw gateway start` |
| Gateway 响应超时 | `GATEWAY_TIMEOUT` | 检查 Gateway 健康状态 |
| Gateway Token 无效 | `TOKEN_INVALID` | 检查 openclaw.json 中的 token |
| Gateway Token 未配置 | `TOKEN_MISSING` | 运行 `openclaw wizard` |
| 网络错误 | `NETWORK_ERROR` | 检查网络连接 |

---

## 安全性

- **仅本地访问**: Gateway URL 必须是 `localhost` 或私有 IP（192.168.x.x, 10.x.x.x, 172.x.x.x）
- **CORS 保护**: 只允许来自 localhost:3100 的请求
- **Token 验证**: 在调用 API 前验证 Gateway Token

---

## Agent 命名规范

OpenClaw 使用统一的 Agent 命名规范，便于管理和扩展。

### 命名格式

```
{项目}-{角色}-{编号}
```

### 项目前缀

| 前缀 | 含义 | 说明 |
|------|------|------|
| `main` | 主 Agent | 与用户直接对话的入口 Agent |
| `pmo` | 项目管理办公室 | 协调、监控、审计 |
| `alpha` | Alpha 项目 | 示例项目 Alpha |
| `beta` | Beta 项目 | 示例项目 Beta |

### 角色类型

| 角色 | 全称 | 职责 |
|------|------|------|
| `pm` | Project Manager | 项目经理，协调团队 |
| `sre` | Site Reliability Engineer | 运维工程师，监控服务 |
| `researcher` | Researcher | 研究员，探索新方向 |
| `algo` | Algorithm Engineer | 算法工程师，实现算法 |
| `qa` | Quality Assurance | 质量保证，审计验证 |
| `submitter` | Submitter | 提交者，提交任务 |
| `tracker` | Tracker | 追踪者，监控进度 |
| `director` | Director | 总监，整体管理 |
| `auditor` | Auditor | 审计员，监督检查 |
| `clocksmith` | Clocksmith | 钟匠，自动化机制 |

---

## License

MIT