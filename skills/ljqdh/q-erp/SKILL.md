---
name: q-erp
version: 1.0.6
description: 千易 ERP 管理查询技能（一期）。覆盖今日经营动态、商品销售情况、增长潜力；所有查询必须通过 q-claw。
user-invocable: true
---

# q-erp Phase 1 Management Query Skill

## Scope

本 Skill 只处理 ERP 一期管理查询：
- 今日经营动态
- 商品销售情况
- 增长潜力

其中以下表达统一视为“商品销售情况”并路由到 `erp.product.sales.overview`：
- 热销商品排行
- 商品排行榜
- 热销 SPU
- 畅销商品
- 爆品排行
- 热销组合品

以下场景不在一期范围内：
- ERP 写入类动作（创建/修改单据、审批、回写）
- 与 ERP 管理查询无关的闲聊、翻译、写作

## Locale Policy

- 读取 `context.locale`。
- `zh_CN`：使用简体中文回复，并优先使用中文示例话术。
- `en_US`：使用英文回复，并优先使用英文示例话术。
- 其他 locale：统一回退到英文。
- 禁止翻译 `scene`、参数名、编码字段、状态码。

## Critical Rules

1. 所有 ERP 管理查询必须调用 `q-claw`，禁止直接编造业务数据。
2. scene 只能从本文件路由表选择，禁止替换为未定义 scene。
3. 结果以后端返回为准；缺失字段明确说明“后端未返回”。
4. 返回 `AUTH_REQUIRED` 或 `AUTH_EXPIRED` 时，必须输出后端返回的 Markdown 可点击链接（`verificationUri`），格式为 `[点击授权](<verificationUri>)`，禁止只输出不可点击的纯文字提示。

## Scene Routing

| 用户意图 | scene |
| --- | --- |
| 今日经营动态 | `erp.management.today.summary` |
| 商品销售情况 / 热销商品排行 / 商品排行榜 / 热销SPU / 畅销商品 / 爆品排行 / 热销组合品 | `erp.product.sales.overview` |
| 增长潜力 | `erp.product.growth.opportunity` |

调用字段固定为：`scene`、`userInput`、`params`（`tenantKey/openId` 由运行时注入）。

英文用户常用表达：
- `How is today's business performance`
- `Show me product sales overview`
- `Analyze growth opportunities`

## Tool Call Examples

今日经营动态：

```json
{"scene":"erp.management.today.summary","userInput":"看下今天经营动态","params":{}}
```

商品销售情况：

```json
{"scene":"erp.product.sales.overview","userInput":"看看商品销售情况","params":{}}
```

热销商品排行：

```json
{"scene":"erp.product.sales.overview","userInput":"热销商品排行，发我看下","params":{}}
```

增长潜力：

```json
{"scene":"erp.product.growth.opportunity","userInput":"分析增长潜力","params":{}}
```

## Result Handling

1. 优先输出工具返回的 `assistantReplyLines`。
2. 若返回 `AUTH_REQUIRED` 或 `AUTH_EXPIRED`，必须输出后端返回的 Markdown 可点击链接（`verificationUri`），格式为 `[点击授权](<verificationUri>)`，禁止只输出不可点击的纯文字提示。
3. 当 `firstTimeAuth: true` 时，先输出业务结果，再根据 `context.locale` 追加对应引导话术（原样输出，不改写）：

### firstTimeAuth.zh_CN

---
🎉 ERP 授权成功，你可以直接问我：

- **今日经营动态**：「今天经营情况怎么样」
- **商品销售情况**：「看看商品销售情况」
- **增长潜力**：「分析下增长潜力」

English examples:

- **Today's operating snapshot**: `How is today's business performance`
- **Product sales overview**: `Show me product sales overview`
- **Growth opportunity**: `Analyze growth opportunities`
---

### firstTimeAuth.en_US

---
🎉 ERP authorization successful. You can ask me directly:

- **Today's operating snapshot**: `How is today's business performance`
- **Product sales overview**: `Show me product sales overview`
- **Growth opportunity**: `Analyze growth opportunities`
---
