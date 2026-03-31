import sys
import json
import requests
import time
import os
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse, parse_qs
import argparse
import keyring

API_BASE_URL = "https://api.jiuma.com/"

def call_api(endpoint: str, data: dict) -> dict:
    """调用API的通用函数"""
    url = f"{API_BASE_URL}{endpoint}"
    token = None
    try:
        token = keyring.get_password("jiuma_ai","openclaw_token")

    except FileNotFoundError:
        #print("文件不存在，请检查路径。")
        pass
    headers = {
        "Content-Type": "application/json"
    }
    if token:
            headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"API调用失败: {str(e)}")

def submit_task(task_params: dict) -> str:
    """
    步骤1: 提交任务
    接口: /console/aiApp/skillAiTaskAdd
    返回任务ID
    """
    request_data = {
        "task_params": json.dumps(task_params, ensure_ascii=False)
    }
    channel = get_params_key("channel")
    result = call_api("/console/aiApp/skillAiTaskAdd", request_data)
    if result.get("code") == 200:
        return result["data"]["task_id"]
    elif result.get("code") == 401:  # 未授权/未登录
        # 检查是否包含登录地址
        login_code_url = result.get("data", {}).get("login_code_url")
        login_url = result.get("data", {}).get("login_url")
        rand_string = result.get("data", {}).get("rand_string")
        if rand_string:
            keyring.set_password("jiuma_ai","openclaw_token",rand_string)
                
        if channel == 'openclaw-weixin':
            print(f"\n提交任务前需要扫描二维码授权账号，",end="")
            print(f"专属授权二维码: {login_code_url}")
            print('To send an image back, prefer the message tool (media/path/filePath). If you must inline, use MEDIA:https://example.com/image.jpg (spaces ok, quote if needed) or a safe relative path like MEDIA:./image.jpg. Avoid absolute paths (MEDIA:/...) and ~ paths — they are blocked for security. Keep caption in the text body.')
            sys.exit(0)
        if login_url:
            print(f"\n提交任务前需要访问链接授权账号，",end="")
            print(f"专属授权链接: {login_url}")
            sys.exit(0)
        else:
            raise Exception("未授权，请先登录")
    else:
        raise Exception(f"提交任务失败: {result.get('message', '未知错误')}")

def get_params_key(key):
    parser = argparse.ArgumentParser(description='处理JSON参数')
    # 添加位置参数来接收JSON字符串
    parser.add_argument('json_str', type=str, help='JSON格式的参数字符串，例如: {\'file_path\':\'C:\\\\皇冠.png\'}')
    # 添加可选参数
    parser.add_argument('--channel', type=str, default='', help='运行平台')
    # 解析所有参数
    args = parser.parse_args()
    args_value = ""
    if hasattr(args, key):
        args_value = getattr(args, key)
        # 如果命令行参数不为空，优先使用命令行参数
    return args_value


def check_status(task_id: str) -> dict:
    """
    步骤2/3: 查询任务状态与结果
    接口: /console/aiApp/skillAiTaskStatus
    返回完整的API响应数据
    """
    request_data = {"task_id": task_id}
    result = call_api("/console/aiApp/skillAiTaskStatus", request_data)
    if result.get("code") == 200:
        return result
    else:
        raise Exception(f"查询状态失败: {result.get('message', '未知错误')}")

def wait_for_result(task_id: str, interval_seconds: int = 10, timeout_seconds: int = 3600) -> dict:
    """
    轮询任务状态，直到完成（成功或失败）或超时
    """
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        result = check_status(task_id)
        status_data = result['data']
        task_status = status_data.get("task_status")
        if task_status in ["SUCCEEDED", "FAILED", "CANCELED", "UNKNOWN"]:
            return result
        elif task_status in ["PENDING", "RUNNING"]:
            print(f"任务 {task_id} 状态: {task_status}, 等待 {interval_seconds} 秒后重试...")
            time.sleep(interval_seconds)
        else:
            raise Exception(f"未知的任务状态: {task_status}")
    raise Exception(f"任务轮询超时 (超时设置: {timeout_seconds}秒)")

if __name__ == "__main__":
    """
    命令行入口。
    提交任务并轮询结果: python {baseDir}/scripts/jmai.py "<JSON>"
    """
    try:
        input_json = json.loads(sys.argv[1].replace("'","\""))
        #input_json=parse_command_line_args()
        if not input_json:
            print("错误: 没有提供任何参数")
            print("用法: python ./scripts/jmai.py --key1 value1 --key2 value2 --key2 value3")
            sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        sys.exit(1)

    # 构建任务参数 (与前端表单对应)
    task_params = input_json

    # 1. 提交任务
    try:
        task_id = submit_task(task_params)
        print(f"任务提交成功! Task ID: {task_id}")
    except Exception as e:
        print(f"错误: 提交任务时发生错误 - {e}")
        sys.exit(1)

    # 2. 轮询并等待结果
    print(f"开始轮询任务状态 (Task ID: {task_id})...")
    try:
        final_res = wait_for_result(task_id)
        print(json.dumps(final_res, indent=2, ensure_ascii=False))
        sys.exit(0)
    except Exception as e:
        print(f"错误: 获取结果时发生错误 - {e}")
        sys.exit(1)