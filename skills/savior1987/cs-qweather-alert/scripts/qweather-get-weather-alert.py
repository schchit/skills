#!/usr/bin/env python3
"""
和风天气预警查询脚本

用法:
    python qweather-get-weather-alert.py <城市名> [API_HOST] [JWT_TOKEN]

环境变量:
    QWEATHER_API_HOST  和风天气 API Host（如 https://api.qweather.com）

Token 配置:
    默认从 ~/.myjwtkey/last-token.dat 读取，也可通过 --token 参数指定

示例:
    python qweather-get-weather-alert.py 北京
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.error


# ============ Emoji 映射 ============

SEVERITY_EMOJI = {
    "extreme": "🔴",
    "severe":   "🟠",
    "moderate": "🟡",
    "minor":    "🔵",
    "unknown":  "⚪",
}

SEVERITY_NAME = {
    "extreme": "极严重",
    "severe":   "严重",
    "moderate": "中等",
    "minor":    "轻微",
    "unknown":  "未知",
}

EVENT_TYPE_EMOJI = {
    # 大风
    "1006": "💨",
    # 高温
    "2001": "🌡️",
    # 台风
    "2002": "🌀",
    # 暴雨
    "2003": "🌧️",
    # 暴雪
    "2004": "❄️",
    # 寒潮
    "2005": "🥶",
    # 大雾
    "2006": "🌫️",
    # 霾
    "2007": "😷",
    # 雷电
    "2008": "⚡",
    # 冰雹
    "2009": "🧊",
    # 沙尘暴
    "2010": "🌪️",
    # 干旱
    "2011": "🏜️",
    # 洪涝
    "2013": "🌊",
    # 渍涝
    "2014": "💧",
    # 城市高温
    "2015": "🏙️",
    # 地质灾害
    "5001": "⛰️",
    # 洪水
    "5002": "🏞️",
    # 崩塌
    "5003": "🪨",
    # 滑坡
    "5004": "⛰️",
    # 泥石流
    "5005": "🌋",
    # 水文
    "5006": "💦",
    # 干旱
    "5007": "🏜️",
    # 森林火险
    "6001": "🔥",
    # 草原火险
    "6002": "🔥",
    # 冰冻
    "6003": "🧊",
    # 低温冻害
    "6004": "🥶",
    # 雪灾
    "6005": "❄️",
}

# 默认事件类型 emoji
DEFAULT_EVENT_EMOJI = "⚠️"


# ============ 工具函数 ============

def get_env_or_arg(env_var: str, arg_val: str | None, description: str) -> str:
    """从环境变量或命令行参数获取配置，优先使用显式传入的参数。"""
    val = arg_val or os.environ.get(env_var)
    if not val:
        print(f"错误: 缺少 {description}", file=sys.stderr)
        print(f"  请设置环境变量 {env_var} 或作为命令行参数传入", file=sys.stderr)
        sys.exit(1)
    return val.strip().rstrip("/")


def get_token(arg_val: str | None) -> str:
    """获取 JWT Token。优先级：1) 命令行参数 2) ~/.myjwtkey/last-token.dat"""
    # 1. 命令行参数
    if arg_val:
        return arg_val.strip()

    # 2. token 文件
    token_file = os.path.expanduser("~/.myjwtkey/last-token.dat")
    if os.path.exists(token_file):
        with open(token_file, "r", encoding="utf-8") as f:
            token = f.read().strip()
        if token:
            return token

    print(f"错误: 缺少 JWT Token", file=sys.stderr)
    print(f"  请通过以下方式提供：1) --token 参数 2) ~/.myjwtkey/last-token.dat", file=sys.stderr)
    sys.exit(1)


def get_host(env_var: str, arg_val: str | None, description: str) -> str:
    """获取 API Host，自动补上 https:// 前缀。"""
    val = arg_val or os.environ.get(env_var)
    if not val:
        print(f"错误: 缺少 {description}", file=sys.stderr)
        print(f"  请设置环境变量 {env_var} 或作为命令行参数传入", file=sys.stderr)
        sys.exit(1)
    val = val.strip().rstrip("/")
    if not val.startswith(("http://", "https://")):
        val = "https://" + val
    return val


def _get_debug_log_path() -> str:
    """获取调试日志文件路径，每天一个文件，放在 /tmp/cslog/ 目录中。"""
    from datetime import datetime
    log_dir = "/tmp/cslog"
    os.makedirs(log_dir, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    return os.path.join(log_dir, f"qweather-get-weather-alert-{today}.log")


def _decompress(body: bytes) -> bytes:
    """尝试解压 gzip，如果失败则返回原始 bytes。"""
    import gzip
    try:
        return gzip.decompress(body)
    except Exception:
        return body


def _mask_token(token: str) -> str:
    """脱敏 JWT token，只显示前8后4位。"""
    if len(token) <= 12:
        return "****"
    return token[:8] + "..." + token[-4:]


def api_get(url: str, headers: dict) -> dict:
    """发送 GET 请求，返回 JSON。支持 gzip 自动解压。"""
    import datetime as dt
    log_path = _get_debug_log_path()
    ts = dt.datetime.now().strftime("%H:%M:%S")
    auth_header = headers.get("Authorization", "")

    # 提取原始 token 用于脱敏
    raw_token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else auth_header
    masked_token = _mask_token(raw_token)

    # 构造可粘贴的 curl 命令（token 已脱敏）
    curl_cmd = (
        f"curl -X GET --compressed \\ \\"
        f" -H 'Authorization: Bearer {masked_token}' \\ \\"
        f" -H 'Accept: application/json' \\ \\"
        f" -H 'Accept-Encoding: gzip' \\ \\"
        f" '{url}'"
    )

    with open(log_path, "a", encoding="utf-8") as log_f:
        log_f.write(f"\n[{ts}] ===== api_get =====\n")
        log_f.write(f"{curl_cmd}\n")
        log_f.write(f"  ────────────────────────────────\n")

    # 实际请求加上 gzip 支持
    req_headers = dict(headers)
    req_headers["Accept-Encoding"] = "gzip"
    req = urllib.request.Request(url, headers=req_headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
            body = _decompress(raw)
            body_str = body.decode("utf-8", errors="replace")
            # 成功时也记录完整响应
            with open(log_path, "a", encoding="utf-8") as log_f:
                log_f.write(f"  响应 [200 OK]: {body_str[:2000]}\n")
            return json.loads(body_str)
    except urllib.error.HTTPError as e:
        raw = e.read()
        body = _decompress(raw)
        body_str = body.decode("utf-8", errors="replace")
        with open(log_path, "a", encoding="utf-8") as log_f:
            log_f.write(f"  HTTP 错误: {e.code} {e.reason}\n")
            log_f.write(f"  响应内容: {body_str[:2000]}\n")
        print(f"HTTP 错误: {e.code} {e.reason}", file=sys.stderr)
        print(f"响应内容: {body_str[:500]}", file=sys.stderr)
        print(f"已记录到: {log_path}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        with open(log_path, "a", encoding="utf-8") as log_f:
            log_f.write(f"  网络错误: {e.reason}\n")
        print(f"网络错误: {e.reason}", file=sys.stderr)
        sys.exit(1)


# ============ 城市经纬度缓存 ============

def _get_cache_path() -> str:
    """获取城市经纬度缓存文件路径，放在脚本同目录的 data 子目录中。"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "location.json")


def _load_cache() -> dict:
    """加载城市缓存。"""
    path = _get_cache_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_cache(cache: dict) -> None:
    """保存城市缓存到文件。"""
    path = _get_cache_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def lookup_city(host: str, token: str, city_name: str) -> dict | None:
    """
    查询城市经纬度。优先从本地缓存读取，缓存不存在则调用 API 并写入缓存。
    """
    cache = _load_cache()

    # 命中缓存
    if city_name in cache:
        print(f"[缓存命中] {city_name} -> {cache[city_name].get('lat')}, {cache[city_name].get('lon')}", file=sys.stderr)
        return cache[city_name]

    print(f"[缓存未命中] 正在查询 API: {city_name} ...", file=sys.stderr)

    url = f"{host}/geo/v2/city/lookup?location={urllib.parse.quote(city_name)}&number=1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    result = api_get(url, headers)
    if result.get("code") != "200":
        print(f"城市查询失败: code={result.get('code')}", file=sys.stderr)
        return None
    locations = result.get("location", [])
    if not locations:
        print(f"未找到城市: {city_name}", file=sys.stderr)
        return None

    city_info = locations[0]

    # 写入缓存
    cache[city_name] = city_info
    _save_cache(cache)
    print(f"[已写入缓存] {city_name}", file=sys.stderr)

    return city_info


# ============ 预警查询 ============

def get_weather_alerts(host: str, token: str, lat: str, lon: str) -> dict:
    """
    调用天气预警 API。
    """
    url = f"{host}/weatheralert/v1/current/{lat}/{lon}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    return api_get(url, headers)


# ============ 格式化输出 ============

def format_timestamp(ts: str) -> str:
    """将 ISO 时间格式化为可读字符串，去掉 T 和时区后缀。"""
    ts = ts.replace("T", " ").replace("+08:00", "").replace("Z", "+00:00")
    return ts.strip()


def get_event_emoji(event_code: str) -> str:
    """根据事件代码获取 emoji。"""
    return EVENT_TYPE_EMOJI.get(event_code, DEFAULT_EVENT_EMOJI)


def get_severity_emoji(severity: str) -> str:
    """根据严重程度获取 emoji。"""
    return SEVERITY_EMOJI.get(severity.lower(), SEVERITY_EMOJI["unknown"])


def format_alert(alert: dict) -> str:
    """将单条预警格式化为易读文本。"""
    severity_emoji = get_severity_emoji(alert.get("severity", "unknown"))
    severity_name = SEVERITY_NAME.get(alert.get("severity", "unknown"), "未知")
    event_code = alert.get("eventType", {}).get("code", "")
    event_name = alert.get("eventType", {}).get("name", "未知预警")
    event_emoji = get_event_emoji(event_code)

    headline = alert.get("headline", "无标题")
    description = alert.get("description", "无详细描述")
    instruction = alert.get("instruction", "")
    sender = alert.get("senderName", "未知来源")
    effective = format_timestamp(alert.get("effectiveTime", ""))
    expire = format_timestamp(alert.get("expireTime", ""))

    lines = [
        f"{severity_emoji} {event_emoji} 【{event_name}】{severity_emoji}",
        f"{'─' * 40}",
        f"⚡ 预警级别: {severity_name}",
        f"📢 预警标题: {headline}",
        f"",
    ]

    if description and description != "无详细描述":
        lines.append(f"📋 详情: {description}")
        lines.append("")

    if instruction:
        # 防御指南每行前加 • 
        instr_lines = instruction.strip().split("\n")
        formatted_instr = "\n".join(f"   • {l.strip()}" for l in instr_lines if l.strip())
        lines.append(f"🛡️  防御指南:")
        lines.append(formatted_instr)
        lines.append("")

    lines.append(f"🏛️  发布机构: {sender}")
    if effective:
        lines.append(f"⏰ 生效时间: {effective}")
    if expire:
        lines.append(f"⏰ 失效时间: {expire}")

    return "\n".join(lines)


def format_output(
    city_name: str,
    lat: str,
    lon: str,
    alert_result: dict,
) -> str:
    """将完整查询结果格式化为最终输出文本。"""
    metadata = alert_result.get("metadata", {})
    zero_result = metadata.get("zeroResult", False)

    header = [
        f"🌤️  {city_name} 天气预警",
        f"坐标: {lat}, {lon}",
        f"{'─' * 40}",
    ]

    if zero_result:
        header.append("✅ 目前没有天气预警")
        attr = metadata.get("attributions", [])
        if attr:
            header.append("")
            header.append(f"📡 数据来源: {attr[0] if attr else '和风天气'}")
        return "\n".join(header)

    alerts = alert_result.get("alerts", [])
    if not alerts:
        header.append("✅ 目前没有天气预警")
        return "\n".join(header)

    header.append(f"⚠️  共 {len(alerts)} 条预警")
    header.append("")

    lines = header[:]
    for i, alert in enumerate(alerts, 1):
        lines.append(f"【预警 {i}/{len(alerts)}】")
        lines.append(format_alert(alert))
        lines.append("")

    attr = metadata.get("attributions", [])
    if attr:
        lines.append(f"{'─' * 40}")
        for a in attr:
            lines.append(f"📡 {a}")

    return "\n".join(lines)


# ============ 入口 ============

import urllib.parse

def main():
    parser = argparse.ArgumentParser(
        description="和风天气预警查询工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "city",
        nargs="?",
        default=None,
        help="城市名称（如北京、上海）",
    )
    parser.add_argument(
        "--host",
        dest="host",
        default=None,
        help="API Host（也可设置环境变量 QWEATHER_API_HOST）",
    )
    parser.add_argument(
        "--token",
        dest="token",
        default=None,
        help="JWT Token（默认从 ~/.myjwtkey/last-token.dat 读取）",
    )
    args = parser.parse_args()

    city_name = args.city or os.environ.get("QWEATHER_CITY", "").strip()
    if not city_name:
        print("错误: 请提供城市名称作为参数，或设置环境变量 QWEATHER_CITY", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    host = get_host("QWEATHER_API_HOST", args.host, "API Host")
    token = get_token(args.token)

    print(f"正在查询城市: {city_name} ...", file=sys.stderr)

    # 1. 查询城市坐标
    city_info = lookup_city(host, token, city_name)
    if not city_info:
        sys.exit(1)

    lat = city_info["lat"]
    lon = city_info["lon"]
    full_city_name = f"{city_info.get('adm2', '')}{city_info.get('name', city_name)}"

    print(
        f"找到: {full_city_name}（{city_info.get('adm1', '')}）{lat}, {lon}",
        file=sys.stderr,
    )
    print(f"正在获取天气预警 ...", file=sys.stderr)

    # 2. 查询预警
    alert_result = get_weather_alerts(host, token, lat, lon)

    # 3. 格式化输出
    output = format_output(full_city_name, lat, lon, alert_result)
    print()
    print(output)


if __name__ == "__main__":
    main()
