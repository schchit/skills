---
name: flink-template-bytehouse-ce
description: ByteHouse CE（企业版）连接器 SQL 模板子技能，提供 ByteHouse CE 源表和结果表的完整模板。Use this skill when the user wants to generate or adapt a ByteHouse CE SQL template for a concrete source/sink or enterprise-cluster scenario. Always trigger only when the request contains a template intent + a ByteHouse CE object/action.
---

# ByteHouse CE（企业版）连接器 SQL 模板子技能

提供 ByteHouse CE（企业版）Flink Connector 的 Flink SQL 模板，用于将数据写入 ByteHouse CE。

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

### 1. 依赖准备（仅说明，不执行）

使用 Flink SQL 方式，需要安装与 Flink 版本匹配的 ByteHouse CE SQL connector jar。

- Maven 坐标（示例）：
  - groupId: `com.bytedance.bytehouse`
  - artifactId: `flink-sql-connector-bytehouse-ce`
  - version: `${flink-sql-connector-bytehouse-ce.version}`
- 本地安装到 Maven（示例命令，仅参考）：

```bash
mvn install:install-file \
  -Dfile=${your_path}/flink-sql-connector-bytehouse-ce-${flink-sql-connector-bytehouse-ce.version}.jar \
  -DgroupId=com.bytedance.bytehouse \
  -DartifactId=flink-sql-connector-bytehouse-ce \
  -Dversion=${flink-sql-connector-bytehouse-ce.version} \
  -Dpackaging=jar
```

注意：请使用与 Flink 版本匹配的驱动，并注意 Flink 发行版对应的 Scala 版本要求（文档列出了不同 Flink 版本的驱动包）。

---

### 2. ByteHouse CE Sink DDL 模板（Flink SQL）

下面模板基于官方文档的 DDL 与参数说明整理，重点是：

- `connector` 使用 `bytehouse-ce`（文档也提到可用 `clickhouse`，但默认按 ByteHouse CE 口径给模板）。
- `table-name` 指的是每个分片上的本地表（不是分布式表名）。
- 连接与分片发现参数集中在 `clickhouse.*` 与 `bytehouse.ce.gateway.*`（按你的网络/部署形态选择）。

```sql
CREATE TABLE bh_ce_sink (
  f0 VARCHAR,
  f1 VARCHAR,
  f2 VARCHAR
) WITH (
  'connector' = 'bytehouse-ce',
  'clickhouse.cluster' = '<BYTEHOUSE_CLUSTER_NAME>',
  'clickhouse.shard-discovery.service.host' = '<SHARD_DISCOVERY_HOST>',
  'username' = '<USERNAME>',
  'password' = '<PASSWORD>',
  'database' = '<DATABASE>',
  'table-name' = '<LOCAL_TABLE_NAME>',
  'sink.buffer-flush.interval' = '10 second',
  'sink.buffer-flush.max-rows' = '5000',
  'clickhouse.shard-discovery.address-mapping' = '<MAPPING_OPTIONAL>'
);
```

#### 参数说明（按文档归纳）

- `connector`: 指定连接器，ByteHouse CE 使用 `bytehouse-ce`（或 `clickhouse`）
- `database`: 要连接的 ByteHouse CE 数据库名
- `table-name`: 要写入的表名（注意是每个分片上的本地表）
- `username` / `password`: 连接认证信息
- `sink.buffer-flush.interval`: flush 间隔（示例 `10 second`）
- `sink.buffer-flush.max-rows`: flush 行数阈值（示例 `5000`）
- `clickhouse.cluster`: ByteHouse 集群名称
- `clickhouse.shard-discovery.kind`: 分片发现类型（文档列举：`SYSTEM_CLUSTERS` / `CE_GATEWAY` / `CE_API_CLUSTERS`）
- `clickhouse.shard-discovery.service.host` / `clickhouse.shard-discovery.service.port`: 分片发现服务 host/port
- `clickhouse.shard-discovery.address-mapping`: 分片地址映射（用于地址可达性转换场景）
- `bytehouse.ce.gateway.host` / `bytehouse.ce.gateway.port`: 企业版网关 host/port（当你选择网关相关的 shard discovery 方式时使用）
- `sharding-strategy`: 写入分片策略（文档列举：`NONE` / `RANDOM` / `ROUND_ROBIN` / `HASH`）

---

### 3. 最小可复制示例：Datagen -> ByteHouse CE

```sql
CREATE TABLE datagen_src (
  f0 VARCHAR,
  f1 VARCHAR,
  f2 VARCHAR
) WITH (
  'connector' = 'datagen'
);

CREATE TABLE bh_ce_sink (
  f0 VARCHAR,
  f1 VARCHAR,
  f2 VARCHAR
) WITH (
  'connector' = 'bytehouse-ce',
  'clickhouse.cluster' = '<BYTEHOUSE_CLUSTER_NAME>',
  'clickhouse.shard-discovery.service.host' = '<SHARD_DISCOVERY_HOST>',
  'username' = '<USERNAME>',
  'password' = '<PASSWORD>',
  'database' = '<DATABASE>',
  'table-name' = '<LOCAL_TABLE_NAME>',
  'sink.buffer-flush.interval' = '10 second',
  'sink.buffer-flush.max-rows' = '5000'
);

INSERT INTO bh_ce_sink
SELECT f0, f1, f2 FROM datagen_src;
```

---

## ⚠️ 常见误区（本技能避免的“幻觉点”）

1. 不把 CE connector 写成 `connector = bytehouse`。
2. 不把连接方式写成 `url = jdbc:bytehouse://...` 的直连 JDBC URL 模板（CE 文档的 Flink SQL 示例重点是 `bytehouse-ce` + `clickhouse.*`/gateway/shard discovery 参数）。
3. 不臆造 `scan.partition.*`、`scan.fetch-size` 这类“读取并行化”参数作为 CE connector 的必选项（文档给的是写入加载的典型 DDL/参数表）。
4. 不把 `table-name` 当成分布式表；按文档，它指每个分片的本地表。

---

## 📚 参考文档

- ByteHouse CE 官方文档：https://www.volcengine.com/docs/6464/1337868?lang=zh#%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E

---

## 🎯 技能总结

### 核心功能
1. ✅ **ByteHouse CE Sink 模板**（`connector = bytehouse-ce` + 分片发现 + flush 参数）
2. ✅ **可复制示例**（Datagen -> ByteHouse CE）
3. ✅ **参数解释**（cluster/shard discovery/address mapping/sharding strategy 等）

这个子技能提供的是“ByteHouse CE Connector（Flink SQL）”的模板生成与参数说明，不负责执行安装或上线操作。
