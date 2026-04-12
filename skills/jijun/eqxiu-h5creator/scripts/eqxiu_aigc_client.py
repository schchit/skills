#!/usr/bin/env python3
"""
易企秀 eqxiu-h5-creator 对外 AIGC HTTP API 的轻量客户端。

依赖：requests（与项目 requirements.txt 一致）
环境变量：EQXIU_AIGC_API_BASE（默认 https://ai-api.eqxiu.com）
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests

DEFAULT_BASE_URL = os.environ.get("EQXIU_AIGC_API_BASE", "https://ai-api.eqxiu.com").rstrip("/")
CONFIG_DIR = Path.home() / ".eqxiu"
CONFIG_PATH = CONFIG_DIR / "config.json"
CONFIG_TOKEN_KEY = "X-Openclaw-Token"
PASSPORT_PROFILE_URL = "https://passport.eqxiu.com/user/profile"


def _load_config() -> dict[str, Any]:
    if not CONFIG_PATH.is_file():
        return {}
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_config(data: dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        CONFIG_PATH.chmod(0o600)
    except OSError:
        pass


def _token_from_config(cfg: dict[str, Any]) -> str:
    v = cfg.get(CONFIG_TOKEN_KEY) or cfg.get("x_openclaw_token")
    return (v if isinstance(v, str) else str(v or "")).strip()


def _check_auth_status(access_token: str, timeout: float) -> dict[str, Any]:
    headers = {CONFIG_TOKEN_KEY: access_token}
    r = requests.get(PASSPORT_PROFILE_URL, headers=headers, timeout=timeout)
    if r.status_code != 200:
        return {"success": False, "code": 1002, "msg":"认证失败"}
    return {"success": True, "code": 200, "msg":"认证成功"}


def _login_interactive() -> int:
    cfg = _load_config()
    print("交互式登录：令牌输入时不会回显。", file=sys.stderr)
    token = getpass.getpass("X-Openclaw-Token: ").strip()
    if not token:
        print("未输入令牌，已取消。", file=sys.stderr)
        return 1
    cfg[CONFIG_TOKEN_KEY] = token
    _save_config(cfg)
    print(f"已保存至 {CONFIG_PATH}（{CONFIG_TOKEN_KEY}）。", file=sys.stderr)
    return 0


class EqxiuAigcApiError(Exception):
    """服务端返回 success=false 或非预期响应时抛出。"""

    def __init__(self, message: str, *, status_code: Optional[int] = None, raw: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.raw = raw


class EqxiuAigcClient:
    """调用 /iaigc/* 接口。注意：outline 与 scene-tpl 可能耗时数分钟，默认 timeout 较大。"""

    def __init__(
        self, base_url: str = DEFAULT_BASE_URL, timeout: float = 900.0, access_token: Optional[str] = None
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        if access_token:
            self._session.headers.update({CONFIG_TOKEN_KEY: access_token})

    def _unwrap(self, resp: requests.Response) -> Any:
        try:
            payload = resp.json()
        except json.JSONDecodeError as e:
            raise EqxiuAigcApiError(
                f"无效 JSON 响应: {e}", status_code=resp.status_code, raw=resp.text
            ) from e
        if not isinstance(payload, dict):
            raise EqxiuAigcApiError("响应不是 JSON 对象", status_code=resp.status_code, raw=payload)
        if payload.get("success") is False:
            raise EqxiuAigcApiError(
                str(payload.get("msg", "请求失败")),
                status_code=resp.status_code if resp.status_code >= 400 else payload.get("code"),
                raw=payload,
            )
        if "data" in payload:
            return payload["data"]
        return payload

    def list_categories(self) -> List[Dict[str, Any]]:
        r = self._session.get(f"{self.base_url}/iaigc/category", timeout=self.timeout)
        r.raise_for_status()
        return self._unwrap(r)

    def list_styles(
        self, two_level_category_id: int, three_level_category_id: int
    ) -> Dict[str, Any]:
        r = self._session.get(
            f"{self.base_url}/iaigc/style",
            params={
                "twoLevelCategoryId": two_level_category_id,
                "threeLevelCategoryIds": three_level_category_id,
            },
            timeout=self.timeout,
        )
        r.raise_for_status()
        return self._unwrap(r)

    def create_outline(self, scene_fields: List[Dict[str, Any]], category_id: int) -> Dict[str, Any]:
        r = self._session.post(
            f"{self.base_url}/iaigc/outline",
            json={"sceneFields": scene_fields, "categoryId": category_id},
            timeout=self.timeout,
        )
        r.raise_for_status()
        data = self._unwrap(r)
        if not isinstance(data, dict):
            raise EqxiuAigcApiError("outline 返回的 data 不是对象", raw=data)
        return data

    def create_scene_tpl(
        self,
        scene_fields: List[Dict[str, Any]],
        scene_id: int,
        title: str,
        outline_task_id: Union[int, str],
        outline: Any,
        image_id: Any = None,
        style_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "sceneFields": scene_fields,
            "sceneId": scene_id,
            "title": title,
            "outlineTaskId": outline_task_id,
            "outline": outline,
        }
        if image_id is not None:
            body["imageId"] = image_id
        if style_id is not None:
            body["styleId"] = style_id
        r = self._session.post(f"{self.base_url}/iaigc/scene-tpl", json=body, timeout=self.timeout)
        r.raise_for_status()
        data = self._unwrap(r)
        if not isinstance(data, dict):
            raise EqxiuAigcApiError("scene-tpl 返回的 data 不是对象", raw=data)
        return data

    def run_pipeline(
        self,
        scene_fields: List[Dict[str, Any]],
        category_id: int,
        title: str,
        *,
        style_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        按正确顺序：先 outline，再 scene-tpl（复用同一份 sceneFields 与 category_id 作为 sceneId）。
        """
        outline_result = self.create_outline(scene_fields, category_id)
        tpl_result = self.create_scene_tpl(
            scene_fields=scene_fields,
            scene_id=category_id,
            title=title,
            outline_task_id=outline_result["outlineTaskId"],
            outline=outline_result["outline"],
            image_id=outline_result.get("imageId"),
            style_id=style_id,
        )
        return {"outline": outline_result, "scene_tpl": tpl_result}


def _load_json_arg(s: str) -> Any:
    return json.loads(s)


def main() -> int:
    parser = argparse.ArgumentParser(description="易企秀 AIGC HTTP API 客户端")
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"API 根地址（默认来自环境变量 EQXIU_AIGC_API_BASE 或 {DEFAULT_BASE_URL!r}）",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=900.0,
        help="请求超时秒数（scene-tpl 可能很慢）",
    )
    parser.add_argument(
        "--access-token",
        default=None,
        help=f"X-Openclaw-Token（默认从 {CONFIG_PATH} 读取）",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("login", help="交互式登录，保存 X-Openclaw-Token")
    p_auth = sub.add_parser("auth", help="认证相关命令")
    auth_sub = p_auth.add_subparsers(dest="auth_cmd", required=True)
    auth_sub.add_parser("status", help="验证 token 是否有效")

    p_cat = sub.add_parser("category", help="GET /iaigc/category")
    p_sty = sub.add_parser("style", help="GET /iaigc/style")
    p_sty.add_argument("--two", type=int, required=True, dest="two_level")
    p_sty.add_argument("--three", type=int, required=True, dest="three_level")

    p_out = sub.add_parser("outline", help="POST /iaigc/outline")
    p_out.add_argument("--category-id", type=int, required=True)
    p_out.add_argument(
        "--fields-json",
        required=True,
        help='sceneFields JSON 数组，如 \'[{"id":1,"value":"活动主题"}]\'',
    )

    p_tpl = sub.add_parser("scene-tpl", help="POST /iaigc/scene-tpl")
    p_tpl.add_argument("--json-file", required=True, help="完整请求体 JSON 文件路径")

    p_pipe = sub.add_parser("pipeline", help="依次调用 outline + scene-tpl")
    p_pipe.add_argument("--category-id", type=int, required=True)
    p_pipe.add_argument("--title", required=True)
    p_pipe.add_argument("--fields-json", required=True)
    p_pipe.add_argument("--style-id", type=int, default=None)

    args = parser.parse_args()
    cfg = _load_config()
    token = (args.access_token or "").strip() or _token_from_config(cfg)

    if args.cmd == "login":
        return _login_interactive()

    try:
        if args.cmd == "auth":
            if args.auth_cmd != "status":
                print("未知 auth 子命令", file=sys.stderr)
                return 2
            if not token:
                print("缺少 X-Openclaw-Token：请先执行 login 或传 --access-token", file=sys.stderr)
                return 1
            out = _check_auth_status(token, args.timeout)
        else:
            client = EqxiuAigcClient(base_url=args.base_url, timeout=args.timeout, access_token=token or None)
            if args.cmd == "category":
                out = client.list_categories()
            elif args.cmd == "style":
                out = client.list_styles(args.two_level, args.three_level)
            elif args.cmd == "outline":
                fields = _load_json_arg(args.fields_json)
                if not isinstance(fields, list):
                    print("fields-json 必须是 JSON 数组", file=sys.stderr)
                    return 2
                out = client.create_outline(fields, args.category_id)
            elif args.cmd == "scene-tpl":
                with open(args.json_file, encoding="utf-8") as f:
                    body = json.load(f)
                out = client.create_scene_tpl(
                    scene_fields=body["sceneFields"],
                    scene_id=body["sceneId"],
                    title=body["title"],
                    outline_task_id=body["outlineTaskId"],
                    outline=body["outline"],
                    image_id=body.get("imageId"),
                    style_id=body.get("styleId"),
                )
            elif args.cmd == "pipeline":
                fields = _load_json_arg(args.fields_json)
                if not isinstance(fields, list):
                    print("fields-json 必须是 JSON 数组", file=sys.stderr)
                    return 2
                out = client.run_pipeline(
                    fields,
                    args.category_id,
                    args.title,
                    style_id=args.style_id,
                )
            else:
                print(f"未知子命令: {args.cmd}", file=sys.stderr)
                return 2
    except EqxiuAigcApiError as e:
        print(json.dumps({"error": str(e), "raw": e.raw}, ensure_ascii=False, indent=2))
        return 1
    except requests.RequestException as e:
        print(json.dumps({"error": f"HTTP 错误: {e}"}, ensure_ascii=False), file=sys.stderr)
        return 1

    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
