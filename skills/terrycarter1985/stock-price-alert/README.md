# Stock Price Alert

对接股票行情接口，监控持仓价格异动，并联动邮件提醒与 Sonos 语音播报。

## 简介

这是一个外部服务集成类技能，用于在 OpenClaw 个人助手工作区内管理股票持仓异动提醒。它参考现有股票公告脚本的目录规范：运行逻辑放在 `scripts/`，技能定义放在 `skills/stock-price-alert/`。

## 功能特性

- 对接股票行情接口获取最新价格
- 读取持仓配置并计算价格变化
- 基于百分比或金额阈值识别异动
- 通过 Gmail 发送提醒邮件
- 通过 Sonos 播放语音提醒
- 支持 dry-run 和结构化 JSON 输出

## 快速开始

1. 准备持仓配置 JSON
2. 配置 Gmail token、收件邮箱与 Sonos 音箱名
3. 运行：

```bash
python scripts/stock_price_alert.py --config config/stock-price-alert.example.json
```

## 详细文档

请参阅 [SKILL.md](SKILL.md) 获取完整文档。

## 许可证

本项目采用 CC BY-NC-SA 4.0 许可证。
