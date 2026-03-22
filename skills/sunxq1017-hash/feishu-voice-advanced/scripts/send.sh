#!/bin/bash
# Feishu Voice Message Sender
# Usage: ./send.sh "text content" [receiver_id] [speaker]
# 
# ⚠️ 使用前必须配置以下环境变量或修改本文件：
# - TTS_APP_ID: 豆包语音 APP ID
# - TTS_ACCESS_KEY: 豆包语音 Access Key
# - FEISHU_APP_ID: 飞书 App ID
# - FEISHU_APP_SECRET: 飞书 App Secret

TEXT="$1"
RECEIVER_ID="${2:-}"
SPEAKER="${3:-zh_male_m191_uranus_bigtts}"

# 配置（请修改为你的实际配置）
TTS_APP_ID="${TTS_APP_ID:-your-tts-app-id}"
TTS_ACCESS_KEY="${TTS_ACCESS_KEY:-your-tts-access-key}"
FEISHU_APP_ID="${FEISHU_APP_ID:-your-feishu-app-id}"
FEISHU_APP_SECRET="${FEISHU_APP_SECRET:-your-feishu-app-secret}"

if [ -z "$TEXT" ]; then
    echo "Usage: $0 \"text content\" [receiver_id] [speaker]"
    echo "Example: $0 \"Hello, this is Tyrion.\" ou_xxx"
    echo ""
    echo "⚠️  使用前请配置 API 密钥："
    echo "   方式1：设置环境变量 TTS_APP_ID, TTS_ACCESS_KEY, FEISHU_APP_ID, FEISHU_APP_SECRET"
    echo "   方式2：直接修改本文件中的默认值"
    exit 1
fi

if [ -z "$RECEIVER_ID" ]; then
    echo "❌ 错误：必须提供接收者 ID (receiver_id)"
    echo "Usage: $0 \"text content\" receiver_id [speaker]"
    exit 1
fi

# 检查是否为占位符
if [ "$TTS_APP_ID" = "your-tts-app-id" ] || [ "$TTS_ACCESS_KEY" = "your-tts-access-key" ]; then
    echo "❌ 错误：请先配置豆包语音 API 密钥"
    echo "请修改本文件或使用环境变量设置 TTS_APP_ID 和 TTS_ACCESS_KEY"
    exit 1
fi

if [ "$FEISHU_APP_ID" = "your-feishu-app-id" ] || [ "$FEISHU_APP_SECRET" = "your-feishu-app-secret" ]; then
    echo "❌ 错误：请先配置飞书 API 密钥"
    echo "请修改本文件或使用环境变量设置 FEISHU_APP_ID 和 FEISHU_APP_SECRET"
    exit 1
fi

echo "🎙️ 正在生成语音: $TEXT"

# 1. TTS 生成语音
curl -s -X POST "https://openspeech.bytedance.com/api/v3/tts/unidirectional" \
  -H "X-Api-App-Key: $TTS_APP_ID" \
  -H "X-Api-Access-Key: $TTS_ACCESS_KEY" \
  -H "X-Api-Resource-Id: seed-tts-2.0" \
  -H "Content-Type: application/json" \
  -d "{
    \"user\": {\"uid\": \"12345\"},
    \"event\": 100,
    \"req_params\": {
      \"text\": \"$TEXT\",
      \"speaker\": \"$SPEAKER\",
      \"audio_params\": {
        \"format\": \"mp3\",
        \"sample_rate\": 24000
      }
    }
  }" -o /tmp/tts-$$.json

# 2. 提取音频
python3 -c "
import json
import base64
import sys

parts = []
with open('/tmp/tts-$$.json', 'r') as f:
    for line in f:
        try:
            data = json.loads(line.strip())
            if data.get('code') == 0 and data.get('data'):
                parts.append(data['data'])
        except:
            pass

if not parts:
    print('TTS failed', file=sys.stderr)
    sys.exit(1)

audio = base64.b64decode(''.join(parts))
with open('/tmp/audio-$$.mp3', 'wb') as f:
    f.write(audio)
print(f'Audio size: {len(audio)} bytes')
"

if [ $? -ne 0 ]; then
    echo "❌ TTS 失败"
    rm -f /tmp/tts-$$.json /tmp/audio-$$.mp3 2>/dev/null
    exit 1
fi

# 3. 转换为 Opus
echo "🔄 转换为 Opus 格式..."
ffmpeg -i /tmp/audio-$$.mp3 -c:a libopus -b:a 24k /tmp/audio-$$.opus 2>/dev/null

if [ ! -f "/tmp/audio-$$.opus" ]; then
    echo "❌ 音频转换失败"
    rm -f /tmp/tts-$$.json /tmp/audio-$$.mp3
    exit 1
fi

# 4. 获取飞书 token
echo "🔑 获取飞书 access token..."
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$FEISHU_APP_ID\",\"app_secret\":\"$FEISHU_APP_SECRET\"}" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tenant_access_token',''))")

if [ -z "$TOKEN" ]; then
    echo "❌ 获取 token 失败"
    rm -f /tmp/tts-$$.json /tmp/audio-$$.mp3 /tmp/audio-$$.opus
    exit 1
fi

# 5. 上传文件
echo "📤 上传到飞书..."
UPLOAD=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_type=opus" \
  -F "file_name=voice.opus" \
  -F "file=@/tmp/audio-$$.opus")

FILE_KEY=$(echo "$UPLOAD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('file_key',''))")

if [ -z "$FILE_KEY" ]; then
    echo "❌ 上传失败: $UPLOAD"
    rm -f /tmp/tts-$$.json /tmp/audio-$$.mp3 /tmp/audio-$$.opus
    exit 1
fi

echo "✅ 获取 file_key: $FILE_KEY"

# 6. 获取音频时长
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 /tmp/audio-$$.opus 2>/dev/null | awk '{print int($1*1000)}')
DURATION=${DURATION:-5000}

# 7. 发送语音消息
echo "📨 发送语音消息..."
RESULT=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"receive_id\": \"$RECEIVER_ID\",
    \"msg_type\": \"audio\",
    \"content\": \"{\\\"file_key\\\":\\\"$FILE_KEY\\\",\\\"duration\\\":$DURATION}\"
  }")

# 检查发送结果
CODE=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('code',''))")

if [ "$CODE" = "0" ]; then
    echo "✅ 语音消息发送成功！"
    MSG_ID=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('message_id',''))")
    echo "📨 Message ID: $MSG_ID"
else
    echo "❌ 发送失败: $RESULT"
fi

# 清理
rm -f /tmp/tts-$$.json /tmp/audio-$$.mp3 /tmp/audio-$$.opus
