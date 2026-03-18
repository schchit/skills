#!/usr/bin/env python3
"""
Media.io Imagen 4 Image Generator - API Router

提供标准的 AIGC 技能实现，具有自动 API 路由和参数映射功能。
"""
import json
import os
import logging
import time
from typing import Any, Dict, Optional, List
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIError(Exception):
    """API 调用错误"""
    def __init__(self, message: str, code: int = None, data: Dict = None):
        self.message = message
        self.code = code
        self.data = data
        super().__init__(self.message)


class Skill:
    """
    标准 AIGC 技能实现，具有自动 API 路由和参数映射功能。

    特性：
    - 自动从 JSON 文档加载 API 定义
    - 严格的 HTTPS 主机验证
    - 自动路径参数替换
    - 内置重试机制
    - 完整的错误处理
    - 详细的日志记录
    """

    # 允许的 API 主机
    ALLOWED_HOST = 'openapi.media.io'

    # 默认请求超时时间（秒）
    DEFAULT_TIMEOUT = 30

    # 默认重试配置
    DEFAULT_RETRY_CONFIG = {
        'total': 3,
        'backoff_factor': 0.5,
        'status_forcelist': [429, 500, 502, 503, 504],
        'allowed_methods': ['POST', 'GET', 'PUT', 'DELETE']
    }

    def __init__(
        self,
        api_doc_path: str,
        enable_retry: bool = True,
        timeout: int = DEFAULT_TIMEOUT,
        retry_config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化 Skill 实例。

        Args:
            api_doc_path: API 文档 JSON 文件路径
            enable_retry: 是否启用自动重试
            timeout: 请求超时时间（秒）
            retry_config: 自定义重试配置
        """
        self.api_doc_path = api_doc_path
        self.enable_retry = enable_retry
        self.timeout = timeout

        # 加载 API 定义
        self.api_definitions = self._load_api_definitions(api_doc_path)

        # 配置重试策略
        if enable_retry:
            self.retry_config = {**self.DEFAULT_RETRY_CONFIG, **(retry_config or {})}
            self.session = self._create_session()
        else:
            self.session = requests.Session()

        logger.info(f"Skill 初始化成功，加载了 {len(self.api_definitions)} 个 API 定义")

    def _load_api_definitions(self, api_doc_path: str) -> Dict[str, Any]:
        """
        从 JSON 文件加载 API 定义。

        Args:
            api_doc_path: API 文档文件路径

        Returns:
            API 定义字典

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: JSON 格式错误或有重复的 API 名称
        """
        if not os.path.exists(api_doc_path):
            raise FileNotFoundError(f"API 文档文件不存在: {api_doc_path}")

        try:
            with open(api_doc_path, 'r', encoding='utf-8') as f:
                api_items = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"API 文档 JSON 格式错误: {e}")

        api_definitions = {}
        duplicate_names = []

        for item in api_items:
            name = item.get('name')
            if not name:
                logger.warning(f"发现缺少 'name' 字段的 API 项，已跳过")
                continue

            if name in api_definitions:
                duplicate_names.append(name)
                logger.warning(f"发现重复的 API 名称: {name}")
                continue

            api_definitions[name] = item

        if duplicate_names:
            deduped = sorted(set(duplicate_names))
            raise ValueError(
                f"在 {api_doc_path} 中检测到重复的 API 名称: {', '.join(deduped)}。"
                f"请在 c_api_doc_detail.json 中使用唯一的 `name` 字段。"
            )

        return api_definitions

    def _create_session(self) -> requests.Session:
        """
        创建配置了重试策略的 requests Session。

        Returns:
            配置好的 Session 对象
        """
        session = requests.Session()

        retry_strategy = Retry(
            total=self.retry_config['total'],
            backoff_factor=self.retry_config['backoff_factor'],
            status_forcelist=self.retry_config['status_forcelist'],
            allowed_methods=self.retry_config['allowed_methods']
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session

    def _validate_url(self, url: str) -> None:
        """
        验证 URL 是否安全（仅允许 HTTPS 和允许的主机）。

        Args:
            url: 要验证的 URL

        Raises:
            ValueError: URL 不安全
        """
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise ValueError(f"无效的 URL: {url}") from e

        if parsed.scheme != 'https':
            raise ValueError(f"仅支持 HTTPS 协议，当前协议: {parsed.scheme}")

        if parsed.netloc.lower() != self.ALLOWED_HOST:
            raise ValueError(
                f"不允许的端点主机: {parsed.netloc}，"
                f"仅允许: {self.ALLOWED_HOST}"
            )

    def _prepare_url(self, endpoint: str, params: Dict[str, Any]) -> str:
        """
        准备请求 URL，替换路径参数。

        Args:
            endpoint: API 端点 URL
            params: 参数字典

        Returns:
            替换后的 URL
        """
        url = endpoint
        if '{' in url:
            for key, value in params.items():
                placeholder = f'{{{key}}}'
                if placeholder in url:
                    url = url.replace(placeholder, str(value))
                    logger.debug(f"替换路径参数: {placeholder} = {value}")

        return url

    def _prepare_body(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备请求体，排除路径参数。

        Args:
            endpoint: API 端点 URL
            params: 参数字典

        Returns:
            请求体字典
        """
        body = {}
        for key, value in params.items():
            placeholder = f'{{{key}}}'
            if placeholder not in endpoint:
                body[key] = value

        return body

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        处理 API 响应。

        Args:
            response: requests.Response 对象

        Returns:
            响应 JSON 数据
        """
        try:
            data = response.json()
        except json.JSONDecodeError:
            logger.error(f"响应不是有效的 JSON: {response.text[:200]}")
            return {
                'error': f'Invalid JSON response',
                'status_code': response.status_code,
                'response_text': response.text[:200]
            }

        # 记录响应状态
        if response.status_code == 200:
            code = data.get('code')
            if code == 0:
                logger.info(f"API 调用成功")
            else:
                logger.warning(f"API 返回错误码: {code}, 消息: {data.get('msg')}")
        else:
            logger.error(f"HTTP 错误: {response.status_code}")

        return data

    def get_available_apis(self) -> List[str]:
        """
        获取所有可用的 API 名称列表。

        Returns:
            API 名称列表
        """
        return list(self.api_definitions.keys())

    def get_api_info(self, api_name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定 API 的详细信息。

        Args:
            api_name: API 名称

        Returns:
            API 信息字典，如果不存在则返回 None
        """
        return self.api_definitions.get(api_name)

    def invoke(
        self,
        api_name: str,
        params: Dict[str, Any],
        api_key: Optional[str] = None,
        raw_response: bool = False
    ) -> Dict[str, Any]:
        """
        调用指定的 API。

        Args:
            api_name: API 名称
            params: 业务参数字典
            api_key: API 密钥。如果省略，则使用环境变量 API_KEY
            raw_response: 是否返回原始响应数据（包含状态码等）

        Returns:
            API 响应负载字典

        Raises:
            APIError: API 调用失败时抛出
        """
        # 验证 API 名称
        if api_name not in self.api_definitions:
            error_msg = f"API '{api_name}' 不存在。可用的 API: {', '.join(self.get_available_apis())}"
            logger.error(error_msg)
            if raw_response:
                return {'error': error_msg, 'status_code': 404}
            return {'error': error_msg}

        # 解析 API Key
        resolved_api_key = (api_key or os.getenv('API_KEY', '')).strip()
        if not resolved_api_key:
            error_msg = '缺少 API 密钥。请设置环境变量 API_KEY 或显式传入 api_key 参数'
            logger.error(error_msg)
            if raw_response:
                return {'error': error_msg, 'status_code': 401}
            return {'error': error_msg}

        # 获取 API 定义
        api = self.api_definitions[api_name]
        endpoint = api['endpoint']
        method = api['method']

        # 验证 URL 安全性
        try:
            self._validate_url(endpoint)
        except ValueError as e:
            logger.error(str(e))
            if raw_response:
                return {'error': str(e), 'status_code': 403}
            return {'error': str(e)}

        # 准备请求
        url = self._prepare_url(endpoint, params)
        body = self._prepare_body(endpoint, params)

        headers = {
            'X-API-KEY': resolved_api_key,
            'Content-Type': 'application/json'
        }

        logger.info(f"调用 API: {api_name}, 方法: {method}, URL: {url}")
        logger.debug(f"请求参数: {body}")

        # 发送请求
        try:
            response = self.session.request(
                method,
                url,
                headers=headers,
                json={'data': body} if body else {},
                timeout=self.timeout
            )

            result = self._handle_response(response)

            if raw_response:
                result['status_code'] = response.status_code

            return result

        except requests.exceptions.Timeout as e:
            error_msg = f"请求超时（{self.timeout}秒）: {str(e)}"
            logger.error(error_msg)
            if raw_response:
                return {'error': error_msg, 'status_code': 408}
            return {'error': error_msg}

        except requests.exceptions.ConnectionError as e:
            error_msg = f"连接错误: {str(e)}"
            logger.error(error_msg)
            if raw_response:
                return {'error': error_msg, 'status_code': 503}
            return {'error': error_msg}

        except requests.exceptions.RequestException as e:
            error_msg = f"请求失败: {str(e)}"
            logger.error(error_msg)
            if raw_response:
                return {'error': error_msg, 'status_code': 500}
            return {'error': error_msg}

        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            logger.exception(error_msg)
            if raw_response:
                return {'error': error_msg, 'status_code': 500}
            return {'error': error_msg}

    def close(self):
        """关闭 Session，释放资源"""
        if self.session:
            self.session.close()
            logger.info("Session 已关闭")

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动关闭 Session"""
        self.close()


# 标准使用示例
if __name__ == '__main__':
    # 使用上下文管理器确保资源正确释放
    script_dir = os.path.dirname(os.path.abspath(__file__))
    api_doc_path = os.path.join(script_dir, 'c_api_doc_detail.json')

    # 检查 API Key
    api_key = os.getenv('API_KEY', '')
    if not api_key:
        print("❌ 错误: 未设置环境变量 API_KEY")
        print("请先设置 API_KEY:")
        print("  Windows PowerShell: $env:API_KEY='your-api-key'")
        print("  macOS/Linux: export API_KEY='your-api-key'")
        exit(1)

    try:
        with Skill(api_doc_path, enable_retry=True) as skill:
            # 显示可用的 API
            print(f"📋 可用的 API: {', '.join(skill.get_available_apis())}")

            # 查询余额
            print("\n💰 查询账户余额...")
            result = skill.invoke('Credits', {}, api_key=api_key)

            if result.get('code') == 0:
                credits = result['data'].get('credits', 0)
                print(f"✅ 当前余额: {credits} 点数")
            else:
                print(f"❌ 查询失败: {result}")

            # 示例：生成图像（需要更多点数）
            # print("\n🎨 生成图像...")
            # result = skill.invoke(
            #     'Imagen 4',
            #     {
            #         'prompt': 'a beautiful sunset over mountains',
            #         'ratio': '16:9',
            #         'counts': '1'
            #     },
            #     api_key=api_key
            # )
            #
            # if result.get('code') == 0:
            #     task_id = result['data']['task_id']
            #     print(f"✅ 任务已创建，ID: {task_id}")
            # else:
            #     print(f"❌ 生成失败: {result}")

    except FileNotFoundError as e:
        print(f"❌ 文件错误: {e}")
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")
