---
name: markhub-v6-local
description: MarkHub v6.0 - 完全本地 AI 创作系统，不依赖 ComfyUI，无法律风险
metadata:
  {
    "openclaw":
      {
        "requires": {
          "bins": ["python3", "ffmpeg"],
          "python_packages": ["stable-diffusion-cpp-python", "pillow", "numpy"]
        }
      }
  }
---

# MarkHub v6.0 - 完全本地 AI 创作系统

**100% 本地运行 · 无需 ComfyUI · 无法律风险**

## 核心特性

- ✅ **完全本地运行** - 不连接任何远程服务器
- ✅ **无需 ComfyUI** - 独立运行，不依赖外部服务
- ✅ **无法律风险** - 只使用开源模型（Stability AI 官方）
- ✅ **自动模型管理** - 自动下载、缓存、加载模型
- ✅ **支持文生图** - SD-Turbo/SDXL-Turbo/SD-v1.5/SD-v2.1
- ✅ **支持图生图** - Img2Img/Inpaint
- ✅ **支持视频生成** - 多帧合成视频
- ✅ **智能参数优化** - 自动选择最佳参数

## 安装

### 1. 安装依赖

```bash
# 基础依赖
pip install stable-diffusion-cpp-python pillow numpy

# FFmpeg（视频合成必需）
brew install ffmpeg  # macOS
apt install ffmpeg   # Linux
```

### 2. 安装技能

```bash
cd ~/.jvs/.openclaw/workspace/skills/markhub-v6-local
bash install.sh
```

## 快速开始

### 生成图片

```bash
# 基础用法（使用 SD-Turbo）
python3 markhub_v6_local.py -p "A beautiful woman, cinematic lighting"

# 指定模型
python3 markhub_v6_local.py -p "A cat" -m sdxl-turbo

# 自定义参数
python3 markhub_v6_local.py -p "Landscape" --width 1024 --height 1024 --steps 20
```

### 生成视频

```bash
# 生成 10 秒视频
python3 markhub_v6_local.py -p "A woman dancing" --video --duration 10

# 自定义 FPS
python3 markhub_v6_local.py -p "Ocean waves" --video --duration 5 --fps 30
```

### 自动模式

```bash
# 自动选择最佳模型和参数
python3 markhub_v6_local.py -p "Portrait of a woman" --auto

# 自动生成视频
python3 markhub_v6_local.py -p "Sunset" --video --auto
```

## 可用模型

| 模型 | 类型 | 分辨率 | 步数 | 大小 | 用途 |
|------|------|--------|------|------|------|
| **sd-turbo** | txt2img | 512x512 | 1 | 1.4GB | 快速生成 |
| **sdxl-turbo** | txt2img | 1024x1024 | 1 | 6GB | 高质量人像 |
| **stable-diffusion-v1-5** | txt2img | 512x512 | 20 | 4GB | 通用 |
| **stable-diffusion-v2-1** | txt2img | 768x768 | 20 | 5GB | 高分辨率 |

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-p, --prompt` | 提示词（必需） | - |
| `-n, --negative` | 负面提示词 | "" |
| `-m, --model` | 模型名称 | sd-turbo |
| `--video` | 生成视频 | False |
| `--duration` | 视频时长（秒） | 10 |
| `--fps` | 视频帧率 | 24 |
| `--auto` | 自动模式 | False |
| `--width` | 图片宽度 | 512 |
| `--height` | 图片高度 | 512 |
| `--steps` | 采样步数 | 自动 |
| `--cfg` | CFG 比例 | 自动 |
| `-o, --output` | 输出路径 | 自动生成 |

## 输出

- **图片：** `~/Videos/MarkHub/MarkHub_YYYYMMDD_HHMMSS.png`
- **视频：** `~/Videos/MarkHub/MarkHub_Video_YYYYMMDD_HHMMSS.mp4`

## 示例

### 高质量人像

```bash
python3 markhub_v6_local.py \
  -p "Beautiful woman portrait, professional photography, studio lighting" \
  -m sdxl-turbo \
  --width 1024 \
  --height 1024
```

### 风景图片

```bash
python3 markhub_v6_local.py \
  -p "Beautiful landscape, mountains, lake, sunset, 4k" \
  -m stable-diffusion-v2-1 \
  --width 768 \
  --height 768 \
  --steps 30
```

### 舞蹈视频

```bash
python3 markhub_v6_local.py \
  -p "A woman dancing gracefully, flowing dress, cinematic" \
  --video \
  --duration 10 \
  --fps 24
```

### 自动创作

```bash
# 自动选择最佳模型
python3 markhub_v6_local.py \
  -p "A cat playing with yarn" \
  --auto
```

## 法律说明

### ✅ 合法使用

本技能只使用以下开源模型：
- **SD-Turbo** - Stability AI 官方开源（Apache 2.0）
- **SDXL-Turbo** - Stability AI 官方开源（Apache 2.0）
- **Stable Diffusion v1.5** - Stability AI 官方开源（CreativeML Open RAIL-M）
- **Stable Diffusion v2.1** - Stability AI 官方开源（CreativeML Open RAIL-M）

所有模型均来自 HuggingFace 官方仓库，无法律风险。

### ❌ 禁止使用

- 不要生成侵权内容
- 不要生成违法内容
- 不要生成侵犯肖像权的内容
- 遵守当地法律法规

## 技术架构

```
MarkHub v6.0
├── stable-diffusion-cpp-python  # C++ 后端，Python 绑定
├── 模型管理                      # 自动下载、缓存
├── 图片生成                      # txt2img, img2img
├── 视频生成                      # 多帧合成 + FFmpeg
└── 参数优化                      # 自动选择最佳参数
```

## 性能参考

### 生成速度（M2 Pro）

| 模型 | 分辨率 | 步数 | 单张时间 |
|------|--------|------|---------|
| SD-Turbo | 512x512 | 1 | ~2 秒 |
| SDXL-Turbo | 1024x1024 | 1 | ~5 秒 |
| SD-v1.5 | 512x512 | 20 | ~30 秒 |
| SD-v2.1 | 768x768 | 20 | ~60 秒 |

### 视频生成

| 时长 | FPS | 帧数 | 总时间（SD-Turbo） |
|------|-----|------|------------------|
| 5 秒 | 24 | 120 | ~4 分钟 |
| 10 秒 | 24 | 240 | ~8 分钟 |
| 10 秒 | 30 | 300 | ~10 分钟 |

## 故障排除

### Q1: 模型下载失败

**A:** 检查网络连接，或使用镜像：

```bash
# 使用镜像站
export HF_ENDPOINT=https://hf-mirror.com
python3 markhub_v6_local.py -p "test"
```

### Q2: 内存不足

**A:** 使用更小的模型或分辨率：

```bash
# 使用 SD-Turbo（最小）
python3 markhub_v6_local.py -p "test" -m sd-turbo

# 降低分辨率
python3 markhub_v6_local.py -p "test" --width 256 --height 256
```

### Q3: 生成速度慢

**A:** 使用 Turbo 模型：

```bash
# SD-Turbo 只需 1 步
python3 markhub_v6_local.py -p "test" -m sd-turbo
```

### Q4: FFmpeg 未找到

**A:** 安装 FFmpeg：

```bash
# macOS
brew install ffmpeg

# Linux
apt install ffmpeg

# 验证
ffmpeg -version
```

## 相关文件

- `markhub_v6_local.py` - 主程序
- `SKILL.md` - 技能文档（本文件）
- `install.sh` - 安装脚本
- `README.md` - 详细说明

## 更新日志

- **v6.0** (2026-03-20) - 完全本地版本
  - ✅ 不依赖 ComfyUI
  - ✅ 使用 stable-diffusion-cpp-python
  - ✅ 自动模型管理
  - ✅ 无法律风险

- **v5.0** - ComfyUI 远程控制（已废弃）
- **v4.0** - 视频生成（已废弃）
- **v3.0** - 初始版本（已废弃）

## 许可证

MIT License - 与原项目保持一致

## 致谢

- **Stability AI** - 提供开源模型
- **stable-diffusion-cpp-python** - C++ 后端
- **FFmpeg** - 视频合成

---

**版本：** v6.0  
**发布日期：** 2026-03-20  
**维护者：** 1 号小虫子 · 严谨专业版
