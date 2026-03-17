---
name: ezviz-audio-broadcast
description: 萤石语音广播技能。支持本地音频文件上传或文本转语音，实现语音内容下发到设备播放。Use when: 需要向萤石设备发送语音通知、广播、提醒等音频内容。
metadata:
  openclaw:
    emoji: "🔊"
    requires: { "env": ["EZVIZ_APP_KEY", "EZVIZ_APP_SECRET", "EZVIZ_DEVICE_SERIAL"], "pip": ["requests"] }
    primaryEnv: "EZVIZ_APP_KEY"
---

# Ezviz Audio Broadcast (萤石语音广播)

通过萤石语音上传和下发接口，实现语音内容到设备的广播播放。

## 快速开始

### 安装依赖

```bash
pip install requests
```

### 设置环境变量

```bash
export EZVIZ_APP_KEY="your_app_key"
export EZVIZ_APP_SECRET="your_app_secret"
export EZVIZ_DEVICE_SERIAL="dev1,dev2,dev3"
```

可选环境变量：
```bash
export EZVIZ_CHANNEL_NO="1" # 通道号，默认 1
export EZVIZ_AUDIO_FILE="/path/to/audio.mp3" # 本地音频文件路径（二选一）
export EZVIZ_TEXT_CONTENT="语音内容文本" # 文本内容（二选一）
export EZVIZ_VOICE_NAME="custom_name" # 自定义语音名称
```

**注意**: 
- 不需要设置 `EZVIZ_ACCESS_TOKEN`！技能会自动获取 Token
- 必须提供 `EZVIZ_AUDIO_FILE` 或 `EZVIZ_TEXT_CONTENT` 其中一个
- 设备需要支持对讲功能（`support_talk=1或3`）

### 运行

```bash
python3 {baseDir}/scripts/audio_broadcast.py
```

命令行参数：
```bash
# 使用本地音频文件
python3 {baseDir}/scripts/audio_broadcast.py appKey appSecret dev1 /path/to/audio.mp3 [channel_no]

# 使用文本内容（自动生成语音）
python3 {baseDir}/scripts/audio_broadcast.py appKey appSecret dev1 "语音内容文本" [channel_no]
```

## 工作流程

```
1. 获取 Token (appKey + appSecret → accessToken)
 ↓
2a. 如果提供音频文件：直接上传文件
2b. 如果提供文本：调用TTS生成音频文件，然后上传
 ↓
3. 下发语音 (accessToken + deviceSerial + fileUrl → 设备播放)
 ↓
4. 输出结果 (JSON + 控制台)
```

## Token 自动获取说明

**你不需要手动获取或配置 `EZVIZ_ACCESS_TOKEN`！**

技能会自动处理 Token 的获取：

```
每次运行:
 appKey + appSecret → 调用萤石 API → 获取 accessToken (有效期 7 天)
 ↓
使用 Token 完成本次请求
 ↓
Token 在内存中使用，不保存到磁盘
```

**Token 管理特性**:
- ✅ **自动获取**: 每次运行自动调用萤石 API 获取
- ✅ **有效期 7 天**: 获取的 Token 7 天内有效
- ✅ **无需配置**: 不需要手动设置 `EZVIZ_ACCESS_TOKEN` 环境变量
- ✅ **安全**: Token 不写入日志，不保存到磁盘
- ⚠️ **注意**: 每次运行会重新获取 Token（不跨运行缓存）

## 输出示例

```
======================================================================
Ezviz Audio Broadcast Skill (萤石语音广播)
======================================================================
[Time] 2026-03-16 16:30:00
[INFO] Target devices: 2
 - dev1 (Channel: 1)
 - dev2 (Channel: 1)
[INFO] Mode: Text-to-Speech
[INFO] Content: 接下来插播一个广告

======================================================================
[Step 1] Getting access token...
[SUCCESS] Token obtained, expires: 2026-03-23 16:30:00

======================================================================
[Step 2] Generating and uploading audio...
[INFO] Generated TTS file: /tmp/ezviz_tts_12345.mp3
[SUCCESS] Audio uploaded successfully!
[INFO] Voice Name: ad_broadcast
[INFO] File URL: https://oss-cn-shenzhen.aliyuncs.com/voice/...

======================================================================
[Step 3] Broadcasting audio to devices...
======================================================================

[Device] dev1 (Channel: 1)
[SUCCESS] Audio broadcast completed!

[Device] dev2 (Channel: 1)  
[SUCCESS] Audio broadcast completed!

======================================================================
BROADCAST SUMMARY
======================================================================
 Total devices: 2
 Success: 2
 Failed: 0
======================================================================
```

## 多设备格式

| 格式 | 示例 | 说明 |
|------|------|------|
| 单设备 | `dev1` | 默认通道 1 |
| 多设备 | `dev1,dev2,dev3` | 全部使用默认通道 |
| 指定通道 | `dev1:1,dev2:2` | 每个设备独立通道 |
| 混合 | `dev1,dev2:2,dev3` | 部分指定通道 |

## API 接口

| 接口 | URL | 文档 |
|------|-----|------|
| 获取 Token | `POST /api/lapp/token/get` | https://open.ys7.com/help/81 |
| 语音上传 | `POST /api/lapp/voice/upload` | https://open.ys7.com/help/1241 |
| 语音下发 | `POST /api/lapp/voice/send` | https://open.ys7.com/help/1253 |

## 网络端点

| 域名 | 用途 |
|------|------|
| `open.ys7.com` | 萤石开放平台 API（Token、语音上传、下发） |

## 音频要求

| 格式 | 支持 | 限制 |
|------|------|------|
| WAV | ✅ | 最大5MB，最长60秒 |
| MP3 | ✅ | 最大5MB，最长60秒 |
| AAC | ✅ | 最大5MB，最长60秒 |

## 注意事项

⚠️ **设备兼容性**: 设备必须支持对讲功能（`support_talk=1或3`），否则返回错误码 `20015`

⚠️ **频率限制**: 语音下发接口有调用频率限制，建议设备间间隔1秒以上

⚠️ **文件大小**: 音频文件不能超过5MB，时长不能超过60秒

⚠️ **Token 安全**: Token 仅在内存中使用，不写入日志，不发送到非萤石端点

⚠️ **TTS依赖**: 文本转语音功能依赖系统TTS服务，确保系统支持

## 数据流出说明

**本技能会向第三方服务发送数据**：

| 数据类型 | 发送到 | 用途 | 是否必需 |
|----------|--------|------|----------|
| 音频文件 | `open.ys7.com` (萤石) | 语音上传和下发 | ✅ 必需 |
| appKey/appSecret | `open.ys7.com` (萤石) | 获取访问 Token | ✅ 必需 |
| 设备序列号 | `open.ys7.com` (萤石) | 请求下发 | ✅ 必需 |
| **EZVIZ_ACCESS_TOKEN** | **自动生成** | **每次运行自动获取** | **✅ 自动** |

**数据流出说明**:
- ✅ **萤石开放平台** (`open.ys7.com`): 所有API调用 - 萤石官方 API
- ❌ **无其他第三方**: 不会发送数据到其他服务

**凭证权限建议**:
- 使用**最小权限**的 appKey/appSecret
- 仅开通必要的 API 权限（语音上传、下发）
- 定期轮换凭证
- 不要使用主账号凭证

**本地处理**:
- ✅ Token 在内存中使用，不写入磁盘
- ✅ TTS临时文件自动清理
- ✅ 不记录完整 API 响应

## 应用场景

| 场景 | 说明 |
|------|------|
| 📢 安全广播 | 向监控区域发送安全提醒、紧急通知 |
| 🏢 办公通知 | 办公室广播会议提醒、访客通知 |
| 🏪 商业应用 | 商店促销广播、排队叫号 |
| 🏠 智能家居 | 家庭语音提醒、门铃通知 |
| 🏭 工厂管理 | 生产线通知、安全警示 |

## 使用示例

**场景1: 紧急安全通知**
```bash
python3 audio_broadcast.py your_key your_secret "kitchen_cam,dining_area" "注意！检测到安全隐患，请立即检查！"
```

**场景2: 商业促销广播**
```bash
export EZVIZ_TEXT_CONTENT="欢迎光临！今日特价商品限时优惠，详情请咨询店员！"
export EZVIZ_DEVICE_SERIAL="store_front,store_back"
python3 audio_broadcast.py
```

**场景3: 使用预录制音频**
```bash
python3 audio_broadcast.py your_key your_secret entrance_cam /path/to/welcome_message.mp3
```
