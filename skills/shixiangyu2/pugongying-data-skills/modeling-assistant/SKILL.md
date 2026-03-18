---
name: modeling-assistant
description: |
  数据建模助手 - 端到端数据建模工作流。包含维度模型设计、dbt模型开发、数据血缘分析三大核心功能。
  当用户需要设计数据仓库模型、开发dbt模型、分析数据血缘时触发。
  触发词：数据建模、维度建模、dbt模型、数据血缘、模型设计。
---

# 数据建模助手

从业务需求到可部署数据模型的完整工作流。三个阶段：模型设计 → dbt开发 → 血缘文档。

## 架构概览

```
┌─────────────────────────────────────────────────────────────────────┐
│                        数据建模助手架构                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   业务需求                                                          │
│      │                                                             │
│      ▼                                                             │
│   ┌────────────────────────────────────────────────────┐          │
│   │  阶段1: 模型设计 (model-design)                     │          │
│   │  Agent: general-purpose                             │          │
│   │  功能：维度建模设计                                 │          │
│   │        - 星型/雪花模型                              │          │
│   │        - 事实表/维度表设计                          │          │
│   │        - SCD策略选择                                │          │
│   │        - ETL映射设计                                │          │
│   └────────────────────┬───────────────────────────────┘          │
│                        │                                           │
│                        ▼                                           │
│   ┌────────────────────────────────────────────────────┐          │
│   │  阶段2: dbt模型开发 (dbt-model)                     │          │
│   │  Agent: general-purpose                             │          │
│   │  功能：生成dbt模型代码                              │          │
│   │        - Staging模型                                │          │
│   │        - Intermediate模型                           │          │
│   │        - Mart模型（Dimension/Fact）                 │          │
│   │        - Schema配置和测试                           │          │
│   └────────────────────┬───────────────────────────────┘          │
│                        │                                           │
│                        ▼                                           │
│   ┌────────────────────────────────────────────────────┐          │
│   │  阶段3: 血缘文档 (lineage-doc)                      │          │
│   │  Agent: Explore                                     │          │
│   │  功能：分析数据血缘                                 │          │
│   │        - 表级血缘分析                               │          │
│   │        - 字段级血缘映射                             │          │
│   │        - 可视化血缘图                               │          │
│   │        - 影响分析                                   │          │
│   └────────────────────────────────────────────────────┘          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 参考资料导航

| 需要时读取 | 文件 | 内容 |
|-----------|------|------|
| 数据建模规范 | [references/data-modeling-standards.md](references/data-modeling-standards.md) | 维度建模、命名规范、dbt最佳实践、血缘规范 |
| 使用示例 | [examples/](examples/) 目录 | 典型建模场景的完整示例 |

## 快速开始

### 方式1：分阶段使用（推荐）

```bash
# 阶段1: 模型设计
/model-design 为电商订单系统设计维度模型，包含销售分析需求

# 阶段2: dbt模型开发
/dbt-model 生成fct_orders事实表模型，依赖stg_orders和stg_order_items

# 阶段3: 血缘分析
/lineage-doc 分析models/marts/fct_orders.sql的血缘关系
```

### 方式2：端到端工作流

```bash
# 启动完整建模工作流
/modeling-assistant 端到端建模：电商销售数据仓库
```

## 核心功能详解

### 功能1：模型设计助手 (/model-design)

**Agent类型**：general-purpose
**工具权限**：Read, Grep, Glob, Edit, Write, Bash

**使用场景**：
- 新数据仓库建模
- 业务系统数仓化
- 模型重构优化

**输入格式**：
```
/model-design 业务场景描述和模型需求
```

**输出内容**：
- 业务背景分析
- 模型架构图（星型/雪花）
- 事实表设计（粒度、维度、度量）
- 维度表设计（SCD策略）
- ETL映射关系
- 物理设计建议（分区、索引）

**示例**：
```
/model-design
业务流程：电商订单销售
分析需求：销售趋势、用户行为、商品分析
数据源：订单表、用户表、商品表、订单明细表
数据量：日增100万订单，历史1亿订单
特殊需求：需要追踪用户等级变化历史
```

**输出**：
```markdown
# 数据模型设计方案

## 模型概览
- 事实表：fact_order_items（订单项级别）
- 维度表：dim_user(SCD2), dim_product(SCD2), dim_date
- 模型类型：星型模型

## 事实表设计
fact_order_items：
- 代理键：order_item_sk
- 维度外键：date_key, user_sk, product_sk
- 退化维度：order_id
- 度量：quantity, unit_price, discount_amount, total_amount

## 维度表设计
dim_user（SCD Type 2）：
- 代理键：user_sk
- 自然键：user_id
- SCD属性：user_level, city（保留历史）
- Type 0属性：register_date（永不改变）
```

---

### 功能2：dbt模型生成器 (/dbt-model)

**Agent类型**：general-purpose
**工具权限**：Read, Grep, Glob, Edit, Write, Bash

**使用场景**：
- dbt项目开发
- 模型代码生成
- 分层模型设计（staging/mart）

**支持的模型类型**：
| 类型 | 前缀 | 说明 |
|------|------|------|
| Staging | stg_ | 清洗标准化 |
| Intermediate | int_ | 业务逻辑处理 |
| Mart - Dimension | dim_ | 维度表 |
| Mart - Fact | fct_ | 事实表 |
| Mart - Aggregate | agg_ | 聚合表 |
| Report | rpt_ | 报表模型 |

**输入格式**：
```
/dbt-model 生成[模型类型]模型，[详细需求]
```

**示例**：
```
/dbt-model 生成mart模型
类型: fact
名称: fct_orders
粒度: 订单商品项级别
依赖: stg_orders, stg_order_items, dim_users, dim_products
维度: user_sk, product_sk, date_sk
度量: quantity, unit_price, discount_amount, total_amount
```

**输出**：
- SQL模型文件（.sql）
- Schema配置文件（.yml）
- 测试配置
- 部署指南

---

### 功能3：血缘文档生成器 (/lineage-doc)

**Agent类型**：Explore
**工具权限**：Read, Grep, Glob

**使用场景**：
- 血缘关系分析
- 影响分析
- 数据地图构建

**输入格式**：
```
/lineage-doc [SQL文件路径或模型名]
```

**输出内容**：
- 表级血缘关系
- 字段级血缘映射
- Mermaid可视化图
- YAML/JSON结构化输出
- 影响分析报告

**示例**：
```
/lineage-doc 分析models/marts/fct_orders.sql的血缘关系
```

**输出**：
```markdown
## 表级血缘 - fct_orders

### 上游依赖
| 层级 | 表名 | 类型 | 关系 |
|------|------|------|------|
| 1 | stg_orders | ref | LEFT JOIN |
| 1 | stg_order_items | ref | LEFT JOIN |
| 2 | raw.orders | source | stg_orders依赖 |

### 血缘图
```mermaid
graph LR
    A[raw.orders] --> B[stg_orders]
    B --> C[fct_orders]
```
```

---

## 配合使用流程

```
业务需求分析 (30分钟)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  阶段1: 模型设计 (/model-design)                             │
│  ├─ 输入：业务场景和分析需求                                 │
│  ├─ 处理：general-purpose Agent                             │
│  └─ 输出：完整模型设计方案                                   │
│       - 星型/雪花模型架构                                    │
│       - 事实表设计（粒度、度量）                             │
│       - 维度表设计（SCD策略）                                │
│       - ETL映射关系                                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  阶段2: dbt模型开发 (/dbt-model)                             │
│  ├─ 输入：模型设计方案                                       │
│  ├─ 处理：general-purpose Agent                             │
│  └─ 输出：dbt模型代码                                        │
│       - Staging模型（stg_*）                                 │
│       - Mart维度模型（dim_*）                                │
│       - Mart事实模型（fct_*）                                │
│       - Schema配置和测试                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  阶段3: 血缘文档 (/lineage-doc)                              │
│  ├─ 输入：dbt模型SQL文件                                     │
│  ├─ 处理：Explore Agent                                     │
│  └─ 输出：血缘分析文档                                       │
│       - 表级血缘关系图                                       │
│       - 字段级血缘映射                                       │
│       - 影响分析报告                                         │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
              模型上线部署
                     │
                     ▼
              持续血缘监控
```

---

## 项目初始化

为团队建立标准化数据建模工作流：

```bash
# 创建数据建模项目骨架
bash .claude/skills/modeling-assistant/scripts/init-project.sh ./modeling-project "数据仓库建模"
```

自动生成：
```
modeling-project/
├── PROJECT.md          # 项目中枢（模型清单+进度+规范）
├── standards.md        # 建模规范（从references复制）
├── models/
│   ├── staging/        # Staging模型
│   ├── intermediate/   # Intermediate模型
│   ├── marts/
│   │   ├── dimensions/ # 维度模型
│   │   └── facts/      # 事实模型
│   └── reports/        # 报表模型
├── lineage/            # 血缘文档
├── docs/               # 模型文档
└── scripts/            # 辅助脚本
```

---

## 维度建模 vs dbt分层

| 维度建模概念 | dbt对应层 | 说明 |
|-------------|----------|------|
| Source系统表 | Sources | 原始数据接入 |
| 清洗标准化 | Staging | stg_*模型 |
| 业务逻辑处理 | Intermediate | int_*模型 |
| 维度表 | Mart | dim_*模型 |
| 事实表 | Mart | fct_*模型 |
| 汇总表 | Mart | agg_*模型 |
| 报表 | Reports | rpt_*模型 |

---

## 最佳实践

### 1. 模型设计原则

**粒度原则**：
- 事实表粒度应是最细的业务级别
- 同一事实表的所有度量必须在相同粒度

**维度原则**：
- 维度表应包含丰富的描述属性
- 默认使用SCD Type 2保留历史

**命名原则**：
- 事实表：fact_* / fct_*
- 维度表：dim_*
- 清晰、一致、有意义

### 2. dbt开发原则

**分层原则**：
- Staging：只做清洗和标准化，无业务逻辑
- Intermediate：处理复杂业务逻辑
- Mart：面向分析的最终模型

**测试原则**：
- 主键：unique + not_null
- 外键：relationships
- 枚举值：accepted_values
- 自定义：业务规则验证

### 3. 血缘管理原则

- 所有模型必须标注清晰的血缘注释
- 关键字段必须维护字段级血缘
- 定期进行影响分析

---

## 故障排除

### 模型设计不符合预期
1. 提供更详细的业务场景描述
2. 明确数据量和性能要求
3. 说明已有的数据源结构

### dbt模型生成失败
1. 检查dbt项目结构是否正确
2. 确认上游依赖模型是否存在
3. 验证字段映射关系

### 血缘分析不完整
1. 确保SQL语法正确
2. 检查所有Refs和Sources都已定义
3. 复杂子查询可能无法完全解析

---

## 示例场景

详见 [examples/](examples/) 目录：

| 示例 | 场景 | 流程 |
|------|------|------|
| example-ecommerce-dw.md | 电商数据仓库建模 | 模型设计 → dbt开发 → 血缘分析 |
| example-scd2-implementation.md | SCD Type 2实现 | 设计 → 开发 → 测试 |

---

## 路线图

### v1.0.0 (当前)
- ✅ 维度模型设计助手 (model-design)
- ✅ dbt模型生成器 (dbt-model)
- ✅ 血缘文档生成器 (lineage-doc)
- ✅ 星型/雪花模型支持
- ✅ SCD Type 1/2/3支持

### v1.1.0 (计划)
- 🔄 数据仓库自动化评估
- 🔄 模型性能优化建议
- 🔄 Data Vault模型支持

### v2.0.0 (计划)
- 📝 AI驱动模型优化
- 📝 自动血缘发现
- 📝 与数据治理平台集成

---

**提示**：本Skill与《AI编程与数据开发工程师融合实战手册》§06 AI辅助数据Pipeline与仓库建模章节配套使用。
