---
name: fb-travel-allowance-skill
description: 差旅补助助手，支持补助标准查询、出差补助计算、补助申请、审批进度查询、发放状态跟踪等功能。Invoke when user needs to calculate travel allowance, submit allowance claims, or check allowance policy and status.
version: 1.0.0
metadata: {"openclaw": {"emoji": "💵", "category": "finance", "tags": ["差旅补助", "出差补贴", "补助申请", "补助标准", "审批"], "requires": {"bins": ["python3"]}, "required": true}}
---
# 差旅补助助手 (fb-travel-allowance-skill)

## 技能描述

差旅补助助手面向企业员工出差场景，支持补助标准查询、自动核算、补助申请、审批流转和发放跟踪。可基于出差申请、实际行程、城市等级、职级、是否统一供餐/住宿等信息，自动计算可领取的差旅补助，降低人工核算和重复申领风险。

---

⚠️ 【重要约束】
- 必须关联出差申请、差旅订单或有效行程单
- 同一出差日期区间不得重复领取同类补助
- 已由公司统一提供餐食、住宿或交通的部分必须扣减或不予发放
- 出差取消、缩短、延期后必须重新核算补助
- 超过申请时效的补助单不得直接提交，需补充说明
- 补助标准必须与职级、城市等级、出差时长匹配

---

## 核心功能

### 1. 补助标准查询
- 查询职级对应的日补助标准
- 查询不同城市等级补助额度
- 查询半天/全天补助规则
- 查询夜间交通补助标准
- 查询特殊地区补助规则

### 2. 自动补助核算
- 按出差申请自动计算补助
- 按实际出发与返回时间核算天数
- 支持半天、全天、跨天规则
- 统一供餐/住宿自动扣减
- 异常行程自动标记

### 3. 补助申请管理
- 创建补助申请单
- 关联出差申请与订单
- 修改补助申请内容
- 提交补助审批
- 撤回未审批申请

### 4. 审批与发放跟踪
- 查询审批进度
- 查看审批意见
- 查询发放状态
- 查询发放时间
- 查询历史补助记录

### 5. 合规与重复校验
- 重复申领检查
- 时效检查
- 出差区间匹配检查
- 城市等级与标准检查
- 公司统一保障扣减检查

### 6. 统计分析
- 月度补助统计
- 个人补助历史
- 部门补助支出分析
- 异常补助预警
- 补助发放效率分析

## 触发场景

1. **标准查询**
   - "北京出差一天补助多少钱"
   - "普通员工去上海的差旅补贴标准"
   - "半天出差怎么算补助"
   - "统一包餐还可以提现吗"

2. **自动计算**
   - "帮我算一下这次上海出差补助"
   - "根据我的出差订单计算补贴"
   - "3天2晚成都出差能领多少补助"
   - "这趟出差补助需要扣多少餐补"

3. **补助申请**
   - "我要提交差旅补助申请"
   - "为 TRIP202604010001 创建补助单"
   - "提交我的补助申请"
   - "撤回刚才那笔补助单"

4. **审批与发放查询**
   - "查看我的补助审批进度"
   - "补助什么时候到账"
   - "查询补助单 TA202604110001"
   - "我这个月领了多少差旅补助"

## 补助类型

| 补助类型 | 代码 | 说明 | 是否需发票 |
|:---|:---|:---|:---|
| 餐饮补助 | MEAL_ALLOWANCE | 出差期间用餐补助 | 否 |
| 市内交通补助 | LOCAL_TRANSPORT_ALLOWANCE | 市内交通补助 | 否 |
| 通讯补助 | COMMUNICATION_ALLOWANCE | 出差通讯补助 | 否 |
| 综合补助 | TRAVEL_ALLOWANCE | 统一按日补贴 | 否 |
| 特殊地区补助 | SPECIAL_REGION_ALLOWANCE | 偏远、高原等特殊地区补贴 | 否 |

## 补助标准体系

### 按职级和城市等级

| 职级 | 一线城市 | 新一线城市 | 其他城市 | 说明 |
|:---|:---|:---|:---|:---|
| 高管 | ¥300/天 | ¥250/天 | ¥220/天 | 含餐饮与市内交通 |
| 中层 | ¥220/天 | ¥180/天 | ¥150/天 | 含餐饮与市内交通 |
| 普通员工 | ¥150/天 | ¥130/天 | ¥100/天 | 含餐饮与市内交通 |

### 时长规则

| 时长 | 计算规则 |
|:---|:---|
| 4小时及以下 | 不发放 |
| 超过4小时且不满8小时 | 发放50% |
| 8小时及以上 | 发放100% |
| 连续跨天 | 按自然日或公司规则累计 |

### 扣减规则
- 公司统一供早餐：扣减日补助 20%
- 公司统一供午餐：扣减日补助 30%
- 公司统一供晚餐：扣减日补助 30%
- 公司统一安排住宿：不影响日补助，但特殊住宿补贴不再发放
- 公司统一安排接送：市内交通补助可按规则扣减

## 输入参数

### 补助标准查询

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---|:---|
| level | string | 是 | 职级：staff / manager / executive |
| city | string | 是 | 出差城市 |
| allowance_type | string | 否 | 补助类型 |
| trip_date | string | 否 | 出差日期 |

### 补助计算

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---|:---|
| trip_id | string | 是 | 出差申请单号 |
| traveler_name | string | 否 | 出差人姓名 |
| level | string | 是 | 职级 |
| destination_city | string | 是 | 出差城市 |
| departure_time | string | 是 | 出发时间 |
| return_time | string | 是 | 返回时间 |
| meal_provided | object | 否 | 是否统一供餐 |
| accommodation_provided | boolean | 否 | 是否统一提供住宿 |
| local_transport_provided | boolean | 否 | 是否统一提供市内交通 |
| remarks | string | 否 | 备注 |

### 补助申请

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---|:---|
| claim_id | string | 否 | 补助申请单号 |
| trip_id | string | 是 | 出差申请单号 |
| allowance_amount | float | 是 | 申请金额 |
| allowance_days | float | 是 | 补助天数 |
| deduction_amount | float | 否 | 扣减金额 |
| reason | string | 否 | 说明 |

## 输出格式

### 补助计算结果

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "trip_id": "TRIP202604010001",
    "allowance_type": "TRAVEL_ALLOWANCE",
    "level": "staff",
    "destination_city": "上海",
    "city_tier": "tier1",
    "standard_amount": 150.00,
    "allowance_days": 2.5,
    "base_amount": 375.00,
    "deduction_amount": 45.00,
    "final_amount": 330.00,
    "deduction_detail": [
      {"type": "meal", "name": "统一午餐", "amount": 45.00}
    ],
    "duplicate": false,
    "warnings": []
  }
}
```

### 补助申请结果

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "claim_id": "TA202604110001",
    "trip_id": "TRIP202604010001",
    "claim_status": "pending_approval",
    "allowance_amount": 330.00,
    "submit_time": "2026-04-11 16:20:00",
    "payment_status": "waiting",
    "approval_flow": [
      {"step": 1, "approver": "部门经理", "status": "pending"},
      {"step": 2, "approver": "财务审核", "status": "waiting"}
    ]
  }
}
```

### 补助详情示例

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "claim_id": "TA202604110001",
    "claim_status": "approved",
    "payment_status": "paid",
    "payment_time": "2026-04-15 10:00:00",
    "allowance_amount": 330.00,
    "allowance_days": 2.5,
    "destination_city": "上海",
    "travel_period": "2026-04-08 09:00 ~ 2026-04-10 21:00"
  }
}
```

## 展示格式示例

### 补助标准查询

```
💵 上海差旅补助标准

═══════════════════════════════════════

📋 基本标准
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
职级：普通员工
城市等级：一线城市
日补助：¥150.00

═══════════════════════════════════════

📐 计算规则
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 4小时及以下：不发放
• 超过4小时且不满8小时：发放50%
• 8小时及以上：发放100%
• 统一供餐时按规则扣减
```

### 补助申请成功

```
✅ 差旅补助申请已提交

═══════════════════════════════════════

📋 申请信息
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
补助单号：TA202604110001
出差单号：TRIP202604010001
出差城市：上海
补助天数：2.5天
补助金额：¥330.00
状态：🟡 待审批

═══════════════════════════════════════

🧮 计算说明
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
基础金额：¥375.00
扣减金额：¥45.00
最终金额：¥330.00

═══════════════════════════════════════

💡 操作提示
• 回复"审批进度"查看当前流程
• 回复"补助详情"查看完整核算明细
• 回复"撤回"撤回未审批申请
```

## API接口列表

| 接口名称 | 功能 | 参数 |
|:---|:---|:---|
| get_allowance_standard | 查询补助标准 | level, city, allowance_type |
| calculate_allowance | 计算补助 | trip_id, level, destination_city, departure_time, return_time |
| create_allowance_claim | 创建补助申请 | trip_id, allowance_amount, allowance_days |
| get_allowance_detail | 查询补助详情 | claim_id |
| submit_allowance_claim | 提交补助申请 | claim_id |
| approve_allowance_claim | 审批补助申请 | claim_id, action, comment |
| withdraw_allowance_claim | 撤回补助申请 | claim_id |
| get_allowance_history | 查询历史记录 | user_id, start_date, end_date |
| get_allowance_stats | 获取补助统计 | start_date, end_date, department |

## 补助单状态说明

| 状态 | 说明 |
|:---|:---|
| draft | 草稿 |
| pending | 待提交 |
| pending_approval | 待审批 |
| approved | 已通过 |
| rejected | 已驳回 |
| processing | 发放处理中 |
| paid | 已发放 |
| cancelled | 已取消 |
| expired | 已过期 |

## 审批流程

### 标准流程

```
补助计算
    ↓
创建补助单
    ↓
提交审批
    ↓
部门经理审批
    ↓
财务审核
    ↓
补助发放
```

### 异常流程

```
补助计算（存在异常）
    ↓
创建补助单
    ↓
补充说明
    ↓
部门经理审批
    ↓
费控复核
    ↓
财务审核
    ↓
补助发放
```

## 合规检查规则

1. **重复检查**
   - 同一出差单重复申请检查
   - 同一日期区间重复补助检查
   - 同一补助类型重复领取检查

2. **时效检查**
   - 补助申请提交时限检查
   - 过期申请说明校验
   - 退回后重新提交时效检查

3. **行程检查**
   - 出差申请与实际行程一致性检查
   - 返回时间早于出发时间校验
   - 出差缩短或取消后的重算检查

4. **扣减检查**
   - 统一供餐扣减校验
   - 统一接送扣减校验
   - 特殊地区补贴叠加规则校验
