---
name: flink-template-tls
description: TLS 日志服务 Kafka 协议消费/写入 SQL 模板子技能，提供 Flink Kafka Connector 连接 TLS 的 Source/Sink DDL 与关键参数说明（SASL_SSL + PLAIN + JAAS），用于模板生成与参数替换。Use this skill when the user wants a Flink SQL template to read from or write to Volcengine TLS (Log Service) via Kafka protocol. Only for template generation and parameter explanation, not for publishing/running jobs.
---

# TLS 日志服务 Kafka SQL 模板子技能

提供 TLS 日志服务（TLS, Log Service）通过 Kafka 协议消费/写入的 Flink SQL 模板与参数说明。

本技能只负责生成模板与解释参数，不负责创建/发布/启动真实任务。

---

## 通用约定（必读）

本技能的基础约定与只读约定统一收敛在：

- `../../../COMMON.md`
- `../../../COMMON_READONLY.md`

本技能主要用于模板生成、示例对比和参数说明，默认不执行创建、发布、启动、删除等变更操作。
如用户从“要模板/示例”切换到“创建/发布真实任务”，应转交给 `flink-sql`、`flink-jar` 等变更技能，并遵循相应的 mutation 约定。

---

## 🎯 核心功能

### 1. TLS Kafka 协议消费（Source）

#### 1.1 前置条件与约束（重要）

在使用 Flink Kafka Connector 连接 TLS 之前，必须满足：

- 控制台已开通 TLS 日志服务与“流式计算 Flink 版”服务
- TLS 控制台已开通 Kafka 协议消费功能
- TLS 与 Flink 需在同一个 Region，建议使用私网地址访问
- Flink 版本建议使用 `Flink-1.16-volcano` 及以上

> 参考官方文档：<https://www.volcengine.com/docs/6581/1471373?lang=zh>

#### 1.2 Source DDL（从 TLS 消费）

关键规则（非常容易写错）：

- 消费 TLS 日志 topic 时，`topic` 需要带前缀：`out-${TLS_TOPIC_ID}`
- 消费端 `properties.bootstrap.servers` 一般使用 `9093` 端口（需开通 Kafka 协议消费）
- 鉴权使用 `SASL_SSL` + `PLAIN`，并通过 JAAS 配置：
  - `username`：`${TLS_PROJECT_ID}`
  - `password`：`${ACCESS_KEY}#${SECRET_KEY}`

```sql
CREATE TABLE tls_kafka_source (
  user_id BIGINT,
  item_id BIGINT,
  behavior STRING
) WITH (
  'connector' = 'kafka',
  -- 消费 topic 需要加前缀 out-
  'topic' = 'out-${TLS_TOPIC_ID}',
  -- 结合具体地域选择相应的私网域名，消费者一般使用 9093 端口
  'properties.bootstrap.servers' = 'tls-${REGION}.ivolces.com:9093',
  -- 配置安全协议为 SASL_SSL，验证机制为 PLAIN
  'properties.security.protocol' = 'SASL_SSL',
  'properties.sasl.mechanism' = 'PLAIN',
  -- 配置 JAAS。username 填 TLS 项目 ID；password 填 AK#SK
  'properties.sasl.jaas.config' = 'org.apache.flink.kafka.shaded.org.apache.kafka.common.security.plain.PlainLoginModule required username="${TLS_PROJECT_ID}" password="${ACCESS_KEY}#${SECRET_KEY}";',
  -- 指定消费者组、启动模式与解析格式
  'properties.group.id' = 'test_topic_01',
  'scan.startup.mode' = 'latest-offset',
  'format' = 'json'
);
```

#### 1.3 常用 Source 参数说明

- `topic`：TLS 日志 Topic ID（消费时必须 `out-` 前缀）
- `properties.bootstrap.servers`：TLS 服务地址（消费者一般为 9093）
- `properties.group.id`：TLS 消费组 ID
- `format`：反序列化 TLS 返回消息体（value）时使用的格式（常见：`json`/`csv`/`raw`）
- `scan.startup.mode`：启动模式（常见：`latest-offset`/`group-offsets`/`timestamp`/`specific-offsets`）
  - `timestamp` 模式需额外配置：`scan.startup.timestamp-millis`
  - `specific-offsets` 模式需额外配置：`scan.startup.specific-offsets`

---

### 2. TLS Kafka 协议写入（Sink）

#### 2.1 Sink DDL（写入 TLS）

关键规则：

- 写入 TLS 时，`topic` 不需要 `out-` 前缀，直接用：`${TLS_TOPIC_ID}`
- 生产者 `properties.bootstrap.servers` 一般使用 `9094` 端口
- 写入 TLS 必须关闭幂等：`properties.enable.idempotence = 'false'`（否则任务可能运行失败）
- 鉴权同样使用 `SASL_SSL` + `PLAIN` + JAAS

```sql
CREATE TABLE tls_kafka_sink (
  user_id BIGINT,
  item_id BIGINT,
  behavior STRING
) WITH (
  'connector' = 'kafka',
  -- 结合具体地域选择相应的私网域名，生产者一般使用 9094 端口
  'properties.bootstrap.servers' = 'tls-${REGION}.ivolces.com:9094',
  -- 写入 TLS 必须关闭幂等
  'properties.enable.idempotence' = 'false',
  'properties.security.protocol' = 'SASL_SSL',
  'properties.sasl.mechanism' = 'PLAIN',
  'properties.sasl.jaas.config' = 'org.apache.flink.kafka.shaded.org.apache.kafka.common.security.plain.PlainLoginModule required username="${TLS_PROJECT_ID}" password="${ACCESS_KEY}#${SECRET_KEY}";',
  'topic' = '${TLS_TOPIC_ID}',
  'format' = 'json'
);
```

#### 2.2 常用 Sink 参数（吞吐与成本）

以下参数来自官方文档的建议值与说明（按需启用）：

- `properties.compression.type`：推荐 `lz4`
- `properties.batch.size`：建议（启用压缩）`262144`；（未启用压缩）`2621440`
- `properties.linger.ms`：建议 `100`（引入小延迟换吞吐与压缩率）
- `properties.max.request.size`：建议（启用压缩）`1046576`；（未启用压缩）`10465760`
- `properties.buffer.memory`：建议按 `buffer.memory >= batch.size * 分区数 * 2` 设置
- `sink.partitioner`：
  - `fixed`（默认）：每个 Flink 分区对应一个 TLS 分区
  - `round-robin`：轮流分配到各分区

---

### 3. SQL 示例（可复制替换）

#### 3.1 TLS Source -> Print

```sql
CREATE TABLE tls_source (
  user_id BIGINT,
  item_id BIGINT,
  behavior STRING
) WITH (
  'connector' = 'kafka',
  'topic' = 'out-${TLS_TOPIC_ID}',
  'properties.bootstrap.servers' = 'tls-${REGION}.ivolces.com:9093',
  'properties.security.protocol' = 'SASL_SSL',
  'properties.sasl.mechanism' = 'PLAIN',
  'properties.sasl.jaas.config' = 'org.apache.flink.kafka.shaded.org.apache.kafka.common.security.plain.PlainLoginModule required username="${TLS_PROJECT_ID}" password="${ACCESS_KEY}#${SECRET_KEY}";',
  'properties.group.id' = 'test_topic_01',
  'scan.startup.mode' = 'latest-offset',
  'format' = 'json'
);

CREATE TABLE print_sink (
  user_id BIGINT,
  item_id BIGINT,
  behavior STRING
) WITH (
  'connector' = 'print'
);

INSERT INTO print_sink
SELECT * FROM tls_source;
);
```

---

#### 3.2 Datagen -> TLS Sink

```sql
CREATE TABLE datagen_source (
  user_id BIGINT,
  item_id BIGINT,
  behavior STRING
) WITH (
  'connector' = 'datagen',
  'rows-per-second' = '5'
);

CREATE TABLE tls_sink (
  user_id BIGINT,
  item_id BIGINT,
  behavior STRING
) WITH (
  'connector' = 'kafka',
  'properties.bootstrap.servers' = 'tls-${REGION}.ivolces.com:9094',
  'properties.enable.idempotence' = 'false',
  'properties.security.protocol' = 'SASL_SSL',
  'properties.sasl.mechanism' = 'PLAIN',
  'properties.sasl.jaas.config' = 'org.apache.flink.kafka.shaded.org.apache.kafka.common.security.plain.PlainLoginModule required username="${TLS_PROJECT_ID}" password="${ACCESS_KEY}#${SECRET_KEY}";',
  'topic' = '${TLS_TOPIC_ID}',
  'format' = 'json'
);

INSERT INTO tls_sink
SELECT * FROM datagen_source;
```

---

## ⚠️ 常见易错点（来自官方约束）

1. 消费 topic 必须是 `out-${TLS_TOPIC_ID}`，写入 topic 必须是 `${TLS_TOPIC_ID}`（不要加 `out-`）
2. 消费端一般走 `9093`；写入端一般走 `9094`
3. 写入 TLS 必须 `properties.enable.idempotence = 'false'`
4. Kafka 协议消费功能需要在 TLS 控制台开启；TLS 与 Flink 需同 Region，建议使用私网连接

## 📚 参考文档

- TLS 官方文档：https://www.volcengine.com/docs/6581/1471373?lang=zh

---

## 🎯 技能总结

### 核心功能
1. ✅ **TLS Kafka Source 模板**（SASL_SSL + PLAIN + JAAS，topic 带 `out-` 前缀）
2. ✅ **TLS Kafka Sink 模板**（SASL_SSL + PLAIN + JAAS，必须关闭幂等）
3. ✅ **可复制示例**（Source->Print、Datagen->Sink）

这个子技能提供的是“TLS 日志服务 Kafka 协议”的 SQL 模板（不是通用 Kafka SSL 证书配置模板）。
