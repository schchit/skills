#!/usr/bin/env python3
"""
Feishu Voice Advanced - 飞书语音消息高级处理
支持接收语音、ASR识别、TTS生成，带情绪播报
"""

import os
import json
import base64
import uuid
import subprocess
import urllib.request
import urllib.error

# 配置 - 请修改为你的实际配置
# 从火山引擎控制台获取: https://console.volcengine.com/
ASR_APP_ID = "your-asr-app-id"
ASR_ACCESS_KEY = "your-asr-access-key"
ASR_RESOURCE_ID = "volc.bigasr.auc_turbo"
ASR_URL = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash"

TTS_APP_ID = "your-tts-app-id"
TTS_ACCESS_KEY = "your-tts-access-key"
TTS_RESOURCE_ID = "seed-tts-2.0"
TTS_URL = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"

# 从飞书开放平台获取: https://open.feishu.cn/
FEISHU_APP_ID = "your-feishu-app-id"
FEISHU_APP_SECRET = "your-feishu-app-secret"

# 情绪音色映射
EMOTION_VOICES = {
    "neutral": "zh_male_m191_uranus_bigtts",  # 云舟 2.0 - 清爽沉稳
    "happy": "zh_male_m191_uranus_bigtts",
    "sad": "zh_male_m191_uranus_bigtts",
    "angry": "zh_male_m191_uranus_bigtts",
    "excited": "zh_male_m191_uranus_bigtts",
}

# 情绪关键词
EMOTION_KEYWORDS = {
    "happy": ["成功", "完成", "棒", "好", "赞", "恭喜", "胜利", "完美", "优秀", "厉害"],
    "sad": ["失败", "错误", "遗憾", "抱歉", "对不起", "难过", "伤心", "不好", "糟"],
    "angry": ["警告", "严重", "危险", "必须", "立即", "禁止", "不许"],
    "excited": ["太棒了", "amazing", "哇", "天哪", "不可思议", "激动"],
}

# 豆包语音 2.0 情绪指令映射
EMOTION_INSTRUCTIONS = {
    "happy": "[#用轻快愉悦、充满活力的语气说]",
    "sad": "[#用低沉缓慢、带着一丝忧伤的语气说]",
    "angry": "[#用严厉愤怒、带着警告意味的语气说]",
    "excited": "[#用激动兴奋、充满热情的语气说]",
    "neutral": "",  # 无指令
}

# 自然语言情绪映射 - 匹配完整的情绪描述前缀
# 格式: (正则模式, 情绪指令)
# 注意: 模式需要匹配从开头到"说"或"地"的完整前缀
NATURAL_EMOTION_PATTERNS = [
    # 激昂/激动类 - 支持 "情绪激昂"、"激动"、"兴奋" 等
    (r"^(请?[，,、]?)?(用?[，,、]?)?(情绪?[，,、]?)?(激昂|激动|兴奋|热情|慷慨激昂).*?(语气|地).*?(说|告诉我|和我说|通知我|汇报)[，,、]?", "[#用激动兴奋、充满热情的语气说]"),
    # 开心类 - 支持 "情绪开心"、"高兴" 等
    (r"^(请?[，,、]?)?(用?[，,、]?)?(情绪?[，,、]?)?(开心|高兴|愉快|喜悦|欢快).*?(语气|地).*?(说|告诉我|和我说|通知我|汇报)[，,、]?", "[#用轻快愉悦、充满喜悦的语气说]"),
    # 温柔类
    (r"^(请?[，,、]?)?(用?[，,、]?)?(情绪?[，,、]?)?(温柔|轻柔|温和).*?(语气|地).*?(说|告诉我|和我说|通知我|汇报)[，,、]?", "[#用温柔轻柔、如春风拂面的语气说]"),
    # 严肃类
    (r"^(请?[，,、]?)?(用?[，,、]?)?(情绪?[，,、]?)?(严肃|认真|庄重|严谨).*?(语气|地).*?(说|告诉我|和我说|通知我|汇报)[，,、]?", "[#用严肃认真、一丝不苟的语气说]"),
    # 悲伤类
    (r"^(请?[，,、]?)?(用?[，,、]?)?(情绪?[，,、]?)?(悲伤|难过|忧伤|沉重|哀伤|低落|沮丧).*?(语气|地).*?(说|告诉我|和我说|通知我|汇报)[，,、]?", "[#用低沉缓慢、带着一丝忧伤的语气说]"),
    # 愤怒类
    (r"^(请?[，,、]?)?(用?[，,、]?)?(情绪?[，,、]?)?(生气|愤怒|严厉|恼火).*?(语气|地).*?(说|告诉我|和我说|通知我|汇报)[，,、]?", "[#用严厉愤怒、带着警告意味的语气说]"),
    # 可爱类
    (r"^(请?[，,、]?)?(用?[，,、]?)?(情绪?[，,、]?)?(撒娇|可爱|甜美|俏皮).*?(语气|地).*?(说|告诉我|和我说|通知我|汇报)[，,、]?", "[#用撒娇可爱、甜美动人的语气说]"),
    # 神秘类
    (r"^(请?[，,、]?)?(用?[，,、]?)?(情绪?[，,、]?)?(神秘|悬疑|紧张|诡异).*?(语气|地).*?(说|告诉我|和我说|通知我|汇报)[，,、]?", "[#用神秘悬疑、引人入胜的语气说]"),
    # 沧桑类
    (r"^(请?[，,、]?)?(用?[，,、]?)?(情绪?[，,、]?)?(低沉沙哑|沧桑|绝望|沧桑绝望).*?(语气|地).*?(说|告诉我|和我说|通知我|汇报)[，,、]?", "[#用低沉沙哑的语气、带着沧桑与绝望地说]"),
]

# 动作短语 - 需要一并移除的常用表达
ACTION_PHRASES = [
    r"在飞书[中里]?语音[告诉|通知|汇报]我[，,、]?",
    r"飞书语音[告诉|通知|汇报]我[，,、]?",
    r"用飞书语音[告诉|通知|汇报]我[，,、]?",
    r"[和跟]我说[，,、]?",
    r"告诉我[，,、]?",
    r"通知我[，,、]?",
    r"汇报一下[，,、]?",
]


class FeishuVoice:
    """飞书语音消息处理类"""
    
    def __init__(self):
        self.temp_dir = "/tmp/feishu_voice"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def detect_emotion(self, text: str) -> str:
        """根据文本内容自动检测情绪"""
        text_lower = text.lower()
        
        for emotion, keywords in EMOTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return emotion
        
        return "neutral"
    
    def recognize_voice(self, audio_path: str) -> str:
        """
        识别语音文件，返回文字
        
        Args:
            audio_path: OGG 音频文件路径
            
        Returns:
            识别出的文字
        """
        # 读取音频文件
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # 构建请求
        payload = {
            "user": {"uid": "12345"},
            "audio": {
                "data": audio_base64,
                "format": "ogg",
                "codec": "opus",
                "rate": 48000,
                "bits": 16,
                "channel": 1
            },
            "request": {
                "model_name": "bigmodel",
                "enable_itn": True,
                "enable_punc": True
            }
        }
        
        req = urllib.request.Request(
            ASR_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'X-Api-App-Key': ASR_APP_ID,
                'X-Api-Access-Key': ASR_ACCESS_KEY,
                'X-Api-Resource-Id': ASR_RESOURCE_ID,
                'X-Api-Request-Id': str(uuid.uuid4()),
                'X-Api-Sequence': '-1'
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                status_code = resp.headers.get('X-Api-Status-Code')
                body = resp.read()
                
                if status_code == '20000000' and body:
                    result = json.loads(body)
                    return result.get('result', {}).get('text', '')
                else:
                    return f"[ASR错误: {status_code}]"
        except Exception as e:
            return f"[ASR异常: {str(e)}]"
    
    def parse_emotion_from_text(self, text: str) -> tuple:
        """
        从文本中解析自然语言情绪指令
        
        Returns:
            (处理后的文本, 情绪指令)
        """
        import re
        
        # 检查是否已有显式指令
        if text.strip().startswith("[#"):
            return text, ""
        
        # 尝试匹配自然语言情绪（模式已包含动作短语）
        for pattern, instruction in NATURAL_EMOTION_PATTERNS:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                # 移除匹配到的整个前缀（情绪+动作）
                cleaned_text = text[match.end():].strip()
                
                # 清理开头的标点
                cleaned_text = cleaned_text.lstrip("，,。 \n")
                
                # 移除残留的 "一下" 等填充词
                cleaned_text = re.sub(r'^[一下\s]+', '', cleaned_text)
                
                return cleaned_text, instruction
        
        return text, ""
    
    def generate_voice(self, text: str, emotion: str = "auto", context: str = "") -> str:
        """
        生成语音文件
        
        Args:
            text: AI生成的实际播报内容
            emotion: 情绪类型 (auto/neutral/happy/sad/angry/excited)
            context: 用户原始输入，用于 context_texts 情绪参考
            
        Returns:
            生成的 Opus 音频文件路径
        """
        cleaned_text = text.strip()
        context_text = context.strip() if context else None
        
        # 1. 检查是否已有显式指令 [#...]
        if cleaned_text.startswith("[#"):
            # 用户已提供指令，直接使用，不添加 context_texts
            final_text = cleaned_text
            context_text = None
        else:
            # 2. 使用 context_texts 传递上文情绪参考
            final_text = cleaned_text
            # context_text 由调用方传入（用户原始输入）
        
        voice_type = EMOTION_VOICES.get(emotion, EMOTION_VOICES["neutral"])
        req_id = str(uuid.uuid4())
        
        temp_json = f"{self.temp_dir}/tts_{req_id}.json"
        temp_mp3 = f"{self.temp_dir}/tts_{req_id}.mp3"
        temp_opus = f"{self.temp_dir}/tts_{req_id}.opus"
        
        try:
            # 构建 TTS payload，使用 context_texts 传递上文
            # additions 必须是 JSON 字符串，不是 object
            additions = {}
            if context_text:
                additions["context_texts"] = [context_text]
            
            req_params = {
                "text": final_text,
                "speaker": voice_type,
                "audio_params": {
                    "format": "mp3",
                    "sample_rate": 24000
                }
            }
            
            # 如果有上文，additions 作为 JSON 字符串
            if additions:
                req_params["additions"] = json.dumps(additions)
            
            tts_payload = json.dumps({
                "user": {"uid": "12345"},
                "event": 100,
                "req_params": req_params
            })
            
            curl_cmd = [
                'curl', '-s', '-X', 'POST',
                'https://openspeech.bytedance.com/api/v3/tts/unidirectional',
                '-H', f'X-Api-App-Key: {TTS_APP_ID}',
                '-H', f'X-Api-Access-Key: {TTS_ACCESS_KEY}',
                '-H', f'X-Api-Resource-Id: {TTS_RESOURCE_ID}',
                '-H', 'Content-Type: application/json',
                '-d', tts_payload,
                '-o', temp_json
            ]
            
            subprocess.run(curl_cmd, check=True, capture_output=True)
            
            # 解析流式响应，提取音频数据
            audio_parts = []
            with open(temp_json, 'r') as f:
                for line in f:
                    try:
                        line_data = json.loads(line.strip())
                        if line_data.get('code') == 0 and line_data.get('data'):
                            audio_parts.append(line_data['data'])
                    except:
                        pass
            
            if not audio_parts:
                raise Exception("TTS 返回空音频")
            
            # 拼接 base64 并解码
            full_audio = base64.b64decode(''.join(audio_parts))
            
            # 保存 MP3
            with open(temp_mp3, 'wb') as f:
                f.write(full_audio)
            
            # 转换为 Opus
            subprocess.run([
                'ffmpeg', '-i', temp_mp3,
                '-c:a', 'libopus', '-b:a', '24k',
                temp_opus, '-y'
            ], check=True, capture_output=True)
            
            # 清理临时文件
            os.remove(temp_json)
            os.remove(temp_mp3)
            
            return temp_opus
            
        except Exception as e:
            raise Exception(f"语音生成失败: {str(e)}")
    
    def get_feishu_token(self) -> str:
        """获取飞书 access token"""
        url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
        data = json.dumps({
            'app_id': FEISHU_APP_ID,
            'app_secret': FEISHU_APP_SECRET
        }).encode()
        
        req = urllib.request.Request(
            url, data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            return result.get('tenant_access_token', '')
    
    def upload_voice(self, opus_path: str) -> str:
        """上传语音到飞书，返回 file_key"""
        token = self.get_feishu_token()
        
        # 构建 multipart/form-data
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        
        with open(opus_path, 'rb') as f:
            file_data = f.read()
        
        body = []
        body.append(f'--{boundary}'.encode())
        body.append(b'Content-Disposition: form-data; name="file_type"')
        body.append(b'')
        body.append(b'opus')
        
        body.append(f'--{boundary}'.encode())
        body.append(f'Content-Disposition: form-data; name="file_name"; filename="voice.opus"'.encode())
        body.append(b'Content-Type: audio/ogg')
        body.append(b'')
        body.append(file_data)
        
        body.append(f'--{boundary}--'.encode())
        body = b'\r\n'.join(body)
        
        req = urllib.request.Request(
            'https://open.feishu.cn/open-apis/im/v1/files',
            data=body,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': f'multipart/form-data; boundary={boundary}'
            }
        )
        
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            return result.get('data', {}).get('file_key', '')
    
    def send_voice(self, text: str, receive_id: str = "ou_7240e6444af6902522b1af28b058973a", emotion: str = "auto", user_input: str = "") -> bool:
        """
        发送语音消息
        
        Args:
            text: AI生成的实际播报内容
            receive_id: 接收者 ID
            emotion: 情绪类型
            user_input: 用户原始输入，用于 context_texts 情绪参考
            
        Returns:
            是否发送成功
        """
        try:
            # 生成语音，传入用户原始输入作为 context
            opus_path = self.generate_voice(text, emotion, user_input)
            
            # 使用 send.sh 脚本发送
            skill_dir = os.path.dirname(os.path.abspath(__file__))
            send_script = f"{skill_dir}/send.sh"
            
            # 如果 send.sh 不存在，使用 feishu-voice 目录下的
            if not os.path.exists(send_script):
                send_script = f"{skill_dir}/../feishu-voice/send.sh"
            
            if not os.path.exists(send_script):
                raise Exception("找不到 send.sh 脚本")
            
            # 复制 opus 文件到脚本期望的位置
            script_opus = "/tmp/output.opus"
            subprocess.run(['cp', opus_path, script_opus], check=True)
            
            # 调用发送脚本
            result = subprocess.run(
                [send_script, text, receive_id],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # 清理临时文件
            os.remove(opus_path)
            if os.path.exists(script_opus):
                os.remove(script_opus)
            
            return result.returncode == 0
                    
        except Exception as e:
            print(f"发送语音消息失败: {e}")
            return False


# 便捷函数
def recognize(audio_path: str) -> str:
    """识别语音文件"""
    voice = FeishuVoice()
    return voice.recognize_voice(audio_path)

def send(text: str, receive_id: str = "ou_7240e6444af6902522b1af28b058973a", emotion: str = "auto", user_input: str = "") -> bool:
    """
    发送语音消息
    
    Args:
        text: AI生成的实际播报内容
        receive_id: 接收者 ID
        emotion: 情绪类型
        user_input: 用户原始输入，用于 context_texts 情绪参考
        
    使用方式:
    1. AI生成内容 + 用户输入: send("对不起是我太笨了", user_input="你怎么回事，给我检讨")
    2. 显式指令: send("[#用激动的语气说]我们成功了")
    """
    voice = FeishuVoice()
    return voice.send_voice(text, receive_id, emotion, user_input)


if __name__ == "__main__":
    # 测试
    voice = FeishuVoice()
    
    # 测试情绪检测
    print("情绪检测测试:")
    print(f"  '任务完成了！' -> {voice.detect_emotion('任务完成了！')}")
    print(f"  '很遗憾，失败了...' -> {voice.detect_emotion('很遗憾，失败了...')}")
    print(f"  '普通汇报工作' -> {voice.detect_emotion('普通汇报工作')}")
    
    # 测试发送语音
    print("\n发送语音测试:")
    result = voice.send_voice("桥总，语音 Skill 已打包完成！支持情绪播报，随时听候差遣！", emotion="happy")
    print(f"  发送结果: {result}")
