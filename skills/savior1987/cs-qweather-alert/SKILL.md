# cs-qweather-alert

和风天气预警查询工具。

## 使用场景

当需要查询某个城市的天气预警信息时使用此 skill。

## 功能

- 根据城市名查询天气预警
- 支持 16 种预警类型：大风、高温、台风、暴雨、暴雪、寒潮、大雾、霾、雷电、冰雹、沙尘暴、干旱、洪涝、地质灾害、森林火险等
- 预警级别 emoji 可视化（🔴极严重、🟠严重、🟡中等、🔵轻微）
- 自动缓存城市经纬度，减少 API 调用
- 日志记录完整请求和响应

## 依赖

- Python 3
- 无需额外 pip 包（仅使用标准库）

## 环境变量

- `QWEATHER_API_HOST` - 和风天气 API Host（如 `https://api.qweather.com` 或 `https://THISISADEMO.re.qweatherapi.com`）
- `QWEATHER_CITY` - 默认城市名称（可选，作为备用）

## Token 配置

- 默认从 `~/.myjwtkey/last-token.dat` 读取
- 也可通过 `--token` 参数指定

## 使用方法

```bash
python3 cs-qweather-alert/scripts/qweather-get-weather-alert.py <城市名> [--host API_HOST] [--token JWT_TOKEN]
```

### 示例

```bash
# 查询北京天气预警
python3 cs-qweather-alert/scripts/qweather-get-weather-alert.py 北京

# 指定 API Host
python3 cs-qweather-alert/scripts/qweather-get-weather-alert.py 上海 --host https://THISISADEMO.re.qweatherapi.com
```

## 输出

- 终端输出格式化的预警信息
- 日志写入 `/tmp/cslog/qweather-get-weather-alert-YYYYMMDD.log`

## 注意事项

- 城市经纬度缓存保存在 `data/location.json`（脚本同目录）
- 日志中敏感信息已脱敏（JWT token 只显示前8后4位）
- 预警信息来自和风天气 API
