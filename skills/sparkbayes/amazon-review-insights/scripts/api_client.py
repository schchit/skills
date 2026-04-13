"""
CustomerInsights API Client
用于 AI Agent 调用评论获取和分析接口

Author: Zhang Di
Email: dizflyme@qq.com
Date: 2025-03-25
LastEditors: Zhang Di
LastEditTime: 2026-03-27
Description: 跨境电商客户洞察 API 客户端封装
"""

import argparse
import json
import os
from typing import Any, Dict

# 使用 requests 库以确保 macOS 证书兼容性
try:
    import requests
except ImportError:
    raise ImportError("请安装 requests 库: pip install requests")

# API 配置
_API_KEY = os.environ.get("CUSTOMER_INSIGHTS_API_KEY", "")
_BASE_URL = "https://api.astrmap.com"


class CustomerInsightsClient:
    """CustomerInsights API 客户端"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _post(self, path: str, data: dict = None) -> dict:
        """POST 请求"""
        url = f"{_BASE_URL}{path}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            response = requests.post(url, json=data or {}, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"API Error: {result.get('msg')}")
            return result.get("data", {})
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request Error: {e}")

    # ==================== 设备管理 ====================

    def check_device_online(self) -> Dict[str, Any]:
        """检查设备是否在线"""
        return self._post("/api/v1/external/device/status", {})

    # ==================== 任务管理 ====================

    def create_task(
        self, submit_content: str, site: str = "US", platform: str = "amazon", is_auto: bool = True
    ) -> str:
        """创建任务

        Args:
            submit_content: ASIN 或产品 URL
            site: 站点代码，默认 US
            platform: 平台，默认 amazon
            is_auto: 是否自动模式，True=自动分析，False=仅采集（需手动触发分析）
        """
        data = {
            "platform": platform,
            "site": site,
            "submit_content": submit_content,
            "is_auto": is_auto,
        }
        result = self._post("/api/v1/external/task/create", data)
        return result["task_id"]

    def trigger_analysis(self, task_id: str) -> Dict[str, Any]:
        """手动触发仅采集任务的 AI 分析流程"""
        return self._post(f"/api/v1/external/task/{task_id}/trigger-analysis", {})

    def get_task_detail(self, task_id: str) -> Dict[str, Any]:
        """查询任务详情"""
        return self._post("/api/v1/external/task/detail", {"task_id": task_id})

    def get_task_list(
        self,
        page: int = 1,
        page_size: int = 20,
        search_keyword: str = "",
        filter_monitoring: bool = False,
    ) -> Dict[str, Any]:
        """获取任务列表"""
        return self._post(
            "/api/v1/external/task/list",
            {
                "page": page,
                "page_size": page_size,
                "search_keyword": search_keyword,
                "filter_monitoring": filter_monitoring,
            },
        )

    def create_incremental(self, task_id: str) -> Dict[str, Any]:
        """为终态任务创建增量获取"""
        return self._post("/api/v1/external/task/incremental", {"task_id": task_id})

    # ==================== 分析结果 ====================

    def get_ai_insights(self, task_id: str) -> Dict[str, Any]:
        """获取 AI 洞察"""
        return self._post("/api/v1/external/analysis/insights", {"task_id": task_id})

    def get_tag_categories(self, task_id: str) -> Dict[str, Any]:
        """获取标签分布"""
        return self._post("/api/v1/external/analysis/tags", {"task_id": task_id})

    def get_issue_statistics(self, task_id: str) -> Dict[str, Any]:
        """获取问题维度统计"""
        return self._post(
            "/api/v1/external/analysis/issue-statistics", {"task_id": task_id}
        )

    def get_top_issues(self, task_id: str) -> Dict[str, Any]:
        """获取要点问题分布"""
        return self._post("/api/v1/external/analysis/top-issues", {"task_id": task_id})

    def get_basic_statistics(self, task_id: str) -> Dict[str, Any]:
        """获取基础统计"""
        return self._post("/api/v1/external/analysis/statistics", {"task_id": task_id})

    def get_negative_reviews(
        self, task_id: str, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """获取差评列表"""
        return self._post(
            "/api/v1/external/analysis/negative-reviews",
            {"task_id": task_id, "page": page, "page_size": page_size},
        )

    def get_trend(
        self, task_id: str, filter_data: str = "30", filter_product: str = "all"
    ) -> Dict[str, Any]:
        """获取评论趋势"""
        return self._post(
            "/api/v1/external/analysis/trend",
            {
                "task_id": task_id,
                "filter_data": filter_data,
                "filter_product": filter_product,
            },
        )

    def get_comments(
        self,
        task_id: str,
        page: int = 1,
        page_size: int = 20,
        filter_star: str = "all",
        filter_verified: str = "all",
    ) -> Dict[str, Any]:
        """获取原始评论"""
        return self._post(
            "/api/v1/external/analysis/comments",
            {
                "task_id": task_id,
                "page": page,
                "page_size": page_size,
                "filter_star": filter_star,
                "filter_verified": filter_verified,
            },
        )

    def get_comments_overview(self, task_id: str) -> Dict[str, Any]:
        """获取评论概览"""
        return self._post(
            "/api/v1/external/analysis/comments-overview", {"task_id": task_id}
        )

    # ==================== 账户管理 ====================

    def get_points(self) -> int:
        """获取积分余额"""
        result = self._post("/api/v1/external/account/points", {})
        return result.get("available_points", 0)


# ==================== CLI 入口 ====================


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="星图客户洞察 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--api-key", "-k", default=_API_KEY, help="API Key")
    parser.add_argument(
        "--action",
        "-a",
        required=True,
        help="执行的操作: check_device, create_task, get_task_detail, get_task_list, create_incremental, get_ai_insights, get_tag_categories, get_issue_statistics, get_top_issues, get_basic_statistics, get_negative_reviews, get_trend, get_comments, get_comments_overview, get_points",
    )

    # 动作参数
    parser.add_argument("--asin", help="ASIN 或产品 URL (create_task)")
    parser.add_argument(
        "--site", default="US", help="站点: US/CA/DE/FR/UK/JP/IT/ES (create_task)"
    )
    parser.add_argument("--platform", default="amazon", help="平台 (create_task)")
    parser.add_argument(
        "--is-auto", type=lambda x: x.lower() == "true", default=True,
        help="是否自动模式: true/false, True=自动分析, False=仅采集 (create_task)"
    )
    parser.add_argument(
        "--task-id", help="任务 ID (get_task_detail, create_incremental, trigger_analysis, get_xxx)"
    )
    parser.add_argument("--page", type=int, default=1, help="页码")
    parser.add_argument("--page-size", type=int, default=20, help="每页数量")
    parser.add_argument(
        "--filter-data", default="30", help="数据范围: 30/60/all (get_trend)"
    )
    parser.add_argument(
        "--filter-star", default="all", help="评分筛选: 1-5/all (get_comments)"
    )

    return parser


def execute(params: dict) -> dict:
    """
    统一入口函数（供 AI Agent 调度）

    :param params: OpenClaw 传入的参数
    :return: 执行结果字典
    """
    try:
        api_key = params.get("api_key") or _API_KEY
        action = params.get("action", "")

        if not api_key:
            return {
                "status": "error",
                "message": "请提供 API Key。通过环境变量 CUSTOMER_INSIGHTS_API_KEY 设置，或通过 --api-key 参数传入。",
            }

        client = CustomerInsightsClient(api_key)

        # 路由到具体方法
        if action == "check_device":
            return {"status": "success", "output": client.check_device_online()}

        elif action == "create_task":
            submit_content = params.get("submit_content") or params.get("asin", "")
            if not submit_content:
                return {
                    "status": "error",
                    "message": "缺少 submit_content 或 asin 参数",
                }
            task_id = client.create_task(
                submit_content=submit_content,
                site=params.get("site", "US"),
                platform=params.get("platform", "amazon"),
                is_auto=params.get("is_auto", True),
            )
            return {"status": "success", "output": {"task_id": task_id}}

        elif action == "get_task_detail":
            task_id = params.get("task_id")
            if not task_id:
                return {"status": "error", "message": "缺少 task_id 参数"}
            return {"status": "success", "output": client.get_task_detail(task_id)}

        elif action == "get_task_list":
            return {
                "status": "success",
                "output": client.get_task_list(
                    page=params.get("page", 1),
                    page_size=params.get("page_size", 20),
                ),
            }

        elif action == "create_incremental":
            task_id = params.get("task_id")
            if not task_id:
                return {"status": "error", "message": "缺少 task_id 参数"}
            return {"status": "success", "output": client.create_incremental(task_id)}

        elif action == "trigger_analysis":
            task_id = params.get("task_id")
            if not task_id:
                return {"status": "error", "message": "缺少 task_id 参数"}
            return {"status": "success", "output": client.trigger_analysis(task_id)}

        elif action == "get_ai_insights":
            task_id = params.get("task_id")
            if not task_id:
                return {"status": "error", "message": "缺少 task_id 参数"}
            return {"status": "success", "output": client.get_ai_insights(task_id)}

        elif action == "get_tag_categories":
            task_id = params.get("task_id")
            if not task_id:
                return {"status": "error", "message": "缺少 task_id 参数"}
            return {"status": "success", "output": client.get_tag_categories(task_id)}

        elif action == "get_issue_statistics":
            task_id = params.get("task_id")
            if not task_id:
                return {"status": "error", "message": "缺少 task_id 参数"}
            return {"status": "success", "output": client.get_issue_statistics(task_id)}

        elif action == "get_top_issues":
            task_id = params.get("task_id")
            if not task_id:
                return {"status": "error", "message": "缺少 task_id 参数"}
            return {"status": "success", "output": client.get_top_issues(task_id)}

        elif action == "get_basic_statistics":
            task_id = params.get("task_id")
            if not task_id:
                return {"status": "error", "message": "缺少 task_id 参数"}
            return {"status": "success", "output": client.get_basic_statistics(task_id)}

        elif action == "get_negative_reviews":
            task_id = params.get("task_id")
            if not task_id:
                return {"status": "error", "message": "缺少 task_id 参数"}
            return {
                "status": "success",
                "output": client.get_negative_reviews(
                    task_id,
                    page=params.get("page", 1),
                    page_size=params.get("page_size", 20),
                ),
            }

        elif action == "get_trend":
            task_id = params.get("task_id")
            if not task_id:
                return {"status": "error", "message": "缺少 task_id 参数"}
            return {
                "status": "success",
                "output": client.get_trend(
                    task_id,
                    filter_data=params.get("filter_data", "30"),
                ),
            }

        elif action == "get_comments":
            task_id = params.get("task_id")
            if not task_id:
                return {"status": "error", "message": "缺少 task_id 参数"}
            return {
                "status": "success",
                "output": client.get_comments(
                    task_id,
                    page=params.get("page", 1),
                    page_size=params.get("page_size", 20),
                    filter_star=params.get("filter_star", "all"),
                ),
            }

        elif action == "get_comments_overview":
            task_id = params.get("task_id")
            if not task_id:
                return {"status": "error", "message": "缺少 task_id 参数"}
            return {
                "status": "success",
                "output": client.get_comments_overview(task_id),
            }

        elif action == "get_points":
            return {
                "status": "success",
                "output": {"available_points": client.get_points()},
            }

        else:
            return {"status": "error", "message": f"未知操作: {action}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def main():
    """命令行入口"""
    parser = create_parser()
    args = parser.parse_args()

    params = {
        "api_key": args.api_key,
        "action": args.action,
        "submit_content": args.asin,
        "site": args.site,
        "platform": args.platform,
        "is_auto": args.is_auto,
        "task_id": args.task_id,
        "page": args.page,
        "page_size": args.page_size,
        "filter_data": args.filter_data,
        "filter_star": args.filter_star,
    }

    result = execute(params)
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ==================== 便捷函数（向后兼容） ====================


def check_device_online(api_key: str = _API_KEY) -> Dict[str, Any]:
    """便捷函数：检查设备是否在线"""
    return execute({"api_key": api_key, "action": "check_device"})


def create_task(
    submit_content: str,
    site: str = "US",
    platform: str = "amazon",
    is_auto: bool = True,
    api_key: str = _API_KEY,
) -> str:
    """便捷函数：创建任务

    Args:
        submit_content: ASIN 或产品 URL
        site: 站点代码，默认 US
        platform: 平台，默认 amazon
        is_auto: 是否自动模式，True=自动分析，False=仅采集（需手动触发分析）
    """
    result = execute(
        {
            "api_key": api_key,
            "action": "create_task",
            "submit_content": submit_content,
            "site": site,
            "platform": platform,
            "is_auto": is_auto,
        }
    )
    if result["status"] == "success":
        return result["output"]["task_id"]
    raise Exception(result["message"])


def trigger_analysis(task_id: str, api_key: str = _API_KEY) -> Dict[str, Any]:
    """便捷函数：手动触发仅采集任务的 AI 分析"""
    return execute(
        {
            "api_key": api_key,
            "action": "trigger_analysis",
            "task_id": task_id,
        }
    )


def get_ai_insights(task_id: str, api_key: str = _API_KEY) -> Dict[str, Any]:
    """便捷函数：获取 AI 洞察"""
    return execute(
        {
            "api_key": api_key,
            "action": "get_ai_insights",
            "task_id": task_id,
        }
    )


def get_points(api_key: str = _API_KEY) -> int:
    """便捷函数：获取积分余额"""
    result = execute({"api_key": api_key, "action": "get_points"})
    if result["status"] == "success":
        return result["output"]["available_points"]
    raise Exception(result["message"])


def get_task_list(
    page: int = 1,
    page_size: int = 20,
    api_key: str = _API_KEY,
) -> Dict[str, Any]:
    """便捷函数：获取任务列表"""
    return execute(
        {
            "api_key": api_key,
            "action": "get_task_list",
            "page": page,
            "page_size": page_size,
        }
    )


def get_task_detail(task_id: str, api_key: str = _API_KEY) -> Dict[str, Any]:
    """便捷函数：获取任务详情"""
    return execute(
        {
            "api_key": api_key,
            "action": "get_task_detail",
            "task_id": task_id,
        }
    )


def create_incremental(task_id: str, api_key: str = _API_KEY) -> Dict[str, Any]:
    """便捷函数：为终态任务创建增量获取"""
    return execute(
        {
            "api_key": api_key,
            "action": "create_incremental",
            "task_id": task_id,
        }
    )


if __name__ == "__main__":
    main()
