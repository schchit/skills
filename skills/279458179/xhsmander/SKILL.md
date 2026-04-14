---
name: xhsmander
description: |
  小红书自动化发布技能。通过 Docker 容器中的 xiaohongshu-mcp 服务，实现登录、发布图文、搜索、互动等操作。
  当用户提到发小红书、发笔记、发布内容、扫码登录小红书、小红书自动化、小红书发布时使用此技能。
---

# xhsmander - 小红书定制化发布技能

通过 `xiaohongshu-mcp` (Docker) 提供完整的小红书自动化能力。

## 核心脚本（scripts/）

所有脚本均位于 `~/.openclaw/.openclaw/workspace/xhsmander/scripts/`，通过 MCP HTTP API 与容器通信。

### 架构说明

```
本机(OpenClaw)  --HTTP+JSON-RPC-->  Docker容器(xiaohongshu-mcp)  --Chrome/ROD--> 小红书网页
```

**关键路径规则：**
- 本机路径（如图片）→ 容器无法直接访问
- 容器内路径 `/app/images/` → 本机 `scripts/images/` 目录（docker-compose 挂载）
- 发布图片时，images 参数传容器内路径 `/app/images/xxx.png`

## 工作流程

### 1. 检查 MCP 服务状态

```python
# scripts/mcp_check.py
import urllib.request, json

url = "http://localhost:18060/mcp"
try:
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=3):
        print("running")
except:
    print("not running")
```

服务未运行时，告知用户启动 Docker。

### 2. 登录流程（首次或 Cookie 过期）

```python
# scripts/mcp_qrcode.py - 获取二维码
import urllib.request, json, base64

url = "http://localhost:18060/mcp"
headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

# 初始化获取 Session ID
init = {"jsonrpc":"2.0","method":"initialize","params":{...},"id":1}
req = urllib.request.Request(url, data=json.dumps(init).encode(), headers=headers)
session_id = resp.headers.get("Mcp-Session-Id")

# 调用 get_login_qrcode
call = {"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_login_qrcode","arguments":{}},"id":2}
# 响应中的 image.data 是 base64 PNG
```

发送二维码图片给用户 → 用户扫码 → 检查 check_login_status 确认已登录。

### 3. 发布图文

```python
# scripts/mcp_publish.py
import urllib.request, json

url = "http://localhost:18060/mcp"
headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

# 每次请求都需要先 initialize 获取新 session（重要！）
init = {"jsonrpc":"2.0","method":"initialize","params":{...},"id":1}
session_id = ...  # 从 initialize 响应 header 获取

# 发布
publish = {
    "jsonrpc":"2.0","method":"tools/call",
    "params":{"name":"publish_content","arguments":{
        "title": "标题（≤20字）",
        "content": "正文（≤1000字）",
        "images": ["/app/images/test.png"],  # 容器内路径！
        "tags": ["标签1", "标签2"]
    }},
    "id":2
}
```

**图片路径规则：**
- 图片必须放在 `scripts/images/` 目录（docker-compose 挂载点）
- 传参时用容器路径 `/app/images/xxx.png`
- 不支持本机其他路径

### 4. 其他工具

| 工具名 | 用途 | 关键参数 |
|---|---|---|
| `check_login_status` | 检查登录状态 | 无 | 
| `search_feeds` | 搜索笔记 | keyword |
| `list_feeds` | 首页推荐 | 无 |
| `like_feed` | 点赞 | feed_id, xsec_token |
| `favorite_feed` | 收藏 | feed_id, xsec_token |
| `get_feed_detail` | 笔记详情 | feed_id, xsec_token |
| `user_profile` | 用户主页 | user_id, xsec_token |
| `post_comment_to_feed` | 评论 | feed_id, xsec_token, content |

feed_id 和 xsec_token 从 list_feeds / search_feeds 结果中获取。

## 限制与注意事项

1. **Session 不可复用**：每次 MCP 请求前必须先发 initialize 获取新 session ID
2. **图片路径**：必须是 `/app/images/xxx.png`（容器内路径），不是本机路径
3. **Cookie 有效期**：Cookie 存储在 Docker volume 中，重启容器需重新登录
4. **二维码时效**：有效期约5分钟，超时需重新获取
5. **发布限制**：每天发帖量建议≤50篇

## Docker 环境信息

- 容器名：`xiaohongshu-mcp`
- 端口：18060
- 镜像：阿里云镜像（国内加速）
- 数据卷：`./data`（cookies）、`./images`（发布图片）
- 挂载配置：参考 `scripts/docker-compose.yml`
