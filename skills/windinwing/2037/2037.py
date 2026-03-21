#!/usr/bin/env python3
"""
Earth2037 Game Skill - 命令行入口
调用 GameSkillAPI 完成 key、注册、登录、apply 等操作。
使用标准库 urllib，无需 pip install。
"""

import json
import os
import sys
import urllib.error
import urllib.request


def load_config(api_base_override=None, lang=None):
    """从 env、config.json 或 apiBaseByLang 读取 apiBase。优先级：api_base_override > EARTH2037_API_BASE > apiBaseByLang[lang] > apiBase"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")
    api_base = "https://2037cn1.9235.net"
    api_base_by_lang = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                api_base = cfg.get("apiBase", api_base)
                api_base_by_lang = cfg.get("apiBaseByLang") or {}
        except (json.JSONDecodeError, IOError):
            pass

    if api_base_override:
        return api_base_override.rstrip("/")
    env_base = os.environ.get("EARTH2037_API_BASE", "").strip()
    if env_base:
        return env_base.rstrip("/")
    if lang and api_base_by_lang.get(lang):
        return api_base_by_lang[lang].rstrip("/")
    return api_base.rstrip("/")


def http_get(url):
    """GET 请求"""
    req = urllib.request.Request(url, method="GET")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_post(url, data):
    """POST JSON 请求"""
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def cmd_key(api_base):
    """GET /auth/key?skill_id=2037"""
    url = f"{api_base}/auth/key?skill_id=2037"
    try:
        r = http_get(url)
        if r.get("ok") and r.get("key"):
            print(json.dumps(r, ensure_ascii=False, indent=2))
            print(f"\n✅ key 已获取，长期有效。请保存后用于注册/绑定。")
        else:
            print(json.dumps(r, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        sys.exit(1)


def _parse_tribe_id(t):
    """解析 tribe_id：1|2|3 或 人类联邦|旭日帝国|鹰之神界"""
    if t is None or t == "":
        return 1
    m = {"1": 1, "2": 2, "3": 3, "人类联邦": 1, "旭日帝国": 2, "鹰之神界": 3}
    return m.get(str(t).strip(), int(t) if str(t).isdigit() else 1)


def cmd_register(api_base, username, password, tribe_id=None):
    """POST /auth/register"""
    url = f"{api_base}/auth/register"
    tid = _parse_tribe_id(tribe_id)
    try:
        r = http_post(url, {"username": username, "password": password, "tribe_id": tid})
        if r.get("ok") and r.get("token"):
            print(json.dumps(r, ensure_ascii=False, indent=2))
            print(f"\n✅ 注册成功。请将 token 填入 OpenClaw 的 2037 API Key 配置。")
        else:
            print(json.dumps(r, ensure_ascii=False))
            sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        sys.exit(1)


def cmd_login(api_base, username, password):
    """POST /auth/token"""
    url = f"{api_base}/auth/token"
    try:
        r = http_post(url, {"username": username, "password": password})
        if r.get("ok") and r.get("token"):
            print(json.dumps(r, ensure_ascii=False, indent=2))
            print(f"\n✅ 登录成功。请将 token 填入 OpenClaw 的 2037 API Key 配置。")
        else:
            print(json.dumps(r, ensure_ascii=False))
            sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        sys.exit(1)


def cmd_apply(api_base, username, password, key, action="register", tribe_id=None):
    """POST /auth/apply"""
    url = f"{api_base}/auth/apply"
    tid = _parse_tribe_id(tribe_id)
    try:
        r = http_post(
            url,
            {
                "username": username,
                "password": password,
                "action": action,
                "key": key,
                "skill_id": "2037",
                "tribe_id": tid,
            },
        )
        if r.get("ok") and r.get("token"):
            print(json.dumps(r, ensure_ascii=False, indent=2))
            print(f"\n✅ 成功。请将 token 填入 OpenClaw 的 2037 API Key 配置。")
        else:
            print(json.dumps(r, ensure_ascii=False))
            sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        sys.exit(1)


def _get_token():
    """从环境变量或 config.json 读取 token"""
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


def cmd_newkey(api_base):
    """POST /auth/newkey - 需 Bearer token，生成新 token 并作废旧 token"""
    token = _get_token()
    if not token:
        print("❌ 未找到 token，请先设置 EARTH2037_TOKEN 或 config.json 中的 token/apiKey")
        sys.exit(1)
    url = f"{api_base}/auth/newkey"
    body = json.dumps({"skill_id": "2037"}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            r = json.loads(resp.read().decode("utf-8"))
        if r.get("ok") and r.get("token"):
            print(json.dumps(r, ensure_ascii=False, indent=2))
            print(f"\n✅ 新 key 已生成，旧 key 已作废。请将新 token 更新到 OpenClaw 的 2037 API Key 配置。")
        else:
            print(json.dumps(r, ensure_ascii=False))
            sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        sys.exit(1)


def cmd_sync(api_base):
    """同步 userinfo、citys 到本地缓存"""
    try:
        from cache import sync as cache_sync
        ui, cs = cache_sync(api_base=api_base)
        print("✅ 缓存已更新")
        print(f"  userinfo.json: userID={ui.get('UserID')}, CapitalID={ui.get('CapitalID')}")
        print(f"  citys.json: {len(cs)} 座城市")
    except Exception as e:
        print(f"❌ 同步失败: {e}")
        sys.exit(1)


def main():
    args = sys.argv[1:]
    api_base_override = None
    lang = None
    while args and args[0].startswith("--"):
        if args[0] == "--api-base" and len(args) > 1:
            api_base_override = args[1]
            args = args[2:]
        elif args[0] == "--lang" and len(args) > 1:
            lang = args[1].lower()
            args = args[2:]
        else:
            args = args[1:]

    if len(args) < 1:
        print("用法: 2037.py [--api-base URL] [--lang zh|en] key | newkey | register ... | login ... | apply ... | sync")
        print("  --api-base: 指定 API 地址，覆盖 config.json")
        print("  --lang zh|en: 按语言选默认服务器（需 config.json 中 apiBaseByLang）")
        print("  tribe_id: 1=人类联邦 2=旭日帝国 3=鹰之神界，默认1")
        print("  newkey: 换新 key（需 token，旧 key 作废）")
        print("  sync: 拉取 userinfo、citys 到本地 userinfo.json、citys.json（需 token）")
        sys.exit(1)

    api_base = load_config(api_base_override=api_base_override, lang=lang)
    cmd = args[0].lower()

    if cmd == "sync":
        cmd_sync(api_base)
    elif cmd == "newkey":
        cmd_newkey(api_base)
    elif cmd == "key":
        cmd_key(api_base)
    elif cmd == "register":
        if len(args) < 4:
            print("用法: 2037.py register <用户名> <密码> [tribe_id]")
            sys.exit(1)
        tribe_id = args[4] if len(args) > 4 else None
        cmd_register(api_base, args[2], args[3], tribe_id)
    elif cmd == "login":
        if len(args) < 4:
            print("用法: 2037.py login <用户名> <密码>")
            sys.exit(1)
        cmd_login(api_base, args[2], args[3])
    elif cmd == "apply":
        if len(args) < 5:
            print("用法: 2037.py apply <用户名> <密码> <key> [tribe_id]")
            sys.exit(1)
        tribe_id = args[5] if len(args) > 5 else None
        cmd_apply(api_base, args[2], args[3], args[4], tribe_id=tribe_id)
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
