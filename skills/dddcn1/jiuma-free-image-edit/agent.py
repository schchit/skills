#!/usr/bin/env python3
"""
九马AI图片编辑工具
输入提示词和图片，编辑图片并返回URL
"""
import argparse
import json
import os.path
from pathlib import Path
import requests

SUBMIT_API = "https://api.jiuma.com/api/imageEdit/add"
CHECK_STATUS_API = "https://api.jiuma.com/api/imageEdit/status"

MIME_MAP = {
    # 图片
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.jpe': 'image/jpeg',
    '.jfif': 'image/jpeg',
    '.pjpeg': 'image/jpeg',
    '.pjp': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.bmp': 'image/bmp',
    '.webp': 'image/webp',
    '.svg': 'image/svg+xml',
    '.svgz': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.tiff': 'image/tiff',
    '.tif': 'image/tiff',
    '.heic': 'image/heic',
    '.heif': 'image/heif',
    '.avif': 'image/avif',
    '.apng': 'image/apng',
}


def output_result(json_data):
    """输出JSON格式结果"""
    print(json.dumps(json_data, ensure_ascii=False, indent=2))


def get_image_param(image_str, image_key_name='image1', request_data=None, image_files=None):
    if not image_str:
        return request_data, image_files
    ext = Path(image_str).suffix.lower()
    if ext not in MIME_MAP:
        return request_data, image_files
    if image_str.startswith(('http://', 'https://', 'ftp://', '//')) or '://' in image_str or image_str.startswith('www.'):
        request_data[f"{image_key_name}_url"] = image_str
    elif os.path.exists(image_str):
        print(f"content_type: {MIME_MAP[ext]}")
        f = open(image_str, 'rb')
        image_files[f"{image_key_name}_file"] = (os.path.basename(image_str), f, MIME_MAP[ext])

    return request_data, image_files


def submit_image_edit(text, image1, image2, image3):
    """
    返回结构
    status: 状态
    message: 返回消息
    data: 数据结构体
    task_id: 任务ID(根据此任务ID查询制作进度)
    示例
    {
      "status": "success",
      "message": "图片编辑任务提交成功",
      "data": {
        "task_id": "202603263844232132"
      }
    }
    """
    if not text:
        output_result({
            "status": "error",
            "message": "请输入编辑图片的描述",
            "data": {}
        })
        return

    if not image1:
        output_result({
            "status": "error",
            "message": "请输入需要编辑的图片",
            "data": {}
        })
        return

    # 1. 提交生成请求
    request_data = {
        "tips": text,
    }
    image_files = {}
    # 获取第一张图片
    request_data, image_files = get_image_param(image1, 'image1', request_data, image_files)
    # 获取第二张图片
    request_data, image_files = get_image_param(image2, 'image2', request_data, image_files)
    # 获取第三张图片
    request_data, image_files = get_image_param(image3, 'image3', request_data, image_files)
    print(image_files)
    try:
        if image_files:
            response = requests.post(SUBMIT_API, request_data, files=image_files, timeout=30)
            for key in image_files:
                image_files[key][1].close()
        else:
            response = requests.post(SUBMIT_API, request_data, timeout=30)
        if response.status_code != 200:
            output_result({
                "status": "error",
                "message": f"请求远程API失败，状态码: {response.status_code}",
                "data": {}
            })
            return

        json_result = response.json()

        # 检查API返回结构 - 根据实际返回的JSON结构调整
        # API返回格式: {"code": 200, "message": "成功", "data": {"task_id": "xxx"}}
        if json_result.get("code") != 200:
            output_result({
                "status": "error",
                "message": f"API返回错误: {json_result.get('message', '未知错误')}",
                "data": json_result
            })
            return

        task_id = json_result.get("data", {}).get("task_id")

        if not task_id:
            output_result({
                "status": "error",
                "message": "API未返回任务ID",
                "data": json_result
            })
            return

        output_result({
            "status": "success",
            "message": "图片编辑任务提交成功",
            "data": {
                "task_id": task_id,
                "text": text,
                "image1": image1,
                "image2": image2,
                "image3": image3
            }
        })
        return
    except requests.exceptions.Timeout:
        output_result({
            "status": "error",
            "message": "请求超时，请检查网络连接",
            "data": {}
        })
        return
    except requests.exceptions.RequestException as e:
        output_result({
            "status": "error",
            "message": f"请求异常: {str(e)}",
            "data": {}
        })
        return
    except json.JSONDecodeError as e:
        output_result({
            "status": "error",
            "message": f"API返回格式错误: {str(e)}",
            "data": {}
        })
        return


def check_task_status(task_id):
    """
    返回结构
    status: 处理结果，success|pending|running|failed
    message: 返回消息
    data: 数据结构体
    task_id: 任务ID
    image_url: 图片链接(如status为success)
    示例
    {
      "status": "success",
      "message": "图片编辑成功",
      "data": {
        "image_url": "https://cache.jiuma.com/static/uploads/20260326/69c4cc01222e1.png",
        "task_id": "20260326486039013"
      }
    }
    """
    if not task_id:
        output_result({
            "status": "error",
            "message": "任务ID不能为空",
            "data": {}
        })
        return None

    try:
        task_response = requests.post(CHECK_STATUS_API, {"task_id": task_id}, timeout=30)
        if task_response.status_code != 200:
            output_result({
                "status": "error",
                "message": f"请求远程API失败，状态码: {task_response.status_code}",
                "data": {}
            })
            return None

        task_detail = task_response.json()

        # 检查API返回状态 - 根据实际返回的JSON结构调整
        if task_detail.get("code") != 200:
            output_result({
                "status": "error",
                "message": f"API返回错误: {task_detail.get('message', '未知错误')}",
                "data": task_detail
            })
            return None

        data = task_detail.get("data", {})
        task_status = data.get("task_status", "").upper()

        if task_status == 'SUCCEEDED':
            image_url = data.get('image_url')
            if not image_url:
                output_result({
                    "status": "error",
                    "message": "API未返回图片URL",
                    "data": data
                })
                return None

            output_result({
                "status": "success",
                "message": "图片生成成功",
                "data": {
                    "image_url": image_url,
                    "task_id": task_id,
                    "download_link": image_url
                }
            })
        elif task_status == 'PENDING':
            output_result({
                "status": "pending",
                "message": "图片编辑任务排队中，请耐心等待",
                "data": {
                    "task_id": task_id,
                    "status": "pending"
                }
            })
        elif task_status == 'RUNNING':
            output_result({
                "status": "pending",
                "message": "图片编辑任务执行中，请耐心等待",
                "data": {
                    "task_id": task_id,
                    "status": "running"
                }
            })
        else:
            output_result({
                "status": "failed",
                "message": f"图片生成失败: {task_detail.get('message', '未知错误')}",
                "data": {
                    "task_id": task_id,
                    "status": "failed"
                }
            })
    except requests.exceptions.Timeout:
        output_result({
            "status": "error",
            "message": "请求超时，请检查网络连接",
            "data": {
                "task_id": task_id
            }
        })
        return None
    except requests.exceptions.RequestException as e:
        output_result({
            "status": "error",
            "message": f"请求异常: {str(e)}",
            "data": {
                "task_id": task_id
            }
        })
        return None
    except json.JSONDecodeError as e:
        output_result({
            "status": "error",
            "message": f"API返回格式错误: {str(e)}",
            "data": {
                "task_id": task_id
            }
        })
        return None
    except Exception as e:
        output_result({
            "status": "error",
            "message": f"未知错误: {str(e)}",
            "data": {
                "task_id": task_id
            }
        })
        return None


def main():
    parser = argparse.ArgumentParser(description="九马AI免费图片编辑工具",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # 主要参数组
    parser.add_argument('--text', type=str, default="", help="图片编辑提示词，对图片需要改动的描述")
    parser.add_argument('--image1', type=str, default='', help="需要编辑的主图")
    parser.add_argument('--image2', type=str, default='', help="图片二")
    parser.add_argument('--image3', type=str, default='', help="图片三")
    parser.add_argument('--task_id', type=str, default='', help="图片编辑执行任务ID")

    # 操作参数
    parser.add_argument('--check', action='store_true', help="检查生成状态")
    parser.add_argument('--submit', action='store_true', help="提交图片编辑制作")

    args = parser.parse_args()

    if args.submit:
        submit_image_edit(args.text, args.image1, args.image2, args.image3)
    elif args.check:
        check_task_status(args.task_id)
    else:
        print("""
九马AI免费图片编辑工具 v1.0
==========================

使用方法:
1. 提交图片编辑任务:
python3 agent.py --submit --text "图1中角色的衣服换成中式秀禾服" --image1 /data/test.png

2. 查询任务状态:
   python3 agent.py --check --task_id "任务ID"

参数说明:
--submit        提交图片编辑任务
--text          图片编辑的描述文本（必需）
--image1        需要被编辑的主图（必需）
--image2        参考图片
--image3        第二张参考图片
--check         查询任务生成状态
--task_id       任务ID（与--check一起使用）

示例:
单图编辑
python3 agent.py --submit --text "图1中角色的衣服换成中式秀禾服" --image1 /data/image1.png
图片融合
python3 agent.py --submit --text "将图片2的首饰戴着图片1的手上" --image1 /data/test1.png --image2 https://example.com/test.png
python3 agent.py --check --task_id "202603263844232132"

注意:
- 输出图片的最大尺寸为832x832
- 图片生成可能需要等待，请使用--check参数查询状态
- 生成的图片URL可以直接在浏览器中打开下载
        """.strip())


if __name__ == '__main__':
    main()
