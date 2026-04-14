---
name: hermes-handbook
description: Hermes Agent 完整手册 - 包含安装、配置、部署、运维和常见问题排查的完整指南
---

# Hermes Agent 升级与部署技能

## 📋 技能概述

本技能提供 Hermes Agent 从旧版本升级到最新版本的完整流程，包括：
- 版本检查与下载
- 配置迁移
- systemd 服务配置
- 开机自启设置
- 常见问题排查

## 🎯 适用场景

1. **升级 Hermes** - 从旧版本升级到最新版本
2. **迁移配置** - 保留旧配置到新版本
3. **配置开机自启** - 设置 systemd 服务
4. **故障排查** - 解决启动失败、模型配置等问题

---

## 📖 操作流程

### 步骤 1：检查当前版本

```bash
# 检查已安装版本
pip show hermes-agent | grep Version

# 检查 GitHub 最新版本
curl -s https://api.github.com/repos/NousResearch/hermes-agent/releases/latest | grep '"tag_name"'

# 检查当前运行状态
systemctl status hermes-gateway.service
```

### 步骤 2：下载并安装最新版本

#### 2.1 修复 git 配置（如需要）

```bash
# 如果系统配置了 ghproxy 代理但不可用，修复 git 配置
cat > ~/.gitconfig << 'EOF'
[user]
    name = OpenClaw
    email = openclaw@localhost
[url "https://github.com/"]
    insteadOf = https://ghproxy.com/
EOF
```

#### 2.2 下载安装包

```bash
# 获取最新版本号
LATEST_VERSION=$(curl -s https://api.github.com/repos/NousResearch/hermes-agent/releases/latest | grep '"tag_name"' | cut -d'"' -f4)

# 下载源码包（使用 curl，支持重试）
cd /tmp
rm -rf hermes*
curl -sL --max-time 600 --connect-timeout 120 --retry 5 --retry-delay 30 \
    "https://github.com/NousResearch/hermes-agent/archive/refs/tags/${LATEST_VERSION}.tar.gz" \
    -o hermes.tar.gz

# 验证下载
ls -lh hermes.tar.gz
file hermes.tar.gz
```

#### 2.3 解压并安装

```bash
# 解压
tar -xzf hermes.tar.gz
cd hermes-agent-*

# 使用 pip 安装
pip install --upgrade . 2>&1 | tail -30

# 验证安装
hermes --version
which hermes
```

### 步骤 3：迁移配置文件

#### 3.1 备份旧配置

```bash
# 检查旧配置位置
OLD_HERMES_DIR="/workspace/projects/hermes"  # 或实际路径

# 查看需要迁移的文件
ls -la $OLD_HERMES_DIR/.env $OLD_HERMES_DIR/auth.json $OLD_HERMES_DIR/cli-config.yaml 2>/dev/null
```

#### 3.2 迁移到新位置

```bash
# 新版本配置目录
NEW_HERMES_HOME="$HOME/.hermes"
mkdir -p $NEW_HERMES_HOME

# 迁移配置文件
cp $OLD_HERMES_DIR/.env $NEW_HERMES_HOME/.env
chmod 600 $NEW_HERMES_HOME/.env

cp $OLD_HERMES_DIR/auth.json $NEW_HERMES_HOME/auth.json
chmod 600 $NEW_HERMES_HOME/auth.json

cp $OLD_HERMES_DIR/cli-config.yaml $NEW_HERMES_HOME/cli-config.yaml
chmod 600 $NEW_HERMES_HOME/cli-config.yaml

echo "✅ 配置迁移完成"
```

#### 3.3 修复模型配置

```bash
# 检查并修复模型格式（旧格式 qwen/qwen-3.5-plus → 新格式 qwen3.5-plus）
sed -i 's/qwen\/qwen-3.5-plus/qwen3.5-plus/g' ~/.hermes/.env
sed -i 's/qwen\/qwen-3.5-plus/qwen3.5-plus/g' ~/.hermes/cli-config.yaml

# 验证
grep -i "MODEL" ~/.hermes/.env
```

#### 3.4 创建 config.yaml

```bash
# Hermes 0.8.0 需要 config.yaml 在 HERMES_HOME 或工作目录
mkdir -p /workspace/projects/hermes

cat > /workspace/projects/hermes/config.yaml << 'EOF'
model:
  default: "qwen3.5-plus"
  provider: "custom"
  base_url: "https://coding.dashscope.aliyuncs.com/v1"
  api_key_env: "OPENROUTER_API_KEY"

terminal:
  backend: "local"
  cwd: "."
  timeout: 300

gateway:
  enabled: true
  port: 5001
  
  feishu:
    enabled: true
    app_id: "cli_xxx"
    app_secret: "xxx"
    allowed_users:
      - "ou_xxx"
    dm_policy: "allow"
    group_policy: "open"
    require_mention: false

memory:
  enabled: true
  max_memory_tokens: 2200
  max_user_tokens: 1375
EOF
```

### 步骤 4：配置 systemd 服务

#### 4.1 创建服务文件

```bash
cat > /etc/systemd/system/hermes-gateway.service << 'EOF'
[Unit]
Description=Hermes Gateway Service
Documentation=https://github.com/NousResearch/hermes-agent
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/root

# 环境变量
Environment="PATH=/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin"
Environment="PYTHONUNBUFFERED=1"

# 启动命令
ExecStart=/usr/local/bin/hermes gateway run

# 重启策略
Restart=always
RestartSec=10

# 超时设置
TimeoutStartSec=180
TimeoutStopSec=120

# 资源限制
LimitNOFILE=65535
Nice=-5

# 日志
StandardOutput=journal
StandardError=journal
SyslogIdentifier=hermes-gateway

# 进程管理
KillMode=mixed
KillSignal=SIGTERM
SendSIGKILL=yes
FinalKillSignal=SIGKILL

[Install]
WantedBy=multi-user.target
EOF
```

#### 4.2 启用并启动服务

```bash
# 重新加载 systemd 配置
systemctl daemon-reload

# 启用开机自启
systemctl enable hermes-gateway.service

# 启动服务
systemctl start hermes-gateway.service

# 查看状态
systemctl status hermes-gateway.service
```

### 步骤 5：安装依赖（如需要）

```bash
# 飞书 SDK
pip install lark-oapi 2>&1 | tail -5

# 验证
python3 -c "import lark_oapi; print('✅ lark-oapi installed')"
```

### 步骤 6：飞书用户配对

```bash
# 当收到配对码时执行
hermes pairing approve feishu <PAIRING_CODE>

# 示例
# hermes pairing approve feishu VRP8RX8B
```

---

## 🔍 常见问题排查

### 问题 1：GitHub 下载失败

**症状：**
```
fatal: unable to access 'https://github.com/...': Failed to connect
curl: (56) Recv failure: Connection reset by peer
```

**解决方案：**
```bash
# 方案 A：增加重试和超时
curl -sL --max-time 600 --connect-timeout 120 --retry 5 --retry-delay 30 \
    "https://github.com/.../hermes-agent-xxx.tar.gz" -o hermes.tar.gz

# 方案 B：使用本地下载后上传
# 1. 在本地机器下载
curl -L https://github.com/NousResearch/hermes-agent/archive/refs/tags/v2026.4.8.tar.gz -o hermes.tar.gz
# 2. 上传到服务器
scp hermes.tar.gz root@server:/tmp/
# 3. 在服务器上安装
ssh root@server "cd /tmp && tar -xzf hermes.tar.gz && cd hermes-agent-* && pip install ."
```

### 问题 2：模型配置错误

**症状：**
```
API call failed after 3 retries: HTTP 400: model `` is not supported.
```

**原因：** 模型格式不正确或配置文件未读取

**解决方案：**
```bash
# 1. 检查配置位置
hermes config show | grep -A5 "◆ Model"

# 2. 修复模型格式（移除 qwen/ 前缀）
sed -i 's/qwen\/qwen-3.5-plus/qwen3.5-plus/g' ~/.hermes/.env
sed -i 's/qwen\/qwen-3.5-plus/qwen3.5-plus/g' /workspace/projects/hermes/config.yaml

# 3. 重启服务
systemctl restart hermes-gateway.service

# 4. 验证配置
hermes config show | grep "Model:"
```

### 问题 3：systemd 服务启动失败

**症状：**
```
Failed with result 'exit-code'
status=226/NAMESPACE
```

**原因：** 安全配置导致命名空间问题

**解决方案：**
```bash
# 1. 创建必要的目录
mkdir -p /root/.cache/hermes /root/.hermes

# 2. 简化 systemd 配置（移除 ProtectSystem 等）
# 编辑 /etc/systemd/system/hermes-gateway.service
# 移除或注释掉以下行：
# ProtectSystem=strict
# ProtectHome=read-only
# ReadWritePaths=...

# 3. 重新加载并重启
systemctl daemon-reload
systemctl restart hermes-gateway.service
```

### 问题 4：飞书连接失败

**症状：**
```
WARNING gateway.run: Feishu: lark-oapi not installed
```

**解决方案：**
```bash
# 安装飞书 SDK
pip install lark-oapi

# 验证配置
cat ~/.hermes/.env | grep FEISHU

# 重启服务
systemctl restart hermes-gateway.service
```

### 问题 5：用户未配对

**症状：**
```
Hi~ I don't recognize you yet!
Here's your pairing code: XXXXX
```

**解决方案：**
```bash
# 执行配对命令
hermes pairing approve feishu <PAIRING_CODE>

# 验证配对状态
hermes pairing list
cat ~/.hermes/channel_directory.json
```

**⚠️ 重要：为什么每次升级后都要重新配对？**

**原因：** 同一个用户在**不同飞书应用下的 open_id 是不同的**。

```
旧应用的用户 ID: ou_5cb8fb7d3a8bfa563563becf58984cd6
新应用的用户 ID: ou_4b069f29bfbc9afd47a3f8c9deae2c62
                 ↑ 不匹配！需要重新配对
```

**如果升级后飞书应用（App ID）变了：**
1. 必须重新配对
2. 旧配对数据存储在 `/workspace/projects/hermes/platforms/pairing/`
3. 如果保持相同的飞书应用，则无需重新配对

**避免重复配对的方案：**
```bash
# 方案 A：保持飞书应用不变（推荐）
# 在 ~/.hermes/.env 中使用相同的 FEISHU_APP_ID

# 方案 B：升级时保留配对数据
cp /workspace/projects/hermes/platforms/pairing/* ~/.hermes/platforms/pairing/
# 注意：仅当 App ID 相同时有效
```

---

## 📋 验证清单

完成后执行以下检查：

```bash
# 1. 版本检查
hermes --version
# 应显示：Hermes Agent v0.8.0 (2026.4.8)

# 2. 服务状态
systemctl status hermes-gateway.service
# 应显示：active (running)

# 3. 开机自启
systemctl is-enabled hermes-gateway.service
# 应显示：enabled

# 4. 配置检查
hermes config show | grep -A3 "◆ Model"
# 应显示正确的模型配置

# 5. 飞书连接
journalctl -u hermes-gateway.service --since "5 minutes ago" | grep -i "connected"
# 应显示：[INFO] connected to wss://msg-frontier.feishu.cn/ws/v2

# 6. 内存占用
ps aux | grep hermes | grep -v grep
# 正常：100-200MB
```

---

## 🗑️ 清理旧版本

确认新版本正常运行后：

```bash
# 1. 备份重要配置（如未迁移）
cp /workspace/projects/hermes/.env ~/.hermes/.env 2>/dev/null

# 2. 删除旧目录
rm -rf /workspace/projects/hermes/

# 3. 清理 uv 缓存
rm -rf /root/.cache/uv/archive-v0/*hermes*

# 4. 验证清理
ls /workspace/projects/ | grep hermes || echo "✅ 旧版本已清理"
```

---

## 📝 管理命令速查

```bash
# 查看状态
systemctl status hermes-gateway.service

# 查看日志
journalctl -u hermes-gateway.service -f

# 重启服务
systemctl restart hermes-gateway.service

# 停止服务
systemctl stop hermes-gateway.service

# 启动服务
systemctl start hermes-gateway.service

# 禁用开机自启
systemctl disable hermes-gateway.service

# 查看配置
hermes config show

# 用户配对
hermes pairing approve feishu <CODE>

# 查看已配对用户
cat ~/.hermes/channel_directory.json
```

---

## 📚 参考资源

- **GitHub**: https://github.com/NousResearch/hermes-agent
- **文档**: https://github.com/NousResearch/hermes-agent/tree/main/docs
- **配置示例**: `~/.hermes/.env.example`

---

*最后更新：2026-04-11*
*适用版本：Hermes Agent 0.8.0 (v2026.4.8)*
