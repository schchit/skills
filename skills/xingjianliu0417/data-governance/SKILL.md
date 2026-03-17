---
name: data-governance
description: 数据治理与资产管理技能。用于数据质量评估、元数据管理、数据血缘追踪、数据标准制定、数据合规检查等任务。
---

# Data Governance Skill

数据治理（Data Governance）是指对数据资产管理行使权力和控制的活动集合。

## 何时使用

当用户提及以下内容时使用此 skill：
- 数据质量、数据标准、数据血缘
- 元数据管理、数据目录、数据资产
- 数据合规、隐私保护、数据安全
- 数据治理框架、数据资产管理

## 核心能力

### 1. 数据质量评估

评估数据的完整性、准确性、一致性、时效性：

**检查维度：**
- 缺失值检测
- 重复记录检测
- 格式校验
- 范围校验
- 业务规则验证

### 2. 元数据管理

帮助构建和管理元数据：

**技术元数据：** 表结构、字段类型、数据来源
**业务元数据：** 字段定义、业务规则、所有者
**运营元数据：** 更新频率、ETL信息、访问统计

### 3. 数据血缘追踪

追踪数据的来龙去脉：

**来源追溯：** 数据从哪来
**转换追踪：** 经过哪些处理
**下游影响：** 谁在使用这些数据

### 4. 数据标准

制定和执行数据标准：

**命名规范：** 表名、字段名命名规则
**类型规范：** 数据类型、格式标准
**编码规范：** 枚举值、代码表

## 常用命令

```bash
# 数据质量检查（支持 SQLite, MySQL, PostgreSQL）
python scripts/data_quality_check.py --table <表名> --db <连接字符串>

# 元数据生成
python scripts/generate_metadata.py --source <表名> --db <连接字符串>

# 数据血缘分析
python scripts/lineage_analysis.py --table <表名>
```

### 数据库连接示例

```bash
# SQLite
--db sqlite:///data.db

# MySQL
--db mysql://user:password@localhost:3306/database

# PostgreSQL  
--db postgresql://user:password@localhost:5432/database
```

### 数据合规检查

```bash
# 完整检查
python scripts/compliance_check.py --table users --db mysql://user:pass@localhost:3306/db

# 仅敏感字段检测
python scripts/compliance_check.py --table users --db sqlite:///data.db --check-type sensitive

# GDPR 合规检查
python scripts/compliance_check.py --table users --db postgresql://user:pass@localhost:5432/db --check-type gdpr
```

## 输出格式

完成数据治理任务后，输出结构化报告：

```markdown
## 数据治理报告

### 数据质量
- 完整性：XX%
- 准确率：XX%
- 发现问题：N个

### 元数据
- 表数量：N
- 字段数量：N
- 缺失文档：N个

### 建议
1. ...
2. ...
```

## 常见场景

| 场景 | 输出 |
|------|------|
| 数据质量评估 | 质量报告 + 问题清单 |
| 元数据梳理 | 数据字典 + 关系图 |
| 血缘分析 | 链路图 + 影响分析 |
| 合规检查 | 合规报告 + 风险点 |
