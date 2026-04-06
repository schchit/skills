---
name: A股财务分析
description: 通过调用Prana平台上的远程 agent 完成以下处理： 使用7步分析法对中国A股进行全方位财务分析，自动生成包含ROE分解、盈利模式识别、行业对比和投资洞察的HTML报告。支持上海和深圳交易所所有股票。
required_env:
  - PRANA_SKILL_API_FLAG
required_env_note: >
  运行随附客户端脚本前须已设置 PRANA_SKILL_API_FLAG；脚本不会调用 GET /api/v2/api-keys。
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


技能使用场景:在投研场景中快速诊断A股公司财务健康度与盈利模式
例如：请用7步分析法分析贵州茅台的财务状况、生成宁德时代最新的A股财务分析HTML报告

# 一、获取标识：从 Prana 平台获取 api_key（需先与用户郑重确认，且以用户触发运行为准配置环境变量）

1. 运行命令检查当前 OpenClaw 环境中是否已配置环境变量 `PRANA_SKILL_API_FLAG`：
```bash
env | grep PRANA_SKILL_API_FLAG
```

- 若环境变量已存在，结束获取标识处理，直接进入二、运行流程；

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

**写入前须征得用户明确同意：** 不得在用户不知情或未同意的情况下执行持久化配置。若用户不同意写入 OpenClaw 全局配置，应停止本技能流程处理。

**补充说明（OpenClaw 全局持久化，可选）：**

仅在用户同意全局持久化时，可通过 OpenClaw 配置命令写入，以便后续会话复用：

```bash
openclaw config set env.PRANA_SKILL_API_FLAG "af_..."
```

# 二、运行流程：调用 Prana 平台接口获取数据
1. 运行命令检查当前 OpenClaw 环境中是否已配置环境变量 `PRANA_SKILL_API_FLAG`：

```bash
env | grep PRANA_SKILL_API_FLAG
```

- 若未检测到环境变量，提示“环境变量不存在，检查环境变量是否生效”，并终止整个流程；

- 若环境变量检测成功，进入第2步。

2. 脚本执行：根据本机已安装的客户端选择运行方式，默认优先使用 `Node.js`；若未安装 Node.js 或无法使用时再选用 `Python 3`。**禁止**在 `node` / `python3` 命令前使用 `PRANA_SKILL_API_FLAG="…"` 与反斜杠换行等形式设置环境变量或者把密钥写进同一条终端命令。
   脚本参数 `-q`：用户要执行的需求任务（例如：请用7步分析法分析贵州茅台的财务状况、生成宁德时代最新的A股财务分析HTML报告）。不要包含账号密码、付款信息、个人隐私等敏感内容。

- **Node.js 18+（默认）**
  执行发起任务调度（**禁止**在命令附带使用 `PRANA_SKILL_API_FLAG="…"` 等形式把设置环境变量写进同一行终端命令一起执行）：
  ```bash
  NODE_OPTIONS=--experimental-default-type=module node scripts/prana_skill_client.js -q "请用7步分析法分析贵州茅台的财务状况"
  ```

- **Python 3（备选）**
  执行（**禁止**在命令前使用 `PRANA_SKILL_API_FLAG="…"` 等形式把设置环境变量写进同一行终端命令一起执行）：
  ```bash
  python3 scripts/prana_skill_client.py -q "请用7步分析法分析贵州茅台的财务状况"
  ```

3. **向用户输出脚本结果时的提示（必读）：**

   3.1 **链接呈现：** 将脚本返回的内容展示或转发给用户时，若其中包含 **网页链接（URL）**，应优先使用 **用户可直接点击即可打开浏览器** 的呈现方式（例如 Markdown 链接 `[说明文字](https://...)`，或所在客户端会自动把 `https://...` 识别为可点击超链接的格式），**避免**只给一段不可点的纯文本长链，让用户不得不手动复制再粘贴到地址栏。

   3.2 **预期内 JSON：** 若输出为形如 `{"code":XXX,"message":XXXXX}` 的 JSON，表示服务端 **预期内** 的返回（成功与失败均属预期），将结果展示给用户即可，**由用户决定** 后续如何处理。**不得**私自替用户“纠错”，例如提示需付费时仍反复重新获取 `api_key`、改环境变量或重复跑脚本等。

   3.3 **达到尝试上限：** 若输出内容匹配或包含 **「提示: 本轮尝试已达到上限」** 及后续说明（如具体上限数字、原因等），须 **询问用户** 是否继续尝试以获取相应结果；若用户同意继续，须 **严格按照** 该提示中给出的命令或步骤执行，不得擅自省略、替换或合并。

# 三、获取历史请求地址（技能获取记录页）

**调用原则（必读）：** 本节接口 **不得** 在常规任务中自动执行。**除非用户明确说出**要查看历史记录、订单/购买记录、技能获取记录、历史请求地址等意图，否则 **不要** 调用 `GET /api/claw/skill-purchase-history-url`，也不要替用户“顺便”拉取链接。完成第二节运行流程并返回结果后，默认即结束；无用户指定需求时，跳过本节全文。

当且仅当用户明确提出上述需求时，按下列步骤执行：

1. 运行命令检查当前 OpenClaw 环境中是否已配置环境变量 `PRANA_SKILL_API_FLAG`：

```bash
env | grep PRANA_SKILL_API_FLAG
```

- 若未检测到环境变量，提示“环境变量不存在，检查环境变量是否生效”，并终止本流程；

- 若环境变量检测成功，进入第2步。

2. 调用接口 `GET /api/claw/skill-purchase-history-url`，获取可在浏览器中打开的 **历史记录（技能获取记录）** 页面链接。

- **成功时**：从响应体 `data.url` 取出链接。不要把返回的完整链接写进日志或持久化存储；将链接以 **用户可直接点击打开** 的形式发给用户（与第二节第 3.1 点链接呈现要求一致），勿仅输出需手动复制的纯文本长链。
接口调用命令（请求头 `x-api-key` 与 `PRANA_SKILL_API_FLAG` 一致）：

```bash
curl -sS -H "x-api-key:af..." "https://claw-uat.ebonex.io/api/claw/skill-purchase-history-url"
```

接口正常响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "url": "https://claw-uat.ebonex.io/skill-purchase-history-url?pay_token=xxxxxxx"
  }
}
```

# 四、安全与审计说明

1. 本技能的远程执行步骤只调用 `https://claw-uat.ebonex.io` 的 claw agent 接口（例如 `POST /api/claw/agent-run`）。
2. 为什么必须调用远程 `https://claw-uat.ebonex.io`？只有https://claw-uat.ebonex.io中才提供了完成本技能分析所需要的相关数据源和agent。
3. 为什么必须写入“全局持久化环境变量”？持久化变量的目的之一是减少重复握手/调用次数，从而尽可能降低对平台每日资源消耗的影响（具体策略以平台实际计费/配额为准）。
4. prana服务公网首页地址:https://claw-uat.ebonex.io/
5. **`required_env` 与取钥（审计）**：`skill.json` 声明 `PRANA_SKILL_API_FLAG` 为必需，含义是**运行随附 `scripts/prana_skill_client.py` / `prana_skill_client.js` 时**该环境变量必须已存在；随附脚本**不会**实现 `GET /api/v2/api-keys`，也不会在缺变量时自动取 token。缺钥时须由宿主（助手/集成方）按第一节取得 `data.api_key` 并写入环境变量后再执行脚本。该 GET 接口在当前环境下是否需额外认证、返回令牌为共享或用户专属，以平台文档为准。

