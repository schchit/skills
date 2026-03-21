#!/usr/bin/env python3
"""
基金查询脚本 - 通过基金代码查询基金名称和最新净值信息
数据源：天天基金 API
支持收藏和分组管理功能
"""

import json
import random
import time
import re
import sys
import os
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# 收藏数据文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
FAVORITES_FILE = os.path.join(DATA_DIR, 'favorites.json')
GROUPS_FILE = os.path.join(DATA_DIR, 'groups.json')


def ensure_data_dir():
    """确保数据目录存在"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def parse_number(value):
    """安全解析数字"""
    if value is None or value == "":
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def get_fund_info(fund_code):
    """
    获取基金实时净值信息
    
    Args:
        fund_code: 基金代码 (6 位数字)
    
    Returns:
        dict: 包含基金信息的字典，失败时返回 error 状态
    """
    # 验证基金代码格式
    if not re.match(r'^\d{6}$', str(fund_code)):
        return {
            "fund_code": fund_code,
            "status": "error",
            "message": "基金代码格式错误，应为 6 位数字"
        }
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]
    
    url = f"https://fundgz.1234567.com.cn/js/{fund_code}.js"
    
    try:
        # 随机延迟，避免请求过快
        time.sleep(random.uniform(0.5, 1.5))
        
        req = Request(
            url,
            headers={
                "User-Agent": random.choice(user_agents),
                "Referer": "http://fund.eastmoney.com/",
                "Accept": "*/*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
        )
        
        with urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8')
        
        # 解析 JSONP 格式：jsonpgz({...});
        if "(" not in content or ")" not in content:
            return {
                "fund_code": fund_code,
                "status": "error",
                "message": "基金返回数据格式异常"
            }
        
        # 提取 JSON 内容
        json_str = content[content.find("(") + 1:content.rfind(")")]
        data = json.loads(json_str)
        
        # 提取关键字段
        fund_name = data.get("name", "未知")
        gsz = parse_number(data.get("gsz", 0))  # 估算净值
        gszzl = parse_number(data.get("gszzl", 0))  # 估算涨跌幅
        dwjz = parse_number(data.get("dwjz", 0))  # 单位净值
        jzrq = data.get("jzrq", "")  # 净值日期
        gztime = data.get("gztime", "")  # 估值时间
        
        # 判断涨跌趋势
        if gszzl > 0:
            trend = "上涨"
        elif gszzl < 0:
            trend = "下跌"
        else:
            trend = "持平"
        
        return {
            "fund_code": fund_code,
            "fund_name": fund_name,
            "estimated_net_value": gsz,
            "unit_net_value": dwjz,
            "growth_rate": gszzl,
            "trend": trend,
            "net_value_date": jzrq,
            "valuation_time": gztime,
            "status": "success"
        }
        
    except HTTPError as e:
        return {
            "fund_code": fund_code,
            "status": "error",
            "message": f"HTTP 错误：{e.code}"
        }
    except URLError as e:
        return {
            "fund_code": fund_code,
            "status": "error",
            "message": f"网络错误：{e.reason}"
        }
    except json.JSONDecodeError as e:
        return {
            "fund_code": fund_code,
            "status": "error",
            "message": f"数据解析错误：{e}"
        }
    except Exception as e:
        return {
            "fund_code": fund_code,
            "status": "error",
            "message": f"未知错误：{e}"
        }


# ============== 分组管理功能 ==============

def load_groups():
    """加载分组列表"""
    ensure_data_dir()
    if not os.path.exists(GROUPS_FILE):
        return {}
    try:
        with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_groups(groups):
    """保存分组列表"""
    ensure_data_dir()
    with open(GROUPS_FILE, 'w', encoding='utf-8') as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)


def create_group(group_name):
    """
    创建新分组
    
    Args:
        group_name: 分组名称
    
    Returns:
        dict: 操作结果
    """
    groups = load_groups()
    
    if group_name in groups:
        return {
            "status": "exists",
            "message": f"分组 '{group_name}' 已存在"
        }
    
    groups[group_name] = {
        "created_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "description": ""
    }
    
    save_groups(groups)
    
    return {
        "status": "success",
        "message": f"已创建分组 '{group_name}'"
    }


def delete_group(group_name):
    """
    删除分组（不删除基金）
    
    Args:
        group_name: 分组名称
    
    Returns:
        dict: 操作结果
    """
    groups = load_groups()
    
    if group_name not in groups:
        return {
            "status": "not_found",
            "message": f"分组 '{group_name}' 不存在"
        }
    
    del groups[group_name]
    save_groups(groups)
    
    # 同时从所有基金中移除该分组
    favorites = load_favorites()
    for fav in favorites:
        if group_name in fav.get("groups", []):
            fav["groups"].remove(group_name)
    save_favorites(favorites)
    
    return {
        "status": "success",
        "message": f"已删除分组 '{group_name}'"
    }


def list_groups():
    """
    获取所有分组
    
    Returns:
        dict: 分组列表
    """
    return load_groups()


# ============== 收藏管理功能 ==============

def load_favorites():
    """加载收藏列表"""
    ensure_data_dir()
    if not os.path.exists(FAVORITES_FILE):
        return []
    try:
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_favorites(favorites):
    """保存收藏列表"""
    ensure_data_dir()
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)


def add_favorite(fund_code, groups=None, fund_name=None):
    """
    添加基金到收藏
    
    Args:
        fund_code: 基金代码
        groups: 分组列表（可选）
        fund_name: 基金名称（可选，如不提供会自动查询）
    
    Returns:
        dict: 操作结果
    """
    favorites = load_favorites()
    
    # 检查是否已存在
    existing = None
    for fav in favorites:
        if fav.get("fund_code") == fund_code:
            existing = fav
            break
    
    # 如果未提供名称，尝试查询
    if not fund_name:
        info = get_fund_info(fund_code)
        if info.get("status") != "success":
            return {
                "status": "error",
                "message": f"查询基金信息失败：{info.get('message', '未知错误')}"
            }
        fund_name = info.get("fund_name", "未知")
    
    if groups is None:
        groups = []
    
    if existing:
        # 已存在，合并分组
        existing_groups = existing.get("groups", [])
        new_groups = list(set(existing_groups + groups))
        existing["groups"] = new_groups
        existing["updated_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        save_favorites(favorites)
        
        return {
            "status": "updated",
            "message": f"已更新 {fund_name}({fund_code}) 的分组：{', '.join(new_groups) if new_groups else '无分组'}"
        }
    else:
        # 添加到收藏
        favorites.append({
            "fund_code": fund_code,
            "fund_name": fund_name,
            "groups": groups,
            "added_time": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        save_favorites(favorites)
        
        return {
            "status": "success",
            "message": f"已添加 {fund_name}({fund_code}) 到收藏，分组：{', '.join(groups) if groups else '无分组'}"
        }


def remove_favorite(fund_code):
    """
    从收藏中移除基金
    
    Args:
        fund_code: 基金代码
    
    Returns:
        dict: 操作结果
    """
    favorites = load_favorites()
    
    for i, fav in enumerate(favorites):
        if fav.get("fund_code") == fund_code:
            removed = favorites.pop(i)
            save_favorites(favorites)
            groups = removed.get("groups", [])
            return {
                "status": "success",
                "message": f"已移除 {removed.get('fund_name', fund_code)}({fund_code})，原分组：{', '.join(groups) if groups else '无分组'}"
            }
    
    return {
        "status": "not_found",
        "message": f"收藏列表中未找到基金 {fund_code}"
    }


def update_fund_groups(fund_code, groups):
    """
    更新基金的分组
    
    Args:
        fund_code: 基金代码
        groups: 新的分组列表
    
    Returns:
        dict: 操作结果
    """
    favorites = load_favorites()
    
    for fav in favorites:
        if fav.get("fund_code") == fund_code:
            fav["groups"] = groups
            fav["updated_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
            save_favorites(favorites)
            return {
                "status": "success",
                "message": f"已更新 {fav['fund_name']}({fund_code}) 的分组：{', '.join(groups) if groups else '无分组'}"
            }
    
    return {
        "status": "not_found",
        "message": f"收藏列表中未找到基金 {fund_code}"
    }


def list_favorites(group=None):
    """
    获取收藏列表
    
    Args:
        group: 分组名称（可选，为 None 时返回全部）
    
    Returns:
        list: 收藏的基金列表
    """
    favorites = load_favorites()
    
    if group is None:
        # 返回全部（包括无分组的）
        return favorites
    elif group == "":
        # 返回无分组的
        return [f for f in favorites if not f.get("groups", [])]
    else:
        # 返回指定分组的（包括无分组的）
        return [f for f in favorites if group in f.get("groups", []) or not f.get("groups", [])]


def refresh_favorites(group=None):
    """
    刷新收藏的基金信息
    
    Args:
        group: 分组名称（可选，为 None 时刷新全部）
    
    Returns:
        list: 刷新后的基金信息列表
    """
    favorites = list_favorites(group)
    results = []
    
    for fav in favorites:
        fund_code = fav.get("fund_code")
        info = get_fund_info(fund_code)
        
        if info.get("status") == "success":
            # 保留收藏信息
            info["groups"] = fav.get("groups", [])
            info["added_time"] = fav.get("added_time", "")
            info["is_favorite"] = True
            results.append(info)
        else:
            # 查询失败，保留旧信息并标记错误
            results.append({
                "fund_code": fund_code,
                "fund_name": fav.get("fund_name", "未知"),
                "groups": fav.get("groups", []),
                "status": "error",
                "message": info.get("message", "刷新失败"),
                "is_favorite": True
            })
        
        # 避免请求过快
        time.sleep(0.3)
    
    return results


# ============== 格式化输出 ==============

def format_result(result):
    """格式化单个基金查询结果"""
    if result.get("status") != "success":
        return f"❌ 查询失败：{result.get('message', '未知错误')}"
    
    output = []
    output.append(f"📊 基金查询结果")
    output.append(f"━━━━━━━━━━━━━━")
    output.append(f"基金代码：{result['fund_code']}")
    output.append(f"基金名称：{result['fund_name']}")
    output.append(f"单位净值：{result['unit_net_value']}")
    output.append(f"估算净值：{result['estimated_net_value']}")
    output.append(f"涨跌幅度：{result['growth_rate']:+.2f}% ({result['trend']})")
    output.append(f"净值日期：{result['net_value_date']}")
    output.append(f"估值时间：{result['valuation_time']}")
    
    return "\n".join(output)


def format_groups_list(groups):
    """格式化分组列表"""
    if not groups:
        return "📭 暂无分组"
    
    output = []
    output.append(f"📁 我的分组 ({len(groups)}个)")
    output.append(f"━━━━━━━━━━━━━━")
    
    for name, info in groups.items():
        created = info.get("created_time", "")
        output.append(f"• {name}")
        if created:
            output[-1] += f" (创建于：{created})"
    
    return "\n".join(output)


def format_favorites_list(favorites, group=None):
    """格式化收藏列表"""
    if not favorites:
        if group:
            return f"📭 分组 '{group}' 中没有基金"
        return "📭 收藏列表为空"
    
    output = []
    if group:
        output.append(f"⭐ 分组 '{group}' 的基金 ({len(favorites)}只)")
    else:
        output.append(f"⭐ 我的基金收藏 ({len(favorites)}只)")
    output.append(f"━━━━━━━━━━━━━━")
    
    for fav in favorites:
        code = fav.get("fund_code", "未知")
        name = fav.get("fund_name", "未知")
        added = fav.get("added_time", "")
        groups = fav.get("groups", [])
        
        line = f"• {code} - {name}"
        if groups:
            line += f" [{', '.join(groups)}]"
        else:
            line += " [无分组]"
        if added:
            line += f" (收藏于：{added})"
        output.append(line)
    
    return "\n".join(output)


def format_refresh_results(results, group=None):
    """格式化刷新结果"""
    if not results:
        if group:
            return f"📭 分组 '{group}' 中没有基金，无需刷新"
        return "📭 收藏列表为空，无需刷新"
    
    output = []
    if group:
        output.append(f"🔄 分组 '{group}' 刷新结果 ({len(results)}只)")
    else:
        output.append(f"🔄 收藏基金刷新结果 ({len(results)}只)")
    output.append(f"━━━━━━━━━━━━━━")
    
    success_count = 0
    error_count = 0
    
    for r in results:
        if r.get("status") == "success":
            success_count += 1
            trend_icon = "📈" if r.get("growth_rate", 0) > 0 else "📉" if r.get("growth_rate", 0) < 0 else "➖"
            groups_str = f" [{', '.join(r.get('groups', []))}]" if r.get('groups') else " [无分组]"
            output.append(f"{trend_icon} {r['fund_code']} {r['fund_name']}{groups_str}")
            output.append(f"   净值：{r['unit_net_value']} | 涨跌：{r['growth_rate']:+.2f}%")
        else:
            error_count += 1
            output.append(f"❌ {r['fund_code']} - {r.get('message', '刷新失败')}")
    
    output.append(f"━━━━━━━━━━━━━━")
    output.append(f"成功：{success_count} | 失败：{error_count}")
    
    return "\n".join(output)


# ============== 主函数 ==============

def print_usage():
    """打印使用说明"""
    print("""
基金查询工具 - 支持收藏和分组管理

用法:
  查询:
    python fund_query.py <基金代码>              查询单只基金
    python fund_query.py query <基金代码>        查询单只基金
    python fund_query.py <基金代码> --add        查询并添加到收藏

  收藏管理:
    python fund_query.py add <基金代码> [分组...]  添加基金到收藏（可指定多个分组）
    python fund_query.py remove <基金代码>       从收藏移除
    python fund_query.py list [分组名]           显示收藏列表（可按分组筛选）
    python fund_query.py refresh [分组名]        刷新收藏（可按分组筛选）
    python fund_query.py groups <基金代码> <分组...>  更新基金的分组

  分组管理:
    python fund_query.py group create <名称>     创建分组
    python fund_query.py group delete <名称>     删除分组
    python fund_query.py group list              列出所有分组

示例:
  python fund_query.py 161725                    查询招商中证白酒
  python fund_query.py add 161725 白酒 重仓      添加到"白酒"和"重仓"分组
  python fund_query.py list 白酒                 查看"白酒"分组的基金
  python fund_query.py refresh 白酒              刷新"白酒"分组
  python fund_query.py group create 科技         创建"科技"分组
  python fund_query.py group list                列出所有分组
""")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    args = sys.argv[1:]
    command = None
    fund_code = None
    add_flag = False
    groups = []
    
    # 处理 --add 标志
    if len(args) >= 2 and args[1] == "--add":
        command = "query"
        fund_code = args[0]
        add_flag = True
    # 纯数字参数 = 查询
    elif args[0].isdigit() and len(args[0]) == 6:
        command = "query"
        fund_code = args[0]
        add_flag = False
    # 命令 + 参数
    elif args[0] in ["query", "q", "add", "remove", "list", "refresh", "group", "groups"]:
        command = args[0]
    # 未知命令
    else:
        print(f"❌ 未知命令：{args[0]}")
        print_usage()
        sys.exit(1)
    
    # 执行命令
    if command in ["query", "q"]:
        if not fund_code:
            fund_code = args[1] if len(args) > 1 else None
        if not fund_code:
            print("❌ 请提供基金代码")
            sys.exit(1)
        result = get_fund_info(fund_code)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()
        print(format_result(result))
        
        # 如果需要添加到收藏
        if add_flag and result.get("status") == "success":
            add_result = add_favorite(fund_code, [], result.get("fund_name"))
            print()
            print(add_result.get("message", ""))
    
    elif command == "add":
        if len(args) < 2:
            print("❌ 请提供基金代码")
            print_usage()
            sys.exit(1)
        fund_code = args[1]
        groups = args[2:] if len(args) > 2 else []
        result = add_favorite(fund_code, groups)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()
        print(result.get("message", ""))
    
    elif command == "remove":
        if len(args) < 2:
            print("❌ 请提供基金代码")
            sys.exit(1)
        fund_code = args[1]
        result = remove_favorite(fund_code)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()
        print(result.get("message", ""))
    
    elif command == "list":
        group = args[1] if len(args) > 1 else None
        favorites = list_favorites(group)
        print(json.dumps(favorites, ensure_ascii=False, indent=2))
        print()
        print(format_favorites_list(favorites, group))
    
    elif command == "refresh":
        group = args[1] if len(args) > 1 else None
        results = refresh_favorites(group)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        print()
        print(format_refresh_results(results, group))
    
    elif command == "groups":
        if len(args) < 2:
            print("❌ 请提供基金代码")
            sys.exit(1)
        fund_code = args[1]
        groups = args[2:] if len(args) > 2 else []
        result = update_fund_groups(fund_code, groups)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()
        print(result.get("message", ""))
    
    elif command == "group":
        if len(args) < 2:
            print("❌ 请提供子命令 (create/delete/list)")
            sys.exit(1)
        
        subcommand = args[1]
        
        if subcommand == "create":
            if len(args) < 3:
                print("❌ 请提供分组名称")
                sys.exit(1)
            group_name = args[2]
            result = create_group(group_name)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print()
            print(result.get("message", ""))
        
        elif subcommand == "delete":
            if len(args) < 3:
                print("❌ 请提供分组名称")
                sys.exit(1)
            group_name = args[2]
            result = delete_group(group_name)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print()
            print(result.get("message", ""))
        
        elif subcommand == "list":
            groups = list_groups()
            print(json.dumps(groups, ensure_ascii=False, indent=2))
            print()
            print(format_groups_list(groups))
        
        else:
            print(f"❌ 未知子命令：{subcommand}")
            print("可用子命令：create, delete, list")
            sys.exit(1)
    
    else:
        print(f"❌ 未知命令：{command}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
