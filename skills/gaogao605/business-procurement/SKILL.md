---
name: fb-procurement-skill
description: 企业采购助手，支持采购申请、预算占用校验、供应商比价、审批流转、收货确认、付款状态查询、采购统计分析等功能。Invoke when user needs to create purchase requests, compare suppliers, check budget, or track procurement orders.
version: 1.0.0
metadata: {"openclaw": {"emoji": "📦", "category": "finance", "tags": ["企业采购", "采购申请", "供应商", "预算校验", "审批"], "requires": {"bins": ["python3"]}, "required": true}}
---
# 企业采购助手 (fb-procurement-skill)

## 技能描述

企业采购助手面向办公用品、行政物资、IT设备、会议服务等企业内部采购场景，支持采购申请创建、预算校验、供应商比价、审批管理、收货确认、付款跟踪和采购统计分析。通过统一的采购流程和费控规则，帮助企业实现采购透明化和成本可控。

---

⚠️ 【重要约束】
- 必须填写采购用途、部门、预算归属、采购明细
- 超预算、超权限或受控品类采购必须进入审批流程
- 达到金额阈值的采购必须至少记录两家供应商比价信息
- 相同商品短期重复采购必须触发预警
- 收货确认后方可进入付款流程
- 发票、订单、收货信息必须保持一致，不得重复核销

---

## 核心功能

### 1. 采购申请
- 创建采购申请单
- 录入商品或服务清单
- 填写用途与预算归属
- 选择紧急程度
- 指定收货人和收货地址
- 提交采购审批

### 2. 预算与权限校验
- 查询预算余额
- 占用预算额度
- 校验采购类别权限
- 超预算自动预警
- 跨部门预算申请校验
- 项目预算归属校验

### 3. 供应商管理与比价
- 查询候选供应商
- 记录供应商报价
- 自动生成比价结果
- 标记推荐供应商
- 跟踪采购议价记录
- 保存比价依据

### 4. 订单执行管理
- 生成采购订单
- 查询订单详情
- 跟踪发货状态
- 确认收货
- 查询付款状态
- 查询发票状态

### 5. 审批与异常处理
- 查询审批进度
- 查看审批意见
- 撤回未审批申请
- 处理驳回重提
- 查询异常订单
- 跟踪延期交付

### 6. 统计分析
- 月度采购统计
- 部门采购对比
- 品类采购分析
- 供应商使用分析
- 成本节约分析
- 重复采购预警统计

## 触发场景

1. **采购申请**
   - "帮我创建一个办公用品采购申请"
   - "我要采购一批笔记本电脑"
   - "给市场部提一个物料采购单"
   - "申请采购会议服务"

2. **预算与权限查询**
   - "这个采购是否超预算"
   - "查看行政部采购预算余额"
   - "我有没有采购IT设备的权限"
   - "这笔采购要不要审批"

3. **供应商比价**
   - "帮我比较这三个供应商报价"
   - "办公椅采购哪家更便宜"
   - "生成这笔采购的比价结果"
   - "查询推荐供应商"

4. **订单与收货管理**
   - "查看采购单 PO202604110001"
   - "确认这笔采购已收货"
   - "查询这笔采购什么时候付款"
   - "看看发票有没有上传"

5. **统计分析**
   - "查看本月采购统计"
   - "分析各部门采购金额"
   - "有哪些重复采购预警"
   - "看看办公用品采购趋势"

## 采购类型

| 采购类型 | 代码 | 说明 | 默认审批 |
|:---|:---|:---|:---|
| 办公用品 | OFFICE_SUPPLIES | 文具、耗材、桌面用品 | 否 |
| IT设备 | IT_EQUIPMENT | 电脑、显示器、网络设备 | 是 |
| 行政物资 | ADMIN_SUPPLIES | 饮水、保洁、日杂物资 | 否 |
| 市场物料 | MARKETING_MATERIAL | 宣传品、活动物料 | 是 |
| 会议服务 | MEETING_SERVICE | 场地、茶歇、布置服务 | 是 |
| 专业服务 | PROFESSIONAL_SERVICE | 外包、人力、设计、咨询 | 是 |

## 预算与比价规则

### 审批与比价阈值

| 金额区间 | 审批要求 | 比价要求 |
|:---|:---|:---|
| ¥0 - ¥1,000 | 部门内确认 | 可不比价 |
| ¥1,001 - ¥10,000 | 部门负责人审批 | 至少2家报价 |
| ¥10,001 - ¥50,000 | 部门负责人 + 财务审批 | 至少2家报价 |
| ¥50,001 以上 | 部门负责人 + 财务 + 管理层审批 | 至少3家报价 |

### 重复采购预警规则
- 30天内同部门同品类重复采购触发提醒
- 15天内同一商品型号重复申请触发高优先级预警
- 已有未完成订单时再次申请相同商品需说明原因

## 输入参数

### 采购申请

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---|:---|
| request_type | string | 是 | 采购类型 |
| department | string | 是 | 申请部门 |
| budget_id | string | 是 | 预算编号 |
| purpose | string | 是 | 采购用途 |
| urgency | string | 否 | 紧急程度：low / medium / high |
| delivery_address | string | 否 | 收货地址 |
| receiver_name | string | 否 | 收货人 |
| items | array | 是 | 商品或服务明细 |
| project_code | string | 否 | 项目编码 |
| remarks | string | 否 | 备注 |

### 采购明细

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---|:---|
| item_name | string | 是 | 商品名称 |
| specification | string | 否 | 规格型号 |
| quantity | int | 是 | 数量 |
| unit | string | 否 | 单位 |
| unit_price | float | 是 | 预估单价 |
| category | string | 是 | 品类 |

### 供应商比价

| 参数 | 类型 | 必填 | 说明 |
|:---|:---|:---|:---|
| request_id | string | 是 | 采购申请单号 |
| supplier_quotes | array | 是 | 供应商报价列表 |
| recommended_supplier | string | 否 | 推荐供应商 |
| comparison_note | string | 否 | 比价说明 |

## 输出格式

### 采购申请结果

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "request_id": "PR202604110001",
    "request_type": "IT_EQUIPMENT",
    "department": "技术部",
    "budget_id": "BUD2026IT001",
    "total_amount": 24500.00,
    "budget_check": {
      "within_budget": true,
      "remaining_budget": 125500.00,
      "warnings": []
    },
    "approval_required": true,
    "quote_required": true,
    "status": "pending_approval",
    "create_time": "2026-04-11 16:45:00"
  }
}
```

### 比价结果

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "request_id": "PR202604110001",
    "quote_count": 3,
    "recommended_supplier": "京采科技",
    "lowest_price": 23800.00,
    "highest_price": 25600.00,
    "price_gap": 1800.00,
    "recommendation_reason": "价格最低且交付周期最短"
  }
}
```

### 采购订单详情

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "order_id": "PO202604110001",
    "request_id": "PR202604110001",
    "status": "delivering",
    "supplier_name": "京采科技",
    "invoice_status": "uploaded",
    "receipt_status": "pending",
    "payment_status": "waiting",
    "delivery_date": "2026-04-14"
  }
}
```

## 展示格式示例

### 采购申请成功

```
✅ 企业采购申请已创建

═══════════════════════════════════════

📋 申请信息
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
申请单号：PR202604110001
采购类型：IT设备
申请部门：技术部
预算编号：BUD2026IT001
申请金额：¥24,500.00
状态：🟡 待审批

═══════════════════════════════════════

✅ 预算校验
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ 在预算范围内
剩余预算：¥125,500.00
⚠️ 需补充供应商比价信息

═══════════════════════════════════════

💡 操作提示
• 回复"比价"补充供应商报价
• 回复"审批进度"查看审批节点
• 回复"订单详情"查看后续执行状态
```

### 比价结果展示

```
📦 供应商比价结果

| 供应商 | 报价 | 交付周期 | 发票 | 备注 |
|:---|---:|:---:|:---:|:---|
| 京采科技 | ¥23,800 | 3天 | 可开专票 | 推荐 |
| 云采办公 | ¥24,600 | 5天 | 可开专票 | 常用供应商 |
| 北辰设备 | ¥25,600 | 4天 | 可开专票 | 含上门安装 |

💡 推荐供应商：京采科技
💡 原因：价格最低且交付周期最短
```

## API接口列表

| 接口名称 | 功能 | 参数 |
|:---|:---|:---|
| create_purchase_request | 创建采购申请 | request_type, department, budget_id, purpose, items |
| check_purchase_budget | 校验预算 | budget_id, total_amount, department |
| get_purchase_request_detail | 查询采购申请详情 | request_id |
| compare_suppliers | 供应商比价 | request_id, supplier_quotes |
| submit_purchase_approval | 提交采购审批 | request_id |
| approve_purchase_request | 审批采购申请 | request_id, action, comment |
| create_purchase_order | 生成采购订单 | request_id, supplier_id |
| get_purchase_order_detail | 查询采购订单详情 | order_id |
| confirm_receipt | 确认收货 | order_id |
| upload_purchase_invoice | 上传采购发票 | order_id, invoice_no, invoice_amount |
| get_procurement_stats | 获取采购统计 | start_date, end_date, department |

## 采购状态说明

| 状态 | 说明 |
|:---|:---|
| draft | 草稿 |
| pending | 待提交 |
| pending_approval | 待审批 |
| approved | 已通过 |
| rejected | 已驳回 |
| ordered | 已下单 |
| delivering | 配送中 |
| received | 已收货 |
| completed | 已完成 |
| cancelled | 已取消 |

## 审批流程

### 标准流程

```
创建采购申请
    ↓
预算校验
    ↓
提交审批
    ↓
部门负责人审批
    ↓
生成采购订单
    ↓
收货确认
    ↓
付款处理
```

### 高金额流程

```
创建采购申请
    ↓
预算校验与比价
    ↓
提交审批
    ↓
部门负责人审批
    ↓
财务审批
    ↓
管理层审批
    ↓
生成采购订单
    ↓
收货确认
    ↓
付款处理
```

## 合规检查规则

1. **预算检查**
   - 预算余额是否充足
   - 预算归属是否匹配部门或项目
   - 超预算申请是否附带说明

2. **权限检查**
   - 采购类型与申请人权限匹配
   - 高价值采购是否具备审批权限
   - 跨部门采购是否经过授权

3. **比价检查**
   - 是否达到最低比价家数要求
   - 比价信息是否完整
   - 推荐供应商理由是否充分

4. **重复检查**
   - 短期同类商品重复采购检查
   - 未完成订单重复申请检查
   - 发票重复核销检查
