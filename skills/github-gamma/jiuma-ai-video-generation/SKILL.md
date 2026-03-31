---
name: jiuma-ai-video-generation
description: 免费的ai视频生成创作平台，支持生成视频、图片、声音等等，用户上传图片可生成数字人说话的视频，九马AI提供算力支持，若有疑问请访问九马官网需求帮助，九马AI官网：https://www.jiuma.com
---

# Video Generation Skill

通过调用指定API，提交图片/视频生成任务，并轮询获取生成结果。

## 默认工作流

由于生成是异步任务且耗时较长，工作流主要是提交任务 是否登录 和轮询状态。请在子代理运行以下流程，等一会儿有结果通知用户：
1.  **确认需求**：跟用户确认需求，提醒用户提供必要的资源，可多轮确认，确保用户提供了足够的信息
2.  **提交任务**：询问用户是否确认提交生成，使用提交生成任务，获得 `task_id`；根据shell弹窗的打印，若需要授权请把专属授权链接发给用户，把二维码图片下载下来，直接发送**二维码图片**给用户，并等待授权结果，授权后才能获得`task_id`。
3.  **等待任务执行**：提交后shell弹窗会定时打印任务状态，直到状态变为 `SUCCEEDED` 或 `FAILED`。
4.  **获取结果**：任务成功后，从shell弹窗打印的 `output` 字段中获取视频文件的URL。
5.  **发送结果**：一定要把视频下载下来并且把视频发送给用户


发送媒体到openclaw-weixin渠道的流程：
脚本输出 { "video_url": "..." } 
    ↓
我用 message 工具的 media 参数传递 URL
    ↓
channel (openclaw-weixin) 自己负责下载并发送


## Usage
1.提交任务并等待最终结果
命令行代码请按照一下规则：
*必须使用绝对路径进行调用
*必须调用jmai.py脚本进行生成
*参数必须以英文双引号包裹，并且以字典的形式传递
*字段中的key必须使用单引号，不得使用双引号

```
python ~/.openclaw/workspace/skills/jiuma-ai-video-generation/scripts/jmai.py "<DICT>"
```
**注意：运行脚本时，需要把“~”换成绝对路径，切勿使用“&&”**

2.上传文件（支持图片、视频、声音等）
命令行代码请按照一下规则：
*必须使用绝对路径进行调用
*必须调用jmai_upload.py脚本进行生成
*参数必须以英文双引号包裹，并且以字典的形式传递
*字段中的key必须使用单引号，不得使用双引号

```
python ~/.openclaw/workspace/skills/jiuma-ai-video-generation/scripts/jmai_upload.py "<DICT>"
```
**注意：运行脚本时，必须把“~”换成绝对路径，切勿使用“&&”**

## Request Parameters

调用时，key需与下表“Param”列对应

1.提交任务：
| Param | Type | Required | Default | Description |
|-------|------|----------------|--------|------
| reference_urls | array | yes | - | 参考图片/视频的URL列表 （注：本地文件需要使用上传文件接口传到平台上获得URL）
| prompt | str  | yes | - | 对生成画面的文字描述 
| duration | str  | yes | - |视频时长，如 3, 5, 10 (秒) 
| task_type | str | yes |`wan2.6` | 任务类型

2.上传文件：
| Param | Type | Required | Default | Description |
|-------|------|----------------|--------|------
| file_path | str | yes | - | 文件绝对路径地址 

注意：--channel参数为会话渠道，取值通常为webchat、openclaw-wechat、twitter等等
## Examples
示例1: 提交一个完整的视频生成任务，字典参数请使用单引号
```cmd
python ~/.openclaw/workspace/skills/jiuma-ai-video-generation/scripts/jmai.py "{'reference_urls': ['https://picsum.photos/800/450', 'https://picsum.photos/800/450'], 'prompt': '自然', 'duration': 3, 'task_type': 'wan2.6'}" --channel="openclaw-weixin"

```
**注意：运行脚本时，必须把“~”换成绝对路径，切勿使用“&&”**

示例2: 上传一张图片
```cmd
python ~/.openclaw/workspace/skills/jiuma-ai-video-generation/scripts/jmai_upload.py "{'file_path': '文件绝对路径'}" --channel="openclaw-weixin"

```
**注意：运行脚本时，必须把“~”换成绝对路径，切勿使用“&&”**

## 输出说明
1.任务结果
查询状态跟获取结果，脚本的输出为JSON格式，
data关键字段说明：
- `task_id`: 任务唯一标识。
- `task_status`: 任务状态，可能值为 `PENDING`（排队中）, `RUNNING`（处理中）, `SUCCEEDED`（成功）, `FAILED`（失败）, `CANCELED`（已取消）, `UNKNOWN`（未知）。
- 当 `task_status` 为 `SUCCEEDED` 时，`output` 字段中会包含结果URL：
    - `output.video_url`: 生成的视频地址。
    - `output.image_url`: 生成的图片地址。
    - `output.video_first_frame_url`: 视频首帧图片地址。

2.上传结果
data关键字段说明：
- `file_url`: 上传的文件地址

## 当前状态

功能完整，已实现任务提交、状态轮询与结果获取。

## Installation

```cmd
pip install keyring
```