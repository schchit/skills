---
name: Office Pro
slug: office-pro
version: 1.0.0
description: "Enterprise-grade document automation suite for Microsoft Word and Excel. Create professional documents, reports, and spreadsheets with business templates, dynamic data binding, and template-based generation. Supports template rendering (Jinja2 for Word, data substitution for Excel), batch processing, and cross-format data exchange. Use when (1) generating business documents with consistent branding; (2) creating reports from structured data; (3) automating Excel workflows with templates; (4) converting between CSV/JSON and Office formats; (5) batch document generation is required."
changelog: "Initial release with Word and Excel automation, 16 enterprise templates, template engine, and CLI tools."
metadata: {"openclaw":{"emoji":"📊","requires":{"bins":["python3"],"pip":["python-docx","openpyxl","docxtpl","Jinja2","pandas","Pillow","click","python-dateutil"]},"os":["linux","darwin","win32"]}}
---

# Office Pro - 企业级文档自动化套件

专业级 Microsoft Word 和 Excel 文档自动化工具，提供企业级模板、动态数据绑定和批量处理能力。

## 核心功能

### Word 文档处理 (.docx)
- **模板引擎**：基于 Jinja2 的 `docxtpl`，支持变量、条件、循环
- **企业模板**：8 个预设专业模板（商务信函、会议纪要、工作报告等）
- **完整格式支持**：段落、表格、图片、页眉页脚、页码、样式
- **动态内容**：邮件合并、批量生成

### Excel 表格处理 (.xlsx)
- **模板驱动**：基于 xlsx-template 理念，数据替换保持格式
- **企业模板**：8 个预设专业模板（财务报表、项目进度、库存管理等）
- **高级功能**：图表、透视表、公式、数据验证、条件格式
- **数据交换**：CSV/JSON 互导、Word ↔ Excel 数据交互

### 批量与自动化
- 批量文档生成
- 命令行接口 (CLI)
- Python API

## API Schema

### Actions 输入输出规范

#### word.generate
生成Word文档（基于模板）

```json
{
  "input": {
    "type": "object",
    "required": ["template", "data", "output"],
    "properties": {
      "template": {
        "type": "string",
        "description": "Template filename (e.g., meeting-minutes.docx)"
      },
      "data": {
        "type": "object",
        "description": "Template data as JSON object or path to JSON file"
      },
      "output": {
        "type": "string",
        "description": "Output file path"
      },
      "template_dir": {
        "type": "string",
        "description": "Custom template directory (optional)"
      }
    }
  },
  "output": {
    "type": "object",
    "properties": {
      "success": {"type": "boolean"},
      "output_path": {"type": "string"},
      "message": {"type": "string"},
      "error": {"type": "string"},
      "error_code": {"type": "string"}
    }
  }
}
```

#### excel.generate
生成Excel报表（基于模板）

```json
{
  "input": {
    "type": "object",
    "required": ["template", "data", "output"],
    "properties": {
      "template": {
        "type": "string",
        "description": "Template filename (e.g., sales-report.xlsx)"
      },
      "data": {
        "type": "object",
        "description": "Template data as JSON object or path to JSON file"
      },
      "output": {
        "type": "string",
        "description": "Output file path"
      },
      "template_dir": {
        "type": "string",
        "description": "Custom template directory (optional)"
      }
    }
  },
  "output": {
    "type": "object",
    "properties": {
      "success": {"type": "boolean"},
      "output_path": {"type": "string"},
      "message": {"type": "string"},
      "error": {"type": "string"},
      "error_code": {"type": "string"}
    }
  }
}
```

#### templates.list
列出可用模板

```json
{
  "input": {
    "type": "object",
    "properties": {
      "type": {
        "type": "string",
        "enum": ["word", "excel", "all"],
        "default": "all",
        "description": "Template type to list"
      },
      "template_dir": {
        "type": "string",
        "description": "Custom template directory (optional)"
      }
    }
  },
  "output": {
    "type": "object",
    "properties": {
      "success": {"type": "boolean"},
      "templates": {
        "type": "object",
        "properties": {
          "word": {"type": "array", "items": {"type": "string"}},
          "excel": {"type": "array", "items": {"type": "string"}}
        }
      }
    }
  }
}
```

#### word.create
创建空白Word文档

```json
{
  "input": {
    "type": "object",
    "required": ["output"],
    "properties": {
      "output": {
        "type": "string",
        "description": "Output file path"
      },
      "title": {
        "type": "string",
        "description": "Document title (optional)"
      }
    }
  },
  "output": {
    "type": "object",
    "properties": {
      "success": {"type": "boolean"},
      "output_path": {"type": "string"},
      "message": {"type": "string"}
    }
  }
}
```

#### excel.create
创建空白Excel工作簿

```json
{
  "input": {
    "type": "object",
    "required": ["output"],
    "properties": {
      "output": {
        "type": "string",
        "description": "Output file path"
      },
      "sheets": {
        "type": "integer",
        "default": 1,
        "description": "Number of sheets to create"
      }
    }
  },
  "output": {
    "type": "object",
    "properties": {
      "success": {"type": "boolean"},
      "output_path": {"type": "string"},
      "message": {"type": "string"}
    }
  }
}
```

### Error Codes

| Code | Description |
|------|-------------|
| SKILL_404 | Template not found |
| SKILL_401 | Invalid file path (security violation) |
| SKILL_402 | Template rendering failed |
| SKILL_501 | Dependency not available |
| SKILL_999 | Document not loaded |

## 快速开始

### 安装

```bash
# 使用 pip 安装依赖
pip install python-docx openpyxl docxtpl pandas Pillow click
```

### 模板初始化

本技能首次运行时会**自动生成** 16 个专业级模板（8个Word + 8个Excel）。模板将在首次调用时自动创建，无需手动上传。

如果需要手动生成模板：

```bash
python generate_premium_templates.py
```

生成的模板位于 `assets/templates/` 目录：
- **Word模板**: `assets/templates/word/` - 会议纪要、商务信函、简历、项目提案、工作报告、合同、新闻稿、邀请函
- **Excel模板**: `assets/templates/excel/` - 销售报告、财务报表、预算表、项目时间线、库存管理、CRM、考勤表、数据透视表

### 使用模板生成 Word 文档

```python
from office_pro import WordProcessor

# 加载模板
wp = WordProcessor()
doc = wp.load_template('meeting-minutes.docx')

# 渲染数据
context = {
    'meeting_title': 'Q1 产品规划会议',
    'date': '2024-03-15',
    'attendees': ['张三', '李四', '王五'],
    'agenda': [
        {'topic': '产品路线图回顾', 'duration': '30分钟'},
        {'topic': '新功能讨论', 'duration': '45分钟'}
    ]
}

# 生成文档
doc.render(context)
doc.save('output/meeting-minutes-2024-03-15.docx')
```

### 使用模板生成 Excel 报表

```python
from office_pro import ExcelProcessor

# 加载模板
ep = ExcelProcessor()
wb = ep.load_template('sales-report.xlsx')

# 数据替换
data = {
    'report_date': '2024-03-15',
    'sales_rep': '张三',
    'total_sales': 150000,
    'target': 120000,
    'products': [
        {'name': '产品A', 'quantity': 100, 'revenue': 50000},
        {'name': '产品B', 'quantity': 80, 'revenue': 60000},
        {'name': '产品C', 'quantity': 50, 'revenue': 40000}
    ]
}

# 生成报表
wb.render(data)
wb.save('output/sales-report-2024-03.xlsx')
```

### 命令行使用

```bash
# Word 文档生成
office-pro word generate --template meeting-minutes.docx --data meeting.json --output meeting-2024-03-15.docx

# Excel 报表生成
office-pro excel generate --template sales-report.xlsx --data sales.json --output sales-march.xlsx

# 查看可用模板
office-pro templates list

# 批量生成
office-pro batch --config batch-config.yaml
```

## 许可协议

MIT License - 开源免费使用
