## 目录

- [接口概述](#接口概述)
- [SDK Request 类字段](#sdk-request-类字段)
- [terminal_device_data 参数](#terminal_device_data-参数json-字符串)
- [返回参数](#返回参数)
- [完整 SDK 调用示例](#完整-sdk-调用示例)
- [注意事项](#注意事项)
- [补充说明](#补充说明)

# 托管交易退款

## 接口概述

| 属性 | 值 |
|-----|-----|
| 汇付 API 端点 | `v2/trade/hosting/payment/htRefund` |
| 请求方式 | POST |
| SDK Request 类 | `V2TradeHostingPaymentHtrefundRequest` |
| 建议业务接口 | `POST /hfpay/htRefund` |

## SDK Request 类字段

`V2TradeHostingPaymentHtrefundRequest` 的专属字段：

| 字段 | setter 方法 | 类型 | 必填 | 说明 |
|------|-----------|------|------|------|
| reqDate | setReqDate() | String(8) | Y | 本次退款的请求日期 |
| reqSeqId | setReqSeqId() | String(128) | Y | 本次退款的请求流水号 |
| huifuId | setHuifuId() | String(32) | Y | 商户号 |
| ordAmt | setOrdAmt() | String(14) | Y | 退款金额，单位元，不超过原交易金额 |
| orgReqDate | setOrgReqDate() | String(8) | Y | 原交易的请求日期 |
| terminalDeviceData | setTerminalDeviceData() | String(2048) | Y | 设备信息（JSON 字符串），线上交易退款**必填** |
| riskCheckData | setRiskCheckData() | String(2048) | C | 风控信息（线上交易退款必填）（JSON 字符串） |
| bankInfoData | setBankInfoData() | String | N | 银行信息（JSON 字符串） |

通过 `setExtendInfo(Map)` 传入的扩展字段（**无独立 setter**）：

| 字段 | 必填 | 说明 |
|------|------|------|
| org_req_seq_id | Y | **原交易的请求流水号**（注意：此字段无专属 setter） |
| notify_url | N | 退款结果异步通知地址 |
| org_hf_seq_id | N | 原交易汇付全局流水号（与 org_req_seq_id 二选一） |

## terminal_device_data 参数（JSON 字符串）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| device_type | String | Y | 设备类型：`1`=SDK、`2`=手机浏览器、`3`=PC 浏览器、`4`=公众号/小程序 |
| devs_id | String(32) | N | 汇付机具号（通过汇付报备的机具必传） |

### device_type 与预下单类型对应关系

退款时 `device_type` 应与原交易的预下单类型匹配：

| 原交易 pre_order_type | 原交易场景 | 退款 device_type | 值 |
|----------------------|-----------|-----------------|-----|
| 1 | H5 手机网页支付 | 手机浏览器 | `"2"` |
| 1 | PC 网页支付 | PC 浏览器 | `"3"` |
| 2 | 支付宝小程序 | 公众号/小程序 | `"4"` |
| 3 | 微信小程序 | 公众号/小程序 | `"4"` |

> **提示**：如果不确定原交易渠道，使用 `"4"` 作为默认值通常可以通过校验。

## 返回参数

| 参数 | 类型 | 说明 |
|------|------|------|
| resp_code | String(8) | `00000000` 表示退款请求已受理 |
| resp_desc | String(128) | 响应描述 |
| huifu_id | String(32) | 商户号 |
| ord_amt | String(14) | 退款金额 |
| org_req_date | String(8) | 原交易请求日期 |
| org_req_seq_id | String(64) | 原交易请求流水号 |
| trans_stat | String(1) | 退款状态：P=处理中、S=成功、F=失败 |
| req_seq_id | String(64) | 本次退款的请求流水号 |

## 完整 SDK 调用示例

> **[关键陷阱] `org_req_seq_id` 无专属 setter！**
>
> 退款最重要的字段 `org_req_seq_id`（原交易流水号）**没有独立的 setter 方法**，必须通过 `extendInfoMap` 传入。如果你尝试调用 `request.setOrgReqSeqId()` 将导致编译错误。这是初次接入退款最常见的踩坑点。
>
> ```java
> // ✗ 错误 — 不存在此方法，编译报错
> request.setOrgReqSeqId("20240514165442868h32ss2g3s7vnxq");
>
> // ✓ 正确 — 通过 extendInfoMap 传入
> extendInfoMap.put("org_req_seq_id", "20240514165442868h32ss2g3s7vnxq");
> request.setExtendInfo(extendInfoMap);
> ```

```java
import com.huifu.bspay.sdk.opps.client.BasePayClient;
import com.huifu.bspay.sdk.opps.core.request.V2TradeHostingPaymentHtrefundRequest;
import com.huifu.bspay.sdk.opps.core.utils.DateTools;
import com.huifu.bspay.sdk.opps.core.utils.SequenceTools;

// 1. 构建请求
V2TradeHostingPaymentHtrefundRequest request = new V2TradeHostingPaymentHtrefundRequest();
request.setReqDate(DateTools.getCurrentDateYYYYMMDD());
request.setReqSeqId(SequenceTools.getReqSeqId32());
request.setHuifuId("6666000123123123");
request.setOrdAmt("1.00");                                 // 退款金额
request.setOrgReqDate("20240514");                          // 原交易日期

// 2. 设置设备信息（线上交易退款必填）
// device_type: 1=SDK, 2=手机浏览器, 3=PC浏览器, 4=公众号/小程序
request.setTerminalDeviceData("{\"device_type\":\"4\"}");
request.setRiskCheckData("");
request.setBankInfoData("");

// 3. 设置扩展参数（org_req_seq_id 无专属 setter，必须通过 extendInfoMap 传入）
Map<String, Object> extendInfoMap = new HashMap<>();
extendInfoMap.put("org_req_seq_id", "20240514165442868h32ss2g3s7vnxq"); // 原交易流水号
extendInfoMap.put("notify_url", "https://your-domain.com/refund-notify");
request.setExtendInfo(extendInfoMap);

// 4. 发起请求
Map<String, Object> response = BasePayClient.request(request, false);

// 5. 处理响应
String respCode = (String) response.get("resp_code");
String transStat = (String) response.get("trans_stat");

if ("00000000".equals(respCode)) {
    if ("P".equals(transStat)) {
        // 退款处理中，等待异步通知或轮询退款查询
    } else if ("S".equals(transStat)) {
        // 退款成功
    }
}
```

## 请求 JSON 示例

```json
{
    "sys_id": "6666000108840829",
    "product_id": "YYZY",
    "data": {
        "req_date": "20240515",
        "req_seq_id": "20240515101010868refund01",
        "huifu_id": "6666000109133323",
        "ord_amt": "1.00",
        "org_req_date": "20240514",
        "org_req_seq_id": "20240514165442868h32ss2g3s7vnxq",
        "terminal_device_data": "{\"device_type\":\"4\"}",
        "notify_url": "https://your-domain.com/refund-notify"
    }
}
```

## 返回 JSON 示例

```json
{
    "data": {
        "resp_code": "00000000",
        "resp_desc": "处理成功",
        "huifu_id": "6666000109133323",
        "ord_amt": "1.00",
        "org_req_date": "20240514",
        "org_req_seq_id": "20240514165442868h32ss2g3s7vnxq",
        "trans_stat": "P",
        "req_seq_id": "20240515101010868refund01"
    }
}
```

## 注意事项

1. **`org_req_seq_id` 无专属 setter**，必须通过 `extendInfoMap` 传入，不要尝试调用不存在的 setter
2. `terminalDeviceData`、`riskCheckData`、`bankInfoData` 是**专属字段**（有独立 setter），直接调用 setter
3. 退款金额不能超过原交易金额
4. `resp_code=00000000` 仅表示退款请求**已受理**，退款最终结果以异步通知或查询为准
5. 相同的 `orgReqSeqId` 重复退款会被拒绝，需做幂等校验
6. `device_type` 根据原交易渠道选择：小程序/公众号用 `"4"`，H5 手机用 `"2"`，PC 用 `"3"`
7. 退款涉及资金变动，日志中记录关键参数但**避免打印完整密钥**

## 补充说明

### 原交易标识（三选一）

退款请求支持以下三种方式定位原交易（通过 extendInfoMap 传入）：

| 字段 | 说明 |
|------|------|
| org_req_seq_id | 原交易请求流水号（最常用） |
| org_hf_seq_id | 原交易汇付全局流水号 |
| org_party_order_id | 原交易商户订单号 |

三者选其一即可，推荐使用 `org_req_seq_id`。

### risk_check_data 详细字段（线上交易退款必填）

| 参数 | 类型 | 说明 |
|------|------|------|
| ip_addr | String | IP 地址 |
| base_station | String | 基站信息 |
| latitude | String | 纬度 |
| longitude | String | 经度 |

### 垫资退款参数（可选）

| 字段 | 说明 |
|------|------|
| loan_flag | Y=垫资退款、N=普通退款（默认） |
| loan_undertaker | 垫资承担方 huifu_id，为空则各自承担 |
| loan_acct_type | 垫资账户类型：01=基本户、05=充值户（默认） |

### 异步通知参数

退款结果通过异步通知回调 notify_url，关键字段：

| 参数 | 类型 | 说明 |
|------|------|------|
| resp_code | String(8) | 业务响应码 |
| resp_desc | String(512) | 响应描述 |
| huifu_id | String(32) | 商户号 |
| req_date | String(8) | 退款请求日期 |
| req_seq_id | String(128) | 退款请求流水号 |
| trans_stat | String(1) | 退款状态：S=成功、F=失败 |
| ord_amt | String(14) | 退款金额 |
| actual_ref_amt | String(14) | 实际退款金额 |
| total_ref_amt | String(14) | 累计退款金额 |
| org_req_date | String(8) | 原交易日期 |
| org_req_seq_id | String(128) | 原交易流水号 |
| org_ord_amt | String(14) | 原订单金额 |
| fee_amt | String(14) | 退款手续费退还金额 |
