# MarkHub v6.0 - 完全本地 AI 创作系统

## 什么是 MarkHub v6.0？

MarkHub v6.0 是一个**完全本地运行**的 AI 创作系统，不依赖任何远程服务，无法律风险。

### 与前代对比

| 特性 | v5.0 (ComfyUI) | v6.0 (本地) |
|------|---------------|------------|
| 运行方式 | 远程 ComfyUI | **100% 本地** |
| 依赖服务 | ComfyUI 服务器 | **无** |
| 网络连接 | 必需 | **不需要** |
| 法律风险 | 中等 | **无** |
| 模型来源 | 手动管理 | **自动下载** |
| 生成速度 | 快 | **快（Turbo）** |

## 核心优势

### 1. 完全本地运行

- ✅ 不连接任何远程服务器
- ✅ 不扫描端口
- ✅ 不依赖 ComfyUI
- ✅ 断网也能用

### 2. 无法律风险

只使用官方开源模型：
- **SD-Turbo** - Apache 2.0 许可
- **SDXL-Turbo** - Apache 2.0 许可
- **Stable Diffusion v1.5/v2.1** - CreativeML Open RAIL-M

### 3. 自动模型管理

- 自动下载模型
- 自动缓存
- 自动选择最佳模型
- 自动清理

### 4. 简单易用

```bash
# 一行命令生成图片
python3 markhub_v6_local.py -p "A beautiful woman"

# 一行命令生成视频
python3 markhub_v6_local.py -p "A woman dancing" --video
```

## 安装

### 快速安装

```bash
# 1. 进入目录
cd ~/.jvs/.openclaw/workspace/skills/markhub-v6-local

# 2. 运行安装脚本
bash install.sh

# 3. 测试
python3 markhub_v6_local.py -p "test"
```

### 手动安装

```bash
# 1. 安装依赖
pip3 install stable-diffusion-cpp-python pillow numpy

# 2. 安装 FFmpeg
brew install ffmpeg  # macOS
apt install ffmpeg   # Linux

# 3. 创建目录
mkdir -p ~/Videos/MarkHub
mkdir -p ~/.markhub/models
```

## 使用示例

### 生成图片

```bash
# 快速生成（SD-Turbo，1 步）
python3 markhub_v6_local.py -p "A cat"

# 高质量人像（SDXL-Turbo）
python3 markhub_v6_local.py \
  -p "Beautiful woman portrait, professional photography" \
  -m sdxl-turbo

# 自定义参数
python3 markhub_v6_local.py \
  -p "Landscape" \
  --width 1024 \
  --height 1024 \
  --steps 30
```

### 生成视频

```bash
# 10 秒视频
python3 markhub_v6_local.py \
  -p "Ocean waves" \
  --video \
  --duration 10

# 自定义 FPS
python3 markhub_v6_local.py \
  -p "Sunset" \
  --video \
  --duration 5 \
  --fps 30
```

### 自动模式

```bash
# 自动选择最佳模型
python3 markhub_v6_local.py \
  -p "Portrait of a woman" \
  --auto
```

## 可用模型

### SD-Turbo（推荐）

- **分辨率：** 512x512
- **步数：** 1 步
- **大小：** 1.4GB
- **速度：** ~2 秒/张
- **用途：** 快速生成、测试

### SDXL-Turbo

- **分辨率：** 1024x1024
- **步数：** 1 步
- **大小：** 6GB
- **速度：** ~5 秒/张
- **用途：** 高质量人像

### Stable Diffusion v1.5

- **分辨率：** 512x512
- **步数：** 20 步
- **大小：** 4GB
- **速度：** ~30 秒/张
- **用途：** 通用

### Stable Diffusion v2.1

- **分辨率：** 768x768
- **步数：** 20 步
- **大小：** 5GB
- **速度：** ~60 秒/张
- **用途：** 高分辨率

## 输出

- **图片：** `~/Videos/MarkHub/MarkHub_YYYYMMDD_HHMMSS.png`
- **视频：** `~/Videos/MarkHub/MarkHub_Video_YYYYMMDD_HHMMSS.mp4`

## 常见问题

### Q: 为什么选择 v6.0 而不是 v5.0？

**A:** v6.0 有以下优势：
- ✅ 完全本地，不依赖外部服务
- ✅ 无法律风险
- ✅ 自动模型管理
- ✅ 更简单、更可靠

### Q: 生成速度慢怎么办？

**A:** 使用 Turbo 模型：
```bash
python3 markhub_v6_local.py -p "test" -m sd-turbo
```

### Q: 内存不足怎么办？

**A:** 使用更小的模型：
```bash
python3 markhub_v6_local.py -p "test" -m sd-turbo --width 256 --height 256
```

### Q: 模型下载失败怎么办？

**A:** 使用镜像站：
```bash
export HF_ENDPOINT=https://hf-mirror.com
python3 markhub_v6_local.py -p "test"
```

## 技术架构

```
MarkHub v6.0
├── stable-diffusion-cpp-python  # C++ 后端
├── 模型管理                      # 自动下载/缓存
├── 图片生成                      # txt2img
├── 视频生成                      # 多帧 + FFmpeg
└── 参数优化                      # 自动选择
```

## 法律说明

### ✅ 合法

- 只使用 Stability AI 官方开源模型
- 遵守开源许可证
- 不侵犯任何版权

### ❌ 禁止

- 生成侵权内容
- 生成违法内容
- 侵犯肖像权

## 更新日志

- **v6.0** (2026-03-20) - 完全本地版本
- **v5.0** - ComfyUI 远程控制（已废弃）
- **v4.0** - 视频生成（已废弃）
- **v3.0** - 初始版本（已废弃）

## 许可证

MIT License

## 致谢

- Stability AI - 开源模型
- stable-diffusion-cpp-python - C++ 后端
- FFmpeg - 视频合成

---

**版本：** v6.0  
**发布日期：** 2026-03-20
