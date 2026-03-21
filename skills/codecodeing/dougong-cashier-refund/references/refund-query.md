## 目录

- [接口概述](#接口概述)
- [SDK Request 类字段](#sdk-request-类字段)
- [返回参数](#返回参数)
- [完整 SDK 调用示例](#完整-sdk-调用示例)
- [流水号关系说明](#流水号关系说明)
- [注意事项](#注意事项)

# 退款结果查询

## 接口概述

| 属性 | 值 |
|-----|-----|
| 汇付 API 端点 | `v2/trade/hosting/payment/queryRefundInfo` |
| 请求方式 | POST |
| SDK Request 类 | `V2TradeHostingPaymentQueryrefundinfoRequest` |
| 建议业务接口 | `POST /hfpay/queryRefundInfo` |

## SDK Request 类字段

`V2TradeHostingPaymentQueryrefundinfoRequest` 的专属字段：

| 字段 | setter 方法 | 类型 | 必填 | 说明 |
|------|-----------|------|------|------|
| reqDate | setReqDate() | String(8) | Y | 本次查询的请求日期 |
| reqSeqId | setReqSeqId() | String(128) | Y | 本次查询的请求流水号 |
| huifuId | setHuifuId() | String(32) | Y | 商户号 |
| orgReqDate | setOrgReqDate() | String(8) | Y | **退款交易**的请求日期（来自退款接口返回） |
| orgReqSeqId | setOrgReqSeqId() | String(64) | N | **退款交易**的请求流水号（与 orgHfSeqId 二选一） |
| orgHfSeqId | setOrgHfSeqId() | String(128) | N | **退款交易**的汇付全局流水号（与 orgReqSeqId 二选一） |

> **注意**：此处 `orgReqSeqId` 是**退款请求**的流水号（不是原支付交易的流水号）。

## 返回参数

| 参数 | 类型 | 说明 |
|------|------|------|
| resp_code | String(8) | `00000000` 表示查询成功 |
| resp_desc | String(128) | 响应描述 |
| huifu_id | String(32) | 商户号 |
| trans_stat | String(1) | **退款状态**：P=处理中、S=成功、F=失败 |
| ord_amt | String(14) | 退款金额 |
| org_req_date | String(8) | 退款交易请求日期 |
| org_req_seq_id | String(64) | 退款交易请求流水号 |
| org_hf_seq_id | String(40) | 退款交易汇付全局流水号 |

## 完整 SDK 调用示例

```java
import com.huifu.bspay.sdk.opps.client.BasePayClient;
import com.huifu.bspay.sdk.opps.core.request.V2TradeHostingPaymentQueryrefundinfoRequest;
import com.huifu.bspay.sdk.opps.core.utils.DateTools;
import com.huifu.bspay.sdk.opps.core.utils.SequenceTools;

// 1. 构建请求
V2TradeHostingPaymentQueryrefundinfoRequest request = new V2TradeHostingPaymentQueryrefundinfoRequest();
request.setReqDate(DateTools.getCurrentDateYYYYMMDD());
request.setReqSeqId(SequenceTools.getReqSeqId32());
request.setHuifuId("6666000123123123");
request.setOrgReqDate("20240515");                          // 退款请求的日期
request.setOrgReqSeqId("20240515101010868refund01");         // 退款请求的流水号

// 2. 发起请求
Map<String, Object> response = BasePayClient.request(request, false);

// 3. 处理响应
String respCode = (String) response.get("resp_code");
String transStat = (String) response.get("trans_stat");

if ("00000000".equals(respCode)) {
    switch (transStat) {
        case "S": // 退款成功
            break;
        case "F": // 退款失败
            break;
        case "P": // 退款处理中
            break;
    }
}
```

## 请求 JSON 示例

```json
{
    "sys_id": "6666000108840829",
    "product_id": "YYZY",
    "data": {
        "req_date": "20240516",
        "req_seq_id": "20240516101010868rquery01",
        "huifu_id": "6666000109133323",
        "org_req_date": "20240515",
        "org_req_seq_id": "20240515101010868refund01"
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
        "trans_stat": "S",
        "ord_amt": "1.00",
        "org_req_date": "20240515",
        "org_req_seq_id": "20240515101010868refund01"
    }
}
```

## 流水号关系说明

退款查询涉及三层流水号，容易混淆：

```
预下单 → req_seq_id = "A001" (原支付交易流水号)
  ↓
退款   → req_seq_id = "B001" (退款请求流水号), org_req_seq_id = "A001"
  ↓
退款查询 → req_seq_id = "C001" (本次查询流水号), org_req_seq_id = "B001" (退款流水号)
```

## 注意事项

1. `orgReqSeqId` 是**退款请求**的流水号，不是原支付交易的流水号
2. `orgReqDate` 是**退款请求**的日期
3. `orgReqSeqId` 和 `orgHfSeqId` 二选一即可查询
4. 退款处理中（trans_stat=P）时应稍后重试查询
