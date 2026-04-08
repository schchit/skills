---
name: flink-template-kafka
description: Kafka 连接器 SQL 模板子技能，提供 Kafka Source 和 Sink 的完整模板，包括 JSON/CSV/Avro 格式、安全认证、性能优化等。Use this skill when the user wants to generate or adapt a Kafka source/sink SQL template for a concrete connector scenario, format, or action. Always trigger only when the request contains a template intent + a Kafka object/action.
---

# Kafka 连接器 SQL 模板子技能

提供 Kafka 连接器的完整 SQL 模板，包括 Source、Sink、多种格式、安全认证、性能优化等。

---

## 通用约定（必读）

本技能的基础约定与只读约定统一收敛在：

- `../../../COMMON.md`
- `../../../COMMON_READONLY.md`

本技能主要用于模板生成、示例对比和参数说明，默认不执行创建、发布、启动、删除等变更操作。
如用户从“要模板/示例”切换到“创建/发布真实任务”，应转交给 `flink-sql`、`flink-jar` 等变更技能，并遵循相应的 mutation 约定。

---

## 🎯 核心功能

### 1. Kafka 源表（Source）模板

#### 1.1 JSON 格式源表模板

**场景**：从 Kafka Topic 读取 JSON 格式数据

```sql
CREATE TABLE kafka_source_json (
  order_id BIGINT,
  order_product_id BIGINT,
  order_customer_id BIGINT,
  order_status VARCHAR,
  order_update_time TIMESTAMP(3)
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
```

**参数说明**：
- `topic`：Kafka Topic 名称
- `properties.bootstrap.servers`：Kafka Broker 地址
- `properties.group.id`：消费组 ID
- `scan.startup.mode`：启动模式（earliest-offset/latest-offset/group-offsets/timestamp/specific-offsets）
- `format`：数据格式（json/csv/avro等）
- `json.fail-on-missing-field`：缺失字段时是否失败（默认 true）
- `json.ignore-parse-errors`：是否忽略解析错误（默认 false）

---

#### 1.2 CSV 格式源表模板

**场景**：从 Kafka Topic 读取 CSV 格式数据

```sql
CREATE TABLE kafka_source_csv (
  order_id BIGINT,
  order_product_id BIGINT,
  order_customer_id BIGINT,
  order_status VARCHAR,
  order_update_time TIMESTAMP(3)
) WITH (
  'connector' = 'kafka',
  'topic' = 'your-topic-name',
  'properties.bootstrap.servers' = 'kafka-server:9092',
  'properties.group.id' = 'flink-consumer-group',
  'scan.startup.mode' = 'earliest-offset',
  'format' = 'csv',
  'csv.allow-comments' = 'false',
  'csv.ignore-parse-errors' = 'true',
  'csv.field-delimiter' = ',',
  'csv.line-delimiter' = U&'\000A'
);
```

---

#### 1.3 Avro 格式源表模板

**场景**：从 Kafka Topic 读取 Avro 格式数据

```sql
CREATE TABLE kafka_source_avro (
  order_id BIGINT,
  order_product_id BIGINT,
  order_customer_id BIGINT,
  order_status VARCHAR,
  order_update_time TIMESTAMP(3)
) WITH (
  'connector' = 'kafka',
  'topic' = 'your-topic-name',
  'properties.bootstrap.servers' = 'kafka-server:9092',
  'properties.group.id' = 'flink-consumer-group',
  'scan.startup.mode' = 'earliest-offset',
  'format' = 'avro',
  'avro.schema' = '{
    "type": "record",
    "name": "Order",
    "fields": [
      {"name": "order_id", "type": "long"},
      {"name": "order_product_id", "type": "long"},
      {"name": "order_customer_id", "type": "long"},
      {"name": "order_status", "type": "string"},
      {"name": "order_update_time", "type": {"type": "long", "logicalType": "timestamp-millis"}}
    ]
  }'
);
```

---

#### 1.4 Debezium JSON CDC 源表模板

**场景**：从 Kafka Topic 读取 Debezium JSON 格式的 CDC 数据

```sql
CREATE TABLE kafka_source_debezium (
  id INT,
  name STRING,
  age INT,
  email STRING,
  update_time TIMESTAMP(3)
) WITH (
  'connector' = 'kafka',
  'topic' = 'your-cdc-topic',
  'properties.bootstrap.servers' = 'kafka-server:9092',
  'properties.group.id' = 'flink-cdc-consumer',
  'scan.startup.mode' = 'earliest-offset',
  'format' = 'debezium-json',
  'debezium-json.schema-include' = 'false'
);
```

---

### 2. Kafka 结果表（Sink）模板

#### 2.1 JSON 格式结果表模板

**场景**：将数据写入 Kafka Topic（JSON 格式）

```sql
CREATE TABLE kafka_sink_json (
  order_id BIGINT,
  order_product_id BIGINT,
  order_customer_id BIGINT,
  order_status VARCHAR,
  order_update_time TIMESTAMP(3)
) WITH (
  'connector' = 'kafka',
  'topic' = 'your-sink-topic',
  'properties.bootstrap.servers' = 'kafka-server:9092',
  'format' = 'json',
  'sink.partitioner' = 'fixed',
  'properties.batch.size' = '524288',
  'properties.linger.ms' = '500',
  'properties.buffer.memory' = '134217728'
);
```

**性能优化参数**：
- `properties.batch.size`：单个 Batch 的最大字节数（建议 524288 = 512KB）
- `properties.linger.ms`：消息在 Batch 中的停留时间（建议 500ms）
- `properties.buffer.memory`：缓存消息的总可用内存（建议 134217728 = 128MB）

---

#### 2.2 CSV 格式结果表模板

**场景**：将数据写入 Kafka Topic（CSV 格式）

```sql
CREATE TABLE kafka_sink_csv (
  order_id BIGINT,
  order_product_id BIGINT,
  order_customer_id BIGINT,
  order_status VARCHAR,
  order_update_time TIMESTAMP(3)
) WITH (
  'connector' = 'kafka',
  'topic' = 'your-sink-topic',
  'properties.bootstrap.servers' = 'kafka-server:9092',
  'format' = 'csv',
  'csv.disable-quote-character' = 'true',
  'sink.partitioner' = 'round-robin'
);
```

---

### 3. 安全认证模板

#### 3.1 SASL_PLAINTEXT 认证模板

**场景**：使用 SASL_PLAINTEXT 安全协议，SASL 机制为 PLAIN

```sql
CREATE TABLE kafka_source_sasl_plain (
  order_id BIGINT,
  order_product_id BIGINT,
  order_customer_id BIGINT,
  order_status VARCHAR,
  order_update_time TIMESTAMP(3)
) WITH (
  'connector' = 'kafka',
  'topic' = 'your-topic-name',
  'properties.bootstrap.servers' = 'kafka-server:9092',
  'properties.group.id' = 'flink-consumer-group',
  'scan.startup.mode' = 'earliest-offset',
  'format' = 'json',
  'properties.security.protocol' = 'SASL_PLAINTEXT',
  'properties.sasl.mechanism' = 'PLAIN',
  'properties.sasl.jaas.config' = 'org.apache.flink.kafka.shaded.org.apache.kafka.common.security.plain.PlainLoginModule required username="yourname" password="yourpassword";'
);
```

---

#### 3.2 SASL_SSL 认证模板

**场景**：使用 SASL_SSL 安全协议，SASL 机制为 SCRAM-SHA-256

```sql
CREATE TABLE kafka_source_sasl_ssl (
  order_id BIGINT,
  order_product_id BIGINT,
  order_customer_id BIGINT,
  order_status VARCHAR,
  order_update_time TIMESTAMP(3)
) WITH (
  'connector' = 'kafka',
  'topic' = 'your-topic-name',
  'properties.bootstrap.servers' = 'kafka-server:9092',
  'properties.group.id' = 'flink-consumer-group',
  'scan.startup.mode' = 'earliest-offset',
  'format' = 'json',
  'properties.security.protocol' = 'SASL_SSL',
  'properties.ssl.truststore.location' = '/path/to/kafka.client.truststore.jks',
  'properties.ssl.truststore.password' = 'yourpassword',
  'properties.sasl.mechanism' = 'SCRAM-SHA-256',
  'properties.sasl.jaas.config' = 'org.apache.flink.kafka.shaded.org.apache.kafka.common.security.scram.ScramLoginModule required username="yourname" password="yourpassword";',
  'properties.ssl.endpoint.identification.algorithm' = ''
);
```

**注意**：`properties.ssl.endpoint.identification.algorithm` 设置为空字符串可以跳过主机名称校验，避免 SSLHandshakeException。

---

### 4. 完整示例

#### 4.1 完整的 Source → Print 示例

```sql
-- Kafka 源表
CREATE TABLE kafka_source (
  order_id BIGINT,
  order_product_id BIGINT,
  order_customer_id BIGINT,
  order_status VARCHAR,
  order_update_time TIMESTAMP(3)
) WITH (
  'connector' = 'kafka',
  'topic' = 'source-topic',
  'properties.bootstrap.servers' = 'localhost:9092',
  'properties.group.id' = 'flink-consumer-group',
  'scan.startup.mode' = 'earliest-offset',
  'format' = 'json'
);

-- Print 结果表
CREATE TABLE print_sink (
  order_id BIGINT,
  order_product_id BIGINT,
  order_customer_id BIGINT,
  order_status VARCHAR,
  order_update_time TIMESTAMP(3)
) WITH (
  'connector' = 'print'
);

-- 插入数据
INSERT INTO print_sink
SELECT * FROM kafka_source;
```

---

#### 4.2 完整的 Datagen → Kafka 示例

```sql
-- Datagen 源表
CREATE TABLE datagen_source (
  order_id BIGINT,
  order_product_id BIGINT,
  order_customer_id BIGINT,
  order_status VARCHAR,
  order_update_time AS LOCALTIMESTAMP
) WITH (
  'connector' = 'datagen',
  'rows-per-second' = '5'
);

-- Kafka 结果表
CREATE TABLE kafka_sink (
  order_id BIGINT,
  order_product_id BIGINT,
  order_customer_id BIGINT,
  order_status VARCHAR,
  order_update_time TIMESTAMP(3)
) WITH (
  'connector' = 'kafka',
  'topic' = 'sink-topic',
  'properties.bootstrap.servers' = 'localhost:9092',
  'properties.group.id' = 'flink-consumer-group',
  'format' = 'json',
  'properties.batch.size' = '524288',
  'properties.linger.ms' = '500',
  'properties.buffer.memory' = '134217728'
);

-- 插入数据
INSERT INTO kafka_sink
SELECT * FROM datagen_source;
```

---

## 💡 最佳实践

### 1. 性能优化

#### 写入性能优化
如果写入 Kafka 数据时出现吞吐量不足，建议调整以下三个配置值：

| 配置参数 | 建议值 | 说明 |
|---------|--------|------|
| `properties.batch.size` | 524288 (512KB) | 单个 Batch 的最大字节数 |
| `properties.linger.ms` | 500 (500ms) | 消息在 Batch 中的停留时间 |
| `properties.buffer.memory` | 134217728 (128MB) | 缓存消息的总可用内存 |

#### 读取性能优化
- 设置 `scan.parallelism` 单独设置 Source 并发，与 Kafka 分区数相等
- 启用 `scan.topic-partition-discovery.interval` 定期扫描新的 Topic 和 Partition（建议 120s）

---

### 2. 启动模式选择

| 启动模式 | 说明 | 适用场景 |
|---------|------|---------|
| `earliest-offset` | 从最早分区开始读取 | 首次启动，需要消费历史数据 |
| `latest-offset` | 从最新位点开始读取 | 首次启动，只消费新数据 |
| `group-offsets` | 根据 Group 读取（默认） | 有 Checkpoint 的任务恢复 |
| `timestamp` | 从指定时间点读取 | 需要从特定时间点恢复 |
| `specific-offsets` | 从指定分区偏移量读取 | 需要精确控制消费位点 |

---

### 3. Offset 管理

#### 方式 1：依赖 Flink Checkpoint（推荐）
Flink 任务开启 Checkpoint 时，Kafka Source 在完成 Checkpoint 时会提交当前的消费位点。

**优点**：保证 Flink 的 Checkpoint 状态和 Kafka Broker 上的提交位点一致。

**注意**：如果上游数据量很大，可能会触发上游的 LAG 告警。

---

#### 方式 2：依赖 Kafka Consumer 定时提交
当 Flink 任务没有开启 Checkpoint 时，Kafka Source 将依赖 Kafka Consumer 的位点定时提交逻辑。

```sql
CREATE TABLE kafka_source (
  ...
) WITH (
  'connector' = 'kafka',
  ...
  'properties.enable.auto.commit' = 'true',
  'properties.auto.commit.interval.ms' = '5000'
);
```

---

## ⚠️ 注意事项

### 1. Kafka 版本支持
- 不再支持 kafka-0.10 和 kafka-0.11 两个版本的连接器
- 请直接使用 kafka 连接器访问 Kafka 0.10 和 0.11 集群

### 2. BMQ 消费注意事项
- 在 Flink 中使用 Kafka 连接器消费 BMQ 消息时，需要提前在 BMQ 平台侧创建 Consumer Group
- 如果没有提前创建 Group，任务可以正常运行，但不能正常提交 Offset

### 3. 动态分区发现
- 默认不开启动态分区发现
- 建议设置 `scan.topic-partition-discovery.interval = '120s'` 定期扫描新的 Topic 和 Partition

### 4. Flink 1.16/1.17 SSL 注意事项
- Flink SQL 1.16 和 1.17 内置的 Kafka 客户端是 3.x 版本
- `properties.ssl.endpoint.identification.algorithm` 在 3.x 版本中默认为 HTTPS
- 如果遇到 SSLHandshakeException，推荐设置为空字符串跳过主机名称校验

---

## 📚 参考文档

- 官方文档：https://www.volcengine.com/docs/6581/138333?lang=zh

---

## 🎯 技能总结

### 核心功能
1. ✅ **Kafka Source 模板** - JSON/CSV/Avro/Debezium JSON 等多种格式
2. ✅ **Kafka Sink 模板** - 多种格式支持，性能优化配置
3. ✅ **安全认证模板** - SASL_PLAINTEXT、SASL_SSL 等认证方式
4. ✅ **完整示例** - Source→Print、Datagen→Sink 等完整示例
5. ✅ **最佳实践** - 性能优化、启动模式、Offset 管理

这个子技能提供了 Kafka 连接器的完整 SQL 模板！
