#!/usr/bin/env python3
"""
Multi-Source Time Tell v1.0
多方法报时 — 综合系统时间、NTP授时、网络时间API，输出可靠报时结果。

支持：
  - Windows / macOS / Linux 系统时钟
  - NTP 服务器池（pool.ntp.org）
  - 网络时间 API（worldtimeapi.org / ip-api.com）
  - TTS 语音播报（sag / Windows SAPI / say）

用法：
  python time.py                         # 默认：系统时间 + 报时
  python time.py --method system         # 仅系统时间
  python time.py --method ntp             # 仅 NTP 同步时间
  python time.py --method web             # 仅网络 API 时间
  python time.py --method all             # 多源融合（默认）
  python time.py --format json            # JSON 输出
  python time.py --voice                  # 语音播报
  python time.py --zone Asia/Shanghai     # 指定时区
  python time.py --verbose                # 显示所有来源详情
"""

import argparse
import json
import socket
import struct
import ssl
import sys
import os
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

# 强制 UTF-8 输出（避免 Windows GBK 终端 emoji 乱码）
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass


# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TimeSource:
    """单个时间源的结果"""
    name: str               # e.g. "system", "ntp.pool", "worldtimeapi"
    datetime_str: str       # ISO 8601 格式
    timestamp: float        # Unix 时间戳（秒）
    offset_ms: float        # 与系统时间偏差（毫秒）；None=未知
    confidence: float       # 置信度 0-1
    error: Optional[str] = None


@dataclass
class TimeReport:
    """多源融合后的报时报告"""
    best_source: str
    datetime_str: str
    timestamp: float
    timezone_name: str
    timezone_offset: str    # e.g. "+08:00"
    day_of_week: str
    week_number: int
    is_dst: bool
    sources: List[Dict]
    fused_offset_ms: Optional[float] = None


# ═══════════════════════════════════════════════════════════════════════════════
# TIME SOURCE: System Clock
# ═══════════════════════════════════════════════════════════════════════════════

def get_system_time(tz_name: str = "") -> TimeSource:
    """读取操作系统本地时间（最高优先级，可靠性最强）"""
    try:
        if tz_name:
            import zoneinfo
            try:
                tz = zoneinfo.ZoneInfo(tz_name)
                now = datetime.now(tz)
                return TimeSource(
                    name="system",
                    datetime_str=now.isoformat(),
                    timestamp=now.timestamp(),
                    offset_ms=0.0,
                    confidence=1.0,
                )
            except Exception:
                pass
        # Fallback: use local timezone from system
        now = datetime.now()
        local_tz = datetime.now().astimezone().tzinfo
        now_aware = datetime.now().astimezone()
        return TimeSource(
            name="system",
            datetime_str=now_aware.isoformat(),
            timestamp=now_aware.timestamp(),
            offset_ms=0.0,
            confidence=1.0,
        )
    except Exception as e:
        return TimeSource(name="system", datetime_str="", timestamp=0,
                         offset_ms=None, confidence=0.0, error=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# TIME SOURCE: NTP
# ═══════════════════════════════════════════════════════════════════════════════

def _ntp_query(host: str, port: int = 123, timeout: float = 5.0) -> Optional[float]:
    """Query a single NTP server, return Unix timestamp or None."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        # NTP packet (Mode 3 = client)
        pkt = b'\x1b' + b'\x00' * 47
        sock.sendto(pkt, (host, port))
        data, _ = sock.recvfrom(1024)
        sock.close()
        # NTP epoch: 1900-01-01; Unix epoch: 1970-01-01
        # Days between 1900-01-01 and 1970-01-01 = 25567 days = 2208988800 seconds
        ntp_ts = struct.unpack('!12I', data)[10]
        unix_ts = ntp_ts - 2208988800
        return unix_ts
    except Exception:
        return None


def get_ntp_time(tz_name: str = "") -> TimeSource:
    """从 NTP 服务器池获取精确时间（零延迟估计）"""
    ntp_hosts = [
        "pool.ntp.org",
        "time.google.com",
        "time.cloudflare.com",
        "time.windows.com",
        "time.apple.com",
    ]
    system_ts = time.time()
    best_ts = None
    best_rtt = float('inf')
    best_host = None
    tried = []

    for host in ntp_hosts:
        ts = _ntp_query(host)
        tried.append(host)
        if ts is not None:
            rtt = abs(ts - system_ts) * 1000  # ms
            if rtt < best_rtt:
                best_rtt = rtt
                best_ts = ts
                best_host = host
        # Stop if we already have a good result
        if best_ts is not None and best_rtt < 100:
            break

    if best_ts is None:
        return TimeSource(
            name="ntp",
            datetime_str="", timestamp=0,
            offset_ms=None, confidence=0.0,
            error=f"所有 NTP 服务器均不可达（已尝试: {', '.join(tried)}）"
        )

    # 系统时钟本身也是 NTP 同步的，偏差即为 NTP 的偏移估计
    offset_ms = (best_ts - system_ts) * 1000

    # 用系统本地时区包裹时间戳
    dt_local = datetime.fromtimestamp(best_ts).astimezone()

    # 大偏移警告（NTP 与系统时钟差 >1s 说明本机时钟可能有漂移）
    error_msg = None
    if abs(offset_ms) > 1000:
        error_msg = (
            f"⚠️ NTP 与系统时钟偏差超过 1 秒（{offset_ms:.0f} ms），"
            f"请检查本机时钟同步设置。网络延迟也可能导致此偏差。"
        )

    return TimeSource(
        name=f"ntp:{best_host}",
        datetime_str=dt_local.isoformat(),
        timestamp=best_ts,
        offset_ms=offset_ms,
        confidence=0.95 if abs(offset_ms) < 500 else 0.7,
        error=error_msg,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TIME SOURCE: Web APIs
# ═══════════════════════════════════════════════════════════════════════════════

def _fetch_json(url: str, timeout: float = 5.0) -> Optional[Dict]:
    """GET JSON with SSL. Returns None on any error."""
    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8", errors="ignore"))
    except urllib.error.HTTPError as e:
        # 4xx/5xx — 有响应但服务器报错，不值得重试
        return None
    except (urllib.error.URLError, socket.timeout, TimeoutError):
        # 网络不可达 / 超时
        return None
    except Exception:
        # 捕获其他所有异常（SSL error, decode error, etc.）
        return None


def get_web_time(tz_name: str = "") -> TimeSource:
    """从网络时间 API 获取时间"""
    system_ts = time.time()

    # Try worldtimeapi.org (most reliable, includes timezone) — HTTPS 优先
    url = "https://worldtimeapi.org/api/ip"
    data = _fetch_json(url)
    if data:
        try:
            dt_str = data.get("datetime", "")
            if dt_str:
                dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                ts = dt.timestamp()
                offset_ms = (ts - system_ts) * 1000
                return TimeSource(
                    name="worldtimeapi",
                    datetime_str=dt.isoformat(),
                    timestamp=ts,
                    offset_ms=offset_ms,
                    confidence=0.9,
                )
        except Exception:
            pass

    # Fallback: ip-api.com time (no timezone info, use UTC) — HTTPS
    url2 = "https://ip-api.com/json/?fields=datetime,timezone"
    data2 = _fetch_json(url2)
    if data2:
        try:
            dt_str = data2.get("datetime", "")
            if dt_str:
                dt_utc = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                dt_local = dt_utc.astimezone()
                ts = dt_local.timestamp()
                offset_ms = (ts - system_ts) * 1000
                return TimeSource(
                    name="ip-api",
                    datetime_str=dt_local.isoformat(),
                    timestamp=ts,
                    offset_ms=offset_ms,
                    confidence=0.85,
                )
        except Exception:
            pass

    return TimeSource(
        name="web",
        datetime_str="", timestamp=0,
        offset_ms=None, confidence=0.0,
        error="所有网络时间 API 均不可达"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# FUSION: Multi-Source Time Aggregation
# ═══════════════════════════════════════════════════════════════════════════════

def fuse_time(sources: List[TimeSource], tz_name: str = "") -> TimeReport:
    """融合多个时间源，返回最佳估计"""
    # Filter valid sources
    valid = [s for s in sources if s.error is None and s.timestamp > 0]
    if not valid:
        # Fallback to system
        sys_src = get_system_time(tz_name)
        return TimeReport(
            best_source=sys_src.name,
            datetime_str=sys_src.datetime_str,
            timestamp=sys_src.timestamp,
            timezone_name=sys_src.name,
            timezone_offset="",
            day_of_week=datetime.now().strftime("%A"),
            week_number=_week_number(sys_src.timestamp),
            is_dst=False,
            sources=[],
            fused_offset_ms=None,
        )

    # Weighted average: weight = confidence / (1 + abs(offset_ms))
    best = max(valid, key=lambda s: s.confidence * (1 / (1 + abs(s.offset_ms or 0))))
    dt_best = datetime.fromisoformat(best.datetime_str)

    # Timezone info
    tz_offset_str = ""
    tz_name_out = best.name
    is_dst = False
    utc_offset = dt_best.utcoffset()
    if utc_offset:
        total_secs = int(utc_offset.total_seconds())
        sign = '+' if total_secs >= 0 else '-'
        abs_secs = abs(total_secs)
        h, m = divmod(abs_secs, 3600)
        tz_offset_str = f"{sign}{h:02d}:{m:02d}"
        tz_name_out = str(dt_best.tzinfo) if dt_best.tzinfo else best.name

    return TimeReport(
        best_source=best.name,
        datetime_str=best.datetime_str,
        timestamp=best.timestamp,
        timezone_name=tz_name_out,
        timezone_offset=tz_offset_str,
        day_of_week=dt_best.strftime("%A"),
        week_number=_week_number(best.timestamp),
        is_dst=is_dst,
        sources=[asdict(s) for s in sources],
        fused_offset_ms=best.offset_ms,
    )


def _week_number(ts: float) -> int:
    """ISO week number (1-53)."""
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.isocalendar()[1]


# ═══════════════════════════════════════════════════════════════════════════════
# VOICE OUTPUT
# ═══════════════════════════════════════════════════════════════════════════════

def speak_time(report: TimeReport, voice: str = "auto") -> None:
    """
    用语音播报时间。
    voice 选项: "auto" | "sag" | "windows" | "say" | "none"
    """
    dt = datetime.fromisoformat(report.datetime_str)
    hour = dt.hour
    minute = dt.minute
    second = dt.second

    # 中文语音播报文字
    chinese_num = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    def num_cn(n: int, unit: str = "") -> str:
        if n == 0:
            return "零" if unit else "整"
        if n < 10:
            return chinese_num[n] + unit
        if n < 20:
            # 10=十, 11=十一, ..., 19=十九
            return "十" + (chinese_num[n - 10] if n > 10 else "") + unit
        # n >= 20
        tens = chinese_num[n // 10]
        rem = n % 10
        ones = chinese_num[rem] if rem != 0 else ""
        return tens + "十" + ones + unit

    hour_str = num_cn(hour, "点")
    minute_str = num_cn(minute, "分") if minute > 0 else ""
    second_str = num_cn(second, "秒") if second > 0 else ""
    ampm = "上午" if hour < 12 else "下午"

    spoken = f"{ampm}，{hour_str}{minute_str}{second_str}"

    # Try sag (ElevenLabs TTS)
    if voice in ("auto", "sag"):
        try:
            import subprocess
            result = subprocess.run(
                ["sag", "-c", spoken],
                capture_output=True, timeout=10
            )
            if result.returncode == 0:
                return
        except Exception:
            pass

    # Try Windows SAPI
    if voice in ("auto", "windows") and sys.platform == "win32":
        try:
            import subprocess
            subprocess.run(
                ["powershell", "-Command",
                 f"Add-Type -AssemblyName System.Speech; "
                 f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                 f"$synth.Rate = -1; "
                 f"$synth.Speak('{spoken}')"],
                capture_output=True, timeout=10
            )
            return
        except Exception:
            pass

    # Try macOS say
    if voice in ("auto", "say") and sys.platform == "darwin":
        try:
            import subprocess
            subprocess.run(["say", spoken], capture_output=True, timeout=10)
            return
        except Exception:
            pass

    # Fallback: print to console
    print(f"🔔 {spoken}")


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT FORMATTING
# ═══════════════════════════════════════════════════════════════════════════════

def _chinese_weekday(dt: datetime) -> str:
    wd_map = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return wd_map[dt.weekday()]


def _chinese_num(n: int) -> str:
    """阿拉伯数字转中文（0-99）"""
    c = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
    if n < 10:
        return c[n]
    elif n < 20:
        return "十" + (c[n-10] if n > 10 else "")
    elif n < 100:
        tens = c[n // 10]
        ones = c[n % 10] if n % 10 else ""
        return tens + "十" + ones
    return str(n)


def _format_timezone(dt: datetime) -> str:
    """Format timezone offset as +HH:MM"""
    off = dt.utcoffset()
    if off is None:
        return ""
    total = int(off.total_seconds())
    sign = '+' if total >= 0 else '-'
    total = abs(total)
    h, m = divmod(total, 3600)
    return f"{sign}{h:02d}:{m:02d}"


def print_text(report: TimeReport, verbose: bool = False):
    """人类可读的报时输出"""
    dt = datetime.fromisoformat(report.datetime_str)
    time_str = dt.strftime("%Y年%m月%d日")
    weekday = _chinese_weekday(dt)
    time_of_day = dt.strftime("%H:%M:%S")
    tz_str = _format_timezone(dt)

    lines = [
        "",
        "═" * 50,
        "  🕐 报时报告",
        "═" * 50,
        f"  {time_str} {weekday}",
        f"  时间: {time_of_day}  (UTC {tz_str})",
        f"  时区: {report.timezone_name}",
        f"  第 {report.week_number} 周",
        f"  最佳来源: {report.best_source}",
    ]

    if report.fused_offset_ms is not None:
        offset_abs = abs(report.fused_offset_ms)
        offset_sign = "" if report.fused_offset_ms >= 0 else "-"
        lines.append(f"  系统偏差: {offset_sign}{offset_abs:.1f} ms")

    if verbose and report.sources:
        lines += ["", "  ─── 各时间源详情 ───"]
        for src in report.sources:
            if src.get("error"):
                # ⚠️ 开头的表示警告（仍使用该源），普通错误才标记 ✗
                if src["error"].startswith("⚠️"):
                    lines.append(f"  ⚠️ {src['name']}: {src['error']}")
                else:
                    lines.append(f"  ✗ {src['name']}: {src['error']}")
            else:
                dt_src = datetime.fromisoformat(src["datetime_str"])
                lines.append(
                    f"  ✓ {src['name']}: "
                    f"{dt_src.strftime('%H:%M:%S')} "
                    f"(置信度 {src['confidence']:.0%}"
                    + (f", 偏差 {src['offset_ms']:.1f}ms" if src.get("offset_ms") is not None else "")
                    + ")"
                )

    print("\n".join(lines))

    # Voice output if requested
    if hasattr(sys.modules[__name__], '_voice_enabled'):
        import sys as _sys
        _speak(report)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="多方法报时")
    parser.add_argument(
        "--method", "-m", default="all",
        help="时间源: system, ntp, web, all (逗号分隔)"
    )
    parser.add_argument("--format", "-f", choices=["json", "text"], default="text")
    parser.add_argument("--zone", "-z", default="", help="时区 (IANA, e.g. Asia/Shanghai)")
    parser.add_argument("--voice", action="store_true", help="语音播报")
    parser.add_argument("--voice-engine", default="auto",
                        help="语音引擎: auto, sag, windows, say, none")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示所有来源详情")
    args = parser.parse_args()

    # Parse methods
    if args.method == "all":
        method_names = ["system", "ntp", "web"]
    else:
        method_names = [m.strip().lower() for m in args.method.split(",")]

    # Collect sources
    sources: List[TimeSource] = []
    method_funcs = {
        "system": lambda: get_system_time(args.zone),
        "ntp":    lambda: get_ntp_time(args.zone),
        "web":    lambda: get_web_time(args.zone),
    }

    for name in method_names:
        fn = method_funcs.get(name)
        if not fn:
            print(f"⚠️ 未知时间源: {name}", file=sys.stderr)
            continue
        src = fn()
        # 警告类信息（⚠️）在 stderr 静默跳过，统一由 print_text(verbose) 展示
        # 真正不可用的源（error 非 ⚠️）也在 print_text(verbose) 里展示，避免重复
        sources.append(src)

    # Fuse
    report = fuse_time(sources, args.zone)

    # Output
    if args.format == "json":
        print(json.dumps(asdict(report), indent=2, ensure_ascii=False))
    else:
        print_text(report, verbose=args.verbose)

    # Voice
    if args.voice:
        speak_time(report, args.voice_engine)

    sys.exit(0)


if __name__ == "__main__":
    main()
