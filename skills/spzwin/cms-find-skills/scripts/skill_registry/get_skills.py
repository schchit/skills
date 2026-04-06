#!/usr/bin/env python3
"""
主要内容：
  浏览、搜索、查看详情、获取下载地址。
  通过 API_BASE 环境变量配置接口基础地址。
"""

from __future__ import annotations

import argparse
import json
import sys
import requests
import warnings

import os

# 禁用 InsecureRequestWarning (因为 verify=False)
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

DEFAULT_API_BASE = "https://skills.mediportal.com.cn"
API_BASE = DEFAULT_API_BASE
API_URL = f"{API_BASE.rstrip('/')}/api/skill/list"


def parse_api_response(response: requests.Response, action: str) -> dict:
    data = response.json()
    if isinstance(data, dict) and data.get("resultCode") not in (None, 1):
        message = data.get("resultMsg") or data.get("detailMsg") or response.text
        raise RuntimeError(f"{action}失败: {message}")
    return data


def call_api() -> dict:
    """调用平台公开 Skill 列表接口（ClawHub 格式）。"""
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            verify=False,
            timeout=60,
            allow_redirects=True,
        )
        response.raise_for_status()
        return parse_api_response(response, "获取 Skill 列表")
    except Exception as exc:
        raise Exception(f"请求失败: {exc}")


def extract_skills(result: dict) -> list[dict]:
    """从响应中提取 Skill 列表。"""
    if isinstance(result, list):
        return result
    return result.get("data") or result.get("resultData") or []


def search_skills(skills: list[dict], keyword: str) -> list[dict]:
    """按名称、描述、skillCode、标签模糊匹配。"""
    kw = keyword.lower()
    results = []
    for skill in skills:
        tags = ""
        metadata = skill.get("metadata") or {}
        openclaw = metadata.get("openclaw") or {}
        if openclaw.get("tags"):
            tags = ",".join(openclaw["tags"])
        if (
            kw in (skill.get("skillCode") or skill.get("name") or "").lower()
            or kw in (skill.get("displayName") or skill.get("name") or "").lower()
            or kw in (skill.get("description") or "").lower()
            or kw in tags.lower()
        ):
            results.append(skill)
    return results


def find_one(skills: list[dict], query: str) -> dict | None:
    """按 skillCode 或 displayName 查找单个 Skill。"""
    q = query.lower()

    for skill in skills:
        if (skill.get("skillCode") or skill.get("name") or "").lower() == q:
            return skill

    for skill in skills:
        if (skill.get("displayName") or "").lower() == q:
            return skill

    for skill in skills:
        code = (skill.get("skillCode") or skill.get("name") or "").lower()
        display = (skill.get("displayName") or "").lower()
        if q in code or q in display:
            return skill

    return None


def get_download_url(skills: list[dict], query: str) -> str | None:
    """按 skillCode 或 displayName 获取下载地址。"""
    skill = find_one(skills, query)
    if not skill:
        return None
    return skill.get("downloadUrl")


def format_list(skills: list[dict]) -> str:
    """以紧凑表格格式展示列表。"""
    if not skills:
        return "（暂无已发布的 Skill）"

    lines = [
        f"{'#':<4} {'显示名':<24} {'SkillCode':<24} {'版本':<10} {'是否内置':<8} {'描述'}",
        "-" * 110,
    ]
    for index, skill in enumerate(skills, 1):
        display_name = (skill.get("displayName") or skill.get("name") or "")[:22]
        skill_code = (skill.get("skillCode") or skill.get("name") or "")[:22]
        version = (skill.get("version") or skill.get("version") or "")[:9]
        metadata = skill.get("metadata") or {}
        xgjk = metadata.get("xgjk") or {}
        internal = "是" if xgjk.get("isInternal") else "否"
        desc = (skill.get("description") or "")[:40]
        lines.append(f"{index:<4} {display_name:<24} {skill_code:<24} {version:<10} {internal:<8} {desc}")
    lines.append(f"\n共 {len(skills)} 个 Skill")
    return "\n".join(lines)


def format_detail(skill: dict) -> str:
    """格式化单个 Skill 的详情。"""
    owner = skill.get("owner") or {}
    metadata = skill.get("metadata") or {}
    xgjk = metadata.get("xgjk") or {}
    openclaw = metadata.get("openclaw") or {}
    tags = ",".join(openclaw.get("tags") or [])
    lines = [
        "=" * 72,
        f"显示名: {skill.get('displayName') or skill.get('name', '-')}",
        f"SkillCode: {skill.get('skillCode') or skill.get('name', '-')}",
        f"ID: {skill.get('id', '-')}",
        f"版本: {skill.get('version', '-')}",
        f"标签: {tags or '-'}",
        f"描述: {skill.get('description') or '-'}",
        f"下载地址: {skill.get('downloadUrl') or '-'}",
        f"作者: {owner.get('name', '-')}",
        f"创建时间: {skill.get('createTime', '-')}",
        f"下载数: {skill.get('downloadCount', '-')}",
        f"点赞数: {skill.get('likeCount', '-')}",
        f"收藏数: {skill.get('favoriteCount', '-')}",
        f"内置 Skill: {'是' if xgjk.get('isInternal') else '否'}",
        "=" * 72,
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Skill 发现：浏览、搜索、详情、下载地址")
    parser.add_argument("--search", "-s", help="按关键词搜索 Skill")
    parser.add_argument("--detail", "-d", help="查看某个 Skill 详情")
    parser.add_argument(
        "--url",
        "--download-url",
        "-u",
        dest="url",
        help="仅输出某个 Skill 的 downloadUrl",
    )
    parser.add_argument("--json", action="store_true", help="输出原始 JSON")
    args = parser.parse_args()

    try:
        result = call_api()
    except Exception as exc:
        print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    skills = extract_skills(result)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.url:
        url = get_download_url(skills, args.url)
        if not url:
            print(f"未找到 \"{args.url}\" 的下载地址", file=sys.stderr)
            sys.exit(1)
        print(url)
        return

    if args.detail:
        skill = find_one(skills, args.detail)
        if not skill:
            print(f"未找到匹配 \"{args.detail}\" 的 Skill", file=sys.stderr)
            sys.exit(1)
        print(format_detail(skill))
        return

    if args.search:
        matched = search_skills(skills, args.search)
        if not matched:
            print(f"搜索 \"{args.search}\" 无结果", file=sys.stderr)
            sys.exit(1)
        print(f"搜索 \"{args.search}\" 匹配到 {len(matched)} 个结果：\n")
        print(format_list(matched))
        return

    print("平台 Skill 列表\n")
    print(format_list(skills))


if __name__ == "__main__":
    main()
