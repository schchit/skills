#!/usr/bin/env python3
"""
百度智能云 BOS Python SDK 操作脚本

依赖：pip install bce-python-sdk
凭证读取优先级：
  1. 环境变量：BCE_ACCESS_KEY_ID / BCE_SECRET_ACCESS_KEY / BCE_BOS_ENDPOINT / BCE_BOS_BUCKET
  2. 配置文件：~/.config/openclaw/baidu-cloud-bos/credentials.json
  BCE_STS_TOKEN（可选，临时凭证）

用法：python3 bos_python.py <action> [--option value ...]
"""

import json
import os
import sys
import argparse
from pathlib import Path

from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials
from baidubce.services.bos.bos_client import BosClient

CRED_PATH = Path.home() / ".config" / "openclaw" / "baidu-cloud-bos" / "credentials.json"


def _load_file_credentials():
    """从 credentials.json 加载凭证，返回 dict 或空 dict"""
    if not CRED_PATH.exists():
        return {}
    try:
        return json.loads(CRED_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def get_client():
    file_cred = _load_file_credentials()

    ak = os.environ.get("BCE_ACCESS_KEY_ID") or file_cred.get("accessKeyId")
    sk = os.environ.get("BCE_SECRET_ACCESS_KEY") or file_cred.get("secretAccessKey")
    endpoint = os.environ.get("BCE_BOS_ENDPOINT") or file_cred.get("endpoint")

    if not ak or not sk or not endpoint:
        print(json.dumps({
            "success": False,
            "error": "缺少凭证。请通过环境变量设置，或运行 setup.sh 将凭证保存到 ~/.config/openclaw/baidu-cloud-bos/credentials.json"
        }))
        sys.exit(1)

    if not endpoint.startswith("http"):
        endpoint = f"https://{endpoint}"

    config = BceClientConfiguration(
        credentials=BceCredentials(ak, sk),
        endpoint=endpoint,
    )

    sts_token = os.environ.get("BCE_STS_TOKEN") or file_cred.get("stsToken")
    if sts_token:
        config.security_token = sts_token

    return BosClient(config)


def get_bucket():
    file_cred = _load_file_credentials()
    bucket = os.environ.get("BCE_BOS_BUCKET") or file_cred.get("bucket")
    if not bucket:
        print(json.dumps({
            "success": False,
            "error": "缺少 Bucket。请通过环境变量 BCE_BOS_BUCKET 设置，或运行 setup.sh 保存到 credentials.json"
        }))
        sys.exit(1)
    return bucket


def output(data):
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def cmd_upload(args):
    client = get_client()
    bucket = get_bucket()

    if not args.file:
        raise ValueError("缺少 --file 参数")
    if not os.path.exists(args.file):
        raise FileNotFoundError(f"文件不存在：{args.file}")

    key = args.key or os.path.basename(args.file)
    file_size = os.path.getsize(args.file)

    response = client.put_object_from_file(bucket, key, args.file)

    output({
        "success": True,
        "action": "upload",
        "key": key,
        "eTag": getattr(response.metadata, "etag", None),
        "size": file_size,
        "bucket": bucket,
    })


def cmd_put_string(args):
    client = get_client()
    bucket = get_bucket()

    if not args.content:
        raise ValueError("缺少 --content 参数")
    if not args.key:
        raise ValueError("缺少 --key 参数")

    content_type = getattr(args, "content_type", None) or "text/plain"
    response = client.put_object_from_string(
        bucket, args.key, args.content,
        content_type=content_type,
    )

    output({
        "success": True,
        "action": "put-string",
        "key": args.key,
        "eTag": getattr(response.metadata, "etag", None),
        "bucket": bucket,
    })


def cmd_download(args):
    client = get_client()
    bucket = get_bucket()

    if not args.key:
        raise ValueError("缺少 --key 参数")

    output_path = args.output or os.path.basename(args.key)
    output_path = os.path.abspath(output_path)

    client.get_object_to_file(bucket, args.key, output_path)

    output({
        "success": True,
        "action": "download",
        "key": args.key,
        "savedTo": output_path,
        "bucket": bucket,
    })


def cmd_list(args):
    client = get_client()
    bucket = get_bucket()

    prefix = args.prefix or ""
    max_keys = int(args.max_keys) if args.max_keys else 100
    marker = args.marker or ""

    response = client.list_objects(
        bucket,
        prefix=prefix,
        max_keys=max_keys,
        marker=marker,
    )

    files = []
    for obj in getattr(response, "contents", []) or []:
        files.append({
            "key": obj.key,
            "size": obj.size,
            "lastModified": str(obj.last_modified),
            "eTag": obj.etag,
            "storageClass": getattr(obj, "storage_class", "STANDARD"),
        })

    output({
        "success": True,
        "action": "list",
        "prefix": prefix,
        "count": len(files),
        "isTruncated": getattr(response, "is_truncated", False),
        "nextMarker": getattr(response, "next_marker", None),
        "files": files,
    })


def cmd_sign_url(args):
    client = get_client()
    bucket = get_bucket()

    if not args.key:
        raise ValueError("缺少 --key 参数")

    expires = int(args.expires) if args.expires else 3600
    url = client.generate_pre_signed_url(bucket, args.key, expiration_in_seconds=expires)

    output({
        "success": True,
        "action": "sign-url",
        "key": args.key,
        "expires": expires,
        "url": url,
    })


def cmd_head(args):
    client = get_client()
    bucket = get_bucket()

    if not args.key:
        raise ValueError("缺少 --key 参数")

    response = client.get_object_meta_data(bucket, args.key)
    metadata = response.metadata

    output({
        "success": True,
        "action": "head",
        "key": args.key,
        "contentLength": getattr(metadata, "content_length", None),
        "contentType": getattr(metadata, "content_type", None),
        "eTag": getattr(metadata, "etag", None),
        "lastModified": str(getattr(metadata, "last_modified", "")),
        "storageClass": getattr(metadata, "bce_storage_class", "STANDARD"),
        "bucket": bucket,
    })


def cmd_delete(args):
    client = get_client()
    bucket = get_bucket()

    if not args.key:
        raise ValueError("缺少 --key 参数")

    client.delete_object(bucket, args.key)

    output({
        "success": True,
        "action": "delete",
        "key": args.key,
        "bucket": bucket,
    })


def cmd_copy(args):
    client = get_client()
    bucket = get_bucket()

    source_bucket = args.source_bucket or bucket
    if not args.source_key:
        raise ValueError("缺少 --source-key 参数")
    if not args.key:
        raise ValueError("缺少 --key 参数（目标路径）")

    response = client.copy_object(
        source_bucket, args.source_key,
        bucket, args.key,
    )

    output({
        "success": True,
        "action": "copy",
        "sourceBucket": source_bucket,
        "sourceKey": args.source_key,
        "destBucket": bucket,
        "destKey": args.key,
        "eTag": getattr(response, "etag", None),
    })


def cmd_list_buckets(args):
    client = get_client()
    response = client.list_buckets()

    buckets = []
    for b in getattr(response, "buckets", []) or []:
        buckets.append({
            "name": b.name,
            "location": getattr(b, "location", None),
            "creationDate": str(getattr(b, "creation_date", "")),
        })

    output({
        "success": True,
        "action": "list-buckets",
        "count": len(buckets),
        "buckets": buckets,
    })


def main():
    parser = argparse.ArgumentParser(description="百度智能云 BOS Python SDK 操作脚本")
    subparsers = parser.add_subparsers(dest="action")

    # upload
    p = subparsers.add_parser("upload")
    p.add_argument("--file", required=True)
    p.add_argument("--key")

    # put-string
    p = subparsers.add_parser("put-string")
    p.add_argument("--content", required=True)
    p.add_argument("--key", required=True)
    p.add_argument("--content-type", dest="content_type")

    # download
    p = subparsers.add_parser("download")
    p.add_argument("--key", required=True)
    p.add_argument("--output")

    # list
    p = subparsers.add_parser("list")
    p.add_argument("--prefix", default="")
    p.add_argument("--max-keys", dest="max_keys")
    p.add_argument("--marker", default="")

    # sign-url
    p = subparsers.add_parser("sign-url")
    p.add_argument("--key", required=True)
    p.add_argument("--expires")

    # head
    p = subparsers.add_parser("head")
    p.add_argument("--key", required=True)

    # delete
    p = subparsers.add_parser("delete")
    p.add_argument("--key", required=True)

    # copy
    p = subparsers.add_parser("copy")
    p.add_argument("--source-bucket", dest="source_bucket")
    p.add_argument("--source-key", dest="source_key", required=True)
    p.add_argument("--key", required=True)

    # list-buckets
    subparsers.add_parser("list-buckets")

    args = parser.parse_args()

    if not args.action:
        output({
            "success": False,
            "error": "未指定操作",
            "availableActions": [
                "upload", "put-string", "download", "list",
                "sign-url", "head", "delete", "copy", "list-buckets",
            ],
            "usage": "python3 bos_python.py <action> [--option value ...]",
        })
        sys.exit(1)

    actions = {
        "upload": cmd_upload,
        "put-string": cmd_put_string,
        "download": cmd_download,
        "list": cmd_list,
        "sign-url": cmd_sign_url,
        "head": cmd_head,
        "delete": cmd_delete,
        "copy": cmd_copy,
        "list-buckets": cmd_list_buckets,
    }

    try:
        actions[args.action](args)
    except Exception as e:
        output({
            "success": False,
            "action": args.action,
            "error": str(e),
            "code": getattr(e, "code", None),
        })
        sys.exit(1)


if __name__ == "__main__":
    main()
