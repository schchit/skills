---
name: openclaw-sync
description: |
  OpenClaw 数据实时同步技能。使用 inotify 监控文件变化，自动将记忆数据、
  配置文件同步到云对象存储（七牛云/腾讯云/阿里云），实现数据持久化。
metadata:
  {
    "openclaw":
      {
        "emoji": "🔄",
        "requires": { "bins": ["rclone", "inotifywait", "python3"] },
        "install":
          [
            { "id": "rclone", "kind": "bin", "package": "rclone", "label": "Install rclone" },
            { "id": "inotify-tools", "kind": "apt", "package": "inotify-tools", "label": "Install inotify-tools" },
          ],
      },
  }
---

# 🔄 OpenClaw 实时同步技能

使用 **inotify** 实时监控文件变化，自动同步到云对象存储。

---

## 🎯 支持的云服务商

| 云服务商 | 免费额度 | 推荐指数 |
|---------|---------|---------|
| **七牛云 Kodo** | 每月 10GB | ⭐⭐⭐⭐⭐ |
| **腾讯云 COS** | 6个月 50GB | ⭐⭐⭐⭐ |
| **阿里云 OSS** | 无 | ⭐⭐⭐ |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 rclone
curl https://rclone.org/install.sh | bash

# 安装 inotify-tools（实时监控必需）
apt-get install inotify-tools
```

### 2. 配置云存储

```bash
cd config/

# 选择云服务商，复制配置模板
cp rclone-qiniu.conf.example rclone.conf
cp backup-qiniu.json.example backup.json

# 编辑配置文件
vim rclone.conf
vim backup.json
```

### 3. 启动实时同步

**方式一：手动启动**
```bash
bash scripts/sync-monitor.sh
```

**方式二：systemd 服务（推荐）**
```bash
# 复制服务文件
sudo cp systemd/openclaw-sync.service /etc/systemd/system/

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable openclaw-sync
sudo systemctl start openclaw-sync

# 查看状态
sudo systemctl status openclaw-sync
sudo journalctl -u openclaw-sync -f
```

---

## 📋 常用命令

| 命令 | 说明 |
|------|------|
| `sync-now.sh` | 立即手动同步 |
| `sync-monitor.sh` | 启动实时监控 |
| `list-remote.sh` | 查看云端文件 |
| `restore.sh` | 恢复数据 |
| `test-config.sh` | 测试配置 |

---

## 📁 同步的数据

默认同步（可在 `data/sync-list.txt` 中修改）：
- **核心数据**：MEMORY.md, memory/, USER.md, IDENTITY.md, SOUL.md
- **配置文件**：AGENTS.md, TOOLS.md, HEARTBEAT.md
- **技能配置**：skills/*/config.json

---

## 🎨 多实例支持

支持多个 OpenClaw 实例共享一个存储桶：

```
云存储桶
├── instance-main/        # 主服务器
├── instance-dev/         # 开发服务器
└── instance-烧烤店/       # 业务服务器
```

---

## 🔧 服务管理

```bash
# 查看状态
sudo systemctl status openclaw-sync

# 查看日志
sudo journalctl -u openclaw-sync -f

# 停止服务
sudo systemctl stop openclaw-sync

# 重启服务
sudo systemctl restart openclaw-sync
```

---

## 📄 许可证

MIT License
