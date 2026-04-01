---
name: tiktok-video-audit
description: TikTok 视频 AI 审核技能。当用户发送 TikTok 链接并要求审核视频、生成审核报告时触发。功能包括：(1) TikTok 短链接解析，(2) yt-dlp 下载视频，(3) OpenCV 抽帧（前10秒10帧），(4) moviepy 音频提取分析（含逐秒 RMS），(5) Lingya AI（gemini-3-flash）多图审核，(6) 输出 JSON/Word 格式审核报告。触发词：审核 TikTok、视频审核、TikTok 报告。支持多类别 SOP：hotel（酒店）、restaurant（餐饮）、product（商品）、travel（旅行）。
---

# TikTok Video Audit

印尼 TikTok 内容 AI 审核技能，支持多类型 SOP。

## 支持类别

| 类别 | 说明 | SOP 文件 |
|------|------|---------|
| `hotel` | 酒店推广 | `references/categories/sop_hotel.md` |
| `restaurant` | 餐饮推广 | `references/categories/sop_restaurant.md` |
| `product` | 商品推广 | `references/categories/sop_product.md` |
| `travel` | 旅行/景点 | `references/categories/sop_travel.md` |

## 使用方式

```bash
# 默认 hotel 类别，同时输出 JSON + Word
python3 skills/tiktok-video-audit/scripts/tiktok_audit.py "TikTok链接"

# 指定类别
python3 skills/tiktok-video-audit/scripts/tiktok_audit.py "TikTok链接" --category restaurant

# 指定类别 + 输出格式
python3 skills/tiktok-video-audit/scripts/tiktok_audit.py "TikTok链接" --category hotel --output-json --output-docx

# 使用本地已有文件（跳过下载）
python3 skills/tiktok-video-audit/scripts/tiktok_audit.py "TikTok链接" --skip-download --category hotel
```

## 参数说明

| 参数 | 说明 |
|------|------|
| `--category` | SOP 类别：`hotel`（默认）、`restaurant`、`product`、`travel` |
| `--output-json` | 输出 JSON 报告 |
| `--output-docx` | 输出 Word 报告 |
| `--skip-download` | 跳过下载，使用本地已有文件 |
| `--output-dir` | 输出目录（默认 `output/tiktok_downloads_test/`） |

## 审核判定规则

| 评分区间 | 结论 |
|---------|------|
| ≥8 分 | 通过 ✅ |
| 3-8 分 | 待修改 ⚠️ |
| <3 分 | 不通过 ❌ |
| 无视频流 | 不通过 ❌ |

## 成本参考

- Input: 2元 / 百万 tokens
- Output: 8元 / 百万 tokens
- 一次审核约 13,000 tokens，约 **4 分钱**

## 报告内容

**JSON 报告包含**：`video_url`, `video_id`, `audio_analysis`（含逐秒 RMS）、`audit_result`（评分/结论/tokens/耗时/成本）、`phase_timings`（总时长/下载时长/分析时长/审核时长/报告时长）、`report_content`（AI 原始报告）

**Word 文档包含**：基本信息、审核结论（含视频/音频流判定）、前10秒逐帧描述表、音频分析（含逐秒 RMS/有效样本/状态）、SOP 逐项检查表、审核效率（含总时长/下载时长/审核时长/报告时长）

## 音频修订判定标准

- **有音频**：有效样本 > 5% 且 活跃 RMS > -45 dBFS
- **静音**：有效样本 < 5% 或 RMS ≤ -45 dBFS
- **不合格**：RMS < -35 dBFS（无论是否有音频内容）

## 关键配置

- yt-dlp 路径: `/Users/apple/Library/Python/3.9/bin/yt-dlp`
- 输出目录: `output/tiktok_downloads_test/`
- API: Lingya AI `https://api.lingyaai.cn/v1/chat/completions`
- 模型: `gemini-3-flash-preview`
- API Key: `sk-0zy1YyzLaabc5rPfqSvC5tF16os74HycNcvXLlMrVr0FXtNz`
