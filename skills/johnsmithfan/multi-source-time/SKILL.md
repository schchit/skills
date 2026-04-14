---
name: multi-source-time
description: >
  多方法报时技能。综合系统时钟、NTP 授时、网络时间 API 等多个时间源，
  融合输出可靠的时间报告（带置信度和偏差估计），并支持语音播报。
  触发场景："现在几点"、"报时"、"报北京时间"、"当前时间"、"帮我看下时间"、
  "time check"、"what time is it"、"报时技能"。
---

# Multi-Source Time Skill

多时间源融合报时 — 系统时钟、NTP、网络 API 多路冗余。

## 何时使用

✅ 用户说以下内容时触发本 Skill：
- "现在几点"
- "报时"
- "报北京时间"
- "帮我看下时间"
- "what time is it"

❌ 不适用：设置闹钟/定时（用 `qclaw-openclaw` 的 cron 提醒）、日历查询。

## 工作流程

```
1. 多源探测
   系统时钟 ──→ NTP 服务器池 ──→ 网络时间 API

2. 偏差计算
   各源与系统时钟偏差（ms），估算误差

3. 融合决策
   加权置信度选择最佳来源

4. 输出 + 语音播报
   文字 / JSON / TTS
```

## 命令行用法

```bash
# 默认：多源融合 + 文字输出
python scripts/time.py

# 仅系统时间（最快）
python scripts/time.py --method system

# 仅 NTP（最精确）
python scripts/time.py --method ntp

# 指定时区
python scripts/time.py --zone Asia/Shanghai

# JSON 输出（供 AI 后续处理）
python scripts/time.py --format json

# 语音播报
python scripts/time.py --voice

# 显示所有来源详情
python scripts/time.py --verbose

# 多源融合
python scripts/time.py --method all --verbose
```

## 时间源说明

| 源 | 精度 | 延迟 | 说明 |
|----|------|------|------|
| system | 毫秒级 | <1ms | 操作系统本地时钟（最可靠） |
| ntp | 微秒级 | 5-100ms | pool.ntp.org / google / cloudflare / windows / apple |
| web | 秒级 | 200-500ms | worldtimeapi.org / ip-api.com |

## 时间源优先级策略

- **system**：直接读取，零网络延迟，可靠性最高
- **ntp**：向多个 NTP 服务器查询（最多 5 个），取 RTT 最小的响应
- **web**：worldtimeapi.org 优先（含时区信息），fallback 到 ip-api.com

## 融合算法

```
置信度 = base_confidence × quality_factor
  system: base=1.0,  offset<500ms → 1.0, offset>5s → 0.7
  ntp:    base=0.95, offset<500ms → 0.95, >5s → 0.7
  web:    base=0.9,  offset<1s → 0.9,   >10s → 0.5

选择：max(confidence × 1/(1+|offset_ms|))
```

## 输出格式

### Text（默认）

```
═══════════════════════════════════════════════
  🕐 报时报告
═══════════════════════════════════════════════
  2026年04月10日 周五
  时间: 18:00:43  (UTC +08:00)
  时区: UTC+08:00
  第 15 周
  最佳来源: ntp:time.cloudflare.com
  系统偏差: +11.9 ms

  ─── 各时间源详情 ───
  ✓ system: 18:00:43 (置信度 100%, 偏差 0.0ms)
  ✓ ntp:time.cloudflare.com: 18:00:43 (置信度 95%, 偏差 +11.9ms)
  ✗ web: 超时
```

### JSON

```json
{
  "best_source": "ntp:time.cloudflare.com",
  "datetime_str": "2026-04-10T18:00:43.123+08:00",
  "timestamp": 1775815243.123,
  "timezone_name": "UTC+08:00",
  "timezone_offset": "+08:00",
  "day_of_week": "Friday",
  "week_number": 15,
  "is_dst": false,
  "fused_offset_ms": 11.9,
  "sources": [
    {"name": "system", "datetime_str": "...", "offset_ms": 0.0, "confidence": 1.0},
    {"name": "ntp:time.cloudflare.com", "offset_ms": 11.9, "confidence": 0.95}
  ]
}
```

## 语音播报

`--voice` 参数触发 TTS 播报（自动选择引擎）：

| 平台 | 引擎 | 说明 |
|------|------|------|
| 全平台 | `sag` (ElevenLabs) | 最自然，优先尝试 |
| Windows | SAPI | 系统内置，无需配置 |
| macOS | `say` | 系统内置，无需配置 |
| Fallback | 文字打印 | 无 TTS 时降级 |

中文数字播报规则：
- 整点：`上午/下午 几点整`
- 非整点：`上午/下午 几点几分`
- 含秒：`上午/下午 几点几分几秒`

## 文件结构

```
multi-source-time/
├── SKILL.md                   ← 本文件
└── scripts/
    └── time.py                ← 报时核心脚本（系统 / NTP / Web 多源）
```
