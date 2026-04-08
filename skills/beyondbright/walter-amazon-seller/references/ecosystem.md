# Walter亚马逊选品运营体系

## Skill架构

```
walter-amazon-seller (主入口)
    │
    ├── walter-product-selector           → 选品方向
    │       12大方法论、三层决策逻辑
    │
    ├── walter-market-intelligence        → 市场可行性
    │       市场大盘、价格带分析、利润测算
    │
    ├── walter-competitor-traffic-battle → 竞品流量攻防
    │       7维流量、CPA/ACOS、广告打法
    │
    └── walter-listing-operations        → 运营执行
            VOC分析、Listing优化、品牌规划
```

## 工作流程

```
Step 1: 选品方向 (walter-product-selector)
    输入：品类方向/种子词
    输出：候选品类/切入角度

Step 2: 市场可行性 (walter-market-intelligence)
    输入：品类 + 售价 + 利润率 + SIF数据
    输出：Go/No-Go + 定价区间

Step 3: 竞品攻防 (walter-competitor-traffic-battle)
    输入：目标竞品ASIN + SIF流量数据
    输出：广告打法/关键词攻击清单

Step 4: 运营执行 (walter-listing-operations)
    输入：产品信息 + 评论数据
    输出：VOC报告/Listing优化方案/品牌规划
```

## 数据文件说明

| 数据类型 | 格式 | 用途 |
|---------|------|------|
| SIF市场数据 | xlsx | 市场大盘/价格带 |
| SIF关键词数据 | xlsx | 关键词分析 |
| SIF流量数据 | xlsx | 竞品流量结构 |
| 竞品评论 | xlsx/txt | VOC分析 |

## 路由规则

| 需求关键词 | 引导Skill |
|-----------|----------|
| 选品方向/好方向/怎么选 | walter-product-selector |
| 市场分析/能不能做/利润 | walter-market-intelligence |
| 打竞品/流量/广告策略 | walter-competitor-traffic-battle |
| VOC/评论/标题/五点/A+ | walter-listing-operations |
| 品牌/主图/视频/合规 | walter-listing-operations |
