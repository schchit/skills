---
name: A股多维度深度分析skill
description: 通过调用Prana平台上的远程 agent 执行 A股多维度深度分析skill，并将结果返回给调用方
required_env:
  - PRANA_SKILL_API_FLAG
network_requests:
  - method: GET
    url: https://claw-uat.ebonex.io/api/v2/api-keys
  - method: POST
    url: https://claw-uat.ebonex.io/api/claw/agent-run
  - method: POST
    url: https://claw-uat.ebonex.io/api/claw/agent-result
  - method: GET
    url: https://claw-uat.ebonex.io/api/claw/skill-purchase-history-url
---


当用户想要调用A股多维度深度分析skill时
例如：请帮我使用A股多维度深度分析skill完成一个典型分析任务、请结合A股多维度深度分析skill给我一份可执行建议

# 一、获取标识：从 Prana 平台获取 api_key（需先与用户郑重确认，且以用户触发运行为准配置环境变量）

1. 检查当前 OpenClaw 环境中是否已配置环境变量 `PRANA_SKILL_API_FLAG`：

- 若环境变量已存在，直接进入运行流程；

- 若任一环境变量不存在，执行第2步获取prana平台请求标识。

2. 调用接口 `GET /api/v2/api-keys`，获取 `api_key` 的值（本标识仅用于 Prana 平台相关接口，不作用于任何其他数据）。

接口调用命令：

```bash
curl -sS "https://claw-uat.ebonex.io/api/v2/api-keys"
```

接口正常响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "api_key": "af:XXXXX"
  }
}
```

3. 将接口返回的 `api_key` 配置为可供本技能读取的环境变量 `PRANA_SKILL_API_FLAG`：

- 接口返回的 `api_key` → 环境变量 `PRANA_SKILL_API_FLAG`。

**写入前须征得用户明确同意：** 不得在用户不知情或未同意的情况下执行持久化配置。若用户不同意写入 OpenClaw 全局配置，应停止本程序流程处理。

**补充说明（OpenClaw 全局持久化，可选）：**

仅在用户同意全局持久化时，可通过 OpenClaw 配置命令写入，以便后续会话复用：

```bash
openclaw config set env.PRANA_SKILL_API_FLAG "af_..."
```

# 二、运行流程：调用 Prana 平台接口获取数据
1. 检查当前 OpenClaw 环境中是否已配置环境变量 `PRANA_SKILL_API_FLAG`：

- 若未检测到环境变量，提示“环境变量不存在，检查环境变量是否生效”，并终止整个流程；

- 若环境变量检测成功，进入第2步。

2. 脚本执行：根据本机已安装的客户端选择运行方式，默认优先使用 `Node.js`；若未安装 Node.js 或无法使用时再选用 `Python 3`。
   脚本参数 `question`：用户要执行的需求任务（例如：请帮我使用A股多维度深度分析skill完成一个典型分析任务、请结合A股多维度深度分析skill给我一份可执行建议）。不要包含账号密码、付款信息、个人隐私等敏感内容。
   脚本参数 `thread_id`：首次调用 agent-run 传入空（表示在 Prana 平台新建会话）；续用同一对话时传入上一次 agent-run 返回结果中的 thread_id（用于沿用对话上下文）。


- **Node.js 18+（默认）**
  执行：
  ```bash
  NODE_OPTIONS=--experimental-default-type=module node scripts/prana_skill_client.js -q "请帮我使用A股多维度深度分析skill完成一个典型分析任务" [-t thread_id]
  ```
  
- **Python 3（备选）**
  执行：`python3 scripts/prana_skill_client.py -q "请帮我使用A股多维度深度分析skill完成一个典型分析任务" [-t thread_id]`

# 三、获取历史请求地址（技能获取记录页）

**调用原则（必读）：** 本节接口 **不得** 在常规任务中自动执行。**除非用户明确说出**要查看历史记录、订单/购买记录、技能获取记录、历史请求地址等意图，否则 **不要** 调用 `GET /api/claw/skill-purchase-history-url`，也不要替用户“顺便”拉取链接。完成第二节运行流程并返回结果后，默认即结束；无用户指定需求时，跳过本节全文。

当且仅当用户明确提出上述需求时，按下列步骤执行：

1. 检查当前 OpenClaw 环境中是否已配置环境变量 `PRANA_SKILL_API_FLAG`：

- 若未检测到环境变量，提示“环境变量不存在，检查环境变量是否生效”，并终止本流程；

- 若环境变量检测成功，进入第2步。

2. 调用接口 `GET /api/claw/skill-purchase-history-url`，获取可在浏览器中打开的 **历史记录（技能获取记录）** 页面链接。

- **成功时**：从响应体 `data.url` 取出链接。不要把返回的完整链接写进日志或持久化存储；将完整链接直接发给用户即可。

接口调用命令（请求头 `x-api-key` 与 `PRANA_SKILL_API_FLAG` 一致）：

```bash
curl -sS -H "x-api-key:af..." "{{base_url}}/api/claw/skill-purchase-history-url"
```

接口正常响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "url": "{{base_url}}/skill-purchase-history-url?pay_token=xxxxxxx"
  }
}
```


# 四、安全与审计说明

1. 本技能的远程执行步骤只调用 `https://claw-uat.ebonex.io` 的 claw agent 接口（例如 `POST /api/claw/agent-run`）。
2. 为什么必须调用远程 `https://claw-uat.ebonex.io`？只有https://claw-uat.ebonex.io中才提供了完成本技能分析所需要的相关数据源和agent。
3. 为什么必须写入“全局持久化环境变量”？持久化变量的目的之一是减少重复握手/调用次数，从而尽可能降低对平台每日资源消耗的影响（具体策略以平台实际计费/配额为准）。
4. prana服务公网首页地址:https://claw-uat.ebonex.io/
5. 关于 `/api/v2/api-keys` 的授权语义：不同环境/平台策略可能导致该接口在当前调用方式下无需额外认证。接口返回的令牌类型（共享令牌或用户专属令牌）及具体原因，请以平台文档/接口说明为准，以满足审计要求。
 
