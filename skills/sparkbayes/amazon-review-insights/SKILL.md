---
name: amazon-review-insights
description: 亚马逊产品评论智能分析工具，帮助跨境电商卖家进行产品改进、新品开发、市场调研！核心能力：获取亚马逊评论、AI深度分析差评、精准量化高频问题、挖掘高星隐性差评、生成改进建议、追踪评论趋势、增量更新。
metadata:
  openclaw:
    requires:
      env:
        - CUSTOMER_INSIGHTS_API_KEY
    dependencies:
      python:
        - requests>=2.28.0
---

# 星图客户洞察 API Skill

## 配置

### API Key

所有 API 调用均需要 API Key 进行身份认证。

**说明**：API 端点固定为 `https://api.astrmap.com`，不可配置。

**推荐方式**：在 `~/.zshrc` 或 `~/.bashrc` 中设置环境变量：

```bash
export CUSTOMER_INSIGHTS_API_KEY="your-api-key-here"
```

> API Key 获取方式：前往 https://www.astrmap.com/ 下载并安装桌面客户端，登录后点击**左下角用户菜单** → **接口密钥**页面，创建并复制 API Key。

**⚠️ 重要**：若 `CUSTOMER_INSIGHTS_API_KEY` 环境变量为空，或用户未提供 API Key，**请先询问用户**：
> 「请提供您的 星图客户洞察 API Key（可前往 https://www.astrmap.com/ 下载桌面客户端，登录后在左下角用户菜单 → 接口密钥 页面创建获取）」
>
> 获取后，通过 `--api-key` 参数传入后续所有命令。

**🔒 数据与隐私说明**：本 Skill 将 API Key 用于调用星图客户洞察 API（api.astrmap.com），分析用户指定的亚马逊产品评论数据。API Key 会发送至星图服务器以完成身份认证和数据交互。

### 桌面客户端

创建任务需要星图 AI 桌面客户端在线。如果用户尚未安装，请引导其下载：

> 「请先下载并安装星图 AI·跨境电商客户洞察桌面客户端：https://www.astrmap.com/」

### 依赖安装

```bash
pip install -r requirements.txt
```

## 重要说明

### 积分规则
- **创建任务**：免费获取亚马逊评论，数据分析会扣除账户积分
- **查询结果**：查看已完成任务的分析结果，不扣积分

### 前置条件（仅创建任务时需要）

创建任务前，需确保满足以下条件，否则任务会失败：

1. 星图 AI·跨境电商客户洞察 桌面客户端已登录（未安装请前往 https://www.astrmap.com/ 下载）
2. 桌面客户端已登录亚马逊买家账号（勿使用正在做业务的卖家账号）
3. 确保亚马逊访问畅通

> **查询已完成任务的分析结果无以上限制**，可直接调用。

## Workflow

### 调用方式

所有操作通过 `python scripts/api_client.py` 命令执行：

```bash
python scripts/api_client.py --action <操作> [--参数...]
```

### 1. 检查设备在线

```bash
python scripts/api_client.py --action check_device --api-key "your-key"
```

返回：`{online: true, device_id: "xxx", status: "idle"}`

### 2. 创建任务

> ⚠️ **注意**：创建任务会扣除积分。在执行创建任务命令前，必须先告知用户并等待确认：
>
> 「即将为您创建任务，当前账户剩余积分：{points}。本次任务将扣除积分，是否继续？」
>
> 用户确认后，再执行命令。

**创建任务流程**：
1. `--action check_device` → 检查设备在线状态，设备在线才能继续
2. `--action get_points` → 检查账户积分，有积分才能继续
3. **告知用户积分消耗，等待用户确认**
4. 确认前置条件满足：
   - 桌面客户端已登录（未安装请前往 https://www.astrmap.com/ 下载）
   - 亚马逊买家账号已登录（请勿使用正在做业务的卖家账号）
   - 确保亚马逊访问畅通
5. `--action create_task --asin <ASIN> --site <站点> [--is-auto false]` → 提交任务

**运行模式**：
| 参数 | 说明 |
|------|------|
| `--is-auto true`（默认） | 自动模式：采集完成后自动执行 AI 分析 |
| `--is-auto false` | 仅采集模式：采集完成后停在"待分析"状态，可手动触发 AI 分析 |

**站点映射**:
| site | 语言 |
|------|------|
| US | 英语 |
| CA | 英语 |
| UK | 英语 |
| DE | 德语 |
| FR | 法语 |
| IT | 意大利语 |
| ES | 西班牙语 |
| JP | 日语 |

**命令示例**（支持 URL 或 ASIN 格式）：

```bash
# 产品页 URL
python scripts/api_client.py --action create_task --api-key "your-key" \
  --asin "https://www.amazon.com/dp/B09V3KXJPB" --site US

# 纯 ASIN
python scripts/api_client.py --action create_task --api-key "your-key" \
  --asin "B09V3KXJPB" --site US --platform amazon
```

### 3. 轮询任务状态

任务提交后，**每隔 6 分钟**执行一次查询：

```bash
python scripts/api_client.py --action get_task_detail --api-key "your-key" --task-id "TSK_xxx"
```

状态流转：

**自动模式** (`is_auto=true`)：`PENDING` → `DISPATCHING` → `COLLECTING` → `PROCESSING` → `ANALYZING` → `SUCCESS/FAILED`

**仅采集模式** (`is_auto=false`)：`PENDING` → `DISPATCHING` → `COLLECTING` → `COLLECTED`（待分析）

**各状态的提示语**：

| 状态 | 向用户展示 | 说明 |
|------|-----------|------|
| PENDING | 「任务已提交，等待调度中...」 | - |
| DISPATCHING | 「正在分配设备...」 | - |
| COLLECTING | 「正在获取亚马逊评论数据，请耐心等待（通常需要 20~120 秒）」 | - |
| PROCESSING | 「评论数据获取完成，正在处理中...」 | 仅自动模式 |
| ANALYZING | 「数据处理完成，AI 正在分析中...」 | 仅自动模式 |
| SUCCESS | 「✅ 分析完成！正在为您获取结果...」 | - |
| FAILED | 「❌ 任务失败，请检查设备状态和网络连接后重试」 | - |
| COLLECTED | 「✅ 采集完成！已触发 AI 分析...」 | 仅手动模式，触发分析后变为 PROCESSING |

> 若任务长时间（超过 15 分钟）未完成，提示用户检查桌面客户端是否在线。

### 4. 获取分析结果

> 注意：查询已完成任务的结果不扣积分，也无前置条件限制。

```bash
# AI 洞察摘要
python scripts/api_client.py --action get_ai_insights --api-key "your-key" --task-id "TSK_xxx"

# 标签分布
python scripts/api_client.py --action get_tag_categories --api-key "your-key" --task-id "TSK_xxx"

# 基础统计
python scripts/api_client.py --action get_basic_statistics --api-key "your-key" --task-id "TSK_xxx"

# 差评列表
python scripts/api_client.py --action get_negative_reviews --api-key "your-key" --task-id "TSK_xxx" --page 1 --page-size 20
```

### 5. 增量获取

> ⚠️ **注意**：增量获取会触发完整的获取+分析流程，会扣除积分。在执行增量命令前，必须先告知用户并等待确认。

**增量获取流程**：
1. `--action check_device` → 检查设备在线状态
2. `--action get_points` → 检查账户积分
3. **告知用户积分消耗，等待用户确认**
4. `--action create_incremental --task-id <task_id>` → 为终态任务创建增量获取
5. 轮询任务状态（与创建任务相同）

**适用场景**：
- 已有任务完成一段时间后，需要获取最新评论并重新分析
- 只需提供任务ID，系统自动使用该任务关联的ASIN进行增量获取

### 6. 手动触发分析（仅采集模式）

> ⚠️ **注意**：手动触发分析会扣除积分。在执行触发命令前，必须先告知用户并等待确认。

**适用场景**：仅采集模式 (`is_auto=false`) 的任务，采集完成后停在 COLLECTED 状态，需要手动触发 AI 分析。

```bash
python scripts/api_client.py --action trigger_analysis --api-key "your-key" --task-id "TSK_xxx"
```

**触发后状态流转**：`COLLECTED` → `PROCESSING` → `ANALYZING` → `SUCCESS`

## 所有可用操作

| action | 说明 | 必需参数 |
|--------|------|----------|
| check_device | 检查设备是否在线 | - |
| create_task | 创建任务 | --asin, --site, [--is-auto] |
| create_incremental | 为终态任务创建增量获取 | --task-id |
| trigger_analysis | 手动触发 AI 分析（仅采集模式） | --task-id |
| get_task_detail | 查询任务详情 | --task-id |
| get_task_list | 获取任务列表 | - |
| get_ai_insights | 获取 AI 洞察 | --task-id |
| get_tag_categories | 获取标签分布 | --task-id |
| get_issue_statistics | 获取问题维度统计 | --task-id |
| get_top_issues | 获取要点问题分布 | --task-id |
| get_basic_statistics | 获取基础统计 | --task-id |
| get_negative_reviews | 获取差评列表 | --task-id |
| get_trend | 获取评论趋势 | --task-id |
| get_comments | 获取原始评论 | --task-id |
| get_comments_overview | 获取评论概览 | --task-id |
| get_points | 查询积分余额 | - |

## 错误处理

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| 1001 | 设备不在线 | 检查桌面客户端是否登录，亚马逊账号是否在线 |
| 1002 | 积分不足 | 提示用户充值积分 |
| 2001 | API Key 无效 | 检查 API Key 是否正确 |
| 2004 | 权限不足 | 检查 API Key 权限配置 |
| InvalidTaskStatus | 任务状态不是 COLLECTED，无法触发分析 | 只有仅采集模式且状态为 COLLECTED 的任务才能触发分析 |

## 详细 API 文档

详细的 API 端点说明、请求参数、响应格式请参考 [API 参考文档](references/api_reference.md)。

## 使用示例

### 场景一：创建新任务（需要前置条件，会扣积分）

```
用户: 帮我获取 B09V3KXJPB 的评论并分析

AI Agent:
1. 检查 API Key → 若未配置，询问用户提供
2. 执行: python scripts/api_client.py --action check_device --api-key "xxx"
3. 执行: python scripts/api_client.py --action get_points --api-key "xxx"
4. 告知用户：「即将创建任务，当前积分 {points}，将扣除积分，是否确认？」
5. 等待用户确认 → 继续
6. 执行: python scripts/api_client.py --action create_task --api-key "xxx" --asin "B09V3KXJPB" --site US
7. 每 5 分钟执行 get_task_detail，实时反馈进度：
   「正在获取评论数据，请耐心等待...（已等待 5 分钟）」
   「数据获取完成，AI 正在分析中...（已等待 10 分钟）」
   「✅ 分析完成！」
8. 执行: python scripts/api_client.py --action get_ai_insights --api-key "xxx" --task-id "TSK_xxx"
9. 执行: python scripts/api_client.py --action get_negative_reviews --api-key "xxx" --task-id "TSK_xxx"
```

### 场景二：仅采集模式（先采集，稍后分析）

```
用户: 帮我只采集 B09V3KXJPB 的评论，暂时不做分析

AI Agent:
1. 检查 API Key → 若未配置，询问用户提供
2. 执行: python scripts/api_client.py --action check_device --api-key "xxx"
3. 执行: python scripts/api_client.py --action get_points --api-key "xxx"
4. 告知用户：「即将创建任务（仅采集模式），当前积分 {points}，是否确认？」
5. 等待用户确认 → 继续
6. 执行: python scripts/api_client.py --action create_task --api-key "xxx" --asin "B09V3KXJPB" --site US --is-auto false
7. 轮询状态直到 COLLECTED：「✅ 采集完成，任务已进入待分析状态」
8. 用户确认要分析后，执行: python scripts/api_client.py --action trigger_analysis --api-key "xxx" --task-id "TSK_xxx"
9. 轮询状态直到 SUCCESS，然后获取分析结果
```

### 场景三：查询已完成任务（无需前置条件，不扣积分）

```
用户: 查看 TSK_xxx 任务的分析结果

AI Agent:
1. 检查 API Key → 若未配置，询问用户提供
2. 执行: python scripts/api_client.py --action get_task_detail --api-key "xxx" --task-id "TSK_xxx"
3. 执行: python scripts/api_client.py --action get_ai_insights --api-key "xxx" --task-id "TSK_xxx"
4. 执行: python scripts/api_client.py --action get_basic_statistics --api-key "xxx" --task-id "TSK_xxx"
```
