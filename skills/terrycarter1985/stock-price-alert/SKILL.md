---
name: stock-price-alert
description: 对接股票行情接口，监控持仓价格异动，并联动邮件提醒与 Sonos 语音播报。
license: LICENSE-CC-BY-NC-SA 4.0 in LICENSE.txt
author: OpenClaw Assistant
---

# Stock Price Alert

一个用于个人持仓股价异动实时提醒的外部服务集成类技能。

## 使用场景

当用户希望在个人助手工作区中，持续监控股票持仓价格变化，并在达到预设阈值时：

1. 拉取股票行情接口获取最新价格
2. 判断是否触发异动条件
3. 通过 Gmail 发送提醒邮件
4. 通过 Sonos 进行语音播报

应使用此技能。

## 前置条件

- Python 3.10+
- 已安装依赖：`yfinance`、`pandas`、`python-dotenv`、`google-api-python-client`、`google-auth`、`google-auth-oauthlib`
- 已配置 Gmail API 授权文件或 token
- 已可通过 `sonos` CLI 访问目标音箱
- 已准备持仓配置文件（JSON）

建议环境变量：

- `STOCK_ALERT_PORTFOLIO_PATH`：持仓配置 JSON 路径
- `STOCK_ALERT_RECIPIENT_EMAIL`：接收提醒的邮箱
- `STOCK_ALERT_SONOS_SPEAKER`：Sonos 音箱名称
- `STOCK_ALERT_GMAIL_TOKEN_PATH`：Gmail token 路径，默认 `config/token.json`
- `STOCK_ALERT_ENABLE_EMAIL`：是否启用邮件，`true/false`
- `STOCK_ALERT_ENABLE_SONOS`：是否启用 Sonos，`true/false`

## 工作流

1. 输入接收
   - 接收持仓配置路径、阈值设置、通知开关等参数
   - 校验股票代码、阈值和必要凭证是否存在

2. 行情获取
   - 通过行情接口（默认 `yfinance`）获取最近两日或最近一次可用收盘/最新价格
   - 计算每个标的的绝对变化与百分比变化

3. 异动判断
   - 按每个持仓独立阈值判断是否触发
   - 支持价格涨跌幅阈值、绝对金额阈值
   - 生成触发清单与摘要

4. 提醒执行
   - 若触发：生成 HTML 邮件并发送
   - 若触发：生成自然语言播报文案并交给 Sonos CLI 播放
   - 若未触发：输出未触发结果，避免误报

5. 结果输出
   - 返回结构化 JSON 摘要
   - 标记每个通知通道是否成功

## 输入参数

推荐输入来源为 JSON 配置文件，格式示例：

```json
{
  "portfolio_name": "daily-holdings",
  "default_threshold_percent": 3.0,
  "default_threshold_amount": 0,
  "holdings": [
    {
      "ticker": "AAPL",
      "shares": 15,
      "threshold_percent": 2.5
    },
    {
      "ticker": "NVDA",
      "shares": 10,
      "threshold_percent": 4.0
    }
  ]
}
```

## 输出格式

脚本输出 JSON，例如：

```json
{
  "triggered": true,
  "date": "2026-04-09",
  "portfolio_name": "daily-holdings",
  "alerts": [
    {
      "ticker": "AAPL",
      "change_percent": 3.21,
      "threshold_percent": 2.5
    }
  ],
  "email_sent": true,
  "sonos_announced": true
}
```

## 使用示例

### 1. 执行一次检查

```bash
python scripts/stock_price_alert.py --config config/stock-price-alert.example.json
```

### 2. 只做检测，不发送通知

```bash
python scripts/stock_price_alert.py --config config/stock-price-alert.example.json --dry-run
```

### 3. 使用环境变量默认配置

```bash
STOCK_ALERT_PORTFOLIO_PATH=config/stock-price-alert.example.json python scripts/stock_price_alert.py
```

## 注意事项

- `yfinance` 更适合个人自动化场景，不保证严格低延迟；如需更强实时性，可替换为券商或付费 API。
- Gmail 与 Sonos 任一通道失败时，不应影响另一个通道执行。
- 阈值判断应基于用户配置，不应写死在脚本中。
- 配置与脚本分离：脚本在 `scripts/`，技能定义在 `skills/stock-price-alert/`。

## 错误处理

- 行情获取失败：返回错误并标记未完成检测
- 配置文件格式错误：直接报错退出
- Gmail 认证失败：仅标记邮件失败
- Sonos 播报失败：仅标记音箱播报失败
