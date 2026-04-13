---
name: video-download-transcribe
description: |
  多平台视频下载 + 本地转录 + 视频内容分析。
  
  **触发词**：这个视频说了什么、视频内容是什么、帮我看这个视频、下载这个视频、视频转录、字幕提取、B站视频、抖音视频、bilibili、youtube视频、帮我转录

  **支持平台**：B站/抖音/TikTok/YouTube/小红书/微博/快手
metadata:
  {
    "openclaw":
      {
        "emoji": "🎬",
        "requires":
          {
            "bins": ["ffmpeg", "yt-dlp"],
          },
      },
  }
---

# 多平台视频下载 + 本地转录

## 功能特点

- ✅ **纯浏览器下载（免费）** — 抖音用 Playwright 无水印抓取，无需 API Key
- ✅ **MLX Whisper** — Apple Silicon 原生 Metal GPU 加速（Mac M系列首选）
- ✅ **faster-whisper** — CPU/CUDA 通用兜底（非 Apple Silicon 也能用）
- ✅ **短视频同步转录** — <5 分钟视频直接返回完整结果
- ✅ **长视频后台转录** — ≥5 分钟自动后台运行，返回 transcript_id 可查询
- ✅ **可检索** — 转录结果支持关键词查询相关片段 + 时间戳

## 支持的平台

| 平台 | 检测关键词 | 下载方式 |
|------|-----------|---------|
| B站 | bilibili.com/video, b23.tv, BV号 | yt-dlp |
| 抖音 | douyin.com, v.douyin.com | Playwright 浏览器抓取 或 TikHub |
| TikTok | tiktok.com | TikHub |
| YouTube | youtube.com, youtu.be | yt-dlp |
| 小红书 | xiaohongshu.com, xhslink.com | TikHub |
| 微博 | weibo.com, m.weibo.cn | TikHub |
| 快手 | kuaishou.com, ksurl.cn | TikHub |

---

## 🔑 核心原则

### 所有平台统一两步走

> **获取下载链接 → curl/yt-dlp 下载 → mlx_whisper 转录**

**原因**：
- `analyze_video` 把下载+转录绑在一起，长视频容易超时
- 两步走每步都 <10秒，稳定可控
- 每步可单独排错

### 排错核心原则

> **当一个工具失败时，不要放弃！找替代方案。**

---

## 初始化安装（首次使用）

### 抖音 Playwright Chromium 安装

```bash
# 运行 setup.sh 自动安装
cd ~/.openclaw/workspace/skills/video-download-transcribe/douyin-mcp/
./setup.sh
```

setup.sh 会：
1. 检测系统环境
2. 查找或安装 Chromium（使用国内 npmmirror 镜像）
3. 设置 `DOUYIN_CHROMIUM_PATH` 环境变量
4. 测试浏览器抓取是否正常

**手动安装**（如果 setup.sh 失败）：
```bash
# 方式 A：用 openclaw-media 的 playwright 安装 chromium
git clone https://github.com/openclaw/openclaw-media ~/openclaw-media 2>/dev/null || true
PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright \
  ~/openclaw-media/.venv/bin/playwright install chromium

# 方式 B：自行安装 playwright
pip install playwright
PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright playwright install chromium
```

**环境变量**（运行 AI 助手前设置）：
```bash
export DOUYIN_CHROMIUM_PATH="$HOME/Library/Caches/ms-playwright/chromium-1105/chrome-mac/Chromium.app/Contents/MacOS/Chromium"
```

---

## 工作流程（统一两步走）

### 第一步：获取下载链接

```bash
# ========== 抖音 ==========

# 方式 A：douyin-analyzer 浏览器抓取（免费，需 Chromium）
mcporter call douyin-analyzer.get_douyin_download_link share_link:"https://v.douyin.com/xxx/"

# 方式 B：tikhub-douyin 获取实时 CDN 地址（更可靠，需 API Key）
mcporter call tikhub-douyin.douyin_web_fetch_video_high_quality_play_url share_url:"https://v.douyin.com/xxx/"

# ========== B站/YouTube/其他平台 ==========

# 用 yt-dlp 直接下载（会自动处理重定向和 Cookie）
yt-dlp -o "/tmp/video.mp4" "https://www.bilibili.com/video/BVxxx"

# ========== TikTok/小红书/微博/快手 ==========

# tikhub-douyin 获取下载链接
mcporter call tikhub-douyin.douyin_web_fetch_one_video_by_share_url share_url:"<链接>"
```

### 第二步：下载 + 转录

```bash
# 用 curl 下载（抖音/TikTok 获取的 CDN 地址）
curl -L -o /tmp/video.mp4 "https://cdn.example.com/video.mp4"

# 转录（本地 mlx_whisper）
python3 << 'PYEOF'
import os
os.environ["HF_HUB_OFFLINE"] = "1"
import mlx_whisper
result = mlx_whisper.transcribe(
    "/tmp/video.mp4",
    path_or_hf_repo="mlx-community/whisper-small-mlx",
    verbose=True
)
for seg in result.get("segments", []):
    print(f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
PYEOF
```

### 长视频（≥5分钟，后台转录）

```bash
# 用 analyze_video 获取 transcript_id（后台转录中）
mcporter call douyin-analyzer.analyze_video url:"https://..." --timeout 300000

# 等待 1-2 分钟后获取结果
mcporter call douyin-analyzer.get_transcript transcript_id:"xxx"
```

---

## MCP 工具

### douyin-analyzer（本地进程，免费）

```bash
# 获取无水印下载链接（浏览器抓取）
mcporter call douyin-analyzer.get_douyin_download_link share_link:"https://v.douyin.com/xxx/"

# 解析视频基本信息
mcporter call douyin-analyzer.parse_douyin_video_info share_link:"https://v.douyin.com/xxx/"

# 通用分析（仅用于获取 transcript_id，后台转录）
mcporter call douyin-analyzer.analyze_video url:"https://..." --timeout 300000

# 获取长视频后台转录结果
mcporter call douyin-analyzer.get_transcript transcript_id:"xxx"

# 检索转录内容
mcporter call douyin-analyzer.query_transcript transcript_id:"xxx" query:"关键词" top_k:3
```

**返回结构（get_douyin_download_link）：**
```json
{
  "video_id": "xxx",
  "download_url": "https://www.iesdouyin.com/aweme/v1/play/?video_id=xxx",
  "share_link": "https://v.douyin.com/xxx/"
}
```

> ⚠️ `download_url` 是 `iesdouyin.com` 重定向 URL，有时效性，建议立即使用。

### tikhub-douyin（远程服务，需认证）

```bash
# 获取视频信息+播放链接（所有平台通用）
mcporter call tikhub-douyin.douyin_web_fetch_one_video_by_share_url share_url:"<链接>"

# 获取最高画质 CDN 地址（推荐，最可靠）
mcporter call tikhub-douyin.douyin_web_fetch_video_high_quality_play_url share_url:"<链接>"
```

**返回字段：**
```json
{
  "data": {
    "original_video_url": "https://cdn.example.com/..."
  }
}
```

---

## ❗️ 排错流程

```
1. 工具返回 error/失败
   ↓
2. 抖音：换一个 MCP（douyin-analyzer ↔ tikhub-douyin）
       B站/YouTube：检查 yt-dlp 是否支持
       TikTok/其他：检查 tikhub-douyin 是否可用
   ↓
3. 抖音：检查 Chromium 是否安装 + DOUYIN_CHROMIUM_PATH 是否设置
   ↓
4. 如果都失败 → 找图文/文字版内容
```

### 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `download_url` 为空 | Playwright Chromium 未安装 | 运行 setup.sh 或手动安装 |
| `DOUYIN_CHROMIUM_PATH` 警告 | 环境变量未设置 | 设置 `export DOUYIN_CHROMIUM_PATH=...` |
| curl 下载失败 | 抖音 URL 已过期 | 改用 TikHub 获取实时 CDN |
| TikHub 返回 401 | API 认证失败 | 检查 mcporter.json 的 TikHub Token |
| yt-dlp 下载失败（B站） | Cookie/地区限制 | 加代理或用 TikHub |
| `analyze_video` 超时 | 视频较大 | 改用两步走 |

### Chromium 安装（国内镜像）

```bash
# 检查是否已安装
ls ~/Library/Caches/ms-playwright/

# 国内镜像安装
PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright \
  ~/openclaw-media/.venv/bin/playwright install chromium
```

---

## 本地转录（mlx_whisper）

```python
import os
os.environ["HF_HUB_OFFLINE"] = "1"  # 必须放在 import 之前！

import mlx_whisper

result = mlx_whisper.transcribe(
    "/path/to/video.mp4",
    path_or_hf_repo="mlx-community/whisper-small-mlx",
    verbose=True
)

for seg in result.get("segments", []):
    print(f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
```

### 推荐 Whisper 模型

| 模型 | 参数量 | 速度 | 精度 |
|------|--------|------|------|
| whisper-small-mlx | 244M | 快 | 中等 |
| whisper-base | 74M | 中 | 中 |
| whisper-large-v3-turbo | 809M | 慢 | 高 |

---

## 踩坑记录

### 2026-04-08 抖音下载修复

**问题**：douyin-analyzer 无法获取下载链接

**排查过程**：
1. 官方 API Cookie 失效（`tt_webid=xxx` 是假的）
2. 第三方 API (`liuxingw.com`) 返回 HTML 而非 JSON，已失效
3. TikHub API 需要认证，公共接口返回 401
4. Playwright Chromium 未安装（网络问题导致安装超时）
5. Chromium 版本不匹配（1.58 需要 chromium-1208，镜像只有 1105）
6. subprocess 中的 chromium 路径变量无法传递到代码字符串
7. `iesdouyin.com` 重定向 URL 有时效性

**最终解决方案**：
- 使用 `openclaw-media` 的 playwright 1.42.0（chromium-1105）
- 在 subprocess 代码字符串中硬编码 chromium 路径
- 用 `DOUYIN_CHROMIUM_PATH` 环境变量配置路径
- 两步走替代 `analyze_video`（下载+转录分离）

**教训**：
- 当工具失败时，列出所有 MCP 找替代方案
- MCP 内部变量无法传递到 subprocess 字符串代码
- `analyze_video` 把下载+转录绑在一起容易超时，**两步走更稳定**
- TikHub 返回 `original_video_url` 是真实 CDN 地址，比 `iesdouyin.com` 重定向 URL 更可靠
- f-string 中的 `{{` 会先被外层 f-string 处理，需用 `dict()` 代替字典字面量
