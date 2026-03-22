---
name: video-to-article
description: 从视频生成图文并排的公众号文章（md格式）。支持本地视频文件或在线视频URL（自动下载），自动完成文本提取、视频帧截取、时间轴匹配、文章撰写全流程。
metadata: { "openclaw": { "emoji": "📝", "requires": { "bins": ["python3"] } } }
---

# video-to-article 技能

## 描述

根据视频文件，自动生成图文并排的公众号文章（Markdown格式）。

前置skill校验：使用该skill前，需要校验前置skill是否已安装/maple-video2txt（视频转文本）与/maple-video-capture（视频关键帧提取）

## 使用场景

- 需要根据视频内容写公众号文章/推文
- 需要将视频内容整理成图文并茂的文档
- 需要为视频创作配套的文字稿

## 完整工作流

### 第零步：判断输入类型（优先阅读skill，从skill中获取真实的执行路径，下发用例仅供参考）

**如果用户提供的是视频URL**（如 B站、YouTube 链接），先调用判断当前是否有用于下载视频的skill

并使用该skill下载这个视频：

video-downloader 技能下载视频：

```bash
python3 C:\Users\user\.openclaw\workspace\skills\video-downloader\scripts\video_downloader.py "<视频URL>" "1080p" "D:\video-downloads"
```

**参数说明：**
- 第一个参数：视频URL（必填）
- 第二个参数：分辨率，如 `1080p`、`720p`、`360p`（可选，默认 720p）
- 第三个参数：输出目录（可选，默认临时目录）

**下载完成后**，使用下载返回的本地文件路径继续后续步骤。

**如果用户提供的是本地视频文件路径**，跳过此步，直接从第一步开始。

---

### 第一步：提取视频文本（优先阅读skill，从skill中获取真实的执行路径，下发用例仅供参考）

使用 video2txt 技能提取视频中的语音内容。

```bash
cd ~/.openclaw/skills/video2txt
python video_to_text.py --input "<视频文件路径>" --language zh
```

**输出文件：**
- `<视频文件名>.txt` — 纯文本
- `<视频文件名>.srt` — 带时间戳字幕

### 第二步：截取视频帧（优先阅读skill，从skill中获取真实的执行路径，下发用例仅供参考）

使用 video-frame-capture 技能从视频中截取关键帧（优先阅读skill）。

```bash
cd ~/.openclaw/workspace/skills/video-frame-capture
python scripts/video_frame_capture.py --input "<视频文件路径>" --output-dir "<输出目录>" --interval-seconds 30
```

**参数说明：**
- `--interval-seconds 30`：每30秒截取一帧（5分钟视频约10-12帧）
- **注意：对于画面变化小的视频（如讲解类、财经类），不要使用 `--skip-similar-frames`**，否则会跳过大量帧

**输出：** 多张截图，命名格式：`视频名_时间戳_序号.jpg`

### 第二点五步：总结视频背景信息

基于第一步提取的文本内容，总结一段 **200字左右** 的背景信息文档，描述这段视频的核心内容。

**总结要点：**
- 视频主题是什么
- 主要讲了哪些核心观点/事件
- 涉及的关键人物/品牌/产品
- 视频的整体立场/基调（客观科普、吐槽批评、推荐安利等）

**输出：** 将背景信息保存为临时变量，后续步骤使用。

---

### 第三步：根据时间轴自动匹配图片与字幕段落

**⚠️ 核心规则：不要调用图片理解/识别skill！直接用时间轴硬匹配即可。**

图片理解AI可能误判画面内容（比如把A产品当成B产品），而时间轴匹配是确定性的，只要字幕时间戳准确，配图就一定对得上。

**图片命名格式：** `视频名_00h01m30s_0003.jpg`
- 时间戳 `00h01m30s` 表示该帧对应视频的 1分30秒 处
- 解析为秒数：0×3600 + 1×60 + 30 = 90秒

**SRT 字幕格式：**
```
4
00:02:15,000 --> 00:02:20,000
这里是字幕内容
```
- 起始时间 `00:02:15` 解析为秒数：2×60 + 15 = 135秒

**匹配算法：**
1. 解析所有截帧图片的文件名，提取时间戳，转为秒数，排序
2. 解析SRT字幕文件，提取每个字幕块的起始时间（秒数）
3. 对每张图片，找到时间戳最接近（≤15秒误差）的字幕块作为该图片的配对文本
4. 如果某张图片附近没有字幕（如纯画面/静音段），则跳过该图片

**具体步骤：**
1. 写一个Python脚本完成上述匹配逻辑
2. 输出一个配对列表：`{图片路径: 对应字幕时间段 + 文本内容}`
3. 按时间顺序排列，用于后续文章段落划分
4. 从配对列表中选择6-8张最有代表性的图片（均匀分布在整个视频时间轴上）

**禁止调用图片理解skill的原因：**
- AI可能误判画面内容，导致配图与文本不匹配
- 时间轴匹配是确定性的，不会出错
- 只要字幕时间戳准确，配图就一定对得上
- 省去不必要的API调用，提高效率

> **记住：提取字幕 → 时间轴匹配图片 → 直接写文章。跳过图片理解步骤。**

### 第四步：撰写图文并排文章

结合文本内容和图片，按照以下结构撰写公众号文章：

**推荐结构：**

```markdown
# 文章标题

**导读：** 简短引言，吸引读者

![封面图](图片路径)

---

## 一、开篇（引入话题/背景）

![配图](图片路径)

内容...

---

## 二、核心问题（深入分析）

![配图](图片路径)

内容...

---

## 三、数据/证据（用数据说话）

![配图](图片路径)

内容...

---

## 四、竞争/对比（如有）

![配图](图片路径)

内容...

---

## 五、总结与展望

内容...

---

*来源说明*
```

**配图原则：**
1. 封面图放在导读后，用于视觉吸引
2. 每个大标题下至少配一张图
3. 图片要与所在段落内容呼应
4. 文章末尾可不配图，留给总结文字

**图文时间轴对齐方法：**
- 使用第三步的时间轴匹配结果，直接获取每张图片对应的字幕段落
- SRT 字幕文件格式：`00:02:15,000 --> 00:02:20,000` 对应图片 `视频名_00h02m15s_序号.jpg`
- 每张配图都自动对应到该时间点附近的字幕内容，无需手动判断

**文章风格：**
- 口语化，适合公众号阅读
- 适当使用引用块（>）突出关键数据或观点
- 可使用表格整理对比信息
- 段落不宜过长，适配手机阅读

### 附：时间轴匹配脚本（timeline_matcher.py）

在 `scripts/` 目录下新建 `timeline_matcher.py`，用于自动完成时间轴匹配：

```bash
python scripts/timeline_matcher.py --frames-dir "<帧截图目录>" --srt "<SRT字幕文件路径>" --max-images 8
```

**功能：**
1. 扫描帧截图目录，解析文件名中的时间戳
2. 解析SRT字幕文件，提取所有时间段和文本
3. 将每张图片匹配到最近的字幕段落（15秒误差内）
4. 输出JSON格式的配对结果，包含图片路径、时间戳、对应字幕文本
5. 筛选出均匀分布在时间轴上的8张代表性图片

**输出示例：**
```json
[
  {
    "image": "video_00h00m30s_0001.jpg",
    "timestamp_sec": 30,
    "srt_time": "00:00:32 --> 00:00:38",
    "subtitle_text": "今天我们来聊一个话题...",
    "selected": true
  },
  ...
]
```

**注意：** 第四步撰写文章时，直接使用脚本输出的 `subtitle_text` 作为配图所在段落的参考内容。

---

## 依赖

- video2txt 技能（文本提取）
- video-frame-capture 技能（帧截取）
- Python 3.11+
- faster-whisper、opencv-python

## 输出文件

最终输出为 Markdown 文件，保存在视频文件同目录下：
- `<视频文件名>_article.md`

## 注意事项

1. **视频帧截取间隔**：建议30秒，根据视频时长调整
2. **相似度过滤**：讲解类视频画面变化小，**不要使用** `--skip-similar-frames`
3. **🚫 禁止调用图片理解skill**：不要使用任何图片识别/理解API，直接依靠时间轴匹配图片和字幕。可以手动浏览图片挑选，但不要用AI理解图片内容
4. **配图数量**：根据视频时长和内容丰富度决定，教程类建议20张以上，科普类6-8张即可
5. **图片路径**：CSDN/公众号发布时手动上传图片，md中使用相对路径引用

## 示例

### 示例1：本地视频文件
```bash
# 1. 提取文本
cd ~/.openclaw/skills/video2txt
python video_to_text.py --input "D:\videos\sam1.mp4" --language zh

# 2. 截取帧
cd ~/.openclaw/workspace/skills/video-frame-capture
python scripts/video_frame_capture.py --input "D:\videos\sam1.mp4" --output-dir "D:\videos\frames" --interval-seconds 30

# 3. 时间轴匹配图片与字幕
# 解析帧文件名时间戳，匹配最近的SRT字幕段落
# 可使用 timeline_matcher.py 脚本或手动匹配

# 4. 撰写文章，保存为 D:\videos\sam1_article.md
```

### 示例2：在线视频URL（B站）
```bash
# 0. 先下载视频
python3 C:\Users\陈凯宁\.openclaw\workspace\skills\video-downloader\scripts\video_downloader.py "https://www.bilibili.com/video/BV1xx" "1080p" "D:\video-downloads"

# 1. 提取文本（使用下载后的本地路径）
cd ~/.openclaw/skills/video2txt
python video_to_text.py --input "D:\video-downloads\视频标题.mp4" --language zh

# 2. 截取帧
cd ~/.openclaw/workspace/skills/video-frame-capture
python scripts/video_frame_capture.py --input "D:\video-downloads\视频标题.mp4" --output-dir "D:\video-downloads\frames" --interval-seconds 30

# 3. 时间轴匹配图片与字幕

# 4. 撰写文章
```

---

**更新记录：**
- 2026-03-20：首次创建，基于《被山姆榨干的中产们》视频的生成流程总结
- 2026-03-21：新增第零步，支持视频URL自动下载（集成 video-downloader 技能）
- 2026-03-21：新增图文时间轴对齐说明，利用图片时间戳与SRT字幕匹配，提高图文准确性
- 2026-03-21：明确禁止调用图片理解skill，完全依靠时间轴硬匹配。理由：AI可能误判画面内容，时间轴匹配更准确可靠
