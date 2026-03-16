---
name: baidu-nearby
description: |
  百度能力集合 - 提供百度搜索和百度地图路线规划功能。
  包含：百度网页搜索(baidu_search)、路线规划(baidu_direction)、附近场所推荐(baidu_nearby)。
  Use when: 需要搜索网页、规划出行路线、查找附近餐饮/景点/酒店等位置服务时。
---

# Baidu Skills for OpenClaw

百度能力集合，提供搜索和位置服务。

## 功能

| 命令 | 说明 |
|------|------|
| `baidu_search` | 百度网页搜索 |
| `baidu_direction` | 百度地图路线规划 |
| `baidu_nearby` | 附近场所推荐 |

## 配置

设置百度 API Key（LBS 位置服务需要）：

```bash
export BAIDU_API_KEY="你的百度AK"
```

获取 AK：
1. 访问 https://lbsyun.baidu.com/
2. 注册开发者账号
3. 创建应用获取 AK

## 使用方法

### 百度搜索

```bash
python scripts/baidu_search.py "搜索关键词" [结果数量]
```

### 路线规划

```bash
python scripts/baidu_direction.py "起点地址" "终点地址" [driving|riding|walking|transit]
```

### 附近场所推荐

```bash
python scripts/baidu_nearby.py "位置" [类别] [半径(米)] [数量]
```

**支持的类别：**
- 餐饮/美食/餐厅
- 娱乐/休闲
- 景点/旅游/景区
- 酒店/住宿
- 购物/商场/超市
- 交通/地铁/公交

**示例：**
```bash
# 搜索三里屯附近美食
python scripts/baidu_nearby.py "北京市朝阳区三里屯" 餐饮 1000 5

# 搜索天安门附近景点
python scripts/baidu_nearby.py "天安门" 景点 5000 10

# 使用坐标搜索
python scripts/baidu_nearby.py "39.9,116.4" 娱乐
```

## 依赖

纯 Python 标准库实现，无需额外依赖。

## 安全说明

- 使用系统默认 SSL 证书验证
- 输入参数已做验证和清理
- 仅支持 HTTP/HTTPS 协议
