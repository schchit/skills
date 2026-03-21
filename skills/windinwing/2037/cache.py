#!/usr/bin/env python3
"""
Earth2037 本地缓存：拉取 userinfo、citys 等数据到本地 JSON，便于映射（主城 tileID、城市名等）。
需 token 认证。执行 2037.py sync 触发同步。
"""

import json
import os
import re
import sys

# 与 2037.py 共用 config
def _load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")
    api_base = "https://2037cn1.9235.net"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                api_base = cfg.get("apiBase", api_base)
        except (json.JSONDecodeError, IOError):
            pass
    return api_base.rstrip("/")


def _get_token():
    """从环境变量或 config 获取 token"""
    token = os.environ.get("EARTH2037_TOKEN", "").strip()
    if token:
        return token
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return (cfg.get("token") or cfg.get("apiKey") or "").strip()
        except (json.JSONDecodeError, IOError):
            pass
    return ""


def _game_command(api_base, token, cmd, args=""):
    """POST /game/command，返回 data 字符串（如 /svr citylist {...}）"""
    import urllib.request
    import urllib.error
    url = f"{api_base}/game/command"
    body = json.dumps({"cmd": cmd, "args": args or ""}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        r = json.loads(resp.read().decode("utf-8"))
    if not r.get("ok"):
        raise RuntimeError(r.get("err", "unknown error"))
    return r.get("data") or ""


def _parse_svr_json(data, prefix):
    """从 /svr cmd {json} 或 /svr cmd json 提取 JSON 字符串"""
    if not data or not isinstance(data, str):
        return None
    # 格式: /svr citylist [{...}] 或 /svr userinfo {...}
    pat = re.compile(r"^/svr\s+" + re.escape(prefix) + r"\s+(.+)$", re.IGNORECASE)
    m = pat.match(data.strip())
    if not m:
        return None
    raw = m.group(1).strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _cache_dir():
    """缓存文件所在目录（skill 根目录）"""
    return os.path.dirname(os.path.abspath(__file__))


def sync(api_base=None, token=None):
    """
    拉取 CURRENTUSER、USERINFO、CITYLIST，写入 userinfo.json、citys.json。
    返回 (userinfo, citys) 或抛出异常。
    """
    api_base = api_base or _load_config()
    token = token or _get_token()
    if not token:
        raise ValueError("需要 token：设置环境变量 EARTH2037_TOKEN 或在 config.json 中配置 token/apiKey")

    # 1. USERINFO（当前用户详情，含 CapitalID）
    raw_user = _game_command(api_base, token, "USERINFO", "")
    userinfo = _parse_svr_json(raw_user, "userinfo")
    if userinfo is None:
        raise RuntimeError("USERINFO 解析失败: " + (raw_user[:200] if raw_user else "无返回"))

    # 2. CITYLIST（城市列表）
    raw_city = _game_command(api_base, token, "CITYLIST", "")
    citys = _parse_svr_json(raw_city, "citylist")
    if citys is None:
        citys = []  # 可能为空数组
    if not isinstance(citys, list):
        citys = [citys] if citys else []

    # 写入本地
    cache_dir = _cache_dir()
    userinfo_path = os.path.join(cache_dir, "userinfo.json")
    citys_path = os.path.join(cache_dir, "citys.json")

    with open(userinfo_path, "w", encoding="utf-8") as f:
        json.dump(userinfo, f, ensure_ascii=False, indent=2)

    with open(citys_path, "w", encoding="utf-8") as f:
        json.dump(citys, f, ensure_ascii=False, indent=2)

    return userinfo, citys


def load_userinfo():
    """读取本地 userinfo.json"""
    path = os.path.join(_cache_dir(), "userinfo.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_citys():
    """读取本地 citys.json"""
    path = os.path.join(_cache_dir(), "citys.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data if isinstance(data, list) else []


def get_capital_id():
    """主城 tileID，无缓存时返回 None"""
    u = load_userinfo()
    if not u:
        return None
    return u.get("CapitalID") or u.get("capitalID")


def get_tile_by_name(name):
    """按城市名查 tileID，支持「主城」「第一座城」等"""
    citys = load_citys()
    if not citys:
        return get_capital_id() if name in ("主城", "首都", "第一座城") else None
    name = (name or "").strip()
    if name in ("主城", "首都", "第一座城"):
        for c in citys:
            if c.get("IsCapital") or c.get("isCapital"):
                return c.get("TileID") or c.get("tileID")
        return get_capital_id() or (citys[0].get("TileID") if citys else None)
    for c in citys:
        if (c.get("Name") or c.get("name") or "") == name:
            return c.get("TileID") or c.get("tileID")
    return None


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sync":
        try:
            ui, cs = sync()
            print("✅ 缓存已更新")
            print(f"  userinfo.json: userID={ui.get('UserID')}, CapitalID={ui.get('CapitalID')}")
            print(f"  citys.json: {len(cs)} 座城市")
        except Exception as e:
            print(f"❌ 同步失败: {e}")
            sys.exit(1)
    else:
        print("用法: python3 cache.py sync")
        print("  需配置 token (EARTH2037_TOKEN 或 config.json)")
