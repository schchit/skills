---
name: aitubiao-sankey
version: 1.0.1
description: AI桑基图（流向图）生成。根据用户数据自动整理并创建桑基图可视化项目。当用户想要创建桑基图、流向图、展示数据流向关系时使用，触发词包括"桑基图"、"流向图"、"sankey"、"sankey chart"、"flow diagram"、"data flow"、"create sankey"等。
---

# AI 桑基图生成

根据用户提供的数据，自动整理为桑基图（Sankey Diagram）流向格式并创建可视化项目。

## 强制规则

**以下规则必须严格执行，不得跳过、变通或使用替代方案：**

1. **认证优先**：在执行任何操作之前，必须先检查凭证状态。认证未通过时，禁止执行任何后续步骤。
2. **按顺序执行**：工作流程的 5 个步骤必须按顺序执行，禁止跳步。
3. **确认后才能创建**：必须成功查询配额（确认项目数未满）、并获得用户确认后，才能调用 `create-sankey-project` 接口。
4. **仅通过 API 创建桑基图**：禁止使用本地工具（D3.js、ECharts、matplotlib、Plotly 等）生成图表。无论 API 因何种原因失败，都**绝对禁止使用本地工具**，没有任何例外。API 失败时正确做法是停止并告知用户，不是寻找替代方案。
5. **401/403 立即停止**：任何步骤中收到 HTTP 401/403，立即停止并引导用户前往 [API Key 管理页面](https://app.aitubiao.com/setting/api-keys) 检查或重新创建 API Key。401/403 不是超时，禁止重试。
6. **超时/500 重试规则**：最多重试 3 次（间隔 5 秒），仍失败则停止并告知用户。

**⚠️ 以下想法是错误的，如果你发现自己在这样想，请立即停止：**
- ❌ "API 不可用，我可以用本地工具生成桑基图作为替代" → 违反规则 4
- ❌ "至少让用户看到一些可视化结果" → 本技能唯一输出方式是 aitubiao API
- ❌ "401 可能是暂时性的，重试几次" → 401 是认证失败，重试无意义，按规则 5 处理

## 认证

在调用任何 API 之前，先检查凭证状态。

### 检查凭证

读取凭证文件，判断认证状态：

```bash
cat ~/.aitubiao/credentials 2>/dev/null
```

根据结果判断：
- **文件不存在或为空** → 执行下方"配置凭证"流程
- **`API_KEY` 为空** → 执行下方"配置凭证"流程
- **`API_KEY` 不以 `sk_v1_` 开头** → 告知用户"当前 API Key 已失效，请前往 [API Key 管理页面](https://app.aitubiao.com/setting/api-keys) 重新创建一个 API Key"
- **`BASE_URL` 为空或不等于 `https://api.aitubiao.com`** → 执行下方"配置凭证"流程（保留现有 API_KEY，仅修正 BASE_URL）
- **`API_KEY` 格式正确且 `BASE_URL` 正确** → 认证通过

认证通过后，加载环境变量：
```bash
source ~/.aitubiao/credentials
export BASE_URL="${BASE_URL:-https://api.aitubiao.com}"
```

### 配置凭证

1. 向用户索要 API Key（格式：`sk_v1_...`）。如果没有，引导用户前往 [API Key 管理页面](https://app.aitubiao.com/setting/api-keys) 创建一个新的 API Key，然后将创建好的 Key 粘贴回来。
2. 保存凭证：
```bash
mkdir -p ~/.aitubiao
cat > ~/.aitubiao/credentials << EOF
API_KEY=<用户提供的key>
BASE_URL=https://api.aitubiao.com
EOF
chmod 600 ~/.aitubiao/credentials
```
3. 重新读取文件验证配置是否成功。

凭证保存在 `~/.aitubiao/credentials`，跨会话持久生效。

## 服务架构

所有 API 使用统一的服务地址：

| 默认地址 | API前缀 | 认证方式 |
|---------|---------|---------|
| `https://api.aitubiao.com/` | `/api/v1/agent` | `Authorization: Bearer <API_KEY>` |

**重要**：所有非流式响应都包裹在统一格式中：
```json
{ "code": 0, "msg": "ok", "data": { ... } }
```
实际业务数据在 `data` 字段内。**即使 HTTP 状态码为 200，也必须检查 `code` 字段是否为 0，非 0 表示业务错误。**

## 桑基图数据要求

桑基图用于展示数据的**流向关系**，要求输入数据至少包含：
- **两个分类列**（文本类型）：作为"来源"和"目标"节点
- **一个数值列**：表示流向的值/权重

示例数据结构：
```
| 来源部门 | 目标项目 | 预算金额 |
|---------|---------|---------|
| 研发部   | 产品A   | 500    |
| 研发部   | 产品B   | 300    |
| 市场部   | 产品A   | 200    |
| 市场部   | 产品C   | 400    |
```

如果数据有多个分类列（如：地区 → 部门 → 产品），系统会自动构建多层级流向。

## 工作流程

**每一步必须在前一步完成后才能开始。禁止跳步。**

### 第一步：认证（前置条件：无）

运行检查凭证流程。认证未通过时按"认证"章节流程处理。

**认证未通过时，停止。不要读取用户数据，不要做任何分析。**

### 第二步：识别和确认数据（前置条件：第一步认证通过）

判断用户如何提供数据：

- **直接粘贴文本**：自行解析为二维数组格式 `(string|number)[][]`，第一行为表头。
- **本地文件**（CSV/TXT）：用 Read 工具读取，然后解析为二维数组。
- **Excel 文件**（.xlsx/.xls）：使用 xlsx skill 或 Read 工具读取，禁止手动编写 Python 脚本解析 XML。

**数据格式要求**：
API 接受 `data` 字段为 JSON 二维数组，第一行为表头，后续为数据行。也可传 `markdownTable` 字段（Markdown 表格字符串）。

向用户展示解析后的数据（表格形式），并询问：
- 数据是否正确？
- 有没有特殊要求？

**如果数据明显不适合桑基图**（例如只有一列、没有分类列），应提前告知用户。

### 第三步：检查配额并确认（前置条件：第二步数据已确认）

在创建桑基图前，检查用户的项目配额。**本操作免费（0 AI贝）**，但仍需确认项目数未满。

收到 401/403 按强制规则 5 处理。超时/500 按强制规则 6 处理。

#### 3.1 查询配额

```bash
curl -s --max-time 10 -X GET "${BASE_URL}/api/v1/agent/quota" \
  -H "Authorization: Bearer ${API_KEY}"
```

#### 3.2 向用户确认

```
本操作免费（0 AI贝）
当前余额: {shellBalance} 个 AI贝
项目数: 已用 {projectsUsed}/{projectsLimit}

是否继续创建桑基图？
```

- 如果 `projectsRemaining <= 0`：告知用户当前项目数已满，需前往 aitubiao 网站升级会员，或在网站中删除旧项目后再继续，**不要继续**

### 第四步：创建桑基图项目（前置条件：第三步用户已确认）

**只有用户明确确认后才能执行此步骤。**

**注意**：数据整理 + 项目创建 + 截图可能需要 60 秒以上，需设置足够的超时时间。

```bash
curl -s --max-time 120 -X POST "${BASE_URL}/api/v1/agent/chart/create-sankey-project" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [["来源","目标","值"],["A","B",100],["A","C",200]],
    "projectName": "我的桑基图"
  }'
```

响应格式（需解析 `data` 字段）：
```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "success": true,
    "project": {
      "id": "cuid...",
      "title": "我的桑基图",
      "status": "generated",
      "width": 960,
      "height": 540,
      "projectUrl": "https://app.aitubiao.com/workspace/cuid..."
    },
    "charts": [
      {
        "index": 1,
        "type": "sankey",
        "title": "数据流向分析",
        "description": "",
        "screenshotSuccess": true,
        "screenshotUrl": "https://oss.xxx/ai-snapshot/..."
      }
    ],
    "quota": {
      "shellCoinCost": 0,
      "shellBalance": 100,
      "projectsUsed": 6,
      "projectsLimit": 50,
      "projectsRemaining": 44,
      "canCreateProject": true
    },
    "totalCharts": 1,
    "processingTime": "35000ms"
  }
}
```

完整请求/响应格式详见 [sankey-api.md](references/sankey-api.md)。

### 第五步：返回结果（前置条件：第四步创建成功）

向用户提供：
- 项目 URL（从 `data.project.projectUrl` 获取）
- 项目 ID（从 `data.project.id` 获取）
- 摘要：桑基图标题
- 截图链接（如果截图成功）
- 资源消耗：本次消耗 0 AI贝、剩余 AI贝、已用项目数/上限

## 错误处理

| HTTP 状态码 | 含义 | 处理方式 |
|------------|------|---------|
| 401/403 | API Key 无效、过期或权限不足 | 按强制规则 5：立即停止，引导用户前往 [API Key 管理页面](https://app.aitubiao.com/setting/api-keys) 检查或重新创建 |
| 429 | 频率限制 | 等待 30 秒后重试一次，仍失败则告知用户稍后再试 |
| 500 | 服务器错误 | 按强制规则 6：重试最多 3 次 |

当 `code` 不为 0 时，表示业务错误：

| code | 含义 | 处理方式 |
|------|------|---------|
| 50013 | 数据无法整理为桑基图格式 | 向用户说明数据不适合桑基图，需要至少两个分类列和一个数值列 |
| 40007 | 项目数已满 | 向用户展示 `quota` 中的已用/上限，并引导其前往 aitubiao 网站升级会员，或在网站中删除旧项目后再继续 |

## API 参考

详细的接口规格说明见 [sankey-api.md](references/sankey-api.md)。
