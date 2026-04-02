# CLI-Obsidian 📝

**让 Obsidian 笔记库对 AI Agent 友好**

[![Version](https://img.shields.io/badge/version-1.0.0-blue)]()
[![Python](https://img.shields.io/badge/python-3.10+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-yellow)]()

---

## 🚀 快速开始

### 安装

```bash
pip install -e .
```

### 使用

```bash
# 进入交互模式
cli-obsidian

# 创建笔记
cli-obsidian note create --title "Meeting Notes" --tags "meeting,work"

# 列出笔记
cli-obsidian note list

# 搜索笔记
cli-obsidian search "project deadline"

# JSON 输出（Agent 使用）
cli-obsidian --json note list
```

---

## 📖 功能

### 笔记管理
- ✅ 创建笔记
- ✅ 列出笔记
- ✅ 打开笔记
- ✅ 添加标签

### 笔记库管理
- ✅ 笔记库信息
- ✅ 统计信息

### 搜索
- ✅ 文件名搜索
- ✅ 内容搜索

### 导出
- ✅ Markdown 导出
- ✅ HTML 导出
- ✅ JSON 导出

---

## 🤖 Agent 集成

CLI-Obsidian 专为 AI Agent 设计：

- **JSON 输出**: `--json` 标志输出结构化数据
- **确定性行为**: 相同输入 = 相同输出
- **错误处理**: 清晰的错误消息
- **无状态**: 每次调用独立

### OpenClaw 示例

```yaml
skill: cli-obsidian
commands:
  - note.create
  - note.list
  - search
```

---

## 💰 商业许可

**个人使用**: 免费  
**商业使用**: ¥68/永久许可

购买许可：[联系开发者](mailto:cli-skill-factory@example.com)

---

## 📄 License

MIT License (个人使用)  
商业许可需单独购买
