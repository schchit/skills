---
name: enterprise-query
description: 封装东方微银企业查询API，支持通过企业名称/统一社会信用代码/组织机构代码/企业注册号查询34种企业数据类别；当用户需要查询企业信息并获取原始JSON响应时使用。
dependency:
  python:
    - coze-workload-identity>=0.1.0
license: MIT-0
---

# 企业查询接口封装

## 任务目标
- 本 Skill 用于：封装东方微银企业信息查询API接口
- 能力包含：通过企业标识查询多维度企业数据
- 触发条件：用户需要查询企业信息（企业名称/统一社会信用代码/组织机构代码/企业注册号）

## 前置准备
- 依赖说明：
  ```
  coze-workload-identity>=0.1.0
  ```
- API密钥配置：
  使用环境变量 `COZE_DFZY_ENTERPRISE_API_7627013027870851122` 存储API密钥

## 操作步骤

### 标准查询流程

1. **确定查询参数**
   - `keyword`：企业标识（必填），支持以下格式：
     - 企业名称
     - 统一社会信用代码
     - 组织机构代码
     - 企业注册号
   - `category`：数据类别编号（必填），34种类别见 [references/category_list.md](references/category_list.md)

2. **调用查询脚本**
   ```bash
   python /workspace/projects/enterprise-query/scripts/query_enterprise.py --keyword <企业标识> --category <类别编号>
   ```

3. **获取原始JSON响应**
   - 脚本直接返回API的原始JSON响应，不进行任何数据处理
   - 响应格式由API决定，包含 `code`、`data`、`msg` 等字段

## 资源索引

### 必要脚本
- [scripts/query_enterprise.py](scripts/query_enterprise.py)
  - 用途：封装东方微银API调用
  - 参数：
    - `--keyword`：企业标识（企业名称/统一社会信用代码/组织机构代码/企业注册号）
    - `--category`：数据类别编号（01-34）
  - 输出：原始JSON响应（原样返回，不做任何处理）

### 领域参考
- [references/category_list.md](references/category_list.md)
  - 何时读取：确定查询类别时
  - 内容：34种企业数据类别的编号和名称对照表

- [references/data_dictionary.md](references/data_dictionary.md)
  - 何时读取：理解字段含义时
  - 内容：数据字典说明，帮助理解API返回字段的含义

### 参考资产
- [assets/data_dictionary.xlsx](assets/data_dictionary.xlsx)
  - 用途：完整的数据字典，包含所有字段的详细说明

## 注意事项

- **原样返回**：脚本不对API响应做任何格式化、分析或计算，直接输出原始JSON
- **错误处理**：脚本会处理HTTP请求错误和API业务错误，通过退出码和错误信息反馈
- **数据字典**：仅作为参考文档，脚本不使用数据字典进行任何处理
- **参数验证**：脚本会验证必需参数是否存在，但不验证参数内容的合法性

## 使用示例

### 示例1：查询企业股东信息
```bash
# 查询企业"14079200A000046"的股东信息（类别01）
python /workspace/projects/enterprise-query/scripts/query_enterprise.py \
  --keyword "14079200A000046" \
  --category "01"
```

### 示例2：查询企业基本信息
```bash
# 查询企业"北京某某科技有限公司"的基本信息（类别00）
python /workspace/projects/enterprise-query/scripts/query_enterprise.py \
  --keyword "北京某某科技有限公司" \
  --category "00"
```

### 示例3：查询企业经营状况
```bash
# 查询企业经营状况（类别14）
python /workspace/projects/enterprise-query/scripts/query_enterprise.py \
  --keyword "911101085923434345" \
  --category "14"
```

## 响应示例

API返回的原始JSON格式（脚本原样返回）：

```json
{
    "code": 200,
    "data": {
        "gudong_now": [
            {
                "country": "",
                "conform": "货币",
                "currency": "人民币元",
                "subconam": "1600.0",
                "conprop": "80.00%",
                "inv": "张永爱",
                "invtype": "自然人股东",
                "subdate": "2029-08-18"
            },
            {
                "country": "",
                "conform": "货币",
                "currency": "人民币元",
                "subconam": "400.0",
                "conprop": "20.00%",
                "inv": "江君",
                "invtype": "自然人股东",
                "subdate": "2029-08-18"
            }
        ]
    },
    "msg": "请求成功"
}
```

**重要**：此为原始响应，脚本不进行任何字段解析、格式化或计算。
