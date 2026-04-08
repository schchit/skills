#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""uapp-umini: 友盟小程序数据查询入口脚本

功能目标：
- 读取 umeng-config.json（支持 --config / UMENG_CONFIG_PATH / 当前目录 / .env）
- 解析应用（支持 --app / --account，含模糊匹配，仅支持小程序应用）
- 支持概况数据查询（启动、活跃、新增、访次、停留时长）
- 支持累计用户查询
- 支持留存数据查询（次日/7日/30日留存）
- 支持页面分析（受访页面、入口页面）
- 支持分享分析（分享概况、页面分享、分享用户）
- 支持场景分析（场景值列表、场景统计）
- 支持自定义事件（事件列表、事件统计、事件属性、属性值分布）
- 支持时间范围：yesterday / last_7_days / last_30_days
- 输出：
  - 文本模式：表格/摘要
  - JSON 模式：结构化数据
"""

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta

# -------------------------
# 微信小程序场景值字典
# -------------------------
WX_SCENE_VALUES = {
    "wx_1000": "其他",
    "wx_1001": "发现栏小程序主入口，「最近使用」列表",
    "wx_1005": "微信首页顶部搜索框的搜索结果页",
    "wx_1006": "发现栏小程序主入口搜索框的搜索结果页",
    "wx_1007": "单人聊天会话中的小程序消息卡片",
    "wx_1008": "群聊会话中的小程序消息卡片",
    "wx_1011": "扫描二维码",
    "wx_1012": "长按图片识别二维码",
    "wx_1013": "扫描手机相册中选取的二维码",
    "wx_1014": "小程序模板消息",
    "wx_1017": "前往小程序体验版的入口页",
    "wx_1019": "微信钱包（微信客户端7.0.0版本改为支付入口）",
    "wx_1020": "公众号 profile 页相关小程序列表（已废弃）",
    "wx_1022": "聊天顶部置顶小程序入口（微信客户端6.6.1版本起废弃）",
    "wx_1023": "安卓系统桌面图标",
    "wx_1024": "小程序 profile 页",
    "wx_1025": "扫描一维码",
    "wx_1026": "发现栏小程序主入口，「附近的小程序」列表",
    "wx_1027": "微信首页顶部搜索框搜索结果页「使用过的小程序」列表",
    "wx_1028": "我的卡包",
    "wx_1029": "小程序中的卡券详情页",
    "wx_1030": "自动化测试下打开小程序",
    "wx_1031": "长按图片识别一维码",
    "wx_1032": "扫描手机相册中选取的一维码",
    "wx_1034": "微信支付完成页",
    "wx_1035": "公众号自定义菜单",
    "wx_1036": "App 分享消息卡片",
    "wx_1037": "小程序打开小程序",
    "wx_1038": "从另一个小程序返回",
    "wx_1039": "摇电视",
    "wx_1042": "添加好友搜索框的搜索结果页",
    "wx_1043": "公众号模板消息",
    "wx_1044": "带 shareTicket 的小程序消息卡片",
    "wx_1045": "朋友圈广告",
    "wx_1046": "朋友圈广告详情页",
    "wx_1047": "扫描小程序码",
    "wx_1048": "长按图片识别小程序码",
    "wx_1049": "扫描手机相册中选取的小程序码",
    "wx_1052": "卡券的适用门店列表",
    "wx_1053": "搜一搜的结果页",
    "wx_1054": "顶部搜索框小程序快捷入口（微信客户端版本6.7.4起废弃）",
    "wx_1056": "聊天顶部音乐播放器右上角菜单",
    "wx_1057": "钱包中的银行卡详情页",
    "wx_1058": "公众号文章",
    "wx_1059": "体验版小程序绑定邀请页",
    "wx_1064": "微信首页连Wi-Fi状态栏",
    "wx_1067": "公众号文章广告",
    "wx_1068": "附近小程序列表广告（已废弃）",
    "wx_1069": "移动应用",
    "wx_1071": "钱包中的银行卡列表页",
    "wx_1072": "二维码收款页面",
    "wx_1073": "客服消息列表下发的小程序消息卡片",
    "wx_1074": "公众号会话下发的小程序消息卡片",
    "wx_1077": "摇周边",
    "wx_1078": "微信连Wi-Fi成功提示页",
    "wx_1079": "微信游戏中心",
    "wx_1081": "客服消息下发的文字链",
    "wx_1082": "公众号会话下发的文字链",
    "wx_1084": "朋友圈广告原生页",
    "wx_1088": "会话中查看系统消息，打开小程序",
    "wx_1089": "微信聊天主界面下拉，「最近使用」栏",
    "wx_1090": "长按小程序右上角菜单唤出最近使用历史",
    "wx_1091": "公众号文章商品卡片",
    "wx_1092": "城市服务入口",
    "wx_1095": "小程序广告组件",
    "wx_1096": "聊天记录，打开小程序",
    "wx_1097": "微信支付签约原生页，打开小程序",
    "wx_1099": "页面内嵌插件",
    "wx_1102": "公众号 profile 页服务预览",
    "wx_1103": "发现栏小程序主入口，「我的小程序」列表（基础库2.2.4版本起废弃）",
    "wx_1104": "微信聊天主界面下拉，「我的小程序」栏（基础库2.2.4版本起废弃）",
    "wx_1106": "聊天主界面下拉，从顶部搜索结果页，打开小程序",
    "wx_1107": "订阅消息，打开小程序",
    "wx_1113": "安卓手机负一屏，打开小程序（三星）",
    "wx_1114": "安卓手机侧边栏，打开小程序（三星）",
    "wx_1124": "扫「一物一码」打开小程序",
    "wx_1125": "长按图片识别「一物一码」",
    "wx_1126": "扫描手机相册中选取的「一物一码」",
    "wx_1129": "微信爬虫访问",
    "wx_1131": "浮窗打开小程序",
    "wx_1133": "硬件设备打开小程序",
    "wx_1135": "小程序profile页其他小程序列表，打开小程序",
    "wx_1146": "地理位置信息打开出行类小程序",
    "wx_1148": "卡包-交通卡，打开小程序",
    "wx_1150": "扫一扫商品条码结果页打开小程序",
    "wx_1153": "「识物」结果页打开小程序",
    "wx_1154": "朋友圈内打开「单页模式」",
    "wx_1155": "「单页模式」打开小程序",
    "wx_1169": "发现栏小程序主入口，各个生活服务入口",
}

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


MINI_PROGRAM_PLATFORMS = ["微信小程序", "支付宝小程序", "百度小程序", "字节跳动小程序", "QQ小程序", "H5", "小游戏"]


def is_mini_program(platform: str) -> bool:
    """判断是否为小程序/H5/小游戏平台。"""
    return platform in MINI_PROGRAM_PLATFORMS


def find_app_by_name(config: dict, app_name: str, account_id: str | None = None, mini_only: bool = True):
    """按应用名称查找应用配置，支持精确匹配 + 去空格模糊匹配。"""
    matches = []
    normalized_input = normalize_app_name(app_name)

    for account in config.get("accounts", []):
        if account_id and account.get("id") != account_id:
            continue
        for app in account.get("apps", []):
            platform = app.get("platform", "")
            if mini_only and not is_mini_program(platform):
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
        result = find_app_by_name(config, app_name, account_id=account_id, mini_only=True)
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


def query_overview(data_source_id: str, from_date: date, to_date: date,
                   time_unit: str = "day", indicators: list[str] | None = None) -> dict:
    """查询概况数据。"""
    from aop import api

    req = api.UmengUminiGetOverviewRequest()
    req.dataSourceId = data_source_id
    req.fromDate = from_date.strftime("%Y-%m-%d")
    req.toDate = to_date.strftime("%Y-%m-%d")
    req.timeUnit = time_unit
    # indicators 是必填参数，默认使用全部指标
    # 官方支持的指标：newUser/activeUser/launch/visitTimes/onceDuration/dailyDuration
    if not indicators:
        indicators = ["activeUser", "newUser", "launch", "visitTimes", "onceDuration", "dailyDuration"]
    req.indicators = ",".join(indicators)

    resp = req.get_response()
    # 处理可能的字符串响应
    if isinstance(resp, str):
        import json
        resp = json.loads(resp)
    return resp if isinstance(resp, dict) else {}


def query_total_user(data_source_id: str, from_date: date, to_date: date) -> dict:
    """查询累计用户。"""
    from aop import api

    req = api.UmengUminiGetTotalUserRequest()
    req.dataSourceId = data_source_id
    req.fromDate = from_date.strftime("%Y-%m-%d")
    req.toDate = to_date.strftime("%Y-%m-%d")

    resp = req.get_response()
    return resp if isinstance(resp, dict) else {}


def query_retention(data_source_id: str, from_date: date, to_date: date,
                    time_unit: str = "day", value_type: str = "rate", indicator: str = "newUser") -> dict:
    """查询留存数据，自动分页获取全部数据。每页固定返回10条，通过 pageIndex 翻页。"""
    from aop import api

    page_size = 10
    page_index = 1
    all_data = []

    while True:
        req = api.UmengUminiGetRetentionByDataSourceIdRequest()
        req.dataSourceId = data_source_id
        req.fromDate = from_date.strftime("%Y-%m-%d")
        req.toDate = to_date.strftime("%Y-%m-%d")
        req.timeUnit = time_unit
        req.valueType = value_type
        req.indicator = indicator
        req.pageIndex = page_index
        req.pageSize = page_size

        resp = req.get_response()
        if not isinstance(resp, dict):
            break

        inner = resp.get("data", {})
        if not isinstance(inner, dict):
            break

        page_data = inner.get("data", [])
        all_data.extend(page_data)

        # 当前页返回条数不足 page_size，说明已是最后一页
        if len(page_data) < page_size:
            break
        page_index += 1

    # 组装成统一格式返回
    return {"data": {"data": all_data, "totalCount": len(all_data)}, "success": True}


def query_visit_pages(data_source_id: str, from_date: date, to_date: date,
                      time_unit: str = "day", order_by: str | None = None,
                      direction: str = "desc", page_index: int = 1, page_size: int = 20) -> dict:
    """查询受访页面列表。"""
    from aop import api

    req = api.UmengUminiGetVisitPageListRequest()
    req.dataSourceId = data_source_id
    req.fromDate = from_date.strftime("%Y-%m-%d")
    req.toDate = to_date.strftime("%Y-%m-%d")
    req.timeUnit = time_unit
    if order_by:
        req.orderBy = order_by
        req.direction = direction
    req.pageIndex = page_index
    req.pageSize = page_size

    resp = req.get_response()
    return resp if isinstance(resp, dict) else {}


def query_landing_pages(data_source_id: str, from_date: date, to_date: date,
                        time_unit: str = "day", order_by: str | None = None,
                        direction: str = "desc", page_index: int = 1, page_size: int = 20) -> dict:
    """查询入口页面列表。"""
    from aop import api

    req = api.UmengUminiGetLandingPageListRequest()
    req.dataSourceId = data_source_id
    req.fromDate = from_date.strftime("%Y-%m-%d")
    req.toDate = to_date.strftime("%Y-%m-%d")
    req.timeUnit = time_unit
    if order_by:
        req.orderBy = order_by
        req.direction = direction
    req.pageIndex = page_index
    req.pageSize = page_size

    resp = req.get_response()
    return resp if isinstance(resp, dict) else {}


def query_share_overview(data_source_id: str, from_date: date, to_date: date,
                         time_unit: str = "day") -> dict:
    """查询分享概况。"""
    from aop import api

    req = api.UmengUminiGetShareOverviewRequest()
    req.dataSourceId = data_source_id
    req.fromDate = from_date.strftime("%Y-%m-%d")
    req.toDate = to_date.strftime("%Y-%m-%d")
    req.timeUnit = time_unit

    resp = req.get_response()
    return resp if isinstance(resp, dict) else {}


def query_share_pages(data_source_id: str, from_date: date, to_date: date,
                      time_unit: str = "day", order_by: str | None = None,
                      direction: str = "desc", page_index: int = 1, page_size: int = 20) -> dict:
    """查询页面分享概况。"""
    from aop import api

    req = api.UmengUminiGetSharePageOverviewRequest()
    req.dataSourceId = data_source_id
    req.fromDate = from_date.strftime("%Y-%m-%d")
    req.toDate = to_date.strftime("%Y-%m-%d")
    req.timeUnit = time_unit
    if order_by:
        req.orderBy = order_by
        req.direction = direction
    req.pageIndex = page_index
    req.pageSize = page_size

    resp = req.get_response()
    return resp if isinstance(resp, dict) else {}


def query_share_users(data_source_id: str, from_date: date, to_date: date,
                      time_unit: str = "day", order_by: str | None = None,
                      direction: str = "desc", page_index: int = 1, page_size: int = 20) -> dict:
    """查询分享用户列表。"""
    from aop import api

    req = api.UmengUminiGetShareUserListRequest()
    req.dataSourceId = data_source_id
    req.fromDate = from_date.strftime("%Y-%m-%d")
    req.toDate = to_date.strftime("%Y-%m-%d")
    req.timeUnit = time_unit
    if order_by:
        req.orderBy = order_by
        req.direction = direction
    req.pageIndex = page_index
    req.pageSize = page_size

    resp = req.get_response()
    return resp if isinstance(resp, dict) else {}


def query_scene_list(data_source_id: str, source_type: str = "channel") -> dict:
    """查询场景值列表。"""
    from aop import api

    req = api.UmengUminiGetSceneInfoListRequest()
    req.dataSourceId = data_source_id
    req.sourceType = source_type

    resp = req.get_response()
    return resp if isinstance(resp, dict) else {}


def query_scene_stats(data_source_id: str, scene: str, from_date: date, to_date: date,
                      time_unit: str = "day", indicators: list[str] | None = None) -> dict:
    """查询场景统计。"""
    from aop import api

    req = api.UmengUminiGetSceneOverviewRequest()
    req.dataSourceId = data_source_id
    req.scene = scene
    req.fromDate = from_date.strftime("%Y-%m-%d")
    req.toDate = to_date.strftime("%Y-%m-%d")
    req.timeUnit = time_unit
    if indicators:
        req.indicators = ",".join(indicators)

    resp = req.get_response()
    return resp if isinstance(resp, dict) else {}


def query_event_list(data_source_id: str) -> dict:
    """查询自定义事件列表。"""
    from aop import api

    req = api.UmengUminiGetEventListRequest()
    req.dataSourceId = data_source_id

    resp = req.get_response()
    return resp if isinstance(resp, dict) else {}


def query_event_overview(data_source_id: str, event_name: str,
                         from_date: date, to_date: date, time_unit: str = "day") -> dict:
    """查询事件统计。"""
    from aop import api

    req = api.UmengUminiGetEventOverviewRequest()
    req.dataSourceId = data_source_id
    req.eventName = event_name
    req.fromDate = from_date.strftime("%Y-%m-%d")
    req.toDate = to_date.strftime("%Y-%m-%d")
    req.timeUnit = time_unit

    resp = req.get_response()
    return resp if isinstance(resp, dict) else {}


def query_event_props(data_source_id: str, event_name: str) -> dict:
    """查询事件属性列表。"""
    from aop import api

    req = api.UmengUminiGetEventProvertyListRequest()
    req.dataSourceId = data_source_id
    req.eventName = event_name

    resp = req.get_response()
    return resp if isinstance(resp, dict) else {}


def query_prop_values(data_source_id: str, event_name: str, property_name: str,
                      from_date: date, to_date: date, time_unit: str = "day",
                      page_index: int = 1, page_size: int = 20) -> dict:
    """查询属性值分布。"""
    from aop import api

    req = api.UmengUminiGetAllPropertyValueCountRequest()
    req.dataSourceId = data_source_id
    req.eventName = event_name
    req.propertyName = property_name
    req.fromDate = from_date.strftime("%Y-%m-%d")
    req.toDate = to_date.strftime("%Y-%m-%d")
    req.timeUnit = time_unit
    req.pageIndex = page_index
    req.pageSize = page_size

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


def format_percent(n, decimals: int = 2) -> str:
    """格式化百分比。"""
    if n is None:
        return "-"
    try:
        return f"{float(n):.{decimals}f}%"
    except (ValueError, TypeError):
        return str(n)


def build_overview_table(result: dict, indicators: list[str] | None = None) -> str:
    """构建概况数据表格。"""
    # 解析嵌套的数据结构: result["data"]["data"]
    outer_data = result.get("data", {})
    if isinstance(outer_data, dict):
        data = outer_data.get("data", [])
    else:
        data = []
    
    if not data:
        return "未查询到概况数据。"

    # 指标名称映射（与官方API一致）
    # 官方支持的指标：newUser/activeUser/launch/visitTimes/onceDuration/dailyDuration
    indicator_names = {
        "activeUser": "活跃用户",
        "newUser": "新增用户",
        "launch": "启动次数",
        "visitTimes": "访问次数",
        "onceDuration": "次均停留时长",
        "dailyDuration": "人均停留时长",
    }

    lines = []
    lines.append("概况数据")
    lines.append("-" * 60)
    lines.append(f"{'日期':<15} {'指标':<15} {'数值'}")
    lines.append("-" * 60)

    for item in data:
        date_str = item.get("dateTime", item.get("date", item.get("time", "")))
        for key, name in indicator_names.items():
            if indicators and key not in indicators:
                continue
            value = item.get(key)
            if value is not None:
                lines.append(f"{date_str:<15} {name:<15} {format_number(value)}")

    return "\n".join(lines)


def extract_data(result: dict) -> list:
    """从 API 响应中提取数据列表。"""
    outer_data = result.get("data", {})
    if isinstance(outer_data, dict):
        return outer_data.get("data", [])
    elif isinstance(outer_data, list):
        return outer_data
    return []


def build_total_user_table(result: dict) -> str:
    """构建累计用户表格。"""
    data = extract_data(result)
    if not data:
        return "未查询到累计用户数据。"

    lines = []
    lines.append("累计用户")
    lines.append("-" * 40)
    lines.append(f"{'日期':<15} {'累计用户数'}")
    lines.append("-" * 40)

    for item in data:
        date_str = item.get("dateTime", item.get("date", item.get("time", "")))
        total = item.get("totalUser", item.get("total", 0))
        lines.append(f"{date_str:<15} {format_number(total)}")

    return "\n".join(lines)


def build_retention_table(result: dict, indicator: str = "newuser", time_unit: str = "day") -> str:
    """构建留存数据表格。"""
    data = extract_data(result)
    if not data:
        return "未查询到留存数据。"

    # 根据 indicator 显示不同的标题
    indicator_names = {
        "newUser": "新增用户",
        "activeUser": "活跃用户"
    }
    user_label = indicator_names.get(indicator, "用户")

    # 根据时间粒度决定列标签
    if time_unit == "week":
        period_labels = ["1周", "2周", "3周", "4周", "5周", "6周", "7周"]
        date_label = "周期"
    else:
        period_labels = ["1日", "2日", "3日", "4日", "5日", "6日", "7日"]
        date_label = "日期"

    lines = []
    lines.append(f"留存数据（{user_label}）")
    lines.append("-" * 80)
    header_periods = "  ".join(f"{lbl:<8}" for lbl in period_labels)
    lines.append(f"{date_label:<14} {user_label:<10} {header_periods}")
    lines.append("-" * 80)

    for item in data:
        date_str = item.get("dateTime", item.get("date", item.get("time", "")))
        value = item.get("value", 0)
        # v1-v7 表示1-7日/周留存率
        v1 = item.get("v1", "-")
        v2 = item.get("v2", "-")
        v3 = item.get("v3", "-")
        v4 = item.get("v4", "-")
        v5 = item.get("v5", "-")
        v6 = item.get("v6", "-")
        v7 = item.get("v7", "-")
        period_vals = "  ".join(f"{v:<8}" for v in [v1, v2, v3, v4, v5, v6, v7])
        lines.append(f"{date_str:<14} {format_number(value):<10} {period_vals}")

    return "\n".join(lines)


def build_page_table(result: dict, title: str, is_visit: bool = True) -> str:
    """构建页面列表表格。"""
    data = extract_data(result)
    if not data:
        return f"未查询到{title}数据。"

    lines = []
    lines.append(f"{title}（共 {len(data)} 条）")
    lines.append("-" * 80)
    
    if is_visit:
        lines.append(f"{'序号':<6} {'页面路径':<40} {'访问次数':<12} {'访问用户'}")
    else:
        lines.append(f"{'序号':<6} {'页面路径':<40} {'访问次数':<12} {'访问用户':<12} {'跳出率'}")
    lines.append("-" * 80)

    for i, item in enumerate(data):
        page = item.get("page", item.get("pageUrl", ""))[:38]
        if is_visit:
            visit_pv = item.get("visitTimes", item.get("visitPv", item.get("pv", 0)))
            visit_uv = item.get("visitUser", item.get("visitUv", item.get("uv", 0)))
            lines.append(f"{i+1:<6} {page:<40} {format_number(visit_pv):<12} {format_number(visit_uv)}")
        else:
            visit_times = item.get("visitTimes", item.get("landingPv", 0))
            visit_user = item.get("visitUser", item.get("landingUser", 0))
            jump_ratio = item.get("jumpRatio", "-")
            lines.append(f"{i+1:<6} {page:<40} {format_number(visit_times):<12} {format_number(visit_user):<12} {jump_ratio}")

    return "\n".join(lines)


def build_share_overview_table(result: dict) -> str:
    """构建分享概况表格。"""
    data = extract_data(result)
    if not data:
        return "未查询到分享概况数据。"

    lines = []
    lines.append("分享概况")
    lines.append("-" * 80)
    lines.append(f"{'日期':<15} {'分享次数':<12} {'分享人数':<12} {'回流量':<12} {'回流率':<12} {'新用户'}")
    lines.append("-" * 80)

    for item in data:
        date_str = item.get("dateTime", item.get("date", item.get("time", "")))
        share_count = item.get("count", item.get("shareCount", 0))
        share_user = item.get("user", item.get("shareUser", 0))
        reflow = item.get("reflow", item.get("backFlow", 0))
        reflow_ratio = item.get("reflowRatio", "-")
        new_user = item.get("newUser", 0)
        lines.append(f"{date_str:<15} {format_number(share_count):<12} {format_number(share_user):<12} {format_number(reflow):<12} {reflow_ratio:<12} {format_number(new_user)}")

    return "\n".join(lines)


def build_share_pages_table(result: dict) -> str:
    """构建页面分享表格。"""
    data = extract_data(result)
    if not data:
        return "未查询到页面分享数据。"

    lines = []
    lines.append(f"页面分享概况（共 {len(data)} 条）")
    lines.append("-" * 70)
    lines.append(f"{'序号':<6} {'页面路径':<35} {'分享次数':<12} {'分享人数'}")
    lines.append("-" * 70)

    for i, item in enumerate(data):
        page = item.get("path", item.get("page", item.get("pageUrl", "")))[:33]
        share_count = item.get("count", item.get("shareCount", 0))
        share_user = item.get("user", item.get("shareUser", 0))
        lines.append(f"{i+1:<6} {page:<35} {format_number(share_count):<12} {format_number(share_user)}")

    return "\n".join(lines)


def build_share_users_table(result: dict) -> str:
    """构建分享用户表格。"""
    data = extract_data(result)
    if not data:
        return "未查询到分享用户数据。"

    lines = []
    lines.append(f"分享用户列表（共 {len(data)} 条）")
    lines.append("-" * 70)
    lines.append(f"{'序号':<6} {'用户ID':<30} {'分享次数':<10} {'回流量':<10} {'回流率'}")
    lines.append("-" * 70)

    for i, item in enumerate(data):
        user_id = item.get("userId", item.get("id", ""))[:28]
        share_count = item.get("count", item.get("shareCount", 0))
        reflow = item.get("reflow", 0)
        reflow_ratio = item.get("reflowRatio", 0)
        lines.append(f"{i+1:<6} {user_id:<30} {format_number(share_count):<10} {format_number(reflow):<10} {reflow_ratio}%")

    return "\n".join(lines)


def build_scene_list_table(result: dict, source_type: str) -> str:
    """构建场景值列表表格。"""
    data = extract_data(result)
    if not data:
        return "未查询到场景值数据。"

    type_names = {"channel": "渠道", "campaign": "活动"}
    
    lines = []
    lines.append(f"{type_names.get(source_type, source_type)}列表（共 {len(data)} 条）")
    lines.append("-" * 50)
    lines.append(f"{'序号':<6} {'场景值':<20} {'场景名称'}")
    lines.append("-" * 50)

    for i, item in enumerate(data):
        scene = item.get("code", item.get("scene", item.get("value", "")))
        name = item.get("name", "")
        lines.append(f"{i+1:<6} {scene:<20} {name}")

    return "\n".join(lines)


def build_wx_scene_list_table() -> str:
    """构建微信小程序场景值列表表格（内置字典）。"""
    lines = []
    lines.append(f"微信小程序场景值列表（共 {len(WX_SCENE_VALUES)} 个）")
    lines.append("-" * 80)
    lines.append(f"{'场景值':<15} {'场景描述'}")
    lines.append("-" * 80)

    for scene_id, desc in sorted(WX_SCENE_VALUES.items()):
        lines.append(f"{scene_id:<15} {desc}")

    return "\n".join(lines)


def build_scene_stats_table(result: dict, scene: str) -> str:
    """构建场景统计表格。"""
    data = extract_data(result)
    if not data:
        return f"未查询到场景 {scene} 的统计数据。"

    lines = []
    lines.append(f"场景统计（场景值: {scene}）")
    lines.append("-" * 60)
    lines.append(f"{'日期':<15} {'活跃用户':<12} {'新增用户':<12} {'访问次数'}")
    lines.append("-" * 60)

    for item in data:
        date_str = item.get("dateTime", item.get("date", item.get("time", "")))
        active_user = item.get("activeUser", 0)
        new_user = item.get("newUser", 0)
        visit = item.get("visitTimes", item.get("visit", 0))
        lines.append(f"{date_str:<15} {format_number(active_user):<12} {format_number(new_user):<12} {format_number(visit)}")

    return "\n".join(lines)


def build_event_list_table(result: dict) -> str:
    """构建事件列表表格。"""
    data = extract_data(result)
    if not data:
        return "未查询到自定义事件数据。"

    lines = []
    lines.append(f"自定义事件列表（共 {len(data)} 个）")
    lines.append("-" * 70)
    lines.append(f"{'序号':<6} {'事件名称':<30} {'显示名称'}")
    lines.append("-" * 70)

    for i, item in enumerate(data):
        event_name = (item.get("eventName", item.get("name", "")))[:28]
        display_name = item.get("displayName", "")
        lines.append(f"{i+1:<6} {event_name:<30} {display_name}")

    return "\n".join(lines)


def build_event_stats_table(result: dict, event_name: str) -> str:
    """构建事件统计表格。"""
    data = extract_data(result)
    if not data:
        return f"未查询到事件 {event_name} 的统计数据。"

    lines = []
    lines.append(f"事件统计（{event_name}）")
    lines.append("-" * 50)
    lines.append(f"{'日期':<15} {'触发次数':<15} {'触发用户数'}")
    lines.append("-" * 50)

    for item in data:
        date_str = item.get("dateTime", item.get("date", item.get("time", "")))
        count = item.get("count", 0)
        device = item.get("device", 0)
        lines.append(f"{date_str:<15} {format_number(count):<15} {format_number(device)}")

    return "\n".join(lines)


def build_event_props_table(result: dict, event_name: str) -> str:
    """构建事件属性列表表格。"""
    data = extract_data(result)
    if not data:
        return f"事件 {event_name} 暂无属性数据。"

    lines = []
    lines.append(f"事件属性列表（{event_name}，共 {len(data)} 个）")
    lines.append("-" * 40)
    lines.append(f"{'序号':<6} {'属性名称'}")
    lines.append("-" * 40)

    for i, item in enumerate(data):
        prop_name = item.get("propertyName", item.get("name", ""))
        lines.append(f"{i+1:<6} {prop_name}")

    return "\n".join(lines)


def build_prop_values_table(result: dict, event_name: str, prop_name: str) -> str:
    """构建属性值分布表格。"""
    data = extract_data(result)
    if not data:
        return f"属性 {prop_name} 暂无数据。"

    lines = []
    lines.append(f"属性值分布（{event_name}.{prop_name}，共 {len(data)} 个）")
    lines.append("-" * 70)
    lines.append(f"{'序号':<6} {'属性值':<30} {'次数':<12} {'占比'}")
    lines.append("-" * 70)

    for i, item in enumerate(data):
        value = str(item.get("propertyValue", item.get("value", "")))[:28]
        count = item.get("count", 0)
        ratio = item.get("countRatio", "-")
        lines.append(f"{i+1:<6} {value:<30} {format_number(count):<12} {ratio}%")

    return "\n".join(lines)


# -------------------------
# JSON 输出
# -------------------------


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
        description="uapp-umini: 友盟小程序数据查询入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 查询概况数据
  python3 scripts/umini.py --overview --app "友小盟数据官"

  # 查询累计用户
  python3 scripts/umini.py --total-user --app "友小盟数据官"

  # 查询留存数据（新增用户）
  python3 scripts/umini.py --retention --app "友小盟数据官"

  # 查询活跃用户留存
  python3 scripts/umini.py --retention --indicator activeUser --app "友小盟数据官"

  # 查询受访页面
  python3 scripts/umini.py --visit-pages --app "友小盟数据官"

  # 查询入口页面
  python3 scripts/umini.py --landing-pages --app "友小盟数据官"

  # 查询分享概况
  python3 scripts/umini.py --share-overview --app "友小盟数据官"

  # 查询场景值列表
  python3 scripts/umini.py --list-scenes --app "友小盟数据官"

  # 查询自定义事件
  python3 scripts/umini.py --list-events --app "友小盟数据官"

  # JSON 输出
  python3 scripts/umini.py --overview --app "友小盟数据官" --json
"""
    )

    # 配置与应用
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--app", required=True, help="应用名称（仅支持小程序应用）")
    parser.add_argument("--account", help="账号 ID")
    parser.add_argument("--range", default="yesterday", help="时间范围：yesterday/last_7_days/last_30_days 或 yyyy-mm-dd（默认 yesterday）")
    parser.add_argument("--from", dest="from_date", help="开始日期 (yyyy-mm-dd)，与 --to 配合使用")
    parser.add_argument("--to", dest="to_date", help="结束日期 (yyyy-mm-dd)，与 --from 配合使用")

    # 查询模式（互斥）
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--overview", action="store_true", help="查询概况数据")
    mode_group.add_argument("--total-user", action="store_true", help="查询累计用户")
    mode_group.add_argument("--retention", action="store_true", help="查询留存数据")
    mode_group.add_argument("--visit-pages", action="store_true", help="查询受访页面")
    mode_group.add_argument("--landing-pages", action="store_true", help="查询入口页面")
    mode_group.add_argument("--share-overview", action="store_true", help="查询分享概况")
    mode_group.add_argument("--share-pages", action="store_true", help="查询页面分享")
    mode_group.add_argument("--share-users", action="store_true", help="查询分享用户")
    mode_group.add_argument("--list-scenes", action="store_true", help="查询渠道/活动场景值列表")
    mode_group.add_argument("--list-scenes-wx", action="store_true", help="查询微信小程序场景值列表（内置）")
    mode_group.add_argument("--scene-stats", metavar="SCENE", help="查询场景统计")
    mode_group.add_argument("--list-events", action="store_true", help="查询事件列表")
    mode_group.add_argument("--event-stats", metavar="EVENT", help="查询事件统计")
    mode_group.add_argument("--list-props", metavar="EVENT", help="查询事件属性列表")
    mode_group.add_argument("--prop-values", metavar="EVENT", help="查询属性值分布")

    # 子参数
    parser.add_argument("--indicators", help="指标列表（概况查询），逗号分隔")
    parser.add_argument("--value-type", choices=["rate", "num"],
                        default="rate", help="留存数据类型：rate(留存率)/num(留存数)，默认 rate")
    parser.add_argument("--indicator", choices=["newUser", "activeUser"],
                        default="newUser", help="留存指标：newUser(新增用户)/activeUser(活跃用户)，默认 newUser")
    parser.add_argument("--time-unit", choices=["day", "week"],
                        default="day", help="留存时间粒度：day(日)/week(周)，默认 day")
    parser.add_argument("--source-type", choices=["channel", "campaign"],
                        default="channel", help="场景类型（默认 channel）")
    parser.add_argument("--prop", help="属性名称（属性值分布查询）")
    parser.add_argument("--order-by", help="排序字段")
    parser.add_argument("--direction", choices=["asc", "desc"], default="desc", help="排序方向（默认 desc）")
    parser.add_argument("--page", type=int, default=1, help="页码（默认 1）")
    parser.add_argument("--per-page", type=int, default=20, help="每页数量（默认 20）")
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

        if args.overview:
            from_date, to_date = resolve_time_range(args.range)
            indicators = args.indicators.split(",") if args.indicators else None
            result = query_overview(data_source_id, from_date, to_date, indicators=indicators)
            output = build_overview_table(result, indicators)

        elif args.total_user:
            from_date, to_date = resolve_time_range(args.range)
            result = query_total_user(data_source_id, from_date, to_date)
            output = build_total_user_table(result)

        elif args.retention:
            # 留存查询支持自定义日期范围或预设范围
            if args.from_date and args.to_date:
                from_date = parse_date(args.from_date)
                to_date = parse_date(args.to_date)
            else:
                # 默认使用 last_7_days（昨日留存可能无数据）
                range_name = args.range if args.range != "yesterday" else "last_7_days"
                from_date, to_date = resolve_time_range(range_name)
            result = query_retention(data_source_id, from_date, to_date,
                                    time_unit=args.time_unit, value_type=args.value_type, indicator=args.indicator)
            output = build_retention_table(result, args.indicator, args.time_unit)

        elif args.visit_pages:
            from_date, to_date = resolve_time_range(args.range)
            result = query_visit_pages(data_source_id, from_date, to_date,
                                       order_by=args.order_by, direction=args.direction,
                                       page_index=args.page, page_size=args.per_page)
            output = build_page_table(result, "受访页面", is_visit=True)

        elif args.landing_pages:
            from_date, to_date = resolve_time_range(args.range)
            result = query_landing_pages(data_source_id, from_date, to_date,
                                         order_by=args.order_by, direction=args.direction,
                                         page_index=args.page, page_size=args.per_page)
            output = build_page_table(result, "入口页面", is_visit=False)

        elif args.share_overview:
            from_date, to_date = resolve_time_range(args.range)
            result = query_share_overview(data_source_id, from_date, to_date)
            output = build_share_overview_table(result)

        elif args.share_pages:
            from_date, to_date = resolve_time_range(args.range)
            result = query_share_pages(data_source_id, from_date, to_date,
                                       order_by=args.order_by, direction=args.direction,
                                       page_index=args.page, page_size=args.per_page)
            output = build_share_pages_table(result)

        elif args.share_users:
            from_date, to_date = resolve_time_range(args.range)
            result = query_share_users(data_source_id, from_date, to_date,
                                       order_by=args.order_by, direction=args.direction,
                                       page_index=args.page, page_size=args.per_page)
            output = build_share_users_table(result)

        elif args.list_scenes:
            result = query_scene_list(data_source_id, args.source_type)
            output = build_scene_list_table(result, args.source_type)

        elif args.list_scenes_wx:
            output = build_wx_scene_list_table()

        elif args.scene_stats:
            from_date, to_date = resolve_time_range(args.range)
            indicators = ["activeUser", "newUser", "visitTimes"]
            result = query_scene_stats(data_source_id, args.scene_stats,
                                       from_date, to_date, indicators=indicators)
            output = build_scene_stats_table(result, args.scene_stats)

        elif args.list_events:
            result = query_event_list(data_source_id)
            output = build_event_list_table(result)

        elif args.event_stats:
            from_date, to_date = resolve_time_range(args.range)
            result = query_event_overview(data_source_id, args.event_stats, from_date, to_date)
            output = build_event_stats_table(result, args.event_stats)

        elif args.list_props:
            result = query_event_props(data_source_id, args.list_props)
            output = build_event_props_table(result, args.list_props)

        elif args.prop_values:
            if not args.prop:
                raise ValueError("--prop-values 需要配合 --prop 参数指定属性名称")
            from_date, to_date = resolve_time_range(args.range)
            result = query_prop_values(data_source_id, args.prop_values, args.prop,
                                       from_date, to_date, page_index=args.page, page_size=args.per_page)
            output = build_prop_values_table(result, args.prop_values, args.prop)

        # 输出结果
        if args.json:
            print(build_json_output(result))
        else:
            print(output)

    except Exception as e:
        if args.json:
            print(build_error_json(str(e)))
        else:
            print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
