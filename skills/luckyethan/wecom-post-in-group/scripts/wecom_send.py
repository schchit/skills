#!/usr/bin/env python3
"""
企业微信群机器人 - 消息发送脚本

支持的消息类型:
  - text:     纯文本消息（支持 @成员）
  - markdown: Markdown 格式消息（支持有限标签）

使用方法:
  # 发送纯文本消息
  python3 wecom_send.py --key <WEBHOOK_KEY> --type text --content "Hello World"

  # 发送 Markdown 消息
  python3 wecom_send.py --key <WEBHOOK_KEY> --type markdown --content "## 标题\n- 列表项"

  # 从文件读取内容发送
  python3 wecom_send.py --key <WEBHOOK_KEY> --type markdown --file report.md

  # @所有人
  python3 wecom_send.py --key <WEBHOOK_KEY> --type text --content "紧急通知" --mention-all

  # @指定成员 (userid)
  python3 wecom_send.py --key <WEBHOOK_KEY> --type text --content "请查收" --mention user1,user2

  # @指定手机号
  python3 wecom_send.py --key <WEBHOOK_KEY> --type text --content "请查收" --mention-mobile 13800138000,13900139000

退出码:
  0 - 发送成功
  1 - 参数错误
  2 - 发送失败
"""

import argparse
import json
import ssl
import sys
import urllib.request
import urllib.error

WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}"

# macOS 上可能遇到 SSL 证书问题，创建不验证的 context
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


def _post(url: str, payload: dict) -> dict:
    """发送 POST 请求到企微 Webhook"""
    json_data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=json_data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15, context=_ssl_ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"errcode": e.code, "errmsg": f"HTTP Error: {e.reason}"}
    except urllib.error.URLError as e:
        return {"errcode": -1, "errmsg": f"URL Error: {e.reason}"}
    except Exception as e:
        return {"errcode": -1, "errmsg": str(e)}


def send_text(key: str, content: str,
              mentioned_list: list = None,
              mentioned_mobile_list: list = None) -> dict:
    """
    发送纯文本消息

    Args:
        key: 机器人 Webhook Key
        content: 消息内容，最长不超过 2048 字节
        mentioned_list: @指定成员的 userid 列表, ["@all"] 表示 @所有人
        mentioned_mobile_list: @指定成员的手机号列表
    Returns:
        API 响应 dict，errcode=0 表示成功
    """
    url = WEBHOOK_URL.format(key)
    data = {
        "msgtype": "text",
        "text": {"content": content},
    }
    if mentioned_list:
        data["text"]["mentioned_list"] = mentioned_list
    if mentioned_mobile_list:
        data["text"]["mentioned_mobile_list"] = mentioned_mobile_list
    return _post(url, data)


def send_markdown(key: str, content: str) -> dict:
    """
    发送 Markdown 消息

    Args:
        key: 机器人 Webhook Key
        content: Markdown 格式内容（支持有限标签，详见 references/api_reference.md）
    Returns:
        API 响应 dict，errcode=0 表示成功
    """
    url = WEBHOOK_URL.format(key)
    data = {
        "msgtype": "markdown",
        "markdown": {"content": content},
    }
    return _post(url, data)


def main():
    parser = argparse.ArgumentParser(description="企业微信群机器人消息发送工具")
    parser.add_argument("--key", required=True, help="Webhook Key")
    parser.add_argument("--type", choices=["text", "markdown"], default="text",
                        help="消息类型 (默认: text)")
    parser.add_argument("--content", help="消息内容（与 --file 二选一）")
    parser.add_argument("--file", help="从文件读取消息内容（与 --content 二选一）")
    parser.add_argument("--mention", help="@指定成员的 userid，逗号分隔")
    parser.add_argument("--mention-mobile", help="@指定成员的手机号，逗号分隔")
    parser.add_argument("--mention-all", action="store_true", help="@所有人")
    args = parser.parse_args()

    # 获取消息内容
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"❌ 文件不存在: {args.file}", file=sys.stderr)
            sys.exit(1)
    elif args.content:
        content = args.content
    else:
        print("❌ 请通过 --content 或 --file 提供消息内容", file=sys.stderr)
        sys.exit(1)

    # 发送消息
    if args.type == "text":
        mentioned_list = None
        mentioned_mobile_list = None
        if args.mention_all:
            mentioned_list = ["@all"]
        elif args.mention:
            mentioned_list = [uid.strip() for uid in args.mention.split(",")]
        if args.mention_mobile:
            mentioned_mobile_list = [m.strip() for m in args.mention_mobile.split(",")]

        result = send_text(args.key, content, mentioned_list, mentioned_mobile_list)
    else:
        result = send_markdown(args.key, content)

    # 输出结果
    if result.get("errcode") == 0:
        print("✅ 消息发送成功!")
        sys.exit(0)
    else:
        errcode = result.get("errcode", "未知")
        errmsg = result.get("errmsg", "未知错误")
        print(f"❌ 发送失败! 错误码: {errcode}", file=sys.stderr)
        print(f"   错误信息: {errmsg}", file=sys.stderr)
        if errcode == 93000:
            print("   💡 提示: Webhook 地址无效，请检查 key 是否正确", file=sys.stderr)
        elif errcode == 45009:
            print("   💡 提示: 发送频率超过限制，请稍后再试", file=sys.stderr)
        # 同时输出 JSON 结果到 stdout 方便程序解析
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(2)


if __name__ == "__main__":
    main()
