---
name: table-skill
description: "端到端表格数据引擎：集成了工业级别表格数据预处理（智能拆分/清洗/表头合并）、深度探索性分析（QA/EDA/特征挖掘）、假设生成，并支持自动化 Python 绘图与现代化 React Web 报告编译。"
metadata: { "openclaw": { "emoji": "📊", "requires": { "bins": ["python"], "env": ["OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL"] }, "primaryEnv": "OPENAI_API_KEY" } }
---

# 📊 工业级表格预处理与深度分析技能 (Table Preprocess & EDA)

本技能集专注于脏数据的早期治理，提供端到端的表格拆分、清洗、表头结构化和基础特征提取功能。所有脚本已深度适配 OpenClaw 环境，Agent 可直接在 workspace 根目录调用。

> ⚠️ **核心依赖说明**: `merge_header` (表头合并) 强依赖 OpenAI 兼容接口。Agent 在执行该技能前，必须确保系统已注入 `OPENAI_API_KEY`、`OPENAI_BASE_URL` 和 `OPENAI_MODEL` 环境变量。
> 📦 **环境安装说明**: 本技能包含动态数据处理与绘图，Agent/用户在执行前请务必完成依赖安装：`pip install -r requirements.txt`

## 🧰 技能列表 (Atomic Skills)

### split_table - 表格拆分
将 Excel/CSV 文件按空行拆分为多个独立表格。
* **命令行 (Agent 首选)**:
  ```bash
  python skills/table-skill-1.0.1/script/split_table_skill.py input.xlsx ./output
  ```
* **使用方式 (Python API)**:
  ```python
  import sys
  sys.path.append("skills/table-skill-1.0.1")
  from script.split_table_skill import SplitTableSkill
  
  skill = SplitTableSkill()
  result = await skill.run("input.xlsx", "./output")
  # 返回: {"split_files": ["output/table1.csv", ...], "table_count": 2, "success": true}
  ```

---

### clean_table - 表格清洗
清洗表格数据，移除空白行列，处理复杂表头。
* **参数**:
  * `--no-merge-header`: 禁用多行表头合并（默认开启）
  * `--remove-chars`: 需要移除的字符列表（默认 `,%`）
* **命令行 (Agent 首选)**:
  ```bash
  python skills/table-skill-1.0.1/script/clean_table_skill.py input.csv ./output
  python skills/table-skill-1.0.1/script/clean_table_skill.py input.csv ./output --no-merge-header
  python skills/table-skill-1.0.1/script/clean_table_skill.py input.csv ./output --remove-chars ",%"
  ```
* **使用方式 (Python API)**:
  ```python
  import sys
  sys.path.append("skills/table-skill-1.0.1")
  from script.clean_table_skill import CleanTableSkill
  
  skill = CleanTableSkill(is_merge_header=True, remove_chars=[',', '%'])
  result = await skill.run("input.csv", "./output")
  # 返回: {"output_file": "output/input_cleaned.csv", "success": true, "row_count": 100, "col_count": 10}
  ```

---

### merge_header - 表头合并
使用 LLM 智能检测并合并多行表头（**依赖 OPENAI 环境变量**）。
* **命令行 (Agent 首选)**:
  ```bash
  python skills/table-skill-1.0.1/script/merge_header_skill.py input.csv ./output
  ```
* **使用方式 (Python API)**:
  ```python
  import sys
  sys.path.append("skills/table-skill-1.0.1")
  from script.merge_header_skill import MergeHeaderSkill
  
  skill = MergeHeaderSkill()
  result = await skill.run("input.csv", "./output")
  # 返回: {"output_file": "output/input_merged.csv", "success": true, "header_rows_detected": 3}
  ```

---

### describe_table - 表格描述生成
生成表格的详细描述信息，包括统计和样本数据。
* **参数**:
  * `--no-abstract`: 禁用 LLM 摘要生成（默认启用）
* **命令行 (Agent 首选)**:
  ```bash
  # 默认启用 LLM 摘要
  python skills/table-skill-1.0.1/script/describe_table_skill.py input.csv ./output
  
  # 禁用 LLM 摘要生成
  python skills/table-skill-1.0.1/script/describe_table_skill.py input.csv ./output --no-abstract
  ```
* **使用方式 (Python API)**:
  ```python
  import sys
  sys.path.append("skills/table-skill-1.0.1")
  from script.describe_table_skill import DescribeTableSkill
  
  skill = DescribeTableSkill(is_abstract=False)
  result = await skill.run("input.csv", "./output")
  # 返回: {"description": {...}, "output_file": "output/input_description.json", "success": true}
  ```

---

### 🌟 eda_and_visualization - 深度数据探索与可视化 (Agent 动态执行)
*(注：此技能无现成 Python 脚本，需 Agent 自行编写代码)*

在预处理完成后，Agent 需根据生成的描述文件，**动态编写 Python 代码**进行业务挖掘和图表绘制。

* **核心任务**: 数据质量校验 (QA)、特征相关性挖掘 (EDA)、业务假设生成 ($H_0$/$H_1$)、现代化 Web 报告编译。
* **详细约束**: Agent 必须严格查阅并遵循 👉 [深度探索与可视化规范](./script/docs/05_eda_mining_skill.md)。
---

## 🔄 完整流程示例

```python
import sys
import asyncio
sys.path.append("skills/table-skill-1.0.1")
from script.split_table_skill import SplitTableSkill
from script.clean_table_skill import CleanTableSkill
from script.merge_header_skill import MergeHeaderSkill
from script.describe_table_skill import DescribeTableSkill

async def main():
    # 1. 拆分
    split_result = await SplitTableSkill().run("data.xlsx", "./output")

    # 2. 遍历处理
    for file in split_result["split_files"]:
        # 清洗 (为 LLM 表头合并做准备，保留原表头)
        clean_result = await CleanTableSkill(is_merge_header=False, remove_chars=[',']).run(file, "./output")
        
        # 表头合并 (依赖 OPENAI 环境变量)
        merged_result = await MergeHeaderSkill().run(clean_result["output_file"], "./output")
        
        # 3. 描述
        desc_result = await DescribeTableSkill(is_abstract=False).run(merged_result["output_file"], "./output")
        
    # 4. 深度探索与可视化 (EDA & Mining)
    # 注意：此处由 Agent 跳出循环后接管，读取上述生成的某一个或全部 JSON 进行深度分析。
    # Agent 将根据 05_eda_mining_skill.md 的规范，自动编写代码生成图表与 Web 报告。

# 执行主函数
asyncio.run(main())
```

---

## 📤 返回格式

所有技能返回统一格式:

**✅ 成功时**:
```json
{
  "success": true,
  "output_file": "output/processed.csv"
}
```

**❌ 失败时**:
```json
{
  "success": false,
  "error": "错误信息"
}
```

---

## 📚 详细文档

- [表格拆分详解](./script/docs/01_split_table_skill.md)
- [表格清洗详解](./script/docs/02_clean_table_skill.md)
- [描述生成详解](./script/docs/03_describe_table_skill.md)
- [表头合并详解](./script/docs/04_merge_header_skill.md)
- [深度探索与可视化规范 (EDA & Mining)](./script/docs/05_eda_mining_skill.md)