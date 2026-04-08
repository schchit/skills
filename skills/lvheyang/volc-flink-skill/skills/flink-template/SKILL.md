---
name: flink-template
description: Flink SQL 模板库和最佳实践技能，提供常用场景的 SQL 模板、最佳实践建议、快速代码片段生成。包含多个子技能：Kafka 模板、Paimon 模板、ByteHouse CDW 模板、ByteHouse CE 模板、TLS 模板、TOS 模板。Use this skill when the user wants to generate, compare, or adapt SQL templates for a specific connector or scenario, such as Kafka source/sink templates, Paimon table patterns, ByteHouse connector SQL, TLS/TOS examples, or scenario-based best practices. Always trigger only when the request contains a template intent + a concrete connector/object/action, such as "生成 Kafka Source 模板", "给我 Paimon 主键表示例", or "提供 TOS 读取 SQL 片段", rather than generic words like "模板" or "最佳实践" alone.
---

# Flink SQL 模板库和最佳实践技能

提供常用场景的 SQL 模板、最佳实践建议、快速代码片段生成。包含多个子技能，覆盖 Kafka、Paimon、ByteHouse、TLS、TOS 等多种数据源和场景。

---

## 通用约定（必读）

本技能的基础约定与只读约定统一收敛在：

- `../../COMMON.md`
- `../../COMMON_READONLY.md`

本技能主要用于模板生成、示例对比和最佳实践建议，默认不执行创建、发布、启动、删除等变更操作。
如用户从“要模板”切换到“创建/发布真实任务”，应转交给 `flink-sql`、`flink-jar` 等变更技能，并遵循相应的 mutation 约定。

---

## 🎯 子技能列表

### 1. Kafka 模板 (flink-template-kafka)
提供 Kafka 连接器的完整模板，包括：
- Kafka 源表（Source）模板
- Kafka 结果表（Sink）模板
- JSON/CSV/Avro 等多种格式支持
- Watermark 设置
- 安全认证配置（SASL、SSL）
- 性能优化配置

**触发关键词**：kafka 模板、kafka source、kafka sink、kafka 连接器

---

### 2. Paimon 模板 (flink-template-paimon)
提供 Paimon 连接器的完整模板，包括：

**写入场景**：
- Append 表（追加表）模板
- 主键表（Primary Key Table）模板
- 部分列更新表（Partial Update）模板
- 聚合表（Aggregate Table）模板

**读取场景**：
- Paimon 源表读取模板
- 时间旅行查询（Time Travel）
- 增量读取模板

**触发关键词**：paimon 模板、paimon 表、append 表、主键表、部分列更新、聚合表

---

### 3. ByteHouse CDW 模板 (flink-template-bytehouse-cdw)
提供 ByteHouse CDW（云数仓）连接器的完整模板，包括：
- ByteHouse CDW 源表模板
- ByteHouse CDW 结果表模板
- 多种写入模式支持
- 性能优化配置

**触发关键词**：bytehouse cdw 模板、bytehouse 云数仓、cdw 模板

---

### 4. ByteHouse CE 模板 (flink-template-bytehouse-ce)
提供 ByteHouse CE（企业版）连接器的完整模板，包括：
- ByteHouse CE 源表模板
- ByteHouse CE 结果表模板
- 多种写入模式支持
- 性能优化配置

**触发关键词**：bytehouse ce 模板、bytehouse 企业版、ce 模板

---

### 5. TLS 模板 (flink-template-tls)
提供 TLS（传输层安全）相关的模板，包括：
- TLS 数据消费模板
- TLS 数据写入模板
- SSL/TLS 安全配置
- 证书配置示例

**触发关键词**：tls 模板、tls 数据、ssl 模板、安全传输

---

### 6. TOS 模板 (flink-template-tos)
提供 TOS（火山引擎对象存储）连接器的完整模板，包括：
- TOS 数据消费模板
- TOS 数据写入模板
- 多种文件格式支持（CSV、JSON、Parquet、ORC）
- 分区表模板
- 性能优化配置

**触发关键词**：tos 模板、tos 数据、对象存储模板

---

## 🎯 核心功能

### 1. 模板选择流程

当用户请求模板时，按以下流程处理：

1. **识别用户需求**
   - 从用户提问中提取关键词
   - 判断用户需要哪个子技能

2. **路由到对应子技能**
   - Kafka 相关 → flink-template-kafka
   - Paimon 相关 → flink-template-paimon
   - ByteHouse CDW → flink-template-bytehouse-cdw
   - ByteHouse CE → flink-template-bytehouse-ce
   - TLS 相关 → flink-template-tls
   - TOS 相关 → flink-template-tos

3. **如果用户没有明确指定，提供场景菜单**
   ```
   请选择您的使用场景：

   1. Kafka 模板（Source/Sink）
   2. Paimon 模板（Append/主键/部分列更新/聚合）
   3. ByteHouse CDW 模板
   4. ByteHouse CE 模板
   5. TLS 模板
   6. TOS 模板
   7. 其他场景（请描述）

   请输入场景编号或描述您的需求：
   ```

---

## 📝 模板展示格式

所有子技能都遵循统一的模板展示格式：

```
# 📝 Flink SQL 模板

## 📋 场景说明
- **场景**: [场景名称]
- **描述**: [场景描述]
- **适用连接器**: [连接器名称]

## 💻 SQL 模板
```sql
[完整的 SQL 模板代码]
```

## 📝 参数说明
- [参数1]: [说明]
- [参数2]: [说明]
- ...

## 💡 最佳实践
[相关的最佳实践建议]

## ⚠️ 注意事项
[使用注意事项]

## ❓ 确认问题
1. 这个模板是否符合您的需求？
2. 是否需要调整参数？
3. 确认后使用 flink-sql 技能进行开发？(yes/no)
```

---

## 🔄 与其他技能的关系

- **配合 flink-sql** - 模板确认后引导使用 flink-sql 进行开发
- **配合 flink-validate** - 可以使用 flink-validate 验证 SQL 语法
- **配合 flink-catalog** - 可以使用 flink-catalog 查看库表结构

---

## 📚 参考文档

各子技能的参考文档：

1. **Kafka 模板**：https://www.volcengine.com/docs/6581/138333?lang=zh
2. **Paimon 模板**：
   - https://www.volcengine.com/docs/6581/1450235?lang=zh
   - https://www.volcengine.com/docs/6581/1456593?lang=zh
   - https://www.volcengine.com/docs/6581/1456594?lang=zh
3. **ByteHouse CDW 模板**：https://www.volcengine.com/docs/6517/1279281?lang=zh#%E4%BD%BF%E7%94%A8%E7%A4%BA%E4%BE%8B
4. **ByteHouse CE 模板**：https://www.volcengine.com/docs/6464/1337868?lang=zh#%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E
5. **TLS 模板**：https://www.volcengine.com/docs/6581/1471373?lang=zh
6. **TOS 模板**：https://www.volcengine.com/docs/6581/1520633?lang=zh

---

## 🎯 技能总结

### 核心功能
1. ✅ **多子技能架构** - 包含 6 个专门的子技能，覆盖主流场景
2. ✅ **智能路由** - 根据用户需求自动路由到对应子技能
3. ✅ **完整模板库** - 提供 Kafka、Paimon、ByteHouse、TLS、TOS 等完整模板
4. ✅ **最佳实践** - 每个模板都包含最佳实践建议
5. ✅ **统一格式** - 所有子技能遵循统一的展示格式

这个技能是 Flink SQL 开发的模板库入口，帮助用户快速创建常用场景的 Flink SQL 任务！
