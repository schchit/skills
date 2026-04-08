---
name: flink-template-paimon
description: Paimon 连接器 SQL 模板子技能，提供 Paimon 表的完整模板，包括 Append 表、主键表、部分列更新表、聚合表等写入场景，以及读取场景。Use this skill when the user wants to generate or adapt a Paimon SQL template for a concrete table pattern or read/write scenario. Always trigger only when the request contains a template intent + a Paimon object/action.
---

# Paimon 连接器 SQL 模板子技能（优化版）

提供 Paimon 连接器的完整 SQL 模板，包括多种写入场景（Append 表、主键表、部分列更新表、聚合表）和读取场景。

---

## 通用约定（必读）

本技能的基础约定与只读约定统一收敛在：

- `../../../COMMON.md`
- `../../../COMMON_READONLY.md`

本技能主要用于模板生成、示例对比和参数说明，默认不执行创建、发布、启动、删除等变更操作。
如用户从“要模板/示例”切换到“创建/发布真实任务”，应转交给 `flink-sql`、`flink-jar` 等变更技能，并遵循相应的 mutation 约定。

---

## 🎯 核心功能

### 0. 前置条件：创建 Catalog 和 Database

Paimon 使用 LAS Catalog 统一管理元数据，需要使用 `${catalog_name}.${db_name}.${table_name}` 三段式访问。

#### 0.1 创建 Catalog（可选：使用 FileSystem Catalog）

这个过程是非必选的，如果采用 [数据目录](https://www.volcengine.com/docs/6581/1817049?lang=zh) 功能，则可以跳过此步骤，不需要创建 Catalog。

```sql
-- 创建 Paimon Catalog（基于 FileSystem）
CREATE CATALOG paimon_catalog
WITH (
  'type' = 'paimon',
  'warehouse' = 'tos://${YOUR_TOS_BUCKET_NAME}/paimon/warehouse'
);

-- 创建 Paimon Catalog（基于 LAS Catalog）
CREATE CATALOG paimon_las_catalog WITH (
    'type' = 'paimon',
    'metastore' = 'hive',
    -- las config
    'is-las' = 'true',
    'hive.client.las.region.name' = '${REGION}',
    'hive.metastore.uris' = 'thrift://lakeformation.las.${REGION}.ivolces.com:48869',
    'hive.hms.client.is.public.cloud' = 'true',
    'hive.client.las.ak' = 'xxx',
    'hive.client.las.sk' = 'xxx',
    'catalog.properties.metastore.catalog.default' = '${YOUR_LAS_CATALOG_NAME}',
    'warehouse' = 'tos://${YOUR_TOS_BUCKET_NAME}/paimon/warehouse'
);

-- 使用 Catalog
USE CATALOG paimon_catalog;
```

#### 0.2 创建 Database

```sql
-- 创建 Database
CREATE DATABASE IF NOT EXISTS paimon_catalog.test_db;

-- 使用 Database
USE paimon_catalog.test_db;
```

---

### 1. Paimon 写入场景模板

#### 1.1 Append 表（追加表）模板

**场景**：只追加数据，不更新或删除，适用于日志、事件等不可变数据。

**注意：Append 表不需要主键！**

**重要说明（仅对 Append 表）**：
- ✅ Append 表默认不需要设置 bucket 数量
- ⚠️ Append 表如果要设置 bucket 数量，就必须设置 bucket-key 分桶键
- ℹ️ 分桶功能不是 Paimon 1.1 才支持的，低版本也支持
- ⚠️ 只是 Paimon 1.1 不允许 Append 表不设置 bucket-key 单独设置 bucket

```sql
-- Append 表（不需要主键，不设置分桶）
CREATE TABLE IF NOT EXISTS paimon_catalog.test_db.append_table (
  id BIGINT,
  name STRING,
  amount DECIMAL(10, 2),
  event_time TIMESTAMP(3),
  dt STRING
) PARTITIONED BY (dt)
WITH (
  'changelog-producer' = 'none'
);
```

```sql
-- Append 表（需要主键，设置分桶 - Paimon 1.1+）
-- 注意：设置 bucket 数量时，必须同时设置 bucket-key
CREATE TABLE IF NOT EXISTS paimon_catalog.test_db.append_table_with_bucket (
  id BIGINT,
  name STRING,
  amount DECIMAL(10, 2),
  event_time TIMESTAMP(3),
  dt STRING,
  PRIMARY KEY (id, dt) NOT ENFORCED
) PARTITIONED BY (dt)
WITH (
  'bucket' = '4',
  'bucket-key' = 'id',
  'changelog-producer' = 'none'
);
```

**参数说明**：
- `bucket`：分桶数量，单个 bucket 推荐存储 1GB 左右数据（可选，设置时必须同时设置 bucket-key）
- `bucket-key`：分桶键（Paimon 1.1+，设置 bucket 时必须设置）
- `changelog-producer'：changelog 生产者（none：不产生 changelog，节省存储和写入资源）

**适用场景**：
- ✅ 日志数据
- ✅ 事件数据
- ✅ 时序数据
- ✅ 不需要更新的历史数据

---

#### 1.2 主键表（Primary Key Table）模板（非分区表）

**场景**：根据主键更新数据，适用于需要 Upsert 的场景。

**重要说明**：
- ⚠️ **主键表建议设置 bucket 数量，单个 bucket 推荐存储 1-2GB 数据量
- ✅ 主键表设置 bucket 时，可以设置 bucket-key 但不强制（只有 Append 表强制要求）
- ℹ️ 分桶功能不是 Paimon 1.1 才支持的，低版本也支持
- ⚠️ 注意：只有 Append 表在 Paimon 1.1 中不允许不设置 bucket-key 单独设置 bucket

```sql
-- 主键表（非分区表，推荐设置分桶）
-- 建议：bucket 数量根据数据量调整，单个 bucket 推荐 1-2GB
CREATE TABLE IF NOT EXISTS paimon_catalog.test_db.primary_key_table (
  word VARCHAR,
  cnt BIGINT,
  PRIMARY KEY (word) NOT ENFORCED
) WITH (
  'bucket' = '4',
  'changelog-producer' = 'input'
);
```

```sql
-- 主键表（非分区表，设置分桶和 bucket-key）
CREATE TABLE IF NOT EXISTS paimon_catalog.test_db.primary_key_table_with_bucket_key (
  word VARCHAR,
  cnt BIGINT,
  PRIMARY KEY (word) NOT ENFORCED
) WITH (
  'bucket' = '4',
  'bucket-key' = 'word',
  'changelog-producer' = 'input'
);
```

**参数说明**：
- `bucket`：分桶数量，单个 bucket 推荐存储 1-2GB 数据（建议设置）
- `bucket-key`：分桶键（可选，主键表不强制要求）
- `changelog-producer`：changelog 生产者（input：根据上游新增数据产生 changelog，用于下游流式读取）

---

#### 1.3 主键表（Primary Key Table）模板（分区表）

**场景**：根据主键更新数据的分区表。

**重要说明**：
- ⚠️ **主键表建议设置 bucket 数量，单个 bucket 推荐存储 1-2GB 数据量
- ✅ 主键表设置 bucket 时，可以设置 bucket-key 但不强制（只有 Append 表强制要求）
- ℹ️ 分桶功能不是 Paimon 1.1 才支持的，低版本也支持
- ⚠️ 注意：只有 Append 表在 Paimon 1.1 中不允许不设置 bucket-key 单独设置 bucket

```sql
-- 主键表（分区表，推荐设置分桶）
-- 建议：bucket 数量根据数据量调整，单个 bucket 推荐 1-2GB
CREATE TABLE IF NOT EXISTS paimon_catalog.test_db.primary_key_partitioned (
  word VARCHAR,
  cnt BIGINT,
  dt STRING,
  hh STRING,
  PRIMARY KEY (dt, hh, word) NOT ENFORCED
) PARTITIONED BY (dt, hh)
WITH (
  'bucket' = '4',
  'changelog-producer' = 'none',
  'metastore.partitioned-table' = 'true'
);
```

```sql
-- 主键表（分区表，设置分桶和 bucket-key）
CREATE TABLE IF NOT EXISTS paimon_catalog.test_db.primary_key_partitioned_with_bucket_key (
  word VARCHAR,
  cnt BIGINT,
  dt STRING,
  hh STRING,
  PRIMARY KEY (dt, hh, word) NOT ENFORCED
) PARTITIONED BY (dt, hh)
WITH (
  'bucket' = '4',
  'bucket-key' = 'word',
  'changelog-producer' = 'none',
  'metastore.partitioned-table' = 'true'
);
```

**参数说明**：
- `bucket`：分桶数量，单个 bucket 推荐存储 1-2GB 数据（建议设置）
- `bucket-key`：分桶键（可选，主键表不强制要求）
- `metastore.partitioned-table`：开启后将分区信息同步到 LAS 元数据管理，默认 false 不开启
- **注意**：一般分区主键表的主键字段必须包含分区字段

---

#### 1.4 部分列更新表（Partial Update Table）模板

**场景**：只更新部分列，其他列保持不变，适用于大宽表场景。

**重要说明**：
- ⚠️ **部分列更新表建议设置 bucket 数量，单个 bucket 推荐存储 1-2GB 数据量
- ✅ 部分列更新表设置 bucket 时，可以设置 bucket-key 但不强制（只有 Append 表强制要求）
- ℹ️ 分桶功能不是 Paimon 1.1 才支持的，低版本也支持
- ⚠️ 注意：只有 Append 表在 Paimon 1.1 中不允许不设置 bucket-key 单独设置 bucket

```sql
-- 部分列更新表（推荐设置分桶）
-- 建议：bucket 数量根据数据量调整，单个 bucket 推荐 1-2GB
CREATE TABLE IF NOT EXISTS paimon_catalog.test_db.partial_update_table (
  uid INT,
  -- 用户基础信息
  username STRING,
  reg_time TIMESTAMP(3),
  -- 用户渠道信息，嵌套结构保存多种登录渠道，以渠道名去重
  logintypes ARRAY<ROW<logintype STRING, bind_time TIMESTAMP(3)>>,
  last_bind_time TIMESTAMP(3),
  -- 会员信息
  vip_is_valid BOOLEAN,
  vip_start_time TIMESTAMP(3),
  vip_end_time TIMESTAMP(3),
  PRIMARY KEY (uid) NOT ENFORCED
) WITH (
  'bucket' = '4',
  'merge-engine' = 'partial-update',
  'changelog-producer' = 'lookup',
  'fields.last_bind_time.sequence-group' = 'logintypes',
  'fields.logintypes.aggregate-function' = 'nested_update',
  'fields.logintypes.nested-key' = 'logintype'
);
```

```sql
-- 部分列更新表（设置分桶和 bucket-key）
CREATE TABLE IF NOT EXISTS paimon_catalog.test_db.partial_update_table_with_bucket_key (
  uid INT,
  -- 用户基础信息
  username STRING,
  reg_time TIMESTAMP(3),
  -- 用户渠道信息，嵌套结构保存多种登录渠道，以渠道名去重
  logintypes ARRAY<ROW<logintype STRING, bind_time TIMESTAMP(3)>>,
  last_bind_time TIMESTAMP(3),
  -- 会员信息
  vip_is_valid BOOLEAN,
  vip_start_time TIMESTAMP(3),
  vip_end_time TIMESTAMP(3),
  PRIMARY KEY (uid) NOT ENFORCED
) WITH (
  'bucket' = '4',
  'bucket-key' = 'uid',
  'merge-engine' = 'partial-update',
  'changelog-producer' = 'lookup',
  'fields.last_bind_time.sequence-group' = 'logintypes',
  'fields.logintypes.aggregate-function' = 'nested_update',
  'fields.logintypes.nested-key' = 'logintype'
);
```

**参数说明**：
- `merge-engine'：合并引擎（partial-update：部分列更新）
- `changelog-producer'：changelog 生产者（lookup 或 full-compaction，用于下游流式读取）
- `fields.<field-name>.sequence-group'：序列组，解决多流更新时的乱序问题
- `fields.<field-name>.aggregate-function'：聚合函数（nested_update：嵌套更新）
- `fields.<field-name>.nested-key'：嵌套表的主键

**关键设计**：
- `merge-engine`：采用 `partial-update`
- `sequence-group'：采用 `last_bind_time` 作为序列组字段
- `aggregate-function'：聚合函数采用 `nested_update`，以 `logintype` 作为嵌套主键，进行去重更新

**适用场景**：
- ✅ 多流实时动态更新
- ✅ 大宽表拼接
- ✅ 数据修正
- ✅ 高频并发写入

---

#### 1.5 聚合表（Aggregate Table）模板

**场景**：自动聚合数据，适用于实时聚合统计。

**重要说明**：
- ⚠️ **聚合表建议设置 bucket 数量，单个 bucket 推荐存储 1-2GB 数据量
- ✅ 聚合表设置 bucket 时，可以设置 bucket-key 但不强制（只有 Append 表强制要求）
- ℹ️ 分桶功能不是 Paimon 1.1 才支持的，低版本也支持
- ⚠️ 注意：只有 Append 表在 Paimon 1.1 中不允许不设置 bucket-key 单独设置 bucket

```sql
-- 聚合表（推荐设置分桶）
-- 建议：bucket 数量根据数据量调整，单个 bucket 推荐 1-2GB
CREATE TABLE IF NOT EXISTS paimon_catalog.test_db.aggregate_table (
  window_start TIMESTAMP(3),
  window_end TIMESTAMP(3),
  category STRING,
  item_id BIGINT,
  total_amount DECIMAL(10, 2),
  count BIGINT,
  dt STRING,
  PRIMARY KEY (window_start, window_end, category, item_id, dt) NOT ENFORCED
) PARTITIONED BY (dt)
WITH (
  'bucket' = '4',
  'changelog-producer' = 'lookup',
  'merge-engine' = 'aggregation',
  'fields.total_amount.aggregate-function' = 'sum',
  'fields.count.aggregate-function' = 'sum',
  'fields.total_amount.ignore-retract' = 'true',
  'fields.count.ignore-retract' = 'true'
);
```

```sql
-- 聚合表（设置分桶和 bucket-key）
CREATE TABLE IF NOT EXISTS paimon_catalog.test_db.aggregate_table_with_bucket_key (
  window_start TIMESTAMP(3),
  window_end TIMESTAMP(3),
  category STRING,
  item_id BIGINT,
  total_amount DECIMAL(10, 2),
  count BIGINT,
  dt STRING,
  PRIMARY KEY (window_start, window_end, category, item_id, dt) NOT ENFORCED
) PARTITIONED BY (dt)
WITH (
  'bucket' = '4',
  'bucket-key' = 'category,item_id',
  'changelog-producer' = 'lookup',
  'merge-engine' = 'aggregation',
  'fields.total_amount.aggregate-function' = 'sum',
  'fields.count.aggregate-function' = 'sum',
  'fields.total_amount.ignore-retract' = 'true',
  'fields.count.ignore-retract' = 'true'
);
```

**参数说明**：
- `merge-engine`：合并引擎（aggregation：聚合）
- `fields.<field-name>.aggregate-function`：字段的聚合函数（sum、max、min、count、last_value、first_value、listagg、bool_and、bool_or）
- `fields.<field-name>.ignore-retract`：是否忽略撤回消息（默认 false）

**可用的聚合函数**：
- `sum`：求和
- `max`：最大值
- `min`：最小值
- `count`：计数
- `last_value`：最后一个值
- `first_value`：第一个值
- `listagg`：字符串连接
- `bool_and`：布尔 AND
- `bool_or`：布尔 OR
- `nested_update`：嵌套更新（用于部分列更新）
- `collect`：收集到数组
- `merge_map`：合并映射

**适用场景**：
- ✅ 实时聚合统计
- ✅ 实时报表
- ✅ 实时 Dashboard 数据

---

### 2. Paimon 读取场景模板

#### 2.1 从 Paimon 表读取数据

```sql
-- 从 Paimon 表读取数据
CREATE TABLE print_result (
  word VARCHAR,
  cnt BIGINT
) WITH (
  'connector' = 'print'
);

-- 插入数据
INSERT INTO print_result
SELECT * FROM paimon_catalog.test_db.primary_key_table;
```

---

### 3. 完整示例

#### 3.1 Kafka → Paimon Append 表示例

```sql
-- ============================================
-- 0. 创建 Catalog 和 Database
-- ============================================
CREATE CATALOG IF NOT EXISTS paimon_catalog
WITH (
  'type' = 'paimon',
  'warehouse' = 'tos://your-bucket/paimon/warehouse'
);

USE CATALOG paimon_catalog;

CREATE DATABASE IF NOT EXISTS paimon_catalog.test_db;

USE paimon_catalog.test_db;

-- ============================================
-- 1. Kafka 源表
-- ============================================
CREATE TABLE kafka_source (
  id BIGINT,
  name STRING,
  amount DECIMAL(10, 2),
  event_time TIMESTAMP(3)
) WITH (
  'connector' = 'kafka',
  'topic' = 'your-topic-name',
  'properties.bootstrap.servers' = 'kafka-server:9092',
  'properties.group.id' = 'flink-consumer-group',
  'scan.startup.mode' = 'earliest-offset',
  'format' = 'json',
  'json.fail-on-missing-field' = 'false',
  'json.ignore-parse-errors' = 'true'
);

-- ============================================
-- 2. Paimon Append 表（结果表）
-- ============================================
CREATE TABLE IF NOT EXISTS paimon_append_sink (
  id BIGINT,
  name STRING,
  amount DECIMAL(10, 2),
  event_time TIMESTAMP(3),
  dt STRING
) PARTITIONED BY (dt)
WITH (
  'bucket' = '4',
  'changelog-producer' = 'none'
);

-- ============================================
-- 3. 插入数据：从 Kafka 写入 Paimon
-- ============================================
INSERT INTO paimon_append_sink
SELECT 
  id,
  name,
  amount,
  event_time,
  DATE_FORMAT(event_time, 'yyyy-MM-dd') AS dt
FROM kafka_source;
```

---

#### 3.2 Datagen → Paimon 主键表示例

```sql
-- ============================================
-- 0. 创建 Catalog 和 Database
-- ============================================
CREATE CATALOG IF NOT EXISTS paimon_catalog
WITH (
  'type' = 'paimon',
  'warehouse' = 'tos://your-bucket/paimon/warehouse'
);

USE CATALOG paimon_catalog;

CREATE DATABASE IF NOT EXISTS paimon_catalog.test_db;

USE paimon_catalog.test_db;

-- ============================================
-- 1. Datagen 源表
-- ============================================
CREATE TABLE datagen_source (
  word VARCHAR,
  cnt BIGINT
) WITH (
  'connector' = 'datagen',
  'rows-per-second' = '5',
  'fields.word.length' = '30'
);

-- ============================================
-- 2. Paimon 主键表（结果表）
-- ============================================
CREATE TABLE IF NOT EXISTS paimon_primary_key_sink (
  word VARCHAR,
  cnt BIGINT,
  PRIMARY KEY (word) NOT ENFORCED
) WITH (
  'bucket' = '4',
  'changelog-producer' = 'input'
);

-- ============================================
-- 3. 插入数据
-- ============================================
INSERT INTO paimon_primary_key_sink
SELECT 
  word,
  count(1) AS cnt
FROM datagen_source
GROUP BY word;
```

---

## 💡 最佳实践

### 1. 选择合适的合并引擎

| 场景 | 推荐的 merge-engine | changelog-producer |
|------|-------------------|-------------------|
| 只追加，不更新 | deduplicate 或不设置 | none |
| 根据主键更新 | deduplicate | input/lookup/full-compaction |
| 只更新部分列 | partial-update | lookup/full-compaction |
| 实时聚合统计 | aggregation | lookup/full-compaction |

---

### 2. 分桶策略

**重要说明**：
- ⚠️ **主键表、部分列更新表、聚合表都建议设置 bucket 数量，单个 bucket 推荐存储 1-2GB 数据量**
- ✅ **Append 表**默认不需要设置 bucket 数量（可选）
- ⚠️ **只有 Append 表**在 Paimon 1.1 中不允许不设置 bucket-key 单独设置 bucket
- ⚠️ 主键表、部分列更新表、聚合表设置 bucket 时，可以设置 bucket-key 但不强制
- ℹ️ 分桶功能不是 Paimon 1.1 才支持的，低版本也支持

- **分桶数量**：单个 bucket 推荐存储 1-2GB 数据
- **bucket 参数**：控制分桶数量（主键表等建议设置，Append 表可选）
- **bucket-key 参数**：分桶键（Append 表设置 bucket 时必须设置；其他表可选）
- 建议根据数据量调整 bucket 数量

**何时需要分桶**：
- ✅ 数据量很大，需要并行读写
- ✅ 需要优化查询性能
- ❌ 小数据量场景（Append 表默认不需要分桶）

---

### 3. Changelog Producer 选择

| Changelog Producer | 说明 | 适用场景 |
|-------------------|------|---------|
| `none` | 不产生 changelog | 只追加，不需要下游流读 |
| `input` | 根据上游新增数据产生 | 需要下游流读，但只需要输入记录 |
| `lookup` | 查找模式 | 需要下游流读，需要完整的变更日志 |
| `full-compaction` | 全量压缩 | 需要下游流读，需要完整的变更日志 |

**注意**：对于流查询，partial-update 和 aggregation 合并引擎必须与 lookup 或 full-compaction 一起使用（input 也支持，但只返回输入记录）。

---

### 4. 分区策略

- **按日期分区**：`dt STRING`，格式 `yyyy-MM-dd`
- **按小时分区**：`dt STRING, hh STRING`，格式 `yyyy-MM-dd, HH`
- **分区信息同步**：设置 `metastore.partitioned-table' = 'true'` 将分区信息同步到 LAS 元数据管理

**注意**：因为分区字段无法动态增加，增加参数后，需要将原有的数据表清掉（包括 LAS 元数据和 TOS 的数据文件），然后重新创建。


### 5. 常见参数优化

- **Paimon 部分列更新不支持删除事件**：Paimon 表增加参数 `'ignore-delete' = 'true'` 忽略删除事件
- **Paimon 非分区表需要行级过期**：在 Paimon 1.1 表上增加如下参数
```sql
'record-level.expire-time' = '30 d',
'record-level.time-field' = 'update_time',
```
- **Paimon 分区表要设置分区过期时间**：需要设置分区的时间格式、和保存周期等
```sql
'partition.expiration-strategy' = 'values-time',
'partition.expiration-time' = '7 d',
'partition.expiration-check-interval' = '1 d',
'partition.timestamp-formatter' = 'yyyyMMdd',
'partition.timestamp-pattern' = '$dt'
```
- **Paimon 表需要加长快照过期时间**：避免下游流读的时候延迟过高导致快照过期
```sql
'snapshot.time-retained' = '3 d',
'snapshot.num-retained.max' = '1000',
``` 
- **Paimon 需要开启异步文件合并**：通过异步 Compaction 避免文件合并阻塞数据写入
```sql
'num-sorted-run.stop-trigger' = '2147483647',
'sort-spill-threshold' = '5',
'lookup-wait' = 'false',
```
- **Paimon 写入的时候数据表上下游主键不同**：Flink SQL 在默认情况下会产生 upsert-materialize 算子，在 Paimon 支持 upsert 情况下，可以在 Flink 任务自定义参数设置为 None。
```sql
table.exec.sink.upsert-materialize: NONE
```



---

## ⚠️ 注意事项

### 1. Catalog 三段式访问

- ✅ **必须使用三段式**：`${catalog_name}.${db_name}.${table_name}`
- ✅ **先创建 Catalog**：使用 FileSystem 或 LAS Catalog
- ✅ **再创建 Database**：在 Catalog 下创建 Database
- ✅ **最后创建表**：在 Database 下创建表

---

### 2. Append 表不需要主键

- ✅ **Append 表不需要主键**
- ✅ 适用于日志、事件等不可变数据
- ✅ 性能最好，无需去重

---

### 3. 分区主键表的主键要求

- ✅ **分区主键表的主键字段必须包含分区字段**
- ✅ 例如：`PRIMARY KEY (dt, hh, word) NOT ENFORCED`

---

### 4. 参数名称完全不同

之前错误的参数（已废弃）：
- ❌ `connector`
- ❌ `path`
- ❌ `warehouse`
- ❌ `auto-create`
- ❌ `write-mode`
- ❌ `file.format`
- ❌ `compression.format`

正确的参数（新）：
- ✅ `bucket`
- ✅ `changelog-producer`
- ✅ `merge-engine`
- ✅ `metastore.partitioned-table`
- ✅ `fields.<field-name>.aggregate-function`
- ✅ `fields.<field-name>.sequence-group`
- ✅ `fields.<field-name>.nested-key`
- ✅ `fields.<field-name>.ignore-retract`

---

### 5. 常见问题处理

#### 问题 1：验证 SQL 时报错

**错误信息**：
```
Caused by: org.apache.thrift.transport.TTransportException
```

**原因**：当前版本暂时无法在验证 SQL 阶段访问 LAS 元数据。

**解决方法**：任务上线过程中选择更多设置 - 跳过上线前的深度检查。

---

#### 问题 2：任务无法启动，报 LAS 数据库不存在

**错误信息**：
```
org.apache.flink.table.catalog.exceptions.DatabaseNotExistException
```

**原因**：在 Flink 任务提交阶段，静态解析 SQL 的时候，当前不会去连接 LAS 获取已有的数据库。

**解决方法**：必须在 SQL 中显式写明建库语句：
```sql
CREATE DATABASE IF NOT EXISTS test_db;
```

---

## 📚 参考文档

- Paimon 使用 LAS Catalog 管理元数据：https://www.volcengine.com/docs/6581/1450235?lang=zh
- Paimon 聚合表功能：https://www.volcengine.com/docs/6581/1456593?lang=zh
- Paimon 部分列更新功能：https://www.volcengine.com/docs/6581/1456594?lang=zh
- Paimon 官方文档：https://paimon.apache.org/docs/0.8/primary-key-table/merge-engine/

---

## 🎯 技能总结

### 核心功能
1. ✅ **Catalog 和 Database 创建** - 正确的三段式访问方式
2. ✅ **Append 表模板** - 只追加数据，不需要主键
3. ✅ **主键表模板** - 根据主键更新数据（分区/非分区）
4. ✅ **部分列更新表模板** - 只更新部分列，适用于大宽表
5. ✅ **聚合表模板** - 自动聚合数据，适用于实时统计
6. ✅ **读取场景模板** - 从 Paimon 表读取数据
7. ✅ **完整示例** - Kafka→Paimon Append 表、Datagen→Paimon 主键表
8. ✅ **最佳实践** - 合并引擎选择、分桶策略、Changelog Producer 选择

这个子技能提供了 Paimon 连接器的完整、正确的 SQL 模板！
