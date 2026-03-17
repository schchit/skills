---
name: yuri-ad-skill
description: Yuri广告平台 MCP API - Facebook广告创建、投放管理、数据监控。支持创建Campaign/Ad Set/Ad、查询余额、受众定位、文案素材管理、预算调整等。
---

# Yuri Ad Platform API

通过 curl 调用 baiz.ai MCP API 管理 Facebook 广告。

## 基础配置

- **Base URL**: `https://baiz.ai/mcp`
- **Auth**: Bearer Token (格式: `xxx|xxx`)

## 通用调用格式

```bash
curl -s "https://baiz.ai/mcp" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"TOOL_NAME","arguments":{ARGUMENTS}},"id":1}'
```

## 核心工具

### 1. 查询余额
```bash
{"name":"get_balance","arguments":{}}
```

### 2. 广告账户
```bash
# 列出BM
{"name":"list_businesses","arguments":{}}

# 列出广告户 (bm_id 从 list_businesses 获取)
{"name":"list_ad_accounts","arguments":{"bm_id":44723}}

# 列出主页
{"name":"list_pages","arguments":{}}
```

### 3. Offer 管理
```bash
# 创建 Offer
{"name":"create_offer","arguments":{"name":"产品名称","url":"https://...","price":29.99}}

# 列出 Offers
{"name":"list_offers","arguments":{}}
```

### 4. 受众定位
```bash
# 创建受众
{"name":"create_targeting","arguments":{"name":"受众名称","countries":["US"],"gender":"all","min_age":25,"max_age":55}}

# 列出受众
{"name":"list_targetings","arguments":{}}
```

### 5. 文案
```bash
# 创建文案
{"name":"create_copywriting","arguments":{"name":"文案名称","primary_text":"正文","headline":"标题","description":"描述"}}

# 列出文案
{"name":"list_copywritings","arguments":{}}
```

### 6. 素材
```bash
# 通过URL上传
{"name":"create_file","arguments":{"url":"https://...","name":"文件名","tag":"标签"}}

# 列出素材
{"name":"list_files","arguments":{}}
```

### 7. 广告计划
```bash
# 创建 Campaign
{"name":"create_campaign","arguments":{
  "name": "广告名称",
  "objective": "OUTCOME_SALES",
  "call_to_action_type": "LEARN_MORE",
  "start_time": "2026-03-16 17:00:00",
  "end_time": "2026-03-23 23:59:59",
  "selected_hours": ["0-23"],
  "copywriting_ids": [文案ID],
  "targeting_ids": [受众ID],
  "file_ids": [素材ID],
  "offer_ids": [OfferID],
  "facebook_business_id": BM系统ID,
  "facebook_page_id": 主页系统ID,
  "ad_account_ids": [广告户系统ID],
  "budget_type": "daily",
  "limit_daily_amount": 20
}}

# 列出 Campaigns
{"name":"list_campaigns","arguments":{}}

# 获取 Campaign 详情
{"name":"get_campaign","arguments":{"id": CampaignID}}

# 发布 Campaign
{"name":"publish_campaign","arguments":{"id": CampaignID}}

# 暂停 Campaign
{"name":"stop_campaign","arguments":{"id": CampaignID}}

# 启动 Campaign
{"name":"start_campaign","arguments":{"id": CampaignID}}

# 调整预算
{"name":"adjust_budget","arguments":{"id": CampaignID, "action": "increase|decrease|set", "amount": 20}}
```

### 8. 数据监控
```bash
# 广告级别数据
{"name":"list_campaign_ads","arguments":{"id": CampaignID}}

# 广告组级别数据
{"name":"list_campaign_adsets","arguments":{"id": CampaignID}}

# 暂停/启动广告组
{"name":"update_adset_status","arguments":{"id": CampaignID, "adset_id": "FB广告组ID", "status": "PAUSED|ACTIVE"}}
```

### 9. 扩量
```bash
# 复制整个Campaign
{"name":"copy_campaign","arguments":{"id": CampaignID}}

# 复制广告组
{"name":"copy_adset","arguments":{"id": CampaignID, "adset_id": "FB广告组ID"}}
```

## 常用ID速查

| 类型 | 示例ID |
|------|--------|
| BM ID | 44723 (Yuri-212-08261204) |
| 广告户ID | 339910 (系统内部), 1919376461994756 (FB) |
| 主页ID | 17623 (Jadiel Manuel Juan Emmitt) |

## 广告状态码

- 0: 草稿
- 1: 审核中
- 2: 投放中
- 3: 被拒
- 4: 不盈利
- 5: 预算耗尽
- 6: 归档
- 7: 已停止
- 8: 已禁用
- 9: 已过期
- 10: 失败

## 使用示例

创建广告流程：
1. get_balance - 检查余额
2. list_businesses + list_ad_accounts + list_pages - 获取BM/广告户/主页
3. create_offer - 创建Offer
4. create_targeting - 创建受众
5. create_copywriting - 创建文案
6. create_file - 上传素材
7. create_campaign - 创建广告计划
8. publish_campaign - 发布广告
