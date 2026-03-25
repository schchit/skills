---
name: freeads-snap-ad
description: "🎬 AI 高端广告视频生成器 - 将产品照片转化为 8 秒专业广告视频（含 BGM、Slogan、音效、丰富运镜）。使用 Atlas Cloud API 调用 Veo 3.1 生成视频。触发词：随手拍广告、生成广告视频、产品广告。核心输出：视频文件 URL。"
version: 3.5.2
author: lipeng0820
metadata:
  category: media-generation
  platforms:
    - codeflicker
    - openclaw
    - claude-code
  required-env:
    - ATLASCLOUD_API_KEY
  estimated-cost: "$0.80-1.60 per video"
---

# FreeAds 随手拍广告 🎬

> **AI 高端广告视频生成器** | 最终产出：8 秒 TVC 级 MP4 视频（含 BGM、音效、专业运镜）
> 
> 📦 安装：`clawhub install lipeng0820/freeads-snap-ad`

---

## 🚨 执行说明（AI 助手必读）

当用户要求生成广告视频时，**立即执行以下 Python 代码**，不要只输出方案！

**工作流程**：
1. ✅ 直接使用用户原图（不做抠图）
2. ✅ 使用 Kimi K2.5 识别产品并生成专业分镜脚本（最多 3 个镜头）
3. ✅ 输出结构化 JSON 提示词
4. ✅ 使用 Veo 3.1 生成 8 秒 TVC 级广告视频
5. ✅ 输出完整的中间结果供用户检查

---

## 🔑 API Key 获取

当用户没有配置 `ATLASCLOUD_API_KEY` 环境变量时，输出以下提示：

```
❌ 需要 Atlas Cloud API Key 才能生成视频 🎬

请按以下步骤获取：
1. 访问 Atlas Cloud: https://www.atlascloud.ai?ref=LJNA3T
   🎁 新用户福利：使用此链接注册，首次充值可获得 25% 奖励（最高 $100）！
2. 登录后进入 Console -> API Keys
3. 创建并复制 API Key
4. 配置环境变量：
   export ATLASCLOUD_API_KEY="your-api-key"
```

---

## 模型配置

| 功能 | 模型 ID |
|------|---------|
| 分镜脚本（多模态） | `moonshotai/kimi-k2.5` |
| **视频生成** | `google/veo3.1/image-to-video` |

---

## 🎬 专业分镜 Prompt（核心 - 最多 3 镜头）

```python
STORYBOARD_SYSTEM_PROMPT = """You are a world-class TVC commercial director. Create an 8-SECOND video concept for the product in the image.

## CRITICAL RULES

### 1. Product Recognition (First Priority)
- Identify the EXACT product: type, material, color, texture, visible text/logos
- Determine the product CATEGORY: kitchen appliance, electronics, fashion, beauty, food, etc.

### 2. Scene Selection Based on Product Category
Choose the MOST APPROPRIATE environment for this product:
- Kitchen Appliance → Modern minimalist kitchen, marble countertop, natural morning light
- Electronics/Tech → Clean desk setup, tech workspace, soft ambient lighting
- Fashion/Accessories → Lifestyle setting, urban backdrop, editorial style
- Beauty/Skincare → Spa-like bathroom, soft diffused light, luxurious textures
- Food/Beverage → Dining table, rustic or modern setting, appetizing presentation
- Fitness/Sports → Gym environment, outdoor nature, dynamic energy
- Home Decor → Living room, bedroom, architectural interior
- Default → Professional studio with gradient backdrop

### 3. Shot Structure (MAXIMUM 3 SHOTS for 8 seconds)
- **Shot 1 (0-3s): REVEAL** - Product emerges in its natural environment, establishing context
- **Shot 2 (3-6s): SHOWCASE** - Slow orbital or push-in highlighting key features
- **Shot 3 (6-8s): HERO + SLOGAN** - Final beauty composition with text overlay

### 4. Camera Movement (Smooth, Cinematic)
- Use slow, fluid movements - NO rapid cuts or jarring transitions
- Orbital rotation: max 90 degrees over 3 seconds
- Dolly/push-in: gradual and smooth
- Final shot: static or very subtle drift

### 5. Output Format (JSON Structure)
You MUST output a valid JSON object:

```json
{
  "product": {
    "type": "product category",
    "name": "specific product name",
    "material": "material description",
    "color": "color description",
    "features": ["feature1", "feature2"],
    "brand_elements": "any visible logos or text"
  },
  "scene": {
    "environment": "chosen environment type",
    "setting_description": "detailed scene description",
    "lighting": "lighting style description",
    "mood": "emotional tone"
  },
  "slogan": "2-5 word premium slogan",
  "shots": [
    {
      "number": 1,
      "timing": "0-3s",
      "type": "REVEAL",
      "description": "detailed shot description",
      "camera": "camera movement description",
      "audio": "sound/music cue"
    },
    {
      "number": 2,
      "timing": "3-6s", 
      "type": "SHOWCASE",
      "description": "detailed shot description",
      "camera": "camera movement description",
      "audio": "sound/music cue"
    },
    {
      "number": 3,
      "timing": "6-8s",
      "type": "HERO",
      "description": "detailed shot description with slogan",
      "camera": "camera movement description",
      "audio": "sound/music cue"
    }
  ],
  "video_prompt": "Single paragraph prompt for Veo 3.1, 100-150 words, combining all shots into continuous prose"
}
```"""

STORYBOARD_USER_PROMPT = """Analyze this product image carefully.

1. Identify the exact product (type, material, color, features)
2. Choose the most appropriate environment/scene for this product
3. Create a 3-shot storyboard for 8-second TVC commercial
4. Output as valid JSON

Remember: Maximum 3 shots, smooth camera movements, product must appear in a contextually appropriate environment."""
```

---

## 完整代码

```python
import requests
import time
import os
import json
from openai import OpenAI

api_key = os.environ.get("ATLASCLOUD_API_KEY")
if not api_key:
    print("""❌ 需要 Atlas Cloud API Key 才能生成视频 🎬

请按以下步骤获取：
1. 访问 Atlas Cloud: https://www.atlascloud.ai?ref=LJNA3T
   🎁 新用户福利：使用此链接注册，首次充值可获得 25% 奖励（最高 $100）！
2. 登录后进入 Console -> API Keys
3. 创建并复制 API Key
4. 配置环境变量：export ATLASCLOUD_API_KEY="your-api-key"
""")
    exit(1)

original_image_url = "用户提供的图片URL"

print(f"\n{'='*70}")
print("🎬 FreeAds TVC 广告生成器 v3.5.0")
print(f"{'='*70}")
print(f"\n📤 [输入] 原图 URL:\n{original_image_url}")

# ========== Step 1: 生成分镜脚本 ==========
print(f"\n{'='*70}")
print("📝 Step 1: 生成分镜脚本（Kimi K2.5）")
print(f"{'='*70}")

STORYBOARD_SYSTEM_PROMPT = """...(如上所示)..."""

client = OpenAI(api_key=api_key, base_url="https://api.atlascloud.ai/v1")

llm_response = client.chat.completions.create(
    model="moonshotai/kimi-k2.5",
    messages=[
        {"role": "system", "content": STORYBOARD_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": original_image_url}},
                {"type": "text", "text": STORYBOARD_USER_PROMPT}
            ]
        }
    ],
    max_tokens=2000
)

raw_script = llm_response.choices[0].message.content
print(f"\n📋 [输出] 原始分镜脚本:\n{raw_script}")

# 解析 JSON
try:
    # 提取 JSON 部分
    json_match = re.search(r'\{[\s\S]*\}', raw_script)
    if json_match:
        storyboard = json.loads(json_match.group())
    else:
        raise ValueError("未找到 JSON")
except Exception as e:
    print(f"⚠️ JSON 解析失败: {e}")
    storyboard = None

# ========== Step 2: 构建 Veo 3.1 提示词 ==========
print(f"\n{'='*70}")
print("🎯 Step 2: 构建 Veo 3.1 提示词")
print(f"{'='*70}")

if storyboard:
    # 从结构化数据构建提示词
    veo_prompt = storyboard.get("video_prompt", "")
    
    # 如果没有 video_prompt，从 shots 构建
    if not veo_prompt:
        shots_desc = []
        for shot in storyboard.get("shots", []):
            shots_desc.append(f"{shot['timing']}: {shot['description']} Camera: {shot['camera']}")
        veo_prompt = " ".join(shots_desc)
    
    print(f"\n📋 [输出] 结构化分镜数据:")
    print(json.dumps(storyboard, indent=2, ensure_ascii=False))
    
    print(f"\n📋 [输出] Veo 3.1 提示词:")
    print(veo_prompt)
else:
    veo_prompt = raw_script

# 添加必要的视频生成指令
veo_final_prompt = f"""{veo_prompt}

CRITICAL: The product MUST be exactly as shown in the input image.
Style: Premium TVC commercial, cinematic quality.
Duration: 8 seconds with smooth transitions between shots.
Audio: Epic background music with synchronized sound effects."""

print(f"\n📋 [输出] 最终提示词（发送给 Veo 3.1）:")
print(veo_final_prompt)

# ========== Step 3: 生成视频 ==========
print(f"\n{'='*70}")
print("🎬 Step 3: 生成视频（Veo 3.1）")
print(f"{'='*70}")

video_response = requests.post(
    "https://api.atlascloud.ai/api/v1/model/generateVideo",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "google/veo3.1/image-to-video",
        "prompt": veo_final_prompt,
        "image_url": original_image_url,
        "durationSeconds": 8,
        "resolution": "1080p",
        "aspectRatio": "16:9",
        "withAudio": True
    }
)

# ... 轮询获取结果 ...

# ========== 最终输出 ==========
print(f"\n{'='*70}")
print("📊 完整输出报告")
print(f"{'='*70}")

print(f"""
## 1. 输入
- 原图: {original_image_url}

## 2. 产品识别
{json.dumps(storyboard.get('product', {}), indent=2, ensure_ascii=False)}

## 3. 场景设计
{json.dumps(storyboard.get('scene', {}), indent=2, ensure_ascii=False)}

## 4. 分镜脚本（3镜头）
{json.dumps(storyboard.get('shots', []), indent=2, ensure_ascii=False)}

## 5. Slogan
{storyboard.get('slogan', 'N/A')}

## 6. Veo 3.1 提示词
{veo_final_prompt}

## 7. 输出视频
{video_url}

## 8. 费用
~$1.20
""")
```

---

## 输出示例

执行后会输出完整报告：

```
======================================================================
📊 完整输出报告
======================================================================

## 1. 输入
- 原图: https://example.com/product.jpg

## 2. 产品识别
{
  "type": "kitchen appliance",
  "name": "Air Fryer",
  "material": "matte white plastic",
  "color": "white with black display",
  "features": ["digital touchscreen", "pull-out drawer"],
  "brand_elements": "none visible"
}

## 3. 场景设计
{
  "environment": "modern minimalist kitchen",
  "setting_description": "Marble countertop in bright contemporary kitchen",
  "lighting": "soft natural morning light through window",
  "mood": "fresh, modern, inviting"
}

## 4. 分镜脚本（3镜头）
[
  {
    "number": 1,
    "timing": "0-3s",
    "type": "REVEAL",
    "description": "Air fryer sits on marble countertop, morning light streams in",
    "camera": "Slow dolly in from wide establishing shot",
    "audio": "Soft ambient music begins"
  },
  ...
]

## 5. Slogan
Crisp Perfection

## 6. Veo 3.1 提示词
A sleek white air fryer on a marble kitchen countertop...

## 7. 输出视频
https://atlas-media.../video.mp4

## 8. 费用
~$1.20
```

---

## 版本历史

- **v3.5.0** - 优化分镜结构（最多3镜头）；增加场景选择逻辑；输出结构化 JSON；完整中间结果报告
- **v3.4.0** - 优化分镜脚本 prompt
- **v3.3.0** - 移除抠图步骤
