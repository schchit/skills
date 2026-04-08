#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""uapp-mini-channel: 友盟小程序推广渠道查询脚本

功能目标：
- 读取 umeng-config.json（支持 --config / UMENG_CONFIG_PATH / 当前目录 / .env）
- 解析应用（支持 --app / --account，含模糊匹配，仅支持小程序应用）
- 支持获客来源排行查询（渠道/活动/H5场景/其他场景）
- 支持指定渠道/活动/场景值的统计数据查询
- 支持趋势分析（--metric + --range）
- 输出：文本表格 / JSON
"""

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta

# -------------------------
# 常量定义
# -------------------------

INDICATOR_NAMES = {
    "newUser": "新增用户",
    "activeUser": "活跃用户",
    "launch": "启动次数",
    "visitTimes": "访问次数",
    "onceDuration": "次均停留时长",
}

SOURCE_TYPE_NAMES = {
    "channel": "渠道",
    "campaign": "活动",
    "platform": "H5场景",
    "scene": "其他场景",
}

ORDER_BY_NAMES = {
    "newUser": "新增用户",
    "activeUser": "活跃用户",
    "launch": "启动次数",
    "visitTimes": "访问次数",
    "onceDuration": "次均停留时长",
    "createDateTime": "创建时间",
}

DEFAULT_INDICATORS = ["newUser", "activeUser", "launch"]

MINI_PROGRAM_PLATFORMS = ["微信小程序", "支付宝小程序", "百度小程序", "字节跳动小程序", "QQ小程序", "H5", "小游戏"]


# -------------------------
# 工具函数：路径 & 配置加载
# -------------------------


def resolve_workspace_root() -> str:
    """解析 workspace 根目录。"""
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    workspace = os.path.dirname(skill_dir)
    return workspace


def load_env_config_path() -> str | None:
    """从环境变量或 .env 中加载 UMENG_CONFIG_PATH。"""
    env_path = os.environ.get("UMENG_CONFIG_PATH")
    if env_path:
        return env_path

    workspace = resolve_workspace_root()
    env_file = os.path.join(workspace, ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("UMENG_CONFIG_PATH="):
                        return line.split("UMENG_CONFIG_PATH=", 1)[1].strip()
        except Exception:
            pass
    return None


def resolve_config_path(cli_config: str | None) -> str:
    """解析配置文件路径。"""
    if cli_config:
        return cli_config

    env_config = load_env_config_path()
    if env_config:
        return env_config

    workspace = resolve_workspace_root()
    default_path = os.path.join(workspace, "umeng-config.json")
    return default_path


def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


# -------------------------
# 应用解析（含模糊匹配）
# -------------------------


def normalize_app_name(name: str) -> str:
    """去除半角/全角空格，用于模糊匹配。"""
    return name.replace(" ", "").replace("\u3000", "")


def is_mini_program(platform: str) -> bool:
    """判断是否为小程序/H5/小游戏平台。"""
    return platform in MINI_PROGRAM_PLATFORMS


def find_app_by_name(config: dict, app_name: str, account_id: str | None = None):
    """按应用名称查找应用配置，支持精确匹配 + 去空格模糊匹配。"""
    matches = []
    normalized_input = normalize_app_name(app_name)

    for account in config.get("accounts", []):
        if account_id and account.get("id") != account_id:
            continue
        for app in account.get("apps", []):
            platform = app.get("platform", "")
            if not is_mini_program(platform):
                continue
            name = app.get("name", "")
            if name == app_name or normalize_app_name(name) == normalized_input:
                matches.append({
                    "account_id": account.get("id"),
                    "apiKey": account.get("apiKey"),
                    "apiSecurity": account.get("apiSecurity"),
                    "app": app,
                })

    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]
    return matches


def resolve_app(config: dict, app_name: str | None, account_id: str | None) -> dict:
    """解析最终使用的应用配置。"""
    if app_name:
        result = find_app_by_name(config, app_name, account_id=account_id)
        if not result:
            available = []
            for account in config.get("accounts", []):
                for app in account.get("apps", []):
                    if is_mini_program(app.get("platform", "")):
                        available.append(f"{app.get('name', '')} ({app.get('platform', '')})")
            raise ValueError(f"未找到名称匹配的小程序应用: {app_name}\n可用小程序应用: {', '.join(available)}")
        if isinstance(result, list):
            raise ValueError("存在多个同名应用，请通过 --account 进一步限定")
        return result

    raise ValueError("未指定应用，请使用 --app 指定小程序应用名称")


# -------------------------
# 时间范围解析
# -------------------------


def parse_date(s: str) -> date:
    """解析日期字符串。"""
    return datetime.strptime(s, "%Y-%m-%d").date()


def resolve_time_range(range_name: str, today: date | None = None) -> tuple[date, date]:
    """解析时间范围名称到起止日期（含）。"""
    if today is None:
        today = date.today()

    if range_name == "yesterday":
        d = today - timedelta(days=1)
        return d, d
    if range_name == "last_7_days":
        end = today - timedelta(days=1)
        start = end - timedelta(days=6)
        return start, end
    if range_name == "last_30_days":
        end = today - timedelta(days=1)
        start = end - timedelta(days=29)
        return start, end
    if range_name == "last_90_days":
        end = today - timedelta(days=1)
        start = end - timedelta(days=89)
        return start, end

    try:
        d = parse_date(range_name)
        return d, d
    except Exception:
        raise ValueError(f"不支持的时间范围: {range_name}")


# -------------------------
# Umeng SDK 调用
# -------------------------


def get_sdk_root() -> str:
    """获取当前 skill 内部 SDK 根目录。"""
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(skill_dir, "友盟_openapi_python_SDK")


def init_sdk(api_key: str, api_security: str) -> None:
    """初始化 SDK 路径和默认服务器配置。"""
    sdk_root = get_sdk_root()
    if sdk_root not in sys.path:
        sys.path.insert(0, sdk_root)

    import aop
    aop.set_default_server('gateway.open.umeng.com')
    aop.set_default_appinfo(int(api_key), api_security)


def query_customer_source(data_source_id: str, source_type: str, from_date: date, to_date: date,
                          time_unit: str = "day", order_by: str = "newUser", direction: str = "desc") -> dict:
    """查询获客来源排行。"""
    from aop import api

    req = api.UmengUminiGetCustomerSourceOverviewRequest()
    req.dataSourceId = data_source_id
    req.sourceType = source_type
    req.fromDate = from_date.strftime("%Y-%m-%d")
    req.toDate = to_date.strftime("%Y-%m-%d")
    req.timeUnit = time_unit
    req.orderBy = order_by
    req.direction = direction

    resp = req.get_response()
    return resp if isinstance(resp, dict) else {}


def query_channel_overview(data_source_id: str, channel: str, from_date: date, to_date: date,
                           time_unit: str = "day", indicators: list[str] | None = None) -> dict:
    """查询渠道统计数据。"""
    from aop import api

    req = api.UmengUminiGetChannelOverviewRequest()
    req.dataSourceId = data_source_id
    req.channel = channel
    req.fromDate = from_date.strftime("%Y-%m-%d")
    req.toDate = to_date.strftime("%Y-%m-%d")
    req.timeUnit = time_unit
    req.indicators = ",".join(indicators or DEFAULT_INDICATORS)

    resp = req.get_response()
    return resp if isinstance(resp, dict) else {}


def query_campaign_overview(data_source_id: str, campaign: str, from_date: date, to_date: date,
                            time_unit: str = "day", indicators: list[str] | None = None) -> dict:
    """查询活动统计数据。"""
    from aop import api

    req = api.UmengUminiGetCampaignOverviewRequest()
    req.dataSourceId = data_source_id
    req.campaign = campaign
    req.fromDate = from_date.strftime("%Y-%m-%d")
    req.toDate = to_date.strftime("%Y-%m-%d")
    req.timeUnit = time_unit
    req.indicators = ",".join(indicators or DEFAULT_INDICATORS)

    resp = req.get_response()
    return resp if isinstance(resp, dict) else {}


def query_scene_overview(data_source_id: str, scene: str, from_date: date, to_date: date,
                         time_unit: str = "day", indicators: list[str] | None = None) -> dict:
    """查询场景值统计数据。"""
    from aop import api

    req = api.UmengUminiGetSceneOverviewRequest()
    req.dataSourceId = data_source_id
    req.scene = scene
    req.fromDate = from_date.strftime("%Y-%m-%d")
    req.toDate = to_date.strftime("%Y-%m-%d")
    req.timeUnit = time_unit
    req.indicators = ",".join(indicators or DEFAULT_INDICATORS)

    resp = req.get_response()
    return resp if isinstance(resp, dict) else {}


def query_scene_info_list(data_source_id: str, source_type: str = "channel") -> dict:
    """查询渠道或活动信息列表。
    
    注意：使用 getCustomerSourceOverview 接口获取列表，因为：
    - getSceneInfoList 返回的 code 字段（25位）与 getChannelOverview 需要的 channel 参数（26位 id）不匹配
    - getCustomerSourceOverview 返回的 id 字段可以直接用于 getChannelOverview/getCampaignOverview
    """
    from aop import api

    req = api.UmengUminiGetCustomerSourceOverviewRequest()
    req.dataSourceId = data_source_id
    req.sourceType = source_type
    req.fromDate = date.today().strftime("%Y-%m-%d")  # 使用今天作为查询日期
    req.toDate = date.today().strftime("%Y-%m-%d")
    req.timeUnit = "day"
    req.orderBy = "newUser"
    req.direction = "desc"

    resp = req.get_response()
    return resp if isinstance(resp, dict) else {}


# -------------------------
# 输出格式化
# -------------------------


def format_number(n) -> str:
    """格式化数字，添加千分位。"""
    if n is None:
        return "-"
    try:
        return f"{int(n):,}"
    except (ValueError, TypeError):
        return str(n)


def extract_data(result: dict) -> list:
    """从 API 响应中提取数据列表。"""
    outer_data = result.get("data", {})
    if isinstance(outer_data, dict):
        return outer_data.get("data", [])
    elif isinstance(outer_data, list):
        return outer_data
    return []


def build_customer_source_table(result: dict, source_type: str, app_name: str, query_date: date) -> str:
    """构建获客来源排行表格。"""
    data = extract_data(result)
    if not data:
        return f"未查询到{SOURCE_TYPE_NAMES.get(source_type, source_type)}获客来源数据。"

    type_name = SOURCE_TYPE_NAMES.get(source_type, source_type)
    lines = []
    lines.append(f"应用 [{app_name}] 的 {type_name} 获客排行（{query_date}）：")
    lines.append("")

    # 表头
    lines.append(f"{'排名':<6} {'名称':<20} {'新增用户':<12} {'活跃用户':<12} {'启动次数'}")
    lines.append("-" * 70)

    # 数据行
    for idx, item in enumerate(data, 1):
        name = item.get("name", item.get("code", "N/A"))[:18]
        new_user = item.get("newUser", 0)
        active_user = item.get("activeUser", 0)
        launch = item.get("launch", 0)
        lines.append(f"{idx:<6} {name:<20} {format_number(new_user):<12} {format_number(active_user):<12} {format_number(launch)}")

    return "\n".join(lines)


def build_overview_table(result: dict, name: str, query_type: str, app_name: str) -> str:
    """构建渠道/活动/场景值统计表格。"""
    data = extract_data(result)
    if not data:
        return f"未查询到 {query_type} [{name}] 的统计数据。"

    type_name = SOURCE_TYPE_NAMES.get(query_type, query_type)
    lines = []
    lines.append(f"应用 [{app_name}] 的 {type_name} [{name}] 统计数据：")
    lines.append("")

    # 表头
    lines.append(f"{'日期':<15} {'新增用户':<12} {'活跃用户':<12} {'启动次数':<12} {'访问次数'}")
    lines.append("-" * 70)

    # 数据行
    for item in data:
        date_str = item.get("dateTime", item.get("date", item.get("time", "")))
        new_user = item.get("newUser", 0)
        active_user = item.get("activeUser", 0)
        launch = item.get("launch", 0)
        visit_times = item.get("visitTimes", 0)
        lines.append(f"{date_str:<15} {format_number(new_user):<12} {format_number(active_user):<12} {format_number(launch):<12} {format_number(visit_times)}")

    return "\n".join(lines)


def build_trend_summary(app_info: dict, metric: str, name: str, query_type: str,
                        start: date, end: date, series: list[dict]) -> str:
    """构建趋势分析摘要。"""
    app_name = app_info["app"].get("name")
    metric_label = INDICATOR_NAMES.get(metric, metric)
    type_name = SOURCE_TYPE_NAMES.get(query_type, query_type)

    lines = [
        f"应用 [{app_name}] {type_name} [{name}] 的 {metric_label} 趋势（{start} 至 {end}）：",
        "",
    ]

    if not series:
        lines.append(f"暂无 {metric_label} 数据。")
        return "\n".join(lines)

    # 提取数值 - 使用指标名（如 activeUser、newUser）而非固定的 value 字段
    values = [item.get(metric) for item in series if item.get(metric) is not None]

    if not values:
        lines.append(f"暂无有效 {metric_label} 数据。")
        return "\n".join(lines)

    # API 返回数据按日期降序排列，所以 values[0] 是末期值，values[-1] 是初期值
    first_val = values[-1]  # 初期值（最早日期）
    last_val = values[0]    # 末期值（最新日期）
    avg_val = sum(values) / len(values)

    # 趋势判断
    if first_val == 0:
        trend = "变化情况不明显"
    else:
        change_rate = (last_val - first_val) / float(first_val)
        if change_rate > 0.05:
            trend = f"整体呈上升趋势，末期较初期上升 {change_rate*100:.1f}%"
        elif change_rate < -0.05:
            trend = f"整体呈下降趋势，末期较初期下降 {abs(change_rate)*100:.1f}%"
        else:
            trend = "整体基本持平"

    lines.append(f"日均 {metric_label}：{format_number(avg_val)}")
    lines.append(f"初期值：{format_number(first_val)}，末期值：{format_number(last_val)}")
    lines.append(trend)

    return "\n".join(lines)


def build_scene_info_list_table(result: dict, source_type: str, app_name: str) -> str:
    """构建渠道/活动列表表格。
    
    注意：使用 getCustomerSourceOverview 返回的 id 字段作为编码，
    该 id 可直接用于 --channel / --campaign 参数。
    """
    data = extract_data(result)
    if not data:
        return f"未查询到{SOURCE_TYPE_NAMES.get(source_type, source_type)}列表数据。"

    type_name = SOURCE_TYPE_NAMES.get(source_type, source_type)
    lines = []
    lines.append(f"应用 [{app_name}] 的 {type_name} 列表（共 {len(data)} 条）：")
    lines.append("")

    # 表头
    lines.append(f"{'序号':<6} {'编码':<26} {'名称'}")
    lines.append("-" * 65)

    # 数据行 - 使用 id 字段（可用于 --channel / --campaign）
    for idx, item in enumerate(data, 1):
        item_id = item.get("id", "")[:24]
        name = item.get("name", "")
        lines.append(f"{idx:<6} {item_id:<26} {name}")

    return "\n".join(lines)


def build_json_output(data: dict, success: bool = True) -> str:
    """构建 JSON 输出。"""
    output = {"success": success, "data": data}
    return json.dumps(output, ensure_ascii=False, indent=2)


def build_error_json(message: str) -> str:
    """构建错误 JSON 输出。"""
    return build_json_output({"error": message}, success=False)


# -------------------------
# CLI 入口
# -------------------------


def main():
    parser = argparse.ArgumentParser(
        description="uapp-mini-channel: 友盟小程序推广渠道查询",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 获客来源排行（各渠道昨天带来了多少用户）
  python3 scripts/mini_channel.py --app "小程序名称"

  # 活动排行
  python3 scripts/mini_channel.py --app "小程序名称" --customer-source --source-type campaign

  # 指定渠道统计
  python3 scripts/mini_channel.py --app "小程序名称" --channel "channel_code"

  # 指定渠道趋势分析
  python3 scripts/mini_channel.py --app "小程序名称" --channel "channel_code" \\
      --metric activeUser --range last_7_days

  # 指定活动效果
  python3 scripts/mini_channel.py --app "小程序名称" --campaign "campaign_code"

  # 场景值数据对比
  python3 scripts/mini_channel.py --app "小程序名称" --scene "wx_1011"

  # 查询渠道列表
  python3 scripts/mini_channel.py --app "小程序名称" --list

  # JSON 输出
  python3 scripts/mini_channel.py --app "小程序名称" --customer-source --json
"""
    )

    # 配置与应用
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--app", required=True, help="应用名称（仅支持小程序应用）")
    parser.add_argument("--account", help="账号 ID")
    parser.add_argument("--range", default="yesterday",
                        help="时间范围：yesterday/last_7_days/last_30_days/last_90_days 或 yyyy-mm-dd（默认 yesterday）")
    parser.add_argument("--from", dest="from_date", help="开始日期 (yyyy-mm-dd)，与 --to 配合使用")
    parser.add_argument("--to", dest="to_date", help="结束日期 (yyyy-mm-dd)，与 --from 配合使用")

    # 查询模式（互斥）
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--customer-source", action="store_true",
                            help="获客来源排行（默认模式）")
    mode_group.add_argument("--channel", metavar="CODE", help="查询指定渠道")
    mode_group.add_argument("--campaign", metavar="CODE", help="查询指定活动")
    mode_group.add_argument("--scene", metavar="CODE", help="查询指定场景值")
    mode_group.add_argument("--list", action="store_true", help="查询渠道/活动列表")

    # 子参数
    parser.add_argument("--source-type", choices=["channel", "campaign", "platform", "scene"],
                        default="channel", help="来源类型（默认 channel）")
    parser.add_argument("--indicators", help="指标列表，逗号分隔（默认：newUser,activeUser,launch）")
    parser.add_argument("--order-by", choices=["newUser", "activeUser", "launch", "visitTimes", "onceDuration", "createDateTime"],
                        default="newUser", help="排序字段（默认 newUser）")
    parser.add_argument("--direction", choices=["asc", "desc"], default="desc",
                        help="排序方向（默认 desc）")
    parser.add_argument("--metric", choices=["newUser", "activeUser", "launch", "visitTimes", "onceDuration"],
                        help="趋势分析指标（与 --range 配合使用）")
    parser.add_argument("--top", type=int, default=10, help="Top N 结果，默认 10")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出")

    args = parser.parse_args()

    try:
        # 加载配置
        config_path = resolve_config_path(args.config)
        config = load_config(config_path)

        # 解析应用
        app_info = resolve_app(config, args.app, args.account)
        data_source_id = app_info["app"]["appkey"]

        # 初始化 SDK
        init_sdk(app_info["apiKey"], app_info["apiSecurity"])

        # 执行查询
        result = None
        output = ""

        # 解析 indicators
        indicators = args.indicators.split(",") if args.indicators else None

        # 解析时间范围
        if args.from_date and args.to_date:
            from_date = parse_date(args.from_date)
            to_date = parse_date(args.to_date)
        else:
            from_date, to_date = resolve_time_range(args.range)

        # 获客来源排行（默认模式）
        if args.customer_source or (not args.channel and not args.campaign and not args.scene and not args.list):
            result = query_customer_source(
                data_source_id, args.source_type, from_date, to_date,
                order_by=args.order_by, direction=args.direction
            )
            output = build_customer_source_table(result, args.source_type, app_info["app"]["name"], from_date)

        # 指定渠道查询
        elif args.channel:
            if args.metric:
                # 趋势分析模式
                result = query_channel_overview(
                    data_source_id, args.channel, from_date, to_date, indicators=[args.metric]
                )
                series = extract_data(result)
                output = build_trend_summary(
                    app_info, args.metric, args.channel, "channel", from_date, to_date, series
                )
            else:
                # 普通统计模式
                result = query_channel_overview(
                    data_source_id, args.channel, from_date, to_date, indicators=indicators
                )
                output = build_overview_table(result, args.channel, "channel", app_info["app"]["name"])

        # 指定活动查询
        elif args.campaign:
            if args.metric:
                result = query_campaign_overview(
                    data_source_id, args.campaign, from_date, to_date, indicators=[args.metric]
                )
                series = extract_data(result)
                output = build_trend_summary(
                    app_info, args.metric, args.campaign, "campaign", from_date, to_date, series
                )
            else:
                result = query_campaign_overview(
                    data_source_id, args.campaign, from_date, to_date, indicators=indicators
                )
                output = build_overview_table(result, args.campaign, "campaign", app_info["app"]["name"])

        # 指定场景值查询
        elif args.scene:
            if args.metric:
                result = query_scene_overview(
                    data_source_id, args.scene, from_date, to_date, indicators=[args.metric]
                )
                series = extract_data(result)
                output = build_trend_summary(
                    app_info, args.metric, args.scene, "scene", from_date, to_date, series
                )
            else:
                result = query_scene_overview(
                    data_source_id, args.scene, from_date, to_date, indicators=indicators
                )
                output = build_overview_table(result, args.scene, "scene", app_info["app"]["name"])

        # 列表查询
        elif args.list:
            result = query_scene_info_list(data_source_id, args.source_type)
            output = build_scene_info_list_table(result, args.source_type, app_info["app"]["name"])

        # 输出结果
        if args.json:
            print(build_json_output(result))
        else:
            print(output)

    except Exception as e:
        if hasattr(args, 'json') and args.json:
            print(build_error_json(str(e)))
        else:
            print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
