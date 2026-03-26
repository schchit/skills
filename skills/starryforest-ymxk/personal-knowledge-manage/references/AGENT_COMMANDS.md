# Agent 命令参考文档

## 目录
1. [快速命令别名](#快速命令别名)
2. [同步命令](#同步命令)
3. [Obsidian CLI 命令](#obsidian-cli-命令)
4. [笔记搜索命令](#笔记搜索命令)
5. [脚本目录](#脚本目录)
6. [配置文件](#配置文件)
7. [使用示例](#使用示例)

---

## 快速命令别名

### Obsidian 相关
```bash
obs-ls              # 列出所有笔记
obs-print            # 打印笔记内容
```

### Rclone 同步相关
```bash
rclone-sync           # 安全双向同步（推荐）
rclone-push           # 单向推送本地修改到 OneDrive
rclone-ls             # 列出 OneDrive 文件
rclone-check          # 检查本地和远程差异
```

### 笔记搜索
```bash
search-notes          # 搜索笔记（文件名/内容）
```

---

## 同步命令

### rclone-sync - 安全双向同步

**功能**: 从 OneDrive 拉取更新 + 推送本地修改到 OneDrive

**安全特性**:
- ✅ 使用 `--update` 标志，只更新较旧的文件
- ✅ 保留本地较新的文件，不会被覆盖
- ✅ 不会删除任何文件
- ✅ 排除 `.obsidian` 目录

**使用方法**:
```bash
rclone-sync
```

**适用场景**:
- 多设备协作
- 本地和远程都有修改
- 需要自动同步

---

### rclone-push - 单向推送

**功能**: 将本地修改推送到 OneDrive

**安全特性**:
- ✅ 使用 `--update` 标志
- ✅ 只更新较旧的远程文件
- ✅ 排除 `.obsidian` 目录

**使用方法**:
```bash
rclone-push
```

**适用场景**:
- 服务器主要作为编辑器
- 需要推送本地修改
- 不想拉取远程更新

---

### rclone-ls - 列出远程文件

**功能**: 列出 OneDrive 上的文件

**使用方法**:
```bash
rclone-ls
```

---

### rclone-check - 检查差异

**功能**: 比较本地和 OneDrive 文件的差异

**排除**: `.obsidian` 目录

**使用方法**:
```bash
rclone-check
```

**输出说明**:
- 0 differences = 完全一致
- ERROR 信息 = 差异详情

---

## Obsidian CLI 命令

### obs-ls - 列出笔记

**功能**: 列出 vault 中的所有笔记和目录

**使用方法**:
```bash
obs-ls
```

**输出示例**:
```
• 工作/
• 游戏/
• 综合/
```

---

### obs-print - 打印笔记

**功能**: 打印笔记的完整内容

**使用方法**:
```bash
obs-print "笔记名称"
obs-print "综合/摄影/摄影欣赏/一名空间摄影师的旅行随拍.md"
```

---

## 笔记搜索命令

### search-notes - 笔记搜索

**功能**: 搜索笔记文件名或内容

**使用方法**:
```bash
# 按文件名搜索（默认）
search-notes 摄影主题

# 按内容搜索
search-notes 摄影 -c

# 按内容搜索并显示匹配行
search-notes 摄影 -c -v
```

**选项**:
- `-n, --name`: 按文件名搜索
- `-c, --content`: 按内容搜索
- `-v, --verbose`: 显示匹配行

**输出示例**:
```
在 vault 中搜索: 摄影
搜索模式: content
==========================================
✓ 综合/摄影/摄影欣赏/IDaily新闻照片欣赏（照片的故事性）.md
✓ 综合/摄影/摄影积累/好的照片都是设计出来的.md
==========================================
```

---

## 脚本目录

### ~/scripts/ - 主脚本目录

```
scripts/
├── configure-rclone.sh          # Rclone OneDrive 配置向导
├── search-notes.sh              # 笔记搜索脚本
├── search-notes.sh.unsafe       # 旧版搜索脚本（已禁用）
├── sync-notes.sh                # 安全双向同步脚本（主）
├── sync-notes.sh.unsafe         # 危险的双向同步脚本（已禁用）
├── sync-to-onedrive.sh         # 反向同步脚本
├── obsidian/                    # Obsidian 相关脚本
│   ├── obsidian-search.sh       # Obsidian 搜索脚本
│   └── obsidian-search-functions.sh  # Obsidian 搜索函数
└── search/                      # 搜索相关脚本
    └── vault-search.sh         # Vault 搜索脚本
```

---

## 配置文件

### ~/.bashrc-rclone-override - 命令别名

**内容**:
- Rclone 命令别名（安全模式）
- Obsidian CLI 命令别名
- 笔记搜索命令别名

---

### ~/.bash_profile - 登录 Shell 配置

**功能**:
- 清理 PATH 中的重复项
- 设置 PATH 顺序
- 加载所有配置文件

---

### ~/.bashrc - 交互式 Shell 配置

**功能**:
- TERM 修复（dumb -> xterm-256color）
- 加载别名和配置

---

### ~/.config/obsidian-cli/vaults.json - Obsidian CLI Vault 配置

**内容**:
```json
{
  "vaults": [
    {
      "name": "PersonalKnowledge",
      "path": "/data/wudi/PersonalKnowledge"
    }
  ],
  "defaultVault": "PersonalKnowledge"
}
```

---

## 路径说明

### 本地 Vault
- **路径**: `/data/wudi/PersonalKnowledge`
- **结构**:
  ```
  PersonalKnowledge/
  ├── 工作/
  ├── 游戏/
  └── 综合/
  ```

### OneDrive 远程路径
- **路径**: `/应用/Graph/Personal Knowledge`
- **Rclone 名称**: `onedrive`

### 日志目录
- **路径**: `~/logs/`
- **日志文件**:
  - `sync-safe.log` - 安全双向同步日志
  - `sync-to-onedrive.log` - 反向同步日志
  - `sync-cron.log` - Cron 任务日志

---

## 使用示例

### 场景 1: 搜索笔记

```bash
# 搜索摄影相关笔记（按内容）
search-notes 摄影 -c

# 查看具体笔记
obs-print "综合/摄影/摄影欣赏/IDaily新闻照片欣赏（照片的故事性）.md"
```

---

### 场景 2: 编辑笔记后同步

```bash
# 方法 1: 安全双向同步（推荐）
rclone-sync

# 方法 2: 单向推送
rclone-push
```

---

### 场景 3: 检查同步状态

```bash
# 检查差异
rclone-check

# 查看远程文件
rclone-ls
```

---

### 场景 4: 查看 vault 结构

```bash
# 列出所有笔记
obs-ls
```

---

## 安全特性总结

### 所有同步命令都具备

| 特性 | 说明 |
|------|------|
| `--update` 标志 | 只更新较旧的文件，保留较新文件 |
| `--exclude ".obsidian/**"` | 排除 Obsidian 配置目录 |
| 不删除文件 | 不会删除本地或远程的任何文件 |
| 详细日志 | 所有操作记录到日志文件 |

---

## Cron 自动化

### 当前配置

```bash
# 每小时执行安全双向同步
0 * * * * ~/scripts/sync-notes.sh >> ~/logs/sync-safe.log 2>&1
```

### 修改 Cron

```bash
crontab -e

# 选项 1: 安全双向同步（推荐）
0 * * * * ~/scripts/sync-notes.sh >> ~/logs/sync-safe.log 2>&1

# 选项 2: 单向拉取（最安全）
0 * * * * ~/scripts/sync-notes.sh --reverse >> ~/logs/sync-cron.log 2>&1

# 选项 3: 不自动同步（手动控制）
# 注释掉或删除 cron 任务
```

---

## 快速参考表

| 命令 | 功能 | 安全性 |
|------|------|--------|
| `obs-ls` | 列出笔记 | ✅ 安全 |
| `obs-print` | 打印笔记 | ✅ 安全 |
| `search-notes` | 搜索笔记 | ✅ 安全 |
| `rclone-sync` | 双向同步 | ✅ 安全（--update） |
| `rclone-push` | 推送修改 | ✅ 安全（--update） |
| `rclone-ls` | 列出远程 | ✅ 安全 |
| `rclone-check` | 检查差异 | ✅ 安全 |

---

## 故障排查

### 命令不存在

**问题**: `command not found`

**解决**:
```bash
# 重新加载配置
source ~/.bash_profile

# 或重新登录
exit
ssh wudi@10.103.14.63
```

---

### 同步失败

**问题**: `✗ 同步失败！`

**解决**:
```bash
# 查看日志
tail -50 ~/logs/sync-safe.log

# 检查网络连接
rclone ls onedrive:/应用/Graph/Personal Knowledge
```

---

### Obsidian CLI 错误

**问题**: `obsidian-cli: command not found`

**解决**:
```bash
# 检查 PATH
which obsidian-cli

# 如果找不到，重新加载配置
source ~/.bash_profile
```

---

## 版本信息

- Rclone: v1.68.2
- obsidian-cli: v0.2.3
- Ubuntu: 22.04.5 LTS

---

**文档更新时间**: 2026-02-06 21:00:00

**维护者**: Agent 系统管理员
