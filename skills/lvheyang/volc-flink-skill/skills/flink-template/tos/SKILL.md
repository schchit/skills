---
name: flink-template-tos
description: TOS（对象存储）SQL 模板子技能，基于 Flink Filesystem Connector 提供读取/写入 `tos://` 路径的 Source/Sink DDL 模板与关键参数说明（rolling policy、partition commit 等）。Use this skill when the user wants a Flink SQL template to read from or write to Volcengine TOS via the filesystem connector. Only for template generation and parameter explanation, not for publishing/running jobs.
---

# TOS（对象存储）SQL 模板子技能

基于 Flink 内置的 Filesystem Connector，生成访问火山引擎对象存储 TOS 的 SQL 模板：读取 `tos://<bucket>/<path>` 作为 Source，或写入 `tos://<bucket>/<path>` 作为 Sink。

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

### 1. 前置说明（避免踩坑）

1. 使用 TOS 时，`path` 必须使用 `tos://bucket_name/file_path/` 形式。
2. 写入场景如果希望尽快在对象存储中看到“可读的完整文件”，通常需要：
   - 配置 rolling policy（例如 `sink.rolling-policy.file-size`、`sink.rolling-policy.rollover-interval`）
   - 并在作业层开启 Checkpoint（让 sink 更稳定地提交/滚动文件）

参考官方文档：<https://www.volcengine.com/docs/6581/1520633?lang=zh>

---

### 2. TOS Source 模板（读取）

**场景**：将 TOS 文件/目录作为数据源。

最小可用模板如下（按需替换字段与 `format`）：

```sql
CREATE TABLE tos_filesystem_source (
  name STRING,
  score INT
)
WITH (
  'connector' = 'filesystem',
  'path' = 'tos://<bucket>/<path>',
  'format' = 'json'
);
```

**关键参数**
- `connector`: 固定为 `filesystem`
- `path`: `tos://bucket_name/file_path/`
- `format`: 文件格式（例如 `json`）。具体可用格式取决于 Flink 环境内置能力与版本，请以“概览/支持列表”为准。

---

### 3. TOS Sink 模板（写入）

**场景**：将数据写入 TOS 文件/目录。

```sql
CREATE TABLE tos_filesystem_sink (
  name STRING,
  score INT
)
WITH (
  'connector' = 'filesystem',
  'path' = 'tos://<bucket>/<path>',
  -- 让文件更快落盘可见（建议配合开启 checkpoint）
  'sink.rolling-policy.file-size' = '1M',
  'sink.rolling-policy.rollover-interval' = '10 min',
  'format' = 'json'
);
```

#### 3.1 rolling policy（写入文件滚动策略）

官方文档给出的核心配置：

- `sink.rolling-policy.file-size`：文件大小达到阈值后滚动（默认 `128MB`）
- `sink.rolling-policy.rollover-interval`：写入时间超过阈值后滚动（默认 `30min`）
- `sink.rolling-policy.check-interval`：滚动条件检查间隔（默认 `1min`）

#### 3.2 分区提交（可选，高级）

如果你在写入路径上使用分区目录（例如 `.../dt=2026-04-08/`），可以考虑配置分区提交策略（示例：生成 `_success` 文件）：

- `sink.partition-commit.trigger`：`process-time` / `partition-time`
- `sink.partition-commit.delay`：分区关闭延迟
- `partition.time-extractor.kind`：分区时间抽取方式（`default`/`custom`）
- `partition.time-extractor.class`：自定义抽取类（仅 custom 时）
- `partition.time-extractor.timestamp-pattern`：从分区字段组合时间戳的 pattern
- `sink.partition-commit.policy.kind`：`success-file` / `custom`
- `sink.partition-commit.policy.class`：自定义提交策略类（仅 custom 时）

---

### 4. 完整示例：Kafka -> TOS Parquet

说明：

1. 这个示例只用于演示“Kafka Source + TOS Sink”的完整 SQL 链路。
2. `parquet` 格式是否可用取决于你的 Flink 环境与已安装的格式依赖；如果环境不支持，可把 `format` 改为 `json/csv` 等你环境支持的格式。
3. `tos://` 的 `<bucket>/<path>`、Kafka 的 `<topic>/<brokers>/<group-id>` 都需要替换成你的实际值。

```sql
-- Kafka 源表（示例：JSON）
CREATE TABLE kafka_source (
  user_id BIGINT,
  item_id BIGINT,
  behavior STRING,
  event_time TIMESTAMP(3)
) WITH (
  'connector' = 'kafka',
  'topic' = '<topic>',
  'properties.bootstrap.servers' = '<brokers>',
  'properties.group.id' = '<group-id>',
  'scan.startup.mode' = 'earliest-offset',
  'format' = 'json'
);

-- TOS Parquet 结果表（filesystem -> tos://）
CREATE TABLE tos_sink_parquet (
  user_id BIGINT,
  item_id BIGINT,
  behavior STRING,
  event_time TIMESTAMP(3),
  dt STRING
) PARTITIONED BY (dt) 
WITH (
  'connector' = 'filesystem',
  'path' = 'tos://<bucket>/<path>/',
  -- 让文件更快落盘可见（建议配合开启 checkpoint）
  'sink.rolling-policy.file-size' = '128MB',
  'sink.rolling-policy.rollover-interval' = '30 min',
  'format' = 'parquet'
);

INSERT INTO tos_sink_parquet
SELECT
  user_id,
  item_id,
  behavior,
  event_time,
  DATE_FORMAT(event_time, 'yyyy-MM-dd') AS dt
FROM kafka_source;
```

## 📚 参考文档

- TOS 官方文档：https://www.volcengine.com/docs/6581/1520633?lang=zh

---

## 🎯 技能总结

### 核心功能
1. ✅ **TOS Source 模板**（filesystem connector + `tos://` 路径）
2. ✅ **TOS Sink 模板**（rolling policy + `tos://` 路径 + format）
3. ✅ **分区提交参数说明**（success-file / custom，按需启用）

这个子技能提供的是“Flink Filesystem Connector 访问 TOS”的 SQL 模板（不是任意文件格式/任意参数的大而全清单）。
