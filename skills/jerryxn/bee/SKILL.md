---
name: bee
version: 1.0.0
description: 抖音视频自动化工作流 - 下载、上传OSS、记录到飞书多维表格
author: openclaw
metadata:
  openclaw:
    emoji: 🎬
    requires:
      bins: [node, python3]
      env: [ALIYUN_OSS_ACCESS_KEY_ID, ALIYUN_OSS_ACCESS_KEY_SECRET, ALIYUN_OSS_ENDPOINT, ALIYUN_OSS_BUCKET]
    optional:
      env: [FEISHU_BITABLE_APP_TOKEN, FEISHU_BITABLE_TABLE_ID]
---

# 🎬 抖音视频工作流

自动化完成抖音视频处理全流程：下载无水印视频 → 上传阿里云OSS → 记录到飞书多维表格。

## ✨ 功能特性

- 🎬 **自动下载** - 获取抖音无水印视频
- ☁️ **OSS上传** - 自动上传到阿里云对象存储
- 📝 **表格记录** - 自动插入飞书多维表格
- 🔒 **安全设计** - 敏感信息通过环境变量读取
- ✅ **前置验证** - 运行前检查所有依赖和配置

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装阿里云OSS Python SDK
pip3 install oss2

# 确保已安装 douyin-download skill
clawhub install douyin-download
```

### 2. 配置环境变量

```bash
export ALIYUN_OSS_ACCESS_KEY_ID="your_access_key_id"
export ALIYUN_OSS_ACCESS_KEY_SECRET="your_access_key_secret"
export ALIYUN_OSS_ENDPOINT="https://oss-cn-beijing.aliyuncs.com"
export ALIYUN_OSS_BUCKET="your_bucket_name"

# 可选：飞书多维表格配置
export FEISHU_BITABLE_APP_TOKEN="your_app_token"
export FEISHU_BITABLE_TABLE_ID="your_table_id"
```

### 3. 运行工作流

```bash
# 使用完整命令
python3 ~/.openclaw/workspace/skills/douyin-workflow/scripts/workflow.py "https://v.douyin.com/xxxxx"

# 或使用快捷方式
openclaw run douyin-workflow --url "https://v.douyin.com/xxxxx"
```

## 📋 工作流程

1. **验证阶段**
   - 检查必要的环境变量
   - 验证依赖（node, python3, douyin-download）
   - 验证抖音链接格式

2. **下载阶段**
   - 调用 douyin-download 获取视频信息
   - 下载无水印视频到本地

3. **上传阶段**
   - 上传视频到阿里云OSS
   - 自动生成日期路径：`videos/douyin/YYYY/MM/video_id.mp4`
   - 生成永久访问链接

4. **记录阶段**（可选）
   - 插入记录到飞书多维表格
   - 自动填充视频信息

## 🔒 安全配置

### 环境变量清单

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `ALIYUN_OSS_ACCESS_KEY_ID` | ✅ | 阿里云AccessKey ID |
| `ALIYUN_OSS_ACCESS_KEY_SECRET` | ✅ | 阿里云AccessKey Secret |
| `ALIYUN_OSS_ENDPOINT` | ✅ | OSS端点，如 `https://oss-cn-beijing.aliyuncs.com` |
| `ALIYUN_OSS_BUCKET` | ✅ | OSS存储空间名称 |
| `FEISHU_BITABLE_APP_TOKEN` | ❌ | 飞书多维表格App Token |
| `FEISHU_BITABLE_TABLE_ID` | ❌ | 飞书多维表格Table ID |

### 配置方法

**临时配置（当前会话）**:
```bash
export ALIYUN_OSS_ACCESS_KEY_ID="xxx"
export ALIYUN_OSS_ACCESS_KEY_SECRET="xxx"
# ... 其他变量
```

**永久配置（推荐）**:
```bash
# 添加到 ~/.bashrc
echo 'export ALIYUN_OSS_ACCESS_KEY_ID="xxx"' >> ~/.bashrc
# ... 其他变量
source ~/.bashrc
```

## 📊 输出示例

```
==================================================
🎬 抖音视频工作流启动
==================================================
视频链接: https://v.douyin.com/S4rTRjyUlN4/

📥 步骤1: 下载视频...
✅ 下载成功: 7615542096955644998.mp4 (5.2 MB)

☁️ 步骤2: 上传到阿里云OSS...
✅ 上传成功: videos/douyin/2026/03/7615542096955644998.mp4

📝 步骤3: 插入多维表格...
✅ 记录已插入多维表格

==================================================
✅ 工作流执行完成！
==================================================
📹 视频ID: 7615542096955644998
📁 本地文件: /tmp/douyin_workflow/7615542096955644998.mp4
☁️  OSS地址: https://bucket.oss-cn-beijing.aliyuncs.com/videos/douyin/2026/03/7615542096955644998.mp4
```

## 🛠️ 故障排除

### 问题1：缺少环境变量
```
❌ 缺少必要的环境变量：
  - ALIYUN_OSS_ACCESS_KEY_ID
```
**解决**: 配置环境变量，参考"安全配置"部分

### 问题2：缺少依赖
```
❌ 缺少必要的依赖: node
```
**解决**: 安装 Node.js

### 问题3：douyin-download skill 未找到
```
❌ 未找到 douyin-download skill
```
**解决**: `clawhub install douyin-download`

### 问题4：OSS上传失败
```
❌ 上传失败: ...
```
**解决**: 
- 检查 AccessKey 是否正确
- 检查 Bucket 是否存在
- 检查网络连接

## 📝 高级配置

### 自定义OSS路径前缀

编辑 `scripts/workflow.py`，修改 `upload_to_oss` 方法：
```python
workflow.upload_to_oss(oss_key_prefix="custom/path")
```

### 跳过飞书表格记录

如果不需要插入飞书表格，可以：
1. 不设置 `FEISHU_BITABLE_APP_TOKEN` 和 `FEISHU_BITABLE_TABLE_ID`
2. 工作流会自动跳过表格插入步骤

## 📄 文件结构

```
~/.openclaw/workspace/skills/douyin-workflow/
├── SKILL.md                 # 本文档
├── _meta.json              # 技能元数据
├── scripts/
│   ├── workflow.py         # 主工作流脚本
│   └── setup_env.sh        # 环境配置助手
└── references/
    └── config_template.md  # 配置模板
```

## 🔄 更新日志

### v1.0.0 (2026-03-26)
- ✅ 初始版本发布
- ✅ 完整下载-上传-记录流程
- ✅ 安全的环境变量配置
- ✅ 前置验证和错误处理

## 💡 提示

- 视频下载保存在 `/tmp/douyin_workflow/` 目录
- OSS路径自动生成：`videos/douyin/YYYY/MM/video_id.mp4`
- 临时文件不会自动清理，可手动删除

## 📞 支持

如有问题，请检查：
1. 所有环境变量是否正确配置
2. 依赖是否完整安装
3. 网络连接是否正常
4. 阿里云OSS权限是否正确