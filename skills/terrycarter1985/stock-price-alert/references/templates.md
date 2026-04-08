# External Service Integration Template Notes

该技能属于“外部服务集成类”，集成了以下外部能力：

- 股票行情接口（默认 yfinance，可替换）
- Gmail API 邮件提醒
- Sonos CLI 语音播报

目录规范：

- 技能定义：`skills/stock-price-alert/`
- 运行脚本：`scripts/stock_price_alert.py`
- 示例配置：`config/stock-price-alert.example.json`

发布目标：

- slug: `stock-price-alert`
- version: `1.0.0`
- changelog: `新增股价异动实时提醒功能`
