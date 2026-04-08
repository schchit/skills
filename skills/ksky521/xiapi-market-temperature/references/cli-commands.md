# CLI 命令参考

本文档详细介绍市场温度分析相关的 CLI 命令。

## 核心命令

### 获取市场温度数据

```bash
npx daxiapi-cli@latest market temp
```

**功能说明**：获取市场温度四大指标数据

**返回字段**：

| 字段             | 类型   | 说明           | 取值范围  |
| ---------------- | ------ | -------------- | --------- |
| date             | string | 交易日期       | YYYY-MM-DD |
| valuation_temp   | number | 估值温度       | 0-100     |
| fear_greed_index | number | 恐贪指数       | 0-100     |
| trend_temp       | number | 趋势温度       | 0-100     |
| momentum_temp    | number | 动量温度       | 0-100     |

**返回示例**：

```json
[
  {
    "date": "2025-01-15",
    "valuation_temp": 45,
    "fear_greed_index": 25,
    "trend_temp": 35,
    "momentum_temp": 30
  },
  {
    "date": "2025-01-14",
    "valuation_temp": 45,
    "fear_greed_index": 28,
    "trend_temp": 33,
    "momentum_temp": 32
  }
]
```

**注意**：返回数组包含最近 20 个交易日的数据，最新日期在前。

## 配置命令

### 检查 Token 配置

```bash
npx daxiapi-cli@latest config get token
```

**功能说明**：检查当前 Token 配置状态

**返回示例**：

```bash
# 已配置
Token: YOUR_TOKEN_FROM_DAXIAPI

# 未配置
Token: (not set)
```

### 配置 Token

```bash
npx daxiapi-cli@latest config set token YOUR_TOKEN_FROM_DAXIAPI
```

**功能说明**：设置 API Token

**参数说明**：

- `YOUR_TOKEN_FROM_DAXIAPI`：从大虾皮网站获取的 API Token

## 命令选项

### 帮助信息

```bash
npx daxiapi-cli@latest --help
npx daxiapi-cli@latest market --help
npx daxiapi-cli@latest market temp --help
```

## 使用示例

### 示例 1：获取最新市场温度

```bash
npx daxiapi-cli@latest market temp
```

### 示例 2：检查配置状态

```bash
# 检查 Token 是否配置
npx daxiapi-cli@latest config get token

# 如果未配置，设置 Token
npx daxiapi-cli@latest config set token YOUR_TOKEN_FROM_DAXIAPI

# 验证配置是否成功
npx daxiapi-cli@latest market temp
```

## 错误处理

### 常见错误码

| 错误码 | 说明         | 解决方案                   |
| ------ | ------------ | -------------------------- |
| 401    | 认证失败     | 检查 Token 是否正确配置    |
| 404    | API 不存在   | 检查命令拼写               |
| 429    | 请求频率超限 | 等待 30-60 秒后重试        |
| 500    | 服务器错误   | 稍后重试                   |

### 错误示例

**401 认证失败**：

```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing API token"
}
```

**解决方案**：

```bash
# 检查 Token
npx daxiapi-cli@latest config get token

# 重新配置
npx daxiapi-cli@latest config set token YOUR_NEW_TOKEN
```

**429 请求频率超限**：

```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded"
}
```

**解决方案**：等待 30-60 秒后重试。

## 最佳实践

### DO ✅

1. 使用最新版本的 CLI：`npx daxiapi-cli@latest`
2. 首次使用前检查 Token 配置
3. 处理错误时先检查网络连接
4. 数据更新时间为每日收盘后

### DON'T ❌

1. 不要在盘中查询（数据未更新）
2. 不要频繁调用 API（避免触发限流）
3. 不要忽略错误提示

## 相关文档

- [API 参考文档](api-reference.md)
- [Token 配置指南](token-setup.md)
- [字段说明](field-descriptions.md)
