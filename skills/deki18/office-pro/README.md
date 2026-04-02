# OpenClaw Office Pro

**企业级文档自动化套件 - 专为OpenClaw AI助手设计**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-green.svg)](https://openclaw.ai)

专业级Microsoft Word和Excel文档自动化工具，提供企业级模板、动态数据绑定和批量处理能力。专为OpenClaw AI助手设计，支持自动化文档生成、报表创建和商务文档处理。

## ✨ 特性

### 📝 Word文档处理
- **模板引擎**: 基于Jinja2的`docxtpl`，支持变量、条件、循环
- **企业模板**: 8个预设专业模板（商务信函、会议纪要、工作报告等）
- **完整格式支持**: 段落、表格、图片、页眉页脚、页码、样式
- **动态内容**: 邮件合并、批量生成

### 📊 Excel表格处理  
- **模板驱动**: 基于xlsx-template理念，数据替换保持格式
- **企业模板**: 8个预设专业模板（财务报表、项目进度、库存管理等）
- **高级功能**: 图表、透视表、公式、数据验证、条件格式
- **数据交换**: CSV/JSON互导、Word ↔ Excel数据交互

### ⚡ 自动化能力
- **批量文档生成**: 一键生成多个文档
- **命令行接口**: 完整的CLI工具
- **Python API**: 易于集成的编程接口
- **OpenClaw集成**: 作为技能直接调用

## 🚀 快速开始

### 安装依赖
```bash
pip install python-docx openpyxl docxtpl pandas Pillow click
```

### 基本使用

#### 1. 使用Python API

```python
from office_pro import WordProcessor, ExcelProcessor

# Word文档生成
wp = WordProcessor()
doc = wp.load_template('meeting-minutes.docx')
doc.render({
    'meeting_title': 'Q1产品规划会议',
    'date': '2024-03-15',
    'attendees': ['张三', '李四', '王五']
})
doc.save('output/meeting-minutes-2024-03-15.docx')

# Excel报表生成
ep = ExcelProcessor()
wb = ep.load_template('sales-report.xlsx')
wb.render({
    'report_date': '2024-03-15',
    'sales_rep': '张三',
    'total_sales': 150000
})
wb.save('output/sales-report-2024-03.xlsx')
```

#### 2. 使用命令行

```bash
# Word文档生成
office-pro word generate --template meeting-minutes.docx --data meeting.json --output meeting.docx

# Excel报表生成
office-pro excel generate --template sales-report.xlsx --data sales.json --output sales.xlsx

# 查看可用模板
office-pro templates list
```

#### 3. 在OpenClaw中使用

```bash
# 作为OpenClaw技能调用
openclaw sessions_spawn \
  --runtime subagent \
  --task "使用Office Pro生成销售报表" \
  --label office-pro \
  --mode run
```

## 🎯 可用模板

### Word模板 (8个)
1. **商务信函** (`letter-business`) - 正式商务往来信函
2. **会议纪要** (`meeting-minutes`) - 标准会议记录模板
3. **项目提案** (`project-proposal`) - 商业项目提案书
4. **工作报告** (`work-report`) - 周/月工作报告
5. **简单合同** (`contract-simple`) - 标准商务合同
6. **专业简历** (`resume-professional`) - 求职简历模板
7. **新闻稿** (`press-release`) - 企业新闻稿
8. **正式邀请函** (`invitation-formal`) - 正式场合邀请函

### Excel模板 (8个)
1. **财务报表** (`financial-statement`) - 资产负债表、利润表、现金流量表
2. **预算表** (`budget-template`) - 年度/月度预算表
3. **项目进度** (`project-timeline`) - 甘特图、里程碑追踪
4. **库存管理** (`inventory-management`) - 产品库存跟踪
5. **销售报表** (`sales-report`) - 销售业绩分析
6. **员工考勤** (`attendance-tracking`) - 月度考勤记录
7. **客户管理** (`crm-simple`) - 客户关系管理
8. **数据透视** (`pivot-demo`) - 数据透视表示例

## 🔧 技术栈

### 核心依赖
- **python-docx** (>=1.1.2) - Word文档处理
- **openpyxl** (>=3.1.5) - Excel表格处理
- **docxtpl** (>=0.6.9) - Word模板引擎 (基于Jinja2)
- **Jinja2** (>=3.1.4) - 模板渲染
- **pandas** (>=2.0.0) - 数据处理与分析
- **click** (>=8.1.0) - CLI框架

### 可选依赖
- **Pillow** (>=10.0.0) - 图片处理
- **python-dateutil** (>=2.8.0) - 日期解析
- **markdown** (>=3.5.0) - Markdown支持

## 📖 文档

- [SKILL.md](SKILL.md) - OpenClaw技能主文档，包含完整API规范和使用指南

## 🛠️ 开发

### 环境设置
```bash
# 克隆仓库
git clone https://github.com/yourusername/Openclaw-Office-Pro.git
cd Openclaw-Office-Pro

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 运行测试
```bash
# 运行功能测试
python -m pytest tests/

# 运行端到端测试
python scripts/test_end_to_end.py
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🤝 致谢

- [python-docx](https://github.com/python-openxml/python-docx) 开发团队
- [openpyxl](https://openpyxl.readthedocs.io/) 开发团队  
- [docxtpl](https://github.com/elapouya/python-docx-template) 开发团队
- [OpenClaw](https://openclaw.ai) 社区

## 📞 支持

- 问题反馈: [GitHub Issues](https://github.com/yourusername/Openclaw-Office-Pro/issues)
- 功能建议: [GitHub Discussions](https://github.com/yourusername/Openclaw-Office-Pro/discussions)

---

**Made with ❤️ for OpenClaw Community**

*让AI助手成为你的专业文档助手*