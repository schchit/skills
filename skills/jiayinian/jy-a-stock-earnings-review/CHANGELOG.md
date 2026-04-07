# 更新日志

## 2026-04-02 - 获取最新财报数据逻辑更新（明阳电气案例）

### 问题背景

**明阳电气 (301291) 案例教训：**
- 查询 2025 年年报时，MCP 返回的 `date` 字段为 "2018-12-31"
- 说明 2025 年年报数据尚未披露
- 必须降级查询 2025 年三季报（`date` = "2025-09-30"）
- 在报告中必须明确标注数据截止日期和报告期类型

### 更新内容

**新增数据时效性验证流程：**
1. 检查返回数据的 `date` 字段
2. 如 `date` 为多年前（如 2018-12-31），说明该报告期不存在
3. 必须降级查询上一报告期（年报→三季报→中报→一季报）
4. 在报告中标注数据截止日期和报告期类型

---

## 2026-04-02 - 获取最新财报数据逻辑更新（石头科技案例）

### 问题背景

在石头科技财报点评任务中发现：
- MCP 数据源中部分公司最新年报数据可能尚未披露
- 需要自动降级查询最新季报数据
- 之前报告使用了 2024 年年报数据，而非 2025 年最新季报数据

### 更新内容

#### 1. SKILL.md 更新

**新增获取最新财报数据的标准流程：**

```markdown
### 步骤 2：数据获取（通过 mcporter 调用聚源 MCP 接口）

**🎯 获取最新财报数据的逻辑：**

1. **优先查询最新年报**：
   ```bash
   # 先尝试获取最新年报数据（当前年份 -1）
   mcporter call gildata_datamap-sse.FinancialDataAPI query="公司名 股票代码 2025 年 年报 营业收入 净利润"
   ```

2. **如年报数据为空，查询最新季报**：
   ```bash
   # 按优先级查询：三季报 > 中报 > 一季报
   mcporter call gildata_datamap-sse.FinancialDataAPI query="公司名 股票代码 2025 年 三季报 营业收入 净利润"
   ```

3. **获取上年同期数据用于对比**：
   ```bash
   # 获取上年同期数据计算同比增速
   mcporter call gildata_datamap-sse.FinancialDataAPI query="公司名 股票代码 2024 年 三季报 营业收入 净利润"
   ```
```

**新增数据验证要求：**
- 必须验证数据是否为最新报告期（检查 `date` 字段）
- 必须获取上年同期数据验证同比增速
- 如最新报告期数据为空，必须降级查询上一报告期
- 所有数据必须标注报告期（年报/三季报/中报/一季报）

#### 2. README.md 更新

**新增"获取最新财报数据流程"章节：**

```markdown
## 📋 获取最新财报数据流程

**步骤 1：查询最新年报**
```bash
mcporter call gildata_datamap-sse.FinancialDataAPI query="公司名 股票代码 2025 年 年报 营业收入 净利润"
```

**步骤 2：如年报无数据，查询最新季报**
```bash
# 按优先级：三季报 > 中报 > 一季报
mcporter call gildata_datamap-sse.FinancialDataAPI query="公司名 股票代码 2025 年 三季报 营业收入 净利润"
```

**步骤 3：获取上年同期数据**
```bash
mcporter call gildata_datamap-sse.FinancialDataAPI query="公司名 股票代码 2024 年 三季报 营业收入 净利润"
```

**步骤 4：验证数据时效性**
- 检查返回数据的 `date` 字段
- 确认是最新报告期
- 在报告中标注报告期类型（年报/三季报/中报/一季报）
```

#### 3. references/data-validation-checklist.md 更新

**新增"获取最新财报数据的逻辑"章节：**

- 第一步：确定最新报告期（年报优先，季报降级）
- 第二步：验证数据时效性（检查 `date` 字段）
- 第三步：获取上年同期数据
- 新增数据时效性验证清单

#### 4. references/gildata_mcp_api.md 更新

**新增"获取最新财报数据（标准流程）"章节：**

- 完整的四步流程示例
- 包含年报查询、季报降级、同期对比、时效性验证

### 使用示例

**石头科技案例：**

```bash
# 1. 先查询 2025 年年报（无数据）
mcporter call gildata_datamap-sse.FinancialDataAPI query="石头科技 688169 2025 年 年报 营业收入 净利润"
# 返回：空

# 2. 降级查询 2025 年三季报（有数据）
mcporter call gildata_datamap-sse.FinancialDataAPI query="石头科技 688169 2025 年 三季报 营业收入 净利润"
# 返回：营收 120.66 亿（+72.2%），净利润 10.38 亿（-29.5%）

# 3. 获取上年同期数据
mcporter call gildata_datamap-sse.FinancialDataAPI query="石头科技 688169 2024 年 三季报 营业收入 净利润"
# 返回：营收 70.07 亿，净利润 14.73 亿

# 4. 验证并标注
# 报告中标注：数据截止日期 2025-09-30（三季报）
```

### 影响范围

- ✅ SKILL.md
- ✅ README.md
- ✅ references/data-validation-checklist.md
- ✅ references/gildata_mcp_api.md

### 后续改进

- [ ] 更新 `fetch_financial_data.py` 脚本，实现自动降级查询逻辑
- [ ] 添加报告期自动检测功能
- [ ] 在脚本中添加数据时效性验证

---

## 2026-04-02 - MCP 服务配置修正

### 问题

技能文档中配置的 MCP 服务名称（`jy-financedata-tool`、`jy-financedata-api`）不存在，导致工具调用失败。

### 修正

- 服务名称：`jy-financedata-tool/api` → `gildata_datamap-sse`
- 工具名称：`IncomeStatement` 等 → `FinancialDataAPI`、`MainOperIncData`

### 更新文件

- SKILL.md
- README.md
- references/gildata_mcp_api.md
- scripts/fetch_financial_data.py

---

## 2026-04-02 - 数据校验清单新增

### 新增文件

- `references/data-validation-checklist.md`

### 内容

- 历史数据错误教训（宁德时代事件）
- 数据校验清单
- 正确的 MCP 工具调用方式
- 常见错误及避免方法
