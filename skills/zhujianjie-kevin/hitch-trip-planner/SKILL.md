---
name: hitch-trip-planner
description: 哈啰顺风车 MCP 出行技能。覆盖地点搜索、询价、发单、邀请司机、行程跟踪、取消等全流程，适用于用户要"去哪、多少钱、帮我叫车、查订单"等场景。
---

# 🚗 哈啰顺风车出行技能

## 🎯 目标

当用户在 Agent 内发起顺风车相关出行需求时，使用本技能完成从地点搜索到行程结束的全流程闭环：

> 确定起终点 → 询价 → 发单 → 邀请司机 → 行程跟踪 → 确认到达

本技能面向乘客侧，通过哈啰顺风车 AI 开放平台 MCP 工具实现。

---

## ⚙️ 准备工作

使用本技能需要提前在 [哈啰 AI 开放平台](https://aiopen.hellobike.com/) 获取接入的 api-key，然后按照以下设置配置 mcp 服务器：

```bash
{
  "mcpServers": {
    "hitch-ai-platform": {
      "url": "https://hellohitchapi.hellobike.com/ai-openplatform/mcp",
      "headers": {
        "Authorization": "YOUR_API_KEY"
      }
    }
  }
}
```

---

## 🔑 触发场景

关键词：`顺风车`、`拼车`、`独享`、`询价`、`从哪到哪`、`帮我叫车`、`发单`、`查订单`、`取消订单`、`司机位置`、`邀请司机`、`生成链接`。

---

## 🧰 可用工具一览

### 🗺️ 地图服务

| 工具 | 说明 |
|------|------|
| `maps_textsearch` | 关键词搜索 POI，获取坐标、cityCode、adCode。所有需要坐标的操作的前置步骤 |

### 🚙 顺风车服务

| 工具 | 类型 | 说明 |
|------|:----:|------|
| `hitch_estimate_price` | 读 | 询价，返回 priceTraceId 和 capacities（运力列表） |
| `hitch_create_order` | ✏️ 写 | 创建订单，必须先完成询价 |
| `hitch_query_order` | 读 | 查询订单状态；不传 orderGuid 返回当前进行中订单列表 |
| `hitch_invite_driver_list` | 读 | 查询可邀请车主列表 |
| `hitch_invite_driver` | ✏️ 写 | 邀请指定司机接单 |
| `hitch_get_driver_location` | 读 | 获取司机实时位置与预计到达时间 |
| `hitch_pax_confirm_get_on_car` | ✏️ 写 | 乘客确认上车 |
| `hitch_pax_confirm_reach_destination` | ✏️ 写 | 乘客确认到达目的地 |
| `hitch_cancel_order` | ✏️ 写 | 取消订单 |
| `hitch_generate_app_link` | 读 | 生成跳转哈啰 App 发单页的 deep link |
| `hitch_generate_wechat_link` | 读 | 生成跳转微信小程序的支付/订单链接 |

---

## 🚧 核心约束

> **约束 1 · 坐标必须通过工具获取**
> 所有经纬度必须通过 `maps_textsearch` 实时获取，禁止使用记忆中的坐标。

> **约束 2 · 数字参数用字符串传递**
> 经纬度等数字参数必须以字符串类型传入。

> **约束 3 · 发单前必须先询价**
> `hitch_create_order` 依赖 `hitch_estimate_price` 返回的 `priceTraceId` 和 `capacities`。

> **约束 4 · 写操作前必须获取用户确认**
> `hitch_create_order`、`hitch_cancel_order`、`hitch_invite_driver` 等写操作调用前，必须向用户展示关键信息并等待明确确认，禁止自动执行。

> **约束 5 · 数据证据优先**
> 如果工具返回的数据与用户描述冲突，必须先引用数据指出冲突，请求用户确认后再继续。

---

## 📋 工作流

### 🛣️ 完整叫车流程

```bash
用户："帮我叫个顺风车去西湖"
```

**① 地址解析** — `maps_textsearch` × 2
分别搜索起点和终点坐标（未提供起点时必须先询问）

**② 询价** — `hitch_estimate_price`
传入起终点坐标，获取可选运力和价格，保存 priceTraceId

**③ 用户选择运力**
以编号列表展示所有可选运力，默认不预选，让用户自己选择：

⚠️ 禁止自动下单，必须等用户明确选择

展示格式示例：
```bash
请选择你想要的运力（回复编号，可多选，如"1 3"或"全选"）：
1. 拼座 — 约 XX 元
2. 独享 — 约 XX 元
3. 特惠独享 — 约 XX 元
4. 只拼一单 — 约 XX 元
```

处理用户回复：
- `"1 3"` 或 `"1、3"` → 选择编号 1 和 3 对应的运力
- `"全选"` 或 `"都要"` → 全选所有 capacities
- `"独享"` → 匹配名称选择
- 用户未选择任何运力 → 不发单，继续等待用户选择

**④ 确认愿等时间**
询问用户愿意等多久，示例：
```bash
你愿意等多久？（默认 10 分钟，最长 180 分钟）
```
- 用户回复具体分钟数 → 使用该值
- 用户说"默认"或不回答 → 使用默认 10 分钟
- 超过 180 分钟 → 提示最长 180 分钟，请重新输入

**⑤ 创建订单** — `hitch_create_order`
传入用户选择的 selectedCapacities、priceTraceId 和 waitMinutes，保存返回的 orderGuid

**⑥ 等待接单 / 邀请司机**
- 查询可邀请车主：`hitch_invite_driver_list`
- 选择合适司机邀请：`hitch_invite_driver`
- 或等待司机主动接单

**⑦ 行程跟踪** — `hitch_query_order` / `hitch_get_driver_location`
按订单状态轮询，展示司机位置和预计到达时间

**⑧ 行程操作**
- 确认上车：`hitch_pax_confirm_get_on_car`
- 确认到达：`hitch_pax_confirm_reach_destination`

---

### 📊 订单状态与建议动作

| 状态 | 建议动作 |
|------|----------|
| 等待接单 | 查询可邀请车主列表，建议用户邀请司机 |
| 司机已接单 | 展示司机信息，查询司机位置 |
| 司机已到达 | 提醒用户上车，可调用确认上车 |
| 行程中 | 展示行程进度 |
| 到达目的地 | 引导确认到达 |
| 已完成 | 展示行程总结 |

---

### 🔗 生成链接流程

- **App 深链**：`hitch_generate_app_link`（需要起终点完整信息含 cityCode、adCode）
- **微信小程序链接**：`hitch_generate_wechat_link`（需要 orderGuid，根据订单状态自动选择跳转页面）

---

## 🔐 幂等键规则

所有写操作都需要 `idempotencyKey` 参数：

| 操作 | 规则 |
|------|------|
| `hitch_create_order` | 首次生成唯一值，超时重试时复用同一个值 |
| `hitch_invite_driver` | 建议用 `orderGuid + driverId` 拼接；邀请不同司机时生成新值 |
| `hitch_pax_confirm_get_on_car` | 建议直接用 orderGuid |
| `hitch_pax_confirm_reach_destination` | 建议直接用 orderGuid |
| `hitch_cancel_order` | 首次生成唯一值，重试时复用 |

---

## ❓ 必须追问的场景

- 用户未提供起点
- 地点描述模糊，如"人民广场附近"
- 用户要询价但没给出发时间
- 用户说"帮我下单"但没有确认价格和运力
- 用户要查订单但没有订单号

---

## ⚠️ 必须再次确认的场景

- 调用 `hitch_create_order` 前：展示价格和运力
- 调用 `hitch_cancel_order` 前：说明取消后果
- 调用 `hitch_invite_driver` 前：展示司机信息（昵称、评分、车型、顺路度）
- 用户从"先看看"切换到"现在就下单"时

---

## 🛡️ 失败与回退

| 场景 | 处理 |
|------|------|
| `maps_textsearch` 多个结果 | 展示候选地点，请用户确认 |
| `hitch_estimate_price` 失败 | 保留起终点信息，建议稍后重试或用深链进 App 查看 |
| `hitch_create_order` 失败 | 说明失败原因，不要暗示已下单 |
| `hitch_invite_driver` 失败 | 说明邀请未成功，可尝试邀请其他司机 |
| `hitch_cancel_order` 失败 | 明确取消未成功，返回失败原因 |
| 任一工具超时 | 说明当前不可用，不要把超时包装成业务结论 |

---

## 💬 对话示例

### 示例 1：询价 + 下单

```bash
用户：明天下午 3 点从杭州东站到西湖，顺风车多少钱？

Agent：
1. maps_textsearch("杭州东站", city_code="0571")
2. maps_textsearch("西湖", city_code="0571")
3. hitch_estimate_price(起终点坐标, start_city_code=...)

回复：
杭州东站 → 西湖，约 XX 公里

请选择你想要的运力（回复编号，可多选，如"1 2"或"全选"）：
1. 拼座 — 约 XX 元
2. 独享 — 约 XX 元

用户：1 2

Agent：你愿意等多久？（默认 10 分钟，最长 180 分钟）

用户：30 分钟

Agent：
4. hitch_create_order(selectedCapacities=[拼座skuCode, 独享skuCode], priceTraceId=..., waitMinutes=30)

回复：
订单已创建，订单号 xxx
正在等待司机接单，要帮你查看附近可邀请的车主吗？
```

---

### 示例 2：邀请司机

```bash
用户：帮我看看有哪些司机可以邀请

Agent：
1. hitch_invite_driver_list(orderGuid=...)

回复：
找到 3 位可邀请车主：
1. 张师傅 ⭐4.9 | 白色本田雅阁 | 顺路度 85%
2. 李师傅 ⭐4.7 | 黑色大众帕萨特 | 顺路度 72%
3. 王师傅 ⭐4.8 | 银色丰田凯美瑞 | 顺路度 90%

要邀请哪位？

用户：邀请王师傅

Agent：
2. hitch_invite_driver(orderGuid=..., driverId=..., hitchPercent="0.90", ...)

回复：已向王师傅发送邀请，等待司机确认。
```

---

### 示例 3：行程跟踪

```bash
用户：司机到哪了？

Agent：
1. hitch_get_driver_location(orderGuid=...)

回复：
司机当前距您约 2.3 公里，预计 5 分钟到达。
```

---

### 示例 4：生成链接

```bash
用户：帮我生成一个去 App 下单的链接

Agent：
1. 确认起终点已标准化
2. hitch_generate_app_link(起终点完整信息...)

回复：
已生成跳转链接，点击后将打开哈啰 App 的发单页面。
注意：链接仅用于跳转，最终下单需在 App 内确认。
```
