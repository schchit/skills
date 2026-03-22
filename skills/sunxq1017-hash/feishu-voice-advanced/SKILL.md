---
name: feishu-voice-advanced
description: |
  🎙️ 飞书语音消息发送 Skill | Feishu Voice Message Sender
  
  当用户要求发送飞书语音消息、用语音回复、或者提到"发语音""语音消息""voice message"时使用此 Skill。
  
  Use this skill when the user asks to: send voice messages via Feishu/Lark, reply with voice, "send voice", "voice message", or any voice-related messaging requests.
  
  功能：语音合成(TTS)生成语音并发送到飞书，支持情绪感知播报。
  Features: Text-to-speech generation and sending to Feishu with emotional voice synthesis.
---

# Feishu Voice Advanced 🎙️

> 让 OpenClaw 听懂你的声音，感受你的情绪  
> Let OpenClaw hear your voice, feel your emotion

飞书语音消息高级处理 Skill，支持接收语音、语音识别(ASR)、语音合成(TTS)发送语音消息，支持智能情绪播报。

## 触发条件

当用户说以下话时，自动使用此 Skill：
- "发语音给..."
- "用语音回复"
- "发送语音消息"
- "voice message"
- "send voice"
- 任何包含"语音"+"发送/发/回复"的请求

## AI 使用方法

当触发条件满足时，使用以下方式发送语音：

```python
import sys
sys.path.insert(0, 'scripts')
from feishu_voice import send

# 发送语音消息
send(
    text="要播报的内容",
    user_input="用户的原始请求（用于情绪感知）"
)
```

**参数说明：**
- `text`: AI 生成的播报内容
- `user_input`: 用户的原始输入，用于让豆包感知情绪（可选）

**示例：**
```python
# 用户说："用激动的语气发语音说项目成功了"
send(
    text="项目成功了！我们超额完成了目标！",
    user_input="用激动的语气发语音说项目成功了"
)
```

## 功能特性

- 🎙️ **接收语音消息** - 自动接收飞书语音消息
- 🎯 **语音识别(ASR)** - 使用豆包极速版 ASR 将语音转为文字
- 🗣️ **语音合成(TTS)** - 使用豆包 TTS 2.0 生成语音
- 🎭 **智能情绪播报** - 使用 `context_texts` 让模型自动判断情绪

## 情绪控制规则 (V1.1)

### 核心原则
**默认使用引用上文**，让豆包模型从用户输入中自动感知情绪。

### 两层逻辑

| 条件 | 处理方式 | 说明 |
|------|---------|------|
| 用户输入以 `[#...]` 开头 | 原样使用，无 `context_texts` | 显式指令，如 `[#用激动的语气说]` |
| 其他情况 | `context_texts` = [用户输入] | 模型从用户输入中感知情绪 |

### 工作原理

- **`text`**: AI 生成的实际播报内容
- **`context_texts`**: 用户原始输入，作为情绪参考（不计费）

豆包模型从 `context_texts` 中理解语境情绪，用相应语气播报 `text`。

## 使用方法

### 1. 接收并识别语音

```python
from feishu_voice import FeishuVoice

voice = FeishuVoice()
text = voice.recognize_voice("/path/to/audio.ogg")
print(f"识别结果: {text}")
```

### 2. 发送语音消息（推荐方式）

```python
from feishu_voice import send

# 方式1：AI生成内容 + 用户输入（用 context_texts）
# 模型从 user_input 中感知情绪，用相应语气播报 text
send(
    text="对不起桥总，是我太笨了，我深刻检讨！",
    user_input="你怎么回事，这么笨，给我做个检讨"
)

# 方式2：显式指令（不用 context_texts）
send("[#用激动的语气说]我们成功了！")
```

### 3. 完整示例

```python
from feishu_voice import FeishuVoice

voice = FeishuVoice()

# 场景1：被批评后检讨
user_input = "你真笨，这么点事都做不好，用飞书语音给我发一段检讨"
ai_response = "桥总，对不起！我确实太笨了，连这么简单的事情都做不好。我深刻反省，一定改进！"
voice.send_voice(ai_response, user_input=user_input)

# 场景2：被表扬后汇报
user_input = "你真棒，汇报一下本周成果"
ai_response = "本周我们完成了三个重要项目，超额完成目标！"
voice.send_voice(ai_response, user_input=user_input)

# 场景3：显式指令
voice.send_voice("[#用低沉沙哑的语气说]高兄，你看这烛火，要灭了...")
```

## API 说明

### `send(text, receive_id, emotion, user_input)`

发送语音消息（便捷函数）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `text` | string | 是 | AI 生成的实际播报内容 |
| `receive_id` | string | 否 | 接收者 ID，默认当前用户 |
| `emotion` | string | 否 | 情绪类型，默认 `auto` |
| `user_input` | string | 否 | 用户原始输入，用于 `context_texts` |

### `FeishuVoice.send_voice(text, receive_id, emotion, user_input)`

类方法，功能同上。

### `FeishuVoice.generate_voice(text, emotion, context)`

生成语音文件，返回 Opus 文件路径。

| 参数 | 类型 | 说明 |
|------|------|------|
| `text` | string | AI 生成的播报内容 |
| `emotion` | string | 情绪类型 |
| `context` | string | 用户原始输入，用于 `context_texts` |

### `FeishuVoice.recognize_voice(audio_path)`

识别语音文件，返回文字。

## 技术细节

### TTS Payload 结构

```json
{
  "user": {"uid": "12345"},
  "event": 100,
  "req_params": {
    "text": "实际播报内容",
    "speaker": "zh_male_m191_uranus_bigtts",
    "audio_params": {
      "format": "mp3",
      "sample_rate": 24000
    },
    "additions": "{\"context_texts\": [\"用户原始输入\"]}"
  }
}
```

**注意：** `additions` 必须是 JSON 字符串，不是 object。

### 与 `[#...]` 语法的区别

| 方式 | 字段 | 说明 |
|------|------|------|
| `[#...]` | `text` | 直接拼接在 text 前，如 `[#用激动的语气说]内容` |
| `context_texts` | `additions` | 独立参数，让模型理解语境后自动选择情绪 |

推荐使用 `context_texts`，更灵活自然。

## 配置

⚠️ **使用前必须配置**：修改 `scripts/feishu_voice.py` 中的 API 密钥

```python
# 豆包 ASR 配置 (从火山引擎获取)
ASR_APP_ID = "your-asr-app-id"
ASR_ACCESS_KEY = "your-asr-access-key"

# 豆包 TTS 配置 (从火山引擎获取)
TTS_APP_ID = "your-tts-app-id"
TTS_ACCESS_KEY = "your-tts-access-key"

# 飞书配置 (从飞书开放平台获取)
FEISHU_APP_ID = "your-feishu-app-id"
FEISHU_APP_SECRET = "your-feishu-app-secret"
```

## 依赖

- ffmpeg（用于音频格式转换）
- Python 3.8+

## 安装 | Installation

```bash
cd scripts
chmod +x install.sh
./install.sh
```

**Dependencies:** ffmpeg, Python 3.8+

**Note:** Scripts are located in the `scripts/` directory.

## 更新日志

### V1.1.1 (2026-03-22)
- 安全配置：移除示例中的真实 APP_ID，改为占位符
- 新增配置说明文档，引导用户配置自己的 API 密钥

### V1.1 (2026-03-22)
- 新增 `context_texts` 支持，使用豆包引用上文功能
- 改进情绪控制逻辑：默认使用引用上文，让模型自动判断情绪
- 简化 API：`user_input` 参数替代复杂的情绪映射
- 修复 `additions` 格式问题（必须是 JSON 字符串）

### V1.0
- 基础语音收发功能
- ASR 语音识别
- TTS 语音合成
- 简单情绪映射

EOF
