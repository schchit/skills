---
name: flink-template-bytehouse-cdw
description: ByteHouse CDW（云数仓）连接器 SQL 模板子技能，提供 ByteHouse CDW 源表和结果表的完整模板。Use this skill when the user wants to generate or adapt a ByteHouse CDW SQL template for a concrete source/sink or warehouse scenario. Always trigger only when the request contains a template intent + a ByteHouse CDW object/action.
---

# ByteHouse CDW（云数仓）连接器 SQL 模板子技能

提供 ByteHouse CDW（云数仓版）Flink Connector Driver 的 Flink SQL 模板，用于将数据写入 ByteHouse CDW。

本技能只负责生成 SQL 模板与参数说明，不负责执行依赖安装、创建/发布/启动真实任务。

---

## 通用约定（必读）

本技能的基础约定与只读约定统一收敛在：

- `../../../COMMON.md`
- `../../../COMMON_READONLY.md`

本技能主要用于模板生成、示例对比和参数说明，默认不执行创建、发布、启动、删除等变更操作。
如用户从“要模板/示例”切换到“创建/发布真实任务”，应转交给 `flink-sql`、`flink-jar` 等变更技能，并遵循相应的 mutation 约定。

---

## 🎯 核心功能

### 1. 连接方式与鉴权（按文档口径）

ByteHouse CDW Connector Driver 支持两类身份连接：

1. IAM 用户：由火山引擎 IAM 创建，权限由 IAM 策略与 ByteHouse 资源授权决定，通常也可访问控制台。
2. 数据库用户：由 ByteHouse 内部创建的数据库级用户，不能访问控制台，但可用于连接驱动/工具访问数据。

本技能默认给出“IAM 用户 + Gateway 连接”场景下的 Flink SQL 模板（文档示例最明确）。如果你使用数据库用户连接，请以官方文档的参数说明为准，并把你要用的连接信息补充给我后，我再帮你生成对应模板。

---

### 2. 依赖准备（仅说明，不执行）

使用 Flink SQL 方式，需要安装与 Flink 版本匹配的 ByteHouse CDW SQL connector jar。

- Maven 坐标（示例）：
  - groupId: `com.bytedance.bytehouse`
  - artifactId: `flink-sql-connector-bytehouse-cdw_${scala.version}`
  - version: `${flink-sql-connector-bytehouse-cdw.version}`
- Maven 仓库（示例）：`https://artifact.bytedance.com/repository/releases`

说明：`${scala.version}` 需要与你使用的 Flink 发行版 Scala 版本匹配（常见 2.11/2.12）。

---

### 3. ByteHouse CDW Sink DDL 模板（Flink SQL）

下面模板基于官方文档的 Flink SQL 示例参数（Gateway 连接）整理，重点是：

- `connector` 必须使用 `bytehouse-cdw`（不是 `bytehouse`，也不是 `jdbc:bytehouse://...` 这种直连写法）。
- Gateway 连接所需信息：region/host/port/api-token/virtual-warehouse。

```sql
CREATE TABLE bh_cdw_sink (
  id STRING NOT NULL,
  event_time STRING,
  content ARRAY<DECIMAL(20, 0)>,
  PRIMARY KEY (id) NOT ENFORCED
) WITH (
  'connector' = 'bytehouse-cdw',
  'jdbc.enable-gateway-connection' = 'true',
  'bytehouse.gateway.region' = 'VOLCANO_PRIVATE',
  'bytehouse.gateway.host' = 'tenant-{TENANT-ID}-{REGION}.bytehouse.ivolces.com',
  'bytehouse.gateway.port' = '19000',
  'bytehouse.gateway.api-token' = '<YOUR_API_KEY>',
  'bytehouse.gateway.virtual-warehouse' = '<YOUR_VIRTUAL_WAREHOUSE_ID>',
  'database' = '<YOUR_BYTEHOUSE_DATABASE_NAME>',
  'table-name' = '<YOUR_BYTEHOUSE_TABLE_NAME>'
);
```

#### 参数说明（按文档示例归纳）

- `jdbc.enable-gateway-connection`: 是否启用 Gateway 连接（示例为 `true`）
- `bytehouse.gateway.region`: Gateway 连接的 region 标识（示例为 `VOLCANO_PRIVATE`）
- `bytehouse.gateway.host`: ByteHouse Gateway 域名（可在控制台网络信息里获取）
- `bytehouse.gateway.port`: Gateway 端口（示例 `19000`）
- `bytehouse.gateway.api-token`: API Key（在控制台连接信息里创建/复制）
- `bytehouse.gateway.virtual-warehouse`: 计算组 ID
- `database`: ByteHouse 数据库名
- `table-name`: ByteHouse 表名

---

### 4. 完整示例：Datagen -> ByteHouse CDW（Flink SQL）

下面示例与官方文档的 Flink SQL 示例保持同一连接参数形态（用于“加载到 CDW”场景）。

```sql
CREATE TABLE bh_de_source (
  id BIGINT NOT NULL,
  time TIMESTAMP(0),
  content ARRAY<DECIMAL(20, 0)>
) WITH (
  'connector' = 'datagen'
);

CREATE TABLE bh_de_sink (
  id STRING NOT NULL,
  event_time STRING,
  content ARRAY<DECIMAL(20, 0)>,
  PRIMARY KEY (id) NOT ENFORCED
) WITH (
  'connector' = 'bytehouse-cdw',
  'jdbc.enable-gateway-connection' = 'true',
  'bytehouse.gateway.region' = 'VOLCANO_PRIVATE',
  'bytehouse.gateway.host' = 'tenant-{TENANT-ID}-{REGION}.bytehouse.ivolces.com',
  'bytehouse.gateway.port' = '19000',
  'bytehouse.gateway.api-token' = '<YOUR_API_KEY>',
  'bytehouse.gateway.virtual-warehouse' = '<YOUR_VIRTUAL_WAREHOUSE_ID>',
  'database' = '<YOUR_BYTEHOUSE_DATABASE_NAME>',
  'table-name' = '<YOUR_BYTEHOUSE_TABLE_NAME>'
);

INSERT INTO bh_de_sink (id, event_time, content)
SELECT
  CAST(id AS STRING),
  CAST(time AS STRING),
  content
FROM bh_de_source;
```

---

## ⚠️ 常见误区（本技能避免的“幻觉点”）

1. 不把 CDW connector 写成 `connector = bytehouse`。
2. 不把连接方式写成 `url = jdbc:bytehouse://...` 的直连 JDBC 模式（文档示例是 Gateway 连接参数集）。
3. 不臆造 `scan.partition.*` 等“并行读取”参数用在 CDW SQL connector 上（文档示例的重点是写入加载）。

---

## 📚 参考文档

- ByteHouse CDW Connector Driver 官方文档：https://www.volcengine.com/docs/6517/1279281?lang=zh

---

## 🎯 技能总结

### 核心功能
1. ✅ **ByteHouse CDW Sink 模板**（`connector = bytehouse-cdw` + Gateway 参数）
2. ✅ **可复制示例**（Datagen -> ByteHouse CDW）
3. ✅ **参数解释**（api-token / virtual-warehouse / database / table-name 等）

这个子技能提供的是“ByteHouse CDW Connector Driver（Flink SQL）”的模板生成与参数说明，不负责执行安装或上线操作。
