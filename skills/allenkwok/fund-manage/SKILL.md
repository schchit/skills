---
name: fund-query
description: 查询中国公募基金信息，支持收藏和分组管理。包括基金名称、单位净值、估算净值、涨跌幅等。使用天天基金 API 获取实时数据。当用户输入基金代码（6 位数字）、询问基金净值、或需要管理基金收藏/分组时使用此技能。
---

# 基金查询技能

通过基金代码查询中国公募基金的名称、净值和涨跌幅信息，支持收藏和分组管理功能。

## 快速使用

### 查询单只基金
```
查询基金 161725
161725 净值
帮我看看 000001 基金
```

### 收藏管理
```
把 161725 加入收藏
收藏 000001 到白酒分组
显示我的基金收藏
刷新所有收藏的基金
从收藏移除 161725
```

### 分组管理
```
创建分组 白酒
创建分组 科技 重仓
显示所有分组
查看白酒分组的基金
刷新白酒分组
删除分组 重仓
```

## 命令行用法

### 查询
```bash
# 查询单只基金
python scripts/fund_query.py 161725

# 查询并添加到收藏（无分组）
python scripts/fund_query.py 161725 --add
```

### 收藏管理
```bash
# 添加基金到收藏（可指定多个分组）
python scripts/fund_query.py add 161725 白酒 重仓

# 添加基金到收藏（无分组）
python scripts/fund_query.py add 000001

# 从收藏移除
python scripts/fund_query.py remove 161725

# 显示收藏列表（全部）
python scripts/fund_query.py list

# 显示指定分组的基金（包括无分组的）
python scripts/fund_query.py list 白酒

# 刷新所有收藏
python scripts/fund_query.py refresh

# 刷新指定分组的基金
python scripts/fund_query.py refresh 白酒

# 更新基金的分组
python scripts/fund_query.py groups 161725 白酒 重仓
```

### 分组管理
```bash
# 创建分组
python scripts/fund_query.py group create 白酒

# 删除分组（不删除基金，仅移除分组关联）
python scripts/fund_query.py group delete 白酒

# 列出所有分组
python scripts/fund_query.py group list
```

## 数据源

- **API**: 天天基金网 (fund.eastmoney.com)
- **接口**: `https://fundgz.1234567.com.cn/js/{fund_code}.js`
- **数据格式**: JSONP

## 返回字段说明

| 字段 | 说明 |
|------|------|
| fund_code | 基金代码 (6 位数字) |
| fund_name | 基金名称 |
| estimated_net_value | 估算净值 (盘中实时) |
| unit_net_value | 单位净值 (最新确认) |
| growth_rate | 涨跌幅 (%) |
| trend | 趋势 (上涨/下跌/持平) |
| net_value_date | 净值日期 |
| valuation_time | 估值时间 |
| groups | 所属分组列表 |
| status | 状态 (success/error) |

## 分组功能

### 设计理念

- **一个基金可以属于多个分组**：如"白酒"和"重仓"
- **无分组的基金**：可以在任何分组查询中看到（作为全局基金）
- **删除分组**：只删除分组本身，不删除基金，基金变为无分组状态

### 数据存储
- **收藏数据**: `data/favorites.json`
- **分组数据**: `data/groups.json`
- **格式**: JSON

### 分组操作

**创建分组**:
```python
from scripts.fund_query import create_group

result = create_group("白酒")
# 返回：{"status": "success", "message": "已创建分组 '白酒'"}
```

**删除分组**:
```python
from scripts.fund_query import delete_group

result = delete_group("白酒")
# 删除分组，同时从所有基金中移除该分组关联
```

**列出分组**:
```python
from scripts.fund_query import list_groups

groups = list_groups()
# 返回：{"白酒": {"created_time": "...", "description": ""}, ...}
```

### 收藏操作

**添加收藏（指定分组）**:
```python
from scripts.fund_query import add_favorite

result = add_favorite("161725", ["白酒", "重仓"])
# 返回：{"status": "success", "message": "已添加..."}
```

**添加收藏（无分组）**:
```python
result = add_favorite("000001", [])
# 无分组的基金可以在任何分组查询中看到
```

**更新分组**:
```python
from scripts.fund_query import update_fund_groups

result = update_fund_groups("161725", ["白酒"])
```

**获取收藏列表**:
```python
from scripts.fund_query import list_favorites

# 获取全部（包括无分组的）
all_favorites = list_favorites()

# 获取指定分组的（包括无分组的）
baijiu_favorites = list_favorites("白酒")

# 获取无分组的
no_group_favorites = list_favorites("")
```

**刷新收藏**:
```python
from scripts.fund_query import refresh_favorites

# 刷新全部
all_results = refresh_favorites()

# 刷新指定分组
baijiu_results = refresh_favorites("白酒")
```

## 错误处理

脚本会处理以下错误情况：

- 基金代码格式错误 (非 6 位数字)
- 网络请求失败
- 数据解析错误
- 基金代码不存在
- 分组不存在

错误返回示例：
```json
{
  "fund_code": "123",
  "status": "error",
  "message": "基金代码格式错误，应为 6 位数字"
}
```

## 使用模式

### 模式 1: 直接调用脚本

```python
import sys
sys.path.append('scripts')
from fund_query import get_fund_info, format_result, add_favorite, refresh_favorites

# 查询
result = get_fund_info("161725")
print(format_result(result))

# 收藏到多个分组
add_result = add_favorite("161725", ["白酒", "重仓"])
print(add_result["message"])

# 刷新指定分组
refresh_results = refresh_favorites("白酒")
for r in refresh_results:
    if r["status"] == "success":
        print(f"{r['fund_name']}: {r['growth_rate']:+.2f}%")
```

### 模式 2: 命令行调用

```bash
# 日常查询
python scripts/fund_query.py 161725

# 添加并分组
python scripts/fund_query.py add 161725 白酒 重仓

# 查看分组
python scripts/fund_query.py list 白酒

# 刷新分组
python scripts/fund_query.py refresh 白酒
```

## 注意事项

1. **请求频率**: 脚本内置随机延迟 (0.5-1.5 秒)，避免请求过快
2. **交易时间**: 盘中数据为估算净值，收盘后为确认净值
3. **数据更新**: 净值通常在交易日 20:00 后更新
4. **网络依赖**: 需要访问天天基金网 API
5. **分组逻辑**: 无分组的基金可以在任何分组查询中看到
6. **数据文件**: 存储在 `data/` 目录，可手动编辑

## 示例基金代码

| 代码 | 名称 | 类型 |
|------|------|------|
| 161725 | 招商中证白酒指数 | 指数型 |
| 000001 | 华夏成长混合 | 混合型 |
| 110011 | 易方达中小盘 | 混合型 |
| 000566 | 华泰柏瑞创新升级 | 混合型 |

## 输出示例

### 查询结果
```
📊 基金查询结果
━━━━━━━━━━━━━━
基金代码：161725
基金名称：招商中证白酒指数 (LOF)A
单位净值：0.6667
估算净值：0.6596
涨跌幅度：-1.06% (下跌)
净值日期：2026-03-18
估值时间：2026-03-19 11:30
```

### 收藏列表（全部）
```
⭐ 我的基金收藏 (3 只)
━━━━━━━━━━━━━━
• 161725 - 招商中证白酒指数 (LOF)A [白酒] (收藏于：2026-03-19 04:49:59)
• 000001 - 华夏成长混合 [科技，重仓] (收藏于：2026-03-19 05:17:38)
• 110011 - 易方达优质精选混合 (QDII) [无分组] (收藏于：2026-03-19 05:18:00)
```

### 收藏列表（按分组）
```
⭐ 分组 '白酒' 的基金 (2 只)
━━━━━━━━━━━━━━
• 161725 - 招商中证白酒指数 (LOF)A [白酒] (收藏于：2026-03-19 04:49:59)
• 110011 - 易方达优质精选混合 (QDII) [无分组] (收藏于：2026-03-19 05:18:00)
```

### 分组列表
```
📁 我的分组 (3 个)
━━━━━━━━━━━━━━
• 白酒 (创建于：2026-03-19 05:17:21)
• 科技 (创建于：2026-03-19 05:17:24)
• 重仓 (创建于：2026-03-19 05:17:25)
```

### 刷新结果
```
🔄 收藏基金刷新结果 (3 只)
━━━━━━━━━━━━━━
📉 161725 招商中证白酒指数 (LOF)A [白酒]
   净值：0.6667 | 涨跌：-1.06%
📉 000001 华夏成长混合 [科技，重仓]
   净值：1.083 | 涨跌：-1.49%
📉 110011 易方达优质精选混合 (QDII) [无分组]
   净值：5.1864 | 涨跌：-2.22%
━━━━━━━━━━━━━━
成功：3 | 失败：0
```
