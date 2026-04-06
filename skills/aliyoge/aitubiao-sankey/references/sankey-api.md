# Sankey Chart API Reference

> **重要**：所有非流式响应都包裹在 `{ "code": 0, "msg": "ok", "data": { ... } }` 结构中。
> 下面的响应示例展示的是 `data` 字段内的业务数据。
> **即使 HTTP 状态码为 200，也必须检查 `code` 字段是否为 0。非 0 表示业务错误。**

## 1. Create Sankey Project (一站式)

**Endpoint**: `POST {BASE_URL}/api/v1/agent/chart/create-sankey-project`

一次调用完成：数据整理（流向格式） → 项目创建 → 截图生成

**免费端点（0 AI贝）**

**Headers**:
```
Authorization: Bearer {API_KEY}
Content-Type: application/json
```

**Request Body**:
```json
{
  "data": [["Source", "Target", "Value"], ["A", "B", 100], ["A", "C", 200]],
  "projectName": "My Sankey Chart"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| data | (string\|number)[][] | 二选一 | 二维数组格式，第一行为表头 |
| markdownTable | string | 二选一 | Markdown 表格格式数据（与 data 二选一） |
| projectName | string | No | 项目名称，默认根据数据自动生成或 "AI桑基图" |
| pageSize | { width, height } | No | 页面尺寸，默认 960x540 |
| elementSize | { width, height } | No | 图表元素尺寸，默认 700x500 |

**Response** (data 字段内容):
```json
{
  "success": true,
  "project": {
    "id": "cuid_string",
    "title": "数据流向分析",
    "status": "generated",
    "width": 960,
    "height": 540,
    "projectUrl": "https://app.aitubiao.com/workspace/cuid_string"
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
```

**注意**:
- 数据整理 + 项目创建 + 截图可能需要 30-60 秒，请设置足够的超时时间 (建议 120s)。
- 截图失败不影响项目创建，`screenshotSuccess` 为 `false` 时查看 `error` 字段。
- `quota` 字段可能为 `null`（配额查询失败时），不影响项目创建结果。
- `shellCoinCost` 始终为 `0`（本端点免费）。

**业务错误响应** (code ≠ 0):

| 错误码 | 含义 | 处理方式 |
|--------|------|---------|
| 50013 | 数据无法整理为桑基图格式 | 检查数据是否包含至少两个分类列和一个数值列 |
| 50006 | 图表设置转换失败 | 系统内部错误，建议重试 |
| 40007 | 项目数已满 | 展示 quota 中的已用/上限，建议删除旧项目或升级会员 |
| 40015 | 项目创建失败 | 系统内部错误，建议重试 |

## 2. Get User Quota (通用配额查询)

**Endpoint**: `GET {BASE_URL}/api/v1/agent/quota`

查询用户当前 AI贝余额和项目配额。桑基图创建虽然免费，但仍需确认项目数未满。

**Headers**:
```
Authorization: Bearer {API_KEY}
```

**Response** (data 字段内容):
```json
{
  "shellBalance": 100,
  "shellLeft": 80,
  "shellNum": 20,
  "projectsUsed": 5,
  "projectsLimit": 50,
  "projectsRemaining": 45,
  "pptGeneratePageLimit": 32,
  "features": {
    "sankeyProject": { "key": "sankeyProject", "cost": 0, "unit": "次", "label": "桑基图项目创建", "billingModel": "per-request" }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| shellBalance | number | 当前 AI贝总余额 |
| projectsUsed | number | 已创建项目数 |
| projectsLimit | number | 项目数上限 |
| projectsRemaining | number | 剩余可创建项目数 |
