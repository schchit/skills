---
name: lark-project-meegle
description: 连接飞书项目/Meegle，查询和管理工作项、待办等。自动检测登录状态，未登录时引导 Device Code 授权。
version: 0.1.1
homepage: https://www.npmjs.com/package/@lark-project/meegle
metadata:
  openclaw:
    homepage: https://www.npmjs.com/package/@lark-project/meegle
    emoji: 📋
    requires:
      bins:
        - node
        - npx
    install:
      - kind: node
        package: "@lark-project/meegle"
        bins:
          - meegle
---

# Meegle SKILL

通过 Meegle CLI 连接飞书项目/Meegle 平台，支持查询工作项、管理待办等操作。

## 前置条件

运行环境需要 Node.js 18+。所有命令通过 `npx @lark-project/meegle@beta` 执行，无需手动安装或更新。

## Auth Guard（所有业务命令前必须执行）

按以下 STEP 顺序执行。每个 STEP 结尾的 GOTO 指明下一步，严格遵循跳转。

---

### STEP 1 — 检查登录状态

```bash
npx @lark-project/meegle@beta auth status --format json
```

返回值示例：
- 已登录：`{ "authenticated": true, "host": "meegle.com", "source": "token_store", "expires_in_minutes": 42 }`
- 未登录且有 host：`{ "authenticated": false, "host": "meegle.com", "source": null, "expires_in_minutes": null }`
- 未登录且无 host：`{ "authenticated": false, "host": null, "source": null, "expires_in_minutes": null }`

解析返回值，保存变量：
- `$authenticated` = response.authenticated
- `$host` = response.host

**跳转：**
- IF `$authenticated == true` → GOTO STEP 6
- IF `$host != null` → GOTO STEP 3
- IF `$host == null` → GOTO STEP 2

---

### STEP 2 — 选择站点

ASK user（等待用户回复）：

> 你要连接哪个站点？
> 1) 飞书项目 (project.feishu.cn)
> 2) Meegle (meegle.com)
> 3) 自定义域名（请直接输入域名）

SAVE `$host` from user reply → GOTO STEP 3

---

### STEP 3 — 初始化 Device Code

```bash
npx @lark-project/meegle@beta auth login --device-code --phase init --host $host --format json
```

SAVE from response：
- `$verification_uri_complete` = response.verification_uri_complete
- `$user_code` = response.user_code
- `$device_code` = response.device_code
- `$client_id` = response.client_id
- `$interval` = response.interval
- `$expires_in` = response.expires_in
- `$max_attempts` = floor($expires_in / $interval)

**发送验证链接给用户：**

IF channel == "feishu" OR channel == "lark"（参考 Runtime metadata 中的 `channel=` 字段）:
- SEND 消息卡片（如果当前 channel 支持卡片格式）：
  - 标题: "Meegle 授权登录"
  - 内容: 验证码 `$user_code`，有效期 `$expires_in` 秒
  - 按钮: "打开授权页面" → `$verification_uri_complete`
  - 如果不支持卡片，回退到下方纯文本格式

ELSE:
- SEND to user: `请在浏览器中打开以下链接完成授权：\n$verification_uri_complete\n验证码：$user_code（$expires_in 秒内有效）`

> ⚠️ 发送后立即 GOTO STEP 4。**禁止**在此停下等用户回复"我授权好了"。你必须主动轮询。

→ GOTO STEP 4

---

### STEP 4 — 轮询授权结果（循环）

> ⚠️ 使用 STEP 3 保存的 `$device_code` 和 `$client_id`。**禁止**重新执行 STEP 3（否则会生成新的验证码，用户之前打开的链接作废）。

```bash
sleep $interval && npx @lark-project/meegle@beta auth login --device-code --phase poll --once \
  --device-code-value $device_code --client-id $client_id --format json
```

PARSE response → `$status` = response.status

**跳转：**
- IF `$status == "ok"` → GOTO STEP 5
- IF `$status == "authorization_pending"` → GOTO STEP 4（重复本步骤，继续轮询）
- IF `$status == "slow_down"` → `$interval = $interval + 5`，GOTO STEP 4
- IF `$status == "expired_token"` → SEND "授权已超时，请重新发起登录"，STOP
- IF attempts > `$max_attempts` → SEND "轮询超时，请重试"，STOP

---

### STEP 5 — 通知登录成功

SEND to user: "登录成功！"

> ⚠️ 此消息**必须单独发送**，不要与后续业务查询结果合并到同一条回复中。用户需要第一时间看到授权状态变化。

→ GOTO STEP 6

---

### STEP 6 — 执行业务命令

Auth 已通过，进入下方「业务命令调用」部分执行用户请求的操作。

## 业务命令调用

Auth Guard 通过后，使用以下模式调用业务命令。

### 命令结构

```bash
npx @lark-project/meegle@beta <resource> <method> [flags] --format json
```

命令采用 `resource method` 两级结构。所有输出默认 JSON 格式。

### 全局 Flag

| Flag | 说明 |
|------|------|
| `--format json\|table\|ndjson` | 输出格式，默认 json |
| `--select <props>` | 选取输出属性，逗号分隔（支持 dot path，如 `name,owner.name`） |
| `--profile <name>` | 临时切换 profile |
| `--verbose` | 显示详细日志 |

### 参数传递

三种方式，优先级从高到低：

1. **Flag 模式**（推荐）：`--project-key PROJ --work-item-type-key story`
2. **--set 模式**（设置工作项字段）：`--set priority=1 --set name="任务标题"`，value 支持 JSON
3. **--params 模式**（完整 JSON）：`--params '{"project_key":"PROJ","work_item_type_key":"story"}'`

Flag 和 --set 会覆盖 --params 中的同名字段。

### 常用命令速查

#### 查询待办

```bash
npx @lark-project/meegle@beta mywork todo --format json
```

#### 查询工作项

```bash
npx @lark-project/meegle@beta workitem get --project-key <project_key> --work-item-id <id> --format json
```

#### 搜索工作项（MQL）

```bash
npx @lark-project/meegle@beta workitem query --project-key <project_key> --search-mql "<MQL>" --format json
```

#### 创建工作项

```bash
npx @lark-project/meegle@beta workitem create --project-key <project_key> --work-item-type-key <type> \
  --set name="标题" --set priority=1 --format json
```

#### 更新工作项字段

```bash
npx @lark-project/meegle@beta workitem update --project-key <project_key> --work-item-id <id> \
  --set name="新标题" --format json
```

#### 查询项目信息

```bash
npx @lark-project/meegle@beta project get --project-key <project_key> --format json
```

#### 查询工作项类型和字段元数据

```bash
npx @lark-project/meegle@beta workitem meta-types --project-key <project_key> --format json
npx @lark-project/meegle@beta workitem meta-fields --project-key <project_key> --work-item-type-key <type> --format json
```

### 查看命令参数（inspect）

使用 `inspect` 查看某个命令的完整参数 schema（必填/可选、类型、描述）：

```bash
npx @lark-project/meegle@beta inspect workitem.create    # 查看 workitem create 的参数详情
npx @lark-project/meegle@beta inspect workitem.query     # 查看 workitem query 的参数详情
```

不带参数时列出所有可用命令：

```bash
npx @lark-project/meegle@beta inspect                    # 列出所有 resource 及其 method
```

> **推荐**：在调用一个不熟悉的命令前，先用 `inspect` 查看其参数 schema，确认必填字段和类型。

### 输出处理

- 始终使用 `--format json` 获取结构化输出，方便解析
- 使用 `--select` 精简返回字段，如 `--select id,name,current_nodes.name`
- 命令返回错误时，JSON 中包含 `error` 和 `message` 字段

## 触发条件

- **主动登录**：用户说"登录 Meegle"、"连接飞书项目"、"login meegle"等。
- **被动拦截**：用户请求任何 Meegle 业务操作（查询待办、查工作项、创建任务等），优先执行 Auth Guard。

## 错误处理

- 如果 bash 返回 `command not found` 或 npx 不可用，提示用户安装 Node.js 18+。
- 如果 `--phase init` 返回错误（站点不支持 Device Code），提示用户在终端中执行 `npx @lark-project/meegle@beta auth login`。
- 如果 `--phase poll` 超时，提示用户重试登录流程。
